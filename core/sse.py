"""SSE 事件序列化 —— 将事件名与事件体统一序列化为 sse-starlette 事件字典"""

import json
from typing import Any


def sse_event(event: str, data: dict[str, Any]) -> dict[str, str]:
    """构造一条标准 SSE 事件，供 EventSourceResponse 消费"""
    return {
        "event": event,
        "data": json.dumps(data, ensure_ascii=False),
    }
