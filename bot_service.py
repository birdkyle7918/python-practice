# -*- coding: utf-8 -*-
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler

import requests
from telegram import Update
from telegram.ext import ContextTypes

# --- 配置 ---
# 从环境变量中读取你的 Telegram Bot Token
# 这样做比硬编码在代码里更安全
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# 你的后端服务地址
BACKEND_API_URL = "http://149.104.18.215:8848/get_schedules/{username}"

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, 'bot_service.log')
logger = logging.getLogger('MyDailyLogger')
logger.setLevel(logging.DEBUG)

# 创建一个 Handler，用于按天轮换日志文件
# filename: 日志文件的完整路径
# when='D': 表示轮换周期为天 (Day)
# interval=1: 表示每 1 天轮换一次
# backupCount=7: 表示最多保留 7 个备份日志文件
# encoding='utf-8': 设置文件编码，避免中文乱码
handler = TimedRotatingFileHandler(
    filename=log_filename,
    when='D',
    interval=1,
    backupCount=7,
    encoding='utf-8'
)
# 设置此 handler 写入文件的最低日志级别
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y%m%d'
)
# 将 formatter 应用到 handler
handler.setFormatter(formatter)
# 将创建的 handler 添加到 logger
logger.addHandler(handler)


"""
开始
"""
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /start 命令时，发送欢迎信息"""
    await update.message.reply_text(
        "你好，老师！欢迎使用排课机器人。\n\n"
        "请发送 /get_schedule 命令来查询你的排课记录。\n"
        "请发送 /add 命令来添加排课\n"
    )

"""
优化输出格式
"""
def to_table_format(json_string: str) -> str | None:
    data = json.loads(json_string)

    if not (data['code'] == 200 and data['data']):
        logger.error('处理json失败，json内容不是标准格式，json内容：%s', json_string)
        return None

    records = data['data']
    if records is None or len(records) == 0:
        return None

    # 1. 定义表头
    headers = {
        "client_username": "客户",
        "scheduled_time": "预约时间"
    }

    # 2. 计算每列所需的最大宽度
    # 先用表头标题的长度初始化
    col_widths = {k: len(v) for k, v in headers.items()}

    # 遍历数据，更新最大宽度
    for record in records:
        for key, value in record.items():
            if key in headers:  # 只处理我们需要展示的列
                col_widths[key] = max(col_widths.get(key, 0), len(str(value)))

    # 3. 构建表头字符串
    header_line = ""
    for key, header_name in headers.items():
        # ljust 用于左对齐，并用空格填充到指定宽度
        header_line += header_name.ljust(col_widths[key] + 2)  # +2 是为了增加一些间距

    # 4. 构建分隔线
    separator_line = ""
    for key in headers:
        separator_line += "-" * col_widths[key] + "  "

    # 5. 构建数据行
    data_lines = []
    for record in records:
        line = ""
        for key in headers:
            value = str(record.get(key, ''))  # 安全地获取值
            line += value.ljust(col_widths[key] + 2)
        data_lines.append(line)

    # 6. 组合成最终消息
    # 使用 <pre> 标签包裹所有内容，以保证是等宽字体并且保留所有空格和换行
    final_message = ""
    final_message += f"{header_line}\n"
    final_message += f"{separator_line}\n"
    final_message += "\n".join(data_lines)

    return final_message

"""
查询排课记录
"""
async def get_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /get_schedule 命令时，此函数会被调用"""

    # 1. 获取用户信息
    user = update.message.from_user
    username = user.username

    # 检查用户是否设置了 Telegram 用户名
    if not username:
        await update.message.reply_text(
            "抱歉，我无法获取你的排课信息，因为你没有设置 Telegram 用户名。\n"
            "请在 Telegram 的“设置”中设置一个公开的用户名（Username）。"
        )
        logger.warning(f"用户 {user.full_name} (ID: {user.id}) 没有设置用户名。")
        return

    logger.info(f"收到来自用户 @{username} 的请求。")

    # 2. 构造请求 URL 并调用后端服务
    api_url = BACKEND_API_URL.format(username=username)

    try:
        # 发送 GET 请求
        response = requests.get(api_url, timeout=10)  # 设置10秒超时

        # 检查 HTTP 响应状态码
        if response.status_code == 200:
            # 假设后端返回的是纯文本或简单的 JSON
            # 你可以根据实际返回的数据格式进行调整
            data = response.text
            # 如果返回的是 JSON，可以这样处理：
            # data = response.json()
            # reply_message = f"为你找到的排课安排：\n{json.dumps(data, indent=2, ensure_ascii=False)}"
            table_content = to_table_format(data)
            if table_content:
                reply_message = "排课信息如下：\n\n" + table_content
            else:
                reply_message = "没有找到排课信息\n\n/help"
        else:
            # 如果服务器返回了错误码（如 404, 500等）
            reply_message = "抱歉，查询失败。"
            logger.error(f"调用 API 失败，状态码: {response.status_code}, URL: {api_url}")

    except requests.exceptions.RequestException as e:
        # 处理网络问题或其他请求错误
        reply_message = "抱歉，无法连接到服务器，请稍后再试。"
        logger.error(f"调用 API 时发生网络错误: {e}")

    # 3. 将结果发送回 Telegram
    logger.info('输出消息为 %s', reply_message)
    await update.message.reply_text(reply_message)

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUsers
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # --- 这里是关键的修正 ---
    # 使用 KeyboardButtonRequestUser 类来创建请求对象，而不是直接使用字典
    request_user_object = KeyboardButtonRequestUsers(
        request_id=1,  # 请求的唯一ID
        user_is_bot=False  # 过滤条件：我们不希望用户选择一个机器人
    )

    # 将创建好的对象传递给 KeyboardButton
    user_request_button = KeyboardButton(
        text="点我选择一个用户",
        request_users=request_user_object
    )

    # 将按钮放入键盘布局中
    reply_markup = ReplyKeyboardMarkup(
        [[user_request_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "你好！请点击下方的按钮，从你的联系人或通过搜索，选择一个你想发送给我的用户：",
        reply_markup=reply_markup
    )


# 2. 接收到用户分享信息的处理函数
async def users_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户通过按钮分享了一个用户后，处理收到的信息。"""

    # 使用海象运算符 (:=) 来进行赋值和检查，代码更健壮且能消除IDE警告
    if (shared_info := update.message.users_shared) and shared_info.request_id == 1:

        shared_user_id = shared_info.users[0].user_id
        logger.info(f"收到了来自用户 {update.effective_user.id} 的分享请求，分享的用户ID是: {shared_user_id}")

        try:
            # 使用 get_chat 方法获取被分享用户的详细信息
            chat = await context.bot.get_chat(shared_user_id)
            username = chat.username
            first_name = chat.first_name

            # 构造回复消息
            if username:
                response_text = f"✅ 选择成功！\n\n你选择的用户是: @{username}\n他们的 User ID 是: `{shared_user_id}`"
            else:
                response_text = f"✅ 选择成功！\n\n你选择的用户是: {first_name}\n（这位用户没有设置公开的 username）\n他们的 User ID 是: `{shared_user_id}`"

            # 以Markdown格式回复用户
            await update.message.reply_text(response_text, parse_mode='MarkdownV2')

        except Exception as e:
            logger.error(f"获取 User ID {shared_user_id} 的信息时出错: {e}")
            await update.message.reply_text(f"抱歉，在获取用户信息时遇到了一个内部错误。")

# --- 主程序入口 ---

def main() -> None:
    """启动机器人"""
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("错误：未设置 TELEGRAM_BOT_TOKEN 环境变量！")
        return

    # 创建 Application 对象
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # 注册命令处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("get_schedule", get_schedule_command))
    application.add_handler(CommandHandler("select_user", select_user))
    application.add_handler(MessageHandler(filters.StatusUpdate.USERS_SHARED, users_shared))



    # 启动机器人，开始轮询接收消息
    print("机器人已启动，正在等待命令...")
    application.run_polling()


if __name__ == "__main__":
    main()