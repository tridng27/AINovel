from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorize import require_admin
from app.core.database import get_db
from app.models.user import User
from app.modules.admin import schemas, service

# require_admin trên toàn router → mọi route đều cần role admin.
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ── Dashboard ─────────────────────────────────────────────────────────────────
@router.get("/stats", response_model=schemas.AdminStats)
async def stats(db: AsyncSession = Depends(get_db)):
    return await service.get_stats(db)


# ── Users ─────────────────────────────────────────────────────────────────────
@router.get("/users", response_model=list[schemas.AdminUserRow])
async def list_users(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await service.list_users(db, limit, offset)


@router.patch("/users/{user_id}/role", response_model=schemas.AdminUserRow)
async def update_user_role(
    user_id: UUID,
    body: schemas.RoleUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_user_role(user_id, body.role, db, admin)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_user(user_id, db, admin)


# ── Novels ────────────────────────────────────────────────────────────────────
@router.get("/novels", response_model=list[schemas.AdminNovelRow])
async def list_novels(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await service.list_novels(db, limit, offset)


@router.delete("/novels/{novel_id}", status_code=204)
async def delete_novel(novel_id: UUID, db: AsyncSession = Depends(get_db)):
    await service.delete_novel(novel_id, db)


# ── Comments ──────────────────────────────────────────────────────────────────
@router.get("/comments", response_model=list[schemas.AdminCommentRow])
async def list_comments(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await service.list_comments(db, limit, offset)


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: UUID, db: AsyncSession = Depends(get_db)):
    await service.delete_comment(comment_id, db)
