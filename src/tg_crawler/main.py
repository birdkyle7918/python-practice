import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.tg_crawler.api import groups
from src.tg_crawler.bot.scheduler import scheduler
from src.tg_crawler.bot.bot_instance import telegram_app
from src.tg_crawler.bot.handlers import register_handlers

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    logger.info("应用启动...")

    # 注册Bot命令
    register_handlers()

    # 启动定时任务
    scheduler.start()

    # 在后台任务中运行Telegram Bot的轮询
    asyncio.create_task(telegram_app.run_polling())

    logger.info("所有服务已启动。")
    yield
    # 应用关闭时执行
    logger.info("应用关闭...")
    scheduler.shutdown()
    logger.info("定时任务已关闭。")


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
