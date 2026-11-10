"""Bài 02 — Embedding: biến chữ thành vector.

Chạy:  python 02_embeddings.py

Có key: dùng embedding thật của OpenAI (hiểu được từ đồng nghĩa).
Không key: dùng embedding giả bằng hash (chỉ khớp theo từ khoá).

Bài học: embedding thật và embedding giả cho kết quả khác nhau rất nhiều.
Đừng đánh giá retrieval bằng chế độ giả.
"""

import numpy as np

from common.knowledge import embed_one, embed_texts, use_real_embeddings

print("Chế độ:", "OpenAI embedding" if use_real_embeddings() else "hash giả lập (không có key)")
print()

sentences = [
    "Chính sách đổi trả trong 7 ngày",
    "Khách được trả hàng trong vòng một tuần",
    "Thời tiết Hà Nội hôm nay nhiều mây",
]


def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


vectors = embed_texts(sentences)

print(f"{'':50} {'câu 1':>8} {'câu 2':>8} {'câu 3':>8}")
for i, sentence in enumerate(sentences):
    scores = [f"{cosine(vectors[i], vectors[j]):.3f}" for j in range(3)]
    print(f"{sentence[:48]:50} {scores[0]:>8} {scores[1]:>8} {scores[2]:>8}")

print()
if use_real_embeddings():
    print("Câu 1 và câu 2 gần nhau dù khác từ — đó là điểm mạnh của embedding thật.")
else:
    print("Câu 1 và câu 2 gần nhau vì trùng từ 'trong', 'ngày' — không phải vì hiểu nghĩa.")
    print("Đây là giới hạn của chế độ giả lập: từ đồng nghĩa sẽ trượt.")

print()
print("=== Vector trông như thế nào? ===")
vector = embed_one(sentences[0])
print(f"Số chiều: {len(vector)}")
print(f"10 giá trị đầu: {[round(x, 3) for x in vector[:10]]}")
