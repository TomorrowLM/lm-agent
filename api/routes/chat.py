"""对话接口"""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services.agent import agent_service

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    reply = await agent_service.chat(req.message, req.model)
    return ChatResponse(reply=reply, model=req.model)
