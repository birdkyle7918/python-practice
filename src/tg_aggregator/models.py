# app/models.py

from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Text, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class TelegramChannel(Base):
    __tablename__ = "telegram_channels"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    channel_identifier = Column(String(128), unique=True, nullable=False, index=True, comment="Telegram频道的唯一标识符")
    channel_name = Column(String(255), nullable=True, comment="频道名称")
    last_processed_message_id = Column(Integer, default=0, comment="最后处理过的消息ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    notes = Column(Text, nullable=True, comment="备注信息")
    tag = Column(String(255), nullable=True, comment="标签")

    # 使用数据库函数自动管理时间
    gmt_create = Column(TIMESTAMP, server_default=func.now(), comment="记录创建时间")
    gmt_modified = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="记录最后修改时间")