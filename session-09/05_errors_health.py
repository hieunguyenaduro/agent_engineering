"""Bài 05 — Lỗi, health check, request id.

Chạy:  python 05_errors_health.py

Ba thứ mọi API chạy thật đều cần:

    1. Lỗi nội bộ không rò rỉ stack trace ra người dùng.
       Người dùng nhận thông điệp an toàn + request_id.
       Log server giữ chi tiết + cùng request_id.

    2. /health cho biết process sống; /ready cho biết phụ thuộc đã sẵn sàng.
       Hai thứ khác nhau. Load balancer dùng /health, deploy dùng /ready.

    3. Mọi response có X-Request-ID để đối chiếu log với báo lỗi của khách.
"""

import logging
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from common.agent import AgentError, answer

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("api")

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

app = FastAPI(title="Shop Agent API", version="0.5.0")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    """Lỗi do input: 400, thông điệp thân thiện."""
    return JSONResponse(
        status_code=400,
        content={"error": "bad_request", "message": str(exc),
                 "request_id": request_id_var.get()},
        headers={"X-Request-ID": request_id_var.get()},
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
    """Lỗi không lường trước: log chi tiết, trả về câu chung."""
    logger.error("unhandled %s: %s (request_id=%s)",
                 type(exc).__name__, exc, request_id_var.get())
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Có lỗi xảy ra. Vui lòng thử lại hoặc gửi mã request_id.",
            "request_id": request_id_var.get(),
        },
        headers={"X-Request-ID": request_id_var.get()},
    )


@app.get("/health")
def health() -> dict:
    """Liveness: process còn trả lời được không."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness: phụ thuộc đã sẵn sàng chưa. Ở đây kiểm tra store."""
    from common import store

    if not isinstance(store.SESSIONS, dict):
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return {"status": "ready", "checks": {"session_store": "ok"}}


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    return {"answer": answer(request.message)}


@app.get("/boom")
def boom() -> dict:
    """Endpoint cố tình lỗi để thấy handler hoạt động."""
    raise RuntimeError("database password=secret123 không kết nối được")


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)

    print("=== /health và /ready ===")
    print(client.get("/health").json())
    print(client.get("/ready").json())

    print("\n=== Lỗi nội bộ ===")
    r = client.get("/boom")
    print("status:", r.status_code)
    print("body:", r.json())
    print("X-Request-ID:", r.headers["x-request-id"])
    print("Stack trace chỉ nằm trong log server, không nằm trong response.")

    print("\n=== Lỗi input ===")
    r = client.post("/chat", json={"message": ""})
    print("status:", r.status_code, "|", r.json()["detail"][0]["msg"])

    print("\n=== Client gửi request id của họ ===")
    r = client.get("/health", headers={"X-Request-ID": "khach-bao-loi-123"})
    print("X-Request-ID trả lại:", r.headers["x-request-id"])
