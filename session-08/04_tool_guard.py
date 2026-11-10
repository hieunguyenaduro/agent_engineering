"""Bài 04 — Guard cho tool: quyền, rate limit, phê duyệt, SSRF, audit.

Chạy: python 04_tool_guard.py

Điều cần nhớ: model chỉ **đề nghị** gọi tool. Guard quyết định có chạy hay
không, dựa trên danh tính và quyền của người dùng — không dựa vào lời model.
"""

import json
import os
import tempfile
from pathlib import Path

from common.demo_tools import SUPPORT, build_guard
from common.guards import check_output
from common.tool_guard import ApprovalRequired, ToolDenied

SECRET = os.getenv("FAKE_API_KEY", "sk-demo-SECRET-123")


def attempt(label: str, fn):
    try:
        result = fn()
        print(f"[allow] {label}: {result}")
    except ApprovalRequired as exc:
        print(f"[wait ] {label}: {exc}")
    except ToolDenied as exc:
        print(f"[block] {label}: {exc}")


def main() -> None:
    log_path = Path(tempfile.mkdtemp()) / "audit.jsonl"
    guard, audit = build_guard(audit_path=log_path, search_limit=2)

    print("### 1. Quyền theo capability")
    attempt("đọc đơn", lambda: guard.call(
        SUPPORT, "search_orders", {"query": "đơn 1234"}))
    attempt("xoá khách", lambda: guard.call(
        SUPPORT, "delete_customer", {"customer_id": "c-9"}))

    print("\n### 2. Rate limit (2 lần / 60 giây; mục 1 đã dùng 1)")
    for i in range(3):
        attempt(f"tra cứu lần {i + 1}", lambda i=i: guard.call(
            SUPPORT, "search_orders", {"query": f"đơn {i}"}))

    print("\n### 3. Tool nguy hiểm cần phê duyệt")
    refund_args = {"order_id": "1234", "amount": 250_000}
    attempt("hoàn tiền không duyệt", lambda: guard.call(
        SUPPORT, "refund", refund_args))

    token = guard.human_approve("refund", refund_args, approver="supervisor")
    print(f"[human] đã duyệt, token={token}")
    attempt("hoàn tiền có duyệt", lambda: guard.call(
        SUPPORT, "refund", refund_args, approval=token))
    attempt("dùng lại token cũ", lambda: guard.call(
        SUPPORT, "refund", refund_args, approval=token))

    print("\n### 4. SSRF: chỉ https, đúng host, không IP nội bộ")
    for url in (
        "https://api.shop.example/orders/1234",
        "http://169.254.169.254/latest/meta-data",
        "https://evil.example/collect",
        "https://api.shop.example@evil.example/",
    ):
        attempt(url, lambda url=url: guard.call(
            SUPPORT, "fetch_url", {"url": url}))

    print("\n### 5. Lọc đầu ra trước khi trả cho người dùng")
    leaky = f"Kết quả: key={SECRET}; khách gửi từ an@example.com"
    verdict = check_output(leaky, secrets=(SECRET,))
    print(f"[block] ok={verdict.ok} lý do={verdict.reason}")
    print(f"[safe]  {verdict.text}")

    print(f"\n### 6. Audit trail ({log_path})")
    for entry in audit.entries()[-8:]:
        brief = {key: entry[key] for key in ("action", "tool", "outcome")}
        print("  " + json.dumps(brief, ensure_ascii=False))

    print("\nBài học: quyền kiểm tra ở guard, không ở prompt.")
    print("Audit cho biết ai đã làm gì; token duyệt dùng một lần.")


if __name__ == "__main__":
    main()
