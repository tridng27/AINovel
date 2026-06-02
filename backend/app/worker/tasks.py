from app.worker.celery_app import celery_app


@celery_app.task(name="check_chapter_continuity")
def check_chapter_continuity(novel_id: str):
    pass


@celery_app.task(name="generate_arc_plan")
def generate_arc_plan(novel_id: str, synopsis: str, chapter_count: int):
    pass


@celery_app.task(name="sync_novel_context")
def sync_novel_context(novel_id: str):
    pass


@celery_app.task(name="summarise_chapter")
def summarise_chapter(novel_id: str, chapter_id: str):
    pass


@celery_app.task(name="recalculate_rankings")
def recalculate_rankings():
    pass


@celery_app.task(name="flush_view_counts")
def flush_view_counts():
    pass
