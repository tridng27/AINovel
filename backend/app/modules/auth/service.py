import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_email_verify_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserSession
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse


async def register_user(body: RegisterRequest, db: AsyncSession) -> User:
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(username=body.username, email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(body: LoginRequest, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    db.add(UserSession(
        user_id=user.id,
        token_hash=hashlib.sha256(refresh.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    ))
    await db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


async def refresh_tokens(refresh_token: str, db: AsyncSession) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    result = await db.execute(
        select(UserSession).where(UserSession.token_hash == token_hash, UserSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")

    await db.delete(session)

    access = create_access_token(str(user_id))
    new_refresh = create_refresh_token(str(user_id))
    db.add(UserSession(
        user_id=user_id,
        token_hash=hashlib.sha256(new_refresh.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    ))
    await db.commit()
    return TokenResponse(access_token=access, refresh_token=new_refresh)


async def logout_user(refresh_token: str, db: AsyncSession) -> None:
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    result = await db.execute(select(UserSession).where(UserSession.token_hash == token_hash))
    session = result.scalar_one_or_none()
    if session:
        await db.delete(session)
        await db.commit()


async def _send_email(to: str, subject: str, html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )


async def send_verification_email(user: User) -> None:
    token = create_email_verify_token(str(user.id))
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f"""
    <h2>Xác nhận email AINovel</h2>
    <p>Xin chào <b>{user.username}</b>,</p>
    <p>Click vào link bên dưới để xác nhận email (hiệu lực 24 giờ):</p>
    <a href="{link}">{link}</a>
    """
    await _send_email(user.email, "Xác nhận email AINovel", html)


async def verify_email(token: str, db: AsyncSession) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "email_verify":
            raise ValueError
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_verified:
        return user

    user.is_verified = True
    await db.commit()
    await db.refresh(user)
    return user


async def resend_verification(email: str, db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        # Return silently to prevent email enumeration
        return
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")
    await send_verification_email(user)
