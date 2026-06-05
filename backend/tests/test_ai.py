"""AI endpoint tests — SSE streaming and async jobs.
SSE tests require a real Anthropic key; skipped in CI unless ANTHROPIC_API_KEY is set.
"""
import os
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)


async def _auth_and_novel(client: AsyncClient, suffix: str = "") -> tuple[dict, str]:
    reg = await client.post("/api/v1/auth/register", json={
        "username": f"ai{suffix}", "email": f"ai{suffix}@example.com", "password": "Password123!",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    novel = await client.post("/api/v1/novels", json={
        "title": "AI Novel", "synopsis": "AI test", "genre_ids": [], "tags": [],
    }, headers=headers)
    return headers, novel.json()["id"]


@pytest.mark.asyncio
async def test_stream_completion(client: AsyncClient):
    headers, novel_id = await _auth_and_novel(client, "1")
    res = await client.post(f"/api/v1/ai/novels/{novel_id}/complete", json={
        "text": "The dragon roared",
    }, headers=headers)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_job_status(client: AsyncClient):
    headers, novel_id = await _auth_and_novel(client, "2")
    enqueue = await client.post(f"/api/v1/ai/novels/{novel_id}/continuity-check", headers=headers)
    assert enqueue.status_code == 202
    job_id = enqueue.json()["id"]
    status = await client.get(f"/api/v1/ai/jobs/{job_id}", headers=headers)
    assert status.status_code == 200
