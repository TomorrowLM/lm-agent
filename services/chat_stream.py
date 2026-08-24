"""聊天流式服务 —— 编排标准 SSE 事件协议，补齐 ID 体系与失败事件"""

from typing import Any, AsyncIterator

from core.ids import (
    new_block_id,
    new_client_request_id,
    new_conversation_id,
    new_message_id,
    new_run_id,
)
from core.sse import sse_event
from models.events import ErrorCode, EventType
from services.agent import agent_service


async def stream_chat_events(
    message: str,
    model: str = "deepseek-chat",
    conversation_id: str | None = None,
    client_request_id: str | None = None,
) -> AsyncIterator[dict[str, str]]:
    """生成一次聊天流的完整 SSE 事件序列

    事件顺序：
        STREAM_CREATED -> MESSAGE_STARTED -> ANSWER_DELTA*
        -> MESSAGE_COMPLETE -> STREAM_COMPLETED
    失败时以 STREAM_FAILED 结尾，且不泄露底层异常细节。
    """
    conversation_id = conversation_id or new_conversation_id()
    client_request_id = client_request_id or new_client_request_id()
    run_id = new_run_id()
    message_id = new_message_id()
    block_id = new_block_id("answer")

    seq = 0

    def base_event(event_type: str) -> dict[str, Any]:
        """构造带统一 ID 体系的事件体，并递增序号"""
        nonlocal seq
        seq += 1
        return {
            "eventType": event_type,
            "conversationId": conversation_id,
            "clientRequestId": client_request_id,
            "runId": run_id,
            "messageId": message_id,
            "seq": seq,
        }
    yield sse_event(EventType.STREAM_CREATED, base_event(EventType.STREAM_CREATED))
    yield sse_event(EventType.MESSAGE_STARTED, base_event(EventType.MESSAGE_STARTED))

    try:
        async for chunk in agent_service.chat_stream(message, model):
            data = base_event(EventType.ANSWER_DELTA)
            data["payload"] = {
                "blockId": block_id,
                "type": "answer",
                "content": chunk,
                "status": "streaming",
            }
            yield sse_event(EventType.ANSWER_DELTA, data)
    except Exception:
        # 统一返回稳定错误码，避免把底层异常细节（如密钥）暴露给前端
        data = base_event(EventType.STREAM_FAILED)
        data["error"] = {
            "code": ErrorCode.CHAT_STREAM_FAILED,
            "message": "流式聊天生成失败，请稍后重试",
            "retryable": True,
        }
        yield sse_event(EventType.STREAM_FAILED, data)
        return

    yield sse_event(EventType.MESSAGE_COMPLETE, base_event(EventType.MESSAGE_COMPLETE))
    yield sse_event(EventType.STREAM_COMPLETED, base_event(EventType.STREAM_COMPLETED))
