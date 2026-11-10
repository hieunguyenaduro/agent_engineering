"""Kho tri thức nhỏ + các hàm dùng chung cho buổi 5.

Chạy được theo hai chế độ:
    - có OPENAI_API_KEY: embedding thật (text-embedding-3-small)
    - không có key:      embedding giả bằng hash từ, đủ để thấy luồng chạy
"""

import hashlib
import os
import re

import numpy as np

DOCS = [
    {
        "doc_id": "doi-tra",
        "tenant": "shop-a",
        "source": "chinh-sach-doi-tra.md",
        "text": (
            "Chính sách đổi trả của Shop A. Khách được đổi trả trong 7 ngày kể từ "
            "ngày nhận hàng nếu sản phẩm còn hộp và chưa qua sử dụng. Tai nghe phải "
            "còn nguyên seal. Phí vận chuyển đổi trả do khách chịu, trừ khi lỗi từ "
            "phía cửa hàng."
        ),
    },
    {
        "doc_id": "van-chuyen",
        "tenant": "shop-a",
        "source": "chinh-sach-van-chuyen.md",
        "text": (
            "Shop A giao hàng toàn quốc. Nội thành Hà Nội và TP.HCM giao trong 24 "
            "giờ. Các tỉnh khác từ 2 đến 4 ngày làm việc. Đơn trên 500 nghìn được "
            "miễn phí vận chuyển. Đơn hoả tốc có phụ phí 30 nghìn."
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
        "doc_id": "quy-trinh-doi-tra",
        "tenant": "shop-a",
        "source": "quy-trinh-doi-tra.md",
        "text": (
            "Quy trình đổi trả của Shop A gồm bốn bước. Bước một, khách mở trang đơn "
            "hàng và chọn sản phẩm muốn đổi trả, sau đó chọn lý do từ danh sách có sẵn. "
            "Bước hai, hệ thống kiểm tra thời hạn đổi trả: bảy ngày với sản phẩm thường, "
            "ba ngày với sản phẩm khuyến mại, và không áp dụng với sản phẩm đã bóc seal. "
            "Bước ba, khách gửi hàng về kho theo địa chỉ hệ thống cung cấp; khách có thể "
            "chọn gửi qua bưu điện hoặc mang trực tiếp đến cửa hàng. Bước bốn, kho kiểm "
            "tra tình trạng sản phẩm trong hai ngày làm việc. Nếu sản phẩm đủ điều kiện, "
            "Shop A hoàn tiền vào phương thức thanh toán ban đầu trong ba đến năm ngày "
            "làm việc, hoặc gửi sản phẩm đổi tương đương nếu khách chọn đổi hàng. Trường "
            "hợp sản phẩm không đủ điều kiện, bộ phận chăm sóc khách hàng gọi điện giải "
            "thích và gửi lại sản phẩm cho khách, khách chịu phí vận chuyển hai chiều. "
            "Mọi yêu cầu đổi trả đều được ghi mã ticket để khách theo dõi. Khách có thể "
            "khiếu nại trong bảy ngày kể từ ngày nhận kết quả xử lý. Khiếu nại được "
            "chuyển tới quản lý cửa hàng và phản hồi trong ba ngày làm việc."
        ),
    },
    {
        "doc_id": "doi-tra-b",
        "tenant": "shop-b",
        "source": "shop-b-doi-tra.md",
        "text": (
            "Shop B chỉ đổi trả trong 3 ngày và không hoàn tiền, chỉ đổi sản phẩm "
            "tương đương. Đây là dữ liệu riêng của Shop B, không được lẫn với Shop A."
        ),
    },
]

CHUNK_SIZE = 60
OVERLAP = 15
HASH_DIM = 256
OPENAI_DIM = 1536


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Cắt theo từ, có phần chồng lên nhau để không mất ngữ cảnh ở ranh giới."""
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        piece = " ".join(words[start:start + size])
        chunks.append(piece)
        if start + size >= len(words):
            break
        start += size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------
def use_real_embeddings() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def embedding_dim() -> int:
    return OPENAI_DIM if use_real_embeddings() else HASH_DIM


def hash_embed(text: str, dim: int = HASH_DIM) -> list[float]:
    """Embedding giả: đếm từ rồi băm vào các chiều. Chỉ khớp được theo từ khoá."""
    vector = np.zeros(dim, dtype=np.float32)
    for word in re.findall(r"\w+", text.lower()):
        digest = hashlib.md5(word.encode()).hexdigest()
        vector[int(digest[:8], 16) % dim] += 1.0
    norm = np.linalg.norm(vector)
    return (vector / norm if norm else vector).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if use_real_embeddings():
        from openai import OpenAI

        response = OpenAI().embeddings.create(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            input=texts,
        )
        return [item.embedding for item in response.data]
    return [hash_embed(text) for text in texts]


def embed_one(text: str) -> list[float]:
    return embed_texts([text])[0]


# ---------------------------------------------------------------------------
# Qdrant
# ---------------------------------------------------------------------------
COLLECTION = "knowledge"


def build_index():
    """Tạo Qdrant trong RAM và nạp toàn bộ tài liệu đã cắt nhỏ."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    client = QdrantClient(location=":memory:")
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=embedding_dim(), distance=Distance.COSINE),
    )

    points, point_id = [], 0
    for doc in DOCS:
        for i, chunk in enumerate(chunk_text(doc["text"])):
            point_id += 1
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embed_one(chunk),
                    payload={
                        "doc_id": doc["doc_id"],
                        "tenant": doc["tenant"],
                        "source": doc["source"],
                        "chunk_index": i,
                        "text": chunk,
                    },
                )
            )

    client.upsert(COLLECTION, points=points)
    return client


def search(client, query: str, tenant: str, limit: int = 3):
    """Tìm kiếm có lọc theo tenant — lọc ở tầng dữ liệu, không phải ở prompt."""
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    query_filter = Filter(
        must=[FieldCondition(key="tenant", match=MatchValue(value=tenant))]
    )
    vector = embed_one(query)

    try:  # qdrant-client mới
        result = client.query_points(
            COLLECTION,
            query=vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
        return result.points
    except AttributeError:  # bản cũ
        return client.search(
            COLLECTION,
            query_vector=vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
