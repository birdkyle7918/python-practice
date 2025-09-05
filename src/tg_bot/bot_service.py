# -*- coding: utf-8 -*-
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler

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


# --- 新增：用于计算字符串显示宽度的辅助函数 ---
def get_display_width(text: str) -> int:
    """
    计算字符串的显示宽度。
    一个英文字符宽度为1，一个中文字符宽度为2。
    """
    width = 0
    for char in text:
        # \u4e00-\u9fa5 是中文字符的 Unicode 范围
        if '\u4e00' <= char <= '\u9fa5':
            width += 2
        else:
            width += 1
    return width


# --- 核心修改：优化输出格式为表格 ---
def to_table_format(json_string: str) -> str | None:
    """将JSON数据转换为对齐的、等宽字体的表格字符串"""
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        logger.error('解析JSON失败, 内容: %s', json_string)
        return None

    if not (data.get('code') == 200 and data.get('data')):
        logger.warning('JSON数据格式不符合预期, 内容: %s', json_string)
        return None

    records = data['data']
    if not records:
        return None

    headers = {
        "client_username": "客户",
        "scheduled_time": "预约时间"
    }

    # 1. 使用 get_display_width 计算每列的最大显示宽度
    col_widths = {k: get_display_width(v) for k, v in headers.items()}
    for record in records:
        for key, value in record.items():
            if key in headers:
                col_widths[key] = max(col_widths.get(key, 0), get_display_width(str(value)))

    # 2. 辅助函数：根据显示宽度进行填充
    def pad_str(text: str, width: int) -> str:
        current_width = get_display_width(text)
        padding = ' ' * (width - current_width)
        return text + padding

    # 3. 构建表头
    header_line = ""
    for key, header_name in headers.items():
        header_line += pad_str(header_name, col_widths[key]) + "  "

    # 4. 构建分隔线
    separator_line = ""
    for key in headers:
        separator_line += "-" * col_widths[key] + "--"

    # 5. 构建数据行
    data_lines = []
    for record in records:
        line = ""
        for key in headers:
            value = str(record.get(key, ''))
            line += pad_str(value, col_widths[key]) + "  "
        data_lines.append(line)

    # --- 语法修正：将 .join() 操作移出 f-string 表达式 ---
    # 6. 组合所有部分
    # 先将所有数据行用换行符连接成一个大字符串
    data_string = "\n".join(data_lines)
    # 然后再用 f-string 组合，避免在表达式内部出现 '\'
    full_content = (
        f"{header_line}\n"
        f"{separator_line}\n"
        f"{data_string}"
    )

    # 使用 <pre> 标签来确保 Telegram 使用等宽字体渲染
    return f"{full_content}"


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
        user_is_bot=False,
        request_name = True,
        request_username = True
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
        "请点击下方的删除排课按钮，选择一个你想删除排课的用户",
        reply_markup=reply_markup
    )


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

        if not selected_user.username:
            await update.message.reply_text("❌ 错误：对方没有设置用户名，无法操作。")
            return ConversationHandler.END
        if not update.effective_user.username:
            await update.message.reply_text("❌ 错误：你没有设置用户名，无法操作。")
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