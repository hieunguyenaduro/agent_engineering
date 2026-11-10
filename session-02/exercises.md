# Bài tập Buổi 2

Bắt buộc: bài 1 và bài 3. Còn lại chọn thêm nếu muốn.

---

## Bài 1 — Ba khách, ba thread (dễ, bắt buộc)

**Việc:** sửa `03_checkpoint.py` để có ba khách A, B, C. Cho A hỏi hai lượt, B hỏi một lượt, C không hỏi gì.

**Tiêu chí đạt:**
- In ra số message trong state của từng thread.
- Chứng minh B không thấy câu hỏi của A.
- Giải thích được: nếu quên truyền `thread_id` thì LangGraph làm gì?

---

## Bài 2 — Thêm node kiểm tra (trung bình)

**Việc:** thêm node `verify` vào graph của `02_agent_loop.py`, chạy sau khi agent trả lời lần cuối.

Gợi ý:
- Node này nhận state, kiểm tra câu trả lời cuối có chứa mã đơn không.
- Nếu thiếu, thêm một message nhắc model bổ sung và quay lại agent.
- Cẩn thận: đừng để verify tạo vòng lặp vô hạn — dùng ngân sách bước.

**Tiêu chí đạt:** câu trả lời thiếu mã đơn bị sửa, và graph vẫn dừng sau tối đa N bước.

---

## Bài 3 — Tool lỗi rồi thành công (trung bình, bắt buộc)

**Việc:** làm `get_order_status` ném lỗi ở hai lần gọi đầu, lần thứ ba trả dữ liệu thật.

Gợi ý:
- Retry nên nằm **trong tool** hay **trong node tools**? Thử cả hai và ghi lại khác biệt.
- Nếu tool ném lỗi, `ToolNode` có bắt được không? Đọc trace để trả lời.
- State nào cần giữ để biết đã thử mấy lần?

**Tiêu chí đạt:**
- Agent không chết, trả lời được kết quả cuối.
- Trace cho thấy đúng 3 lần gọi.
- Giải thích được vì sao retry trong tool dễ kiểm soát hơn retry trong graph.

---

## Bài 4 — Duyệt theo ngưỡng tiền (trung bình)

**Việc:** chỉ xin duyệt khi số tiền hoàn **lớn hơn** 500.000 đồng. Dưới ngưỡng thì tự chạy.

**Tiêu chí đạt:** hai câu hỏi khác nhau đi hai nhánh khác nhau, chứng minh bằng trace.

**Câu hỏi suy nghĩ:** ngưỡng này nên nằm trong prompt, trong code, hay trong cấu hình? Vì sao?

---

## Bài 5 — State sống qua restart (khó)

**Việc:** đổi `InMemorySaver` sang `SqliteSaver`.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
```

Gợi ý: cần `langgraph-checkpoint-sqlite`. Mở kết nối sqlite, đóng bằng `with`.

**Tiêu chí đạt:**
1. Chạy lượt 1, thoát chương trình.
2. Chạy lại chương trình khác, cùng `thread_id`, hỏi tiếp.
3. Agent vẫn nhớ lượt trước.

Đây là bài chứng minh "state không nằm trong RAM".

---

## Bài 6 — Đo chi phí từng bước (khó)

**Việc:** dùng `stream_mode="updates"` để in ra, sau mỗi node: số message, số token ước tính, thời gian chạy.

**Tiêu chí đạt:** bảng kết quả cho 3 câu hỏi khác nhau, chỉ ra bước nào tốn nhất.

Đây là bản nháp của observability — buổi 7 sẽ làm tử tế bằng Langfuse.
