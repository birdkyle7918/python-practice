import logging
import os
from logging.handlers import TimedRotatingFileHandler

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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
            reply_message = f"为你找到 @{username} 的排课安排：\n\n{data}"
            logger.info(f"成功从 API 获取到 @{username} 的数据。")
        else:
            # 如果服务器返回了错误码（如 404, 500等）
            reply_message = f"抱歉，查询失败。服务器返回状态码：{response.status_code}"
            logger.error(f"调用 API 失败，状态码: {response.status_code}, URL: {api_url}")

    except requests.exceptions.RequestException as e:
        # 处理网络问题或其他请求错误
        reply_message = "抱歉，无法连接到排课服务，请稍后再试。"
        logger.error(f"调用 API 时发生网络错误: {e}")

    # 3. 将结果发送回 Telegram
    await update.message.reply_text(reply_message)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /start 命令时，发送欢迎信息"""
    await update.message.reply_text(
        "你好，老师！欢迎使用排课机器人。\n"
        "请发送 /get_schedule 命令来查询你的排课记录。\n"
        "请发送 /add 命令来添加排课\n"
    )


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
    application.add_handler(CommandHandler("get_schedule", get_schedule_command))

    # 启动机器人，开始轮询接收消息
    logger.info("机器人已启动，正在等待命令...")
    application.run_polling()


if __name__ == "__main__":
    main()