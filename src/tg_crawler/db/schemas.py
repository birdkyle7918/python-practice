from pydantic import BaseModel
from datetime import datetime


class GroupBase(BaseModel):
    group_id: int
    group_name: str


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    last_message_id: int | None = None
    gmt_create: datetime
    gmt_modified: datetime

    class Config:
        from_attributes = True