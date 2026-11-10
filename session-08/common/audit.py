"""Audit log dạng JSONL: ai làm gì, khi nào, với tool nào.

Hai luật của log bảo mật:
    1. Không ghi bí mật (API key, token, mật khẩu) — kể cả trong URL.
    2. Không ghi PII thô — che trước khi ghi, vì log thường được sao lưu rộng rãi.

Log không phải nơi "để sau này xử lý". Log đã ghi là đã rời khỏi hệ thống.
"""

import json
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .pii import redact

SENSITIVE_KEYS = {
    "api_key", "apikey", "password", "passwd", "token", "access_token",
    "authorization", "cookie", "secret", "client_secret",
}
_SECRET_QUERY = re.compile(
    r"([?&](?:token|api_key|key|password|secret)=)[^&\s]+", re.I
)


def _clean(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            cleaned[key] = "[REDACTED]" if normalized in SENSITIVE_KEYS else _clean(item)
        return cleaned
    if isinstance(value, (list, tuple)):
        return [_clean(item) for item in value]
    if isinstance(value, str):
        return redact(_SECRET_QUERY.sub(r"\1[REDACTED]", value))
    return value


class AuditLog:
    def __init__(self, path=None):
        self.path = (
            Path(path) if path
            else Path(tempfile.gettempdir()) / "agent_engineering_audit.jsonl"
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, *, actor, action, tool=None, args=None,
               outcome="ok", tenant_id=None, request_id=None) -> dict:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "request_id": request_id or uuid.uuid4().hex[:8],
            "actor": _clean(str(actor)),
            "tenant_id": tenant_id,
            "action": action,
            "tool": tool,
            "args": _clean(args or {}),
            "outcome": outcome,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def entries(self, limit: int | None = None) -> list[dict]:
        if not self.path.exists():
            return []
        rows = [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return rows[-limit:] if limit else rows
