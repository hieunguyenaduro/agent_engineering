"""Kho tri thức nhỏ cho buổi capstone.

Không phụ thuộc dịch vụ ngoài: token hoá đơn giản + cosine trên token count.
Đủ để chứng minh luồng retrieval; production thay bằng embedding thật.
"""

import math
import re

DOCS = [
    {
        "doc_id": "doi-tra",
        "tenant": "shop-a",
        "source": "chinh-sach-doi-tra.md",
        "text": (
            "Khách được đổi trả trong 7 ngày kể từ ngày nhận hàng nếu sản phẩm còn hộp "
            "và chưa qua sử dụng. Tai nghe phải còn nguyên seal. Phí vận chuyển đổi trả "
            "do khách chịu, trừ khi lỗi từ phía cửa hàng. Hoàn tiền trong 3 đến 5 ngày "
            "làm việc sau khi kho kiểm tra xong."
        ),
    },
    {
        "doc_id": "van-chuyen",
        "tenant": "shop-a",
        "source": "chinh-sach-van-chuyen.md",
        "text": (
            "Shop A giao hàng toàn quốc. Nội thành Hà Nội và TP.HCM giao trong 24 giờ. "
            "Các tỉnh khác từ 2 đến 4 ngày làm việc. Đơn trên 500 nghìn được miễn phí "
            "vận chuyển. Đơn hoả tốc có phụ phí 30 nghìn."
        ),
    },
    {
        "doc_id": "bao-hanh",
        "tenant": "shop-a",
        "source": "chinh-sach-bao-hanh.md",
        "text": (
            "Bảo hành 12 tháng cho bàn phím và 6 tháng cho tai nghe. Không bảo hành "
            "các trường hợp rơi vỡ, vào nước hoặc tự tháo. Thời gian xử lý bảo hành "
            "từ 7 đến 10 ngày làm việc."
        ),
    },
    {
        "doc_id": "doi-tra-b",
        "tenant": "shop-b",
        "source": "shop-b-doi-tra.md",
        "text": (
            "Shop B chỉ đổi trả trong 3 ngày và không hoàn tiền, chỉ đổi sản phẩm "
            "tương đương. Dữ liệu riêng của Shop B, không được lẫn với Shop A."
        ),
    },
]

STOPWORDS = {
    "và", "có", "là", "của", "cho", "trong", "khi", "thì", "được", "không", "một",
    "shop", "gì", "bao", "nhiêu", "nào", "sao",
}


class RetrievalError(RuntimeError):
    """Kho tri thức không sẵn sàng."""


def tokens(text: str) -> list[str]:
    return [
        word for word in re.findall(r"\w+", text.lower())
        if word not in STOPWORDS
    ]


def cosine(a: dict[str, int], b: dict[str, int]) -> float:
    common = set(a) & set(b)
    numerator = sum(a[word] * b[word] for word in common)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    return numerator / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in tokens(text):
        counts[word] = counts.get(word, 0) + 1
    return counts


def retrieve(
    question: str,
    tenant: str,
    k: int = 2,
    fail: str | None = None,
) -> list[dict]:
    """Tìm trong đúng tenant. `fail` dùng cho failure drill."""
    if fail == "retrieval_down":
        raise RetrievalError("dịch vụ tìm kiếm không phản hồi")
    if fail == "empty_index":
        return []

    query = _counts(question)
    hits = []
    for doc in DOCS:
        if doc["tenant"] != tenant:
            continue
        hits.append(
            {
                "doc_id": doc["doc_id"],
                "source": doc["source"],
                "text": doc["text"],
                "score": round(cosine(query, _counts(doc["text"])), 3),
            }
        )

    hits.sort(key=lambda item: item["score"], reverse=True)
    return hits[:k]
