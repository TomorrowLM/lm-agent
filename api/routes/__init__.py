"""API 路由聚合层，统一注册聊天与健康检查路由。"""

from fastapi import APIRouter

from api.routes.chat import router as chat_router
from api.routes.health import router as health_router

router = APIRouter()
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(health_router, prefix="/health", tags=["Health"])
