import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select

from src.tg_crawler.db.session import AsyncSessionLocal
from src.tg_crawler.db.models import MonitoredGroup, Subscriber
from src.tg_crawler.bot.bot_instance import bot, TARGET_CHANNEL_ID

logger = logging.getLogger(__name__)


async def check_groups_for_new_messages():
    logger.info("定时任务启动：检查群组新消息...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MonitoredGroup))
        groups = result.scalars().all()

        sub_result = await session.execute(select(Subscriber))
        subscribers = sub_result.scalars().all()

        if not groups:
            logger.info("数据库中没有需要监控的群组。")
            return

        for group in groups:
            try:
                chat = await bot.get_chat(chat_id=group.group_id)
                last_msg = chat.last_message

                if last_msg and (group.last_message_id is None or last_msg.message_id > group.last_message_id):
                    logger.info(f"在群组 {group.group_name} 中发现新消息: {last_msg.message_id}")

                    sender_name = last_msg.from_user.full_name
                    message_text = last_msg.text or "[非文本消息]"
                    message_link = last_msg.link

                    formatted_message = (
                        f"**来自群组**: `{group.group_name}`\n"
                        f"**发送者**: `{sender_name}`\n\n"
                        f"{message_text}\n\n"
                        f"[查看原文]({message_link})"
                    )

                    await bot.send_message(
                        chat_id=TARGET_CHANNEL_ID,
                        text=formatted_message,
                        parse_mode='Markdown'
                    )

                    for sub in subscribers:
                        try:
                            await bot.send_message(
                                chat_id=sub.chat_id,
                                text=formatted_message,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"发送给订阅者 {sub.user_id} 失败: {e}")

                    group.last_message_id = last_msg.message_id
                    await session.commit()

            except Exception as e:
                logger.error(f"处理群组 {group.group_name} 时出错: {e}")


scheduler = AsyncIOScheduler()
scheduler.add_job(check_groups_for_new_messages, 'interval', minutes=1, id="check_messages_job")
