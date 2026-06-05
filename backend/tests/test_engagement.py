import pytest
from httpx import AsyncClient

from tests.conftest import register_and_login


async def _create_novel_and_chapter(client: AsyncClient, headers: dict) -> tuple[str, str, str]:
    """Returns (novel_id, slug, chapter_id)."""
    novel = await client.post("/api/v1/novels", json={
        "title": "Engagement Novel", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers)
    novel_id = novel.json()["id"]
    slug = novel.json()["slug"]
    chapter = await client.post(f"/api/v1/novels/{novel_id}/chapters", json={
        "title": "Chapter 1", "content": "Some content here",
    }, headers=headers)
    return novel_id, slug, chapter.json()["id"]


# ── Bookmarks ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_list_bookmark(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng1")
    novel_id, _, chapter_id = await _create_novel_and_chapter(client, headers)

    res = await client.post("/api/v1/engagement/bookmarks", json={
        "chapter_id": chapter_id, "note": "Great scene",
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["note"] == "Great scene"

    list_res = await client.get("/api/v1/engagement/bookmarks", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1


@pytest.mark.asyncio
async def test_delete_bookmark(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng2")
    _, _, chapter_id = await _create_novel_and_chapter(client, headers)

    bm = await client.post("/api/v1/engagement/bookmarks", json={"chapter_id": chapter_id}, headers=headers)
    bm_id = bm.json()["id"]

    del_res = await client.delete(f"/api/v1/engagement/bookmarks/{bm_id}", headers=headers)
    assert del_res.status_code == 204

    list_res = await client.get("/api/v1/engagement/bookmarks", headers=headers)
    assert list_res.json() == []


# ── Reading List ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reading_list_upsert(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng3")
    novel_id, _, _ = await _create_novel_and_chapter(client, headers)

    res = await client.put(f"/api/v1/engagement/reading-list/{novel_id}",
                           json={"status": "reading"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "reading"

    # update to completed
    res2 = await client.put(f"/api/v1/engagement/reading-list/{novel_id}",
                            json={"status": "completed"}, headers=headers)
    assert res2.json()["status"] == "completed"


# ── Comments ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_list_comment(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng4")
    _, _, chapter_id = await _create_novel_and_chapter(client, headers)

    res = await client.post(f"/api/v1/engagement/chapters/{chapter_id}/comments",
                            json={"body": "Great chapter!"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["body"] == "Great chapter!"

    list_res = await client.get(f"/api/v1/engagement/chapters/{chapter_id}/comments")
    assert len(list_res.json()) == 1


@pytest.mark.asyncio
async def test_reply_to_comment(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng5")
    _, _, chapter_id = await _create_novel_and_chapter(client, headers)

    parent = await client.post(f"/api/v1/engagement/chapters/{chapter_id}/comments",
                               json={"body": "Parent comment"}, headers=headers)
    parent_id = parent.json()["id"]

    reply = await client.post(f"/api/v1/engagement/chapters/{chapter_id}/comments",
                              json={"body": "Reply", "parent_id": parent_id}, headers=headers)
    assert reply.status_code == 201
    assert reply.json()["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_delete_own_comment(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng6")
    _, _, chapter_id = await _create_novel_and_chapter(client, headers)

    comment = await client.post(f"/api/v1/engagement/chapters/{chapter_id}/comments",
                                json={"body": "To delete"}, headers=headers)
    comment_id = comment.json()["id"]

    res = await client.delete(f"/api/v1/engagement/comments/{comment_id}", headers=headers)
    assert res.status_code == 204


# ── Ratings ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_novel(client: AsyncClient):
    headers, _ = await register_and_login(client, "eng7")
    novel_id, _, _ = await _create_novel_and_chapter(client, headers)

    res = await client.put(f"/api/v1/engagement/novels/{novel_id}/rating",
                           json={"score": 5}, headers=headers)
    assert res.status_code == 200
    assert res.json()["score"] == 5


@pytest.mark.asyncio
async def test_rating_updates_novel_avg(client: AsyncClient):
    headers1, _ = await register_and_login(client, "eng8")
    headers2, _ = await register_and_login(client, "eng9")

    # author creates novel
    novel = await client.post("/api/v1/novels", json={
        "title": "Rated Novel", "synopsis": "", "genre_ids": [], "tags": [],
    }, headers=headers1)
    novel_id = novel.json()["id"]
    slug = novel.json()["slug"]

    # two users rate it
    await client.put(f"/api/v1/engagement/novels/{novel_id}/rating",
                     json={"score": 4}, headers=headers1)
    await client.put(f"/api/v1/engagement/novels/{novel_id}/rating",
                     json={"score": 2}, headers=headers2)

    novel_res = await client.get(f"/api/v1/novels/{slug}")
    assert float(novel_res.json()["rating_avg"]) == 3.0


# ── Follows ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_follow_and_unfollow(client: AsyncClient):
    headers1, user1_id = await register_and_login(client, "eng10")
    headers2, user2_id = await register_and_login(client, "eng11")

    follow = await client.post(f"/api/v1/engagement/authors/{user2_id}/follow", headers=headers1)
    assert follow.status_code == 201

    unfollow = await client.delete(f"/api/v1/engagement/authors/{user2_id}/follow", headers=headers1)
    assert unfollow.status_code == 204


@pytest.mark.asyncio
async def test_cannot_follow_self(client: AsyncClient):
    headers, user_id = await register_and_login(client, "eng12")
    res = await client.post(f"/api/v1/engagement/authors/{user_id}/follow", headers=headers)
    assert res.status_code == 400
