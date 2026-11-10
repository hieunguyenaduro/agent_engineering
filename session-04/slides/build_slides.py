"""Tạo slide Buổi 4.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from pptx.enum.text import PP_ALIGN  # noqa: E402
from pptx.util import Inches  # noqa: E402
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, CONTENT_W, INK, MARGIN, MUTED, NAVY, PANEL,
    Deck,
)

d = Deck(session="Agent Engineering · Buổi 4", out=Path(__file__).with_name("slides.pptx"))


def section(number, title, subtitle="", notes=""):
    """Giữ style của deck, chỉ nới hộp số để không bị báo tràn 23pt."""
    slide = d.section(number, title, subtitle, notes)
    number_box = slide.shapes[0]
    number_box.top = Inches(1.32)
    number_box.height = Inches(2.0)
    return slide

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 4/10",
    "Context Engineering\nvới Prompt, Skill và Memory",
    "Chọn cái gì đặt lên bàn",
    "120 phút · 55 phút lý thuyết & demo · 60 phút lab · 5 phút tổng kết",
    notes="""Buổi trước agent có thêm tool. Hôm nay giải quyết hệ quả: mọi thứ đều chiếm chỗ.
Đừng nói 'prompt dài quá thì cắt'. Câu hỏi đúng là: cắt cái gì trước, và cất phần còn lại ở đâu.
Ba từ khoá: context, skill, memory. Cuối buổi mỗi bạn phải đo được context của agent mình.""",
)

# --- 2. Vấn đề --------------------------------------------------------------
s = d.content(
    "Vấn đề",
    "Agent càng giỏi, bàn càng chật",
    notes="""Kể một tình huống thật: thêm tool tra đơn, thêm tài liệu chính sách, thêm lịch sử chat.
Mỗi thứ đều hữu ích, nhưng cộng lại thì vượt cửa sổ hoặc làm model bỏ sót chỉ dẫn cũ.
Hỏi lớp: lần gần nhất model 'quên' chỉ dẫn là khi nào? Thường là do context chứ không phải model dở.""",
)
d.bullets(s, [
    "Tool schema: 5 tool đã chiếm 177/700 token",
    "Kết quả tool: 6 lần gọi chiếm 260/700",
    "Lịch sử: 12 message chiếm 240/700",
    "Tài liệu retrieve: 3 đoạn chiếm 234/700",
], top=2.25, height=3.2, size=22, gap=22)
d.text(s, MARGIN, 5.75, CONTENT_W, 0.8,
       "Số liệu từ 01_context_budget.py — cửa sổ thu nhỏ 700 token để nhìn thấy tỉ lệ.", 16, MUTED)

# --- 3. Section 01 ----------------------------------------------------------
section("01", "Context window là gì?", "Mặt bàn, không phải cái tủ.", notes="""Phần này 12 phút, gồm cả cái gì chiếm chỗ.
Định nghĩa ngắn: số token tối đa model nhận trong một lần gọi. Không phải bộ nhớ.
Nếu lớp đã quen 'context dài thì tốt', đây là chỗ sửa lại.""") 

# --- 4. Statement -----------------------------------------------------------
d.statement(
    "Cách nghĩ",
    "Context không phải bộ nhớ.\nNó là mặt bàn.",
    "Bạn chỉ đặt được thứ vừa bàn.\nMuốn giữ thứ khác, phải cất vào tủ — và nhớ đường đến tủ.",
    notes="""Đây là câu sẽ quay lại suốt buổi. Bộ nhớ là thứ tồn tại ngoài lần gọi; context là thứ được gửi đi.
Mặt bàn có giới hạn cứng, không thương lượng. Cất vào tủ là filesystem, sqlite, skill.
Hỏi: nếu bàn đầy, bạn bỏ tờ giấy nào trước?""",
)

# --- 5. Bảng chiếm chỗ ------------------------------------------------------
s = d.content(
    "Đo lường",
    "Cái gì chiếm chỗ?",
    notes="""Đọc từng dòng, dừng ở 'kết quả tool' vì ít người nghĩ tới.
Tool schema là chi phí thường trực: mỗi request đều trả, kể cả khi không gọi tool.
Cột % cộng lại hơn 100 vì tổng đang vượt cửa sổ — đó chính là vấn đề.""",
)
d.table(
    s,
    ["Thành phần", "Token", "% cửa sổ"],
    [
        ["System + developer", "182", "26%"],
        ["Tool schema (5 tool)", "177", "25%"],
        ["Lịch sử (12 message)", "240", "34%"],
        ["Kết quả tool (6 lần)", "260", "37%"],
        ["Tài liệu retrieve (3 đoạn)", "234", "33%"],
    ],
    top=2.12, col_widths=[5.6, 2.2, 2.8], size=18, row_height=0.6,
)
d.text(s, MARGIN, 5.85, CONTENT_W, 0.7,
       "Tổng 1.093 token cho cửa sổ 700 — vượt 393 token (56%).", 18, NAVY, bold=True)

# --- 6. Ước lượng -----------------------------------------------------------
s = d.content(
    "Công cụ",
    "Đo trước khi cắt",
    notes="""Chỉ vào hàm: chars/4 là sàn, không phải hoá đơn. Tiếng Việt thường tốn hơn.
Điều cần nhớ không phải công thức mà là thói quen: đo theo từng thành phần.
Nếu chỉ đo tổng, bạn không biết cắt vào đâu.""",
)
d.code(
    s,
    '''from math import ceil

def estimate_tokens(text: str) -> int:
    """4 ký tự ≈ 1 token; đây là sàn, không phải hoá đơn."""
    return max(1, ceil(len(text) / 4))''',
    top=2.05, height=2.0, size=16,
)
d.bullets(s, [
    "Tiếng Việt tốn token hơn tiếng Anh cùng độ dài — đừng dùng con số này để tính tiền.",
    "Đo theo từng thành phần: system, schema, lịch sử, tool, tài liệu.",
], top=4.35, height=1.8, size=18, gap=12)

# --- 7. Section 02 ----------------------------------------------------------
section("02", "Ngân sách context", "Cắt theo thứ tự, không cắt theo cảm giác.", notes="""Phần này 10 phút, là trái tim của buổi.
Nhấn: thứ tự cắt quan trọng vì mỗi bước có giá khác nhau. Cắt tool trước là rẻ nhất.""") 

# --- 8. Thứ tự cắt ----------------------------------------------------------
s = d.content(
    "Chiến lược",
    "Bốn bước, theo đúng thứ tự",
    notes="""Bước 1 rẻ nhất: kết quả tool cũ dài, đã có kết luận, ít khi đọc lại nguyên văn.
Bước 2 đắt hơn vì phải gọi model hoặc chạy hàm tóm tắt. Vì vậy đừng làm trước bước 1.
Bước 4 là lưới an toàn, không phải chiến lược chính. System không bao giờ nằm trong danh sách cắt.""",
)
d.table(
    s,
    ["Thứ tự", "Cắt gì", "Vì sao"],
    [
        ["1", "Kết quả tool cũ", "Dài, đã có kết luận, ít đọc lại nguyên văn"],
        ["2", "Lượt chat cũ", "Nén thành summary + facts, giữ N message gần"],
        ["3", "Tài liệu retrieve", "Chỉ giữ đoạn thật sự được trích dẫn"],
        ["4", "Tài liệu / lượt cuối", "Lưới an toàn; không bao giờ chạm system"],
    ],
    top=2.1, col_widths=[1.1, 4.0, 6.4], size=16, row_height=0.72,
)
d.text(s, MARGIN, 6.0, CONTENT_W, 0.6,
       "Cắt tool trước vì đó là bước rẻ nhất — chưa cần gọi model.", 16, MUTED)

# --- 9. Kết quả -------------------------------------------------------------
s = d.content(
    "Demo · 01_context_budget.py",
    "1.093 → 644 token",
    notes="""Chạy file live nếu có thể. Chỉ vào ba dòng của bảng diễn biến.
Hỏi: nếu đảo bước 1 và bước 2 thì mất gì? Trả lời: trả tiền tóm tắt những thứ sắp bị cắt.
Nhấn: system và message gần nhất vẫn nguyên — đó là điều kiện của mọi chiến lược cắt.""",
)
d.table(
    s,
    ["Bước", "Giải phóng", "Còn lại"],
    [
        ["1. Cắt kết quả tool cũ", "96 token", "997"],
        ["2. Tóm tắt lượt cũ", "219 token", "778"],
        ["3. Tỉa tài liệu retrieve", "134 token", "644"],
    ],
    top=2.1, col_widths=[5.6, 3.0, 2.6], size=18, row_height=0.78,
)
d.text(s, MARGIN, 5.4, CONTENT_W, 1.0,
       "Còn 56 token trống. System prompt và 6 message gần nhất vẫn nguyên vẹn.", 19, NAVY, bold=True)

# --- 10. Nguyên tắc ---------------------------------------------------------
s = d.content(
    "Ghi nhớ",
    "Ba nguyên tắc không thương lượng",
    notes="""Ba dòng này thay cho cả một chương sách.
Nguyên tắc 3 hay bị bỏ: cứ cắt mãi mà không hỏi vì sao vẫn vượt. Đó là tín hiệu tác vụ sai, không phải hàm cắt sai.
Nếu còn thời gian, hỏi lớp: system prompt của bạn có thể gọn đi bao nhiêu mà không mất luật nào?""",
)
d.bullets(s, [
    "System prompt không bao giờ bị cắt — đó là hợp đồng với model.",
    "Cắt theo giá trị, không theo tuổi: kết quả tool cũ có thể quý hơn lượt chat mới.",
    "Cắt xong vẫn vượt = tác vụ quá lớn, không phải lỗi của hàm cắt.",
], top=2.25, height=3.0, size=22, gap=26)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8,
       "Thử đổi KEEP_RECENT_TOOL_RESULTS từ 2 lên 6: bước 1 gần như không còn tác dụng.", 16, MUTED)

# --- 11. Section 03 ---------------------------------------------------------
section("03", "Prompt có tầng", "Ai được ghi đè ai — và ai thực thi.", notes="""Phần này 10 phút. Đây là chỗ phân biệt 'prompt hay' với 'prompt có cấu trúc'.
Bốn tầng không phải bốn màu cho đẹp; chúng là thứ tự ưu tiên khi xung đột.""",
) 

# --- 12. Bốn tầng -----------------------------------------------------------
s = d.content(
    "Cấu trúc",
    "Bốn tầng, quyền giảm dần",
    notes="""Đi từ trái sang phải: system do bạn viết, developer do sản phẩm viết, user do người dùng viết, untrusted do thế giới viết.
Tầng thấp không có nghĩa là vô dụng: nó cung cấp dữ liệu. Nó chỉ không có quyền ra lệnh.
Hỏi lớp: email khách hàng nằm ở tầng nào? Chắc chắn là untrusted.""",
)
labels = [
    ("SYSTEM", "Vai trò, giới hạn", "Luôn tiếng Việt\nKhông lộ mã nội bộ", NAVY, "FFFFFF"),
    ("DEVELOPER", "Quy tắc nghiệp vụ", "Hoàn tiền > 500k\nphải xin duyệt", ACCENT_SOFT, NAVY),
    ("USER", "Yêu cầu", "Đơn 1234 bị rè,\ncho mình hoàn tiền", PANEL, INK),
    ("UNTRUSTED", "Dữ liệu", "Web, tài liệu, email\ncó thể chứa chỉ thị", PANEL, MUTED),
]
for i, (label, title, example, color, text_color) in enumerate(labels):
    x = MARGIN + i * 2.95
    d.panel(s, x, 2.15, 2.7, 2.55, color)
    d.text(s, x + 0.22, 2.38, 2.25, 0.35, label, 11, ACCENT if color != NAVY else "8FA6C4", bold=True)
    d.text(s, x + 0.22, 2.78, 2.25, 0.6, title, 16, text_color, bold=True)
    d.text(s, x + 0.22, 3.45, 2.25, 1.0, example, 13, text_color, line_spacing=1.3)
d.text(s, MARGIN, 5.0, 8.0, 0.7, "← quyền cao hơn", 15, ACCENT, bold=True)
d.text(s, MARGIN + 8.6, 5.0, 3.0, 0.7, "quyền thấp hơn →", 15, MUTED, align=PP_ALIGN.RIGHT)

# --- 13. build_prompt -------------------------------------------------------
s = d.content(
    "Demo · 02_prompt_layers.py",
    "Một hàm, bốn nhãn",
    notes="""Code ngắn nhưng có chủ ý: mỗi message mang theo layer, không chỉ role.
Nhờ nhãn này mà bộ giải quyết xung đột biết tầng nào thắng, kể cả khi thứ tự gửi thay đổi.
Tài liệu luôn bị bọc trong thẻ có id và source — để truy vết, không phải để bảo mật.""",
)
d.code(
    s,
    '''def build_prompt(system, developer, user, docs):
    messages = [
        {"role": "system", "layer": "system", "content": system},
        {"role": "developer", "layer": "developer", "content": developer},
        {"role": "user", "layer": "user", "content": user},
    ]
    for doc in docs:
        messages.append({"role": "user", "layer": "untrusted",
                         "content": wrap_untrusted(doc)})
    return messages''',
    top=2.0, height=3.25, size=14,
)
d.text(s, MARGIN, 5.5, CONTENT_W, 0.8,
       "Thứ tự gửi đi cũng là thứ tự ưu tiên. Tài liệu ngoài luôn bị bọc và ghi nguồn.", 17, MUTED)

# --- 14. Injection ----------------------------------------------------------
s = d.content(
    "Giới hạn",
    "Prompt có tầng vẫn bị injection",
    notes="""Đây là slide quan trọng nhất phần prompt. Đừng để lớp ra về với niềm tin 'có tầng là an toàn'.
Kịch bản: tài liệu web chứa dòng SYSTEM giả, dụ model in canary.
Cả prompt phẳng và prompt có tầng đều lộ. Chỉ guard đầu ra mới chặn. Hỏi: guard nên kiểm tra gì ngoài canary?""",
)
d.table(
    s,
    ["Thử nghiệm", "Kết quả", "Kết luận"],
    [
        ["Prompt phẳng", "Lộ ORCHID-7", "Mọi thứ ngang hàng"],
        ["Prompt có tầng", "Vẫn lộ ORCHID-7", "Tầng không phải bảo mật"],
        ["Guard đầu ra", "BLOCKED", "Chặn mới là thực thi"],
    ],
    top=2.1, col_widths=[3.4, 3.6, 4.5], size=17, row_height=0.65,
)
d.code(
    s,
    '''answer = fake_model(render(layered))
if CANARY in answer:
    answer = "[BLOCKED] Câu trả lời chứa canary."''',
    top=4.85, height=1.15, size=14,
)

# --- 15. Statement ----------------------------------------------------------
d.statement(
    "Ranh giới",
    "Tầng phân xử.\nGuard thực thi.",
    "Prompt nói ai nên thắng. Code quyết định điều gì thật sự ra ngoài.",
    notes="""Đọc chậm hai câu. Đây là câu chuyển từ 'prompt engineering' sang 'system engineering'.
Nếu chỉ nhớ một điều về prompt trong buổi này, nhớ điều này.
Ví dụ cụ thể: canary, kiểm tra quyền tool, validate output trước khi gửi khách.""",
)

# --- 16. Section 04 ---------------------------------------------------------
section("04", "Skill", "Dạy cách mở đúng cuốn sổ, không dạy thuộc lòng.", notes="""Phần này 8 phút. Skill là cách đóng gói quy trình để nạp muộn.
Đừng bán skill như một tính năng; nó chỉ là file markdown + một quy ước frontmatter.""") 

# --- 17. Skill là gì --------------------------------------------------------
s = d.content(
    "Định nghĩa",
    "Skill là một file markdown",
    notes="""Frontmatter là phần model thấy trước; thân bài là phần nạp sau.
when_to_use phải là ngôn ngữ người dùng, không phải tên team nội bộ.
Hỏi: skill khác tool ở đâu? Tool là hành động; skill là hướng dẫn cách làm một việc.""",
)
d.bullets(s, [
    "Một file skills/<tên>/SKILL.md — không phải code, không cần deploy.",
    "Frontmatter: name, description, when_to_use.",
    "Thân bài: quy trình, mẫu câu, sai sót thường gặp.",
    "Model chỉ thấy metadata cho tới khi câu hỏi khớp.",
], top=2.2, height=3.2, size=21, gap=20)
d.text(s, MARGIN, 5.6, CONTENT_W, 0.7,
       "Skill không cấp thêm quyền. Nó chỉ dạy cách dùng quyền đã có.", 17, MUTED)

# --- 18. Progressive disclosure ---------------------------------------------
s = d.content(
    "Demo · 03_skill_loader.py",
    "Metadata trước, thân bài sau",
    notes="""Đọc bảng: metadata 2 skill là 85 token; nhồi toàn văn là 663 token mỗi request.
Ba request thực tế chỉ tốn 833 token thay vì 1.989 — tiết kiệm 58%.
Câu hỏi 'đổi mật khẩu' không khớp skill nào, nên chỉ trả 85 token. Đó là hành vi đúng.
Hỏi lớp: nếu có 50 skill thì metadata bao nhiêu? Bắt đầu phải tìm kiếm metadata rồi.""",
)
d.table(
    s,
    ["Cách nạp", "Mỗi request", "3 request"],
    [
        ["Metadata 2 skill", "85 token", "255"],
        ["Toàn văn 2 skill", "663 token", "1.989"],
        ["Progressive (thực tế)", "85 + 1 thân bài", "833"],
    ],
    top=2.08, col_widths=[5.4, 3.4, 2.6], size=18, row_height=0.68,
)
d.text(s, MARGIN, 4.95, CONTENT_W, 0.7, "Tiết kiệm 1.156 token — 58%.", 28, ACCENT, bold=True)
d.text(s, MARGIN, 5.78, CONTENT_W, 0.7,
       "Câu hỏi không khớp skill nào chỉ tốn metadata. Không khớp thì đừng nạp.", 16, MUTED)

# --- 19. SKILL.md -----------------------------------------------------------
s = d.content(
    "Định dạng",
    "Frontmatter là bề mặt tìm kiếm",
    notes="""Chỉ vào when_to_use: đây là thứ loader dùng để khớp, nên viết bằng từ người dùng sẽ gõ.
description dài quá thì tốn token thường trực; ngắn quá thì không đủ để phân biệt.
Thân bài có thể dài bao nhiêu cũng được vì chỉ nạp khi cần — nhưng vẫn nên gọn.""",
)
d.code(
    s,
    '''---
name: refund
description: Xử lý yêu cầu hoàn tiền hoặc đổi trả cho đơn hàng.
when_to_use: hoàn tiền, trả lại tiền, đổi trả, refund, bị rè
---

# Quy trình hoàn tiền
## 1. Xác minh trước khi hứa
## 2. Phân loại: lỗi NSX / đổi ý / rơi vỡ''',
    top=2.0, height=3.1, size=14,
)
d.text(s, MARGIN, 5.35, CONTENT_W, 0.8,
       "Loader dừng ở dòng --- thứ hai. Thân bài chỉ được đọc khi when_to_use khớp.", 17, MUTED)

# --- 20. Vì sao skill -------------------------------------------------------
s = d.content(
    "So sánh",
    "Vì sao không nhồi vào system prompt?",
    notes="""Ba dòng này trả lời câu hỏi hay gặp: 'skill khác gì một đoạn system prompt dài?'.
Khác ở chỗ nó có điều kiện nạp và có bề mặt tìm kiếm.
Nếu system prompt của bạn đang dài vì chứa quy trình, đó là dấu hiệu nên tách thành skill.""",
)
d.table(
    s,
    ["Vấn đề", "System prompt", "Skill"],
    [
        ["Chi phí", "Trả mọi request", "Chỉ trả khi khớp"],
        ["Sửa đổi", "Deploy code", "Sửa file markdown"],
        ["Tìm kiếm", "Một khối lớn, không nhãn", "when_to_use là bề mặt"],
    ],
    top=2.15, col_widths=[3.0, 4.4, 5.0], size=18, row_height=0.82,
)
d.text(s, MARGIN, 5.6, CONTENT_W, 0.7,
       "System prompt nên nói vai trò và giới hạn. Quy trình dài thuộc về skill.", 17, MUTED)

# --- 21. Section 05 ---------------------------------------------------------
section("05", "Memory", "Nhớ có nguồn, có hạn, có chủ.", notes="""Phần này 11 phút, gồm memory ngắn hạn, dài hạn và filesystem.
Điểm cần nhấn: memory không phải một dict không đáy. Nó là dữ liệu có cấu trúc và có trách nhiệm.""") 

# --- 22. Ngắn hạn -----------------------------------------------------------
s = d.content(
    "Demo · 04_short_memory.py",
    "Memory ngắn hạn: nén phần cũ",
    notes="""Luồng: vượt ngưỡng → giữ N message gần nhất → trích facts → summary.
Con số 202 → 113 token là ví dụ, không phải chuẩn. Điều quan trọng là facts sống sót.
Hỏi: chi tiết 'màu trắng' có trong facts không? Nếu không, nó sẽ mất — và ai chịu trách nhiệm?""",
)
d.bullets(s, [
    "Vượt ngưỡng → giữ nguyên N message gần nhất.",
    "Phần cũ → trích facts có khoá + một summary ngắn.",
    "Fact sống ngoài summary: tên, mã đơn, ngân sách, ngôn ngữ.",
    "Chi tiết không nằm trong facts sẽ mất khi nén.",
], top=2.2, height=2.8, size=20, gap=18)
d.text(s, MARGIN, 5.05, CONTENT_W, 0.65, "202 → 113 token sau 2 lần nén; 6 facts được giữ.", 22, NAVY, bold=True)
d.text(s, MARGIN, 5.75, CONTENT_W, 0.7,
       "Tóm tắt để tiết kiệm chỗ, không phải để quên lời hứa.", 16, MUTED)

# --- 23. Dài hạn ------------------------------------------------------------
s = d.content(
    "Demo · 05_long_memory.py",
    "Memory dài hạn: một bảng có cột",
    notes="""sqlite đủ cho phần lớn agent cá nhân; không cần vector DB cho facts có khoá.
Ba cột không được bỏ: source, expires_at, user_id. Thiếu source thì fact thành tin đồn.
Thiếu expires_at thì memory cũ dần mà không ai biết. Thiếu user_id thì đó là lỗ hổng.
Demo cho thấy fact hết hạn vẫn nằm trong DB để audit, nhưng recall không trả về.""",
)
d.code(
    s,
    '''CREATE TABLE facts (
    id         INTEGER PRIMARY KEY,
    user_id    TEXT NOT NULL,
    key        TEXT NOT NULL,
    value      TEXT NOT NULL,
    source     TEXT NOT NULL,     -- fact đến từ đâu?
    created_at TEXT NOT NULL,
    expires_at TEXT,              -- bao lâu phải kiểm tra lại?
    UNIQUE (user_id, key)
)''',
    top=2.0, height=3.15, size=14,
)
d.text(s, MARGIN, 5.35, CONTENT_W, 0.8,
       "Nguồn, hạn, chủ: ba cột biến memory từ 'nhớ bừa' thành dữ liệu kiểm tra được.", 17, MUTED)

# --- 24. Filesystem ---------------------------------------------------------
s = d.content(
    "Workspace",
    "Filesystem cũng là memory",
    notes="""Đây là dạng memory bị đánh giá thấp nhất. File trên đĩa bền hơn RAM, dễ kiểm tra hơn vector DB.
Agent không cần nhớ nội dung; nó chỉ cần biết đường dẫn và đọc lại khi cần.
Con người mở được, diff được, backup được. Đó là lợi thế vận hành, không chỉ kỹ thuật.""",
)
d.bullets(s, [
    "workspace/<user_id>/ là bộ nhớ bền, sống qua restart.",
    "notes.md cho ghi chú; artifacts/ cho file sinh ra; scratch/ cho nháp.",
    "Model không nhớ nội dung — nó nhớ đường dẫn và đọc lại.",
    "Con người mở, diff, backup, xoá được. Vector DB không cho bạn mấy thứ đó.",
], top=2.2, height=2.8, size=20, gap=18)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.7,
       "Rẻ hơn và dễ kiểm tra hơn nhiều loại dữ liệu bạn đang nghĩ đến vector DB.", 16, MUTED)

# --- 25. Section 06 ---------------------------------------------------------
section("06", "Nhiều người dùng", "Cô lập nằm trong code, không nằm trong lời dặn.", notes="""Phần này 4 phút nhưng là phần dễ gây sự cố nhất.
Nếu chỉ nhớ một câu: user_id phải đi vào đường dẫn và vào câu WHERE, không chỉ vào prompt.""") 

# --- 26. Isolation code -----------------------------------------------------
s = d.content(
    "Demo · 06_isolation.py",
    "Chặn trước khi mở file",
    notes="""resolve() xử lý '..' và symlink, rồi mới kiểm tra ranh giới. Thứ tự này quan trọng.
Kiểm tra user_id trước khi ghép đường dẫn, nếu không '../user-B' sẽ thành tên file hợp lệ.
Audit log ghi lại lần bị chặn — không có log thì không biết mình đang bị dò.
Hỏi: nếu chỉ kiểm tra chuỗi '../' mà không resolve, symlink có lọt không?""",
)
d.code(
    s,
    '''def _resolve(self, relative):
    target = (self.root / relative).resolve()
    if not target.is_relative_to(self.root):
        audit(self.user_id, f"read:{relative}", "BLOCKED")
        raise PermissionError("ngoài workspace")
    return target''',
    top=2.0, height=2.55, size=14,
)
d.bullets(s, [
    "Namespace theo user_id: workspaces/user-A, memory/user-A.json.",
    "Validate user_id trước khi ghép đường dẫn: chữ, số, _, -.",
    "resolve() xử lý '..' và symlink; so sánh sau khi resolve.",
], top=4.75, height=1.6, size=17, gap=10)

# --- 27. Redact -------------------------------------------------------------
s = d.content(
    "Ranh giới",
    "Redact không phải cô lập",
    notes="""Ba lớp này độc lập. Thiếu lớp nào cũng đủ để lộ dữ liệu.
Redact chỉ giảm thiểu rò rỉ khi hiển thị; nó không ngăn user-A đọc file user-B.
Ngược lại, cô lập hoàn hảo vẫn nên redact để log và UI không chứa PII.
Hỏi: nếu phải bỏ một lớp, bỏ lớp nào? Không nên bỏ lớp nào — nhưng thứ tự ưu tiên là cô lập trước.""",
)
d.table(
    s,
    ["Lớp", "Chặn gì", "Không chặn gì"],
    [
        ["Workspace", "../, absolute, symlink", "Nội dung file hợp lệ"],
        ["UserMemory", "user_id lạ", "Fact bị ghi sai"],
        ["Redact", "PII khi hiển thị", "Truy cập trái phép"],
    ],
    top=2.1, col_widths=[3.0, 4.4, 4.8], size=17, row_height=0.82,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8,
       "Redact là giảm thiểu rò rỉ. Cô lập là kiểm soát truy cập. Đừng thay thế nhau.", 17, NAVY, bold=True)

# --- 28. Lab ----------------------------------------------------------------
s = d.content(
    "Lab · 60 phút",
    "Hai phần",
    notes="""Phần A 25 phút: chạy 6 file, trả lời câu hỏi trong bảng. Đi vòng, hỏi mỗi nhóm một câu khác nhau.
Phần B 35 phút: dựng context pack cho agent của chính họ. Không cần UI, chỉ cần chứng minh bằng log.
Ai xong sớm: thêm skill thứ ba hoặc symlink test.""",
)
d.panel(s, MARGIN, 2.15, 5.3, 3.2, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.7, 0.4, "25 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.3, 2.8, 4.7, 0.6, "Chạy và đọc", 22, NAVY, bold=True)
d.text(s, MARGIN + 0.3, 3.5, 4.7, 1.6,
       "Sáu file, mỗi file một câu hỏi.\nĐo token, thử cắt sai thứ tự,\nthử injection, thử đọc chéo.",
       16, INK, line_spacing=1.4)

d.panel(s, MARGIN + 5.7, 2.15, 5.3, 3.2, ACCENT_SOFT)
d.text(s, MARGIN + 6.0, 2.4, 4.7, 0.4, "35 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 6.0, 2.8, 4.7, 0.6, "Dựng context pack", 22, NAVY, bold=True)
d.text(s, MARGIN + 6.0, 3.5, 4.7, 1.6,
       "build_context(user_id, question),\nđo token, cắt theo thứ tự,\n3 facts sqlite, hai user A/B.",
       16, INK, line_spacing=1.4)
d.text(s, MARGIN, 5.75, CONTENT_W, 0.7,
       "Điều kiện đạt: giải thích được vì sao mỗi lần cắt không làm mất thông tin bắt buộc.", 16, MUTED)

# --- 29. Tổng kết -----------------------------------------------------------
s = d.content(
    "Tổng kết",
    "Năm câu mang về",
    notes="""Đọc chậm. Dừng ở câu 5.
Câu 1 là nền của mọi thứ: context là tài nguyên hữu hạn.
Câu 4 và 5 là hai thứ buổi 5 sẽ dùng tiếp: skill để chọn hướng dẫn, memory để giữ facts.
Mời lớp đặt câu hỏi trước khi chuyển buổi.""",
)
d.bullets(s, [
    "Context là mặt bàn: mọi thứ gửi lên đều chiếm chỗ, kể cả tool schema.",
    "Đo trước khi cắt; cắt kết quả tool cũ trước, system prompt sau cùng.",
    "Prompt có tầng để phân xử, nhưng chỉ guard ở đầu ra mới thực thi.",
    "Skill là progressive disclosure: metadata trước, thân bài khi khớp.",
    "Memory phải có nguồn, có hạn, có chủ; workspace là memory bền nhất.",
], top=2.0, size=19, gap=13)

# --- 30. Buổi sau -----------------------------------------------------------
s = d.content(
    "Buổi 5",
    "Tiếp theo: Retrieval và Vector Database",
    notes="""Nhắc nộp bài 1 và bài 4. Buổi 5 dùng lại đúng bảng chiếm chỗ hôm nay.
Họ sẽ thấy tài liệu retrieve là khoản lớn, và học cách chọn đúng đoạn trước khi đưa vào.
Mời lớp mang theo bộ tài liệu nhỏ của riêng mình.""",
)
d.bullets(s, [
    "Lấy đúng đoạn tài liệu trước khi đưa vào context.",
    "Chunking, embedding, tìm kiếm lai (hybrid), xếp hạng lại.",
    "Đo chất lượng retrieval, không chỉ đo 'có câu trả lời'.",
    "Kết hợp skill metadata và retrieval để chọn đúng hướng dẫn.",
], top=2.15, height=3.1, size=20, gap=16)
d.text(s, MARGIN, 5.5, CONTENT_W, 0.8,
       "Chuẩn bị: đọc lại mục 1 của buổi 4; mang 5–20 file tài liệu của bạn.", 17, MUTED)

d.save()
