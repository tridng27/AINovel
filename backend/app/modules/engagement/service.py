import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engagement import Bookmark, Comment, Follow, Rating, ReadingList, ReadingProgress
from app.models.novel import Novel
from app.modules.engagement.schemas import (
    BookmarkCreate,
    CommentCreate,
    RatingUpsert,
    ReadingListUpsert,
    ReadingProgressUpsert,
)


# ── Reading Progress ──────────────────────────────────────────────────────────

async def upsert_reading_progress(
    user_id: uuid.UUID, chapter_id: uuid.UUID, body: ReadingProgressUpsert, db: AsyncSession
) -> ReadingProgress:
    result = await db.execute(
        select(ReadingProgress).where(
            ReadingProgress.user_id == user_id,
            ReadingProgress.chapter_id == chapter_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress:
        progress.scroll_percent = body.scroll_percent
    else:
        progress = ReadingProgress(user_id=user_id, chapter_id=chapter_id, scroll_percent=body.scroll_percent)
        db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress


# ── Bookmarks ─────────────────────────────────────────────────────────────────

async def list_bookmarks(user_id: uuid.UUID, db: AsyncSession) -> list[Bookmark]:
    result = await db.execute(
        select(Bookmark).where(Bookmark.user_id == user_id).order_by(Bookmark.created_at.desc())
    )
    return list(result.scalars().all())


async def create_bookmark(user_id: uuid.UUID, body: BookmarkCreate, db: AsyncSession) -> Bookmark:
    bookmark = Bookmark(user_id=user_id, chapter_id=body.chapter_id, note=body.note)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


async def delete_bookmark(user_id: uuid.UUID, bookmark_id: uuid.UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    await db.delete(bookmark)
    await db.commit()


# ── Reading List ──────────────────────────────────────────────────────────────

async def upsert_reading_list(
    user_id: uuid.UUID, novel_id: uuid.UUID, body: ReadingListUpsert, db: AsyncSession
) -> ReadingList:
    result = await db.execute(
        select(ReadingList).where(ReadingList.user_id == user_id, ReadingList.novel_id == novel_id)
    )
    entry = result.scalar_one_or_none()
    if entry:
        entry.status = body.status
    else:
        entry = ReadingList(user_id=user_id, novel_id=novel_id, status=body.status)
        db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_reading_list(user_id: uuid.UUID, db: AsyncSession) -> list[ReadingList]:
    result = await db.execute(
        select(ReadingList).where(ReadingList.user_id == user_id).order_by(ReadingList.updated_at.desc())
    )
    return list(result.scalars().all())


async def remove_from_reading_list(user_id: uuid.UUID, novel_id: uuid.UUID, db: AsyncSession) -> None:
    await db.execute(
        delete(ReadingList).where(ReadingList.user_id == user_id, ReadingList.novel_id == novel_id)
    )
    await db.commit()


# ── Comments ──────────────────────────────────────────────────────────────────

async def list_comments(chapter_id: uuid.UUID, db: AsyncSession) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.chapter_id == chapter_id, Comment.parent_id.is_(None))
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().all())


async def create_comment(
    user_id: uuid.UUID, chapter_id: uuid.UUID, body: CommentCreate, db: AsyncSession
) -> Comment:
    if body.parent_id:
        parent = await db.get(Comment, body.parent_id)
        if not parent or parent.chapter_id != chapter_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent comment not found")

    comment = Comment(user_id=user_id, chapter_id=chapter_id, body=body.body, parent_id=body.parent_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(user_id: uuid.UUID, comment_id: uuid.UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.user_id == user_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await db.delete(comment)
    await db.commit()


# ── Ratings ───────────────────────────────────────────────────────────────────

async def upsert_rating(
    user_id: uuid.UUID, novel_id: uuid.UUID, body: RatingUpsert, db: AsyncSession
) -> Rating:
    result = await db.execute(
        select(Rating).where(Rating.user_id == user_id, Rating.novel_id == novel_id)
    )
    rating = result.scalar_one_or_none()
    if rating:
        rating.score = body.score
        rating.review_text = body.review_text
    else:
        rating = Rating(user_id=user_id, novel_id=novel_id, score=body.score, review_text=body.review_text)
        db.add(rating)

    await db.commit()
    await db.refresh(rating)

    # recalculate novel average rating
    avg = await db.execute(
        select(func.avg(Rating.score)).where(Rating.novel_id == novel_id)
    )
    avg_score = avg.scalar_one() or 0
    novel = await db.get(Novel, novel_id)
    if novel:
        novel.rating_avg = round(float(avg_score), 2)
        await db.commit()

    return rating


# ── Follows ───────────────────────────────────────────────────────────────────

async def follow_author(follower_id: uuid.UUID, author_id: uuid.UUID, db: AsyncSession) -> Follow:
    if follower_id == author_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    result = await db.execute(
        select(Follow).where(Follow.follower_id == follower_id, Follow.author_id == author_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already following")

    follow = Follow(follower_id=follower_id, author_id=author_id)
    db.add(follow)
    await db.commit()
    await db.refresh(follow)
    return follow


async def unfollow_author(follower_id: uuid.UUID, author_id: uuid.UUID, db: AsyncSession) -> None:
    await db.execute(
        delete(Follow).where(Follow.follower_id == follower_id, Follow.author_id == author_id)
    )
    await db.commit()
