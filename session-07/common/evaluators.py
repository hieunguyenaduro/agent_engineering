"""Bốn evaluator deterministic — chạy nhanh, không tốn token, không gọi mạng.

Mỗi evaluator nhận (case, result) và trả về (đạt?, lý do). Nhờ cùng một chữ ký,
bài 06 có thể chạy lại toàn bộ và so với baseline.
"""

from __future__ import annotations

from common.agent import RunResult


def eval_contains(case: dict, result: RunResult) -> tuple[bool, str]:
    """Tầng end-to-end: câu trả lời có chứa các chuỗi bắt buộc không?"""
    missing = [text for text in case["expected_contains"] if text.lower() not in result.answer.lower()]
    if missing:
        return False, "thiếu: " + ", ".join(missing)
    return True, "đủ chuỗi bắt buộc"


def eval_must_call(case: dict, result: RunResult) -> tuple[bool, str]:
    """Tầng tool use: agent có gọi đúng tool cần thiết không?"""
    required = case.get("must_call_tool")
    if not required:
        return True, "không bắt buộc tool"
    if required in result.tool_calls:
        return True, f"đã gọi {required}"
    called = ", ".join(result.tool_calls) if result.tool_calls else "không gọi tool nào"
    return False, f"thiếu {required} ({called})"


def eval_forbidden(case: dict, result: RunResult) -> tuple[bool, str]:
    """Tầng trajectory: có đi qua tool bị cấm không, dù câu trả lời đúng?"""
    forbidden = [name for name in case.get("forbidden_tools", []) if name in result.tool_calls]
    if forbidden:
        return False, "đã gọi tool cấm: " + ", ".join(forbidden)
    return True, "không gọi tool cấm"


def eval_latency(case: dict, result: RunResult) -> tuple[bool, str]:
    """Ngân sách thời gian: chậm quá thì người dùng bỏ đi trước khi thấy câu trả lời."""
    limit = case.get("max_latency_ms", 250)
    if result.latency_ms <= limit:
        return True, f"{result.latency_ms:.0f}ms / {limit}ms"
    return False, f"{result.latency_ms:.0f}ms vượt {limit}ms"


EVALUATORS = [
    ("contains", eval_contains),
    ("must_tool", eval_must_call),
    ("forbidden", eval_forbidden),
    ("latency", eval_latency),
]


def evaluate_case(case: dict, result: RunResult) -> tuple[bool, dict[str, tuple[bool, str]], list[str]]:
    """Chạy cả bốn evaluator, trả về kết quả tổng và tên các check fail."""
    checks = {name: function(case, result) for name, function in EVALUATORS}
    failed = [name for name, (ok, _) in checks.items() if not ok]
    return not failed, checks, failed
