"""请求/响应数据模型"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    model: str = Field(default="deepseek-chat", description="模型名称")
    stream: bool = Field(default=False, description="是否流式返回")
    conversation_id: Optional[str] = Field(
        default=None, description="会话 ID，首次请求可不传，后续追问复用"
    )
    client_request_id: Optional[str] = Field(
        default=None, description="客户端本次发送请求 ID，每次点击发送生成新值"
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Agent 回复")
    model: str = Field(default="", description="使用的模型")


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
