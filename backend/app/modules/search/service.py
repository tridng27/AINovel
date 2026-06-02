"""Search service — Meilisearch integration for full-text novel search."""
import uuid

from app.modules.search.schemas import SearchRequest, SearchResponse

NOVELS_INDEX = "novels"


def get_search_client():
    import meilisearch
    from app.core.config import settings
    return meilisearch.Client("http://meilisearch:7700", settings.MEILI_MASTER_KEY)


async def search_novels(req: SearchRequest) -> SearchResponse:
    raise NotImplementedError


async def index_novel(novel_id: uuid.UUID) -> None:
    """Index or re-index a novel document in Meilisearch."""
    raise NotImplementedError


async def delete_novel_from_index(novel_id: uuid.UUID) -> None:
    raise NotImplementedError
