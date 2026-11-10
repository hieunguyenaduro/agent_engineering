# Bài tập Buổi 7

Bắt buộc: **bài 1 và bài 3**. Còn lại chọn thêm nếu muốn.

Nộp bài bằng cách mở một PR nhỏ, kèm output chạy thật — không nộp ảnh chụp màn hình không có lệnh.

---

## Bài 1 — Thêm case từ failure thật (dễ, bắt buộc)

**Việc:** thêm 3 case mới vào `evals/cases.jsonl`, trong đó ít nhất một case đến từ một lỗi bạn từng gặp (hoặc một lỗi rất dễ xảy ra) khi dùng agent.

Gợi ý nguồn case:
- Một câu hỏi người dùng viết tắt, sai chính tả, hoặc trộn tiếng Anh.
- Một câu hỏi yêu cầu agent làm việc ngoài phạm vi.
- Một câu hỏi mà agent dễ trả lời đúng nhưng gọi tool sai.

**Tiêu chí đạt:**
- `python 03_eval_dataset.py` báo hợp lệ và hiển thị đủ 11 case.
- Mỗi case mới có `expected_contains`, `must_call_tool` (hoặc `null`), `forbidden_tools`, `tags`.
- Chạy `python 04_code_evaluators.py` và giải thích được case mới bắt được lỗi gì.

**Câu hỏi suy nghĩ:** nếu case mới fail ngay từ lần đầu, bạn sửa agent hay sửa kỳ vọng? Vì sao?

---

## Bài 2 — Evaluator cho tầng retrieval (trung bình)

**Việc:** viết thêm evaluator `eval_retrieval` kiểm tài liệu kỳ vọng có trong `result.retrieved`.

Gợi ý:
- Thêm trường tuỳ chọn `expected_docs` vào case, ví dụ `["doc-policy-tai-nghe"]`.
- Evaluator đạt khi **mọi** doc kỳ vọng đều có trong danh sách lấy về.
- Đăng ký evaluator vào `EVALUATORS` trong `common/evaluators.py`.
- Cập nhật `validate()` để kiểm kiểu của `expected_docs` nếu có.

**Tiêu chí đạt:**
- Case `policy-headphone` và `policy-keyboard` phân biệt được tài liệu đúng.
- Làm retrieval sai (sửa tạm `retrieve()`) thì evaluator báo fail.
- Bảng của bài 04 có thêm cột `retrieval`.

**Câu hỏi suy nghĩ:** vì sao kiểm retrieval lại hữu ích hơn chỉ kiểm câu trả lời cuối?

---

## Bài 3 — Calibrate judge với nhãn người (trung bình, bắt buộc)

**Việc:** tạo 5 cặp (câu hỏi, câu trả lời, nhãn người) trong một file riêng, chạy judge trên cả 5, tính lệch trung bình, rồi sửa rubric hoặc prompt để giảm lệch.

Gợi ý:
- Giữ nguyên judge và chỉ đổi prompt trước; đổi model sau.
- Thêm vào rubric tiêu chí cụ thể: "trả lời sai số ngày trong chính sách = 1 điểm".
- Ghi lại bảng trước/sau, không chỉ nói "đã cải thiện".

**Tiêu chí đạt:**
- Có bảng 5 case với ba cột: nhãn người, judge trước, judge sau.
- Lệch trung bình giảm, hoặc bạn giải thích được vì sao không giảm.
- Nêu ít nhất một case mà judge vẫn sai sau khi sửa, và lý do.

**Câu hỏi suy nghĩ:** nếu judge đúng 5/5 case calibration, bạn đã chứng minh được gì? Chưa chứng minh được gì?

---

## Bài 4 — Regression chặn merge (trung bình)

**Việc:** viết một script `ci_check.sh` (hoặc lệnh trong Makefile) chạy `06_regression.py` và trả mã lỗi. Chứng minh nó chặn khi chất lượng tụt.

Gợi ý:
- Chạy `python 06_regression.py --update-baseline` trên code tốt.
- Dùng `--break` để tạo một lần tụt chất lượng, chạy script, kiểm tra `echo $?`.
- Thêm một dòng trong README của bạn giải thích khi nào được cập nhật baseline.

**Tiêu chí đạt:**
- Script trả 0 khi mọi case giữ nguyên, trả 1 khi có case PASS → FAIL.
- Có log chứng minh cả hai lần chạy.
- Không dùng `|| true` để nuốt mã lỗi.

**Câu hỏi suy nghĩ:** case FAIL → PASS có nên chặn merge không? Vì sao?

---

## Bài 5 — Truy nguyên một lỗi bằng trace (khó)

**Việc:** cố tình làm retrieval trả sai tài liệu (ví dụ sửa `DOCS` hoặc hàm `retrieve`), chạy `01_trace_local.py`, rồi dùng trace để chỉ ra chính xác span nào sai.

**Tiêu chí đạt:**
- In được cây trace của lần chạy hỏng.
- Chỉ ra: span `retrieve` lấy docs nào, span `tool.*` nhận args gì, câu trả lời cuối ra sao.
- Giải thích được lỗi nằm ở retrieval hay ở model/tool — dựa trên dữ liệu trace, không dựa vào cảm giác.
- Khôi phục code gốc sau khi làm xong.

**Câu hỏi suy nghĩ:** nếu trace không ghi `docs`, bạn còn cách nào tìm ra lỗi không? Mất bao lâu?

---

## Bài 6 — Ngân sách token và latency (khó)

**Việc:** thêm hai evaluator ngân sách: `max_tokens` và `max_latency_ms`, chạy trên toàn bộ dataset, và đặt ngưỡng có lý do.

Gợi ý:
- Token hiện là ước tính từ số từ. Ghi rõ trong báo cáo rằng đó là ước tính.
- Đừng đặt ngưỡng latency quá sát máy bạn; CI thường chậm hơn.
- Thử scenario `slow` để chứng minh evaluator bắt được.

**Tiêu chí đạt:**
- Có bảng token/latency cho 8 case.
- Ngưỡng được giải thích bằng một câu: "chọn X vì …", không phải "cho đẹp".
- Một case vượt ngưỡng bị đánh fail, và bạn nói rõ đó là lỗi agent hay ngưỡng quá chặt.

**Câu hỏi suy nghĩ:** vì sao latency nên là **cảnh báo** trong CI, còn token vượt ngân sách có thể là **chặn merge**?
