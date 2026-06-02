import uuid
from io import BytesIO

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.core.storage import COVER_BUCKET, get_minio
from app.models.user import User
from app.modules.users.schemas import ChangePasswordRequest, UserProfileUpdate

AVATAR_BUCKET = "avatars"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB


async def get_profile(user_id: uuid.UUID, db: AsyncSession) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def update_profile(user_id: uuid.UUID, body: UserProfileUpdate, db: AsyncSession) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(user_id: uuid.UUID, body: ChangePasswordRequest, db: AsyncSession) -> None:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user.password_hash = hash_password(body.new_password)
    await db.commit()


async def upload_avatar(user_id: uuid.UUID, file_bytes: bytes, content_type: str, db: AsyncSession) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only JPEG, PNG, WebP allowed")
    if len(file_bytes) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 5 MB)")

    client = get_minio()
    ext = content_type.split("/")[1]
    object_name = f"{user_id}.{ext}"

    if not client.bucket_exists(AVATAR_BUCKET):
        client.make_bucket(AVATAR_BUCKET)

    client.put_object(
        AVATAR_BUCKET,
        object_name,
        BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type,
    )

    avatar_url = f"/storage/{AVATAR_BUCKET}/{object_name}"

    user = await db.get(User, user_id)
    if user:
        user.avatar_url = avatar_url
        await db.commit()

    return avatar_url


async def get_public_profile(username: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
