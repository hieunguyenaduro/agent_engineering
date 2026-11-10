# Bài tập Buổi 4

Bắt buộc: bài 1 và bài 4. Bốn bài còn lại chọn thêm nếu muốn.

Nộp: file đã sửa + một ảnh chụp terminal hoặc file log chứng minh kết quả. Không cần slide.

---

## Bài 1 — Đo context thật của bạn (dễ, bắt buộc)

**Việc:** lấy một system prompt và một hội thoại thật (hoặc tự dựng 10 lượt) từ agent của bạn. Chạy nó qua cách đo trong `01_context_budget.py`.

**Yêu cầu:**
- In bảng 5 thành phần: system, developer, tool schema, lịch sử, tài liệu.
- Chỉ ra thành phần nào chiếm nhiều token nhất và vì sao.
- Đề xuất một thay đổi cụ thể, không phải "cắt bớt cho ngắn".

**Tiêu chí đạt:**
- Có số đo trước và sau thay đổi.
- Giải thích được thay đổi đó không làm mất thông tin bắt buộc nào.

**Câu hỏi suy nghĩ:** nếu phải bỏ một trong hai — mô tả tool hoặc 3 lượt chat cũ — bạn bỏ cái nào? Vì sao?

---

## Bài 2 — Viết skill thứ ba (trung bình)

**Việc:** thêm `skills/<tên>/SKILL.md` cho một việc bạn làm hằng ngày (viết email, review hợp đồng, kiểm tra hoá đơn, v.v.).

**Yêu cầu:**
- Frontmatter có đủ `name`, `description`, `when_to_use`.
- `when_to_use` chứa từ khoá mà người dùng thật sẽ gõ, không phải từ nội bộ.
- Thân bài có ít nhất 4 bước và một mục "sai sót thường gặp".

**Tiêu chí đạt:**
- `03_skill_loader.py` tìm thấy skill mới mà không sửa code.
- Một câu hỏi không liên quan không khớp skill đó.
- Metadata của skill dưới 60 token ước lượng.

**Câu hỏi suy nghĩ:** nếu `when_to_use` quá rộng, chuyện gì xảy ra với chi phí token? Nếu quá hẹp thì sao?

---

## Bài 3 — Loader xếp hạng nhiều skill (trung bình)

**Việc:** sửa `Registry.match()` để trả về **tối đa 2 skill** khớp, xếp theo điểm, thay vì chỉ một.

**Gợi ý:**
- Điểm hiện tại đếm số từ khoá xuất hiện trong câu hỏi.
- Thêm trọng số: khớp ở `name` cao hơn khớp ở `when_to_use`.
- Đừng nạp thân bài của cả hai nếu chỉ một cái đủ; thử nạp cái đầu, nếu câu trả lời thiếu thì mới nạp cái sau.

**Tiêu chí đạt:**
- In ra bảng: câu hỏi, các skill khớp, điểm, skill được nạp.
- Tổng token của 3 câu hỏi không tăng quá 30% so với bản một skill.

**Câu hỏi suy nghĩ:** xếp hạng bằng từ khoá hỏng ở đâu? Buổi 5 sẽ thay bằng gì?

---

## Bài 4 — TTL và nguồn cho memory (trung bình, bắt buộc)

**Việc:** mở rộng `05_long_memory.py` để mỗi fact có `source`, `created_at`, `expires_at`, và một hàm `why(user_id, key)` trả về nguồn + tuổi của fact.

**Gợi ý:**
- Bỏ dòng `DB_PATH.unlink(missing_ok=True)` nếu muốn kiểm tra memory sống qua hai lần chạy.
- Fact hết hạn không được `recall()` trả về, nhưng vẫn còn trong DB đến khi dọn.
- `why()` in được: "fact này lấy từ đâu, tạo khi nào, còn hạn bao lâu".
- Thêm một fact có TTL 0 ngày để chứng minh nó hết hạn ngay.

**Tiêu chí đạt:**
- Chạy hai lần, lần hai đọc lại được fact của lần một.
- Có ít nhất một fact bị loại vì hết hạn và một fact bị loại vì sai `user_id`.

**Câu hỏi suy nghĩ:** TTL nên do người viết fact quyết định hay do loại fact quyết định? Cho ví dụ hai loại fact có TTL rất khác nhau.

---

## Bài 5 — Tóm tắt có facts do model trích (khó)

**Việc:** thay `extract_facts()` bằng regex hiện tại bằng một bước gọi model có schema JSON.

**Gợi ý:**
- Schema: `{"name": str|null, "order_id": str|null, "budget": number|null, "language": str|null}`.
- Nếu không có key, giữ regex làm fallback và in rõ "đang dùng fallback".
- So sánh facts do model trích với facts do regex trích trên cùng 10 lượt.

**Tiêu chí đạt:**
- Bảng so sánh: fact nào model tìm được mà regex bỏ sót, và ngược lại.
- Context sau khi nén không vượt ngưỡng.
- Không có fact nào bị bịa ra mà không có trong hội thoại.

**Câu hỏi suy nghĩ:** nếu model trích sai một mã đơn, hậu quả nặng hơn hay nhẹ hơn việc không trích được? Vì sao?

---

## Bài 6 — Test cô lập, kể cả symlink (khó)

**Việc:** viết `test_isolation.py` bằng `pytest` cho `Workspace`.

**Các case tối thiểu:**
1. `read("notes.md")` trong workspace → được phép.
2. `read("../user-b/secret.md")` → `PermissionError`.
3. `read("/etc/passwd")` → `PermissionError`.
4. Tạo symlink trong workspace trỏ ra ngoài, `read()` → `PermissionError`.
5. `UserMemory("../user-B")` → `ValueError`.

**Tiêu chí đạt:**
- 5 test pass.
- Không test nào phụ thuộc vào thứ tự chạy.
- Có ít nhất một test chứng minh audit log được ghi.

**Câu hỏi suy nghĩ:** nếu workspace nằm trên filesystem không hỗ trợ symlink, test 4 nên skip hay fail? Vì sao?

---

## Cách nộp

- Đặt file trong thư mục `session-04/` hoặc một thư mục riêng, giữ nguyên tên file gốc nếu sửa.
- Ghi rõ bài nào bắt buộc đã làm, bài nào bỏ qua.
- Không gửi kèm `data/` hay `memory.db`; chỉ gửi code và log.
