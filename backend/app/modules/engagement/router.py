import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorize import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.modules.engagement import schemas, service

router = APIRouter(prefix="/engagement", tags=["engagement"])


@router.put("/progress/{chapter_id}", status_code=204)
async def update_progress(
    chapter_id: uuid.UUID,
    progress_percent: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.upsert_reading_progress(current_user.id, chapter_id, progress_percent, db)


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


@router.put("/novels/{novel_id}/rating", response_model=schemas.RatingResponse)
async def rate_novel(
    novel_id: uuid.UUID,
    body: schemas.RatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.upsert_rating(current_user.id, novel_id, body, db)


@router.post("/users/{user_id}/follow", status_code=204)
async def follow(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.follow_user(current_user.id, user_id, db)


@router.delete("/users/{user_id}/follow", status_code=204)
async def unfollow(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.unfollow_user(current_user.id, user_id, db)
