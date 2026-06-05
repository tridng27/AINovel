import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorize import get_current_user, require_author
from app.core.database import get_db
from app.models.user import User
from app.modules.novels import service
from app.modules.novels.schemas import (
    ChapterCreate,
    ChapterResponse,
    ChapterUpdate,
    NovelCreate,
    NovelListResponse,
    NovelResponse,
    NovelUpdate,
)

router = APIRouter(prefix="/novels", tags=["Novels"])


@router.get("", response_model=NovelListResponse)
async def list_novels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    genre_id: int | None = None,
    sort: str = Query("updated_at", pattern="^(updated_at|view_count|rating_avg)$"),
    db: AsyncSession = Depends(get_db),
):
    novels, total = await service.list_novels(db, page, page_size, status, genre_id, sort)
    return NovelListResponse(items=novels, total=total, page=page, page_size=page_size)


@router.get("/{slug}", response_model=NovelResponse)
async def get_novel(slug: str, db: AsyncSession = Depends(get_db)):
    return await service.get_novel_by_slug(slug, db)


@router.get("/{slug}/chapters", response_model=list[ChapterResponse])
async def list_chapters(slug: str, db: AsyncSession = Depends(get_db)):
    novel = await service.get_novel_by_slug(slug, db)
    return await service.list_chapters(novel.id, db)


@router.get("/{slug}/chapters/{number}", response_model=ChapterResponse)
async def get_chapter(slug: str, number: int, db: AsyncSession = Depends(get_db)):
    novel = await service.get_novel_by_slug(slug, db)
    return await service.get_chapter(novel.id, number, db)


@router.post("", response_model=NovelResponse, status_code=201)
async def create_novel(
    body: NovelCreate,
    author: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_novel(body, author.id, db)


@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(
    novel_id: uuid.UUID,
    body: NovelUpdate,
    author: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_novel(novel_id, author.id, body, db)


@router.post("/{novel_id}/chapters", response_model=ChapterResponse, status_code=201)
async def create_chapter(
    novel_id: uuid.UUID,
    body: ChapterCreate,
    author: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_chapter(novel_id, author.id, body, db)


@router.put("/{novel_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    novel_id: uuid.UUID,
    chapter_id: uuid.UUID,
    body: ChapterUpdate,
    author: User = Depends(require_author),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_chapter(novel_id, chapter_id, author.id, body, db)
