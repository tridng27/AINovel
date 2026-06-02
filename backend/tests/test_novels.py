import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_list_novels_empty(client: AsyncClient):
    res = await client.get("/api/v1/novels")
    assert res.status_code == 200
    data = res.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_novel_requires_auth(client: AsyncClient):
    res = await client.post("/api/v1/novels", json={
        "title": "Unauthorized Novel", "synopsis": "", "genre_ids": [], "tags": [],
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_create_novel_success(client: AsyncClient):
    headers, _ = await register_and_login(client, "author1")
    res = await client.post("/api/v1/novels", json={
        "title": "My First Novel",
        "synopsis": "A great adventure",
        "genre_ids": [],
        "tags": ["fantasy", "adventure"],
    }, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "My First Novel"
    assert data["slug"]  # auto-generated
    assert data["status"] == "ongoing"


@pytest.mark.asyncio
async def test_get_novel_by_slug(client: AsyncClient):
    headers, _ = await register_and_login(client, "author2")
    create = await client.post("/api/v1/novels", json={
        "title": "Slug Test Novel", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    slug = create.json()["slug"]

    res = await client.get(f"/api/v1/novels/{slug}")
    assert res.status_code == 200
    assert res.json()["slug"] == slug


@pytest.mark.asyncio
async def test_get_novel_not_found(client: AsyncClient):
    res = await client.get("/api/v1/novels/nonexistent-slug-abc123")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_novel(client: AsyncClient):
    headers, _ = await register_and_login(client, "author3")
    create = await client.post("/api/v1/novels", json={
        "title": "Update Me", "synopsis": "old", "genre_ids": [], "tags": [],
    }, headers=headers)
    novel_id = create.json()["id"]

    res = await client.put(f"/api/v1/novels/{novel_id}", json={"synopsis": "updated synopsis"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["synopsis"] == "updated synopsis"


@pytest.mark.asyncio
async def test_create_chapter(client: AsyncClient):
    headers, _ = await register_and_login(client, "author4")
    novel = await client.post("/api/v1/novels", json={
        "title": "Chapter Novel", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    novel_id = novel.json()["id"]

    res = await client.post(f"/api/v1/novels/{novel_id}/chapters", json={
        "title": "Chapter One",
        "content": "It was a dark and stormy night...",
    }, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["number"] == 1
    assert data["title"] == "Chapter One"
    assert data["word_count"] > 0


@pytest.mark.asyncio
async def test_chapter_numbering(client: AsyncClient):
    headers, _ = await register_and_login(client, "author5")
    novel = await client.post("/api/v1/novels", json={
        "title": "Multi-Chapter", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    novel_id = novel.json()["id"]

    for i in range(1, 4):
        res = await client.post(f"/api/v1/novels/{novel_id}/chapters", json={
            "title": f"Chapter {i}", "content": "Content here",
        }, headers=headers)
        assert res.json()["number"] == i


@pytest.mark.asyncio
async def test_list_chapters(client: AsyncClient):
    headers, _ = await register_and_login(client, "author6")
    novel = await client.post("/api/v1/novels", json={
        "title": "List Chapters", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    slug = novel.json()["slug"]
    novel_id = novel.json()["id"]

    await client.post(f"/api/v1/novels/{novel_id}/chapters", json={
        "title": "Ch 1", "content": "Content",
    }, headers=headers)

    res = await client.get(f"/api/v1/novels/{slug}/chapters")
    assert res.status_code == 200
    # draft chapters not listed (only published)
    assert isinstance(res.json(), list)
