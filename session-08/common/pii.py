"""Phát hiện và che PII (thông tin định danh cá nhân).

Bốn loại được dạy trong buổi:
    email, số điện thoại Việt Nam, số CCCD (12 chữ số), số thẻ (16 chữ số).

Đây là bộ nhận dạng tối giản để học. Production nên dùng thêm thư viện như
Presidio, nhưng nguyên tắc vẫn vậy: phát hiện -> che -> chỉ giữ bản đã che.

Chạy thử nhanh:
    python -c "from common.pii import redact; print(redact('a@b.com 0912345678'))"
"""

import re
from dataclasses import dataclass

# Thứ tự trong alternation quan trọng: thẻ (16 số) phải đứng trước CCCD (12 số).
EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
CARD = r"(?<!\d)(?:\d{4}[ -]?){3}\d{4}(?!\d)"
CCCD = r"(?<!\d)\d{12}(?!\d)"
PHONE = r"(?<!\d)(?:\+84|0)[35789](?:[ .-]?\d){8}(?!\d)"

PATTERN = re.compile(
    rf"(?P<email>{EMAIL})|(?P<card>{CARD})|(?P<cccd>{CCCD})|(?P<phone>{PHONE})"
)
LABELS = {"email": "EMAIL", "card": "CARD", "cccd": "CCCD", "phone": "PHONE"}


@dataclass(frozen=True)
class Finding:
    kind: str
    value: str
    start: int
    end: int


def luhn_valid(number: str) -> bool:
    """Kiểm tra checksum của số thẻ; giảm nhầm lẫn với dãy số ngẫu nhiên."""
    digits = [int(ch) for ch in number if ch.isdigit()]
    if not digits:
        return False
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def detect(text: str) -> list[Finding]:
    """Trả về mọi PII tìm thấy, không chồng lấn nhau."""
    return [
        Finding(match.lastgroup or "", match.group(), match.start(), match.end())
        for match in PATTERN.finditer(text or "")
    ]


def mask_value(kind: str, value: str) -> str:
    """Bản rút gọn để hiển thị khi dạy — không dùng để ghi log thật."""
    if kind == "email":
        name, _, domain = value.partition("@")
        return f"{name[:2]}***@{domain}"
    digits = "".join(ch for ch in value if ch.isdigit())
    return f"***{digits[-3:]}"


def redact(text: str) -> str:
    """Thay từng PII bằng nhãn ổn định: [EMAIL_1], [PHONE_2]..."""
    if not text:
        return ""
    parts: list[str] = []
    last = 0
    counts: dict[str, int] = {}
    for finding in detect(text):
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
        label = f"[{LABELS[finding.kind]}_{counts[finding.kind]}]"
        parts.append(text[last:finding.start])
        parts.append(label)
        last = finding.end
    parts.append(text[last:])
    return "".join(parts)


def kinds(text: str) -> set[str]:
    """Tập loại PII có trong chuỗi — dùng cho test và metric."""
    return {finding.kind for finding in detect(text)}
