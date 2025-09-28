import asyncio
import os
from dotenv import load_dotenv

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# Load environment variables from .env file
load_dotenv()

# ------------------- 配置信息 ------------------- #
# 替换为你的 Bot Token (从 @BotFather 获取)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# 替换为你的公开频道的用户名 (以 @ 开头)
CHANNEL_ID = '@yuangu_channel'


# --------------------------------------------- #

# 你想发送的消息文本
message_text = "👇 点击下方的按钮，可以快速搜索指定城市的相关内容："


async def send_message_with_buttons():
    """
    连接到 Telegram Bot API 并发送带有搜索按钮的消息。
    """
    # 初始化 Bot
    bot = Bot(token=BOT_TOKEN)

    # 创建按钮
    # key: 按钮上显示的文本
    # switch_inline_query_current_chat: 点击后在当前聊天窗口输入框中填入的文本
    button_changsha = InlineKeyboardButton(
        text="长沙",
        switch_inline_query_current_chat="#长沙"
    )

    button_shenzhen = InlineKeyboardButton(
        text="深圳",
        switch_inline_query_current_chat="#深圳"
    )

    button_chengdu = InlineKeyboardButton(
        text="成都",
        switch_inline_query_current_chat="#成都"
    )

    # 将按钮排列成一行。每个列表代表一行按钮。
    # 例如 [[button1, button2]] 代表一行两列
    # [[button1], [button2]] 代表两行一列
    keyboard = [
        [button_changsha, button_shenzhen, button_chengdu]
    ]

    # 创建内联键盘布局
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 发送消息
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message_text,
            reply_markup=reply_markup
        )
        print("🎉 消息已成功发送到频道！")
    except Exception as e:
        print(f"❌ 发送失败，错误信息: {e}")
        print("请检查：")
        print("1. BOT_TOKEN 是否正确。")
        print("2. CHANNEL_ID 是否正确，且以 '@' 开头。")
        print("3. Bot 是否已经是频道的管理员，并拥有发送消息的权限。")


# 运行异步函数
if __name__ == '__main__':
    asyncio.run(send_message_with_buttons())
