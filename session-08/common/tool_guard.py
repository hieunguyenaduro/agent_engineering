"""Kiểm soát quyền gọi tool: capability, rate limit, approval, SSRF, audit.

Nguyên tắc: model không bao giờ gọi tool trực tiếp. Mọi lời gọi đi qua guard,
và guard kiểm tra trên **danh tính đã xác thực** cùng **quyền đã cấp**, không
dựa vào lời model nói trong prompt.

Giới hạn đã biết: allowlist host không chặn được DNS rebinding hay redirect.
Production cần thêm egress proxy và kiểm tra lại host sau mỗi lần redirect.
"""

import ipaddress
import json
import secrets
import time
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from .audit import AuditLog


class ToolDenied(Exception):
    """Lời gọi tool bị từ chối trước khi chạy."""


class ApprovalRequired(ToolDenied):
    """Tool nguy hiểm cần con người phê duyệt."""


@dataclass(frozen=True)
class Actor:
    user_id: str
    tenant_id: str
    permissions: frozenset[str] = frozenset()


@dataclass
class ToolSpec:
    name: str
    capability: str
    fn: Callable[..., object]
    risk: str = "low"
    requires_approval: bool = False
    rate_limit: int = 30              # số lần trong một cửa sổ 60 giây
    allowed_hosts: tuple[str, ...] = ()


class ToolGuard:
    def __init__(self, specs: list[ToolSpec], audit: AuditLog | None = None,
                 window_seconds: int = 60):
        self.specs = {spec.name: spec for spec in specs}
        self.audit = audit or AuditLog()
        self.window = window_seconds
        self._calls: dict[tuple[str, str], list[float]] = {}
        self._approvals: dict[str, tuple[str, float]] = {}

    def human_approve(self, tool: str, args: dict,
                      approver: str = "supervisor", ttl: int = 300) -> str:
        """Chỉ UI của con người gọi hàm này. Model không có quyền sinh token."""
        token = f"approve-{tool}-{secrets.token_urlsafe(8)}"
        self._approvals[token] = (self._key(tool, args), time.time() + ttl)
        self.audit.record(actor=approver, action="approve", tool=tool, args=args,
                          outcome="approved")
        return token

    def call(self, actor: Actor, tool: str, args: dict | None = None,
             approval: str | None = None):
        args = args or {}
        spec = self.specs.get(tool)

        if spec is None:
            self._deny(actor, tool, args, "tool không tồn tại")
        if spec.capability not in actor.permissions:
            self._deny(actor, tool, args, f"thiếu quyền {spec.capability}")

        now = time.time()
        bucket = self._calls.setdefault((actor.user_id, tool), [])
        bucket[:] = [stamp for stamp in bucket if now - stamp < self.window]
        if len(bucket) >= spec.rate_limit:
            self._deny(actor, tool, args, "vượt rate limit")

        if spec.requires_approval:
            record = self._approvals.get(approval or "")
            if not record or record[0] != self._key(tool, args) or record[1] < now:
                self._deny(actor, tool, args,
                           "cần phê duyệt của con người", ApprovalRequired)
            self._approvals.pop(approval, None)

        if spec.allowed_hosts:
            problem = self._url_problem(str(args.get("url", "")), spec.allowed_hosts)
            if problem:
                self._deny(actor, tool, args, problem)

        bucket.append(now)
        try:
            result = spec.fn(**args)
        except Exception as exc:
            self.audit.record(actor=actor.user_id, tenant_id=actor.tenant_id,
                              action="tool_error", tool=tool, args=args,
                              outcome=f"error:{type(exc).__name__}")
            raise

        self.audit.record(actor=actor.user_id, tenant_id=actor.tenant_id,
                          action="tool_call", tool=tool, args=args, outcome="ok")
        return result

    # -- nội bộ ------------------------------------------------------------
    @staticmethod
    def _key(tool: str, args: dict) -> str:
        return json.dumps({"tool": tool, "args": args}, sort_keys=True,
                          ensure_ascii=False)

    @staticmethod
    def _url_problem(url: str, allowed_hosts: tuple[str, ...]) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            return "chỉ cho phép https"
        if parsed.username or parsed.password:
            return "URL chứa thông tin đăng nhập"
        host = (parsed.hostname or "").lower()
        if host not in allowed_hosts:
            return f"host {host or '(trống)'} không nằm trong allowlist"
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return None
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return "chặn IP nội bộ"
        return None

    def _deny(self, actor: Actor, tool: str, args: dict, reason: str,
              exc: type[ToolDenied] = ToolDenied):
        self.audit.record(actor=actor.user_id, tenant_id=actor.tenant_id,
                          action="tool_denied", tool=tool, args=args,
                          outcome=reason)
        raise exc(f"{tool}: {reason}")
