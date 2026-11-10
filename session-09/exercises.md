# Bài tập Buổi 9

Bắt buộc: bài 1 và bài 3. Còn lại chọn thêm nếu muốn.

---

## Bài 1 — Bốn test cho bốn lỗi (dễ, bắt buộc)

**Việc:** viết test cho API ở `04_sessions_auth.py`, dùng `TestClient`:

1. Không có key → 401.
2. Key sai → 401.
3. User B đọc phiên của A → 404.
4. Body rỗng → 422.

**Tiêu chí đạt:** cả bốn test pass bằng `pytest -q`. Không test nào phụ thuộc thứ tự chạy.

---

## Bài 2 — Giới hạn tần suất (trung bình)

**Việc:** thêm rate limit đơn giản theo user: tối đa 5 request/phút. Vượt → 429 kèm header `Retry-After`.

**Gợi ý:**
- Lưu `(user_id, phút hiện tại) -> count` trong dict.
- Không cần Redis cho bài này, nhưng ghi chú vì sao production cần.
- Test bằng cách gọi 6 lần liên tiếp.

**Tiêu chí đạt:** request thứ 6 nhận 429; request của user khác không bị ảnh hưởng.

---

## Bài 3 — Nối agent thật vào API (trung bình, bắt buộc)

**Việc:** thay `common/agent.py` bằng agent LangGraph của bạn (buổi 5 hoặc 6).

**Yêu cầu:**
- Giữ nguyên chữ ký `answer(question, history)` và `stream_answer(question)`.
- Endpoint `/chat` vẫn trả cùng schema.
- Endpoint `/chat/stream` stream từng token thật.
- Không để lỗi graph làm sập server: bắt và trả 503 kèm request id.

**Tiêu chí đạt:** cùng một câu hỏi, gọi `/chat` và `/chat/stream` cho nội dung tương đương; stream đến từng token, không phải gửi một cục.

---

## Bài 4 — SSE chịu lỗi giữa stream (trung bình)

**Việc:** tạo một endpoint cố tình lỗi sau khi đã gửi 3 token. Client phải nhận `event: error` và biết đây là lỗi, không phải kết thúc bình thường.

**Gợi ý:**
- Generator `try/except`, gửi `event: error` với thông điệp an toàn + request id.
- Không gửi stack trace.
- Test đọc stream và kiểm tra có event `error`.

**Tiêu chí đạt:** client phân biệt được `done` và `error`; log server có chi tiết.

---

## Bài 5 — Session store có TTL (khó)

**Việc:** đổi `common/store.py` sang SQLite, thêm `expires_at`. Phiên quá 24h bị coi như không tồn tại.

**Gợi ý:**
- Bảng `sessions(user_id, session_id, role, content, created_at)`.
- Truy vấn luôn kèm `user_id`; không có hàm đọc "tất cả".
- Có hàm `cleanup()` xoá phiên hết hạn.

**Tiêu chí đạt:** test tạo phiên, chỉnh `expires_at` về quá khứ, đọc lại nhận 404. Chạy lại process vẫn còn phiên chưa hết hạn.

---

## Bài 6 — Đo và báo cáo (khó)

**Việc:** thêm middleware đo latency từng request, ghi ra JSONL: `request_id`, `path`, `status`, `ms`, `user_id` (nếu có).

**Yêu cầu:**
- Không ghi API key, không ghi nội dung tin nhắn.
- Chạy 20 request, tính p50/p95.
- So sánh latency của `/chat` và `/chat/stream` (đến token đầu tiên và đến token cuối).

**Tiêu chí đạt:** bảng số thật + nhận xét: streaming không làm tổng thời gian ngắn hơn, nó làm **thời gian đến token đầu tiên** ngắn hơn.

Đây là bản nháp của phần latency trong buổi 10.
