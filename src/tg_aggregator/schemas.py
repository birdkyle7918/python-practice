# app/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 基础模型，包含所有模型共有的字段
class ChannelBase(BaseModel):
    channel_identifier: str = Field(..., description="Telegram频道的唯一标识符, 如@username")
    channel_name: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None
    tag: Optional[str] = None

# 创建频道时使用的模型 (输入)
class ChannelCreate(ChannelBase):
    pass

# 更新频道时使用的模型 (输入)
class ChannelUpdate(BaseModel):
    channel_identifier: Optional[str] = None
    channel_name: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    tag: Optional[str] = None

# 从数据库读取并返回给客户端的模型 (输出)
class Channel(ChannelBase):
    id: int
    last_processed_message_id: int
    gmt_create: datetime
    gmt_modified: datetime
    tag: Optional[str] = None

    class Config:
        from_attributes = True # 兼容ORM模式