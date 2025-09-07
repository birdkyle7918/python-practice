from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class MonitoredGroup(Base):
    __tablename__ = 'monitored_groups'
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(BigInteger, unique=True, nullable=False)
    group_name = Column(String(255), nullable=False)
    last_message_id = Column(BigInteger, nullable=True)
    gmt_create = Column(TIMESTAMP, server_default=func.now())
    gmt_modified = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=True)
    gmt_create = Column(TIMESTAMP, server_default=func.now())
    gmt_modified = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
