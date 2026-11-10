"""Tạo slide Buổi 9.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from pptx.enum.text import PP_ALIGN  # noqa: E402
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, CONTENT_W, INK, MARGIN, MUTED, NAVY, PANEL, WHITE, Deck,
)

d = Deck(session="Agent Engineering · Buổi 9", out=Path(__file__).with_name("slides.pptx"))

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 9/10",
    "Serving Agents",
    "FastAPI · SSE · Session · Auth",
    "120 phút · 55 phút lý thuyết & demo · 60 phút thực hành",
    notes="""Agent đang chạy bằng python file.py. Hôm nay biến nó thành API có người dùng thật.
Không phải học FastAPI từ đầu — chỉ học đúng phần cần cho agent.
Bốn thứ sẽ làm: schema, session, streaming, auth. Cộng thêm health và request id.""",
)

# --- 2. Vì sao API ----------------------------------------------------------
s = d.content("Vấn đề", "Agent chạy bằng file .py thì không ai dùng được", notes="""Hỏi lớp: nếu đưa file.py cho 100 người dùng thì chuyện gì xảy ra?
Key nằm trong máy họ. Không giới hạn tải. Không biết ai gọi. Không cập nhật được.
API là ranh giới tin cậy: phía sau được tin, phía trước phải kiểm tra.""")
d.table(
    s,
    ["Thiếu gì", "Hậu quả"],
    [
        ["Không có API", "Key nằm trong client, ai cũng lấy được"],
        ["Không quản lý phiên", "Mỗi client giữ lịch sử riêng, không đồng bộ"],
        ["Không kiểm soát tải", "Không giới hạn, không đo, không chặn"],
    ],
    top=2.15, col_widths=[4.4, 7.2], size=17, row_height=0.9,
)
d.text(s, MARGIN, 5.45, CONTENT_W, 0.8, "API không phải lớp trang trí — nó giữ key, giữ quyền, giữ trạng thái.", 19, NAVY, bold=True)

# --- 3. Section 1 -----------------------------------------------------------
d.section("01", "API nhỏ nhất", "Hai endpoint, không magic.", notes="""Phần này 8 phút. Bắt đầu từ cái nhỏ nhất chạy được.
Đừng đi vào dependency injection, middleware, background task ngay.""")

# --- 4. Code hello ----------------------------------------------------------
s = d.content("Demo · 01_hello_api.py", "Mười dòng là có API", notes="""Chạy live. Chỉ vào ba chỗ: BaseModel, decorator, response_model.
Sau đó mở /docs để lớp thấy tài liệu tự sinh — đây là điểm bán hàng thật của FastAPI.
Thử gửi body rỗng để thấy 422.""")
d.code(
    s,
    '''app = FastAPI(title="Shop Agent API")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(answer=answer(request.message))''',
    top=2.0, height=3.25, size=15,
)

# --- 5. FastAPI làm hộ gì ---------------------------------------------------
s = d.content("Vì sao FastAPI", "Ba việc bạn không phải viết", notes="""Một: đọc JSON và kiểm tra kiểu, trả 422 kèm lý do cụ thể.
Hai: sinh /docs — người dùng API đọc được mà không hỏi bạn.
Ba: sinh OpenAPI schema — dùng để sinh client và test contract.
Không có gì huyền bí: nó chỉ là Pydantic + Starlette.""")
d.table(
    s,
    ["Việc", "Bạn được gì"],
    [
        ["Đọc JSON, kiểm tra kiểu", "Body sai → 422 kèm lý do cụ thể"],
        ["Sinh /docs", "Người dùng API tự đọc, không cần hỏi"],
        ["Sinh OpenAPI schema", "Sinh client, viết test contract"],
    ],
    top=2.15, col_widths=[4.6, 7.0], size=17, row_height=0.9,
)
d.text(s, MARGIN, 5.4, CONTENT_W, 0.8, "Kiểu dữ liệu rõ ràng là tài liệu sống, không phải thủ tục.", 19, NAVY, bold=True)

# --- 6. Section 2 -----------------------------------------------------------
d.section("02", "Session", "Nối các lượt thành một cuộc trò chuyện.", notes="""Phần này 10 phút. Session là khái niệm sẽ theo suốt buổi.
Điểm dễ sai nhất: session_id bị dùng như danh tính người dùng.""")

# --- 7. Code session --------------------------------------------------------
s = d.content("Demo · 02_agent_endpoint.py", "Client gửi session_id, server giữ lịch sử", notes="""Chạy live hai lượt cùng session, rồi một session khác.
Chỉ vào turns: metadata giúp client hiển thị tiến độ và giúp bạn debug.
Nhấn: store trong RAM chỉ để học; production đổi sang Redis/Postgres, API không đổi.""")
d.code(
    s,
    '''class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    session_id: str = Field(default="default", max_length=64)

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    previous = store.history(user_id, request.session_id)
    reply = answer(request.message, previous)

    store.append(user_id, request.session_id, "user", request.message)
    store.append(user_id, request.session_id, "assistant", reply)
    return ChatResponse(answer=reply, turns=len(previous) // 2 + 1)''',
    top=1.98, height=3.5, size=13,
)

# --- 8. Ba quyết định -------------------------------------------------------
s = d.content("Thiết kế", "Ba quyết định về session", notes="""session_id do client gửi: client biết khi nào bắt đầu cuộc mới.
Server lưu lịch sử: đổi thiết bị vẫn tiếp tục được.
Trả turns: client hiển thị tiến độ, debug dễ.
Nhấn câu cuối: session_id là danh tính cuộc trò chuyện, không phải danh tính người dùng.""")
d.table(
    s,
    ["Quyết định", "Vì sao"],
    [
        ["session_id do client gửi", "Client biết khi nào bắt đầu cuộc mới"],
        ["Server lưu lịch sử", "Đổi thiết bị vẫn tiếp tục được"],
        ["Response trả turns", "Client hiển thị tiến độ, debug dễ"],
    ],
    top=2.15, col_widths=[4.6, 7.0], size=17, row_height=0.9,
)
d.text(s, MARGIN, 5.4, CONTENT_W, 0.9, "session_id là danh tính cuộc trò chuyện — đừng dùng nó làm danh tính người dùng.", 18, NAVY, bold=True)

# --- 9. Section 3 -----------------------------------------------------------
d.section("03", "Streaming bằng SSE", "Một kết nối HTTP, server đẩy text xuống.", notes="""Phần này 12 phút. SSE đơn giản hơn WebSocket và đủ cho hầu hết chat agent.
Điểm cần nhấn: streaming là yêu cầu trải nghiệm, không phải tính năng phụ.""")

# --- 10. Định dạng SSE ------------------------------------------------------
s = d.content("Giao thức", "SSE chỉ là text", notes="""Chỉ vào định dạng: event, data, dòng trống ngăn cách.
Không có gì huyền bí. Client chỉ cần đọc từng dòng.
Nhấn: dòng trống thứ hai là thứ kết thúc một event — thiếu nó, client treo.""")
d.code(
    s,
    '''event: token
data: {"text": "Đơn "}

event: token
data: {"text": "1234 "}

event: done
data: {"status": "ok"}''',
    top=2.0, height=3.4, size=15,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8, "Hai dòng trống liên tiếp mới kết thúc một event — thiếu nó, client treo chờ.", 16, MUTED)

# --- 11. Code SSE -----------------------------------------------------------
s = d.content("Demo · 03_sse_stream.py", "Mỗi token là một event", notes="""Chạy live. Chỉ vào EventSourceResponse và generator.
Sau đó chỉ vào /chat/stream-raw: cùng dữ liệu, tự viết tay, để thấy không có magic.
Nhấn except: lỗi giữa stream phải gửi event error, không được im lặng.""")
d.code(
    s,
    '''from sse_starlette.sse import EventSourceResponse

def event_stream(message):
    for piece in stream_answer(message):
        yield {"event": "token",
               "data": json.dumps({"text": piece}, ensure_ascii=False)}
    yield {"event": "done", "data": '{"status": "ok"}'}

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    return EventSourceResponse(event_stream(request.message))''',
    top=2.0, height=3.35, size=13,
)

# --- 12. SSE vs WebSocket ---------------------------------------------------
s = d.content("Chọn công nghệ", "SSE hay WebSocket?", notes="""SSE: một chiều, đi qua proxy dễ, tự reconnect.
WebSocket: hai chiều, cần khi client gửi liên tục (voice, collaborative editing).
Long polling: chỉ khi hạ tầng không cho SSE — chậm và tốn tài nguyên hơn.
Mặc định cho chat agent là SSE.""")
d.table(
    s,
    ["Chọn", "Khi nào"],
    [
        ["SSE", "Chỉ cần server → client, đi qua proxy dễ"],
        ["WebSocket", "Cần hai chiều, client gửi liên tục"],
        ["Long polling", "Hạ tầng không cho SSE — chậm hơn"],
    ],
    top=2.1, col_widths=[3.4, 8.2], size=17, row_height=0.9,
)

# --- 13. Ba lỗi SSE ---------------------------------------------------------
s = d.content("Vận hành", "Ba lỗi SSE hay gặp", notes="""Một: proxy buffer — Nginx gom response, người dùng thấy im lặng rồi cả câu hiện ra.
Hai: không heartbeat — kết nối rỗng bị đóng sau 30-60s.
Ba: lỗi giữa stream không báo — client thấy stream đứt mà không biết vì sao.
Đây là ba lỗi production thật, không phải lý thuyết.""")
d.bullets(s, [
    "Proxy buffer response — người dùng thấy im lặng rồi cả câu hiện ra",
    "Không gửi heartbeat — kết nối rỗng bị đóng sau 30–60 giây",
    "Lỗi giữa stream không báo — client chỉ thấy stream đứt",
    "Cả ba đều không lộ ra khi chạy localhost",
], top=2.2, size=21, gap=20)

# --- 14. Section 4 ----------------------------------------------------------
d.section("04", "Xác thực", "Không tin bất cứ thứ gì client gửi.", notes="""Phần này 12 phút. Đây là phần bảo mật của buổi.
Ba lỗi hay gặp, lỗi nào cũng đã từng xảy ra ở sản phẩm thật.""")

# --- 15. Code auth ----------------------------------------------------------
s = d.content("Demo · 04_sessions_auth.py", "API key → user, ở server", notes="""Chạy live bốn tình huống: không key, key đúng, Bình đọc phiên An, key sai.
Chỉ vào Dependency get_user: mọi endpoint cần user đều dùng nó.
Nhấn 404 thay vì 403: không xác nhận phiên của người khác có tồn tại.""")
d.code(
    s,
    '''def get_user(authorization: str | None = Header(default=None)) -> dict:
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
    return SessionResponse(session_id=session_id, messages=messages)''',
    top=1.98, height=3.75, size=13,
)

# --- 16. Ba lỗi bảo mật -----------------------------------------------------
s = d.content("Bảo mật", "Ba lỗi hay gặp ở tầng API", notes="""Một: tin user_id trong body — client sửa một dòng là đọc được dữ liệu người khác.
Hai: trả 403 khi phiên thuộc người khác — 403 xác nhận phiên tồn tại.
Ba: chỉ kiểm tra quyền ở endpoint list — quên endpoint chi tiết, tải file, xoá.
Nguyên tắc: kiểm tra ở tầng dữ liệu, mọi endpoint.""")
d.table(
    s,
    ["Lỗi", "Hậu quả", "Sửa"],
    [
        ["Tin user_id trong body", "Đọc dữ liệu người khác", "Lấy user từ token"],
        ["Trả 403 cho phiên người khác", "Lộ phiên có tồn tại", "Trả 404"],
        ["Chỉ kiểm tra ở endpoint list", "Lộ qua endpoint chi tiết", "Kiểm tra mọi endpoint"],
    ],
    top=2.1, col_widths=[4.4, 4.4, 2.8], size=16, row_height=0.9,
)

# --- 17. Section 5 ----------------------------------------------------------
d.section("05", "Lỗi và health", "Lỗi là chuyện bình thường. Không debug được mới là chuyện lớn.", notes="""Phần này 10 phút. Ba thứ: handler, health/ready, request id.
Đây là phần ít hào hứng nhất nhưng quyết định có ngủ ngon hay không.""")

# --- 18. Code handler -------------------------------------------------------
s = d.content("Demo · 05_errors_health.py", "Log chi tiết, trả câu an toàn", notes="""Chạy live /boom. Chỉ vào response: không có stack trace, chỉ có câu chung + request id.
Log server giữ chi tiết. Cùng request id để đối chiếu.
Nhấn: đừng trả str(exc) — nó có thể chứa connection string, key, đường dẫn.""")
d.code(
    s,
    '''@app.exception_handler(Exception)
async def unhandled_handler(request, exc):
    logger.error("unhandled %s (request_id=%s)",
                 type(exc).__name__, request_id_var.get())
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Có lỗi xảy ra. Vui lòng thử lại hoặc gửi mã request_id.",
            "request_id": request_id_var.get(),
        },
        headers={"X-Request-ID": request_id_var.get()},
    )''',
    top=1.95, height=3.85, size=13,
)

# --- 19. Health vs ready ----------------------------------------------------
s = d.content("Vận hành", "/health khác /ready", notes="""Health: process còn sống. Load balancer dùng.
Ready: phụ thuộc đã sẵn sàng. Deploy dùng.
Gộp hai thứ là lỗi: process sống nhưng database chết thì traffic vẫn vào.
Hỏi lớp: nếu chỉ có một endpoint, bạn chọn cái nào? Không có câu trả lời đúng — nên có cả hai.""")
d.table(
    s,
    ["Endpoint", "Câu hỏi", "Ai dùng"],
    [
        ["/health", "Process còn sống?", "Load balancer, orchestrator"],
        ["/ready", "Phụ thuộc đã sẵn sàng?", "Deploy, trước khi nhận traffic"],
    ],
    top=2.15, col_widths=[2.8, 5.2, 4.0], size=17, row_height=0.9,
)
d.text(s, MARGIN, 4.85, CONTENT_W, 1.0, "Process sống nhưng database chết thì /health vẫn 200 — và traffic vẫn vào.", 17, MUTED)

# --- 20. Request id ---------------------------------------------------------
s = d.content("Debug", "Một mã để nối log với báo lỗi", notes="""Middleware sinh hoặc nhận request id, gắn vào response header.
Khách báo lỗi, bạn hỏi mã, tìm trong log — xong.
Không có nó, bạn đoán. Và đoán trong hệ thống nhiều service là vô vọng.
Đây là thứ rẻ nhất và hữu ích nhất trong buổi.""")
d.code(
    s,
    '''@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response''',
    top=2.0, height=2.55, size=14,
)
d.text(s, MARGIN, 4.85, CONTENT_W, 0.8, "Client gửi mã của họ thì giữ nguyên — trace xuyên service mới hoạt động.", 16, MUTED)

# --- 21. Section 6 ----------------------------------------------------------
d.section("06", "Client và UI", "Chứng minh API chạy thật, không chỉ trong test.", notes="""Phần này 10 phút. UI tối giản để lớp thấy luồng thật.
Không dùng React, không build — chỉ HTML + fetch + SSE.""")

# --- 22. Luồng UI -----------------------------------------------------------
s = d.content("Kiến trúc", "UI không được gọi thẳng model", notes="""UI -> API -> agent -> model. Key chỉ nằm ở API.
Nếu UI gọi thẳng model: không chặn được, không đo được, đổi model phải phát hành lại app.
Hỏi lớp: tại sao không đặt key trong biến môi trường của trình duyệt? Vì ai cũng đọc được.""")
d.panel(s, MARGIN, 2.3, 2.7, 1.3, PANEL)
d.text(s, MARGIN + 0.2, 2.55, 2.3, 0.5, "browser", 18, INK, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 0.2, 3.05, 2.3, 0.4, "không có key", 12, MUTED, align=PP_ALIGN.CENTER)

d.text(s, MARGIN + 2.85, 2.65, 0.9, 0.5, "→", 28, ACCENT, bold=True)

d.panel(s, MARGIN + 3.7, 2.3, 2.7, 1.3, ACCENT_SOFT)
d.text(s, MARGIN + 3.9, 2.55, 2.3, 0.5, "API", 18, NAVY, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 3.9, 3.05, 2.3, 0.4, "giữ key, session", 12, MUTED, align=PP_ALIGN.CENTER)

d.text(s, MARGIN + 6.55, 2.65, 0.9, 0.5, "→", 28, ACCENT, bold=True)

d.panel(s, MARGIN + 7.4, 2.3, 2.7, 1.3, PANEL)
d.text(s, MARGIN + 7.6, 2.55, 2.3, 0.5, "agent", 18, INK, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 7.6, 3.05, 2.3, 0.4, "model + tool", 12, MUTED, align=PP_ALIGN.CENTER)

d.text(s, MARGIN, 4.25, CONTENT_W, 1.2, "Key chỉ nằm ở API. Nếu đặt key trong trình duyệt, mở DevTools là thấy.\nClient chỉ được biết giao thức, không được biết bí mật.", 17, MUTED, line_spacing=1.4)

# --- 23. Client code --------------------------------------------------------
s = d.content("Demo · 06_client_and_ui.py", "Đọc stream bằng fetch", notes="""Chạy server rồi mở localhost:8000. Gõ thử một câu, thấy chữ chạy.
Sau đó chỉ vào đoạn JS: đọc từng chunk, tách block theo hai dòng trống.
Nhấn: UI chỉ là client — cùng giao thức với bất kỳ client nào khác.""")
d.code(
    s,
    '''const response = await fetch('/chat/stream', {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ message })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = '';
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  // tách block theo "\\n\\n", đọc event: và data:
}''',
    top=1.95, height=4.4, size=13,
)

# --- 24. Production checklist ----------------------------------------------
s = d.content("Trước khi deploy", "Checklist tối thiểu", notes="""Đọc nhanh, không đọc từng dòng. Nhấn ba dòng: tắt proxy buffer cho SSE, timeout proxy lớn hơn timeout agent, test cả lỗi.
Hai điều không nên làm: tự viết auth, CORS * cho API có key.
Đây là checklist, không phải giáo trình — hãy in ra dán lên tường.""")
d.bullets(s, [
    "uvicorn sau reverse proxy; không expose trực tiếp",
    "Tắt proxy buffering cho route SSE; timeout proxy > timeout agent",
    "Giới hạn body size và rate limit theo user",
    "Log có request id, không có key, không có nội dung nhạy cảm",
    "Tách /health và /ready; test cả 401, 404, 422, 500",
    "Session store có TTL; không giữ mãi",
], top=2.05, size=19, gap=14, line_spacing=1.15)

# --- 25. Lab ----------------------------------------------------------------
d.section("Lab", "60 phút thực hành", "Nối agent thật vào API.", notes="""25 phút chạy 6 file, 35 phút nối agent LangGraph vào API.
Đi vòng quanh, hỏi mỗi nhóm: stream của bạn đến từng token hay gửi một cục?""")

# --- 26. Lab roadmap --------------------------------------------------------
s = d.content("Lab", "Hai phần", notes="""Phần A đọc code. Phần B là bài thật: thay agent luật bằng agent của bạn.
Yêu cầu: giữ chữ ký hàm, stream thật, auth theo user, 4 test.
Ai xong sớm: thêm rate limit và đo p95.""")
d.panel(s, MARGIN, 2.2, 5.2, 2.9, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.6, 0.4, "25 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.3, 2.8, 4.6, 0.6, "Chạy 6 file", 21, NAVY, bold=True)
d.text(s, MARGIN + 0.3, 3.45, 4.6, 1.5, "Mỗi file trả lời một câu hỏi\nvề schema, session, SSE,\nauth hoặc lỗi.", 15, INK, line_spacing=1.35)

d.panel(s, MARGIN + 5.6, 2.2, 5.2, 2.9, ACCENT_SOFT)
d.text(s, MARGIN + 5.9, 2.4, 4.6, 0.4, "35 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 5.9, 2.8, 4.6, 0.6, "Nối agent thật", 21, NAVY, bold=True)
d.text(s, MARGIN + 5.9, 3.45, 4.6, 1.5, "Thay common/agent.py,\nstream từng token, auth theo user,\nviết 4 test lỗi.", 15, INK, line_spacing=1.35)

# --- 27. Bài tập ------------------------------------------------------------
s = d.content("Về nhà", "Bài tập bắt buộc", notes="""Bài 1 là bốn test lỗi — nhanh và củng cố phản xạ.
Bài 3 là bài thật: nối agent, stream thật.
Ai làm xong bài 3 là đã có một sản phẩm demo được.""")
d.bullets(s, [
    "Bài 1 — bốn test: 401, 401, 404, 422",
    "Bài 3 — nối agent LangGraph, stream từng token, giữ nguyên schema",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 3.8, CONTENT_W, 1.6, "Nộp: test pass + ảnh chụp stream đến từng token.\nTiêu chí: giải thích được vì sao trả 404 thay vì 403.", 17, MUTED, line_spacing=1.5)

# --- 28. Tổng kết -----------------------------------------------------------
s = d.content("Tổng kết", "Năm câu mang về", notes="""Đọc chậm. Câu 4 là câu hay bị bỏ qua nhất khi deploy.
Câu 5 là câu sẽ dùng ngay khi có sự cố đầu tiên.""")
d.bullets(s, [
    "API giữ key, quyền và trạng thái — không phải lớp trang trí.",
    "Kiểu dữ liệu rõ ràng là tài liệu sống; /docs sinh từ đó.",
    "Session là danh tính cuộc trò chuyện, không phải danh tính người dùng.",
    "Streaming cần tắt proxy buffer, có heartbeat, báo lỗi giữa stream.",
    "Không tin client; luôn có request id; /health khác /ready.",
], top=2.05, size=20, gap=16)

# --- 29. Buổi sau -----------------------------------------------------------
s = d.content("Buổi 10", "Tiếp theo: Capstone", notes="""Buổi cuối: ghép tất cả thành một hệ thống, chạy failure drill, báo cáo eval, demo 10 phút.
Mang theo agent hoàn chỉnh nhất của bạn.
Mời lớp đặt câu hỏi.""")
d.bullets(s, [
    "Chọn kiến trúc và giải thích lựa chọn bằng số",
    "Nối retrieval + agent + API + observability",
    "Failure drill: tắt một phụ thuộc, xem hệ thống phản ứng",
    "Báo cáo eval, chi phí, latency; demo 10 phút",
], top=2.15, size=20, gap=16)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.9, "Chuẩn bị: một câu hỏi bạn muốn agent trả lời đúng trước lớp.", 17, MUTED)

d.save()
