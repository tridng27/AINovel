import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    role: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=500)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class PublicUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None

    model_config = {"from_attributes": True}


class AvatarResponse(BaseModel):
    avatar_url: str
