from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NovelCreate(BaseModel):
    title: str
    synopsis: str | None = None
    genre_ids: list[int] = []
    tags: list[str] = []


class NovelUpdate(BaseModel):
    title: str | None = None
    synopsis: str | None = None
    status: str | None = None


class NovelResponse(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    slug: str
    synopsis: str | None
    cover_image_url: str | None
    status: str
    view_count: int
    word_count: int
    rating_avg: float
    chapter_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NovelListResponse(BaseModel):
    items: list[NovelResponse]
    total: int
    page: int
    page_size: int


class ChapterCreate(BaseModel):
    title: str
    content: str | None = None


class ChapterUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None


class ChapterResponse(BaseModel):
    id: UUID
    novel_id: UUID
    number: int
    title: str
    content: str | None
    word_count: int
    status: str
    published_at: datetime | None
    view_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
