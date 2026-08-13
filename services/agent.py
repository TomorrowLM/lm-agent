"""Agent 服务层 —— 封装 LLM 调用逻辑，后续可替换为 LangChain/CrewAI 等框架"""

from typing import AsyncIterator

from openai import AsyncOpenAI

from core.config import settings


class AgentService:
    """基础 Agent，后续可扩展为多 Agent 协作、RAG、工具调用等"""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url=settings.deepseek_base_url,
            api_key=settings.deepseek_api_key,
        )

    async def chat(self, message: str, model: str = "deepseek-chat") -> str:
        """同步对话"""
        resp = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
        )
        return resp.choices[0].message.content or ""

    async def chat_stream(self, message: str, model: str = "deepseek-chat") -> AsyncIterator[str]:
        """流式对话"""
        stream = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            print(delta.content)
            if delta.content:
                yield delta.content


# 全局单例
agent_service = AgentService()
