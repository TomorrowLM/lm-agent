"""对话接口"""

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from models.schemas import ChatRequest, ChatResponse
from services.agent import agent_service
from services.chat_stream import stream_chat_events

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    reply = await agent_service.chat(req.message, req.model)
    return ChatResponse(reply=reply, model=req.model)


@router.post(
    "/stream",
    response_class=EventSourceResponse,
    responses={
        200: {
            "description": "SSE 聊天事件流",
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                    "example": (
                        "event: STREAM_CREATED\n"
                        'data: {"eventType":"STREAM_CREATED","seq":1}\n\n'
                        "event: MESSAGE_STARTED\n"
                        'data: {"eventType":"MESSAGE_STARTED","seq":2}\n\n'
                    ),
                }
            },
        }
    },
)
async def chat_stream(req: ChatRequest) -> EventSourceResponse:
    # 使用 LF 换行，与前端/测试解析器的 "\n\n" 事件分隔约定保持一致
    # EventSourceResponse 是 sse-starlette 提供的 SSE（Server-Sent Events）流式响应类。
    # 它会持续读取迭代器产生的数据，并通过 HTTP text/event-stream 响应逐条发送给客户端。
    return EventSourceResponse(
        stream_chat_events(
            message=req.message,
            model=req.model,
            conversation_id=req.conversation_id,
            client_request_id=req.client_request_id,
        ),
        sep="\n",
    )
