"""Ước lượng token và in bảng — dùng chung cho các ví dụ của buổi 4.

Ước lượng chars/4 là thô. Tiếng Việt thường tốn token hơn tiếng Anh cùng độ dài,
nên hãy coi con số ở đây là **sàn**, không phải hoá đơn thật. Muốn chính xác thì
dùng tokenizer của model bạn đang gọi.
"""

from math import ceil


def estimate_tokens(text: str) -> int:
    """Ước lượng nhanh: 4 ký tự ≈ 1 token."""
    if not text:
        return 0
    return max(1, ceil(len(text) / 4))


def message_tokens(message: dict) -> int:
    """Mỗi message có thêm vài token cho role và dấu phân cách."""
    return 4 + estimate_tokens(str(message.get("content", "")))


def bar(value: int, total: int, width: int = 22) -> str:
    """Thanh tỉ lệ bằng ký tự, để nhìn bằng mắt thay vì đọc số."""
    if total <= 0:
        return ""
    filled = min(width, round(width * value / total))
    return "█" * filled + "·" * (width - filled)


def print_table(headers, rows, widths=None) -> None:
    """In bảng ASCII, tự canh cột theo nội dung nếu không truyền widths."""
    rows = [[str(cell) for cell in row] for row in rows]
    if widths is None:
        widths = [
            max(len(str(headers[i])), *(len(row[i]) for row in rows))
            for i in range(len(headers))
        ]

    def line(left, mid, right):
        return left + mid.join("─" * (w + 2) for w in widths) + right

    def render(cells):
        return "│" + "│".join(f" {c:<{w}} " for c, w in zip(cells, widths)) + "│"

    print(line("┌", "┬", "┐"))
    print(render(headers))
    print(line("├", "┼", "┤"))
    for row in rows:
        print(render(row))
    print(line("└", "┴", "┘"))


def shorten(text: str, limit: int = 120) -> str:
    """Cắt bớt nhưng để lại dấu ... để người đọc biết đã mất dữ liệu."""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."
