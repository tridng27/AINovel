import uuid
from datetime import datetime

from pydantic import BaseModel


class ReadingProgressResponse(BaseModel):
    novel_id: uuid.UUID
    chapter_id: uuid.UUID
    progress_percent: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookmarkCreate(BaseModel):
    novel_id: uuid.UUID
    chapter_id: uuid.UUID | None = None
    note: str | None = None


class BookmarkResponse(BaseModel):
    id: uuid.UUID
    novel_id: uuid.UUID
    chapter_id: uuid.UUID | None
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str
    parent_id: uuid.UUID | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    chapter_id: uuid.UUID
    content: str
    parent_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RatingCreate(BaseModel):
    score: int  # 1–5


class RatingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    novel_id: uuid.UUID
    score: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FollowResponse(BaseModel):
    follower_id: uuid.UUID
    following_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
