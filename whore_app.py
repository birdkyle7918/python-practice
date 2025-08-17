# -*- coding: utf-8 -*-
import logging
import os
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

import mysql.connector.pooling
from flask import Flask, request, jsonify

# ------------------- 日志 -----------------------------
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, 'whore_app.log')
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


# ------------------- 配置 -----------------------------
app = Flask(__name__)

DB_PASSWORD = os.getenv("DB_PASSWORD")
# --- 数据库连接池配置 ---
# 请替换为您的数据库连接信息
DB_CONFIG = {
    "host": "149.104.18.215",
    "user": "tguser",     # 替换为您的 MySQL 用户名
    "password": DB_PASSWORD, # 替换为您的 MySQL 密码
    "database": "tg", # 替换为您的数据库名
    "pool_name": "mypool",       # 连接池名称
    "pool_size": 10               # 连接池大小，建议根据应用负载调整
}

# 数据库连接池
db_pool = None

def init_db_pool():
    """初始化数据库连接池"""
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
        logger.info('数据库连接池 %s 初始化成功，大小为 %s', DB_CONFIG['pool_name'], DB_CONFIG['pool_size'])
    except mysql.connector.Error as e:
        logger.error('数据库连接池初始化失败: %s', e)
        exit(1) # 如果连接池初始化失败，直接退出应用

@app.before_request
def setup_db_pool_on_first_request():
    """在第一次请求时初始化数据库连接池"""
    # 确保连接池只被初始化一次
    global db_pool
    if db_pool is None:
        init_db_pool()

def get_db_connection():
    """从连接池获取一个数据库连接"""
    try:
        # pool.get_connection() 会返回一个数据库连接
        conn = db_pool.get_connection()
        return conn
    except mysql.connector.Error as e:
        logger.error('从连接池获取连接失败: %s', e)
        return None

# ------------------- 接口 -----------------------------

@app.route('/schedule', methods=['POST'])
def add_schedule():
    """
    新增排课计划。
    """

    # 入参json
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求体为空或不是有效的 JSON"}), 400

    whore_username = data.get('whore_username')
    client_username = data.get('client_username')
    scheduled_time_str = data.get('scheduled_time')
    user_id = data.get('user_id')

    if not all([whore_username, client_username, scheduled_time_str, user_id]):
        return jsonify({"code": 400, "message": "缺少必要的参数"}), 400

    # 先插入用户
    try:
        insert_user_obj: User = User(user_id=user_id)
        insert_user_info(insert_user_obj)
    except ValueError as v_e:
        return jsonify({"code": 400, "message": str(v_e)}), 400
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

    try:
        # 将字符串时间转换为 datetime 对象
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"code": 400, "message": "scheduled_time 格式不正确，应为 YYYY-MM-DD HH:MM:SS"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"code": 500, "message": "无法连接到数据库"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO whore_service_schedule (whore_username, client_username, scheduled_time, gmt_create, gmt_modified)
        VALUES (%s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (whore_username, client_username, scheduled_time))
        conn.commit()
        return jsonify({"code": 200, "message": "排课添加成功！"}), 200
    except mysql.connector.Error as e:
        conn.rollback() # 出现错误时回滚事务
        logger.error('插入数据失败: %s', e)
        return jsonify({"code": 200, "message": "已有排课记录"}), 200
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() # 使用完毕后将连接归还到连接池

@app.route('/get_schedules/<whore_username>', methods=['GET'])
def get_schedules(whore_username):
    """
    查询指定 whore_username 下所有 scheduled_time 大于今日的数据。
    """
    if not whore_username:
        return jsonify({"code": 400, "message": "请求无效"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"code": 500, "message": "无法连接到数据库"}), 500

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True) # 以字典形式返回结果
        today = date.today() # 获取今天的日期
        # 查询 scheduled_time 大于今天的数据
        query = """
        SELECT whore_username, client_username, scheduled_time, gmt_create, gmt_modified
        FROM whore_service_schedule
        WHERE whore_username = %s AND scheduled_time > %s
        ORDER BY scheduled_time ASC
        LIMIT 30    
        """
        cursor.execute(query, (whore_username, today))
        results = cursor.fetchall()

        # 对 datetime 对象进行序列化处理，转换为字符串
        for row in results:
            # 客户名需要添加一个@符号
            if 'client_username' in row and row['client_username']:
                row['client_username'] = '@' + row['client_username']

            for key, value in row.items():
                if isinstance(value, (datetime, date)):
                    row[key] = value.strftime('%Y年%m月%d日 %H:%M:%S')

        return jsonify({"code": 200, "data": results, "message": "查询成功！"}), 200
    except mysql.connector.Error as e:
        logger.error('查询数据失败: %s', e)
        return jsonify({"code": 500, "message": f"查询数据失败: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() # 使用完毕后将连接归还到连接池

@app.route('/schedule', methods=['DELETE'])
def delete_schedule():

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求体为空或不是有效的 JSON"}), 400

    whore_username = data.get('whore_username')
    client_username = data.get('client_username')
    if not whore_username or not client_username:
        return jsonify({"code": 400, "message": "请求体为空或不是有效的 JSON"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"code": 500, "message": "无法连接到数据库"}), 500

    cursor = None
    try:
        cursor = conn.cursor()  # 以字典形式返回结果
        today = date.today()  # 获取今天的日期

        delete_sql = """
        DELETE FROM
        whore_service_schedule
        WHERE whore_username = %s AND client_username = %s AND scheduled_time > %s
        """
        cursor.execute(delete_sql, (whore_username, client_username, today))
        conn.commit()
        rows_deleted = cursor.rowcount
        return jsonify({"code": 200, "message": f"成功删除 {rows_deleted} 条数据", "row_deleted": rows_deleted}), 200

    except mysql.connector.Error as e:
        logger.error('删除数据失败: %s', e)
        return jsonify({"code": 500, "message": f"删除数据失败: {e}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() # 使用完毕后将连接归还到连接池

"""user类"""
@dataclass
class User:
    user_id: int
    premium_flag: bool = False
    expired_time: Optional[datetime] = None

"""插入user"""
def insert_user_info(user: User) -> int:
    """
    如果用户不存在，则插入用户信息。
    使用 INSERT IGNORE 实现原子操作，避免竞争条件。
    """
    if not user or not user.user_id:
        raise ValueError("User and user_id cannot be empty.") # 使用更具体的异常类型

    row_added = 0
    sql = "INSERT IGNORE INTO user_info (user_id) VALUES (%s)"

    try:
        # 使用 'with' 语句自动管理连接和游标的关闭
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user.user_id,)) # 注意参数是元组
                conn.commit() # 提交事务，让插入生效
                row_added = cursor.rowcount # rowcount 会返回受影响的行数 (插入成功为1, 忽略为0)
    except mysql.connector.Error as e:
        logger.error(f"Failed to insert user_info for user_id {user.user_id}: {e}")
        # 重新抛出异常，并附带原始异常信息，便于追踪
        raise Exception(f"Database operation failed for user_id {user.user_id}") from e

    return row_added



if __name__ == '__main__':
    # Flask 应用启动时不会直接初始化连接池，而是通过 @app.before_request 确保在第一次请求前初始化
    # 您也可以选择在这里直接调用 init_db_pool()，但这可能会在没有请求时也创建连接池。
    # app.run(debug=True, host='0.0.0.0', port=8848) # 在开发环境中可以使用 debug=True

    app.run(host='0.0.0.0', port=8848) # 生产环境建议关闭 debug 模式
    print("排课服务已启动")