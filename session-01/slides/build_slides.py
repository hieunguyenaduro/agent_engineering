"""Tạo slide Buổi 1 (slides.pptx) từ code.

Chạy:  pip install python-pptx
       python slides/build_slides.py

Sửa nội dung ngay trong file này rồi chạy lại. Mỗi slide có speaker notes
để bạn đọc khi giảng.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------------------
# Bảng màu
# ---------------------------------------------------------------------------
NAVY = "0F2137"
NAVY_SOFT = "1D3557"
INK = "1B2A41"
MUTED = "5B6B82"
ACCENT = "2F6FED"
ACCENT_SOFT = "E8F0FE"
BG = "FFFFFF"
PANEL = "F4F6FA"
CODE_BG = "0F172A"
CODE_TEXT = "E2E8F0"
CODE_COMMENT = "94A3B8"
GREEN = "0F766E"
AMBER = "B45309"
WHITE = "FFFFFF"

FONT = "Arial"
MONO = "Consolas"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

W = 13.333
MARGIN = 0.9
CONTENT_W = W - 2 * MARGIN


def _rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def _slide():
    return prs.slides.add_slide(BLANK)


def _bg(slide, color: str):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(color)


def _box(slide, left, top, width, height):
    shape = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    return shape, tf


def _style(run, size, color, bold=False, italic=False, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = _rgb(color)
    run.font.name = font


def text(slide, left, top, width, height, content, size=20, color=INK,
         bold=False, align=PP_ALIGN.LEFT, line_spacing=1.15, space_after=6):
    shape, tf = _box(slide, left, top, width, height)
    lines = content.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        run = p.add_run()
        run.text = line
        _style(run, size, color, bold=bold)
    return shape


def bullets(slide, left, top, width, height, items, size=20, color=INK,
            gap=14, line_spacing=1.2):
    shape, tf = _box(slide, left, top, width, height)
    for i, item in enumerate(items):
        level = 0
        if isinstance(item, tuple):
            item, level = item
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = line_spacing
        prefix = "•  " if level == 0 else "–  "
        run = p.add_run()
        run.text = prefix + item
        _style(run, size if level == 0 else size - 2, color if level == 0 else MUTED)
        if level > 0:
            p.level = 1
    return shape


def panel(slide, left, top, width, height, color=PANEL, line=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(color)
    if line:
        shape.line.color.rgb = _rgb(line)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    shape.adjustments[0] = 0.06
    return shape


def code_box(slide, code, left, top, width, height, size=14):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(CODE_BG)
    shape.line.fill.background()
    shape.shadow.inherit = False
    shape.adjustments[0] = 0.04

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.18)
    tf.margin_bottom = Inches(0.12)

    for i, line in enumerate(code.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.05
        p.space_after = Pt(2)
        run = p.add_run()
        run.text = line if line else " "
        is_comment = line.strip().startswith("#")
        _style(
            run,
            size,
            CODE_COMMENT if is_comment else CODE_TEXT,
            italic=is_comment,
            font=MONO,
        )
    return shape


def table(slide, headers, rows, left, top, width, col_widths,
          size=15, row_height=0.52, header_color=NAVY):
    shape = slide.shapes.add_table(
        len(rows) + 1, len(headers),
        Inches(left), Inches(top), Inches(width), Inches(row_height * (len(rows) + 1)),
    )
    tbl = shape.table
    tbl.first_row = True
    tbl.horz_banding = False
    tbl.vert_banding = False

    total = sum(col_widths)
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = Emu(int(Inches(width) * w / total))

    for r_idx, row in enumerate([headers] + rows):
        tbl.rows[r_idx].height = Inches(row_height)
        for c_idx, value in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.margin_left = Inches(0.14)
            cell.margin_right = Inches(0.1)
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r_idx == 0:
                cell.fill.fore_color.rgb = _rgb(header_color)
            else:
                cell.fill.fore_color.rgb = _rgb(WHITE if r_idx % 2 else PANEL)

            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            p.line_spacing = 1.1
            run = p.add_run()
            run.text = str(value)
            _style(
                run,
                size,
                WHITE if r_idx == 0 else INK,
                bold=(r_idx == 0),
            )
    return shape


def footer(slide, number):
    text(slide, MARGIN, 6.95, 6.0, 0.3, "Agent Engineering · Buổi 1", 9, MUTED)
    text(slide, W - MARGIN - 1.2, 6.95, 1.2, 0.3, f"{number:02d}", 9, MUTED,
         align=PP_ALIGN.RIGHT)


def notes(slide, content):
    slide.notes_slide.notes_text_frame.text = content


def content_slide(kicker, title, number):
    slide = _slide()
    _bg(slide, BG)
    text(slide, MARGIN, 0.42, CONTENT_W, 0.3, kicker.upper(), 11, ACCENT, bold=True)
    text(slide, MARGIN, 0.78, CONTENT_W, 0.9, title, 34, NAVY, bold=True,
         line_spacing=1.05)
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(MARGIN), Inches(1.72),
        Inches(1.1), Inches(0.045),
    )
    line.fill.solid()
    line.fill.fore_color.rgb = _rgb(ACCENT)
    line.line.fill.background()
    footer(slide, number)
    return slide


def section_slide(number, title, subtitle, page):
    slide = _slide()
    _bg(slide, NAVY)
    text(slide, MARGIN, 1.55, 3.0, 1.6, number, 96, ACCENT, bold=True)
    text(slide, MARGIN, 3.35, 10.5, 1.0, title, 44, WHITE, bold=True)
    text(slide, MARGIN, 4.45, 10.5, 0.8, subtitle, 20, "9DB2CE")
    footer(slide, page)
    return slide


def statement_slide(kicker, big, small, number, color=NAVY):
    slide = _slide()
    _bg(slide, BG)
    text(slide, MARGIN, 0.42, CONTENT_W, 0.3, kicker.upper(), 11, ACCENT, bold=True)
    text(slide, MARGIN, 2.0, CONTENT_W, 2.2, big, 44, color, bold=True, line_spacing=1.15)
    if small:
        text(slide, MARGIN, 4.5, 9.5, 1.4, small, 20, MUTED, line_spacing=1.3)
    footer(slide, number)
    return slide


# ===========================================================================
# SLIDE
# ===========================================================================

# --- 1. Bìa -----------------------------------------------------------------
s = _slide()
_bg(s, NAVY)
bar = s.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, Inches(MARGIN), Inches(1.35), Inches(0.09), Inches(2.75)
)
bar.fill.solid()
bar.fill.fore_color.rgb = _rgb(ACCENT)
bar.line.fill.background()

text(s, MARGIN + 0.35, 1.25, 10.6, 0.4, "AGENT ENGINEERING  ·  BUỔI 1/10", 12, "8FA6C4", bold=True)
text(s, MARGIN + 0.35, 1.75, 10.6, 1.9, "Hệ thống Agent hiện đại\nvà Harness", 44, WHITE, bold=True, line_spacing=1.12)
text(s, MARGIN + 0.35, 3.85, 10.6, 0.6, "Agent  =  Model  +  Harness", 26, ACCENT)
text(s, MARGIN, 6.15, 11.5, 0.4, "120 phút  ·  55 phút lý thuyết & demo  ·  60 phút thực hành", 13, "8FA6C4")
notes(s, """Chào lớp. Hôm nay chỉ cần nhớ đúng một câu: agent = model + harness.
Mọi thứ khác trong 9 buổi còn lại là làm dày chữ 'harness'.
Cách học: gõ lại code, chạy, sửa, làm hỏng rồi sửa lại. Không học bằng cách đọc slide.
Nhắc: ai chưa có API key thì dùng FAKE=1, vẫn chạy được toàn bộ ví dụ.""")

# --- 2. Hôm nay -------------------------------------------------------------
s = content_slide("Buổi 1", "Hôm nay bạn sẽ", 2)
bullets(s, MARGIN, 2.25, 11.0, 4.2, [
    "Thấy model một mình không phải agent — và thiếu đúng cái gì",
    "Chạy tool calling thật, hiểu ai là người thực sự thi hành",
    "Chọn workflow hay agent cho đúng bài toán, đúng chi phí",
    "Tự viết agent 100 dòng: loop, tool, memory, trace",
], size=23, gap=22)
notes(s, """Bốn mục này chính là bốn phần của buổi.
Nhấn mạnh mục 4: cuối buổi mỗi người có một file agent chạy được, và đó là bộ xương của agent cuối khóa.
Đừng đi nhanh phần lý thuyết để dành thời gian thực hành — thực hành mới là chỗ hiểu bài.""")

# --- 3. Section 1 -----------------------------------------------------------
s = section_slide("01", "Model chỉ là một hàm", "Văn bản vào → văn bản ra. Hết.", 3)
notes(s, """Phần này 15 phút. Mục tiêu: hạ bệ cảm giác 'model là phép màu'.
Sẽ có người phản đối: 'nhưng nó thông minh mà'. Đúng, nhưng nó vẫn là một hàm.
Thông minh nằm ở chất lượng đầu ra, không nằm ở khả năng tự hành động.""")

# --- 4. Model là hàm --------------------------------------------------------
s = content_slide("Model", "Một hàm, ba điều không", 4)
panel(s, MARGIN, 2.15, 3.55, 2.8, PANEL)
text(s, MARGIN + 0.3, 2.4, 3.0, 0.4, "KHÔNG NHỚ", 13, ACCENT, bold=True)
text(s, MARGIN + 0.3, 2.85, 3.0, 2.5, "Mỗi lần gọi là một lần bắt đầu lại từ số 0.", 19, INK)

panel(s, MARGIN + 3.85, 2.15, 3.55, 2.8, PANEL)
text(s, MARGIN + 4.15, 2.4, 3.0, 0.4, "KHÔNG TAY CHÂN", 13, ACCENT, bold=True)
text(s, MARGIN + 4.15, 2.85, 3.0, 2.5, "Không đọc file, không chạy lệnh, không gọi API.", 19, INK)

panel(s, MARGIN + 7.7, 2.15, 3.55, 2.8, PANEL)
text(s, MARGIN + 8.0, 2.4, 3.0, 0.4, "KHÔNG BIẾT HÔM NAY", 13, ACCENT, bold=True)
text(s, MARGIN + 8.0, 2.85, 3.0, 2.5, "Không có đồng hồ, không có dữ liệu mới.", 19, INK)
text(s, MARGIN, 5.45, CONTENT_W, 0.7, "Cả ba khoảng trống đó chính là việc của harness.", 19, MUTED)
notes(s, """Ba điều không này là gốc của mọi vấn đề kỹ thuật trong khóa.
Không nhớ -> phải gửi lại lịch sử (memory).
Không tay chân -> phải có tool.
Không biết hôm nay -> phải có retrieval hoặc tool tra cứu.
Hỏi lớp: nếu model không nhớ, tại sao ChatGPT vẫn 'nhớ' cuộc trò chuyện? Để dành câu trả lời cho slide sau.""")

# --- 5. Analogy -------------------------------------------------------------
s = content_slide("Cách nghĩ", "Một chuyên gia trong phòng kín", 5)
text(s, MARGIN, 2.25, 8.2, 3.4,
     "Anh ta rất giỏi, nhưng bị nhốt trong phòng không điện thoại, không máy tính.\n"
     "Chỉ có một khe giấy: đưa câu hỏi vào, nhận câu trả lời ra.",
     23, INK, line_spacing=1.45)
panel(s, MARGIN + 8.6, 2.3, 2.9, 2.9, ACCENT_SOFT)
text(s, MARGIN + 8.85, 2.55, 2.4, 0.4, "HARNESS LÀ", 12, ACCENT, bold=True)
text(s, MARGIN + 8.85, 3.0, 2.4, 2.2,
     "ống nói,\ncửa ra vào,\ngiấy tờ,\nngười trợ lý.", 20, NAVY, line_spacing=1.35)
notes(s, """Ẩn dụ này dùng suốt buổi. Model = chuyên gia. Harness = toà nhà và người trợ lý.
Muốn chuyên gia làm được việc thật, không cần huấn luyện anh ta giỏi hơn — chỉ cần mở cửa và đưa tài liệu.
Đó chính là công việc của agent engineer, và cũng là lý do khóa học không dạy train model.""")

# --- 6. Code 01 -------------------------------------------------------------
s = content_slide("Demo · 01_hello_llm.py", "Gọi model: chỉ có vậy", 6)
code_box(s, '''from common.llm import chat, text, usage_line

messages = [
    {"role": "user", "content": "Giải thích trong 2 câu: AI agent là gì?"}
]

response = chat(messages)
print(text(response))        # câu trả lời
print(usage_line(response))  # in ra số token thực tế''',
         MARGIN, 2.05, CONTENT_W, 3.15, size=16)
text(s, MARGIN, 5.45, CONTENT_W, 1.0,
     "Toàn bộ 'trạng thái' của chương trình là một list messages. Không có gì khác.",
     18, MUTED)
notes(s, """Chạy live. Chỉ vào hai dòng: chat() và text().
Hỏi lớp: chương trình này nhớ gì giữa hai lần chạy? Không gì cả.
usage_line in ra token — cho lớp thấy mỗi lần gọi là một lần trả tiền, ngay từ slide đầu.""")

# --- 7. Không có trí nhớ ----------------------------------------------------
s = content_slide("Demo · 02_stateless.py", "Cùng một câu hỏi, hai kết quả", 7)
table(s,
      ["Cách gửi", "Model nhìn thấy", "Kết quả"],
      [["Chỉ câu hỏi", '["Mình tên gì?"]', "Không biết bạn là ai"],
       ["Kèm lịch sử", '["Mình tên Minh", ..., "Mình tên gì?"]', '"Bạn tên Minh."']],
      MARGIN, 2.2, CONTENT_W, [2.6, 4.4, 3.4], size=17, row_height=0.75)
text(s, MARGIN, 4.9, CONTENT_W, 1.2,
     "Không có bộ nhớ nào cả. Chỉ là lần thứ hai bạn gửi nhiều chữ hơn.",
     20, MUTED)
notes(s, """Đây là slide 'à ra thế' của buổi. Chạy 02 live nếu còn thời gian.
Nhấn: memory không phải tính năng của model, mà là quyết định của người viết harness.
Từ đây suy ra toàn bộ bài toán context ở buổi 4: gửi gì, bỏ gì, nén thế nào.""")

# --- 8. Memory là gì --------------------------------------------------------
s = content_slide("Định nghĩa", "Memory thật ra là một list", 8)
code_box(s, '''history = []

history.append({"role": "user", "content": cau_hoi_moi})
messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

# mỗi lượt, list này dài thêm -> đó là "trí nhớ"
# dài quá -> tốn token, chậm, và model bắt đầu quên giữa chừng''',
         MARGIN, 2.05, CONTENT_W, 2.5, size=16)
statement = panel(s, MARGIN, 4.85, CONTENT_W, 1.15, ACCENT_SOFT)
text(s, MARGIN + 0.4, 5.05, CONTENT_W - 0.8, 0.8,
     "Model không nhớ. Harness nhớ hộ.", 26, NAVY, bold=True)
notes(s, """Một câu chốt duy nhất. Cho lớp ghi vào vở.
Nói trước: câu này sẽ quay lại ở buổi 4 với tên gọi 'context engineering'.
Và ở buổi 7 với tên gọi 'evaluation' — vì gửi sai context là nguyên nhân số một gây trả lời sai.""")

# --- 9. Section 2 -----------------------------------------------------------
s = section_slide("02", "Suy nghĩ là một khoản ngân sách", "Không phải phép màu, cũng không miễn phí.", 9)
notes(s, """Phần này 10 phút. Mục tiêu: học viên biết chọn model theo việc, không theo mốt.
Hai loại model khác nhau ở chỗ có dành thời gian nghĩ trước khi nói hay không.
Đừng để lớp nghĩ reasoning model luôn tốt hơn — nó chỉ tốt hơn cho việc nhiều bước.""")

# --- 10. Hai loại model -----------------------------------------------------
s = content_slide("Model", "Hai kiểu suy nghĩ", 10)
panel(s, MARGIN, 2.1, 5.5, 3.7, PANEL)
text(s, MARGIN + 0.35, 2.35, 4.8, 0.5, "MODEL THƯỜNG", 12, ACCENT, bold=True)
text(s, MARGIN + 0.35, 2.85, 4.8, 2.35,
     "gpt-4o-mini\nTrả lời ngay.\nNhanh, rẻ.\nĐủ cho phần lớn việc.", 20, INK, line_spacing=1.3, space_after=4)

panel(s, MARGIN + 5.9, 2.1, 5.5, 3.7, ACCENT_SOFT)
text(s, MARGIN + 6.25, 2.35, 4.8, 0.5, "MODEL REASONING", 12, ACCENT, bold=True)
text(s, MARGIN + 6.25, 2.85, 4.8, 2.35,
     "gpt-5, o-series\nNghĩ trước khi nói.\nChậm hơn, đắt hơn.\nGiỏi việc nhiều bước.", 20, INK, line_spacing=1.3, space_after=4)
notes(s, """Đừng sa vào chi tiết kiến trúc model. Chỉ cần: có loại trả lời ngay, có loại nghĩ trước.
Ví dụ: gpt-5, o-series là loại nghĩ trước. gpt-4o-mini là loại trả lời ngay.
Chi phí khác nhau có thể 10-30 lần. Đó là lý do phải chọn theo việc, không chọn theo 'xịn nhất'.""")

# --- 11. Demo 03 ------------------------------------------------------------
s = content_slide("Demo · 03_reasoning.py", "Cùng model, ba cách hỏi", 11)
table(s,
      ["Cách", "Bạn thêm gì", "Đúng?", "Token"],
      [["A", '"Chỉ trả lời đáp án"', "Hay ra 10 (sai)", "Ít nhất"],
       ["B", '"Suy nghĩ từng bước rồi chốt"', "Thường ra 8 (đúng)", "Nhiều hơn chút"],
       ["C", "Đổi sang model reasoning", "Đúng nhất", "Nhiều nhất"]],
      MARGIN, 2.15, CONTENT_W, [1.2, 5.0, 3.2, 2.4], size=17, row_height=0.68)
text(s, MARGIN, 5.0, CONTENT_W, 1.0,
     "Câu đố: ốc sên leo cột 10m, ngày 3m đêm tụt 2m. Đáp án đúng là 8 ngày.",
     17, MUTED)
notes(s, """Chạy live nếu có key. Nếu model trả lời đúng ngay từ A, đừng giả vờ ngạc nhiên — nói thật: model mới đã khá hơn, nhưng nguyên tắc vẫn đúng.
Điểm cần nhấn: B chỉ là đổi prompt, không đổi model. Đó là context engineering, rẻ hơn nhiều so với đổi model.""")

# --- 12. Khi nào bật --------------------------------------------------------
s = content_slide("Quy tắc", "Khi nào bật suy nghĩ?", 12)
bullets(s, MARGIN, 2.15, 11.2, 4.2, [
    "Phân loại, trích xuất, viết lại câu  →  model thường",
    "Tính nhiều bước, lập kế hoạch, debug logic  →  reasoning",
    "Việc chạy hằng ngày, khối lượng lớn  →  model thường + đo chất lượng định kỳ",
], size=21, gap=20)
text(s, MARGIN, 5.45, 11.2, 1.0,
     "Mỗi lần bật suy nghĩ là một lần trả thêm tiền và bắt người dùng chờ.",
     18, MUTED)
notes(s, """Đây là quyết định kỹ thuật, không phải sở thích.
Buổi 7 sẽ dạy cách đo: bật reasoning tăng bao nhiêu % độ chính xác, tốn thêm bao nhiêu tiền.
Nếu không đo được, đừng bật.""")

# --- 13. Section 3 ----------------------------------------------------------
s = section_slide("03", "Tool calling", "Model xin phép. Bạn mới là người chạy.", 13)
notes(s, """Phần quan trọng nhất buổi. Dành 20 phút. Đi chậm.
Nếu lớp chỉ nhớ một thứ sau buổi này, hãy là phần này.""")

# --- 14. Model không chạy code ----------------------------------------------
s = statement_slide(
    "Điều quan trọng nhất buổi hôm nay",
    "Model không chạy code của bạn.",
    "Nó chỉ sinh ra một JSON nói rằng: “tôi muốn gọi hàm này, với tham số này”.\n"
    "Chính bạn — harness — là người chạy hàm đó.",
    14,
)
notes(s, """Nói chậm, rõ. Nhiều người học xong vẫn tin model tự chạy tool.
Đây là ranh giới an ninh quan trọng nhất của cả khóa: model không có quyền gì trên máy bạn.
Mọi quyền đều do harness cấp. Buổi 8 sẽ khai thác đúng ranh giới này.""")

# --- 15. 3 bước -------------------------------------------------------------
s = content_slide("Cơ chế", "Ba bước, không hơn", 15)
steps = [
    ("1", "Bạn gửi", "câu hỏi\n+ danh sách tool"),
    ("2", "Model xin gọi", 'tool_calls:\nget_weather(city="Hà Nội")\ncontent = None'),
    ("3", "Bạn chạy tool", "get_weather('Hà Nội')\n→ 28°C\nrồi gửi lại kết quả"),
]
x = MARGIN
for idx, (num, head, body) in enumerate(steps):
    panel(s, x, 2.15, 3.5, 2.75, PANEL)
    text(s, x + 0.3, 2.35, 0.6, 0.5, num, 22, ACCENT, bold=True)
    text(s, x + 0.3, 2.85, 3.0, 0.45, head, 17, NAVY, bold=True)
    text(s, x + 0.3, 3.35, 2.95, 1.6, body, 14, INK, line_spacing=1.25)
    if idx < 2:
        text(s, x + 3.52, 3.35, 0.35, 0.5, "→", 26, ACCENT, bold=True)
    x += 3.9
text(s, MARGIN, 5.45, CONTENT_W, 1.0,
     "Bước 2 là chỗ hay bị hiểu nhầm nhất: chưa có câu trả lời nào cả, chỉ có một lời xin.",
     18, MUTED)
notes(s, """Vẽ lại sơ đồ này lên bảng nếu được. Ba hộp, hai mũi tên.
Nhấn bước 2: content rỗng. Nhiều người tưởng model trả lời luôn, thực ra không.
Bước 3 là code của bạn. Nếu bạn không chạy, agent đứng im.""")

# --- 16. Code 3 dòng --------------------------------------------------------
s = content_slide("Demo · 04_tool_calling.py", "Ba dòng cuối là toàn bộ bí mật", 16)
code_box(s, '''# 1. nối lời xin gọi tool vào lịch sử
messages.append(message)

# 2. ta chạy hàm Python thật, gửi kết quả lại
messages.append({
    "role": "tool",
    "tool_call_id": call.id,
    "content": ket_qua,
})

# 3. model giờ mới viết câu trả lời
second = chat(messages, tools=TOOLS)''', MARGIN, 2.0, CONTENT_W, 3.6, size=14)
text(s, MARGIN, 5.85, CONTENT_W, 0.7,
     "Bỏ dòng nào trong ba dòng này, agent cũng hỏng theo một kiểu khác nhau.",
     17, MUTED)
notes(s, """Cho lớp sửa thử ngay tại chỗ: xoá dòng append(message) rồi chạy — API sẽ báo lỗi.
Đó là cách học nhanh nhất: làm hỏng có kiểm soát.
Câu hỏi cho lớp: nếu tool trả về kết quả sai thì ai chịu trách nhiệm? Trả lời: harness, không phải model.""")

# --- 17. Hiểu nhầm ----------------------------------------------------------
s = content_slide("Cảnh báo", "Ba hiểu nhầm hay gặp", 17)
table(s,
      ["Hiểu nhầm", "Sự thật"],
      [["Model tự chạy code của tôi", "Không. Nó chỉ sinh JSON mô tả hàm muốn gọi."],
       ["Model biết kết quả tool là đúng", "Không. Nó tin bạn. Tool sai thì agent sai."],
       ["Có tool là agent tự biết dùng", "Chỉ khi mô tả tool đủ rõ và tham số đủ dễ điền."]],
      MARGIN, 2.15, CONTENT_W, [4.6, 7.0], size=17, row_height=0.9)
text(s, MARGIN, 5.6, CONTENT_W, 0.8,
     "Vì vậy viết mô tả tool là một kỹ năng — đó là buổi 3.",
     17, MUTED)
notes(s, """Hiểu nhầm thứ ba là lý do nhiều agent 'không chịu dùng tool'.
Không phải model dở, mà mô tả tool mơ hồ: tên hàm xấu, tham số không rõ kiểu, không nói khi nào nên dùng.
Buổi 3 sẽ có checklist thiết kế tool.""")

# --- 18. Section 4 ----------------------------------------------------------
s = section_slide("04", "Workflow hay Agent?", "Chọn mức đơn giản nhất đủ dùng.", 18)
notes(s, """Phần này 15 phút — phần dễ bị bỏ qua nhất, nhưng là phần tiết kiệm tiền nhất.
Nhiều đội xây agent khi chỉ cần ba dòng if. Kết quả: chậm, đắt, khó debug.
Thông điệp: agent không phải đích đến, nó là một mức trong thang.""")

# --- 19. Thang 5 mức --------------------------------------------------------
s = content_slide("Thang bậc", "Từ chắc chắn đến linh hoạt", 19)
table(s,
      ["Mức", "Tên", "Ví dụ", "Ai quyết định"],
      [["1", "Prompt", "Viết lại email", "Không ai"],
       ["2", "Chain", "Dịch → tóm tắt → kiểm tra", "Bạn, cố định"],
       ["3", "Routing", "Hỏi hoá đơn → nhánh hoá đơn", "Model chọn nhánh"],
       ["4", "Orchestrator", "Chia việc, chạy song song", "Model chọn việc"],
       ["5", "Agent", "Tự lập kế hoạch, tự gọi tool", "Model"]],
      MARGIN, 2.05, CONTENT_W, [1.0, 2.6, 5.2, 2.8], size=15,
      row_height=0.62)
text(s, MARGIN, 5.85, CONTENT_W, 0.7,
     "Càng lên cao: linh hoạt hơn, khó đoán hơn, khó test hơn, tốn hơn.",
     17, MUTED)
notes(s, """Đừng đọc cả bảng. Chỉ vào mức 2 và mức 5, vì đó là hai đầu thực tế.
Hỏi lớp: việc của bạn hằng ngày nằm ở mức mấy? Phần lớn câu trả lời là 2-3.
Nếu ai nói 5, hỏi lại: bạn có eval chưa? Nếu chưa, hạ xuống 3.""")

# --- 20. So sánh ------------------------------------------------------------
s = content_slide("Demo · 05_workflow_vs_agent.py", "Cùng một câu hỏi, hai cách viết", 20)
panel(s, MARGIN, 2.1, 5.5, 3.3, PANEL)
text(s, MARGIN + 0.35, 2.3, 4.8, 0.45, "WORKFLOW", 12, ACCENT, bold=True)
text(s, MARGIN + 0.35, 2.75, 4.9, 2.3,
     "get_order_status(\"1234\")\ncheck_return_policy(\"tai nghe\")\nchat(...)  # chỉ viết câu trả lời", 15, INK,
     line_spacing=1.5)
text(s, MARGIN + 0.35, 4.6, 4.8, 0.5, "Đoán trước được · dễ test · rẻ", 14, GREEN, bold=True)

panel(s, MARGIN + 5.9, 2.1, 5.5, 3.3, ACCENT_SOFT)
text(s, MARGIN + 6.25, 2.3, 4.8, 0.45, "AGENT", 12, ACCENT, bold=True)
text(s, MARGIN + 6.25, 2.75, 4.9, 2.3,
     "for _ in range(max_buoc):\n    model tự chọn tool\n    ta chạy tool\n    lặp đến khi model dừng", 15, INK,
     line_spacing=1.5)
text(s, MARGIN + 6.25, 4.6, 4.8, 0.5, "Linh hoạt · khó đoán · khó test", 14, AMBER, bold=True)

text(s, MARGIN, 5.75, CONTENT_W, 0.9,
     "Đổi câu hỏi sang đơn 9999: workflow phải sửa code, agent thì không.",
     18, NAVY, bold=True)
notes(s, """Chạy 05 nếu còn thời gian. Chỉ vào bảng so sánh in ra cuối chương trình.
Câu hỏi hay để hỏi lớp: nếu khách hỏi câu chưa từng có trong kịch bản, cách nào sống sót?
Nhưng đừng kết luận 'agent luôn tốt hơn' — chi phí và độ ổn định là giá phải trả.""")

# --- 21. Section 5 ----------------------------------------------------------
s = section_slide("05", "Agent = Model + Harness", "Sáu phần, và 9 buổi còn lại làm dày chúng.", 21)
notes(s, """Phần này 20 phút, là trọng tâm của buổi.
Đây là bản đồ: sáu ô, mỗi ô ứng với một buổi sau này.
Học viên nên chụp lại slide sáu phần — nó là mục lục của khóa.""")

# --- 22. Sáu phần -----------------------------------------------------------
s = content_slide("Kiến trúc", "Sáu phần của một agent", 22)
table(s,
      ["#", "Thành phần", "Trong 06_mini_harness.py", "Làm dày ở"],
      [["1", "Model", "chat()", "Buổi 1–2"],
       ["2", "Tools", "common/shop.py + TOOLS", "Buổi 3"],
       ["3", "Loop", "for step in range(1, MAX_STEPS+1)", "Buổi 2"],
       ["4", "Context", "SYSTEM_PROMPT + messages", "Buổi 4"],
       ["5", "Memory", "self.history", "Buổi 4"],
       ["6", "Observability", "self.trace + traces/last_run.json", "Buổi 7"]],
      MARGIN, 1.98, CONTENT_W, [0.8, 2.6, 5.8, 2.3], size=15, row_height=0.55)
notes(s, """Đây là bản đồ của cả khóa. Chỉ vào từng dòng và nói buổi nào sẽ mở rộng.
Học viên hay hỏi: vậy guardrails, security đâu? Trả lời: đó là lớp bọc quanh cả sáu phần, buổi 8.
Persistence/checkpoint? Buổi 2. Multi-agent? Buổi 6.""")

# --- 23. Loop ---------------------------------------------------------------
s = content_slide("Vòng lặp", "Observe → Think → Act → Verify", 23)
items = [("OBSERVE", "nhận câu hỏi\nvà kết quả tool"),
         ("THINK", "model quyết định:\ntrả lời hay gọi tool"),
         ("ACT", "harness chạy tool\nthật trên máy bạn"),
         ("VERIFY", "câu trả lời có dùng\nđúng dữ liệu không?")]
x = MARGIN
for idx, (head, body) in enumerate(items):
    panel(s, x, 2.2, 2.6, 2.0, PANEL if idx != 3 else ACCENT_SOFT)
    text(s, x + 0.25, 2.45, 2.1, 0.4, head, 14, ACCENT, bold=True)
    text(s, x + 0.25, 2.9, 2.15, 1.4, body, 14, INK, line_spacing=1.3)
    if idx < 3:
        text(s, x + 2.62, 2.9, 0.3, 0.4, "→", 24, ACCENT, bold=True)
    x += 2.93
text(s, MARGIN, 5.05, CONTENT_W, 1.2,
     "Trong file, VERIFY là _finish(): câu trả lời thiếu dữ kiện → nhắc model sửa một lần.\n"
     "Kiểm tra là việc của harness, không phải của model.",
     17, MUTED, line_spacing=1.4)
notes(s, """Bốn bước này sẽ quay lại nguyên văn ở buổi 2 với LangGraph.
Nhấn VERIFY: hầu hết agent tự viết đều thiếu bước này, nên trả lời sai một cách tự tin.
Đây cũng là nền của evaluation ở buổi 7.""")

# --- 24. ChatGPT / Claude Code / Cursor -------------------------------------
s = content_slide("So sánh", "Cùng bộ não, khác cơ thể", 24)
table(s,
      ["", "ChatGPT", "Claude Code", "Cursor"],
      [["Tools", "web, python, ảnh", "file, shell, git", "file, terminal, LSP"],
       ["Context", "hội thoại + memory", "tự đọc file, nén lịch sử", "file mở + index repo"],
       ["Chạy ở đâu", "server của họ", "máy bạn", "máy bạn"],
       ["Kiểm soát", "ít", "hỏi trước lệnh nguy hiểm", "hỏi trước khi sửa file"]],
      MARGIN, 2.1, CONTENT_W, [2.0, 3.2, 3.4, 3.2], size=15, row_height=0.6)
text(s, MARGIN, 5.45, CONTENT_W, 0.8,
     "Khác biệt lớn nhất không nằm ở model — mà ở harness.",
     19, NAVY, bold=True)
notes(s, """Hỏi lớp: ai dùng Claude Code? Nó xin phép bạn ở đâu? Đó là human-in-the-loop.
Ai dùng Cursor? Nó đọc file nào trước? Đó là context engineering.
Mục đích: học viên thấy những khái niệm sắp học không phải lý thuyết suông, mà là thứ họ gặp hằng ngày.""")

# --- 25. Section Lab --------------------------------------------------------
s = section_slide("Lab", "60 phút thực hành", "Chạy, làm hỏng, sửa lại.", 25)
notes(s, """60 phút. Ba phần: chạy 6 bài (20 phút), quan sát harness có sẵn (20 phút), sửa harness (20 phút).
Đi vòng quanh lớp. Câu hỏi duy nhất cần hỏi mỗi nhóm: dòng này ai quyết định — model hay bạn?
Cuối giờ gọi 2-3 nhóm trình bày. Không chữa bài thay họ.""")

# --- 26. Lab roadmap --------------------------------------------------------
s = content_slide("Lab", "Ba phần", 26)
panel(s, MARGIN, 2.1, 3.5, 2.55, PANEL)
text(s, MARGIN + 0.3, 2.3, 2.9, 0.4, "20 PHÚT", 12, ACCENT, bold=True)
text(s, MARGIN + 0.3, 2.7, 2.9, 0.6, "Chạy 6 bài", 20, NAVY, bold=True)
text(s, MARGIN + 0.3, 3.3, 2.9, 1.4, "Mỗi file trả lời:\ndòng nào model quyết định?\ndòng nào tôi quyết định?", 14, INK)

panel(s, MARGIN + 3.9, 2.1, 3.5, 2.55, PANEL)
text(s, MARGIN + 4.2, 2.3, 2.9, 0.4, "20 PHÚT", 12, ACCENT, bold=True)
text(s, MARGIN + 4.2, 2.7, 2.9, 0.6, "Quan sát", 20, NAVY, bold=True)
text(s, MARGIN + 4.2, 3.3, 2.9, 1.4, "Dùng một agent có sẵn.\nĐiền worksheet.md.\nĐối chiếu với bài 06.", 14, INK)

panel(s, MARGIN + 7.8, 2.1, 3.5, 2.55, ACCENT_SOFT)
text(s, MARGIN + 8.1, 2.3, 2.9, 0.4, "20 PHÚT", 12, ACCENT, bold=True)
text(s, MARGIN + 8.1, 2.7, 2.9, 0.6, "Sửa harness", 20, NAVY, bold=True)
text(s, MARGIN + 8.1, 3.3, 2.9, 1.4, "Chọn ≥ 2 bài trong\nexercises.md.\nLàm ngay tại lớp.", 14, INK)
notes(s, """Chia lớp thành cặp nếu đông. Mỗi cặp một máy chạy, một người đọc code.
Đi vòng quanh, chỗ nào cũng hỏi đúng một câu: 'dòng này ai quyết định?'
Cuối giờ gọi 2-3 cặp trình bày phát hiện. Đừng chữa bài tập thay họ.""")

# --- 27. Bài tập ------------------------------------------------------------
s = content_slide("Về nhà", "Bài tập bắt buộc", 27)
bullets(s, MARGIN, 2.15, 11.2, 4.0, [
    "Bài 1 — thêm tool calc_refund, xem agent có chọn đúng không",
    "Bài 4 — làm tool ném lỗi thật, bọc try/except, agent không được chết",
], size=21, gap=18)
text(s, MARGIN, 3.6, 11.2, 2.0,
     "Tiêu chí: giải thích được vì sao sửa như vậy, không chỉ chạy được.\n"
     "Nộp: file đã sửa + một đoạn trace chứng minh.",
     17, MUTED, line_spacing=1.5)
notes(s, """Bài 4 là bài quan trọng nhất: nó dạy rằng tool luôn có thể hỏng, và harness phải chịu được.
Bài 1 dạy viết mô tả tool — chuẩn bị cho buổi 3.
Ai làm xong sớm: bài 6 (viết test) là bản nháp của evaluation.""")

# --- 28. Tổng kết -----------------------------------------------------------
s = content_slide("Tổng kết", "Năm câu mang về", 28)
bullets(s, MARGIN, 2.05, 11.4, 4.5, [
    "Model là hàm văn bản → văn bản. Không nhớ, không làm.",
    "\"Memory\" là messages được gửi lại. Context là thứ bạn thiết kế.",
    "Tool calling: model xin gọi, harness chạy thật.",
    "Chọn mức đơn giản nhất đủ dùng: workflow trước, agent sau.",
    "Muốn agent tốt hơn: sửa harness trước khi đổi model.",
], size=20, gap=16)
notes(s, """Đọc chậm từng câu. Dừng ở câu 5 — đó là triết lý của cả khóa.
Nếu chỉ còn 30 giây: 'agent = model + harness, và bạn viết harness'.""")

# --- 29. Buổi sau -----------------------------------------------------------
s = content_slide("Buổi 2", "Tiếp theo: Agent Loop với LangGraph", 29)
bullets(s, MARGIN, 2.15, 11.2, 3.2, [
    "Thay vòng for tự viết bằng graph có state",
    "Checkpoint: agent chết giữa đường vẫn chạy tiếp được",
    "Streaming: người dùng thấy agent đang làm gì",
    "Human-in-the-loop: dừng lại xin phép trước hành động nguy hiểm",
], size=20, gap=16)
text(s, MARGIN, 5.3, 11.2, 1.0,
     "Chuẩn bị: đọc lại 06_mini_harness.py đến khi giải thích được vòng for mà không mở file.",
     17, MUTED)
notes(s, """Kết thúc. Nhắc nộp bài trước buổi 2.
Buổi 2 sẽ dùng chính file 06 làm điểm xuất phát — nên ai không hiểu file đó sẽ rất vất vả.
Mời lớp đặt câu hỏi.""")

# --- Lưu --------------------------------------------------------------------
out = Path(__file__).with_name("slides.pptx")
prs.save(out)
print(f"Đã tạo {out} ({len(prs.slides)} slide)")
