"""对话接口"""

import json
import uuid

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from models.schemas import ChatRequest, ChatResponse
from services.agent import agent_service

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    reply = await agent_service.chat(req.message, req.model)
    return ChatResponse(reply=reply, model=req.model)

@router.post("/stream")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        block_id = f"answer_{uuid.uuid4().hex[:12]}"

        yield {
            "event": "MESSAGE_STARTED",
            "data": json.dumps({
                "eventType": "MESSAGE_STARTED",
                "messageId": message_id,
            }, ensure_ascii=False),
        }

        async for chunk in agent_service.chat_stream(req.message, req.model):
            yield {
                "event": "ANSWER_DELTA",
                "data": json.dumps({
                    "eventType": "ANSWER_DELTA",
                    "messageId": message_id,
                    "payload": {
                        "blockId": block_id,
                        "type": "answer",
                        "content": chunk, 
                        "status": "streaming",
                    },
                }, ensure_ascii=False),
            }

        yield {
            "event": "STREAM_COMPLETED",
            "data": json.dumps({
                "eventType": "STREAM_COMPLETED",
                "messageId": message_id,
            }, ensure_ascii=False),
        }

    return EventSourceResponse(event_generator())
