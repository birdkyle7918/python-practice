import os
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
# load_dotenv() 会自动寻找 .env 文件
load_dotenv()


class Settings:
    # 数据库配置
    DB_USER: str = os.getenv("DB_USER", "tg_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "tg")
    DATABASE_URL: str = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Telegram 配置
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    TARGET_CHANNEL_ID: str = os.getenv("TARGET_CHANNEL_ID")

    # 检查关键配置是否存在
    if not BOT_TOKEN or not TARGET_CHANNEL_ID:
        raise ValueError("请在环境变量中配置 BOT_TOKEN 和 TARGET_CHANNEL_ID")


settings = Settings()
