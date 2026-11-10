# Buổi 9 — Serving Agents: FastAPI, Streaming và Session

> Agent của bạn đang chạy bằng `python file.py`. Không ai dùng được nó. Buổi này biến nó thành một API: có kiểu dữ liệu, có session, có streaming, có xác thực, có health check — và có một UI tối giản để chứng minh nó chạy thật.

**Thời lượng:** 120 phút — 55 phút giảng + demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-09
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python 01_hello_api.py          # chạy demo bằng TestClient
```

Chạy server thật:

```bash
uvicorn 01_hello_api:app --reload --port 8000
curl localhost:8000/health
```

Mở `http://localhost:8000/docs` để thấy tài liệu API tự sinh.

Sáu ví dụ đều chạy được **không cần API key**. Chúng dùng một agent luật đơn giản trong `common/agent.py`; mục tiêu buổi này là tầng phục vụ, không phải chất lượng câu trả lời. Khi nối agent thật, chỉ thay `answer()` và `stream_answer()`.

---

## 1. Vì sao phải có API? (5 phút)

Ba lý do, không phải một:

| Lý do | Nếu không có API |
|---|---|
| Bảo vệ key | Key nằm trong app điện thoại/web, ai cũng lấy được |
| Quản lý phiên | Mỗi client tự giữ lịch sử, không đồng bộ |
| Kiểm soát tải | Không giới hạn, không đo, không chặn |

API cũng là **ranh giới tin cậy**. Mọi thứ phía sau API được tin; mọi thứ từ client đến phải kiểm tra.

> **Một câu chốt:** API không phải lớp trang trí — nó là nơi giữ key, giữ quyền và giữ trạng thái.

---

## 2. API nhỏ nhất (8 phút)

Chạy `01_hello_api.py`.

```python
app = FastAPI(title="Shop Agent API", version="0.1.0")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)

@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(answer=answer(request.message))
```

FastAPI làm hộ ba việc:

1. **Đọc JSON và kiểm tra kiểu.** Body sai → `422` kèm lý do cụ thể.
2. **Sinh `/docs`.** Người dùng API đọc được mà không cần hỏi bạn.
3. **Sinh OpenAPI schema.** Dùng để sinh client, viết test contract.

Hai endpoint tối thiểu: `/health` (process sống) và một endpoint nghiệp vụ. Chưa cần database, chưa cần auth.

> **Một câu chốt:** kiểu dữ liệu rõ ràng là tài liệu sống, không phải thủ tục.

---

## 3. Session: nối các lượt (10 phút)

Chạy `02_agent_endpoint.py`.

```python
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    session_id: str = Field(default="default", min_length=1, max_length=64)

previous = store.history(user_id, request.session_id)
reply = answer(request.message, previous)
store.append(user_id, request.session_id, "user", request.message)
store.append(user_id, request.session_id, "assistant", reply)
```

Ba quyết định thiết kế:

| Quyết định | Vì sao |
|---|---|
| `session_id` do client gửi | Client biết khi nào bắt đầu cuộc mới |
| Server lưu lịch sử | Client không cần giữ, đổi thiết bị vẫn tiếp tục |
| Trả `turns` | Client hiển thị được tiến độ, debug dễ hơn |

Session trong file lưu bằng dict. Production dùng Redis/Postgres, có TTL và mã hoá. **API không đổi** — chỉ đổi phần store. Đó là lợi ích của việc tách tầng.

> **Một câu chốt:** session_id là danh tính cuộc trò chuyện; đừng để nó là danh tính người dùng.

---

## 4. Streaming bằng SSE (12 phút)

Chạy `03_sse_stream.py`.

```python
from sse_starlette.sse import EventSourceResponse

def event_stream(message):
    for piece in stream_answer(message):
        yield {"event": "token", "data": json.dumps({"text": piece}, ensure_ascii=False)}
    yield {"event": "done", "data": '{"status": "ok"}'}

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    return EventSourceResponse(event_stream(request.message))
```

Giao thức SSE chỉ là text:

```
event: token
data: {"text": "Đơn "}

event: done
data: {"status": "ok"}
```

| Chọn | Khi nào |
|---|---|
| SSE | Chỉ cần server → client, đi qua proxy dễ |
| WebSocket | Cần hai chiều, client gửi liên tục |
| Long polling | Không kiểm soát được hạ tầng, nhưng chậm |

Ba lỗi thường gặp:

1. **Proxy buffer response.** Nginx mặc định gom response; phải tắt buffer cho route SSE.
2. **Không gửi heartbeat.** Kết nối rỗng bị đóng sau 30–60s. `sse-starlette` gửi ping hộ.
3. **Lỗi giữa stream không báo.** Nếu generator ném exception, client chỉ thấy stream đứt. Phải bắt và gửi `event: error`.

Trong file còn `/chat/stream-raw` để bạn thấy SSE không có gì huyền bí: chỉ là `yield` chuỗi đúng định dạng.

> **Một câu chốt:** streaming là yêu cầu trải nghiệm — agent im lặng 20 giây bị coi là hỏng.

---

## 5. Xác thực và cô lập phiên (12 phút)

Chạy `04_sessions_auth.py`.

```python
def get_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Thiếu hoặc sai Authorization header.")
    user = store.authenticate(authorization.removeprefix("Bearer ").strip())
    if user is None:
        raise HTTPException(401, "API key không hợp lệ.")
    return user

@app.get("/sessions/{session_id}")
def get_session(session_id: str, user: dict = Depends(get_user)):
    messages = store.load(user["user_id"], session_id)
    if messages is None:
        raise HTTPException(404, "Không tìm thấy phiên.")
    return SessionResponse(...)
```

Ba lỗi bảo mật hay gặp:

1. **Tin `user_id` trong body.** Client sửa một dòng là đọc được dữ liệu người khác. `user_id` phải đến từ token, không từ body.
2. **Trả 403 khi phiên thuộc người khác.** 403 xác nhận phiên tồn tại — rò rỉ thông tin. Trả **404**.
3. **Chỉ kiểm tra quyền ở endpoint list.** Endpoint đọc chi tiết, tải file, xoá — endpoint nào cũng phải kiểm tra.

Đây là AuthN (bạn là ai). AuthZ (bạn được làm gì) sẽ nói kỹ ở buổi 8, nhưng nguyên tắc giống nhau: kiểm tra ở tầng dữ liệu.

> **Một câu chốt:** không tin bất cứ thứ gì client gửi — kể cả `user_id`.

---

## 6. Lỗi, health, request id (10 phút)

Chạy `05_errors_health.py`.

Ba thứ mọi API chạy thật cần:

**1. Lỗi không rò rỉ chi tiết.**

```python
@app.exception_handler(Exception)
async def unhandled_handler(request, exc):
    logger.error("unhandled %s (request_id=%s)", type(exc).__name__, request_id_var.get())
    return JSONResponse(500, {
        "error": "internal_error",
        "message": "Có lỗi xảy ra. Vui lòng thử lại hoặc gửi mã request_id.",
        "request_id": request_id_var.get(),
    })
```

Người dùng nhận câu an toàn. Log server giữ chi tiết. Cùng `request_id` để đối chiếu.

**2. Hai loại health check.**

| Endpoint | Câu hỏi | Ai dùng |
|---|---|---|
| `/health` | Process còn sống? | Load balancer, orchestrator |
| `/ready` | Phụ thuộc đã sẵn sàng? | Deploy, trước khi nhận traffic |

Gộp hai thứ này là lỗi: process sống nhưng database chết thì `/health` vẫn 200 và traffic vẫn vào.

**3. Request id.**

```python
@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

Khách báo lỗi, bạn hỏi mã request id, tìm trong log — xong. Không có nó, bạn đoán.

> **Một câu chốt:** lỗi là chuyện bình thường; không có request id mới là chuyện không debug được.

---

## 7. Client và UI (10 phút)

Chạy `06_client_and_ui.py`, sau đó `uvicorn 06_client_and_ui:app --reload` và mở `http://localhost:8000`.

UI chỉ là một trang HTML gọi `POST /chat/stream` và đọc SSE bằng `fetch` + `ReadableStream`:

```javascript
const response = await fetch('/chat/stream', { method: 'POST', ... });
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  // tách từng block cách nhau bởi \n\n, đọc event: và data:
}
```

Phía Python, client thật dùng `httpx`:

```python
async with client.stream("POST", "/chat/stream", json={...}) as response:
    async for line in response.aiter_lines():
        ...
```

Điểm quan trọng: UI **không** gọi thẳng model. Nó chỉ nói chuyện với API. API giữ key, giữ session, giữ quyền. Nếu UI gọi thẳng model, bạn không có cách nào chặn, đo, hay đổi model mà không phát hành lại app.

> **Một câu chốt:** client chỉ được biết giao thức, không được biết bí mật.

---

## 8. Trước khi lên production (5 phút)

Checklist tối thiểu:

- [ ] Chạy `uvicorn --workers N` sau reverse proxy; không expose trực tiếp.
- [ ] Tắt proxy buffering cho route SSE.
- [ ] Timeout của proxy **lớn hơn** timeout của agent.
- [ ] Giới hạn body size và rate limit theo user.
- [ ] Log có request id, không có key, không có nội dung nhạy cảm.
- [ ] `/health` và `/ready` tách riêng.
- [ ] Có test cho 401, 404, 422, 500 — không chỉ happy path.
- [ ] Session store có TTL; không giữ mãi.

Hai điều không nên làm: tự viết lại auth, và để CORS `*` cho API có key.

---

## 9. Lab (60 phút)

### Phần A — Chạy và đọc (25 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_hello_api.py` | Body sai thì FastAPI trả gì, ở đâu sinh ra lỗi đó? |
| `02_agent_endpoint.py` | Vì sao phải trả `turns`, không chỉ `answer`? |
| `03_sse_stream.py` | Nếu proxy buffer, người dùng thấy gì? |
| `04_sessions_auth.py` | Vì sao trả 404 thay vì 403 cho phiên người khác? |
| `05_errors_health.py` | `/health` và `/ready` khác nhau ở đâu? |
| `06_client_and_ui.py` | UI có biết API key không? Vì sao? |

### Phần B — Nối agent thật (35 phút)

Lấy agent buổi 5 hoặc 6 và làm bốn việc:

1. Thay `common/agent.py` bằng agent thật (giữ chữ ký hàm).
2. Thêm endpoint `POST /chat/stream` trả SSE từ `graph.stream(stream_mode="messages")`.
3. Thêm auth bằng API key, mỗi user có session riêng.
4. Viết 4 test: 200, 401, 404, 422.

Làm theo `exercises.md` nếu cần gợi ý.

---

## 10. Bài tập về nhà

Xem `exercises.md`. Bắt buộc bài 1 và bài 3.

---

## 11. Tổng kết — 5 câu mang về

1. API là nơi giữ key, quyền và trạng thái — không phải lớp trang trí.
2. Kiểu dữ liệu rõ ràng là tài liệu sống; `/docs` sinh ra từ đó.
3. Session là danh tính cuộc trò chuyện, không phải danh tính người dùng.
4. Streaming cần tắt proxy buffer, có heartbeat, và báo lỗi giữa stream.
5. Không tin client; luôn có request id; `/health` khác `/ready`.

---

## 12. Chuẩn bị buổi 10

- Mang theo agent hoàn chỉnh nhất của bạn (buổi 5 hoặc 6).
- Buổi 10 là capstone: chọn kiến trúc, nối thành hệ thống, chạy failure drill, viết báo cáo eval và demo 10 phút.
- Chuẩn bị một câu hỏi bạn muốn agent trả lời đúng trước lớp.

---

## Phụ lục — Cấu trúc thư mục

```
session-09/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_hello_api.py
├── 02_agent_endpoint.py
├── 03_sse_stream.py
├── 04_sessions_auth.py
├── 05_errors_health.py
├── 06_client_and_ui.py
├── common/
│   ├── agent.py      ← agent luật, thay bằng agent thật
│   └── store.py      ← session + user, thay bằng Redis/Postgres
├── exercises.md
├── requirements.txt
└── .env.example
```
