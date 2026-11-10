"""01 — Ngân sách context: cái gì chiếm chỗ, và cắt theo thứ tự nào.

Chạy: python 01_context_budget.py
Không gọi model, không cần API key. Token là ước lượng chars/4 (xem common/tokens.py).
"""

import json
from dataclasses import dataclass, field

from common.demo_data import (
    DEVELOPER, DOCS, FACTS, SYSTEM, TOOLS, TOOL_RESULTS, TURNS,
)
from common.tokens import bar, estimate_tokens, print_table, shorten

# Cửa sổ thu nhỏ để bài học hiện ra rõ. Model thật có thể lớn hơn hàng chục lần,
# nhưng tỉ lệ giữa các thành phần thì giống nhau.
WINDOW = 700
KEEP_RECENT_MESSAGES = 6      # số message gần nhất luôn giữ nguyên
KEEP_RECENT_TOOL_RESULTS = 2  # chỉ giữ full kết quả của 2 lần gọi gần nhất


@dataclass
class Context:
    system: str = SYSTEM
    developer: str = DEVELOPER
    tools: str = field(default_factory=lambda: json.dumps(TOOLS, ensure_ascii=False))
    summary: str = ""
    history: list = field(default_factory=lambda: [
        {"role": role, "content": text} for role, text in TURNS
    ])
    docs: list = field(default_factory=lambda: list(DOCS))

    def add_tool_results(self):
        # Chèn kết quả tool ngay sau câu hỏi tương ứng, như một hội thoại thật.
        for i, result in enumerate(TOOL_RESULTS):
            self.history.insert(min(len(self.history), 2 + i * 2), {"role": "tool", "content": result})

    def total(self):
        parts = [self.system, self.developer, self.tools, self.summary]
        parts += [message["content"] for message in self.history]
        return sum(estimate_tokens(p) for p in parts) + sum(estimate_tokens(d) for d in self.docs)

    def rows(self):
        turns = [m for m in self.history if m["role"] != "tool"]
        tools = [m for m in self.history if m["role"] == "tool"]
        rows = [
            ("System prompt", len(self.system), estimate_tokens(self.system)),
            ("Developer rules", len(self.developer), estimate_tokens(self.developer)),
            ("Tool schema (5 tool)", len(self.tools), estimate_tokens(self.tools)),
            (f"Lịch sử ({len(turns)} message)", sum(len(m["content"]) for m in turns),
             sum(estimate_tokens(m["content"]) for m in turns)),
            (f"Kết quả tool ({len(tools)} lần)", sum(len(m["content"]) for m in tools),
             sum(estimate_tokens(m["content"]) for m in tools)),
            (f"Tài liệu retrieve ({len(self.docs)} đoạn)", sum(len(d) for d in self.docs),
             sum(estimate_tokens(d) for d in self.docs)),
        ]
        if self.summary:
            rows.append(("Tóm tắt hội thoại", len(self.summary), estimate_tokens(self.summary)))
        return rows


def show(ctx: Context, title: str):
    rows = ctx.rows()
    total = ctx.total()
    print(f"\n{title}  —  {total}/{WINDOW} token ({total * 100 // WINDOW}% cửa sổ)")
    print_table(
        ["Thành phần", "Ký tự", "Token", "% cửa sổ", ""],
        [[name, chars, tok, f"{tok * 100 // WINDOW}%", bar(tok, WINDOW)] for name, chars, tok in rows]
        + [["TỔNG", sum(r[1] for r in rows), total, f"{total * 100 // WINDOW}%", bar(total, WINDOW)]],
        widths=[24, 7, 6, 7, 22],
    )


def trim_old_tool_results(ctx: Context) -> int:
    """Cắt kết quả tool cũ trước: chúng dài, ít giá trị lâu dài, và đã có kết luận."""
    before = ctx.total()
    tool_indexes = [i for i, m in enumerate(ctx.history) if m["role"] == "tool"]
    for i in tool_indexes[:-KEEP_RECENT_TOOL_RESULTS]:
        ctx.history[i]["content"] = shorten(ctx.history[i]["content"], 90)
    return before - ctx.total()


def summarize_old_turns(ctx: Context) -> int:
    """Nén các lượt cũ thành tóm tắt + facts, giữ nguyên các lượt gần nhất."""
    before = ctx.total()
    old, recent = ctx.history[:-KEEP_RECENT_MESSAGES], ctx.history[-KEEP_RECENT_MESSAGES:]
    if not old:
        return 0
    ctx.summary = "Tóm tắt các lượt trước: " + "; ".join(FACTS) + "."
    ctx.history = recent
    return before - ctx.total()


def trim_docs(ctx: Context) -> int:
    """Tài liệu retrieve chỉ giữ đoạn đầu, và chỉ khi còn chỗ."""
    before = ctx.total()
    ctx.docs = [shorten(ctx.docs[0], 420)] if ctx.docs else []
    return before - ctx.total()


def main():
    ctx = Context()
    ctx.add_tool_results()
    show(ctx, "TRƯỚC")

    if ctx.total() <= WINDOW:
        print("\nVừa cửa sổ, không cần cắt.")
        return

    steps = []
    for name, fn in [
        ("1. Cắt kết quả tool cũ", trim_old_tool_results),
        ("2. Tóm tắt lượt cũ", summarize_old_turns),
        ("3. Tỉa tài liệu retrieve", trim_docs),
    ]:
        freed = fn(ctx)
        steps.append([name, freed, ctx.total()])
        if ctx.total() <= WINDOW:
            break

    if ctx.total() > WINDOW:
        # Lớp cuối: bỏ tài liệu, rồi bỏ dần lượt cũ. System không bao giờ bị bỏ.
        while ctx.docs and ctx.total() > WINDOW:
            ctx.docs.pop()
        while len(ctx.history) > 2 and ctx.total() > WINDOW:
            ctx.history.pop(0)
        steps.append(["4. Bỏ tài liệu / lượt cũ", 0, ctx.total()])

    print("\nDIỄN BIẾN")
    print_table(["Bước", "Token giải phóng", "Còn lại"], steps, widths=[28, 17, 8])
    show(ctx, "SAU")

    if ctx.total() <= WINDOW:
        print(f"\n[done] Còn {WINDOW - ctx.total()} token trống. System prompt và các message gần nhất vẫn nguyên.")
    else:
        print("\n[warn] Vẫn vượt cửa sổ: cần giảm tool schema hoặc tách tác vụ.")


if __name__ == "__main__":
    main()
