"""Bài 02 — Endpoint agent: session, lịch sử, kiểu dữ liệu rõ ràng.

Chạy:  python 02_agent_endpoint.py

Điểm khác bài 01:
    - Có `session_id` để nối các lượt trong cùng một cuộc trò chuyện.
    - Response trả thêm metadata (số lượt), không chỉ câu trả lời.
    - Agent nhận lịch sử, nên câu trả lời có thể phụ thuộc lượt trước.

Session ở đây lưu trong RAM. Production dùng Redis/Postgres — nhưng API
không đổi, chỉ đổi phần store.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from common import store
from common.agent import answer

app = FastAPI(title="Shop Agent API", version="0.2.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    session_id: str = Field(default="default", min_length=1, max_length=64)


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    turns: int


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    user_id = "demo-user"  # bài 04 sẽ thay bằng user từ API key

    previous = store.history(user_id, request.session_id)
    reply = answer(request.message, previous)

    store.append(user_id, request.session_id, "user", request.message)
    store.append(user_id, request.session_id, "assistant", reply)

    return ChatResponse(
        answer=reply,
        session_id=request.session_id,
        turns=len(store.history(user_id, request.session_id)) // 2,
    )


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    store.reset()
    client = TestClient(app)

    print("=== Hai lượt, cùng session ===")
    for message in ["Đơn 1234 đâu?", "Còn đơn 5678?"]:
        body = client.post(
            "/chat", json={"message": message, "session_id": "phien-A"}
        ).json()
        print(f"  hỏi: {message}")
        print(f"  đáp: {body['answer']}  (lượt {body['turns']})\n")

    print("=== Session khác, lịch sử riêng ===")
    body = client.post(
        "/chat", json={"message": "Xin chào", "session_id": "phien-B"}
    ).json()
    print(f"  {body}")

    print("\nLịch sử phiên A:")
    for turn in store.load("demo-user", "phien-A"):
        print(f"  [{turn['role']}] {turn['content']}")

    print("\nLưu ý: session_id do client gửi lên. Bài 04 sẽ kiểm tra nó thuộc về ai.")
