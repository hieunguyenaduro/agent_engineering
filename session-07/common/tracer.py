"""Span và Tracer tối giản — đủ để học, không cần dịch vụ ngoài.

Một trace là một cây span. Mỗi span ghi tên, thời gian, thuộc tính và span con.
Langfuse, Jaeger hay OpenTelemetry đều dùng đúng mô hình này; chúng chỉ khác
nhau ở chỗ dữ liệu được gửi đi đâu và được lưu bao lâu.
"""

from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


@dataclass
class Span:
    """Một bước có thời gian bắt đầu/kết thúc và các thuộc tính đi kèm."""

    name: str
    start: float
    end: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    children: list["Span"] = field(default_factory=list)
    status: str = "ok"

    @property
    def duration_ms(self) -> float:
        end = self.end if self.end is not None else time.time()
        return round((end - self.start) * 1000, 2)


class Tracer:
    """Giữ các span gốc của một lần chạy và cho phép mở span lồng nhau."""

    def __init__(self, name: str = "trace"):
        self.name = name
        self.trace_id = uuid.uuid4().hex
        self.roots: list[Span] = []
        self._stack: list[Span] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[Span]:
        """Mở span; tự đóng và ghi lỗi nếu code bên trong ném exception."""
        current = Span(name=name, start=time.time(), attributes=dict(attributes))
        if self._stack:
            self._stack[-1].children.append(current)
        else:
            self.roots.append(current)
        self._stack.append(current)
        try:
            yield current
        except Exception as exc:
            current.status = "error"
            current.attributes["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            current.end = time.time()
            self._stack.pop()
def _short(value: Any, limit: int = 64) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 3] + "..."
def _print_span(span: Span, prefix: str, is_last: bool, root: bool = False) -> None:
    connector = "" if root else ("└─ " if is_last else "├─ ")
    attrs = "  ".join(f"{key}={_short(value)}" for key, value in span.attributes.items())
    status = "" if span.status == "ok" else f"  [{span.status}]"
    print(f"{prefix}{connector}{span.name}  {span.duration_ms}ms{status}")
    if attrs:
        print(f"{prefix}{'   ' if root else ('   ' if is_last else '│  ')}  {attrs}")
    child_prefix = prefix if root else prefix + ("   " if is_last else "│  ")
    for index, child in enumerate(span.children):
        _print_span(child, child_prefix, index == len(span.children) - 1)
def print_tree(tracer: Tracer) -> None:
    """In cây trace theo thứ tự đọc từ trên xuống."""
    print(f"\nTRACE {tracer.trace_id[:8]} · {tracer.name}")
    for root in tracer.roots:
        _print_span(root, "", True, root=True)
def _iter_spans(spans: list[Span]) -> Iterator[Span]:
    for span in spans:
        yield span
        yield from _iter_spans(span.children)
def summary(tracer: Tracer) -> dict[str, Any]:
    """Đếm span, lỗi, token và thời gian — những số hay dùng khi review."""
    spans = list(_iter_spans(tracer.roots))
    tokens_in = sum(
        span.attributes.get("tokens_in", 0)
        for span in spans
        if isinstance(span.attributes.get("tokens_in"), (int, float))
    )
    tokens_out = sum(
        span.attributes.get("tokens_out", 0)
        for span in spans
        if isinstance(span.attributes.get("tokens_out"), (int, float))
    )
    return {
        "spans": len(spans),
        "errors": sum(1 for span in spans if span.status != "ok"),
        "tokens_in": int(tokens_in),
        "tokens_out": int(tokens_out),
        "duration_ms": round(sum(span.duration_ms for span in tracer.roots), 2),
    }
def save_jsonl(tracer: Tracer, path: str | Path) -> tuple[Path, int]:
    """Ghi mỗi span thành một dòng JSONL để nạp vào công cụ phân tích."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    def visit(span: Span, parent_id: str | None) -> None:
        span_id = uuid.uuid4().hex[:16]
        rows.append(
            {
                "trace_id": tracer.trace_id,
                "span_id": span_id,
                "parent_id": parent_id,
                "name": span.name,
                "start": datetime.fromtimestamp(span.start, timezone.utc).isoformat(),
                "end": (
                    datetime.fromtimestamp(span.end, timezone.utc).isoformat()
                    if span.end
                    else None
                ),
                "duration_ms": span.duration_ms,
                "status": span.status,
                "attributes": span.attributes,
            }
        )
        for child in span.children:
            visit(child, span_id)

    for root in tracer.roots:
        visit(root, None)

    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path, len(rows)
