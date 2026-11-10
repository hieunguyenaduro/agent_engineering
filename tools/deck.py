"""Thư viện dựng slide dùng chung cho các buổi.

Mỗi buổi có một file slides/build_slides.py riêng, import thư viện này để giữ
đúng một phong cách trình bày.

Ví dụ tối thiểu:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
    from deck import Deck

    d = Deck(session="Buổi 2")
    d.title("AGENT ENGINEERING", "Agent Loop với LangGraph", "Graph, state, checkpoint", "120 phút")
    s = d.content("LÝ THUYẾT", "Vì sao cần graph?")
    d.bullets(s, ["Vòng lặp viết tay khó debug", "Graph cho thấy rõ từng bước"])
    d.note(s, "Ghi chú cho giảng viên.")
    d.save()
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# --- Bảng màu (giữ nguyên cho toàn khóa) ------------------------------------
NAVY = "0F2137"
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
RED = "B91C1C"
WHITE = "FFFFFF"

FONT = "Arial"
MONO = "Consolas"

SLIDE_W = 13.333
SLIDE_H = 7.5
MARGIN = 0.9
CONTENT_W = SLIDE_W - 2 * MARGIN


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


class Deck:
    def __init__(self, session="Agent Engineering", out="slides.pptx"):
        self.session = session
        self.out = Path(out)
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.blank = self.prs.slide_layouts[6]
        self.page = 0

    # -- hạ tầng -----------------------------------------------------------
    def _slide(self, count=True):
        slide = self.prs.slides.add_slide(self.blank)
        if count:
            self.page += 1
        return slide

    def _bg(self, slide, color):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = rgb(color)

    def _footer(self, slide):
        self.text(slide, MARGIN, 6.95, 6.0, 0.3, self.session, 9, MUTED)
        self.text(
            slide, SLIDE_W - MARGIN - 1.2, 6.95, 1.2, 0.3,
            f"{self.page:02d}", 9, MUTED, align=PP_ALIGN.RIGHT,
        )

    @staticmethod
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

    @staticmethod
    def _style(run, size, color, bold=False, italic=False, font=FONT):
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = rgb(color)
        run.font.name = font

    # -- thành phần --------------------------------------------------------
    def title(self, kicker, title, subtitle="", meta="", notes=""):
        slide = self._slide(count=False)
        self._bg(slide, NAVY)
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(MARGIN), Inches(1.35), Inches(0.09), Inches(2.75)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = rgb(ACCENT)
        bar.line.fill.background()

        self.text(slide, MARGIN + 0.35, 1.25, 10.6, 0.4, kicker.upper(), 12, "8FA6C4", bold=True)
        self.text(slide, MARGIN + 0.35, 1.75, 10.6, 1.9, title, 44, WHITE, bold=True, line_spacing=1.12)
        if subtitle:
            self.text(slide, MARGIN + 0.35, 3.85, 10.6, 0.6, subtitle, 24, ACCENT)
        if meta:
            self.text(slide, MARGIN, 6.15, 11.5, 0.4, meta, 13, "8FA6C4")
        if notes:
            self.note(slide, notes)
        return slide

    def section(self, number, title, subtitle="", notes=""):
        slide = self._slide()
        self._bg(slide, NAVY)
        self.text(slide, MARGIN, 1.55, 3.0, 1.6, number, 96, ACCENT, bold=True)
        self.text(slide, MARGIN, 3.35, 10.5, 1.0, title, 42, WHITE, bold=True)
        if subtitle:
            self.text(slide, MARGIN, 4.45, 10.5, 0.8, subtitle, 20, "9DB2CE")
        self._footer(slide)
        if notes:
            self.note(slide, notes)
        return slide

    def statement(self, kicker, big, small="", notes="", color=NAVY):
        slide = self._slide()
        self._bg(slide, BG)
        self.text(slide, MARGIN, 0.42, CONTENT_W, 0.3, kicker.upper(), 11, ACCENT, bold=True)
        self.text(slide, MARGIN, 2.0, CONTENT_W, 2.2, big, 42, color, bold=True, line_spacing=1.15)
        if small:
            self.text(slide, MARGIN, 4.5, 9.5, 1.4, small, 20, MUTED, line_spacing=1.3)
        self._footer(slide)
        if notes:
            self.note(slide, notes)
        return slide

    def content(self, kicker, title, notes=""):
        slide = self._slide()
        self._bg(slide, BG)
        self.text(slide, MARGIN, 0.42, CONTENT_W, 0.3, kicker.upper(), 11, ACCENT, bold=True)
        self.text(slide, MARGIN, 0.78, CONTENT_W, 0.9, title, 34, NAVY, bold=True, line_spacing=1.05)
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(MARGIN), Inches(1.72), Inches(1.1), Inches(0.045)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = rgb(ACCENT)
        line.line.fill.background()
        self._footer(slide)
        if notes:
            self.note(slide, notes)
        return slide

    # -- nội dung ----------------------------------------------------------
    def text(self, slide, left, top, width, height, content, size=20, color=INK,
             bold=False, align=PP_ALIGN.LEFT, line_spacing=1.15, space_after=6):
        shape, tf = self._box(slide, left, top, width, height)
        for i, line in enumerate(content.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = line_spacing
            p.space_after = Pt(space_after)
            run = p.add_run()
            run.text = line
            self._style(run, size, color, bold=bold)
        return shape

    def bullets(self, slide, items, left=MARGIN, top=2.15, width=CONTENT_W,
                height=4.2, size=20, color=INK, gap=16, line_spacing=1.2):
        shape, tf = self._box(slide, left, top, width, height)
        for i, item in enumerate(items):
            level = 0
            if isinstance(item, tuple):
                item, level = item
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(gap)
            p.line_spacing = line_spacing
            run = p.add_run()
            run.text = ("•  " if level == 0 else "–  ") + item
            self._style(run, size if level == 0 else size - 2, color if level == 0 else MUTED)
            if level > 0:
                p.level = 1
        return shape

    def panel(self, slide, left, top, width, height, color=PANEL, line=None):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left), Inches(top), Inches(width), Inches(height),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(color)
        if line:
            shape.line.color.rgb = rgb(line)
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        shape.shadow.inherit = False
        shape.adjustments[0] = 0.06
        return shape

    def code(self, slide, code, left=MARGIN, top=2.0, width=CONTENT_W,
             height=3.2, size=14):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left), Inches(top), Inches(width), Inches(height),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(CODE_BG)
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
            self._style(
                run, size,
                CODE_COMMENT if is_comment else CODE_TEXT,
                italic=is_comment, font=MONO,
            )
        return shape

    def table(self, slide, headers, rows, left=MARGIN, top=2.1, width=CONTENT_W,
              col_widths=None, size=15, row_height=0.55, header_color=NAVY):
        col_widths = col_widths or [1] * len(headers)
        shape = slide.shapes.add_table(
            len(rows) + 1, len(headers),
            Inches(left), Inches(top), Inches(width),
            Inches(row_height * (len(rows) + 1)),
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
                    cell.fill.fore_color.rgb = rgb(header_color)
                else:
                    cell.fill.fore_color.rgb = rgb(WHITE if r_idx % 2 else PANEL)

                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT
                p.line_spacing = 1.1
                run = p.add_run()
                run.text = str(value)
                self._style(run, size, WHITE if r_idx == 0 else INK, bold=(r_idx == 0))
        return shape

    def note(self, slide, content):
        slide.notes_slide.notes_text_frame.text = content

    def save(self, path=None):
        target = Path(path) if path else self.out
        target.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(target)
        print(f"Đã tạo {target} ({len(self.prs.slides)} slide)")
        return target
