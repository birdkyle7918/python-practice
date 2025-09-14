# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas

def get_channel(db: Session, channel_id: int):
    """通过ID查询单个频道"""
    return db.query(models.TelegramChannel).filter(models.TelegramChannel.id == channel_id).first()

def get_channel_by_identifier(db: Session, identifier: str):
    """通过频道标识符查询单个频道"""
    return db.query(models.TelegramChannel).filter(models.TelegramChannel.channel_identifier == identifier).first()

def get_channels(db: Session, skip: int = 0, limit: int = 100):
    """查询频道列表（分页）"""
    return db.query(models.TelegramChannel).offset(skip).limit(limit).all()

def get_active_channels(db: Session):
    """获取所有启用的频道，用于定时任务"""
    return db.query(models.TelegramChannel).filter(models.TelegramChannel.is_active == True).all()

def create_channel(db: Session, channel: schemas.ChannelCreate):
    """创建新频道"""
    db_channel = models.TelegramChannel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

def update_channel(db: Session, db_channel: models.TelegramChannel, channel_update: schemas.ChannelUpdate):
    """更新频道信息"""
    update_data = channel_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_channel, key, value)
    db.commit()
    db.refresh(db_channel)
    return db_channel

def delete_channel(db: Session, channel_id: int):
    """删除频道"""
    db_channel = db.query(models.TelegramChannel).filter(models.TelegramChannel.id == channel_id).first()
    if db_channel:
        db.delete(db_channel)
        db.commit()
    return db_channel

def update_last_processed_id(db: Session, channel_id: int, message_id: int):
    """更新频道的last_processed_message_id"""
    db.query(models.TelegramChannel).filter(models.TelegramChannel.id == channel_id).update({"last_processed_message_id": message_id})
    db.commit()