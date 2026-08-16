import json

from fastapi.testclient import TestClient

from main import app
from services.agent import agent_service


def _parse_sse(text: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []

    for raw_event in text.strip().split("\n\n"):
        event_name = ""
        data = ""
        for line in raw_event.splitlines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ")
            if line.startswith("data: "):
                data = line.removeprefix("data: ")
        events.append((event_name, json.loads(data)))

    return events


def test_chat_stream_returns_stage_two_event_protocol(monkeypatch):
    async def fake_chat_stream(message: str, model: str):
        yield "你好"
        yield "，世界"

    monkeypatch.setattr(agent_service, "chat_stream", fake_chat_stream)

    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": "hello",
            "model": "deepseek-chat",
            "conversation_id": "conv_custom",
            "client_request_id": "req_custom",
        },
    )

    assert response.status_code == 200

    events = _parse_sse(response.text)
    event_names = [event_name for event_name, _ in events]
    assert event_names == [
        "STREAM_CREATED",
        "MESSAGE_STARTED",
        "ANSWER_DELTA",
        "ANSWER_DELTA",
        "MESSAGE_COMPLETE",
        "STREAM_COMPLETED",
    ]

    message_ids = {data["messageId"] for _, data in events}
    run_ids = {data["runId"] for _, data in events}
    assert len(message_ids) == 1
    assert len(run_ids) == 1

    for seq, (event_name, data) in enumerate(events, start=1):
        assert data["eventType"] == event_name
        assert data["conversationId"] == "conv_custom"
        assert data["clientRequestId"] == "req_custom"
        assert data["seq"] == seq
        assert data["runId"].startswith("run_")
        assert data["messageId"].startswith("msg_")

    answer_payloads = [data["payload"] for event_name, data in events if event_name == "ANSWER_DELTA"]
    block_ids = {payload["blockId"] for payload in answer_payloads}
    assert len(block_ids) == 1
    assert answer_payloads[0]["content"] == "你好"
    assert answer_payloads[1]["content"] == "，世界"


def test_chat_stream_openapi_declares_sse_protocol():
    client = TestClient(app)

    operation = client.get("/openapi.json").json()["paths"]["/api/v1/chat/stream"]["post"]
    sse_response = operation["responses"]["200"]["content"]["text/event-stream"]

    assert sse_response["schema"] == {"type": "string"}
    assert "event: STREAM_CREATED" in sse_response["example"]
    assert "event: MESSAGE_STARTED" in sse_response["example"]


def test_chat_stream_returns_failed_event_without_sensitive_details(monkeypatch):
    async def fake_chat_stream(message: str, model: str):
        raise RuntimeError("secret api key failed")
        yield ""

    monkeypatch.setattr(agent_service, "chat_stream", fake_chat_stream)

    client = TestClient(app)
    response = client.post("/api/v1/chat/stream", json={"message": "hello"})

    assert response.status_code == 200

    events = _parse_sse(response.text)
    assert events[-1][0] == "STREAM_FAILED"
    assert events[-1][1]["eventType"] == "STREAM_FAILED"
    assert events[-1][1]["error"] == {
        "code": "CHAT_STREAM_FAILED",
        "message": "流式聊天生成失败，请稍后重试",
        "retryable": True,
    }
    assert "secret" not in response.text
