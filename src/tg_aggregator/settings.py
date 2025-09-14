# app/settings.py
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 加载 .env 文件
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8')

    # Telegram Client API 配置
    API_ID: int
    API_HASH: str
    SESSION_NAME: str

    # 数据库配置
    DATABASE_URL: str

    # 聚合器配置
    DESTINATION_CHANNEL_ID: int
    SCHEDULE_MINUTES: int

# 创建一个全局可用的配置实例
DB_URL = os.getenv("DB_URL")
TELEGRAM_DESTINATION_CHANNEL_ID = int(os.getenv("TELEGRAM_DESTINATION_CHANNEL_ID"))
SCHEDULE_MINUTES = int(os.getenv("SCHEDULE_MINUTES"))
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")


settings = Settings(API_ID=TELEGRAM_API_ID, API_HASH=TELEGRAM_API_HASH, SESSION_NAME="my_session",
                    DATABASE_URL=DB_URL, DESTINATION_CHANNEL_ID=TELEGRAM_DESTINATION_CHANNEL_ID, SCHEDULE_MINUTES=SCHEDULE_MINUTES)