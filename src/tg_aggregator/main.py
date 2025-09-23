# app/main.py

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import List

# 定时任务库，用于周期性执行消息聚合任务
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# FastAPI 框架和依赖注入相关
from fastapi import FastAPI, Depends, HTTPException, status
# SQLAlchemy 的数据库会话管理
from sqlalchemy.orm import Session
# Telegram 官方客户端库
from telethon import TelegramClient
# Telethon 可能抛出的特定异常
from telethon.errors import ChannelPrivateError, ChannelInvalidError

# 从当前应用模块导入数据库会话、引擎和依赖注入函数
from .database import SessionLocal, engine, get_db
# 从当前应用模块导入应用配置
from .settings import settings
# 从当前应用模块导入 CRUD 操作、数据库模型和 Pydantic schema
import crud, models, schemas

# ------------------- 日志配置 -----------------------------
# 获取一个名为 "MyStreamLogger" 的日志记录器实例
logger = logging.getLogger("MyStreamLogger")
# 设置日志记录器的最低级别为 DEBUG
logger.setLevel(logging.DEBUG)

# 创建一个流处理器，将日志输出到标准输出 (sys.stdout)
handler = logging.StreamHandler(sys.stdout)
# 设置处理器的日志级别为 DEBUG
handler.setLevel(logging.DEBUG)

# 创建一个日志格式化器，定义日志输出的格式
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
# 将格式化器应用到处理器
handler.setFormatter(formatter)
# 将处理器添加到日志记录器
logger.addHandler(handler)


# ------------------- 初始化部分 -------------------

# 根据定义的模型在数据库中创建所有表（如果它们尚不存在）
models.Base.metadata.create_all(bind=engine)

# 使用配置文件中的 API ID 和 HASH 初始化 Telegram 客户端
# 'settings.SESSION_NAME' 是会话文件的名称，用于保存登录状态
client = TelegramClient(settings.SESSION_NAME, settings.API_ID, settings.API_HASH)

# 初始化一个异步的定时任务调度器
scheduler = AsyncIOScheduler()


# ------------------- 核心业务逻辑 -------------------

def process_message_text(original_text: str, channel_name: str, channel_id: str) -> str:
    """
    处理并格式化从源频道获取到的消息文本，准备转发。
    这是可以根据个人需求进行定制的核心函数。

    Args:
        original_text (str): 从 Telegram 频道获取的原始消息内容。
        channel_name (str): 消息来源频道的名称。
        channel_id (str): 消息来源频道的标识符 (如 @username)。

    Returns:
        str: 经过处理和格式化后的、准备发送到目标频道的文本。
    """
    if not original_text:
        return ""  # 如果原始消息为空，则返回空字符串

    # 在原始消息末尾追加来源信息
    processed_text = f"{original_text}\n\n---\n来自频道: `{channel_name} {channel_id}`"
    return processed_text


async def aggregate_messages():
    """
    核心的消息聚合任务。
    此函数由定时任务调度器周期性调用。
    它会连接 Telegram，获取所有启用的源频道，检查新消息，并将其转发到目标频道。
    """
    logger.info("定时任务执行: 开始聚合消息...")

    # 检查 Telegram 客户端的连接和授权状态
    try:
        is_connected = client.is_connected()
        is_authorized = await client.is_user_authorized() if is_connected else False

        # 如果未连接或未授权，则尝试重新连接
        if not (is_connected and is_authorized):
            logger.error("Telegram 客户端未连接或未授权，尝试重新连接...")
            await client.connect()
            if not await client.is_user_authorized():
                logger.error("聚合任务错误: 重新连接成功，但用户未授权。请检查session文件或重新登录。")
                return  # 授权失败，则终止本次任务
            logger.info("重新连接成功。")

    except Exception as e:
        logger.error(f"聚合任务错误: 检查或重新连接Telegram客户端时失败: {e}", exc_info=True)
        return  # 连接失败，则终止本次任务

    # 创建一个新的数据库会话
    db = SessionLocal()
    try:
        # 从数据库获取所有状态为“活跃”的频道
        active_channels = crud.get_active_channels(db)
        logger.info(f"找到 {len(active_channels)} 个启用的频道进行处理。")

        # 遍历每个活跃的频道
        for channel_in_db in active_channels:
            channel_display_name = channel_in_db.channel_name or channel_in_db.channel_identifier
            logger.info(f"正在处理频道: {channel_display_name}")
            try:
                # 获取频道的实体对象，这是与 Telethon 交互所必需的
                channel_entity = await client.get_entity(channel_in_db.channel_identifier)
                
                # 从频道获取最新的1条消息
                messages = await client.get_messages(
                    channel_entity,
                    limit=1
                )
                
                # 遍历获取到的消息
                for temp_message in messages:
                    if not temp_message.message:
                        logger.info(f"跳过频道 '{channel_display_name}' 的一条空消息。")
                        continue

                    # 如果最新消息的ID不大于数据库中记录的ID，说明没有新消息
                    if temp_message.id <= channel_in_db.last_processed_message_id:
                        logger.info(f"频道 '{channel_display_name}' 没有新消息。")
                        continue

                    # 如果有新消息，则处理并转发
                    forward_text = process_message_text(temp_message.message, channel_display_name, channel_in_db.channel_identifier)
                    logger.info(f"准备从 '{channel_display_name}' 转发新消息。")
                    
                    # 发送到目标频道
                    await client.send_message(settings.DESTINATION_CHANNEL_ID, forward_text, parse_mode=None)
                    logger.info(f"已成功转发来自 '{channel_display_name}' 的消息。")
                    
                    # 等待2秒，防止请求过于频繁
                    await asyncio.sleep(1)

                    # 更新数据库，记录最新处理的消息ID
                    crud.update_last_processed_id(db, channel_id=channel_in_db.id, message_id=temp_message.id)
                    logger.info(f"频道 '{channel_display_name}' 的最新消息ID更新为: {temp_message.id}")

            except (ChannelPrivateError, ValueError, ChannelInvalidError) as e:
                logger.error(f"错误：无法访问频道 {channel_in_db.channel_identifier}。可能是私有频道、无效用户名或您未加入。错误: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"处理频道 {channel_in_db.channel_identifier} 时发生未知错误: {e}", exc_info=True)
    finally:
        # 确保数据库会话在使用后被关闭
        db.close()
    logger.info("定时任务执行: 消息聚合结束。")


# ------------------- FastAPI 生命周期事件 -------------------

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """
    FastAPI 的生命周期管理器。
    在应用启动时执行 'yield' 之前的代码，在应用关闭时执行 'yield' 之后的代码。
    """
    # --- 应用启动时 ---
    logger.info("应用启动...")
    try:
        # 启动 Telegram 客户端并连接
        await client.start()
        logger.info("Telegram 客户端已连接。")

        # 添加定时任务，并设置执行频率
        scheduler.add_job(aggregate_messages, 'interval', minutes=settings.SCHEDULE_MINUTES, id="aggregate_job")
        # 启动定时任务调度器
        scheduler.start()
        logger.info(f"定时任务已启动，每 {settings.SCHEDULE_MINUTES} 分钟执行一次。")

    except Exception as e:
        # 如果在启动过程中（如登录）失败，则记录致命错误
        logger.error(f"致命错误: Telegram 客户端启动失败: {e}", exc_info=True)

    yield  # 应用在此处运行

    # --- 应用关闭时 ---
    logger.info("应用关闭...")
    # 关闭定时任务调度器
    scheduler.shutdown()
    # 如果客户端已连接，则断开连接
    if client.is_connected():
        await client.disconnect()
    logger.info("Telegram 客户端已断开，定时任务已停止。")


# 初始化 FastAPI 应用实例，并应用上面定义的生命周期管理器
app = FastAPI(title="Telegram Channel Aggregator", lifespan=lifespan)


# ------------------- REST API Endpoints -------------------

@app.post("/channels/", response_model=schemas.Channel, status_code=status.HTTP_201_CREATED, summary="创建一个新的源频道")
def create_channel(channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    """
    API 端点：创建一个新的频道以进行监控。
    """
    # 检查频道标识符是否已存在
    db_channel = crud.get_channel_by_identifier(db, identifier=channel.channel_identifier)
    if db_channel:
        raise HTTPException(status_code=400, detail="此频道标识符已存在")
    # 创建频道
    return crud.create_channel(db=db, channel=channel)


@app.get("/channels/", response_model=List[schemas.Channel], summary="获取所有源频道列表")
def read_channels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    API 端点：获取所有已添加的频道列表，支持分页。
    """
    channels = crud.get_channels(db, skip=skip, limit=limit)
    return channels


@app.get("/channels/{channel_id}", response_model=schemas.Channel, summary="根据ID获取单个频道详情")
def read_channel(channel_id: int, db: Session = Depends(get_db)):
    """
    API 端点：根据数据库ID获取单个频道的详细信息。
    """
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="未找到该频道")
    return db_channel


@app.put("/channels/{channel_id}", response_model=schemas.Channel, summary="更新指定频道的信息")
def update_channel(channel_id: int, channel_update: schemas.ChannelUpdate, db: Session = Depends(get_db)):
    """
    API 端点：更新一个已存在频道的信息（例如，切换 is_active 状态）。
    """
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="未找到该频道")
    return crud.update_channel(db=db, db_channel=db_channel, channel_update=channel_update)


@app.delete("/channels/{channel_id}", response_model=schemas.Channel, summary="删除一个频道")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    """
    API 端点：根据ID从数据库中删除一个频道。
    """
    db_channel = crud.delete_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="未找到该频道")
    return db_channel
