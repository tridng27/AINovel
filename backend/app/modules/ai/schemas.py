from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CompletionRequest(BaseModel):
    text: str
    instruction: str | None = None


class RewriteRequest(BaseModel):
    text: str
    instruction: str


class DialogueRequest(BaseModel):
    character_a: str
    character_b: str
    context: str | None = None


class ArcPlanRequest(BaseModel):
    chapter_count: int = 10


class AIJobResponse(BaseModel):
    id: UUID
    job_type: str
    novel_id: UUID
    result: str | None
    model_used: str | None
    tokens_used: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AIContextResponse(BaseModel):
    novel_id: UUID
    chapter_summaries: list
    last_synced_chapter: int
    token_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}
