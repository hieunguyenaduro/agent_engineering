"""Bài 03 — Streaming bằng SSE: người dùng thấy agent đang chạy.

Chạy:  python 03_sse_stream.py
Server thật: uvicorn 03_sse_stream:app --reload

SSE (Server-Sent Events) là một kết nối HTTP một chiều, server đẩy text xuống.
Mỗi event có dạng:

    event: token
    data: {"text": "Đơn "}

    event: done
    data: {"tokens": 12}

Vì sao dùng SSE thay vì WebSocket:
    - Đi qua proxy/firewall dễ hơn (chỉ là HTTP thường).
    - Tự reconnect ở phía browser.
    - Đủ cho hầu hết chat agent (chỉ cần server -> client).
"""

import json
import time

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from common.agent import stream_answer

app = FastAPI(title="Shop Agent API", version="0.3.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


def event_stream(message: str):
    """Sinh event đúng giao thức SSE."""
    try:
        for piece in stream_answer(message):
            yield {"event": "token", "data": json.dumps({"text": piece}, ensure_ascii=False)}
        yield {"event": "done", "data": json.dumps({"status": "ok"})}
    except Exception as exc:  # noqa: BLE001 — phải báo lỗi cho client, không im lặng
        yield {"event": "error", "data": json.dumps({"message": str(exc)}, ensure_ascii=False)}


@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    return EventSourceResponse(event_stream(request.message))


@app.post("/chat/stream-raw")
def chat_stream_raw(request: ChatRequest):
    """Cùng dữ liệu, nhưng tự viết SSE bằng StreamingResponse.

    Dùng khi bạn không muốn thêm dependency, hoặc cần kiểm soát từng byte.
    """

    def generate():
        for piece in stream_answer(request.message):
            payload = json.dumps({"text": piece}, ensure_ascii=False)
            yield f"event: token\ndata: {payload}\n\n"
            time.sleep(0)  # nhường event loop
        yield 'event: done\ndata: {"status": "ok"}\n\n'

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)

    print("=== POST /chat/stream ===")
    with client.stream("POST", "/chat/stream", json={"message": "Đơn 1234 đâu?"}) as response:
        print("content-type:", response.headers["content-type"])
        print("các event:")
        current_event = None
        for line in response.iter_lines():
            if line.startswith("event:"):
                current_event = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                print(f"  [{current_event}] {line.split(':', 1)[1].strip()}")

    print("\nClient chỉ cần đọc từng dòng — không cần đợi cả câu trả lời.")
    print("Đây là thứ khiến chat cảm giác nhanh, dù tổng thời gian không đổi.")
