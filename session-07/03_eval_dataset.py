"""Bài 03 — Tạo và kiểm tra eval dataset.

Chạy:  python 03_eval_dataset.py

File này tạo evals/cases.jsonl nếu chưa có, đọc lại, validate schema rồi in bảng.
Dataset là tài sản của sản phẩm: thêm case mới là thêm một yêu cầu đã được kiểm
chứng, không phải thêm một dòng test cho có.
"""

from collections import Counter

from common.dataset import CASES_PATH, ensure_cases, load_cases, validate


def print_table(cases: list[dict]) -> None:
    print(f"{'ID':<20} {'Tool bắt buộc':<22} {'Tags':<22} Input")
    print("-" * 100)
    for case in cases:
        tool = case.get("must_call_tool") or "-"
        tags = ", ".join(case["tags"])
        print(f"{case['id']:<20} {tool:<22} {tags:<22} {case['input']}")


if __name__ == "__main__":
    created = ensure_cases()
    print(f"{'Đã tạo' if created else 'Đang đọc'} {CASES_PATH}\n")

    try:
        cases = load_cases()
    except (OSError, ValueError) as exc:
        print(f"Không đọc được dataset: {exc}")
        raise SystemExit(1)

    errors = validate(cases)
    if errors:
        print(f"Dataset KHÔNG hợp lệ ({len(errors)} lỗi):")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print(f"Hợp lệ: {len(cases)} case\n")
    print_table(cases)

    counts = Counter(tag for case in cases for tag in case["tags"])
    print("\nPhân bố theo tag:")
    for tag, count in sorted(counts.items()):
        print(f"  {tag:<16} {count}")

    tools = Counter(case["must_call_tool"] for case in cases if case["must_call_tool"])
    print("\nCase bắt buộc gọi tool:")
    for tool, count in sorted(tools.items()):
        print(f"  {tool:<22} {count}")

    print("\nNhắc lại: mỗi case phải đến từ yêu cầu sản phẩm hoặc một lỗi thật đã gặp.")
    print("Đừng bịa case cho đủ số lượng — dataset rác sẽ tạo cảm giác an toàn giả.")
