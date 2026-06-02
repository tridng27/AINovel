import asyncio
import uuid

import anthropic

from app.worker.celery_app import celery_app

_anthropic = anthropic.Anthropic()


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    # Celery tasks use sync SQLAlchemy (not async)
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    engine = create_engine(sync_url)
    Session = sessionmaker(bind=engine)
    return Session()


# ── AI Tasks ──────────────────────────────────────────────────────────────────

@celery_app.task(name="check_chapter_continuity", bind=True, max_retries=2)
def check_chapter_continuity(self, novel_id: str):
    from sqlalchemy import select
    from app.models.novel import Chapter, Novel
    from app.models.ai import AIJobResult

    db = _get_db_session()
    try:
        novel = db.get(Novel, uuid.UUID(novel_id))
        if not novel:
            return

        chapters = db.execute(
            select(Chapter)
            .where(Chapter.novel_id == novel.id, Chapter.status == "published")
            .order_by(Chapter.number)
        ).scalars().all()

        if not chapters:
            return

        chapter_texts = "\n\n".join(
            f"Chapter {ch.number}: {ch.title}\n{(ch.content or '')[:500]}"
            for ch in chapters[-5:]  # last 5 chapters to stay within token limits
        )

        response = _anthropic.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are a story continuity checker. Identify any plot holes, character inconsistencies, or continuity errors.",
            messages=[{"role": "user", "content": f"Check continuity in these chapters:\n\n{chapter_texts}"}],
        )
        result_text = response.content[0].text

        job = db.execute(
            select(AIJobResult)
            .where(AIJobResult.novel_id == novel.id, AIJobResult.job_type == "continuity_check")
            .order_by(AIJobResult.created_at.desc())
        ).scalars().first()

        if job:
            job.result = result_text
            job.tokens_used = response.usage.input_tokens + response.usage.output_tokens
            db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery_app.task(name="generate_arc_plan", bind=True, max_retries=2)
def generate_arc_plan(self, novel_id: str, synopsis: str, chapter_count: int):
    from sqlalchemy import select
    from app.models.novel import Novel
    from app.models.ai import AIJobResult

    db = _get_db_session()
    try:
        novel = db.get(Novel, uuid.UUID(novel_id))
        if not novel:
            return

        prompt = (
            f"Novel: {novel.title}\nSynopsis: {synopsis}\n"
            f"Current chapters: {chapter_count}\n\n"
            "Create a detailed story arc plan for the next 10 chapters. "
            "Include: chapter goals, key events, character development, pacing notes."
        )

        response = _anthropic.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system="You are a professional story architect helping plan novel arcs.",
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.content[0].text

        job = db.execute(
            select(AIJobResult)
            .where(AIJobResult.novel_id == novel.id, AIJobResult.job_type == "arc_plan")
            .order_by(AIJobResult.created_at.desc())
        ).scalars().first()

        if job:
            job.result = result_text
            job.tokens_used = response.usage.input_tokens + response.usage.output_tokens
            db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(name="sync_novel_context", bind=True, max_retries=2)
def sync_novel_context(self, novel_id: str):
    """Summarise each unsynced chapter and update AINovelContext."""
    from sqlalchemy import select
    from app.models.novel import Chapter, Novel
    from app.models.ai import AINovelContext

    db = _get_db_session()
    try:
        novel = db.get(Novel, uuid.UUID(novel_id))
        if not novel:
            return

        ctx = db.execute(
            select(AINovelContext).where(AINovelContext.novel_id == novel.id)
        ).scalar_one_or_none()

        if not ctx:
            ctx = AINovelContext(novel_id=novel.id, chapter_summaries=[], last_synced_chapter=0)
            db.add(ctx)

        chapters = db.execute(
            select(Chapter)
            .where(Chapter.novel_id == novel.id, Chapter.number > ctx.last_synced_chapter)
            .order_by(Chapter.number)
        ).scalars().all()

        for ch in chapters:
            if not ch.content:
                continue
            response = _anthropic.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                system="Summarise this novel chapter in 2-3 sentences.",
                messages=[{"role": "user", "content": ch.content[:3000]}],
            )
            summary = response.content[0].text
            ctx.chapter_summaries = [*ctx.chapter_summaries, {"chapter": ch.number, "summary": summary}]
            ctx.last_synced_chapter = ch.number
            ctx.token_count += response.usage.input_tokens + response.usage.output_tokens

        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(name="summarise_chapter", bind=True, max_retries=2)
def summarise_chapter(self, novel_id: str, chapter_id: str):
    """Summarise a single chapter and store in AINovelContext."""
    sync_novel_context.delay(novel_id)


# ── Periodic Tasks ────────────────────────────────────────────────────────────

@celery_app.task(name="recalculate_rankings")
def recalculate_rankings():
    """Recompute novel rankings based on views + ratings + recency."""
    from sqlalchemy import text
    db = _get_db_session()
    try:
        db.execute(text("""
            UPDATE novels SET
                rating_avg = COALESCE((
                    SELECT AVG(score) FROM ratings WHERE ratings.novel_id = novels.id
                ), 0)
            WHERE id IN (
                SELECT DISTINCT novel_id FROM ratings
            )
        """))
        db.commit()
    finally:
        db.close()


@celery_app.task(name="flush_view_counts")
def flush_view_counts():
    """Flush Redis view count increments into PostgreSQL."""
    import redis
    from app.core.config import settings

    r = redis.from_url(settings.REDIS_URL)
    db = _get_db_session()
    try:
        keys = r.keys("view:novel:*")
        for key in keys:
            count = r.getdel(key)
            if count:
                novel_id = key.decode().split(":")[-1]
                from sqlalchemy import text
                db.execute(
                    text("UPDATE novels SET view_count = view_count + :c WHERE id = :id"),
                    {"c": int(count), "id": novel_id},
                )
        db.commit()
    finally:
        db.close()
