"""Search service — tìm kiếm novel bằng SQL ILIKE (MVP, chưa cần Meilisearch)."""
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel, NovelGenre
from app.models.user import User
from app.modules.search.schemas import SearchHit, SearchRequest, SearchResponse


async def search_novels(req: SearchRequest, db: AsyncSession) -> SearchResponse:
    q = select(Novel, User.username).join(User, Novel.author_id == User.id)

    term = f"%{req.q.strip()}%"
    q = q.where(or_(Novel.title.ilike(term), Novel.synopsis.ilike(term)))
    if req.status:
        q = q.where(Novel.status == req.status)
    if req.genre_id:
        q = q.join(NovelGenre).where(NovelGenre.genre_id == req.genre_id)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()

    q = (
        q.order_by(Novel.view_count.desc())
        .offset((req.page - 1) * req.hits_per_page)
        .limit(req.hits_per_page)
    )
    rows = (await db.execute(q)).all()

    hits = [
        SearchHit(
            id=str(n.id),
            title=n.title,
            slug=n.slug,
            synopsis=n.synopsis,
            author_username=username,
            cover_url=n.cover_image_url,
            view_count=n.view_count,
            rating_avg=float(n.rating_avg) if n.rating_avg is not None else None,
        )
        for n, username in rows
    ]
    total_pages = max(1, (total + req.hits_per_page - 1) // req.hits_per_page)
    return SearchResponse(hits=hits, total=total, page=req.page, total_pages=total_pages)


# Giữ chỗ cho Meilisearch sau này — hiện không cần với SQL search.
async def index_novel(novel_id: uuid.UUID) -> None:
    return None


async def delete_novel_from_index(novel_id: uuid.UUID) -> None:
    return None
