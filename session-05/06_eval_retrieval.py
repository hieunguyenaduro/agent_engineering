"""Bài 06 — Đánh giá retrieval: hit rate và MRR.

Chạy:  python 06_eval_retrieval.py

Hai chỉ số đơn giản, đủ dùng để biết retrieval tốt lên hay tệ đi:

    Hit@k  = tỉ lệ câu hỏi có tài liệu đúng nằm trong k kết quả đầu
    MRR    = trung bình 1/rank của tài liệu đúng (đúng ở vị trí 1 -> 1.0)

Chỉ số chỉ đáng tin khi bộ câu hỏi đại diện cho câu hỏi thật của người dùng.
"""

from common.knowledge import build_index, search, use_real_embeddings

CASES = [
    ("Được đổi trả trong bao nhiêu ngày?", "doi-tra"),
    ("Giao hàng nội thành mất bao lâu?", "van-chuyen"),
    ("Tai nghe bảo hành mấy tháng?", "bao-hanh"),
    ("Đơn trên 500 nghìn có được miễn phí ship không?", "van-chuyen"),
    ("Đổi trả có mất phí vận chuyển không?", "doi-tra"),
]

client = build_index()


def evaluate(k: int):
    hits, rr = 0, 0.0
    print(f"\n=== Hit@{k} ===")
    for question, expected in CASES:
        results = search(client, question, tenant="shop-a", limit=k)
        ids = [hit.payload["doc_id"] for hit in results]
        if expected in ids:
            rank = ids.index(expected) + 1
            hits += 1
            rr += 1 / rank
            print(f"  ĐÚNG  rank {rank}  {question}")
        else:
            print(f"  TRƯỢT           {question}  (top: {ids[:k]})")
    return hits / len(CASES), rr / len(CASES)


if __name__ == "__main__":
    print("Chế độ:", "embedding thật" if use_real_embeddings() else "hash giả lập")
    for k in (1, 3):
        hit_rate, mrr = evaluate(k)
        print(f"  -> Hit@{k} = {hit_rate:.0%}   MRR = {mrr:.2f}")

    print("\nĐọc kết quả:")
    print("- Hit@1 thấp mà Hit@3 cao: tài liệu đúng có trong kho, nhưng xếp hạng chưa tốt.")
    print("- Cả hai đều thấp: vấn đề nằm ở chunking, embedding hoặc tài liệu thiếu.")
    print("- Ở chế độ hash, chỉ số thấp là bình thường: nó không hiểu từ đồng nghĩa.")
