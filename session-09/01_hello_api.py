"""Bài 01 — API nhỏ nhất: hai endpoint, không magic.

Chạy demo:   python 01_hello_api.py
Chạy server: uvicorn 01_hello_api:app --reload --port 8000
Thử:         curl localhost:8000/health
             curl -X POST localhost:8000/chat -H 'content-type: application/json' \
                  -d '{"message": "Đơn 1234 đâu?"}'

Ba thứ FastAPI làm hộ bạn:
    1. Đọc JSON body và kiểm tra kiểu (Pydantic).
    2. Sinh OpenAPI docs tại /docs.
    3. Trả lỗi 422 rõ ràng khi body sai.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from common.agent import answer

app = FastAPI(title="Shop Agent API", version="0.1.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict:
    """Liveness: process còn sống. Không kiểm tra database."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(answer=answer(request.message))


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)

    print("=== GET /health ===")
    print(client.get("/health").json())

    print("\n=== POST /chat ===")
    response = client.post("/chat", json={"message": "Đơn 1234 đâu?"})
    print("status:", response.status_code)
    print("body:", response.json())

    print("\n=== POST /chat với body sai ===")
    response = client.post("/chat", json={"message": ""})
    print("status:", response.status_code)
    print("chi tiết lỗi:", response.json()["detail"][0]["msg"])

    print("\nChạy thật: uvicorn 01_hello_api:app --reload")
    print("Docs tự sinh: http://localhost:8000/docs")
