import json
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.authorize import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.modules.ai import service
from app.modules.ai.schemas import (
    AIContextResponse,
    AIJobResponse,
    ArcPlanRequest,
    CompletionRequest,
    DialogueRequest,
    RewriteRequest,
)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/novels/{novel_id}/complete")
async def stream_completion(
    novel_id: uuid.UUID,
    body: CompletionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    novel = await service.get_novel_for_author(novel_id, user.id, db)

    async def generate():
        async for chunk in service.stream_completion(novel, body.text):
            yield {"data": json.dumps({"token": chunk})}

    return EventSourceResponse(generate())


@router.post("/novels/{novel_id}/rewrite")
async def stream_rewrite(
    novel_id: uuid.UUID,
    body: RewriteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    novel = await service.get_novel_for_author(novel_id, user.id, db)

    async def generate():
        async for chunk in service.stream_rewrite(novel, body.text, body.instruction):
            yield {"data": json.dumps({"token": chunk})}

    return EventSourceResponse(generate())


@router.post("/novels/{novel_id}/dialogue")
async def stream_dialogue(
    novel_id: uuid.UUID,
    body: DialogueRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    novel = await service.get_novel_for_author(novel_id, user.id, db)

    async def generate():
        async for chunk in service.stream_dialogue(novel, body.character_a, body.character_b, body.context):
            yield {"data": json.dumps({"token": chunk})}

    return EventSourceResponse(generate())


@router.post("/novels/{novel_id}/continuity-check", response_model=AIJobResponse, status_code=202)
async def continuity_check(
    novel_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.get_novel_for_author(novel_id, user.id, db)
    return await service.enqueue_continuity_check(novel_id, db)


@router.post("/novels/{novel_id}/arc-plan", response_model=AIJobResponse, status_code=202)
async def arc_plan(
    novel_id: uuid.UUID,
    body: ArcPlanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    novel = await service.get_novel_for_author(novel_id, user.id, db)
    return await service.enqueue_arc_plan(novel, body.chapter_count, db)


@router.get("/jobs/{job_id}", response_model=AIJobResponse)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_job(job_id, db)


@router.get("/novels/{novel_id}/context", response_model=AIContextResponse)
async def get_context(
    novel_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.get_novel_for_author(novel_id, user.id, db)
    return await service.get_context(novel_id, db)


@router.post("/novels/{novel_id}/context/sync", status_code=202)
async def sync_context(
    novel_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.get_novel_for_author(novel_id, user.id, db)
    await service.enqueue_context_sync(novel_id)
    return {"detail": "Context sync queued"}
