"""Bài 01 — Trace local: nhìn thấy đường đi của agent.

Chạy:  python 01_trace_local.py

Một trace là cây span. Span gốc là cả lượt chạy; span con là retrieve, gọi tool,
gọi model, trả lời. File này dùng Span/Tracer trong common/tracer.py, chạy một
agent giả 3 bước rồi in cây và ghi JSONL để phân tích sau.
"""

from pathlib import Path

from common.agent import run_agent
from common.tracer import Tracer, print_tree, save_jsonl, summary

if __name__ == "__main__":
    question = "Đơn 1234 đang ở đâu?"
    tracer = Tracer("demo-order-1234")

    result = run_agent(question, tracer=tracer)

    print(f"Câu hỏi: {question}")
    print(f"Câu trả lời: {result.answer}")
    print_tree(tracer)

    stats = summary(tracer)
    print(
        f"\nTổng: {stats['spans']} span · {stats['duration_ms']}ms · "
        f"{stats['errors']} lỗi · token ~{stats['tokens_in']} vào / {stats['tokens_out']} ra"
    )

    path, rows = save_jsonl(tracer, Path(__file__).parent / "traces" / "trace.jsonl")
    print(f"Đã ghi {rows} span vào {path}")
    print("Mỗi dòng JSONL là một span — nạp được vào spreadsheet hoặc công cụ trace.")
