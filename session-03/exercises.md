# Bài tập Buổi 3

**Bắt buộc: bài 1 và bài 5.** Bốn bài còn lại chọn thêm — càng làm nhiều càng chắc tay.

Nộp bài: file `.py` đã sửa (hoặc file mới) + phần trả lời ngắn cho các câu hỏi. Không cần ảnh chụp màn hình.

---

## Bài 1 — Viết lại một tool tệ (dễ, bắt buộc)

**Việc:** lấy tool tệ trong `01_tool_contract.py` và viết lại thành tool tốt. Sau đó viết thêm một tool thứ hai cùng họ (ví dụ `get_order_detail`) để thấy model phải phân biệt hai tool.

**Gợi ý:**
- Bắt đầu bằng mô tả: viết một câu nói khi nào dùng, một câu nói khi nào **không** dùng.
- Đặt tên theo mẫu `động_từ + đối_tượng`.
- Chỉ giữ tham số thật sự cần; tham số suy ra được thì bỏ.
- Viết kiểu trả về bằng một ví dụ cụ thể trong mô tả.

**Tiêu chí đạt:**
- Schema của cả hai tool in ra được bằng `json.dumps`.
- Mỗi tham số có `description`, tham số giới hạn có `enum` hoặc `minimum`/`maximum`.
- Giải thích được: nếu bỏ mô tả "không dùng để hoàn tiền" thì model có thể chọn nhầm tool nào, trong tình huống nào.

---

## Bài 2 — Tool lỗi có phân loại (trung bình)

**Việc:** sửa `02_tool_errors.py` để có ba loại kết quả: thành công, lỗi tạm thời (đáng retry), lỗi vĩnh viễn (không retry). Ví dụ: timeout là tạm thời; "không tìm thấy đơn" là vĩnh viễn.

**Gợi ý:**
- Trả chuỗi có tiền tố rõ ràng: `"LỖI TẠM THỜI: ..."` và `"LỖI: ..."`.
- Retry chỉ khi tiền tố là tạm thời.
- Đừng để retry biến một lỗi nghiệp vụ thành 3 lần gọi vô ích.

**Tiêu chí đạt:**
- Trace cho thấy câu "không tìm thấy" chỉ gọi 1 lần.
- Trace cho thấy timeout gọi đúng số lần tối đa.
- Có tổng thời gian chờ tối đa, không chỉ timeout từng lần.

---

## Bài 3 — SQL tool chặt hơn (trung bình)

**Việc:** mở rộng `03_sql_readonly.py`:

1. Thêm bảng `customers(id, name, email)` và cho phép truy vấn cả hai bảng.
2. Chặn truy vấn vào bảng không nằm trong allowlist (ví dụ bảng `secrets`).
3. Thêm tham số `max_rows` cho `run_select` và kiểm tra nó không vượt trần.

**Gợi ý:**
- Allowlist theo tên bảng khó hơn tưởng tượng vì có alias và subquery. Một cách đơn giản: chỉ cho `FROM`/`JOIN` trỏ tới bảng trong danh sách, và nói rõ đây là kiểm tra thô.
- Đừng quên: lớp chặn thật vẫn là quyền của user database.

**Tiêu chí đạt:**
- 4 câu demo cũ vẫn bị chặn đúng.
- Có ít nhất 2 câu mới: một câu hợp lệ chạm bảng mới, một câu bị chặn vì bảng lạ.
- Giải thích được vì sao kiểm tra tên bảng bằng chuỗi không đủ an toàn.

---

## Bài 4 — Sandbox có ngân sách (trung bình)

**Việc:** thêm vào `04_sandbox.py` một hàm `run_many(codes, budget)` chạy nhiều đoạn code nhưng tổng thời gian không vượt `budget` giây. Đoạn nào làm cạn ngân sách thì dừng cả lô.

**Gợi ý:**
- Đo bằng `time.monotonic()` trước và sau mỗi lần chạy.
- Không chỉ dựa vào timeout từng đoạn: 10 đoạn × 2 giây vẫn là 20 giây.
- In ra đoạn nào đã chạy, đoạn nào bị bỏ.

**Tiêu chí đạt:**
- Một lô 5 đoạn, trong đó 2 đoạn treo, kết thúc trong khoảng ngân sách.
- Có dòng log nói rõ đã bỏ đoạn nào và vì sao.
- Không có tiến trình con nào còn sống sau khi hàm trả về.

---

## Bài 5 — Đóng gói MCP server (trung bình, bắt buộc)

**Việc:** lấy tool tốt ở bài 1, đóng gói thành MCP server theo mẫu `05_mcp_server.py`, rồi viết client gọi nó.

Yêu cầu tối thiểu:
- 1 tool tra dữ liệu + 1 tool tính toán (không đổi trạng thái).
- 1 resource chứa chính sách hoặc hướng dẫn dùng.
- Client in được: tên server, danh sách tool kèm schema, kết quả một lần gọi, nội dung resource.

**Gợi ý:**
- Chạy `python server.py` (không `--serve`) trước để kiểm tra capability, rồi mới chạy client.
- Nếu client treo: kiểm tra server có in gì ra `stdout` không. In debug ra `stderr`.
- Dùng `sys.executable` trong `StdioServerParameters`, đừng hardcode `python`.

**Tiêu chí đạt:**
- Client chạy một lệnh, in đủ 4 phần trên, không traceback.
- Server không có `print()` nào ra `stdout` khi serve.
- Trả lời được: đổi server sang chạy ở máy khác thì client phải sửa gì? (Gợi ý: transport, không phải logic tool.)

---

## Bài 6 — Phân quyền và audit cho MCP (khó)

**Việc:** thêm vào server bài 5 một lớp kiểm tra quyền theo tool. Ví dụ: biến môi trường `MCP_ROLE=viewer|support`; `viewer` chỉ được gọi tool tra dữ liệu, `support` được gọi cả tool tính toán.

Kèm theo: mỗi lần gọi ghi một dòng audit ra `stderr` gồm thời gian, role, tên tool, tham số (che bớt thông tin nhạy cảm nếu có).

**Gợi ý:**
- Kiểm tra quyền **trong** hàm tool hoặc trong một wrapper, đừng kiểm tra ở client.
- Trả lỗi dạng chuỗi dễ đọc: `"LỖI: role viewer không được gọi quote_refund."`
- Nếu chạy HTTP: thêm bearer token; token nào cũng phải đi kèm role, không chỉ "hợp lệ".

**Tiêu chí đạt:**
- Cùng một client, đổi `MCP_ROLE` thì tool bị từ chối khác nhau.
- Audit log đọc được bằng mắt, không lẫn vào giao thức MCP.
- Giải thích được: vì sao phân quyền ở client là vô nghĩa.

---

## Cách tự kiểm tra trước khi nộp

```bash
python -m py_compile bai_tap_cua_ban.py
python bai_tap_cua_ban.py        # phải chạy được, không cần key
```

Ba câu tự hỏi:

1. Nếu model gọi tool với tham số sai, chuyện gì xảy ra? Có traceback không?
2. Nếu tool treo 30 giây, người dùng chờ bao lâu?
3. Nếu người dùng độc hại đọc được mô tả tool, họ thuyết phục được model làm gì? Lớp nào chặn?
