# Buổi 10 — Capstone: Ghép hệ thống và bảo vệ trước lớp

> Chín buổi trước cho bạn từng mảnh: vòng lặp agent, tool, context, retrieval, multi-agent, eval, bảo mật, API. Buổi cuối không dạy khái niệm mới. Nó bắt bạn **ghép các mảnh thành một hệ thống**, rồi chứng minh bằng số rằng hệ thống đó chạy được, hỏng tử tế, và có giới hạn rõ ràng.

**Thời lượng:** 120 phút — 55 phút lý thuyết & demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-10
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python 01_architecture_choice.py
python 02_wire_system.py
python 03_failure_drill.py
python 04_eval_report.py
python 05_cost_latency.py
python 06_demo_script.py
```

Sáu file chạy **không cần API key, không cần Docker, không cần mạng**. Pipeline capstone là bản rút gọn có chủ ý: retrieval bằng token + cosine, sinh câu trả lời bằng cách chọn câu gần nhất. Nhờ vậy eval **lặp lại được** — chạy hôm nay và tuần sau ra cùng kết quả.

Đổi sang model thật chỉ ở một chỗ: hàm `answer()` trong `common/pipeline.py`. Phần đo lường, guard, trace, báo cáo giữ nguyên.

---

## 1. Capstone chấm cái gì? (5 phút)

Không chấm số tính năng. Chấm năm thứ:

| Tiêu chí | Trọng số | Bằng chứng phải có |
|---|---|---|
| Chạy được end-to-end | 20% | Một câu hỏi đi từ input đến câu trả lời có nguồn |
| Chất lượng có đo | 25% | Eval report với case đạt/trượt, không phải cảm nhận |
| Hỏng tử tế | 20% | Failure drill: tắt một phụ thuộc, không crash |
| Chi phí & độ trễ | 20% | p50/p95, token, USD/1.000 request |
| Giải thích được | 15% | Trả lời được "vì sao chọn kiến trúc này" |

Một hệ thống nhỏ mà đo được, giải thích được, **luôn thắng** một hệ thống nhiều tính năng mà không ai biết nó đúng hay sai.

> **Một câu chốt:** capstone không phải cuộc thi tính năng — nó là cuộc thi bằng chứng.

---

## 2. Chọn kiến trúc bằng bảng điểm (12 phút)

Chạy `01_architecture_choice.py`.

Ba phương án cho cùng bài toán chăm sóc khách hàng:

| Phương án | Cấu trúc | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| A | Một agent + retrieval | Đơn giản, nhanh, rẻ | Chất lượng giới hạn ở một prompt |
| B | Supervisor + 2 worker | Tách tra cứu và soạn câu | Thêm lần gọi model, khó debug |
| C | Handoff chain | Chuyển hẳn ngữ cảnh | Chậm nhất, đắt nhất |

Mỗi tiêu chí có trọng số, mỗi phương án có điểm 1–5. Tổng là trung bình có trọng số:

```python
CRITERIA = {
    "chat_luong": (0.30, "Chất lượng câu trả lời"),
    "do_tre":     (0.20, "Độ trễ thấp"),
    "chi_phi":    (0.20, "Chi phí thấp"),
    "don_gian":   (0.15, "Dễ xây và dễ hiểu"),
    "debug":      (0.15, "Dễ debug khi sai"),
}

def score(option: dict) -> float:
    return sum(weight * option[key] for key, (weight, _) in CRITERIA.items())
```

Điểm quan trọng không nằm ở phương án thắng. Nó nằm ở **phần kiểm tra độ nhạy**: đổi trọng số thì người thắng có đổi không?

Trong ví dụ, A thắng ở cả ba bộ trọng số. Đó là kết luận đáng tin: lựa chọn không phụ thuộc vào việc bạn ưu tiên gì. Nếu đổi trọng số mà người thắng đổi, bạn phải nói rõ mình đang ưu tiên gì — và đó chính là điều hội đồng sẽ hỏi.

Bảng điểm không phải công thức chân lý. Nó là cách buộc bạn viết ra mình đang đánh đổi gì, thay vì nói "em thấy cái này hợp".

> **Một câu chốt:** chọn kiến trúc là chọn cái mình chấp nhận mất, không phải chọn cái mình thích.

---

## 3. Nối hệ thống: một câu hỏi đi qua đâu? (12 phút)

Chạy `02_wire_system.py`.

```
question
  -> retrieve (lọc tenant ngay trong truy vấn)
  -> guard: đủ dữ liệu chưa? chưa thì từ chối
  -> chọn câu trả lời tốt nhất từ tài liệu
  -> trả lời kèm nguồn
  -> đo token, chi phí, độ trễ, từng span
```

Toàn bộ nằm trong một hàm:

```python
result = answer("Đổi trả trong bao nhiêu ngày?", tenant="shop-a")

result["status"]     # "ok" | "refused" | "degraded" | "error"
result["answer"]     # câu trả lời kèm [nguon: ...]
result["sources"]    # danh sách nguồn + score
result["spans"]      # từng bước, thời gian, trạng thái
```

Trả **dict** thay vì chuỗi là quyết định thiết kế quan trọng. Người gọi cần biết: có nguồn không, mất bao lâu, bước nào chậm, tốn bao nhiêu. Nếu chỉ trả chuỗi, mọi thứ đó biến mất và bạn phải đo lại từ ngoài.

Bốn trạng thái, không phải hai:

| Trạng thái | Nghĩa | Người dùng thấy |
|---|---|---|
| `ok` | Trả lời được, có nguồn | Câu trả lời + nguồn |
| `refused` | Không đủ dữ liệu | "Mình không tìm thấy tài liệu..." |
| `degraded` | Một phụ thuộc chết, vẫn trả lời an toàn | "Hệ thống tra cứu đang bảo trì..." |
| `error` | Không thể trả lời | "Có lỗi, vui lòng thử lại" |

Trong ví dụ, câu "Shop A có bán laptop không?" trả `refused` vì điểm khớp thấp hơn ngưỡng. Câu về Shop B chỉ thấy tài liệu của Shop B. Đó là hai hành vi quan trọng nhất của cả khóa, chạy trong cùng một pipeline.

> **Một câu chốt:** hệ thống tốt trả về trạng thái, không chỉ trả về chữ.

---

## 4. Failure drill: hỏng tử tế (10 phút)

Chạy `03_failure_drill.py`.

Năm kịch bản, chạy trên cùng một câu hỏi:

| Kịch bản | Điều gì hỏng | Trạng thái mong đợi |
|---|---|---|
| `normal` | Không | `ok` |
| `retrieval_down` | Dịch vụ tìm kiếm chết | `degraded` |
| `empty_index` | Kho dữ liệu rỗng | `refused` |
| `slow_model` | Model chậm | `ok` nhưng p95 xấu |
| `model_error` | Model trả 500 | `error` |

Tiêu chí không phải "không bao giờ lỗi". Tiêu chí là:

- **0 crash** — process không sập, không traceback ra người dùng.
- **5/5 có câu trả lời an toàn** — kể cả khi lỗi, người dùng vẫn biết chuyện gì đang xảy ra.
- **Trạng thái đúng** — không đánh đồng "không có dữ liệu" với "hệ thống hỏng".

Đây là phần phân biệt demo với sản phẩm. Demo chỉ chạy đường đẹp. Sản phẩm biết đường xấu trông thế nào.

Một chi tiết đáng chú ý trong output: `slow_model` vẫn trả `ok`, nhưng chậm hơn hàng trăm lần. Nếu chỉ nhìn trạng thái, bạn tưởng mọi thứ ổn. Phải nhìn p95 ở bài sau.

> **Một câu chốt:** hỏng tử tế là một tính năng, không phải lời xin lỗi.

---

## 5. Eval report: bằng chứng thay cảm giác (12 phút)

Chạy `04_eval_report.py`. Báo cáo được ghi ra `reports/eval-report.md`.

Bộ case nhỏ, mỗi case kiểm tra ba thứ:

```python
{
    "question": "Đổi trả trong bao nhiêu ngày?",
    "tenant": "shop-a",
    "expect_status": "ok",
    "expect_source": "chinh-sach-doi-tra.md",
    "must_contain": "7 ngày",
}
```

Ba kiểm tra độc lập:

1. **Trạng thái đúng** — `ok` khi có dữ liệu, `refused` khi không.
2. **Nguồn đúng** — tài liệu trả về phải là tài liệu mong đợi.
3. **Nội dung đúng** — câu trả lời phải chứa thông tin then chốt.

Một case chỉ đạt khi cả ba đúng. Đây là điểm hay bị bỏ: câu trả lời có thể đúng chữ nhưng sai nguồn, hoặc đúng nguồn nhưng thiếu chi tiết.

Báo cáo có bốn phần:

| Phần | Trả lời câu hỏi |
|---|---|
| Tóm tắt | Bao nhiêu case đạt, bao nhiêu có nguồn, p95, tổng chi phí |
| Chi tiết | Từng case: trạng thái, nguồn, đạt hay trượt |
| Case trượt | Trượt vì sao — để sửa, không để che |
| Cách đọc | Nhắc rằng chất lượng là cột Đạt, không phải cảm nhận |

Trong lần chạy mẫu: 6/6 case đạt, 5/5 câu trả lời có nguồn, 1/1 từ chối đúng. Đó là con số thật của pipeline này, không phải số trang trí.

Bộ 6 case đủ để học, không đủ để tin. Bộ thật nên có 30–100 case, lấy từ câu hỏi người dùng và failure case đã gặp.

> **Một câu chốt:** không có eval report thì "đã cải thiện" chỉ là ý kiến.

---

## 6. Chi phí và độ trễ: nhìn p95 (8 phút)

Chạy `05_cost_latency.py`.

Bài này chạy 40 request, trong đó 4 request cuối cố tình chậm. Kết quả mẫu:

```
p50 :      0.3 ms
p95 :    353.4 ms
p99 :    354.1 ms
```

Nếu bỏ 4 request chậm, p95 về 0.6 ms. Bốn request trong 40 (10%) đủ để p95 tăng hàng trăm lần.

Đó là lý do phải nhìn p95, không nhìn trung bình:

| Chỉ số | Trả lời câu hỏi |
|---|---|
| Trung bình | "Phần lớn request nhanh" |
| p50 | "Một nửa người dùng thấy nhanh hơn con số này" |
| p95 | "5% người dùng chậm nhất — thường là người bỏ đi" |
| p99 | "Sự cố hiếm nhưng có thật" |

Chi phí tính theo cùng bộ request: token trung bình, USD/request, USD/1.000, rồi chiếu 10.000 request/ngày trong 30 ngày. Con số tuyệt đối của pipeline luật không chuyển sang production được, nhưng **cách đo** thì chuyển được.

Bài còn ước lượng multi-agent: giả định thêm một lần điều phối và một lần tổng hợp, khoảng 2.4× token. Đó là giả định, không phải kết quả đo — và phải nói rõ như vậy khi báo cáo.

> **Một câu chốt:** người dùng nhớ lần chậm nhất, không nhớ lần trung bình.

---

## 7. Demo 10 phút: kể chuyện, không liệt kê (8 phút)

Chạy `06_demo_script.py`.

Kịch bản sáu phần:

| Thời gian | Nội dung |
|---|---|
| 0:00–1:00 | Vấn đề: nhân viên mất 4 phút tra 3 file |
| 1:00–3:00 | Ba câu hỏi thật: có dữ liệu, phải từ chối, tenant khác |
| 3:00–5:00 | Kiến trúc: bốn hộp, chỉ vào chỗ kiểm tra tenant |
| 5:00–7:00 | Bằng chứng: mở eval report |
| 7:00–8:30 | Failure drill: tắt retrieval, thấy `degraded` |
| 8:30–10:00 | Giới hạn và bước tiếp |

Ba nguyên tắc demo:

1. **Câu hỏi thật, không phải câu đã thuộc.** Demo câu dễ trông giống diễn tập.
2. **Có một lần từ chối.** Đó là lúc hội đồng tin bạn nhất.
3. **Nói rõ chưa làm gì.** Danh sách giới hạn làm bạn đáng tin hơn, không kém đi.

Nếu demo hỏng: nói "phần này đang lỗi, mình có bản ghi", chuyển sang eval report, kết thúc đúng giờ. Sửa live quá 30 giây là mất cả buổi.

> **Một câu chốt:** demo tốt không phải demo nhiều tính năng — nó là một câu chuyện có bằng chứng.

---

## 8. Lab (60 phút)

### Phần A — Chạy và đọc (20 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_architecture_choice.py` | Đổi trọng số thì người thắng có đổi không? Vì sao? |
| `02_wire_system.py` | Bốn trạng thái khác nhau ở đâu? |
| `03_failure_drill.py` | Kịch bản nào trả `degraded`, kịch bản nào `refused`? |
| `04_eval_report.py` | Một case đạt cần mấy điều kiện? |
| `05_cost_latency.py` | Bỏ 4 request chậm thì p95 đổi thế nào? |
| `06_demo_script.py` | Phần nào của demo là bằng chứng, phần nào là trình bày? |

### Phần B — Capstone của bạn (40 phút)

Ghép hệ thống của bạn và chuẩn bị ba thứ:

1. **Một pipeline chạy được** — một hàm `answer()` hoặc một graph, có ít nhất retrieval + guard + trả nguồn.
2. **Một eval report** — tối thiểu 8 case, có case đạt và case từ chối. Ghi ra file Markdown.
3. **Một failure drill** — tắt một phụ thuộc (retrieval, model, DB), chứng minh không crash và có câu trả lời an toàn.

Yêu cầu tối thiểu:

- Trạng thái rõ ràng: `ok` / `refused` / `degraded` / `error`.
- Có số: số case đạt, p95, chi phí/1.000 request.
- Có một slide hoặc một đoạn demo 10 phút.

Làm theo `exercises.md` để có gợi ý từng bước.

---

## 9. Bài tập về nhà

Xem `exercises.md`. Bắt buộc bài 1 và bài 4.

Bài 1 là bản capstone thu nhỏ. Bài 4 là phần bảo vệ: viết ra giới hạn và bước tiếp.

---

## 10. Tổng kết — 5 câu mang về

1. Capstone chấm bằng chứng, không chấm số tính năng.
2. Chọn kiến trúc bằng bảng điểm có trọng số, và kiểm tra độ nhạy.
3. Hệ thống tốt trả về trạng thái — `ok`, `refused`, `degraded`, `error` — không chỉ trả về chữ.
4. Hỏng tử tế là một tính năng; failure drill chứng minh điều đó.
5. Chất lượng đo bằng eval report, tốc độ đo bằng p95, chi phí đo bằng USD/1.000 request.

---

## 11. Sau khóa học

Ba việc nên làm trong hai tuần sau khóa:

1. **Thay pipeline luật bằng model thật**, giữ nguyên eval và failure drill. So sánh số trước/sau.
2. **Mở rộng eval lên 30 case** lấy từ câu hỏi người dùng thật. Đo lại Hit@k và tỉ lệ từ chối đúng.
3. **Thêm observability thật** (Langfuse hoặc OTel) và nối `trace_id` từ API xuống retrieval.

Đừng thêm tính năng mới cho đến khi ba việc trên xong. Một hệ thống nhỏ, đo được, có người dùng thật — tốt hơn một hệ thống nhiều tính năng không ai dùng.

---

## Phụ lục — Cấu trúc thư mục

```
session-10/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_architecture_choice.py
├── 02_wire_system.py
├── 03_failure_drill.py
├── 04_eval_report.py
├── 05_cost_latency.py
├── 06_demo_script.py
├── common/
│   ├── knowledge.py    ← tài liệu, token, cosine, retrieve theo tenant
│   └── pipeline.py     ← answer(): retrieve → guard → trả lời → đo
├── reports/
│   └── eval-report.md  ← sinh bởi 04_eval_report.py
├── exercises.md
├── requirements.txt
└── .env.example
```
