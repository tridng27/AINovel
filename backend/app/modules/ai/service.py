import uuid
from typing import AsyncGenerator

import anthropic
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai import AIJobResult, AINovelContext
from app.models.novel import Novel

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def get_novel_for_author(novel_id: uuid.UUID, author_id: uuid.UUID, db: AsyncSession) -> Novel:
    result = await db.execute(select(Novel).where(Novel.id == novel_id, Novel.author_id == author_id))
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


async def stream_completion(novel: Novel, text: str) -> AsyncGenerator[str, None]:
    async with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=f"You are a writing assistant for the novel '{novel.title}'. Continue the text naturally.",
        messages=[{"role": "user", "content": text}],
    ) as stream:
        async for chunk in stream.text_stream:
            yield chunk


async def stream_rewrite(novel: Novel, text: str, instruction: str) -> AsyncGenerator[str, None]:
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=f"You are a writing assistant for the novel '{novel.title}'.",
        messages=[{"role": "user", "content": f"Rewrite the following. Instruction: {instruction}\n\nText:\n{text}"}],
    ) as stream:
        async for chunk in stream.text_stream:
            yield chunk


async def stream_dialogue(novel: Novel, char_a: str, char_b: str, context: str | None) -> AsyncGenerator[str, None]:
    prompt = f"Write a natural dialogue between {char_a} and {char_b}."
    if context:
        prompt += f"\n\nContext: {context}"
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=f"You are a writing assistant for the novel '{novel.title}'.",
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for chunk in stream.text_stream:
            yield chunk


async def enqueue_continuity_check(novel_id: uuid.UUID, db: AsyncSession) -> AIJobResult:
    from app.worker.tasks import check_chapter_continuity
    check_chapter_continuity.delay(str(novel_id))
    job = AIJobResult(job_type="continuity_check", novel_id=novel_id, input_hash=str(novel_id), model_used="claude-sonnet-4-6")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def enqueue_arc_plan(novel: Novel, chapter_count: int, db: AsyncSession) -> AIJobResult:
    from app.worker.tasks import generate_arc_plan
    generate_arc_plan.delay(str(novel.id), novel.synopsis or "", chapter_count)
    job = AIJobResult(job_type="arc_plan", novel_id=novel.id, input_hash=f"{novel.id}-{chapter_count}", model_used="claude-sonnet-4-6")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job(job_id: uuid.UUID, db: AsyncSession) -> AIJobResult:
    result = await db.execute(select(AIJobResult).where(AIJobResult.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


async def get_context(novel_id: uuid.UUID, db: AsyncSession) -> AINovelContext:
    result = await db.execute(select(AINovelContext).where(AINovelContext.novel_id == novel_id))
    ctx = result.scalar_one_or_none()
    if not ctx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
    return ctx


async def enqueue_context_sync(novel_id: uuid.UUID) -> None:
    from app.worker.tasks import sync_novel_context
    sync_novel_context.delay(str(novel_id))
