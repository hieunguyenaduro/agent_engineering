# Bài tập Buổi 6

Bắt buộc: bài 1 và bài 4. Còn lại chọn thêm nếu muốn.

---

## Bài 1 — Đo chi phí thật của subagent (dễ, bắt buộc)

**Việc:** thêm bộ đếm vào `01_subagent_as_tool.py`: mỗi lần `research` được gọi, ghi lại số lần gọi model bên trong subagent.

**Gợi ý:**
- Dùng một dict module-level `CALLS = {"main": 0, "research": 0}`.
- Tăng biến đếm trong `agent_node` và trong `gather`/`summarize`.
- In bảng sau khi chạy.

**Tiêu chí đạt:** trả lời được "một câu hỏi của người dùng tốn bao nhiêu lần gọi model?" bằng số thật.

---

## Bài 2 — Supervisor bằng LLM (trung bình)

**Việc:** thay hàm `if/else` trong `02_supervisor.py` bằng một LLM gọi structured output.

**Gợi ý:**
- Dùng `with_structured_output` với một Pydantic model có `route` và `reason`.
- Giữ nguyên các worker và edge.
- Bắt lỗi khi model trả route không hợp lệ, fallback về `general`.

**Tiêu chí đạt:** ba câu hỏi mẫu đi đúng ba nhánh; route sai không làm graph crash.

---

## Bài 3 — Song song có giới hạn (trung bình)

**Việc:** sửa `03_parallel_fanout.py` để tối đa 2 worker chạy cùng lúc, dùng `asyncio.Semaphore`.

**Gợi ý:**
- Tạo semaphore trong worker hoặc trong một dependency dùng chung.
- Đo thời gian với 4 topic: không giới hạn vs giới hạn 2.

**Tiêu chí đạt:** bảng thời gian chứng minh giới hạn hoạt động, và giải thích khi nào cần giới hạn (rate limit, tài nguyên).

---

## Bài 4 — Một nhánh chết, hai cách xử lý (trung bình, bắt buộc)

**Việc:** trong `05_partial_failure.py`, thêm chế độ `FAIL_MODE`:

- `"partial"` — trả lời phần lấy được (như hiện tại).
- `"strict"` — nếu có bất kỳ lỗi nào, trả lời "chưa thể trả lời, vui lòng thử lại".

**Tiêu chí đạt:**
- Cùng một input, hai chế độ cho hai output khác nhau.
- Giải thích được khi nào dùng chế độ nào, dựa trên loại câu hỏi (tra cứu vs giao dịch).

---

## Bài 5 — Chặn handoff vòng lặp (khó)

**Việc:** thêm luật vào `04_handoff.py`: mỗi agent chỉ được handoff tối đa một lần, và tổng số handoff tối đa là 3.

**Gợi ý:**
- Đếm trong state.
- Nếu vượt, chuyển thẳng tới node `handoff_to_human` thay vì agent tiếp theo.

**Tiêu chí đạt:** tạo được một chuỗi A -> B -> A và chứng minh graph dừng, không treo.

---

## Bài 6 — So sánh ba kiến trúc (khó)

**Việc:** chọn một tác vụ thật (ví dụ: xử lý yêu cầu hoàn tiền). Cài đặt ba phiên bản:

1. Một agent duy nhất.
2. Supervisor + 3 worker.
3. Handoff chain.

Đo trên cùng 5 input: số lần gọi model, token, thời gian, và chất lượng câu trả lời (chấm tay 1–5).

**Tiêu chí đạt:** bảng so sánh + kết luận chọn kiến trúc nào cho tác vụ đó và **vì sao**. Không có kết luận "multi-agent luôn tốt hơn".

Đây là bản nháp của bài capstone buổi 10.
