import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, suffix: str = "") -> dict:
    res = await client.post("/api/v1/auth/register", json={
        "username": f"author{suffix}", "email": f"author{suffix}@example.com", "password": "Password123!",
    })
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.mark.asyncio
async def test_create_novel(client: AsyncClient):
    headers = await _auth_headers(client, "1")
    res = await client.post("/api/v1/novels", json={
        "title": "My Novel", "synopsis": "A great story", "genre_ids": [], "tags": [],
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["title"] == "My Novel"


@pytest.mark.asyncio
async def test_list_novels(client: AsyncClient):
    res = await client.get("/api/v1/novels")
    assert res.status_code == 200
    assert "items" in res.json()


@pytest.mark.asyncio
async def test_get_novel_by_slug(client: AsyncClient):
    headers = await _auth_headers(client, "2")
    create = await client.post("/api/v1/novels", json={
        "title": "Slug Novel", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    slug = create.json()["slug"]
    res = await client.get(f"/api/v1/novels/{slug}")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_create_chapter(client: AsyncClient):
    headers = await _auth_headers(client, "3")
    novel = await client.post("/api/v1/novels", json={
        "title": "Chapter Novel", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    novel_id = novel.json()["id"]
    res = await client.post(f"/api/v1/novels/{novel_id}/chapters", json={
        "title": "Chapter 1", "content": "Once upon a time...",
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["number"] == 1
