"""LM Agent API —— FastAPI 入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router
from core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
