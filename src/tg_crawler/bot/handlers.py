from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy.future import select

from src.tg_crawler.db.session import AsyncSessionLocal
from src.tg_crawler.db.models import Subscriber
from src.tg_crawler.bot.bot_instance import telegram_app


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Subscriber).where(Subscriber.user_id == user.id))
        existing_subscriber = result.scalar_one_or_none()

        if existing_subscriber:
            await update.message.reply_html(
                f"你好 {user.mention_html()}！你已经订阅了我的推送。"
            )
        else:
            new_subscriber = Subscriber(
                user_id=user.id,
                chat_id=chat_id,
                username=user.username
            )
            session.add(new_subscriber)
            await session.commit()
            await update.message.reply_html(
                f"你好 {user.mention_html()}！你已成功订阅，将会收到最新的群组消息推送。"
            )


# 注册命令处理器
def register_handlers():
    telegram_app.add_handler(CommandHandler("start", start))
