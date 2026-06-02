import re
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Chapter, Novel, NovelGenre, NovelTag
from app.modules.novels.schemas import ChapterCreate, ChapterUpdate, NovelCreate, NovelUpdate


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return f"{slug}-{uuid.uuid4().hex[:8]}"


async def list_novels(db: AsyncSession, page: int, page_size: int, status: str | None, genre_id: int | None, sort: str):
    q = select(Novel)
    if status:
        q = q.where(Novel.status == status)
    if genre_id:
        q = q.join(NovelGenre).where(NovelGenre.genre_id == genre_id)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    q = q.order_by(getattr(Novel, sort).desc()).offset((page - 1) * page_size).limit(page_size)
    novels = (await db.execute(q)).scalars().all()
    return novels, total


async def get_novel_by_slug(slug: str, db: AsyncSession) -> Novel:
    result = await db.execute(select(Novel).where(Novel.slug == slug))
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


async def create_novel(body: NovelCreate, author_id: uuid.UUID, db: AsyncSession) -> Novel:
    novel = Novel(author_id=author_id, title=body.title, slug=_slugify(body.title), synopsis=body.synopsis)
    db.add(novel)
    await db.flush()
    for gid in body.genre_ids:
        db.add(NovelGenre(novel_id=novel.id, genre_id=gid))
    for tag in body.tags:
        db.add(NovelTag(novel_id=novel.id, tag=tag))
    await db.commit()
    await db.refresh(novel)
    return novel


async def update_novel(novel_id: uuid.UUID, author_id: uuid.UUID, body: NovelUpdate, db: AsyncSession) -> Novel:
    result = await db.execute(select(Novel).where(Novel.id == novel_id, Novel.author_id == author_id))
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(novel, field, value)
    await db.commit()
    await db.refresh(novel)
    return novel


async def list_chapters(novel_id: uuid.UUID, db: AsyncSession) -> list[Chapter]:
    result = await db.execute(
        select(Chapter)
        .where(Chapter.novel_id == novel_id, Chapter.status == "published")
        .order_by(Chapter.number)
    )
    return result.scalars().all()


async def get_chapter(novel_id: uuid.UUID, number: int, db: AsyncSession) -> Chapter:
    result = await db.execute(select(Chapter).where(Chapter.novel_id == novel_id, Chapter.number == number))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter


async def create_chapter(novel_id: uuid.UUID, author_id: uuid.UUID, body: ChapterCreate, db: AsyncSession) -> Chapter:
    result = await db.execute(select(Novel).where(Novel.id == novel_id, Novel.author_id == author_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    count = (await db.execute(select(func.count()).where(Chapter.novel_id == novel_id))).scalar_one()
    chapter = Chapter(
        novel_id=novel_id,
        number=count + 1,
        title=body.title,
        content=body.content,
        word_count=len(body.content.split()) if body.content else 0,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter


async def update_chapter(novel_id: uuid.UUID, chapter_id: uuid.UUID, author_id: uuid.UUID, body: ChapterUpdate, db: AsyncSession) -> Chapter:
    novel_result = await db.execute(select(Novel).where(Novel.id == novel_id, Novel.author_id == author_id))
    if not novel_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    ch_result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.novel_id == novel_id))
    chapter = ch_result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(chapter, field, value)
    if body.content:
        chapter.word_count = len(body.content.split())

    await db.commit()
    await db.refresh(chapter)
    return chapter
