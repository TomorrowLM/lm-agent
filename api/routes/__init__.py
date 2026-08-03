"""路由注册"""

from fastapi import APIRouter

from api.routes.chat import router as chat_router
from api.routes.health import router as health_router

router = APIRouter()
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(health_router, prefix="/health", tags=["Health"])
