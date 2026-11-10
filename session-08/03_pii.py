"""Bài 03 — PII: phát hiện, che, và log sạch.

Chạy: python 03_pii.py

Luồng đúng:
    người dùng -> phát hiện PII -> che -> model chỉ thấy bản che
    -> log cũng chỉ ghi bản che.

PII gồm: email, số điện thoại Việt Nam, số CCCD, số thẻ.
Dữ liệu trong file là giả, nhưng cách xử lý là cách dùng thật.
"""

import json
import os
import tempfile
from pathlib import Path

from common.audit import AuditLog
from common.pii import detect, kinds, luhn_valid, mask_value, redact

SECRET = os.getenv("FAKE_API_KEY", "sk-demo-SECRET-123")

RAW = (
    "Khách Nguyễn Văn A, email nguyenvana@example.com, "
    "SĐT 0912 345 678, CCCD 012345678901, "
    "thẻ 4111 1111 1111 1111. Đơn 1234 bị lỗi."
)


def show_detection() -> None:
    print("### 1. Phát hiện")
    for finding in detect(RAW):
        masked = mask_value(finding.kind, finding.value)
        print(f"  {finding.kind:6} {masked:24} vị trí {finding.start}-{finding.end}")
    print(f"[verify] checksum thẻ: {luhn_valid('4111111111111111')}")


def show_redaction() -> None:
    print("\n### 2. Che trước khi gửi model")
    safe = redact(RAW)
    print("  gốc :", RAW)
    print("  che :", safe)
    print(f"[verify] còn loại PII nào trong bản che: {kinds(safe) or 'không'}")

    payload = {
        "system": "Bạn là trợ lý CSKH. Không lưu PII thô.",
        "user": safe,
    }
    print("  payload gửi model:")
    print("  " + json.dumps(payload, ensure_ascii=False))


def show_logs() -> None:
    print("\n### 3. Log sạch")
    bad = json.dumps({"message": RAW}, ensure_ascii=False)
    good = json.dumps({"message": redact(RAW)}, ensure_ascii=False)
    print("  [bad ]", bad)
    print("  [good]", good)

    with tempfile.TemporaryDirectory() as tmp:
        log = AuditLog(Path(tmp) / "audit.jsonl")
        entry = log.record(
            actor="nguyenvana@example.com",
            action="chat",
            args={"message": RAW, "api_key": SECRET},
        )
        line = json.dumps(entry, ensure_ascii=False, indent=2)
        print("\n  một dòng audit thật:")
        print("  " + line.replace("\n", "\n  "))

        raw_line = log.path.read_text(encoding="utf-8")
        leaked = [
            value for value in (
                "nguyenvana@example.com", "0912 345 678",
                "012345678901", "4111 1111 1111 1111", SECRET,
            )
            if value in raw_line
        ]
        print(f"\n[verify] giá trị thô còn trong log: {leaked or 'không'}")


def show_policy() -> None:
    print("\n### 4. Chính sách lưu trữ (ví dụ, không phải luật)")
    print("  - PII thô chỉ tồn tại trong RAM lúc xử lý, không ghi xuống đĩa.")
    print("  - DB: mã hoá cột nhạy cảm, TTL 30 ngày, chỉ role support_admin đọc.")
    print("  - Log: chỉ bản đã che; không ghi request body, không ghi header.")
    print("  - Xuất dữ liệu: chạy lại redact và kiểm tra trước khi gửi đi.")
    print("  - Xoá theo yêu cầu: xoá cả bản chính, bản sao lưu và cache.")


if __name__ == "__main__":
    show_detection()
    show_redaction()
    show_logs()
    show_policy()
    print("\nBài học: che ở cửa vào, che ở cửa ra, và đừng quên log là một cửa ra.")
