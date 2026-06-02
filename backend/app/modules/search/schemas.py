from pydantic import BaseModel


class SearchRequest(BaseModel):
    q: str
    page: int = 1
    hits_per_page: int = 20
    genre_id: int | None = None
    status: str | None = None


class SearchHit(BaseModel):
    id: str
    title: str
    slug: str
    synopsis: str | None
    author_username: str | None
    cover_url: str | None
    view_count: int
    rating_avg: float | None


class SearchResponse(BaseModel):
    hits: list[SearchHit]
    total: int
    page: int
    total_pages: int
