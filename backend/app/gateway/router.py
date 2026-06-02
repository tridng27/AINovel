"""API Gateway — single entry point that aggregates all module routers under /api/v1."""
from fastapi import APIRouter

from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.novels.router import router as novels_router

gateway = APIRouter(prefix="/api/v1")

# Public — no auth required
gateway.include_router(auth_router)

# Protected modules — auth is enforced per-route via core.authorize dependencies
gateway.include_router(novels_router)
gateway.include_router(ai_router)
