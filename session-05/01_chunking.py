"""Bài 01 — Chunking: cắt tài liệu trước khi nhúng.

Chạy:  python 01_chunking.py     (không cần API key)

Máy không đọc được cả tài liệu dài, nên ta cắt thành đoạn nhỏ. Cắt sai thì
retrieval sai, và mọi thứ phía sau đều sai theo.
"""

from common.knowledge import CHUNK_SIZE, DOCS, OVERLAP, chunk_text

print(f"Kích thước chunk: {CHUNK_SIZE} từ, chồng lấn {OVERLAP} từ\n")

for doc in DOCS:
    chunks = chunk_text(doc["text"])
    print(f"[{doc['tenant']}] {doc['source']} -> {len(chunks)} chunk")
    for i, chunk in enumerate(chunks):
        print(f"  chunk {i}: {len(chunk.split())} từ | {chunk[:70]}...")
    print()

print("=== Vì sao cần overlap? ===")
text = "Khách được đổi trả trong 7 ngày. Nếu tai nghe còn seal. Phí do khách chịu."
no_overlap = chunk_text(text, size=6, overlap=0)
with_overlap = chunk_text(text, size=6, overlap=2)
print("Không overlap:", no_overlap)
print("Có overlap:   ", with_overlap)
print()
print("Không overlap có thể cắt đôi 'tai nghe còn seal' và 'phí do khách chịu',")
print("khiến chunk chứa câu trả lời bị mất nửa sau.")
