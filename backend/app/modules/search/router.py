from fastapi import APIRouter, Depends

from app.modules.search import schemas, service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/novels", response_model=schemas.SearchResponse)
async def search_novels(req: schemas.SearchRequest = Depends()):
    return await service.search_novels(req)
