from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorize import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await service.register_user(body, db)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await service.login_user(body, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await service.refresh_tokens(body.refresh_token, db)


@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await service.logout_user(body.refresh_token, db)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
