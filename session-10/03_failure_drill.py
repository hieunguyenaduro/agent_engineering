"""Bài 03 — Failure drill: tắt từng phụ thuộc và xem hệ thống phản ứng.

Chạy:  python 03_failure_drill.py

Năm kịch bản:
    1. normal         — mọi thứ bình thường
    2. retrieval_down — dịch vụ tìm kiếm chết
    3. empty_index    — kho rỗng (deploy lỗi, chưa nạp dữ liệu)
    4. slow_model     — model chậm gấp nhiều lần
    5. model_error    — model trả 500

Mục tiêu không phải "không bao giờ lỗi". Mục tiêu là: lỗi nào cũng có
câu trả lời an toàn, có trạng thái rõ, và không làm sập process.
"""

import time

from common.pipeline import answer

DRILLS = [
    ("normal", None, "hệ thống bình thường"),
    ("retrieval_down", "retrieval_down", "dịch vụ tìm kiếm chết"),
    ("empty_index", "empty_index", "kho dữ liệu rỗng"),
    ("slow_model", "slow_model", "model phản hồi chậm"),
    ("model_error", "model_error", "model trả lỗi 500"),
]

QUESTION = "Đổi trả trong bao nhiêu ngày?"

if __name__ == "__main__":
    print(f"Câu hỏi drill: {QUESTION}\n")
    print(f"{'kịch bản':16} {'trạng thái':10} {'ms':>7}  câu trả lời")
    print("-" * 88)

    rows = []
    for name, fail, description in DRILLS:
        started = time.perf_counter()
        try:
            result = answer(QUESTION, "shop-a", fail=fail)
            crashed = False
        except Exception as exc:  # drill phải chứng minh không có exception
            crashed = True
            result = {"status": "CRASH", "latency_ms": 0, "answer": repr(exc), "spans": []}
        elapsed_ms = (time.perf_counter() - started) * 1000

        rows.append((name, result, crashed, elapsed_ms))
        short = result["answer"][:52] + ("..." if len(result["answer"]) > 52 else "")
        print(f"{name:16} {result['status']:10} {elapsed_ms:7.1f}  {short}")
        print(f"{'':16} ({description})")

    print("\n=== Kiểm tra ===")
    crashed_count = sum(1 for _, _, crashed, _ in rows if crashed)
    safe_count = sum(
        1 for _, result, _, _ in rows
        if result["status"] in {"ok", "refused", "degraded", "error"} and result["answer"]
    )
    print(f"  crash              : {crashed_count}/5")
    print(f"  có câu trả lời an toàn: {safe_count}/5")

    slow = next(row for row in rows if row[0] == "slow_model")
    normal = next(row for row in rows if row[0] == "normal")
    print(f"  chậm hơn bình thường : {slow[3] / max(normal[3], 0.001):.0f}× "
          f"({slow[3]:.0f} ms vs {normal[3]:.0f} ms)")

    print("\nĐiều đáng chú ý:")
    print("- retrieval_down trả 'degraded', không phải 500. Người dùng biết phải thử lại.")
    print("- empty_index trả 'refused'. Hệ thống không bịa khi kho rỗng.")
    print("- slow_model vẫn trả 'ok', nhưng p95 sẽ xấu. Cần timeout + báo tiến độ.")
    print("- Không có dòng nào là crash. Đó là tiêu chí của buổi học này.")
