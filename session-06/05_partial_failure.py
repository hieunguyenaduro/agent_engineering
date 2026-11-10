"""Bài 05 — Một nhánh chết, cả câu trả lời không được chết.

Chạy:  python 05_partial_failure.py

Multi-agent làm tăng số thứ có thể hỏng: một worker timeout, một tool lỗi,
một API trả 500. Nếu để exception bay lên, cả request mất trắng.

Nguyên tắc: worker tự bắt lỗi của mình, trả về "không làm được" như dữ liệu.
Aggregator quyết định trả lời một phần hay báo lỗi toàn bộ.

    worker(refund)  -> RuntimeError  -> errors: [...]
    worker(legacy)  -> quá 0.2s      -> errors: [...]
    worker(pricing) -> ok            -> findings: [...]

    aggregate -> trả lời 1 nguồn + ghi rõ 2 nguồn thất bại
"""

import asyncio
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

TIMEOUT = 0.2  # giây, cố tình nhỏ để bài chạy nhanh

ANSWERS = {
    "pricing": "Gói cơ bản 199k/tháng, gói pro 499k/tháng.",
    "policy": "Hoàn tiền trong 7 ngày nếu chưa dùng quá 80%.",
}


class State(TypedDict):
    question: str
    topics: list[str]
    findings: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    summary: str


def supervisor(state: State) -> dict:
    question = state["question"].lower()
    topics = []
    if any(word in question for word in ("giá", "gói")):
        topics.append("pricing")
    if any(word in question for word in ("chính sách", "hoàn tiền")):
        topics.append("policy")
    if "hoàn tiền" in question:
        topics.append("refund")      # worker này sẽ lỗi
    if "hệ thống cũ" in question:
        topics.append("legacy")      # worker này sẽ timeout
    return {"topics": topics or ["policy"]}


def fan_out(state: State) -> list[Send]:
    return [Send("worker", {"topic": topic}) for topic in state["topics"]]


async def call_service(topic: str) -> str:
    """Giả lập dịch vụ ngoài: nhanh, chậm, hoặc chết."""
    if topic == "refund":
        raise RuntimeError("dịch vụ hoàn tiền đang bảo trì")
    if topic == "legacy":
        await asyncio.sleep(1.0)     # chậm hơn TIMEOUT rất nhiều
    return ANSWERS[topic]


async def worker(state: dict) -> dict:
    """Không để lỗi bay ra ngoài: biến lỗi thành dữ liệu."""
    topic = state["topic"]
    try:
        answer = await asyncio.wait_for(call_service(topic), timeout=TIMEOUT)
        return {"findings": [f"[{topic}] {answer}"]}
    except asyncio.TimeoutError:
        return {"errors": [f"[{topic}] timeout sau {TIMEOUT}s"]}
    except Exception as exc:  # noqa: BLE001 — cố ý bắt mọi lỗi của worker
        return {"errors": [f"[{topic}] lỗi: {exc}"]}


def aggregate(state: State) -> dict:
    parts = [f"- {finding}" for finding in sorted(state["findings"])]
    if state["errors"]:
        parts.append("\nKhông lấy được:")
        parts.extend(f"- {error}" for error in sorted(state["errors"]))

    total = len(state["findings"]) + len(state["errors"])
    status = "đầy đủ" if not state["errors"] else "một phần"
    return {
        "summary": (
            f"Kết quả {status} ({len(state['findings'])}/{total} nguồn):\n"
            + "\n".join(parts)
        )
    }


builder = StateGraph(State)
builder.add_node("supervisor", supervisor)
builder.add_node("worker", worker)
builder.add_node("aggregate", aggregate, defer=True)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", fan_out, ["worker"])
builder.add_edge("worker", "aggregate")
builder.add_edge("aggregate", END)

graph = builder.compile()


if __name__ == "__main__":
    question = "Cho tôi giá các gói, chính sách hoàn tiền, và thông tin hệ thống cũ."
    result = asyncio.run(
        graph.ainvoke(
            {
                "question": question,
                "topics": [],
                "findings": [],
                "errors": [],
                "summary": "",
            }
        )
    )

    print(f"Hỏi: {question}\n")
    print(result["summary"])
    print("\nNgười dùng vẫn nhận được câu trả lời, kèm lời thú nhận phần nào thiếu.")
    print("Nếu exception bay lên, họ sẽ nhận trang lỗi 500 và không biết gì cả.")
