import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.main import app

# Đọc từ env (CI truyền DATABASE_URL); fallback cho chạy local.
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
)

# NullPool: mỗi test (event loop riêng) tạo connection mới, không tái dùng chéo loop.
engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Helpers ────────────────────────────────────────────────────────────────────

async def register_and_login(client: AsyncClient, suffix: str = "") -> tuple[dict, str]:
    """Register a user and return (token_headers, user_id). Register auto-logs-in."""
    res = await client.post("/api/v1/auth/register", json={
        "username": f"user{suffix}",
        "email": f"user{suffix}@test.com",
        "password": "Password123!",
    })
    data = res.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return headers, data["id"]
