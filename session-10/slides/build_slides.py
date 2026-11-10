"""Tạo slide Buổi 10.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from pptx.enum.text import PP_ALIGN  # noqa: E402
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, CONTENT_W, INK, MARGIN, MUTED, NAVY, PANEL, WHITE, Deck,
)

d = Deck(session="Agent Engineering · Buổi 10", out=Path(__file__).with_name("slides.pptx"))

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 10/10",
    "Capstone:\nGhép hệ thống",
    "Kiến trúc · Eval · Failure drill · Demo",
    "120 phút · 55 phút lý thuyết & demo · 60 phút thực hành",
    notes="""Hôm nay không có khái niệm mới. Chín buổi trước đã cho đủ mảnh.
Việc của buổi này là ghép lại và chứng minh bằng số.
Nói ngay từ đầu: điểm capstone nằm ở bằng chứng, không ở số tính năng.
Mời lớp mở sẵn 6 file, chúng ta chạy lần lượt.""",
)

# --- 2. Statement -----------------------------------------------------------
d.statement(
    "Nguyên tắc capstone",
    "Không chấm số tính năng.\nChấm bằng chứng.",
    "Một hệ thống nhỏ mà đo được, giải thích được, luôn thắng\nmột hệ thống nhiều tính năng mà không ai biết nó đúng hay sai.",
    notes="""Đây là câu định hướng cả buổi. Lặp lại khi chấm bài.
Hỏi lớp: hệ thống của bạn có con số nào chứng minh nó tốt không?
Nếu câu trả lời là 'em thấy nó trả lời khá đúng', đó chính là vấn đề buổi này giải quyết.""",
)

# --- 3. Rubric --------------------------------------------------------------
s = d.content("Chấm điểm", "Năm tiêu chí của capstone", notes="""Đọc bảng, nhấn ba dòng: chạy được, đo được, giải thích được.
20% cho 'chạy được end-to-end' nghĩa là không cần tính năng gì thêm.
25% cho eval là phần nặng nhất — vì đó là thứ phân biệt demo với sản phẩm.
Nói rõ: thiếu một mục vẫn qua, thiếu 'giải thích được' thì không.""")
d.table(
    s,
    ["Tiêu chí", "Trọng số", "Bằng chứng phải có"],
    [
        ["Chạy được end-to-end", "20%", "Một câu hỏi đi từ input đến câu trả lời có nguồn"],
        ["Chất lượng có đo", "25%", "Eval report với case đạt/trượt"],
        ["Hỏng tử tế", "20%", "Failure drill: tắt một phụ thuộc, không crash"],
        ["Chi phí & độ trễ", "20%", "p50/p95, token, USD/1.000 request"],
        ["Giải thích được", "15%", "Trả lời được 'vì sao chọn kiến trúc này'"],
    ],
    top=2.0, col_widths=[4.0, 1.9, 7.3], size=15, row_height=0.72,
)

# --- 4. Section 1 -----------------------------------------------------------
d.section("01", "Chọn kiến trúc", "Bằng bảng điểm, không bằng cảm giác.", notes="""Phần này 12 phút. Bắt đầu bằng quyết định lớn nhất: chọn kiến trúc nào.
Điểm cần nhấn: bảng điểm không phải công thức chân lý, nó là cách buộc bạn nói ra đánh đổi.
Cuối phần sẽ có kiểm tra độ nhạy — đó là phần đáng tin nhất.""",
)

# --- 5. Ba phương án --------------------------------------------------------
s = d.content("Lựa chọn", "Ba phương án cho cùng một bài toán", notes="""Ba phương án này tương ứng ba buổi: một agent (buổi 2), supervisor (buổi 6), handoff (buổi 6).
Hỏi lớp: phương án nào nghe 'xịn' nhất? Thường là C.
Nhưng xịn không có nghĩa là phù hợp. Bảng điểm sẽ trả lời.
Đừng vội kết luận trước khi xem trọng số.""")
d.table(
    s,
    ["Phương án", "Cấu trúc", "Điểm mạnh", "Điểm yếu"],
    [
        ["A", "Một agent + retrieval", "Đơn giản, nhanh, rẻ", "Chất lượng giới hạn ở một prompt"],
        ["B", "Supervisor + 2 worker", "Tách tra cứu và soạn câu", "Thêm lần gọi model, khó debug"],
        ["C", "Handoff chain", "Chuyển hẳn ngữ cảnh", "Chậm nhất, đắt nhất"],
    ],
    top=2.1, col_widths=[1.5, 4.3, 3.4, 4.0], size=16, row_height=0.95,
)

# --- 6. Code bảng điểm ------------------------------------------------------
s = d.content("Demo · 01_architecture_choice.py", "Trọng số phải cộng lại bằng 1.0", notes="""Chạy live. Chỉ vào CRITERIA: mỗi dòng là một đánh đổi có trọng số.
Điểm 1–5 là chủ quan — và điều đó ổn, miễn là bạn viết ra.
Hàm score chỉ là trung bình có trọng số, không có gì huyền bí.
Nhấn: nếu trọng số không cộng bằng 1.0, kết quả vô nghĩa.""")
d.code(
    s,
    '''CRITERIA = {
    "chat_luong": (0.30, "Chất lượng câu trả lời"),
    "do_tre":     (0.20, "Độ trễ thấp"),
    "chi_phi":    (0.20, "Chi phí thấp"),
    "don_gian":   (0.15, "Dễ xây và dễ hiểu"),
    "debug":      (0.15, "Dễ debug khi sai"),
}

def score(option: dict) -> float:
    return sum(weight * option[key]
               for key, (weight, _) in CRITERIA.items())''',
    top=2.0, height=3.3, size=14,
)
d.text(s, MARGIN, 5.5, CONTENT_W, 0.7, "Điểm 1–5 là chủ quan. Viết ra trọng số là cách biến chủ quan thành tranh luận được.", 16, MUTED)

# --- 7. Độ nhạy -------------------------------------------------------------
s = d.content("Kiểm tra độ nhạy", "Đổi trọng số, người thắng có đổi?", notes="""Đây là slide quan trọng nhất phần này.
Nếu đổi trọng số mà người thắng đổi, lựa chọn của bạn phụ thuộc vào ưu tiên — phải nói rõ.
Trong ví dụ, A thắng ở cả ba bộ. Đó là kết luận đáng tin.
Hỏi lớp: kết luận của bạn có đổi khi ưu tiên chất lượng gấp đôi không?""")
d.table(
    s,
    ["Bộ trọng số", "Người thắng", "Điểm"],
    [
        ["Cân bằng (mặc định)", "A. Một agent + retrieval", "4.70"],
        ["Ưu tiên độ trễ gấp đôi", "A. Một agent + retrieval", "4.82"],
        ["Ưu tiên chất lượng gấp đôi", "A. Một agent + retrieval", "4.55"],
    ],
    top=2.1, col_widths=[4.4, 5.2, 2.2], size=17, row_height=0.85,
)
d.text(s, MARGIN, 5.35, CONTENT_W, 0.9, "Nếu người thắng đổi, bạn phải nói rõ mình đang ưu tiên gì. Đó chính là câu hội đồng sẽ hỏi.", 17, MUTED)

# --- 8. Statement -----------------------------------------------------------
d.statement(
    "Ra quyết định",
    "Chọn kiến trúc là chọn\ncái mình chấp nhận mất.",
    "Bạn không chọn phương án tốt nhất. Bạn chọn phương án\ncó điểm yếu mình sống được.",
    notes="""Câu này khó nghe nhưng đúng. Mọi kiến trúc đều mất thứ gì đó.
A mất chất lượng ở câu hỏi phức tạp. B mất độ trễ và tiền. C mất khả năng debug.
Ai nói phương án của mình không có điểm yếu là chưa hiểu phương án đó.""",
)

# --- 9. Section 2 -----------------------------------------------------------
d.section("02", "Nối hệ thống", "Một câu hỏi đi qua những đâu?", notes="""Phần này 12 phút. Ghép retrieval, guard, generation, đo lường vào một hàm.
Điểm cần nhấn: trả dict thay vì chuỗi. Đó là quyết định thiết kế, không phải chi tiết.""",
)

# --- 10. Sơ đồ pipeline -----------------------------------------------------
s = d.content("Luồng", "Bốn bước, một hàm", notes="""Vẽ theo chiều ngang: question → retrieve → guard → generate → result.
Chỉ vào chỗ retrieve: lọc tenant ngay trong truy vấn, không lọc sau.
Chỉ vào guard: đây là chỗ quyết định từ chối, không phải prompt.
Nhấn: mọi bước đều ghi span — thời gian và trạng thái.""")
steps = [("question", PANEL), ("retrieve\n+ tenant", ACCENT_SOFT), ("guard\nđủ dữ liệu?", PANEL), ("generate\n+ nguồn", ACCENT_SOFT)]
for i, (label, color) in enumerate(steps):
    x = MARGIN + i * 2.95
    d.panel(s, x, 2.35, 2.55, 1.5, color)
    d.text(s, x + 0.18, 2.75, 2.2, 0.9, label, 17, INK if color != NAVY else WHITE,
           bold=True, align=PP_ALIGN.CENTER)
    if i < 3:
        d.text(s, x + 2.58, 2.85, 0.4, 0.5, "→", 24, ACCENT, bold=True)

d.panel(s, MARGIN + 3.0, 4.45, 6.3, 0.95, NAVY)
d.text(s, MARGIN + 3.2, 4.65, 5.9, 0.6, "result: status · answer · sources · spans · cost", 15, WHITE, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN, 5.75, CONTENT_W, 0.7, "Không bước nào được ném exception ra ngoài. Mỗi bước trả trạng thái.", 17, MUTED)

# --- 11. Code answer --------------------------------------------------------
s = d.content("Demo · 02_wire_system.py", "Trả dict, không trả chuỗi", notes="""Chạy live một câu. Chỉ vào bốn trường: status, answer, sources, spans.
Hỏi lớp: nếu chỉ trả chuỗi, bạn mất gì? Mất nguồn, mất thời gian từng bước, mất khả năng phân biệt từ chối với lỗi.
Nhấn: bốn trạng thái là hợp đồng với tầng trên — API, UI, alert đều dựa vào đó.""")
d.code(
    s,
    '''result = answer("Đổi trả trong bao nhiêu ngày?", tenant="shop-a")

result["status"]    # ok | refused | degraded | error
result["answer"]    # câu trả lời kèm [nguon: ...]
result["sources"]   # danh sách nguồn + score
result["spans"]     # từng bước: tên, ms, trạng thái

# Một câu ngoài phạm vi:
result = answer("Shop A có bán laptop không?", tenant="shop-a")
result["status"]    # -> "refused"''',
    top=2.0, height=3.4, size=15,
)

# --- 12. Bốn trạng thái -----------------------------------------------------
s = d.content("Hợp đồng", "Bốn trạng thái, không phải hai", notes="""Hai trạng thái (đúng/sai) là thiết kế non. Bốn trạng thái giúp tầng trên xử lý đúng.
ok: trả lời bình thường. refused: không có dữ liệu — không phải lỗi, không nên alert.
degraded: một phụ thuộc chết, vẫn trả lời an toàn — nên alert mức thấp.
error: không thể trả lời — alert ngay.
Hỏi lớp: 'không tìm thấy tài liệu' nên là refused hay error? Trả lời: refused.""")
d.table(
    s,
    ["Trạng thái", "Nghĩa", "Người dùng thấy", "Có alert?"],
    [
        ["ok", "Trả lời được, có nguồn", "Câu trả lời + nguồn", "Không"],
        ["refused", "Không đủ dữ liệu", "Mình không tìm thấy tài liệu...", "Không"],
        ["degraded", "Một phụ thuộc chết", "Hệ thống tra cứu đang bảo trì...", "Mức thấp"],
        ["error", "Không thể trả lời", "Có lỗi, vui lòng thử lại", "Ngay"],
    ],
    top=2.0, col_widths=[2.2, 3.6, 5.2, 2.2], size=15, row_height=0.78,
)

# --- 13. Demo output --------------------------------------------------------
s = d.content("Kết quả thật", "Ba câu, ba hành vi", notes="""Ba dòng này là toàn bộ buổi học trong một bảng.
Câu 1: có dữ liệu, trả lời kèm nguồn.
Câu 2: ngoài phạm vi, từ chối — đây là hành vi đáng tin nhất.
Câu 3: tenant khác, chỉ thấy tài liệu của tenant đó.
Nhấn: không câu nào bịa. Đó là điều bạn phải chứng minh trước lớp.""")
d.table(
    s,
    ["Câu hỏi", "Trạng thái", "Kết quả"],
    [
        ["Đổi trả trong bao nhiêu ngày?", "ok", "7 ngày + nguồn doi-tra"],
        ["Shop A có bán laptop không?", "refused", "Không tìm thấy tài liệu đủ liên quan"],
        ["Chính sách đổi trả của Shop B?", "ok", "Chỉ nguồn shop-b, không lẫn shop-a"],
    ],
    top=2.1, col_widths=[5.0, 2.4, 5.8], size=16, row_height=0.9,
)
d.text(s, MARGIN, 5.25, CONTENT_W, 0.8, "Không câu nào bịa. Đó là điều phải chứng minh, không phải điều phải tuyên bố.", 17, MUTED)

# --- 14. Section 3 ----------------------------------------------------------
d.section("03", "Failure drill", "Tắt từng phụ thuộc và xem hệ thống phản ứng.", notes="""Phần này 10 phút. Đây là phần phân biệt demo với sản phẩm.
Mục tiêu không phải không bao giờ lỗi — mà là lỗi nào cũng có câu trả lời an toàn.""",
)

# --- 15. Năm kịch bản -------------------------------------------------------
s = d.content("Kịch bản", "Năm cách hệ thống có thể hỏng", notes="""Năm kịch bản, cùng một câu hỏi. Chỉ khác phụ thuộc bị tắt.
retrieval_down: dịch vụ chết — degraded. empty_index: kho rỗng — refused.
slow_model: chậm nhưng vẫn ok. model_error: 500 — error.
Nhấn: 'kho rỗng' và 'dịch vụ chết' là hai chuyện khác nhau, phải trả hai trạng thái khác nhau.""")
d.table(
    s,
    ["Kịch bản", "Điều gì hỏng", "Trạng thái"],
    [
        ["normal", "Không", "ok"],
        ["retrieval_down", "Dịch vụ tìm kiếm chết", "degraded"],
        ["empty_index", "Kho dữ liệu rỗng", "refused"],
        ["slow_model", "Model chậm", "ok, nhưng p95 xấu"],
        ["model_error", "Model trả 500", "error"],
    ],
    top=2.0, col_widths=[3.4, 5.6, 4.2], size=16, row_height=0.75,
)

# --- 16. Code drill ---------------------------------------------------------
s = d.content("Demo · 03_failure_drill.py", "Không để exception bay ra", notes="""Chạy live. Chỉ vào khối try/except: drill cố tình bắt mọi Exception để chứng minh không crash.
Kết quả in ra: 0/5 crash, 5/5 có câu trả lời an toàn.
Nhấn: đây không phải 'nuốt lỗi'. Lỗi được ghi vào span và trạng thái, chỉ không làm sập request.""")
d.code(
    s,
    '''for name, fail, description in DRILLS:
    try:
        result = answer(QUESTION, "shop-a", fail=fail)
        crashed = False
    except Exception as exc:
        crashed = True        # drill phải chứng minh không xảy ra
        result = {"status": "CRASH", "answer": repr(exc)}

# Kết quả:
# crash              : 0/5
# câu trả lời an toàn: 5/5''',
    top=2.0, height=3.7, size=15,
)
d.text(s, MARGIN, 5.85, CONTENT_W, 0.7, "Bắt lỗi không phải nuốt lỗi: lỗi vào span và trạng thái, request vẫn sống.", 17, MUTED)

# --- 17. Statement ----------------------------------------------------------
d.statement(
    "Hành vi",
    "Hỏng tử tế là một tính năng,\nkhông phải lời xin lỗi.",
    "Người dùng nhận được câu trả lời an toàn và biết chuyện gì đang xảy ra.\nĐó là thứ khiến họ quay lại sau sự cố.",
    notes="""Câu này nên đọc chậm.
Hỏi lớp: lần cuối bạn thấy một sản phẩm hỏng và vẫn khiến bạn tin, đó là khi nào?
Thường là khi nó nói rõ 'phần này đang lỗi' thay vì hiện trang trắng.
Đây cũng là câu nên dùng khi demo trước hội đồng.""",
)

# --- 18. Section 4 ----------------------------------------------------------
d.section("04", "Eval report", "Bằng chứng thay cảm giác.", notes="""Phần này 12 phút. Đây là phần nặng nhất của capstone.
Một báo cáo Markdown đính kèm khi review — không phải ảnh chụp màn hình chat.""",
)

# --- 19. Case schema --------------------------------------------------------
s = d.content("Demo · 04_eval_report.py", "Mỗi case kiểm tra ba thứ", notes="""Ba kiểm tra độc lập: trạng thái, nguồn, nội dung.
Một case chỉ đạt khi cả ba đúng. Đây là chỗ hay bị bỏ: đúng chữ nhưng sai nguồn vẫn là trượt.
Nhấn: expect_source = None cho case refused — không có nguồn là đúng.
Bộ 6 case đủ để học, không đủ để tin.""")
d.code(
    s,
    '''{
    "question": "Đổi trả trong bao nhiêu ngày?",
    "tenant": "shop-a",
    "expect_status": "ok",
    "expect_source": "chinh-sach-doi-tra.md",
    "must_contain": "7 ngày",
}

passed = (status_ok and source_ok and contains_ok)''',
    top=2.0, height=3.0, size=15,
)
d.text(s, MARGIN, 5.25, CONTENT_W, 0.8, "Đúng chữ nhưng sai nguồn vẫn là trượt. Đúng nguồn nhưng thiếu chi tiết cũng trượt.", 17, MUTED)

# --- 20. Báo cáo mẫu --------------------------------------------------------
s = d.content("Kết quả", "Báo cáo mẫu: 6/6 case", notes="""Đây là số thật của pipeline này, không phải số trang trí.
6/6 case đạt, 5/5 câu trả lời có nguồn, 1/1 từ chối đúng.
p95 khoảng 1 ms vì pipeline luật chạy offline — nói rõ đây là số của demo, không phải production.
Nhấn: báo cáo có cả phần 'case trượt'. Nếu không có case trượt, bộ eval quá dễ.""")
d.table(
    s,
    ["Chỉ số", "Kết quả"],
    [
        ["Case đạt", "6/6 (100%)"],
        ["Câu trả lời có nguồn", "5/5"],
        ["Từ chối đúng khi thiếu dữ liệu", "1/1"],
        ["Độ trễ p95", "~1 ms (pipeline luật, không phải model thật)"],
        ["Tổng token / chi phí", "636 token · $0.00014805"],
    ],
    top=2.0, col_widths=[5.4, 7.8], size=16, row_height=0.75,
)

# --- 21. Cách đọc báo cáo ---------------------------------------------------
s = d.content("Đọc báo cáo", "Bốn phần, một mục đích", notes="""Tóm tắt: trả lời 'có tốt không' trong 5 giây.
Chi tiết: trả lời 'case nào trượt'.
Case trượt: trả lời 'vì sao' — để sửa, không để che.
Cách đọc: nhắc rằng chất lượng là cột Đạt.
Nhấn: đừng xoá case trượt khỏi bộ eval để báo cáo đẹp. Đó là tự lừa mình.""")
d.bullets(s, [
    "Tóm tắt — có tốt không, trong 5 giây",
    "Chi tiết — case nào trượt, nguồn nào được dùng",
    "Case trượt — trượt vì sao, để sửa chứ không để che",
    "Cách đọc — chất lượng là cột Đạt, không phải cảm nhận",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 4.9, CONTENT_W, 1.0, "Không có eval report thì 'đã cải thiện' chỉ là ý kiến.", 19, NAVY, bold=True)

# --- 22. Section 5 ----------------------------------------------------------
d.section("05", "Chi phí & độ trễ", "Người dùng nhớ lần chậm nhất.", notes="""Phần này 8 phút. Ngắn nhưng quyết định bạn có dám đưa hệ thống ra dùng hay không.
Điểm cần nhấn: p95, không phải trung bình.""",
)

# --- 23. Percentile ---------------------------------------------------------
s = d.content("Đo lường", "Bốn con số, bốn câu hỏi", notes="""Chạy 40 request, 4 request cuối cố tình chậm.
p50 0.3 ms, p95 353 ms, p99 354 ms. Bỏ 4 request chậm thì p95 về 0.6 ms.
Hỏi lớp: nếu chỉ báo cáo trung bình, bạn giấu được điều gì? Giấu đuôi chậm.
Đây là lý do các SLA thật luôn dùng p95 hoặc p99.""")
d.table(
    s,
    ["Chỉ số", "Giá trị mẫu", "Trả lời câu hỏi"],
    [
        ["Trung bình", "—", "Phần lớn request nhanh"],
        ["p50", "0.3 ms", "Một nửa người dùng nhanh hơn con số này"],
        ["p95", "353 ms", "5% chậm nhất — thường là người bỏ đi"],
        ["p99", "354 ms", "Sự cố hiếm nhưng có thật"],
    ],
    top=2.0, col_widths=[3.0, 3.2, 7.0], size=16, row_height=0.65,
)
d.text(s, MARGIN, 5.75, CONTENT_W, 0.8, "4 request chậm trong 40 đủ để p95 tăng hàng trăm lần. Trung bình che mất điều đó.", 17, MUTED)

# --- 24. Chi phí ------------------------------------------------------------
s = d.content("Demo · 05_cost_latency.py", "Chiếu chi phí, ghi rõ giả định", notes="""Chỉ vào chuỗi: token trung bình → USD/request → USD/1.000 → 10k/ngày × 30 ngày.
Nhấn: con số tuyệt đối của pipeline luật không chuyển sang production được, nhưng cách đo thì chuyển được.
Phần multi-agent là ước lượng 2.4× token — nói rõ là giả định, không phải kết quả đo.
Đừng bao giờ trình bày ước lượng như số thật.""")
d.code(
    s,
    '''total_cost = sum(costs)
per_request = total_cost / len(costs)
per_1k = per_request * 1_000
per_month = per_request * 10_000 * 30

# Giả định multi-agent: thêm 1 lần điều phối
# và 1 lần tổng hợp -> ~2.4x token.
multi_cost = per_request * 2.4''',
    top=2.0, height=2.9, size=15,
)
d.text(s, MARGIN, 5.15, CONTENT_W, 0.9, "Ước lượng phải được gọi là ước lượng. Nếu không, bạn đang bịa số.", 17, MUTED)

# --- 25. Section 6 ----------------------------------------------------------
d.section("06", "Demo 10 phút", "Kể chuyện, không liệt kê tính năng.", notes="""Phần này 8 phút. Demo là kỹ năng, không phải may mắn.
Sáu phần, mỗi phần có mục đích. Tập hai lần rồi bỏ script.""",
)

# --- 26. Kịch bản -----------------------------------------------------------
s = d.content("Kịch bản", "Sáu phần trong 10 phút", notes="""Đọc nhanh sáu dòng. Nhấn phần 2 và phần 5.
Phần 2 có một câu bị từ chối — đó là lúc hội đồng tin bạn nhất.
Phần 5 là failure drill, không phải phần 'nếu còn thời gian'.
Nhấn: phần 6 nói rõ chưa làm gì. Danh sách giới hạn làm bạn đáng tin hơn.""")
d.table(
    s,
    ["Thời gian", "Nội dung", "Mục đích"],
    [
        ["0:00–1:00", "Vấn đề: 4 phút tra 3 file", "Cho thấy nỗi đau có thật"],
        ["1:00–3:00", "Ba câu hỏi thật", "Có dữ liệu, từ chối, tenant khác"],
        ["3:00–5:00", "Kiến trúc bốn hộp", "Chỉ vào chỗ kiểm tra tenant"],
        ["5:00–7:00", "Eval report", "Bằng chứng thay cảm giác"],
        ["7:00–8:30", "Failure drill", "Hỏng tử tế trông thế nào"],
        ["8:30–10:00", "Giới hạn và bước tiếp", "Nói rõ chưa làm gì"],
    ],
    top=2.0, col_widths=[2.4, 5.4, 5.4], size=15, row_height=0.62,
)

# --- 27. Nguyên tắc demo ----------------------------------------------------
s = d.content("Trình bày", "Ba nguyên tắc, một kế hoạch dự phòng", notes="""Một: câu hỏi thật, không phải câu đã thuộc.
Hai: có một lần từ chối — đừng giấu.
Ba: nói rõ chưa làm gì.
Nếu hỏng: nói 'phần này đang lỗi, mình có bản ghi', chuyển sang eval report, kết thúc đúng giờ. Sửa live quá 30 giây là mất cả buổi.
Đọc câu chốt cuối buổi — đó là câu kết demo.""")
d.bullets(s, [
    "Câu hỏi thật, không phải câu đã thuộc",
    "Có một lần từ chối — đó là lúc đáng tin nhất",
    "Nói rõ chưa làm gì, đừng giấu giới hạn",
    "Hỏng thì chuyển sang eval report, kết thúc đúng giờ",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 4.95, CONTENT_W, 1.2, "Câu kết: 'Hệ thống này không phải agent thông minh nhất.\nNó là agent mình biết đo, biết từ chối, và biết hỏng một cách tử tế.'", 17, NAVY, bold=True, line_spacing=1.4)

# --- 28. Lab ----------------------------------------------------------------
s = d.content("Lab", "60 phút: chạy, rồi ghép hệ thống của bạn", notes="""20 phút chạy 6 file, 40 phút ghép hệ thống của bạn.
Đi vòng quanh, hỏi mỗi nhóm: 'hệ thống của bạn trả trạng thái gì khi retrieval chết?'
Ai chưa có eval report, cho họ dùng 04 làm mẫu và thay dữ liệu.
Nhắc: bài nộp cần số thật, không cần nhiều tính năng.""")
d.panel(s, MARGIN, 2.2, 5.2, 2.9, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.6, 0.4, "20 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.3, 2.8, 4.6, 0.6, "Chạy 6 file", 21, NAVY, bold=True)
d.text(s, MARGIN + 0.3, 3.45, 4.6, 1.5, "Kiến trúc, pipeline,\nfailure drill, eval report,\nchi phí, demo script.", 15, INK, line_spacing=1.35)

d.panel(s, MARGIN + 5.6, 2.2, 5.2, 2.9, ACCENT_SOFT)
d.text(s, MARGIN + 5.9, 2.4, 4.6, 0.4, "40 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 5.9, 2.8, 4.6, 0.6, "Capstone của bạn", 21, NAVY, bold=True)
d.text(s, MARGIN + 5.9, 3.45, 4.6, 1.5, "Pipeline chạy được, 8 case eval,\nmột failure drill,\nmột demo 10 phút.", 15, INK, line_spacing=1.35)

# --- 29. Bài tập ------------------------------------------------------------
s = d.content("Về nhà", "Bài tập bắt buộc", notes="""Bài 1 là capstone thu nhỏ. Bài 4 là phần bảo vệ.
Bài 4 quan trọng hơn vẻ ngoài của nó: người viết được giới hạn là người hiểu hệ thống.
Nhắc hạn nộp và tiêu chí: số thật, giải thích được, không bịa.""")
d.bullets(s, [
    "Bài 1 — capstone thu nhỏ: retrieve + guard + nguồn + trạng thái",
    "Bài 4 — GIOI-HAN.md: chưa làm gì, rủi ro, ba việc tiếp theo",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 3.8, CONTENT_W, 1.6, "Nộp: repo + eval-report.md + GIOI-HAN.md + video demo 10 phút.\nTiêu chí: số thật, giải thích được, không bịa.", 17, MUTED, line_spacing=1.5)

# --- 30. Tổng kết -----------------------------------------------------------
s = d.content("Tổng kết", "Năm câu mang về", notes="""Đọc chậm, đây là lần cuối cả khóa.
Câu 1 nhắc lại tinh thần buổi. Câu 3 là hợp đồng trạng thái. Câu 5 là bộ số bạn mang đi.
Dừng ở câu 5 và mời lớp đặt câu hỏi. Cảm ơn lớp.""")
d.bullets(s, [
    "Capstone chấm bằng chứng, không chấm số tính năng.",
    "Chọn kiến trúc bằng bảng điểm, và kiểm tra độ nhạy.",
    "Hệ thống tốt trả trạng thái: ok, refused, degraded, error.",
    "Hỏng tử tế là một tính năng; failure drill chứng minh điều đó.",
    "Chất lượng đo bằng eval, tốc độ bằng p95, chi phí bằng USD/1.000.",
], top=2.05, size=20, gap=16)

d.save()
