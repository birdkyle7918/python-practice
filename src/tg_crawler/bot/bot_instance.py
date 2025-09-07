import telegram
from telegram.ext import Application
from src.tg_crawler.config import settings

# Bot 实例，用于主动发送消息
bot = telegram.Bot(token=settings.BOT_TOKEN)

# Telegram Application 实例，用于处理命令和轮询
telegram_app = Application.builder().token(settings.BOT_TOKEN).build()

# 获取频道ID，处理数字和 @username 格式
try:
    TARGET_CHANNEL_ID = int(settings.TARGET_CHANNEL_ID)
except ValueError:
    TARGET_CHANNEL_ID = settings.TARGET_CHANNEL_ID
