# -*- coding: utf-8 -*-
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Any

import httpx
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUsers
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from time_parser import SimpleChineseTimeParser

# -------------------------------------------------配置--------------------------------------------------
# 从环境变量中读取你的 Telegram Bot Token
# 这样做比硬编码在代码里更安全
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 查询排课列表URL
BACKEND_API_URL_GET_SCHEDULES = "https://whore-bot.birdkyle7918.com/get_schedules/{username}"
# 新增排课URL
BACKEND_API_URL_POST_SCHEDULE = "https://whore-bot.birdkyle7918.com/schedule"
# 删除排课URL
BACKEND_API_URL_DELETE_SCHEDULE = "https://whore-bot.birdkyle7918.com/schedule"



# -------------------------------------------------日志--------------------------------------------------
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
    datefmt='%Y-%m-%d %H:%M:%S'
)
# 将 formatter 应用到 handler
handler.setFormatter(formatter)
# 将创建的 handler 添加到 logger
logger.addHandler(handler)


# -------------------------------------------------方法--------------------------------------------------
"""开始"""
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /start 命令时，发送欢迎信息"""
    await update.message.reply_text(
        "你好，老师！欢迎使用排课机器人。\n\n"
        "请点击 /get_schedule 命令来查询你的排课记录。\n"
        "请点击 /select_user 命令来添加排课\n\n\n"
        "有问题请联系作者：@birdkyle79\n"
    )


"""优化输出格式为表格"""
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

"""查询排课记录"""
async def get_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /get_schedule 命令时，此函数会被调用"""
    user = update.message.from_user
    username = user.username

    if not username:
        await update.message.reply_text(
            "抱歉，我无法获取你的排课信息，因为你没有设置 Telegram 用户名。\n"
            "请在 Telegram 的“设置”中设置一个公开的用户名（Username）。"
        )
        return

    api_url = BACKEND_API_URL_GET_SCHEDULES.format(username=username)
    reply_message = ""

    try:
        # --- 修改：使用 httpx 进行异步请求 ---
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.text
            table_content = to_table_format(data)
            if table_content:
                reply_message = "排课信息如下：\n\n" + table_content
            else:
                reply_message = "没有找到排课信息\n\n/help"
        else:
            reply_message = "抱歉，查询失败，请联系作者 @birdkyle7918"
            logger.error(f"调用 API 失败，状态码: {response.status_code}, URL: {api_url}")

    except httpx.RequestError as e:
        reply_message = "机器人开小差了～"
        logger.error(f"调用 API 时发生网络错误: {e}")

    await update.message.reply_text(reply_message)



"""接收/select_user指令"""
async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # 使用 KeyboardButtonRequestUser 类来创建请求对象，而不是直接使用字典
    request_user_object = KeyboardButtonRequestUsers(
        request_id=1,  # 请求的唯一ID
        user_is_bot=False,  # 过滤条件：我们不希望用户选择一个机器人
        request_name=True,
        request_username=True
    )

    # 将创建好的对象传递给 KeyboardButton
    user_request_button = KeyboardButton(
        text="点我选择一个排课用户",
        request_users=request_user_object
    )

    # 将按钮放入键盘布局中
    reply_markup = ReplyKeyboardMarkup(
        [[user_request_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "你好！请点击下方的按钮，然后选择一个你想排课的用户",
        reply_markup=reply_markup
    )

# --- 定义对话状态 ---
# 使用 range 创建唯一的整数状态码，更稳健
AWAITING_TIME, _ = range(2)

"""接收到用户分享信息后处理"""
async def users_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """当用户通过按钮分享了一个用户后，处理收到的信息。"""

    # 使用海象运算符 (:=) 来进行赋值和检查，代码更健壮且能消除IDE警告
    if (shared_info := update.message.users_shared) and shared_info.request_id == 1:

        selected_user = shared_info.users[0]

        selected_username: str = selected_user.username
        user_id: int = update.effective_user.id
        username: str = update.effective_user.username

        # 选择的用户没有用户名，直接结束
        if not selected_username:
            await update.message.reply_text("❌ 错误：你选择的用户没有设置Telegram用户名，无法进行排课。\n /select_user")
            return ConversationHandler.END
        if not user_id:
            await update.message.reply_text("❌ 错误：你没有user_id，无法进行排课。\n /select_user")
            return ConversationHandler.END
        if not username:
            await update.message.reply_text("❌ 错误：你没有设置username，无法进行排课。\n /select_user")
            return ConversationHandler.END

        # 有用户名，则放入上下文
        context.user_data['selected_username'] = selected_username
        context.user_data['user_id'] = user_id

        # ✅ 核心步骤：要求用户输入时间
        await update.message.reply_text(
            f"✅ 选择成功！你选择了用户: @{selected_username}\n\n"
            f"请发送给我，你要为他安排的时间（例如：`今天下午5点` 或 `今天晚上10点` 或 `明天晚上10点30`）："
        )
        # ✅ 核心步骤：告诉 ConversationHandler 进入下一个状态
        return AWAITING_TIME

    # 如果消息不符合预期，也结束对话
    return ConversationHandler.END


"""处理用户输入的时间，并调用post接口保存数据"""
async def handle_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """接收用户输入的时间，调用API，并结束对话。"""
    user_input_time = update.message.text

    # 处理中文时间为标准字符串
    simply_parser_obj = SimpleChineseTimeParser()
    user_input_time_str = simply_parser_obj.parse_time(user_input_time)

    # 从上下文中取出之前存储的用户名
    selected_username: str = context.user_data.get('selected_username')
    user_id: int = context.user_data.get('user_id')

    if not selected_username:
        await update.message.reply_text("发生了一个错误，我忘记你之前选了哪个用户。请使用 /select_user 重新开始。")
        logger.error("在 handle_time_input 中无法从 user_data 获取 selected_username")
        return ConversationHandler.END

    await update.message.reply_text(f"正在为 @{selected_username} 排课")

    # --- 调用后端API ---
    payload = {
        "whore_username": update.effective_user.username, # 操作的老师
        "client_username": selected_username, # 被排课的客户
        "scheduled_time": user_input_time_str, # 安排的时间
        "user_id": user_id #本人user_id
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(BACKEND_API_URL_POST_SCHEDULE, json=payload, timeout=5)

        if response.status_code == 200 or response.status_code == 201: # 200 OK or 201 Created
            reply_message = f"✅ 成功！已为 @{selected_username} 安排时间：`{user_input_time_str}`。"
        else:
            reply_message = f"❌ 排课失败，机器人偷懒去了~"
            logger.error(f"调用新增排课API失败: {update.effective_user.username}")

    except httpx.RequestError as e:
        reply_message = "❌ 机器人开小差啦～"
        logger.error(f"调用新增排课API时发生网络错误: {e}")

    await update.message.reply_text(reply_message)

    # 清理 user_data 并结束对话
    context.user_data.clear()
    return ConversationHandler.END

"""接收/delete指令"""
async def delete_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """当用户发送 /delete 命令时，发送选择用户的按钮"""
    # 使用不同的 request_id 来区分是“新增”还是“删除”操作
    request_user_object = KeyboardButtonRequestUsers(
        request_id=2,  # 删除排课的请求ID为 2
        user_is_bot=False
    )

    user_request_button = KeyboardButton(
        text="删除排课",
        request_users=request_user_object
    )

    reply_markup = ReplyKeyboardMarkup(
        [[user_request_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "请点击下方的删除排课按钮，选择一个你想删除其排课记录的用户",
        reply_markup=reply_markup
    )

"""接收到用户分享信息后处理"""
async def user_to_delete_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not (update.message.users_shared and update.message.users_shared.users):
        return ConversationHandler.END

    selected_user = update.message.users_shared.users[0]
    if not selected_user.username or not update.effective_user.username:
        await update.message.reply_text("❌ 错误：你或对方没有设置用户名，无法操作。")
        return ConversationHandler.END

    await update.message.reply_text(f"正在删除客户 @{selected_user.username} 的排课...")
    payload = {"whore_username": update.effective_user.username, "client_username": selected_user.username}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request("DELETE", BACKEND_API_URL_DELETE_SCHEDULE, json=payload, timeout=10)
        if response.status_code == 200:
            row_deleted = response.json().get('row_deleted', 0)
            reply_message = f"✅ 成功！已删除 @{selected_user.username} 的 {row_deleted} 条排课记录"
        else:
            reply_message = f"❌ 删除失败，请联系作者 @birdkyle79"
            logger.error(
                f"删除排课API失败: @{update.effective_user.username}, 状态码: {response.status_code}, 响应: {response.text}")
    except httpx.RequestError as e:
        reply_message = "❌ 机器人开小差啦"
        logger.error(f"删除排课API网络错误: {e}")

    await update.message.reply_text(reply_message)
    return ConversationHandler.END

"""用于取消对话"""
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """用户主动取消对话。"""
    await update.message.reply_text("操作已取消")
    # 清理可能存在的临时数据
    context.user_data.clear()
    return ConversationHandler.END


# --- 核心修改：创建一个统一的“路由器”函数 ---
async def route_user_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    根据 request_id 分发用户分享事件。
    request_id=1: 新增排课流程
    request_id=2: 删除排课操作
    """
    if not (update.message and update.message.users_shared and update.message.users_shared.users):
        return ConversationHandler.END

    request_id = update.message.users_shared.request_id
    selected_user = update.message.users_shared.users[0]

    # --- 逻辑分支 1: 新增排课 ---
    if request_id == 1:
        if not selected_user.username:
            await update.message.reply_text("❌ 错误：你选择的用户没有设置用户名，无法排课。\n /select_user")
            return ConversationHandler.END
        if not update.effective_user.username:
            await update.message.reply_text("❌ 错误：你没有设置用户名，无法排课。\n /select_user")
            return ConversationHandler.END

        context.user_data['selected_username'] = selected_user.username
        context.user_data['user_id'] = update.effective_user.id
        await update.message.reply_text(
            f"✅ 选择成功！你选择了用户: @{selected_user.username}\n\n"
            f"请发送给我你要为他安排的时间（例如：`今天下午5点`）："
        )
        # 进入下一个对话状态，等待时间输入
        return AWAITING_TIME

    # --- 逻辑分支 2: 删除排课 ---
    elif request_id == 2:
        if not selected_user.username or not update.effective_user.username:
            await update.message.reply_text("❌ 错误：你或对方没有设置用户名，无法操作。")
            return ConversationHandler.END

        await update.message.reply_text(f"正在删除客户 @{selected_user.username} 的排课...")
        payload = {"whore_username": update.effective_user.username, "client_username": selected_user.username}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request("DELETE", BACKEND_API_URL_DELETE_SCHEDULE, json=payload, timeout=10)
            if response.status_code == 200:
                row_deleted = response.json().get('row_deleted', 0)
                reply_message = f"✅ 成功！已删除 @{selected_user.username} 的 {row_deleted} 条排课记录"
            else:
                reply_message = f"❌ 删除失败，请联系作者 @birdkyle79"
                logger.error(
                    f"删除排课API失败: @{update.effective_user.username}, 状态码: {response.status_code}, 响应: {response.text}")
        except httpx.RequestError as e:
            reply_message = "❌ 机器人开小差啦"
            logger.error(f"删除排课API网络错误: {e}")

        await update.message.reply_text(reply_message)
        # 删除操作是单步的，直接结束对话
        return ConversationHandler.END

    # 如果 request_id 不是 1 或 2，也结束对话
    return ConversationHandler.END


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("错误：未设置 TELEGRAM_BOT_TOKEN 环境变量！")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- 修改：使用统一的入口点和路由器 ---
    conv_handler = ConversationHandler(
        entry_points=[
            # 只用一个 Handler 来捕获所有用户分享事件
            MessageHandler(filters.StatusUpdate.USERS_SHARED, route_user_shared)
        ],
        states={
            AWAITING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=200
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("get_schedule", get_schedule_command))
    application.add_handler(CommandHandler("select_user", select_user))
    application.add_handler(CommandHandler("delete", delete_schedule_command))

    # 注册这一个总的对话处理器
    application.add_handler(conv_handler)

    print("机器人已启动，正在等待命令...")
    logger.info("机器人服务已启动")
    application.run_polling()


if __name__ == "__main__":
    main()