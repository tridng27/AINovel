from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.search import schemas, service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/novels", response_model=schemas.SearchResponse)
async def search_novels(
    req: schemas.SearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await service.search_novels(req, db)
