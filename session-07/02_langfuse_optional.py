"""Bài 02 — Gửi trace lên Langfuse nếu có key, không thì dùng tracer local.

Chạy:  python 02_langfuse_optional.py

Langfuse là tuỳ chọn. Thiếu package, thiếu key, sai host hay mạng lỗi — mọi
trường hợp đều in lý do và quay về trace local. Không có API key vẫn học được.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from common.agent import run_agent
from common.tracer import Span, Tracer, print_tree, save_jsonl

QUESTION = "Tai nghe đổi trả trong bao nhiêu ngày?"


def cloud_reason() -> str | None:
    """Trả về lý do không dùng cloud, hoặc None nếu đủ điều kiện thử."""
    if os.getenv("FAKE") == "1":
        return "FAKE=1 (chế độ offline bắt buộc)"
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return "thiếu LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY"
    try:
        import langfuse  # noqa: F401
    except Exception as exc:
        return f"chưa cài package langfuse ({type(exc).__name__})"
    return None


def make_client():
    """Tạo client; ném exception để main bắt và in lý do cụ thể."""
    from langfuse import Langfuse

    client = Langfuse(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )
    client.auth_check()
    return client


def send_spans(client, spans: list[Span], parent=None) -> None:
    """Phát lại cây span local lên Langfuse, giữ nguyên quan hệ cha-con."""
    for span in spans:
        remote = client.start_span(
            name=span.name,
            start_time=datetime.fromtimestamp(span.start, timezone.utc),
            metadata=span.attributes,
        )
        send_spans(client, span.children, remote)
        remote.end(
            end_time=datetime.fromtimestamp(span.end or span.start, timezone.utc),
            metadata={"status": span.status},
        )


if __name__ == "__main__":
    client = None
    reason = cloud_reason()
    if reason:
        print(f"[fallback] {reason} → chỉ dùng tracer local.")
    else:
        try:
            client = make_client()
            print("[cloud] Đã kết nối Langfuse, trace sẽ được gửi sau khi chạy.")
        except Exception as exc:
            print(f"[fallback] Không kết nối được Langfuse ({type(exc).__name__}: {exc}) → tracer local.")

    tracer = Tracer("langfuse-optional")
    result = run_agent(QUESTION, tracer=tracer)
    print(f"Câu trả lời: {result.answer}")
    print_tree(tracer)

    if client is not None:
        try:
            send_spans(client, tracer.roots)
            client.flush()
            print("[cloud] Đã gửi trace. Mở dashboard để xem cây span.")
        except Exception as exc:
            print(f"[fallback] Gửi trace thất bại ({type(exc).__name__}: {exc}); trace local vẫn còn.")

    path, rows = save_jsonl(tracer, Path(__file__).parent / "traces" / "trace.jsonl")
    print(f"[local] Đã ghi {rows} span vào {path}")
