from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engagement import Comment
from app.models.novel import Chapter, Novel
from app.models.user import User
from app.modules.admin import schemas

VALID_ROLES = {"reader", "author", "admin"}


async def get_stats(db: AsyncSession) -> schemas.AdminStats:
    return schemas.AdminStats(
        users=await db.scalar(select(func.count()).select_from(User)),
        novels=await db.scalar(select(func.count()).select_from(Novel)),
        chapters=await db.scalar(select(func.count()).select_from(Chapter)),
        comments=await db.scalar(select(func.count()).select_from(Comment)),
        admins=await db.scalar(select(func.count()).select_from(User).where(User.role == "admin")),
    )


async def list_users(db: AsyncSession, limit: int, offset: int) -> list[User]:
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def update_user_role(user_id: UUID, role: str, db: AsyncSession, current_admin: User) -> User:
    if role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role không hợp lệ")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy user")
    if user.id == current_admin.id and role != "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể tự gỡ quyền admin của chính mình")
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user_id: UUID, db: AsyncSession, current_admin: User) -> None:
    if user_id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể tự xóa chính mình")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy user")
    await db.delete(user)
    await db.commit()


async def list_novels(db: AsyncSession, limit: int, offset: int) -> list[schemas.AdminNovelRow]:
    result = await db.execute(
        select(Novel, User.username)
        .join(User, Novel.author_id == User.id)
        .order_by(Novel.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [
        schemas.AdminNovelRow(
            id=novel.id,
            title=novel.title,
            slug=novel.slug,
            author_username=username,
            status=novel.status,
            view_count=novel.view_count,
            chapter_count=novel.chapter_count,
            created_at=novel.created_at,
        )
        for novel, username in result.all()
    ]


async def delete_novel(novel_id: UUID, db: AsyncSession) -> None:
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy truyện")
    await db.delete(novel)
    await db.commit()


async def list_comments(db: AsyncSession, limit: int, offset: int) -> list[schemas.AdminCommentRow]:
    result = await db.execute(
        select(Comment, User.username)
        .join(User, Comment.user_id == User.id)
        .order_by(Comment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [
        schemas.AdminCommentRow(
            id=c.id,
            body=c.body,
            username=username,
            chapter_id=c.chapter_id,
            created_at=c.created_at,
        )
        for c, username in result.all()
    ]


async def delete_comment(comment_id: UUID, db: AsyncSession) -> None:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bình luận")
    await db.delete(comment)
    await db.commit()
