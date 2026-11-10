# Khuôn làm một buổi học

Tài liệu này dành cho người (hoặc agent) soạn bài. Mọi buổi phải theo đúng khuôn để học viên không phải học lại cách đọc tài liệu mỗi tuần.

## 1. Cấu trúc thư mục

```
session-XX/
├── README.md              ← tài liệu giảng, tiếng Việt
├── slides/
│   ├── build_slides.py    ← dùng tools/deck.py
│   └── slides.pptx        ← sinh ra, không sửa tay
├── 01_....py              ← 5–6 ví dụ, đánh số theo thứ tự dạy
├── 02_....py
├── ...
├── common/                ← code dùng chung trong buổi
├── exercises.md           ← bài tập, ghi rõ bắt buộc
├── requirements.txt
└── .env.example
```

## 2. Giọng văn

- Tiếng Việt, câu ngắn, xưng "bạn", không dùng từ đao to búa lớn.
- Mỗi phần lý thuyết phải có **một câu chốt** in đậm: `> **Một câu chốt:** ...`
- Dùng ẩn dụ cụ thể (chuyên gia trong phòng kín, đôi tay, phanh xe...), không dùng ẩn dụ trừu tượng.
- Giải thích **vì sao**, không chỉ **làm thế nào**.
- Mỗi khái niệm đi kèm đúng một file code chạy được.
- Không bịa số liệu (token, %, thời gian) — nếu không đo được thì nói là ví dụ.

## 3. README

Cấu trúc bắt buộc:

```
# Buổi N — Tên
> Một đoạn mở: buổi này giải quyết vấn đề gì, nối tiếp buổi trước ra sao.
**Thời lượng:** 120 phút — 55 lý thuyết + 60 lab + 5 tổng kết.

## 0. Chuẩn bị        (lệnh cài đặt, cách chạy FAKE=1)
## 1..7. Các phần lý thuyết (mỗi phần 10–20 phút, có demo và câu chốt)
## 8. Lab             (bảng: file → câu hỏi phải trả lời được; 2 phần A/B)
## 9. Bài tập về nhà
## 10. Tổng kết — 5 câu mang về
## 11. Chuẩn bị buổi sau
## Phụ lục — Cấu trúc thư mục
```

Độ dài: 250–400 dòng. Không dài hơn — học viên phải đọc hết trước buổi.

## 4. Code

- Mỗi file chạy độc lập: `python 03_ten_file.py` từ thư mục buổi.
- Đầu file: docstring 3–6 dòng nói file dạy gì và lệnh chạy.
- Comment tiếng Việt, chỉ comment chỗ **vì sao**, không comment chỗ hiển nhiên.
- In ra terminal theo từng bước, có nhãn `[think]`, `[act]`, `[done]`, `[verify]` khi phù hợp.
- **Luôn có chế độ offline**: nếu dịch vụ ngoài không có (API key, Qdrant server, Langfuse), code vẫn chạy bằng fallback và in ra thông báo rõ ràng.
- Không bắt buộc Docker. Qdrant dùng `QdrantClient(":memory:")` hoặc path local.
- Không file nào quá ~150 dòng. Nếu dài hơn, tách `common/`.
- Không hardcode key. Đọc từ `.env`.
- Mọi lỗi có thể xảy ra phải được bắt và in ra dễ hiểu.

## 5. Slide

Dùng `tools/deck.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from deck import Deck, MARGIN, CONTENT_W, ...

d = Deck(session="Agent Engineering · Buổi N", out=Path(__file__).with_name("slides.pptx"))
d.title("AGENT ENGINEERING · BUỔI N/10", "Tiêu đề", "Phụ đề", "120 phút ...")
d.section("01", "Tên phần", "Một dòng mô tả")
s = d.content("KICKER", "Tiêu đề slide", notes="...")
d.bullets(s, [...])
d.code(s, "code...", top=2.0, height=3.0, size=14)
d.table(s, headers, rows, col_widths=[...])
d.panel(s, x, y, w, h, color)
d.note(s, "ghi chú giảng")
d.save()
```

Yêu cầu:

- 24–30 slide.
- **Mọi slide đều có speaker notes** (2–5 câu, nói giảng viên cần nói gì, chỗ nào hỏi lớp).
- Mỗi slide một ý. Tối đa 5 bullet, mỗi bullet một dòng.
- Code trên slide: tối đa 14 dòng, font ≥ 13.
- Bảng: tối đa 5 hàng, font ≥ 15.
- Dùng `d.statement()` cho câu quan trọng nhất của buổi.
- Không nhồi chữ. Nếu không vừa, tách slide.

## 6. Kiểm tra trước khi giao

```bash
# 1. Cú pháp
<PATHS>/python -m py_compile 0*.py common/*.py slides/build_slides.py

# 2. Chạy từng ví dụ ở chế độ offline
for f in 0*.py; do FAKE=1 <PYTHON> "$f" || echo "FAIL $f"; done

# 3. Sinh slide
<PYTHON> slides/build_slides.py

# 4. Kiểm tra tràn chữ (script nội bộ)
<PYTHON> /tmp/check_slides.py slides/slides.pptx
```

Báo cáo lại: file nào chạy được, file nào cần điều kiện gì (API key, package), slide có bao nhiêu trang.

## 7. Những điều không được làm

- Không bịa kết quả chạy.
- Không thêm dịch vụ trả phí bắt buộc.
- Không copy nguyên bài của buổi khác mà không đổi nội dung.
- Không dùng thuật ngữ mà không giải thích ngay lần đầu xuất hiện.
- Không để code minh hoạ dài hơn 150 dòng.
