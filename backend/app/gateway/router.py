"""API Gateway — single entry point that aggregates all module routers under /api/v1."""
from fastapi import APIRouter

from app.modules.admin.router import router as admin_router
from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.engagement.router import router as engagement_router
from app.modules.novels.router import router as novels_router
from app.modules.search.router import router as search_router
from app.modules.users.router import router as users_router

gateway = APIRouter(prefix="/api/v1")

# Public — no auth required
gateway.include_router(auth_router)
gateway.include_router(search_router)

# Protected modules — auth is enforced per-route via core.authorize dependencies
gateway.include_router(novels_router)
gateway.include_router(ai_router)
gateway.include_router(engagement_router)
gateway.include_router(users_router)
gateway.include_router(admin_router)
