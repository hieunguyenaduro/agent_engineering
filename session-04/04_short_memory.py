"""04 — Memory ngắn hạn: hội thoại dài thì nén phần cũ, giữ facts quan trọng.

Chạy: python 04_short_memory.py
Không gọi model. Hàm tóm tắt ở đây là bản offline, cố tình đơn giản để bạn nhìn thấy
cái gì được giữ và cái gì bị mất.
"""

import re

from common.tokens import estimate_tokens, print_table, shorten

LIMIT = 130          # ngưỡng token của cả context
KEEP_RECENT = 2      # số message gần nhất không bao giờ nén
SYSTEM = (
    "Bạn là trợ lý SoundHouse. Trả lời ngắn, bằng tiếng Việt. "
    "Luôn xưng tên khách nếu biết. Không bịa mã đơn."
)

TURNS = [
    ("user", "Chào bạn, mình tên Minh. Mình đang dùng tai nghe SoundMax X2 mua ở shop."),
    ("assistant", "Chào Minh, mình có thể giúp gì cho chiếc tai nghe SoundMax X2 của bạn?"),
    ("user", "Đơn của mình là 1234, đặt hôm 12/10. Số điện thoại 0909 123 456."),
    ("assistant", "Cảm ơn Minh. Mình thấy đơn 1234 đã giao. Bạn đang gặp vấn đề gì?"),
    ("user", "Tai nghe bị rè ở tai trái sau 3 ngày. Mình muốn đổi màu trắng nếu còn hàng."),
    ("assistant", "Lỗi nhà sản xuất trong 7 ngày được đổi mới. Màu trắng còn 3 chiếc ở quận 1."),
    ("user", "Ngân sách mình khoảng 500.000đ. Nếu đổi được thì giữ hàng giúp mình."),
    ("assistant", "Mình đã giữ một chiếc màu trắng đến 18h mai. Mã giữ hàng GH-7788."),
    ("user", "Mình thích được trả lời bằng tiếng Việt. Mai mình ghé lấy, nhớ gọi trước."),
    ("assistant", "Dạ, mai mình gọi trước khi bạn đến. Bạn nhớ mang hộp và phụ kiện."),
]

PATTERNS = {
    "tên": r"tên (\w+)",
    "đơn": r"đơn (?:của mình là )?(\d{3,})",
    "sản phẩm": r"(tai nghe|loa|bàn phím)",
    "điện thoại": r"(0\d{3} \d{3} \d{3})",
    "ngân sách": r"(\d{3}\.\d{3})đ",
    "ngôn ngữ": r"tiếng (Việt|Anh)",
}


def extract_facts(text: str) -> dict:
    """Trích facts bằng regex. Thật ra nên để model làm, nhưng nguyên tắc thì giống."""
    found = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found[key] = match.group(1) if match.groups() else match.group(0)
    return found


def build_summary(facts: dict) -> str:
    if not facts:
        return ""
    body = "; ".join(f"{key}={value}" for key, value in facts.items())
    return f"Tóm tắt: {body}. Các chi tiết khác đã lược."


class ShortMemory:
    def __init__(self):
        self.messages = []
        self.facts = {}
        self.summary = ""
        self.compactions = 0
        self.snapshots = []

    def tokens(self) -> int:
        return (
            estimate_tokens(SYSTEM)
            + estimate_tokens(self.summary)
            + sum(estimate_tokens(m["content"]) for m in self.messages)
        )

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        # Trích facts ngay khi có message. Giữ giá trị đầu tiên; muốn cập nhật
        # thì phải có quy tắc rõ ràng, đừng để message sau ghi đè âm thầm.
        for key, value in extract_facts(content).items():
            self.facts.setdefault(key, value)

    def compact(self) -> bool:
        if self.tokens() <= LIMIT:
            return False
        before = self.tokens()
        old, self.messages = self.messages[:-KEEP_RECENT], self.messages[-KEEP_RECENT:]
        self.summary = build_summary(self.facts)
        self.compactions += 1
        self.snapshots.append((before, self.tokens(), len(old), dict(self.facts)))
        return True

    def render(self) -> str:
        parts = [f"[system]\n{SYSTEM}"]
        if self.summary:
            parts.append(f"[summary]\n{self.summary}")
        parts += [f"[{m['role']}]\n{m['content']}" for m in self.messages]
        return "\n\n".join(parts)


def main():
    memory = ShortMemory()
    for role, content in TURNS:
        memory.add(role, content)
        before = memory.tokens()
        if memory.compact():
            after, count = memory.tokens(), memory.snapshots[-1][2]
            print(f"[compact] {before} → {after} token, nén {count} message cũ, "
                  f"giữ {len(memory.messages)} message gần nhất")

    full = estimate_tokens(SYSTEM) + sum(estimate_tokens(t) for _, t in TURNS)
    print(f"\n[before] Nếu gửi toàn bộ hội thoại: {full} token / {len(TURNS)} message")
    print(f"[after ] Context hiện tại: {memory.tokens()} token / {len(memory.messages)} message")
    print(f"[facts ] {memory.facts}")
    print(f"[cost  ] Đã nén {memory.compactions} lần, tiết kiệm {full - memory.tokens()} token.")

    print("\n[context sau khi nén]")
    print(memory.render())

    rows = []
    for i, (before, after, count, facts) in enumerate(memory.snapshots, 1):
        rows.append([i, count, before, after, f"{len(facts)} facts"])
    if rows:
        print()
        print_table(["Lần nén", "Message bị nén", "Token trước", "Token sau", "Facts giữ"],
                    rows, widths=[8, 15, 12, 10, 10])

    print("\n[done] Tóm tắt giữ được facts, nhưng mất chi tiết thô. Chi tiết nào quan trọng")
    print("       thì phải nằm trong facts, đừng trông vào trí nhớ của bản tóm tắt.")


if __name__ == "__main__":
    main()
