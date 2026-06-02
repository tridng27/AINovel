"""Engagement tests — bookmarks, comments, ratings, follows.
All service functions are NotImplementedError stubs; tests are skipped until feature/engagement is merged.
"""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.skip(reason="feature/engagement not yet merged")


async def _auth_headers(client: AsyncClient, suffix: str = "") -> dict:
    res = await client.post("/api/v1/auth/register", json={
        "username": f"eng{suffix}", "email": f"eng{suffix}@example.com", "password": "Password123!",
    })
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.mark.asyncio
async def test_create_bookmark(client: AsyncClient):
    pass


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient):
    pass


@pytest.mark.asyncio
async def test_rate_novel(client: AsyncClient):
    pass
