"""Engagement service — reading progress, bookmarks, comments, ratings, follows."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.engagement.schemas import BookmarkCreate, CommentCreate, RatingCreate


async def upsert_reading_progress(
    user_id: uuid.UUID, chapter_id: uuid.UUID, progress_percent: float, db: AsyncSession
):
    raise NotImplementedError


async def list_bookmarks(user_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError


async def create_bookmark(user_id: uuid.UUID, body: BookmarkCreate, db: AsyncSession):
    raise NotImplementedError


async def delete_bookmark(user_id: uuid.UUID, bookmark_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError


async def list_comments(chapter_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError


async def create_comment(user_id: uuid.UUID, chapter_id: uuid.UUID, body: CommentCreate, db: AsyncSession):
    raise NotImplementedError


async def delete_comment(user_id: uuid.UUID, comment_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError


async def upsert_rating(user_id: uuid.UUID, novel_id: uuid.UUID, body: RatingCreate, db: AsyncSession):
    raise NotImplementedError


async def follow_user(follower_id: uuid.UUID, following_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError


async def unfollow_user(follower_id: uuid.UUID, following_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError
