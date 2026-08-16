"""ID 生成工具 —— 统一生成聊天协议中各层级的 ID"""

import uuid


def new_conversation_id() -> str:
    """生成会话 ID，表示一整场连续聊天，用于多轮上下文"""
    return f"conv_{uuid.uuid4().hex[:12]}"


def new_client_request_id() -> str:
    """生成客户端请求 ID，每次点击发送都应生成新值"""
    return f"req_{uuid.uuid4().hex[:12]}"


def new_run_id() -> str:
    """生成后端 Agent 执行 ID，一次提问对应一次 run"""
    return f"run_{uuid.uuid4().hex[:12]}"


def new_message_id() -> str:
    """生成 assistant 消息 ID，同一条回复下的多个内容块共用"""
    return f"msg_{uuid.uuid4().hex[:12]}"


def new_block_id(prefix: str = "block") -> str:
    """生成内容块 ID，prefix 用于区分 answer / think / tool 等块类型"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
