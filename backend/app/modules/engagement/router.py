import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorize import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.modules.engagement import schemas, service

router = APIRouter(prefix="/engagement", tags=["engagement"])


# ── Reading Progress ──────────────────────────────────────────────────────────

@router.put("/progress/{chapter_id}", response_model=schemas.ReadingProgressResponse)
async def update_progress(
    chapter_id: uuid.UUID,
    body: schemas.ReadingProgressUpsert,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.upsert_reading_progress(current_user.id, chapter_id, body, db)


# ── Bookmarks ─────────────────────────────────────────────────────────────────

@router.get("/bookmarks", response_model=list[schemas.BookmarkResponse])
async def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_bookmarks(current_user.id, db)


@router.post("/bookmarks", response_model=schemas.BookmarkResponse, status_code=201)
async def create_bookmark(
    body: schemas.BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_bookmark(current_user.id, body, db)


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_bookmark(current_user.id, bookmark_id, db)


# ── Reading List ──────────────────────────────────────────────────────────────

@router.get("/reading-list", response_model=list[schemas.ReadingListResponse])
async def get_reading_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_reading_list(current_user.id, db)


@router.put("/reading-list/{novel_id}", response_model=schemas.ReadingListResponse)
async def upsert_reading_list(
    novel_id: uuid.UUID,
    body: schemas.ReadingListUpsert,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.upsert_reading_list(current_user.id, novel_id, body, db)


@router.delete("/reading-list/{novel_id}", status_code=204)
async def remove_reading_list(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.remove_from_reading_list(current_user.id, novel_id, db)


# ── Comments ──────────────────────────────────────────────────────────────────

@router.get("/chapters/{chapter_id}/comments", response_model=list[schemas.CommentResponse])
async def list_comments(chapter_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.list_comments(chapter_id, db)


@router.post("/chapters/{chapter_id}/comments", response_model=schemas.CommentResponse, status_code=201)
async def create_comment(
    chapter_id: uuid.UUID,
    body: schemas.CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_comment(current_user.id, chapter_id, body, db)


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_comment(current_user.id, comment_id, db)


# ── Ratings ───────────────────────────────────────────────────────────────────

@router.put("/novels/{novel_id}/rating", response_model=schemas.RatingResponse)
async def rate_novel(
    novel_id: uuid.UUID,
    body: schemas.RatingUpsert,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.upsert_rating(current_user.id, novel_id, body, db)


# ── Follows ───────────────────────────────────────────────────────────────────

@router.post("/authors/{author_id}/follow", response_model=schemas.FollowResponse, status_code=201)
async def follow_author(
    author_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.follow_author(current_user.id, author_id, db)


@router.delete("/authors/{author_id}/follow", status_code=204)
async def unfollow_author(
    author_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.unfollow_author(current_user.id, author_id, db)
