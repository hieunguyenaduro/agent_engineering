"""Tạo slide Buổi 3 — Tool and MCP Engineering.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, CONTENT_W, INK, MARGIN, MUTED, NAVY, PANEL, Deck,
)

d = Deck(session="Agent Engineering · Buổi 3", out=Path(__file__).with_name("slides.pptx"))

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 3/10",
    "Tool &\nMCP Engineering",
    "Contract · Lỗi · SQL · Sandbox · MCP",
    "120 phút · 55 phút lý thuyết & demo · 60 phút thực hành · 5 phút tổng kết",
    notes="""Buổi 1 và 2 cho các bạn một vòng lặp chạy được. Hôm nay nói về đôi tay của agent: tool.
Câu hỏi xuyên suốt: làm sao để model chọn đúng tool, gọi đúng tham số, và không phá dữ liệu.
Cuối buổi sẽ đóng gói tool thành MCP server để nhiều agent dùng chung.""",
)

# --- 2. Nhắc lại vòng gọi tool ----------------------------------------------
s = d.content(
    "Nhắc lại",
    "Model xin gọi, harness chạy",
    notes="""Đây là kiến thức buổi 1, nhắc 60 giây để cả lớp cùng mốc.
Hỏi lớp: trong bốn bước, bước nào model thực sự làm? Chỉ bước 1 và 4.
Nhấn: quyền, timeout, kiểm tra dữ liệu đều nằm ở bước 2 — phía harness.""",
)
d.table(
    s,
    ["Bước", "Ai làm", "Dữ liệu qua lại"],
    [
        ["1. Think", "Model", "tool_calls: [{name, args}]"],
        ["2. Act", "Harness", "tra tên → gọi hàm thật"],
        ["3. Observe", "Harness", "message role=tool"],
        ["4. Think lại", "Model", "trả lời hoặc gọi tiếp"],
    ],
    top=2.05, col_widths=[2.4, 2.4, 6.7], size=17, row_height=0.8,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.7,
       "Model không chạy tool. Nó phát ra một đề nghị dạng JSON; harness quyết định có thực hiện hay không.",
       17, MUTED)

# --- 3. Section 01 ----------------------------------------------------------
d.section("01", "Tool là đôi tay", "Agent chỉ giỏi bằng những gì nó làm được.", notes="""Chuyển ý: nếu model là người trong phòng kín, tool là đôi tay thò ra ngoài.
Đôi tay đó chỉ làm được đúng những gì ta gắn vào — và làm sai được đúng những gì ta cho phép.
Phần này 5 phút, chủ yếu để thống nhất từ ngữ.""")

# --- 4. Model thấy gì -------------------------------------------------------
s = d.content(
    "Góc nhìn của model",
    "Model chỉ thấy hợp đồng, không thấy code",
    notes="""Đây là slide quan trọng nhất phần đầu. Đọc từng dòng, dừng ở cột phải.
Model không thấy database, không thấy quyền, không thấy exception. Nó chỉ thấy một khối JSON.
Vì vậy mọi thứ muốn model biết phải viết vào mô tả; mọi thứ muốn chặn phải viết vào code.""",
)
d.table(
    s,
    ["Model THẤY", "Model KHÔNG thấy"],
    [
        ["Tên tool", "Code Python bên trong"],
        ["Mô tả + khi nào dùng", "Database, file, API thật"],
        ["JSON Schema tham số", "Quyền của tool"],
        ["Kiểu trả về (nếu mô tả)", "Exception và stack trace"],
    ],
    top=2.05, col_widths=[5.8, 5.7], size=17, row_height=0.78,
)
d.text(s, MARGIN, 5.5, CONTENT_W, 0.8,
       "Hệ quả: mô tả là giao diện người dùng của tool. Code là phần bảo vệ.",
       18, NAVY, bold=True)

# --- 5. Section 02 ----------------------------------------------------------
d.section("02", "Tool là API contract", "Năm phần, và model chỉ đọc phần mô tả.", notes="""Phần này 10 phút, gắn với file 01_tool_contract.py.
Nói rõ: contract không phải tài liệu cho người, nó là đầu vào của model.
Sai contract thì model chọn sai — và ta thường đổ lỗi cho model.""")

# --- 6. Năm phần ------------------------------------------------------------
s = d.content(
    "Contract",
    "Năm phần của một tool",
    notes="""Đọc bảng theo thứ tự. Nhấn cột 'ví dụ tốt' — đây là thứ cần viết ra giấy trước khi code.
Hỏi: phần nào hay bị bỏ nhất? Trả lời: kiểu trả về và lỗi.
Mô tả kiểu trả về giúp model biết có nên gọi tiếp hay không.""",
)
d.table(
    s,
    ["Phần", "Ví dụ tốt", "Vì sao"],
    [
        ["Tên", "search_orders", "Động từ + đối tượng"],
        ["Mô tả", "khi nào dùng / khi nào không", "Model phân biệt tool bằng đây"],
        ["Tham số", "customer_id, limit=5", "Ít tham số, ít chỗ đoán sai"],
        ["Trả về", "chuỗi nhiều dòng, có ví dụ", "Model đọc chữ, không đọc object"],
        ["Lỗi", "LỖI: không tìm thấy đơn 1234", "Model đọc được và nói lại"],
    ],
    top=2.0, col_widths=[1.7, 5.0, 4.8], size=16, row_height=0.72,
)
d.text(s, MARGIN, 5.85, CONTENT_W, 0.6,
       "Viết contract trước, code sau. Đổi contract là đổi hành vi của agent.",
       17, MUTED)

# --- 7. Hai schema ----------------------------------------------------------
s = d.content(
    "Demo · 01_tool_contract.py",
    "Hai schema, cùng một model nhìn",
    notes="""Chạy file này live, hoặc chiếu phần in ra. Không cần key.
Chỉ vào schema tệ: một tham số 'data', mô tả không nói gì. Model chỉ có thể đoán.
Rồi schema tốt: enum, minimum/maximum, mô tả nói cả khi nào KHÔNG dùng.""",
)
d.text(s, MARGIN, 1.86, 5.4, 0.3, "TOOL TỆ", 11, ACCENT, bold=True)
d.text(s, MARGIN + 5.9, 1.86, 5.4, 0.3, "TOOL TỐT", 11, ACCENT, bold=True)
d.code(
    s,
    '''{
 "name": "do_stuff",
 "description": "Xử lý dữ liệu.",
 "parameters": {"type": "object",
  "properties": {"data":
   {"type": "string"}}},
 "returns": "string"
}''',
    left=MARGIN, top=2.15, width=5.45, height=3.9, size=13,
)
d.code(
    s,
    '''{
 "name": "search_orders",
 "description": "Tìm đơn của
  một khách. Không dùng
  để hoàn tiền.",
 "parameters": {"type": "object",
  "properties": {
   "customer_id": {"type": "string"},
   "limit": {"type": "integer",
    "maximum": 20}}},
 "required": ["customer_id"]
}''',
    left=MARGIN + 5.9, top=2.15, width=5.45, height=3.9, size=13,
)
d.text(s, MARGIN, 6.2, CONTENT_W, 0.4,
       "Cùng một model, cùng một câu hỏi. Khác nhau ở chỗ model có đoán được hay không.",
       15, MUTED)

# --- 8. Statement -----------------------------------------------------------
d.statement(
    "Bài học từ 01",
    "Model chọn sai tool\nvì mô tả, không vì code.",
    "Hai hàm cùng schema, một đúng một sai. Model không phân biệt được.\nTest mới là thứ phân biệt được — không phải model.",
    notes="""Đây là câu chốt của phần contract. Nói chậm.
Nếu học viên than 'model ngu', hỏi lại: mô tả có nói khi nào không dùng chưa?
Nhắc: schema chỉ là hợp đồng; implementation phải có test riêng.""",
)

# --- 9. Section 03 ----------------------------------------------------------
d.section("03", "Checklist thiết kế", "Sáu điều, theo thứ tự hay vi phạm.", notes="""Phần này 12 phút. Không phải lý thuyết suông — mỗi điều đều có ví dụ trong bài.
Có thể cho lớp chấm chéo tool của nhau theo checklist này ở phần lab.""")

# --- 10. Checklist ----------------------------------------------------------
s = d.content(
    "Checklist",
    "Sáu điều kiểm trước khi viết code",
    notes="""Đọc 5 bullet, rồi nhấn dòng cuối: điều thứ sáu là idempotency.
Hỏi lớp: tool hoàn tiền có nên retry không? Chỉ khi có khoá idempotency.
Đừng đọc thuộc lòng — hỏi từng điều ứng với tool nào trong dự án của họ.""",
)
d.bullets(s, [
    "Động từ rõ: get_order_status, không phải do_stuff",
    "Tham số tối thiểu: mỗi tham số là một chỗ model điền sai",
    "Một việc một tool: tra đơn ≠ hoàn tiền",
    "Trả chuỗi dễ đọc: model đọc chữ, không đọc object",
    "Lỗi là dữ liệu: \"LỖI: ...\" thay vì exception",
], top=2.05, size=19, gap=16)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.9,
       "Điều thứ sáu: idempotent khi có thể — gọi lại không đổi kết quả.\nNếu buộc phải đổi trạng thái, cần khoá idempotency và audit.",
       17, NAVY, bold=True, line_spacing=1.3)

# --- 11. Section 04 ---------------------------------------------------------
d.section("04", "Khi tool lỗi", "Lỗi là dữ liệu, không phải exception.", notes="""Phần này 12 phút, gắn với 02_tool_errors.py.
Đây là phần phân biệt demo với production rõ nhất: mạng sẽ lỗi, dịch vụ sẽ treo.
Câu hỏi dẫn: nếu tool treo 30 giây, agent của bạn làm gì?""")

# --- 12. Timeout code -------------------------------------------------------
s = d.content(
    "Demo · 02_tool_errors.py",
    "Timeout nằm ở lớp bọc, không ở model",
    notes="""Chạy live phần A: tool hỏng 2 lần, lần 3 thành công.
Chỉ vào chỗ exception bị biến thành chuỗi 'LỖI:' — model không bao giờ thấy traceback.
Lưu ý kỹ thuật: thread timeout chỉ bỏ phía gọi; muốn kill thật phải dùng subprocess.""",
)
d.code(
    s,
    '''def call_with_timeout(fn, args, timeout=1.0):
    box = queue.Queue()
    threading.Thread(
        target=lambda: box.put(fn(**args)),
        daemon=True).start()
    try:
        return box.get(timeout=timeout)
    except queue.Empty:
        return f"LỖI: quá {timeout}s (timeout)."''',
    top=1.98, height=2.95, size=15,
)
d.bullets(s, [
    "Thread là daemon: tool treo không giữ tiến trình sống",
    "Kết quả lỗi là chuỗi, model đọc được và nói lại với người dùng",
    "Timeout từng lần chưa đủ — cần cả tổng thời gian",
], top=5.1, height=1.6, size=16, gap=10)

# --- 13. Retry --------------------------------------------------------------
s = d.content(
    "Retry",
    "Khi nào retry, khi nào không",
    notes="""Bảng này là thứ học viên sẽ dùng lại nhiều lần.
Nhấn hàng cuối: retry hoàn tiền mà không idempotent là trừ tiền hai lần.
Hỏi: 400 có nên retry? Không — gọi lại vẫn sai, chỉ tốn tiền và thời gian.""",
)
d.table(
    s,
    ["Tình huống", "Retry?", "Vì sao"],
    [
        ["Timeout mạng, 503", "Có, 2–3 lần", "Lỗi tạm thời, có thể qua"],
        ["400, sai tham số", "Không", "Gọi lại vẫn sai"],
        ["Không tìm thấy đơn", "Không", "Kết quả nghiệp vụ, không phải lỗi"],
        ["Hoàn tiền, gửi mail", "Chỉ khi idempotent", "Retry mù là làm hai lần"],
    ],
    top=2.0, col_widths=[4.4, 3.0, 4.1], size=16, row_height=0.8,
)
d.text(s, MARGIN, 5.6, CONTENT_W, 0.9,
       "Ba con số phải có: số lần thử tối đa · chờ mỗi lần · tổng thời gian được phép.",
       17, NAVY, bold=True)

# --- 14. Demo 02 trace ------------------------------------------------------
s = d.content(
    "Demo · 02_tool_errors.py",
    "Tool treo, agent vẫn trả lời",
    notes="""Chạy phần B: tool ngủ 2 giây, timeout 1 giây, retry 3 lần.
Cho lớp xem trace: ba dòng retry, rồi một chuỗi LỖI, rồi câu trả lời tử tế.
Điểm cần nhấn: người dùng không thấy traceback, chỉ thấy một lời xin lỗi có lý do.""",
)
d.table(
    s,
    ["Lần", "Chuyện gì", "Đưa cho model"],
    [
        ["1", "tool không trả lời sau 1s", "LỖI: timeout"],
        ["2", "vẫn treo, backoff tăng", "LỖI: timeout"],
        ["3", "hết lượt, dừng retry", "LỖI: timeout"],
        ["Sau đó", "model tổng hợp", "câu trả lời + lý do"],
    ],
    top=2.0, col_widths=[1.6, 5.4, 4.5], size=16, row_height=0.78,
)
d.text(s, MARGIN, 5.6, CONTENT_W, 0.8,
       "Tool lỗi không phải agent lỗi. Agent lỗi khi harness để lỗi thành exception.",
       18, MUTED)

# --- 15. Section 05 ---------------------------------------------------------
d.section("05", "Tool nguy hiểm", "Least privilege, allowlist, audit.", notes="""Phần này 10 phút, gắn với 03_sql_readonly.py.
Đây là phần có hậu quả thật: xoá nhầm bảng, hoàn nhầm tiền.
Nói thẳng: prompt không phải hàng rào bảo mật.""")

# --- 16. Bốn nguyên tắc -----------------------------------------------------
s = d.content(
    "Nguyên tắc",
    "Bốn lớp cho tool đổi trạng thái",
    notes="""Bảng này lặp lại có chủ ý ở buổi 8 (security), nên chỉ cần giới thiệu.
Least privilege: tool chỉ có quyền tối thiểu, không phải quyền của bạn.
Allowlist: liệt kê việc được làm — dễ kiểm hơn danh sách việc bị cấm.""",
)
d.table(
    s,
    ["Lớp", "Cách làm", "Ví dụ"],
    [
        ["Least privilege", "quyền tối thiểu", "user DB chỉ SELECT"],
        ["Allowlist", "liệt kê việc được làm", "chỉ 3 bảng được truy vấn"],
        ["Giới hạn", "timeout, trần dòng, trần tiền", "LIMIT 20, hoàn ≤ 2 triệu"],
        ["Audit", "ghi ai gọi gì, khi nào", "log riêng, không vào prompt"],
    ],
    top=2.0, col_widths=[2.7, 4.9, 4.4], size=16, row_height=0.8,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.7,
       "Bốn lớp này độc lập: một lớp bị lách thì lớp khác vẫn còn.",
       17, MUTED)

# --- 17. SQL layers ---------------------------------------------------------
s = d.content(
    "Demo · 03_sql_readonly.py",
    "SQL tool: năm lớp chặn",
    notes="""Chạy file, chỉ vào hàm run_select trước rồi mới chạy demo.
Năm lớp xếp từ rẻ đến đắt: chuỗi, từ khoá, loại câu, LIMIT, thời gian.
Nhấn: lớp quan trọng nhất không nằm trong Python — đó là quyền của user database.""",
)
d.bullets(s, [
    "Chặn dấu ';' — không có multi-statement",
    "Chặn INSERT / UPDATE / DELETE / DROP / ALTER",
    "Chỉ cho câu bắt đầu bằng SELECT hoặc WITH",
    "Thiếu LIMIT → bọc truy vấn, thêm LIMIT 20",
    "Quá 0,5 giây → ngắt bằng progress handler",
], top=2.05, size=19, gap=15)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8,
       "Nhưng lớp thật sự: cấp cho tool một user database chỉ có quyền SELECT.",
       18, NAVY, bold=True)

# --- 18. Demo 03 results ----------------------------------------------------
s = d.content(
    "Demo · 03_sql_readonly.py",
    "Bốn câu, ba bị chặn",
    notes="""Chạy từng câu, để lớp đoán trước kết quả.
Câu 1 hợp lệ nhưng thiếu LIMIT — chỉ ra dòng 'đã thêm LIMIT 20'.
Ba câu sau bị chặn ở ba lớp khác nhau. Cuối file kiểm tra bảng còn 6 dòng.""",
)
d.table(
    s,
    ["Câu", "Kết quả"],
    [
        ["SELECT ... ORDER BY amount DESC", "chạy, tự thêm LIMIT 20"],
        ["SELECT ...; DROP TABLE orders", "chặn vì có dấu ';'"],
        ["DELETE FROM orders", "chặn vì từ khoá DELETE"],
        ["DROP TABLE orders", "chặn vì từ khoá DROP"],
    ],
    top=2.0, col_widths=[7.4, 4.1], size=16, row_height=0.8,
)
d.text(s, MARGIN, 5.6, CONTENT_W, 0.8,
       "Kiểm tra bằng dữ liệu: bảng còn đủ 6 dòng. Đừng tin thông báo \"đã chặn\".",
       17, MUTED)

# --- 19. Section 06 ---------------------------------------------------------
d.section("06", "Sandbox", "Chạy code lạ mà không mất máy.", notes="""Phần này 8 phút, gắn với 04_sandbox.py.
Đây là phần dễ gây cảm giác an toàn giả — phải nói rõ giới hạn.
Sandbox trong bài là giảm thiệt hại, không phải cách ly tuyệt đối.""")

# --- 20. Sandbox ------------------------------------------------------------
s = d.content(
    "Demo · 04_sandbox.py",
    "Bốn lớp, bốn kết quả",
    notes="""Chạy từng kịch bản. Kịch bản 3 bị chặn trước khi chạy; kịch bản 4 bị chặn ở runtime.
Chỉ vào chỗ dùng __import__('socket') để lách kiểm tra tĩnh — và prelude vẫn bắt được.
Đây là ví dụ về defense in depth, không phải về một lớp hoàn hảo.""",
)
d.table(
    s,
    ["Lớp", "Cách làm", "Bắt được gì"],
    [
        ["Kiểm tra tĩnh", "AST: đường dẫn, import", "code ngây thơ, lỗi sớm"],
        ["Cách ly", "subprocess, python -I -S", "env, PYTHONPATH"],
        ["Tài nguyên", "RLIMIT_CPU/FSIZE, timeout", "treo, file quá lớn"],
        ["Mạng", "thay socket bằng hàm lỗi", "gọi ra ngoài"],
    ],
    top=2.0, col_widths=[2.5, 5.0, 4.4], size=16, row_height=0.78,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8,
       "Demo: in 285 · vòng lặp vô hạn bị kill sau 2s · /etc/hosts bị chặn · mở mạng bị chặn.",
       16, MUTED)

# --- 21. Statement sandbox --------------------------------------------------
d.statement(
    "Giới hạn",
    "Sandbox không làm code lạ\nan toàn.",
    "Nó chỉ làm thiệt hại nhỏ hơn. Cách ly thật cần container,\nseccomp, user riêng, hoặc dịch vụ sandbox chuyên dụng.",
    notes="""Câu này phải nói rõ, đừng để học viên tưởng subprocess là đủ.
Kiểm tra AST có thể bị lách; chặn socket có thể bị lách.
Nếu chạy code của người lạ trong production, hãy dùng hạ tầng cách ly thật.""",
)

# --- 22. Section 07 ---------------------------------------------------------
d.section("07", "MCP", "Một giao thức, nhiều agent dùng chung.", notes="""Phần này 18 phút, phần dài nhất buổi.
MCP giải bài toán tái sử dụng: cùng một tool, nhiều host khác nhau.
Đi từ kiến trúc đến capability, rồi mới tới bảo mật.""")

# --- 23. Kiến trúc ----------------------------------------------------------
s = d.content(
    "Kiến trúc",
    "Host → client → server",
    notes="""Vẽ lên bảng nếu có thể. Host là ứng dụng có LLM; client là đầu nối giữ phiên; server expose tool.
Một host có thể có nhiều client, mỗi client một server.
stdio: server là tiến trình con. HTTP: server mở cổng — khác hẳn về mô hình tin cậy.""",
)
d.panel(s, MARGIN, 2.15, 3.35, 2.35, NAVY)
d.text(s, MARGIN + 0.25, 2.35, 2.85, 0.35, "HOST", 12, "8FA6C4", bold=True)
d.text(s, MARGIN + 0.25, 2.75, 2.85, 1.5, "Ứng dụng có LLM\nClaude Desktop, IDE,\nagent runtime", 16, "FFFFFF", line_spacing=1.3)
d.panel(s, MARGIN + 4.1, 2.15, 3.35, 2.35, ACCENT_SOFT)
d.text(s, MARGIN + 4.35, 2.35, 2.85, 0.35, "CLIENT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 4.35, 2.75, 2.85, 1.5, "Đầu nối trong host\nGiữ một phiên\nvới server", 16, INK, line_spacing=1.3)
d.panel(s, MARGIN + 8.2, 2.15, 3.35, 2.35, PANEL)
d.text(s, MARGIN + 8.45, 2.35, 2.85, 0.35, "SERVER", 12, ACCENT, bold=True)
d.text(s, MARGIN + 8.45, 2.75, 2.85, 1.5, "Nơi expose\ntool, resource,\nprompt", 16, INK, line_spacing=1.3)
d.text(s, MARGIN + 3.55, 2.95, 0.4, 0.7, "→", 26, ACCENT, bold=True)
d.text(s, MARGIN + 7.65, 2.95, 0.4, 0.7, "→", 26, ACCENT, bold=True)
d.text(s, MARGIN, 5.0, CONTENT_W, 1.0,
       "stdio: không có cổng mạng, quyền nằm ở tiến trình khởi chạy.\nHTTP: mở cổng ra ngoài, bắt buộc xác thực.",
       17, MUTED, line_spacing=1.4)

# --- 24. Ba primitive -------------------------------------------------------
s = d.content(
    "Capability",
    "Ba loại, ba người quyết định",
    notes="""Đây là chỗ hay nhầm: tool không phải resource.
Tool là hành động do model quyết định; resource là dữ liệu do ứng dụng/người dùng chọn.
Ví dụ: chính sách đổi trả nên là resource, không nên nhồi vào mô tả tool.""",
)
d.table(
    s,
    ["Loại", "Ai quyết định", "Ví dụ"],
    [
        ["Tools", "Model", "get_order_status, quote_refund"],
        ["Resources", "Ứng dụng / người dùng", "policy://shop/returns"],
        ["Prompts", "Người dùng chọn", "mẫu mail xin lỗi"],
        ["Discovery", "Client hỏi server", "initialize → list_tools"],
    ],
    top=2.0, col_widths=[2.4, 4.6, 4.9], size=16, row_height=0.8,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8,
       "Client không import code server. Nó chỉ biết tên, schema, URI — nên đổi server mà không sửa client.",
       16, MUTED)

# --- 25. MCP security -------------------------------------------------------
s = d.content(
    "Bảo mật MCP",
    "Xác thực, phân quyền, audit",
    notes="""Với stdio, auth ít quan trọng hơn vì server là tiến trình con. Với HTTP thì bắt buộc.
Bearer token chỉ trả lời 'ai đang gọi'; nó không trả lời 'được gọi tool nào'.
Phân quyền phải theo tool, và audit phải ghi ra stderr — stdout là kênh giao thức.""",
)
d.table(
    s,
    ["Việc", "Cách làm", "Ghi chú"],
    [
        ["Xác thực", "Authorization: Bearer <token>", "khi chạy HTTP"],
        ["Phân quyền", "scope theo từng tool", "viewer ≠ support"],
        ["Audit", "log mỗi lần gọi", "stderr, không phải stdout"],
        ["Transport", "stdio khi cùng máy", "quyền ở tiến trình"],
    ],
    top=2.0, col_widths=[2.4, 5.3, 4.2], size=16, row_height=0.78,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 1.15,
       "Token hợp lệ không có nghĩa là được gọi mọi tool.\nVà token của khách A không được chạm dữ liệu của khách B.",
       17, NAVY, bold=True, line_spacing=1.35)

# --- 26. Demo 05/06 ---------------------------------------------------------
s = d.content(
    "Demo · 05_mcp_server.py + 06_mcp_client.py",
    "Client không import code server",
    notes="""Nếu máy đã cài mcp: chạy client, cho lớp xem 4 phần in ra.
Nếu chưa: chạy 05 không --serve để xem danh sách capability, và đọc code client.
Nhấn: toàn bộ hiểu biết của client về server nằm trong list_tools và URI resource.""",
)
d.code(
    s,
    '''async with stdio_client(params) as (r, w):
    async with ClientSession(r, w) as s:
        await s.initialize()
        tools = await s.list_tools()
        result = await s.call_tool(
            "get_order_status", {"order_id": "1234"})
        policy = await s.read_resource(
            "policy://shop/returns")''',
    top=1.98, height=2.55, size=14,
)
d.bullets(s, [
    "list_tools: tên + schema + mô tả — capability discovery",
    "call_tool: chạy một tool, nhận content dạng text",
    "read_resource: đọc dữ liệu chỉ đọc, không phải hành động",
], top=4.8, size=16, gap=10)

# --- 27. Lab ----------------------------------------------------------------
s = d.content(
    "Lab",
    "60 phút: đọc và viết",
    notes="""Phần A 25 phút: chạy 6 file, mỗi file trả lời một câu trong bảng.
Phần B 35 phút: viết tool của chính họ theo checklist, có 3 test.
Đi vòng hỏi từng nhóm: nếu bỏ lớp chặn ';' thì chuyện gì xảy ra?""",
)
d.table(
    s,
    ["File", "Câu hỏi phải trả lời được"],
    [
        ["01_tool_contract.py", "Model thấy gì, không thấy gì?"],
        ["02_tool_errors.py", "Vì sao retry không nằm trong model?"],
        ["03_sql_readonly.py", "Lớp nào chặn ';'? Bỏ đi thì sao?"],
        ["04_sandbox.py", "Kịch bản nào chặn tĩnh, nào chặn runtime?"],
        ["05 + 06 MCP", "Client biết gì về server, và không biết gì?"],
    ],
    top=2.0, col_widths=[4.0, 7.5], size=15, row_height=0.68,
)
d.text(s, MARGIN, 6.2, CONTENT_W, 0.6,
       "A · 25 phút đọc 6 file   |   B · 35 phút viết tool: schema → code → timeout → 3 test",
       16, NAVY, bold=True)

# --- 28. Bài tập ------------------------------------------------------------
s = d.content(
    "Về nhà",
    "Sáu bài, hai bài bắt buộc",
    notes="""Bài 1 và bài 5 là bắt buộc. Bài 1 củng cố contract; bài 5 là bài duy nhất chạm MCP end-to-end.
Bài 6 dành cho ai muốn đi sâu bảo mật — cũng là bản nháp của buổi 8.
Nhắc nộp kèm phần trả lời câu hỏi, không chỉ code.""",
)
d.bullets(s, [
    "Bài 1 (bắt buộc) — viết lại một tool tệ, thêm tool thứ hai cùng họ",
    "Bài 5 (bắt buộc) — đóng gói MCP server + client đọc resource",
    "Bài 2–4 — phân loại lỗi, SQL allowlist, sandbox có ngân sách",
    "Bài 6 — phân quyền theo role và audit log cho MCP",
], top=2.15, size=20, gap=20)
d.text(s, MARGIN, 4.95, CONTENT_W, 1.2,
       "Nộp: file chạy được + câu trả lời cho các câu hỏi trong exercises.md.\nTiêu chí: giải thích được vì sao, không chỉ chạy được.",
       17, MUTED, line_spacing=1.5)

# --- 29. Tổng kết -----------------------------------------------------------
s = d.content(
    "Tổng kết",
    "Năm câu mang về",
    notes="""Đọc chậm, dừng ở câu 4 và 5.
Câu 4 là câu sẽ quay lại ở buổi 8: quyền nằm ở tầng dữ liệu, không ở prompt.
Câu 5 là lý do MCP tồn tại: tách tool khỏi agent để dùng lại.""",
)
d.bullets(s, [
    "Model chỉ thấy hợp đồng: tên, mô tả, schema.",
    "Một tool một việc; tham số tối thiểu; trả chuỗi dễ đọc.",
    "Timeout và retry phải có trần; retry mù là làm hai lần.",
    "Quyền nằm ở tầng dữ liệu: SELECT-only, allowlist, audit.",
    "MCP tách tool khỏi agent; bảo mật phải đặt ở server.",
], top=2.0, size=18, gap=14)

# --- 30. Buổi sau -----------------------------------------------------------
s = d.content(
    "Buổi 4",
    "Tiếp theo: Context, Skills và Memory",
    notes="""Nhắc nộp bài 1 và 5. Buổi 4 nói về thứ được đưa vào cửa sổ context.
Mang theo tool đã viết ở lab, kèm 3 test — buổi 4 sẽ dùng lại.
Mời lớp đặt câu hỏi, đặc biệt về MCP nếu đã chạy được client.""",
)
d.bullets(s, [
    "Context window: cái gì vào, cái gì để ngoài",
    "Skills: đóng gói quy trình, không chỉ đóng gói hàm",
    "Memory ngắn hạn và dài hạn",
    "Vì sao mô tả tool tốt vẫn có thể bị chôn trong quá nhiều context",
], top=2.05, size=20, gap=18)
d.text(s, MARGIN, 4.9, CONTENT_W, 1.1,
       "Chuẩn bị: đọc lại 06_mcp_client.py — client không hề biết code server.\nBuổi 4 áp dụng cùng ý tưởng cho context: biết ít mà đúng còn hơn biết nhiều mà loạn.",
       17, MUTED, line_spacing=1.5)

d.save()
