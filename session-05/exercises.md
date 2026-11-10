# Bài tập Buổi 5

Bắt buộc: bài 1 và bài 3. Còn lại chọn thêm nếu muốn.

---

## Bài 1 — Chọn cấu hình chunking (dễ, bắt buộc)

**Việc:** sửa `01_chunking.py` để thử ba cấu hình `(size, overlap)`: `(30, 5)`, `(60, 15)`, `(120, 30)`. In số chunk cho từng tài liệu.

**Tiêu chí đạt:**
- Bảng so sánh số chunk của cả ba cấu hình.
- Chỉ ra một câu bị cắt đôi ở cấu hình nhỏ nhưng trọn vẹn ở cấu hình lớn hơn.
- Giải thích được: vì sao không có một con số đúng cho mọi tài liệu?

---

## Bài 2 — Đo độ trùng lặp của kết quả (trung bình)

**Việc:** sau khi search, đến bao nhiêu phần trăm kết quả đến từ cùng một `doc_id`?

**Gợi ý:**
- Thêm hàm `dedup_by_doc(hits)` chỉ giữ chunk có score cao nhất mỗi tài liệu.
- So sánh kết quả trước và sau khi dedup trên cùng 5 câu hỏi.
- Ghi lại trường hợp dedup làm mất thông tin (nếu có).

**Tiêu chí đạt:** giải thích được khi nào nên dedup, khi nào không.

---

## Bài 3 — Thêm tài liệu và đo lại (trung bình, bắt buộc)

**Việc:** thêm một tài liệu mới (FAQ, chính sách, ghi chú) vào `DOCS`, kèm 3 case eval mới trong `06_eval_retrieval.py`.

**Tiêu chí đạt:**
- Ba case mới có ít nhất một case **trượt** ở cấu hình hiện tại.
- Đề xuất và thử một thay đổi (đổi chunk size, thêm từ khoá vào tài liệu, đổi cách viết câu hỏi) để case đó pass.
- Báo cáo Hit@1 trước/sau bằng số thật, không ước lượng.

Đây là bài mô phỏng đúng công việc thật: thêm dữ liệu luôn làm chỉ số tụt, và bạn phải biết vì sao.

---

## Bài 4 — Chặn tenant bằng hai lớp (trung bình)

**Việc:** thêm một lớp kiểm tra thứ hai: sau khi search, kiểm tra lại `payload["tenant"] == tenant` trước khi trả về. Nếu sai, ném lỗi rõ ràng.

**Câu hỏi suy nghĩ:** nếu filter đã đúng, lớp thứ hai này có thừa không? Vì sao vẫn nên có?

**Tiêu chí đạt:** viết một test cố tình gọi sai tenant và chứng minh bị chặn.

---

## Bài 5 — Trả lời có trích dẫn (khó)

**Việc:** sửa prompt/tool để câu trả lời cuối luôn kèm `[nguon: ...]`. Nếu không có nguồn, câu trả lời phải nói không đủ dữ liệu.

**Tiêu chí đạt:**
- Ba câu hỏi có nguồn, một câu không có.
- Không câu trả lời nào chứa thông tin không xuất hiện trong tool result.
- Kiểm tra bằng mắt, ghi lại kết quả.

---

## Bài 6 — Đo chi phí embedding (khó)

**Việc:** ước lượng chi phí nạp 10.000 tài liệu, mỗi tài liệu 1.000 từ, chunk 60 từ.

**Gợi ý:**
- Tính số chunk, số token, tra giá `text-embedding-3-small` trên trang chính thức.
- So sánh với chi phí retrieve 1.000 câu hỏi/ngày.
- Ghi rõ giả định và nguồn giá.

**Tiêu chí đạt:** bảng chi phí có công thức, không chỉ con số cuối. Nêu một cách giảm chi phí mà không giảm chất lượng rõ rệt.

Đây là bản nháp của phần cost trong buổi 10.
