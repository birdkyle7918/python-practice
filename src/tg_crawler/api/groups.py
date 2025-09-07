from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from src.tg_crawler.db import models, schemas
from src.tg_crawler.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Group, summary="添加一个监控群组")
async def create_group(group: schemas.GroupCreate, db: AsyncSession = Depends(get_db)):
    db_group = models.MonitoredGroup(group_id=group.group_id, group_name=group.group_name)
    db.add(db_group)
    try:
        await db.commit()
        await db.refresh(db_group)
        return db_group
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Group with ID {group.group_id} already exists.")

@router.get("/", response_model=list[schemas.Group], summary="获取所有监控群组")
async def read_groups(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MonitoredGroup).offset(skip).limit(limit))
    return result.scalars().all()

@router.delete("/{group_id}", summary="删除一个监控群组")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MonitoredGroup).where(models.MonitoredGroup.group_id == group_id))
    db_group = result.scalar_one_or_none()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    await db.delete(db_group)
    await db.commit()
    return {"ok": True, "detail": "Group deleted successfully"}
