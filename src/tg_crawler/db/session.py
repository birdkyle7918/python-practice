from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio.base import ProxyComparable
from sqlalchemy.orm import sessionmaker
from typing import Callable

from src.tg_crawler.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)

# 通过添加 Callable[[...], AsyncSession] 的类型注解来解决IDE的类型警告
AsyncSessionLocal: Callable[[], AsyncSession] = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
) # type: ignore

async def get_db():
    """
    FastAPI dependency that provides a database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

