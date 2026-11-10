"""Bài 06 — Kịch bản demo 10 phút.

Chạy:  python 06_demo_script.py

Demo tốt không phải demo nhiều tính năng. Nó là một câu chuyện có:
    vấn đề -> giải pháp -> bằng chứng -> thất bại có kiểm soát -> giới hạn.

File này in kịch bản và chạy ba câu hỏi thật để bạn đo trước.
Đừng đọc script trên sân khấu — hãy tập 2 lần và bỏ script đi.
"""

import time

from common.pipeline import answer

SCRIPT = [
    ("0:00–1:00", "Vấn đề",
     "Một khách hỏi chính sách. Nhân viên mất 4 phút tra 3 file. Agent mất 2 giây."),
    ("1:00–3:00", "Demo câu hỏi thật",
     "Hỏi 3 câu: một có dữ liệu, một cần từ chối, một của tenant khác."),
    ("3:00–5:00", "Kiến trúc",
     "Vẽ 4 hộp: API -> agent -> retrieval -> guard. Chỉ vào chỗ kiểm tra tenant."),
    ("5:00–7:00", "Bằng chứng",
     "Mở eval-report.md: 6/6 case, 5/5 có nguồn, p95, chi phí/tháng."),
    ("7:00–8:30", "Failure drill",
     "Tắt retrieval. Hệ thống trả 'degraded', không phải 500. Đây là điểm tin cậy."),
    ("8:30–10:00", "Giới hạn và bước tiếp",
     "Nói rõ chưa làm gì: chưa có auth thật, chưa có Postgres, eval còn 6 case."),
]

QUESTIONS = [
    ("Đổi trả trong bao nhiêu ngày?", "shop-a", "có dữ liệu"),
    ("Shop A có bán laptop không?", "shop-a", "phải từ chối"),
    ("Chính sách đổi trả của Shop B là gì?", "shop-b", "tenant khác"),
]


def check_environment() -> list[str]:
    checks = []
    try:
        result = answer("Đổi trả trong bao nhiêu ngày?", "shop-a")
        checks.append(f"pipeline: {result['status']} ({result['latency_ms']} ms)")
    except Exception as exc:  # noqa: BLE001
        checks.append(f"pipeline: LỖI {exc!r}")
    return checks


if __name__ == "__main__":
    print("=== Checklist trước khi demo ===")
    for line in check_environment():
        print(f"  [ ] {line}")
    print("  [ ] Mở sẵn eval-report.md ở tab khác")
    print("  [ ] Tắt thông báo, tắt Slack, để điện thoại im lặng")
    print("  [ ] Có bản ghi hình dự phòng nếu mạng hỏng")

    print("\n=== Kịch bản 10 phút ===")
    for timing, title, detail in SCRIPT:
        print(f"\n{timing}  {title}")
        print(f"          {detail}")

    print("\n=== Chạy thử ba câu demo ===")
    total = 0.0
    for question, tenant, note in QUESTIONS:
        started = time.perf_counter()
        result = answer(question, tenant)
        elapsed = (time.perf_counter() - started) * 1000
        total += elapsed

        print(f"\n  Hỏi: {question}  [{note}]")
        print(f"  -> [{result['status']}] {result['answer']}")
        if result["sources"]:
            print(f"     nguồn: {', '.join(s['source'] for s in result['sources'])}")
        print(f"     {elapsed:.1f} ms")

    print(f"\nTổng thời gian chạy ba câu: {total:.1f} ms.")
    print("\n=== Nếu demo hỏng ===")
    print("  1. Nói: 'phần này đang lỗi, mình có bản ghi ở đây' — đừng sửa live quá 30 giây.")
    print("  2. Chuyển sang eval-report.md. Bằng chứng vẫn còn.")
    print("  3. Kết thúc đúng giờ. Demo dài quá giờ tệ hơn demo ngắn.")
    print("\n  Câu chốt khi kết thúc:")
    print("  'Hệ thống này không phải agent thông minh nhất. Nó là agent mình")
    print("   biết đo, biết từ chối, và biết hỏng một cách tử tế.'")
