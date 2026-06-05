from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminStats(BaseModel):
    users: int
    novels: int
    chapters: int
    comments: int
    admins: int


class AdminUserRow(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleUpdate(BaseModel):
    role: str  # reader | author | admin


class AdminNovelRow(BaseModel):
    id: UUID
    title: str
    slug: str
    author_username: str | None
    status: str
    view_count: int
    chapter_count: int
    created_at: datetime


class AdminCommentRow(BaseModel):
    id: UUID
    body: str
    username: str | None
    chapter_id: UUID
    created_at: datetime
