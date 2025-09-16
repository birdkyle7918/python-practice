# app/main.py

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import TimedRotatingFileHandler
from typing import List

# 定时任务相关导入
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChannelInvalidError

# 数据库和模型相关导入
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
# 配置和Telegram相关导入
from .settings import settings

# ------------------- 日志 -----------------------------
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, "tg_aggregator.log")
logger = logging.getLogger("MyDailyLogger")
logger.setLevel(logging.DEBUG)

# 创建一个 Handler，用于按天轮换日志文件
# filename: 日志文件的完整路径
# when='D': 表示轮换周期为天 (Day)
# interval=1: 表示每 1 天轮换一次
# backupCount=7: 表示最多保留 7 个备份日志文件
# encoding='utf-8': 设置文件编码，避免中文乱码
handler = TimedRotatingFileHandler(
    filename=log_filename, when="D", interval=1, backupCount=7, encoding="utf-8"
)
# 设置此 handler 写入文件的最低日志级别
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
# 将 formatter 应用到 handler
handler.setFormatter(formatter)
# 将创建的 handler 添加到 logger
logger.addHandler(handler)


# --- 初始化 ---

# 创建所有数据库表 (如果不存在)
models.Base.metadata.create_all(bind=engine)

# 初始化Telethon客户端
client = TelegramClient(settings.SESSION_NAME, settings.API_ID, settings.API_HASH)

# 初始化定时任务调度器
scheduler = AsyncIOScheduler()


# --- 核心业务逻辑 ---

def process_message_text(original_text: str, channel_name: str, channel_id: str) -> str:
    """
    处理转发内容的文本。
    这是您需要根据自己需求定制化处理的地方。
    """
    if not original_text:
        return ""


    processed_text = f"{original_text}\n\n---\n来自频道: `{channel_name} {channel_id}`"
    return processed_text


async def aggregate_messages():
    """
    核心聚合任务，已增强连接检查。
    """
    logger.info("定时任务执行: 开始聚合消息...")

    # 检查客户端是否已连接并授权。如果未就绪，则尝试重连。
    try:
        is_connected = client.is_connected()
        is_authorized = await client.is_user_authorized() if is_connected else False

        if not (is_connected and is_authorized):
            logger.error("Telegram 客户端未连接或未授权，尝试重新连接...")
            # 下面这行代码是正确的，但IDE Linter可能误报，请忽略
            await client.connect()
            if not await client.is_user_authorized():
                logger.error("聚合任务错误: 重新连接成功，但用户未授权。请检查session文件或重新登录。")
                return
            logger.info("重新连接成功。")

    except Exception as e:
        logger.error("聚合任务错误: 检查或重新连接Telegram客户端时失败", e, exc_info=True)
        return  # 连接失败则退出本次任务

    db = SessionLocal()
    try:
        active_channels = crud.get_active_channels(db)
        logger.info(f"找到 {len(active_channels)} 个启用的频道进行处理。")

        for channel_in_db in active_channels:
            logger.info(f"正在处理频道: {channel_in_db.channel_name or channel_in_db.channel_identifier}")
            try:
                channel_entity = await client.get_entity(channel_in_db.channel_identifier)
                channel_title = channel_in_db.channel_name or channel_in_db.channel_identifier
                channel_id = channel_in_db.channel_identifier
                messages = await client.get_messages(
                    channel_entity,
                    limit=1
                )
                messages.reverse()

                for temp_message in messages:
                    if not temp_message.message:
                        logger.info(f"处理 {channel_in_db.channel_name or channel_in_db.channel_identifier} 时没有message")
                        continue

                    # 如果群组最后一条id比数据库里的小，则不处理
                    if temp_message.id <= channel_in_db.last_processed_message_id:
                        logger.info(f"处理 {channel_in_db.channel_name or channel_in_db.channel_identifier} 时，已经达到最新消息状态")
                        continue

                    # 否则需要转发消息
                    forward_text = process_message_text(temp_message.message, channel_title, channel_id)
                    logger.info(f"处理 {channel_in_db.channel_name or channel_in_db.channel_identifier} 时准备转发消息")
                    await client.send_message(settings.DESTINATION_CHANNEL_ID, forward_text, parse_mode='md')
                    logger.info(f"处理 {channel_in_db.channel_name or channel_in_db.channel_identifier} 时已经转发消息")
                    await asyncio.sleep(2)

                    # 然后更新消息id
                    crud.update_last_processed_id(db, channel_id=channel_in_db.id, message_id=temp_message.id)
                    logger.info(f"频道 '{channel_title}' 的最新消息ID更新为: {temp_message.id}")

            except (ChannelPrivateError, ValueError, ChannelInvalidError) as e:
                logger.error(f"错误：无法访问频道 {channel_in_db.channel_identifier}。可能是私有频道、无效用户名或您未加入。", e, exc_info=True)
            except Exception as e:
                logger.error(f"处理频道 {channel_in_db.channel_identifier} 时发生未知错误", e, exc_info=True)
    finally:
        db.close()
    logger.info("定时任务执行: 消息聚合结束。")


# --- FastAPI 生命周期事件 (使用 Lifespan) ---

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # 应用启动时执行
    logger.info("应用启动...")
    try:
        # 下面这行代码是正确的，但某些IDE的Linter可能会误报一个'__await__'相关的警告。
        # 这是因为Telethon库的内部结构复杂，Linter难以正确推断类型。
        # 请直接运行代码，它应该能正常工作。
        await client.start()
        logger.info("Telegram 客户端已连接。")

        # 添加并启动定时任务
        scheduler.add_job(aggregate_messages, 'interval', minutes=settings.SCHEDULE_MINUTES, id="aggregate_job")
        scheduler.start()
        logger.info(f"定时任务已启动，每 {settings.SCHEDULE_MINUTES} 分钟执行一次。")

    except Exception as e:
        # 如果启动时登录失败（例如，session文件失效或需要2FA），在这里会抛出异常
        logger.error("致命错误: Telegram 客户端启动失败", e, exc_info=True)

    yield

    # 应用关闭时执行
    logger.info("应用关闭...")
    scheduler.shutdown()
    if client.is_connected():
        await client.disconnect()
    logger.info("Telegram 客户端已断开，定时任务已停止。")


# 初始化FastAPI应用, 并应用lifespan管理器
app = FastAPI(title="Telegram Channel Aggregator", lifespan=lifespan)


# --- REST API Endpoints (这部分代码保持不变) ---

@app.post("/channels/", response_model=schemas.Channel, status_code=status.HTTP_201_CREATED, summary="创建新频道")
def create_channel(channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    db_channel = crud.get_channel_by_identifier(db, identifier=channel.channel_identifier)
    if db_channel:
        raise HTTPException(status_code=400, detail="Channel identifier already registered")
    return crud.create_channel(db=db, channel=channel)


@app.get("/channels/", response_model=List[schemas.Channel], summary="获取频道列表")
def read_channels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    channels = crud.get_channels(db, skip=skip, limit=limit)
    return channels


# ... (其他API端点 get, put, delete 保持不变)
@app.get("/channels/{channel_id}", response_model=schemas.Channel, summary="获取单个频道详情")
def read_channel(channel_id: int, db: Session = Depends(get_db)):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel


@app.put("/channels/{channel_id}", response_model=schemas.Channel, summary="更新频道信息")
def update_channel(channel_id: int, channel_update: schemas.ChannelUpdate, db: Session = Depends(get_db)):
    db_channel = crud.get_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return crud.update_channel(db=db, db_channel=db_channel, channel_update=channel_update)


@app.delete("/channels/{channel_id}", response_model=schemas.Channel, summary="删除频道")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    db_channel = crud.delete_channel(db, channel_id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel