"""Bài 03 — Qdrant: lưu vector và tìm kiếm.

Chạy:  python 03_qdrant_basic.py

Qdrant ở đây chạy trong RAM, không cần Docker. Khi lên production chỉ đổi
location thành URL của server.
"""

from common.knowledge import build_index, search, use_real_embeddings

print("Đang tạo index...", "bằng embedding thật" if use_real_embeddings() else "bằng hash giả lập")
client = build_index()

queries = [
    "Được đổi trả trong bao nhiêu ngày?",
    "Giao hàng nội thành mất mấy giờ?",
    "Tai nghe bảo hành bao lâu?",
]

for query in queries:
    print(f"\n=== {query} ===")
    hits = search(client, query, tenant="shop-a", limit=3)
    for hit in hits:
        payload = hit.payload
        print(f"  {hit.score:.3f}  {payload['source']} (chunk {payload['chunk_index']})")
        print(f"         {payload['text'][:80]}...")

print()
print("Điểm score là độ tương đồng cosine: càng gần 1 càng giống.")
print("Điểm cao không có nghĩa là câu trả lời đúng — chỉ là đoạn văn giống câu hỏi.")
