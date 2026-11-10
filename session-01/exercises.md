# Bài tập Buổi 1

Làm tại lớp: chọn ít nhất 2 bài. Về nhà: bắt buộc bài 1 và bài 4.

Mỗi bài đều sửa trực tiếp trong `session-01/`. Không cần thư viện mới.

---

## Bài 1 — Thêm tool thứ ba (dễ, bắt buộc)

**Việc:** thêm tool `calc_refund(amount)` vào agent ở `06_mini_harness.py` để agent trả lời được câu "đơn 1234 hoàn tiền bao nhiêu?".

Gợi ý:
- Hàm `calc_refund` đã có sẵn trong `common/shop.py` nhưng chưa được khai báo trong `TOOLS` và `TOOL_FUNCTIONS`.
- Mô tả tool phải nói rõ đơn vị tiền và khi nào nên dùng.

**Tiêu chí đạt:**
- Hỏi "hoàn tiền đơn 1234" → agent gọi `calc_refund`.
- Trace hiện đúng bước `[think] muốn gọi calc_refund(...)`.

**Câu hỏi suy nghĩ:** điều gì khiến model chọn đúng tool — tên hàm, mô tả, hay tham số? Thử đổi mô tả thành mơ hồ rồi xem kết quả.

---

## Bài 2 — Dạy agent từ chối (dễ)

**Việc:** sửa `SYSTEM_PROMPT` để agent từ chối các câu ngoài phạm vi cửa hàng (ví dụ: "viết giúp tôi bài thơ về mùa thu").

**Tiêu chí đạt:** câu ngoài phạm vi → agent từ chối lịch sự, không gọi tool.

**Câu hỏi suy nghĩ:** từ chối bằng prompt đủ chưa? Nếu người dùng cố tình lách thì sao? (Buổi 8 sẽ trả lời.)

---

## Bài 3 — Làm agent lặp vô hạn rồi cứu nó (trung bình)

**Việc:**
1. Bỏ `MAX_STEPS`, cho vòng `while True`.
2. Cho tool `get_order_status` luôn trả về "Không tìm thấy đơn".
3. Quan sát chuyện gì xảy ra.

**Tiêu chí đạt:** bạn giải thích được vì sao agent không tự dừng, và thêm lại **hai** lớp bảo vệ:
- giới hạn số bước,
- dừng khi tool trả lỗi quá N lần.

**Câu hỏi suy nghĩ:** lớp bảo vệ nào nên nằm trong harness, lớp nào nên nằm trong tool?

---

## Bài 4 — Tool hỏng thì sao? (trung bình, bắt buộc)

**Việc:** hỏi agent về đơn `9999` (không tồn tại), rồi làm tool ném lỗi thật:

```python
def get_order_status(order_id: str) -> str:
    return ORDERS[order_id]["trang_thai"]   # KeyError nếu không có
```

**Tiêu chí đạt:** agent không chết, mà trả lời được "không tìm thấy đơn". Gợi ý: bọc lời gọi tool trong `try/except` và trả về chuỗi lỗi dễ đọc.

**Câu hỏi suy nghĩ:** nên đưa lỗi thô (`KeyError: '9999'`) hay câu giải thích cho model? Khác nhau thế nào?

---

## Bài 5 — Đo chi phí suy nghĩ (trung bình)

**Việc:** chạy `03_reasoning.py` với 5 câu đố tương tự, ghi lại bảng:

| Câu | Cách A đúng? | Cách B đúng? | Token A | Token B |
|---|---|---|---|---|

**Tiêu chí đạt:** kết luận được bằng số liệu: tăng bao nhiêu token để tăng bao nhiêu độ chính xác. Đây là bản nháp đầu tiên của evaluation — buổi 7.

---

## Bài 6 — Viết 5 test case cho agent (khó)

**Việc:** tạo `test_agent.py`, kiểm tra agent mà **không** gọi API thật (dùng `FAKE=1` hoặc thay `chat` bằng hàm giả).

5 case gợi ý:
1. Đơn tồn tại → trả lời có mã đơn.
2. Đơn không tồn tại → nói không tìm thấy.
3. Câu hỏi ngoài phạm vi → từ chối.
4. Câu hỏi thiếu mã đơn → hỏi lại.
5. Tool lỗi → không crash.

**Tiêu chí đạt:** `pytest -q` xanh, và mỗi test nói rõ nó bảo vệ điều gì.

---

## Bài 7 — Đọc trace như thám tử (khó)

**Việc:** chạy 5 câu hỏi khác nhau, mở `traces/last_run.json`, tìm:
- bước nào agent gọi tool **không cần thiết**,
- bước nào thiếu tool nên trả lời sai,
- câu nào tốn nhiều bước nhất và vì sao.

**Tiêu chí đạt:** một bảng 5 dòng, mỗi dòng một câu hỏi + nhận xét + đề xuất sửa harness.

Đây chính là công việc của một agent engineer thật: không viết thêm prompt hay hơn, mà đọc trace rồi sửa đúng chỗ.
