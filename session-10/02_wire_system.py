"""Bài 02 — Nối hệ thống: một câu hỏi đi qua những đâu?

Chạy:  python 02_wire_system.py

Pipeline:
    question -> retrieve (lọc tenant) -> guard đủ dữ liệu -> chọn câu -> trả lời có nguồn
             -> đo token, chi phí, độ trễ, từng span

Đây là bản rút gọn của cả khóa: retrieval buổi 5, guard buổi 1–2,
quan sát buổi 7, và API buổi 9 chỉ là lớp bọc quanh hàm `answer()` này.
"""

from common.pipeline import answer

CASES = [
    ("Đổi trả trong bao nhiêu ngày?", "shop-a"),
    ("Giao hàng nội thành mất bao lâu?", "shop-a"),
    ("Shop A có bán laptop không?", "shop-a"),
    ("Chính sách đổi trả của Shop B là gì?", "shop-b"),
]

if __name__ == "__main__":
    results = []
    for question, tenant in CASES:
        result = answer(question, tenant)
        results.append(result)

        print(f"\n=== {question}  [tenant={tenant}]")
        print(f"  trạng thái : {result['status']}")
        print(f"  trả lời    : {result['answer']}")
        if result["sources"]:
            sources = ", ".join(f"{s['source']}({s['score']})" for s in result["sources"])
            print(f"  nguồn      : {sources}")
        print(f"  token      : {result['tokens']}  |  chi phí: ${result['cost_usd']:.8f}")
        print(f"  độ trễ     : {result['latency_ms']} ms")
        print("  trace:")
        for span in result["spans"]:
            print(f"    - {span['name']:9} {span['status']:8} {span['ms']:7.1f} ms  {span['detail']}")

    print("\n=== Kiểm tra cô lập tenant ===")
    shop_b = results[-1]
    leaked = [s["source"] for s in shop_b["sources"] if "shop-b" not in s["source"]]
    print("  nguồn của shop-b:", [s["source"] for s in shop_b["sources"]])
    print("  rò rỉ sang shop-a:", leaked or "không")

    refusals = [r for r in results if r["status"] == "refused"]
    print(f"\n{len(results)} câu hỏi, {len(refusals)} câu bị từ chối vì thiếu dữ liệu.")
    print("Từ chối đúng là hành vi tốt — miễn là nó nói rõ lý do và không bịa.")
