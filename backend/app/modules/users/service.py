"""User profile service — view/edit profile, change password, avatar upload."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.schemas import ChangePasswordRequest, UserProfileUpdate


async def get_profile(user_id: uuid.UUID, db: AsyncSession):
    raise NotImplementedError


async def update_profile(user_id: uuid.UUID, body: UserProfileUpdate, db: AsyncSession):
    raise NotImplementedError


async def change_password(user_id: uuid.UUID, body: ChangePasswordRequest, db: AsyncSession):
    raise NotImplementedError


async def upload_avatar(user_id: uuid.UUID, file_bytes: bytes, content_type: str, db: AsyncSession) -> str:
    """Upload avatar to MinIO, return public URL."""
    raise NotImplementedError


async def get_public_profile(username: str, db: AsyncSession):
    raise NotImplementedError
