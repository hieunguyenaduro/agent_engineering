# Bài tập Buổi 10 — Capstone

Bắt buộc: bài 1 và bài 4. Đây là hai bài tạo nên bộ hồ sơ nộp cuối khóa.

---

## Bài 1 — Capstone thu nhỏ, chạy được end-to-end (bắt buộc)

**Việc:** dựng một hệ thống tối thiểu trong một file `capstone.py` (hoặc tách `common/` nếu dài), gồm:

1. Một kho tài liệu nhỏ (3–5 tài liệu) có trường `tenant`.
2. Retrieval **lọc tenant ngay trong truy vấn**.
3. Guard: nếu điểm khớp thấp hơn ngưỡng thì trả `refused`, không bịa.
4. Câu trả lời cuối có `[nguon: ...]`.
5. Trả về dict có `status`, `answer`, `sources`, `latency_ms`.

**Tiêu chí đạt:**
- Ba câu hỏi chạy được: một `ok`, một `refused`, một của tenant khác.
- Không câu trả lời nào chứa thông tin không có trong tài liệu đã lấy.
- In ra được trạng thái và nguồn cho từng câu.

Đây chính là `02_wire_system.py` phiên bản dữ liệu của bạn.

---

## Bài 2 — Bảng điểm kiến trúc của bạn (trung bình)

**Việc:** sửa `01_architecture_choice.py` để so sánh **ba phương án của chính bạn**, không dùng ba phương án mẫu.

**Yêu cầu:**
- Tự chọn 5 tiêu chí và trọng số, tổng = 1.0.
- Chấm điểm 1–5 cho từng phương án, kèm một dòng lý do cho mỗi điểm.
- Chạy kiểm tra độ nhạy với ít nhất hai bộ trọng số khác.

**Tiêu chí đạt:** giải thích được vì sao chọn phương án thắng, và nói rõ phương án đó **mất gì**. Câu "vì nó tốt hơn" không được tính.

---

## Bài 3 — Failure drill đầy đủ (trung bình)

**Việc:** thêm vào `03_failure_drill.py` hai kịch bản nữa:

1. `timeout` — một bước chạy quá lâu, bị cắt.
2. `guard_fail` — guard tự ném lỗi (ví dụ cấu hình ngưỡng sai).

**Yêu cầu:**
- Cả hai không được làm process crash.
- Mỗi kịch bản phải có trạng thái và câu trả lời an toàn.
- In bảng tổng hợp: kịch bản → trạng thái → có câu trả lời hay không.

**Tiêu chí đạt:** 7/7 kịch bản, 0 crash. Giải thích được sự khác nhau giữa `degraded` và `error`.

---

## Bài 4 — Viết phần "giới hạn và bước tiếp" (bắt buộc)

**Việc:** viết một file `GIOI-HAN.md` cho hệ thống của bạn, tối đa 1 trang, gồm ba phần:

1. **Chưa làm gì** — ít nhất 4 mục cụ thể (ví dụ: chưa có auth thật, eval mới 8 case, chưa có TTL cho session).
2. **Rủi ro nếu lên production ngay** — mỗi giới hạn đi kèm một hậu quả thật.
3. **Ba việc tiếp theo** — theo thứ tự ưu tiên, mỗi việc nêu tiêu chí hoàn thành đo được.

**Tiêu chí đạt:**
- Không có câu chung chung kiểu "cần cải thiện chất lượng".
- Mỗi việc tiếp theo có con số hoặc điều kiện kiểm chứng.
- Đọc xong, người khác biết chính xác bạn đang ở đâu.

Đây là phần hội đồng tin bạn nhất. Đừng bỏ qua.

---

## Bài 5 — Eval lên 20 case (khó)

**Việc:** mở rộng `04_eval_report.py` lên 20 case, trong đó:

- 12 case `ok` (có nguồn đúng và nội dung đúng).
- 4 case `refused` (câu hỏi ngoài phạm vi kho).
- 4 case biên: câu hỏi mơ hồ, câu hỏi có từ khoá trùng nhưng khác nghĩa, câu hỏi của tenant khác.

**Yêu cầu:**
- Ghi ra `reports/eval-report.md` với đủ bốn phần như bản mẫu.
- Chỉ ra ít nhất một case trượt và **vì sao** trượt.
- Sửa một thứ (thêm từ đồng nghĩa, đổi ngưỡng, thêm tài liệu) rồi đo lại.

**Tiêu chí đạt:** bảng trước/sau bằng số thật, kèm giải thích. Không được xoá case trượt khỏi bộ eval để đẹp báo cáo.

---

## Bài 6 — Demo 10 phút có bản ghi (khó)

**Việc:** quay một video 10 phút demo hệ thống của bạn, theo đúng sáu phần trong `06_demo_script.py`.

**Yêu cầu:**
- Có một câu hỏi bị từ chối, và bạn giải thích vì sao từ chối là đúng.
- Có một lần chạy failure drill.
- Có phần nói rõ giới hạn (dùng `GIOI-HAN.md`).
- Không đọc script; chỉ dùng nó để tập.

**Tiêu chí đạt:** người xem hiểu hệ thống làm gì, tin vào con số, và biết nó chưa làm gì — trong 10 phút.
