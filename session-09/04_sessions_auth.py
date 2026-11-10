"""Bài 04 — Xác thực và cô lập phiên.

Chạy:  python 04_sessions_auth.py

Ba lỗi bảo mật hay gặp ở tầng API:
    1. Tin `user_id` do client gửi trong body.
    2. Trả 403 khi session thuộc người khác -> tiết lộ session có tồn tại.
    3. Chỉ kiểm tra quyền ở endpoint list, quên endpoint đọc chi tiết.

Cách làm ở đây:
    - API key -> user, tra ở server (không tin body).
    - Đọc/ghi phiên luôn kèm user_id.
    - Không tìm thấy trong phạm vi người dùng -> 404, không phải 403.

Đây là AuthN (bạn là ai). AuthZ (bạn được làm gì) nằm ở tầng dữ liệu,
và sẽ nói kỹ hơn ở buổi 8.
"""

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from common import store
from common.agent import answer

app = FastAPI(title="Shop Agent API", version="0.4.0")


def get_user(authorization: str | None = Header(default=None)) -> dict:
    """Dependency: đổi Bearer token thành user. Sai -> 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu hoặc sai Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = authorization.removeprefix("Bearer ").strip()
    user = store.authenticate(api_key)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key không hợp lệ.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    session_id: str = Field(default="default", min_length=1, max_length=64)


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    turns: int


class SessionResponse(BaseModel):
    session_id: str
    messages: list[dict]


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: dict = Depends(get_user)) -> ChatResponse:
    user_id = user["user_id"]
    previous = store.history(user_id, request.session_id)
    reply = answer(request.message, previous)

    store.append(user_id, request.session_id, "user", request.message)
    store.append(user_id, request.session_id, "assistant", reply)

    return ChatResponse(
        answer=reply,
        session_id=request.session_id,
        turns=len(store.history(user_id, request.session_id)) // 2,
    )


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, user: dict = Depends(get_user)) -> SessionResponse:
    messages = store.load(user["user_id"], session_id)
    if messages is None:
        # 404 chứ không phải 403: không xác nhận session của người khác có tồn tại.
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên.")
    return SessionResponse(session_id=session_id, messages=messages)


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    store.reset()
    client = TestClient(app)
    an = {"Authorization": "Bearer key-an"}
    binh = {"Authorization": "Bearer key-binh"}

    print("=== Không có key ===")
    r = client.post("/chat", json={"message": "Đơn 1234 đâu?"})
    print("status:", r.status_code, "|", r.json()["detail"])

    print("\n=== An hỏi, tạo phiên riêng ===")
    r = client.post(
        "/chat", json={"message": "Đơn 1234 đâu?", "session_id": "phien-an"}, headers=an
    )
    print("status:", r.status_code, "|", r.json())

    print("\n=== An đọc phiên của mình ===")
    r = client.get("/sessions/phien-an", headers=an)
    print("status:", r.status_code, "| số message:", len(r.json()["messages"]))

    print("\n=== Bình thử đọc phiên của An ===")
    r = client.get("/sessions/phien-an", headers=binh)
    print("status:", r.status_code, "|", r.json()["detail"])
    print("404 vì Bình không có phiên đó — không phải 'cấm', mà là 'không tồn tại'.")

    print("\n=== Key sai ===")
    r = client.post(
        "/chat", json={"message": "hi"}, headers={"Authorization": "Bearer key-gia"}
    )
    print("status:", r.status_code, "|", r.json()["detail"])
