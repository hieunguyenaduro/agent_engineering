# Bài tập Buổi 8

Bắt buộc: **bài 1** và **bài 4**. Bốn bài còn lại chọn thêm nếu muốn.

Nộp: file đã sửa + một đoạn giải thích ngắn. Tiêu chí chung là **giải thích được**, không chỉ chạy được.

---

## Bài 1 — Mô hình mối đe doạ cho agent của bạn (dễ, bắt buộc)

**Việc:** chọn agent bạn đã làm ở buổi 5 hoặc 6. Viết một bảng mối đe doạ gồm 5 dòng, mỗi dòng một bề mặt: đầu vào, dữ liệu, công cụ, đầu ra, người dùng.

Mỗi dòng trả lời:

- Tài sản nào bị ảnh hưởng?
- Kẻ tấn công làm gì cụ thể?
- Thiệt hại tối đa là gì?
- Lớp phòng thủ nào đang có? Lớp nào còn thiếu?

**Tiêu chí đạt:**
- Có ít nhất một tấn công **gián tiếp** qua tài liệu hoặc kết quả tool.
- Có ít nhất một tấn công liên quan tới quyền của tool, không chỉ prompt.
- Chỉ ra được một rủi ro còn lại mà bạn **chấp nhận**, kèm lý do.

**Câu hỏi suy nghĩ:** nếu agent của bạn bị lừa gọi một tool có thật, lớp nào chặn được? Nếu không có lớp nào, vì sao?

---

## Bài 2 — Lách input guard (trung bình)

**Việc:** viết 3 biến thể của một câu injection mà `check_input` trong `common/guards.py` **không** chặn. Ví dụ: viết không dấu, chèn ký tự, đổi ngôn ngữ, chia chỉ thị thành hai phần.

Với mỗi biến thể:

1. In ra `check_input(...).ok` và lý do.
2. Giải thích vì sao regex bỏ sót.
3. Đề xuất một lớp khác bắt được nó (không chỉ "thêm regex").

**Tiêu chí đạt:**
- Cả 3 biến thể đều lọt qua `check_input`.
- Có ít nhất một đề xuất không dựa vào regex, ví dụ allowlist tool hoặc phê duyệt.
- Không sửa test hiện có để test xanh.

**Lưu ý:** chỉ thử trên máy của bạn, với dữ liệu giả.

---

## Bài 3 — PII trong tệp và trong log (trung bình)

**Việc:** thêm một loại PII mới vào `common/pii.py` (ví dụ địa chỉ nhà, số hộ chiếu, hoặc mã số thuế). Sau đó:

- Viết 3 câu chứa loại PII đó, trong đó có một câu **không** nên bị che (false positive).
- Thêm test vào `test_security.py`.
- Chứng minh log audit không còn giá trị thô.

**Tiêu chí đạt:**
- `pytest -q` xanh.
- Có ít nhất một test cho false positive hoặc một ghi chú vì sao chấp nhận false positive.
- Giải thích được che ở cửa vào khác che ở cửa ra thế nào.

---

## Bài 4 — Phê duyệt theo ngưỡng tiền (trung bình, bắt buộc)

**Việc:** sửa `04_tool_guard.py` (hoặc viết file mới) để:

- Hoàn tiền **≤ 500.000 đồng**: tự chạy, không cần duyệt.
- Hoàn tiền **> 500.000 đồng**: bắt buộc có token duyệt của con người.
- Token chỉ dùng một lần và gắn đúng số tiền, đúng `order_id`.

Viết test cho cả hai nhánh và cho trường hợp dùng lại token.

**Tiêu chí đạt:**
- Test nhỏ chứng minh 500.000 tự chạy, 500.001 cần duyệt.
- Đổi `amount` sau khi duyệt thì token không còn hợp lệ.
- Giải thích được: ngưỡng nên nằm trong code, trong cấu hình, hay trong prompt? Vì sao?

**Gợi ý:** đừng để model tự quyết định "khoản này nhỏ nên khỏi duyệt". Ngưỡng là chính sách của con người.

---

## Bài 5 — SSRF và redirect (khó)

**Việc:** `ToolGuard` hiện chặn host lạ và IP nội bộ trước khi gọi. Nhưng nếu `api.shop.example` trả về redirect 302 tới `http://169.254.169.254/...` thì sao?

1. Viết một tool giả lập luôn redirect tới địa chỉ nội bộ.
2. Chứng minh guard hiện tại **không** chặn được redirect.
3. Đề xuất và cài đặt một lớp chặn: kiểm tra lại host sau mỗi redirect, hoặc dùng egress proxy.

**Tiêu chí đạt:**
- Có test chứng minh lỗ hổng trước khi sửa.
- Có test chứng minh redirect độc bị chặn sau khi sửa.
- Nêu được vì sao allowlist theo tên miền vẫn có thể bị DNS rebinding.

---

## Bài 6 — Bộ test đa tenant (khó)

**Việc:** thêm tenant thứ ba (`gamma`) và một người dùng thuộc cả `acme` lẫn `gamma`. Viết 5 test:

1. `acme` không đọc được tài liệu `beta`.
2. `acme` không đọc được tài liệu `gamma`.
3. Người dùng thuộc hai tenant đọc được đúng tài liệu của từng tenant khi chọn tenant rõ ràng.
4. `recall` memory không trả nhầm tenant.
5. Payload cố đổi `tenant_id` bị từ chối.

**Tiêu chí đạt:**
- `pytest -q` xanh.
- Không test nào dựa vào việc "model được dặn chỉ trả lời một tenant".
- Giải thích được: nếu một người thuộc hai tenant, `tenant_id` phải đến từ đâu trong request?

---

## Cách nộp

```bash
cd session-08
pytest -q
python 06_security_tests.py
```

Nộp kèm ảnh chụp terminal hoặc file log test. Bài nào làm hỏng test cũ thì chưa đạt.
