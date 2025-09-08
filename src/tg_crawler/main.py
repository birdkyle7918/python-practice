import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.tg_crawler.api import groups
from src.tg_crawler.bot.bot_instance import telegram_app

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    在应用启动时初始化并启动 Telegram Bot，在应用关闭时停止它。
    """
    # === 应用启动时执行 ===
    await telegram_app.initialize()  # 初始化 bot application
    await telegram_app.start()  # 启动 polling (在后台运行，非阻塞)

    print("FastAPI app started with Telegram Bot.")

    yield  # yield 之前的代码在启动时运行，之后的在关闭时运行

    # === 应用关闭时执行 ===
    print("Stopping Telegram Bot...")
    await telegram_app.stop()  # 停止 polling
    await telegram_app.shutdown()  # 清理 bot application 资源
    print("Telegram Bot stopped.")


# 创建FastAPI应用
app = FastAPI(
    title="Telegram Group Monitor API",
    description="一个监控Telegram群组消息并进行推送的机器人API",
    version="1.0.0",
    lifespan=lifespan
)

# 包含API路由
app.include_router(groups.router, prefix="/groups", tags=["Groups"])


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Telegram Monitor Bot is running."}
