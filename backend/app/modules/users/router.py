from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorize import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.modules.users import schemas, service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_profile(current_user.id, db)


@router.patch("/me", response_model=schemas.UserProfileResponse)
async def update_my_profile(
    body: schemas.UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_profile(current_user.id, body, db)


@router.post("/me/password", status_code=204)
async def change_password(
    body: schemas.ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.change_password(current_user.id, body, db)


@router.post("/me/avatar", response_model=schemas.AvatarResponse)
async def upload_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    url = await service.upload_avatar(current_user.id, content, file.content_type or "image/jpeg", db)
    return schemas.AvatarResponse(avatar_url=url)


@router.get("/{username}", response_model=schemas.PublicUserResponse)
async def get_public_profile(username: str, db: AsyncSession = Depends(get_db)):
    return await service.get_public_profile(username, db)
