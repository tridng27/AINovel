import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Reading Progress ──────────────────────────────────────────────────────────

class ReadingProgressUpsert(BaseModel):
    scroll_percent: int = Field(ge=0, le=100)


class ReadingProgressResponse(BaseModel):
    user_id: uuid.UUID
    chapter_id: uuid.UUID
    scroll_percent: int
    last_read_at: datetime

    model_config = {"from_attributes": True}


# ── Bookmarks ─────────────────────────────────────────────────────────────────

class BookmarkCreate(BaseModel):
    chapter_id: uuid.UUID
    note: str | None = None


class BookmarkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    chapter_id: uuid.UUID
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Reading List ──────────────────────────────────────────────────────────────

ReadingListStatus = Literal["plan_to_read", "reading", "completed", "dropped"]


class ReadingListUpsert(BaseModel):
    status: ReadingListStatus


class ReadingListResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    novel_id: uuid.UUID
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Comments ──────────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: uuid.UUID | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    chapter_id: uuid.UUID
    body: str
    parent_id: uuid.UUID | None
    like_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Ratings ───────────────────────────────────────────────────────────────────

class RatingUpsert(BaseModel):
    score: int = Field(ge=1, le=5)
    review_text: str | None = None


class RatingResponse(BaseModel):
    user_id: uuid.UUID
    novel_id: uuid.UUID
    score: int
    review_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Follows ───────────────────────────────────────────────────────────────────

class FollowResponse(BaseModel):
    follower_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
