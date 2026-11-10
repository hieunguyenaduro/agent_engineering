"""Bài 04 — Bốn evaluator deterministic chạy trên agent giả.

Chạy:  python 04_code_evaluators.py

Bốn tầng kiểm tra khác nhau, cùng một bộ case:
    contains   — tầng end-to-end: câu trả lời có đúng thông tin?
    must_tool  — tầng tool use: có gọi đúng tool?
    forbidden  — tầng trajectory: có đi qua tool cấm?
    latency    — ngân sách thời gian.

Cuối file chạy ba scenario cố tình hỏng để chứng minh evaluator bắt được lỗi.
"""

from common.agent import run_agent
from common.dataset import ensure_cases, load_cases
from common.evaluators import EVALUATORS, evaluate_case

CHECKS = [name for name, _ in EVALUATORS]
DEMOS = [
    ("skip_tool", "order-status-1234"),
    ("unsafe_refund", "refund-guard"),
    ("slow", "order-status-5678"),
]


def mark(checks: dict, name: str) -> str:
    return "PASS" if checks[name][0] else "FAIL"


if __name__ == "__main__":
    ensure_cases()
    cases = load_cases()
    rows = []

    for case in cases:
        result = run_agent(case["input"])
        passed, checks, failed = evaluate_case(case, result)
        rows.append((case, result, passed, checks, failed))

    header = f"{'Case':<22} {'contains':<9} {'must_tool':<10} {'forbidden':<10} {'latency':<8} Kết quả"
    print(header)
    print("-" * len(header))
    for case, result, passed, checks, _ in rows:
        marks = " ".join(f"{mark(checks, name):<9}" for name in CHECKS)
        print(f"{case['id']:<22} {marks} {'PASS' if passed else 'FAIL'}")
        print(f"{'':<22} → {result.answer[:70]}")

    passed_count = sum(1 for _, _, passed, _, _ in rows if passed)
    print(f"\nKết quả: {passed_count}/{len(rows)} case đạt cả bốn evaluator.")

    failures = [(case["id"], name, checks[name][1]) for case, _, _, checks, failed in rows for name in failed]
    if failures:
        print("\nChi tiết lỗi:")
        for case_id, name, reason in failures:
            print(f"  - {case_id} / {name}: {reason}")

    print("\n--- Phá agent để xem evaluator có bắt được không ---")
    by_id = {case["id"]: case for case in cases}
    for scenario, case_id in DEMOS:
        case, result = by_id[case_id], run_agent(by_id[case_id]["input"], scenario=scenario)
        _, _, failed = evaluate_case(case, result)
        verdict = "BẮT ĐƯỢC" if failed else "KHÔNG BẮT ĐƯỢC"
        print(f"{scenario:<14} {case_id:<22} {verdict:<16} {', '.join(failed) or '-'}")

    print("\nunsafe_refund vẫn qua 'contains' vì câu trả lời có chữ “không thể”;")
    print("chỉ evaluator trajectory bắt được hành động sai. Vì vậy phải chấm nhiều tầng.")
    print("\nEvaluator deterministic rẻ và nhanh, nhưng không chấm được giọng điệu.")
    print("Phần đó để bài 05 — LLM-as-judge.")
