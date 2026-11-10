"""Bài 06 — Biến mỗi cuộc tấn công thành một test.

Chạy không cần pytest:
    python 06_security_tests.py

Chạy bằng pytest:
    pytest -q test_security.py
    pytest -q 06_security_tests.py      # pytest thu cả test được import

Vì sao làm thế này: một lỗ hổng đã sửa mà không có test sẽ quay lại. Mỗi test
dưới đây là một cuộc tấn công cụ thể, chạy trong vài giây, không tốn token.
"""

import sys

from test_security import TESTS
# pytest chỉ thu các hàm test_* nằm trong namespace của module được chỉ định.
# Star import đưa chúng vào đây để `pytest -q 06_security_tests.py` cũng chạy.
from test_security import *  # noqa: F401,F403

ATTACKS = {
    "test_direct_injection_is_blocked":
        "người dùng gõ 'bỏ qua hướng dẫn'",
    "test_indirect_injection_is_treated_as_data":
        "chỉ thị độc giấu trong tài liệu RAG",
    "test_spotlight_cannot_be_escaped":
        "đóng thẻ </untrusted> giả để thoát vùng dữ liệu",
    "test_pii_is_redacted":
        "email, điện thoại, CCCD, thẻ lọt vào prompt",
    "test_audit_never_stores_secrets_or_raw_pii":
        "API key và PII lọt vào log",
    "test_tool_outside_capability_is_denied":
        "model gọi tool xoá khách ngoài quyền",
    "test_tool_rate_limit_is_enforced":
        "gọi tool liên tục để dò dữ liệu",
    "test_dangerous_tool_needs_human_approval":
        "hoàn tiền không có người duyệt",
    "test_ssrf_to_metadata_and_unknown_host_is_blocked":
        "SSRF tới metadata cloud và host lạ",
    "test_tenant_a_cannot_read_tenant_b":
        "công ty A đọc tài liệu công ty B",
    "test_tenant_id_in_payload_is_rejected":
        "đổi tenant_id trong body request",
    "test_memory_is_isolated_by_tenant":
        "memory của B bị A đọc",
    "test_output_filter_blocks_secret":
        "API key lọt vào câu trả lời",
    "test_output_filter_redacts_pii":
        "PII lọt vào câu trả lời",
}


def main() -> int:
    print(f"Chạy {len(TESTS)} test bảo mật — mỗi test là một cuộc tấn công.\n")
    failures = 0

    for name, test in TESTS:
        attack = ATTACKS.get(name, "")
        try:
            test()
            print(f"[pass] {name:52} | {attack}")
        except Exception as exc:  # noqa: BLE001 — runner cần bắt mọi lỗi
            failures += 1
            print(f"[FAIL] {name:52} | {attack}")
            print(f"       {type(exc).__name__}: {exc}")

    print(f"\nKết quả: {len(TESTS) - failures}/{len(TESTS)} pass")
    if failures:
        print("Có test hỏng. Đừng deploy. Sửa guard, không sửa test.")
        return 1

    print("Toàn bộ tấn công đã bị chặn. Đây là điều kiện tối thiểu để deploy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
