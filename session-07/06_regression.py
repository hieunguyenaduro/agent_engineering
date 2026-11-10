"""Bài 06 — Regression: chặn merge khi chất lượng tụt.

Chạy:  python 06_regression.py
       python 06_regression.py --update-baseline
       python 06_regression.py --break          # cố tình làm agent hỏng để xem exit code

So sánh từng case với evals/baseline.json. Case từng PASS mà nay FAIL là
regression: in bảng delta và thoát với mã 1 để CI chặn merge.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from common.agent import run_agent
from common.dataset import CASES_PATH, ensure_cases, load_cases
from common.evaluators import evaluate_case

BASELINE = Path(__file__).parent / "evals" / "baseline.json"


def evaluate_all(scenario: str = "normal") -> dict[str, dict]:
    rows = {}
    for case in load_cases():
        result = run_agent(case["input"], scenario=scenario)
        passed, _, failed = evaluate_case(case, result)
        rows[case["id"]] = {"passed": passed, "failed": failed}
    return rows


def update_baseline(rows: dict[str, dict], scenario: str) -> None:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scenario": scenario,
        "cases": rows,
    }
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã ghi baseline {len(rows)} case vào {BASELINE}")
    print("Commit file này để cả nhóm và CI so với cùng một mốc.")


def main() -> int:
    args = set(sys.argv[1:])
    scenario = "skip_tool" if "--break" in args else "normal"
    ensure_cases()
    now = evaluate_all(scenario)
    print(f"Đã chạy {len(now)} case với scenario='{scenario}' ({CASES_PATH.name}).\n")

    if "--update-baseline" in args:
        if scenario != "normal":
            print("Từ chối cập nhật baseline từ scenario cố tình hỏng. Bỏ --break rồi chạy lại.")
            return 2
        update_baseline(now, scenario)
        return 0

    if not BASELINE.exists():
        print(f"Chưa có {BASELINE.name}. Tạo mốc đầu tiên bằng:")
        print("  python 06_regression.py --update-baseline")
        print("Sau đó chạy lại không tham số để so sánh.")
        return 0

    baseline = json.loads(BASELINE.read_text(encoding="utf-8")).get("cases", {})
    header = f"{'Case':<24} {'Baseline':<10} {'Bây giờ':<10} Delta"
    print(header)
    print("-" * len(header))
    regressions, fixes = [], []
    for case_id, row in now.items():
        before = baseline.get(case_id, {}).get("passed")
        after = row["passed"]
        if before is True and not after:
            delta, regressions = "TỤT", regressions + [case_id]
        elif before is False and after:
            delta, fixes = "LÊN", fixes + [case_id]
        elif before is None:
            delta = "MỚI"
        else:
            delta = "="
        before_text = "?" if before is None else ("PASS" if before else "FAIL")
        print(f"{case_id:<24} {before_text:<10} {'PASS' if after else 'FAIL':<10} {delta}")

    for case_id in regressions:
        print(f"  ! {case_id} hỏng: {', '.join(now[case_id]['failed'])}")
    if fixes:
        print(f"\nCase được sửa: {', '.join(fixes)}")

    if regressions:
        print(f"\nREGRESSION: {len(regressions)} case từng PASS nay FAIL. Chặn merge (exit 1).")
        return 1
    print("\nKhông có regression. Được phép merge (exit 0).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
