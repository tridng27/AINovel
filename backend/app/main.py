from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.gateway.router import gateway

app = FastAPI(
    title="AINovel API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gateway)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
