"""Bài 03 — Chạy song song với Send.

Chạy:  python 03_parallel_fanout.py

Với supervisor tuần tự, ba việc mất 3×thời gian. Với Send, ba worker chạy
song song và kết quả được gộp bằng reducer.

    START ──> supervisor ──Send──> worker(pricing)  ──┐
                        ──Send──> worker(policy)    ──┼──> aggregate ──> END
                        ──Send──> worker(technical) ──┘

Ba điểm kỹ thuật:
    1. `Annotated[list, operator.add]` để nhiều worker cùng ghi vào một list.
    2. `Send(node, payload)` phát một nhánh cho mỗi việc.
    3. `defer=True` để aggregate chỉ chạy một lần, sau khi mọi nhánh xong.

Lưu ý quan trọng: node phải là `async def` và gọi bằng `ainvoke` thì mới
chạy thật song song. Nếu dùng hàm sync, LangGraph chạy lần lượt — Send
vẫn đúng về logic nhưng không nhanh hơn.
"""

import asyncio
import operator
import time
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

QUESTIONS = {
    "pricing": "Giá gói cơ bản và gói pro?",
    "policy": "Chính sách hoàn tiền?",
    "technical": "Hỗ trợ kỹ thuật qua kênh nào?",
}

ANSWERS = {
    "pricing": "Gói cơ bản 199k/tháng, gói pro 499k/tháng, dùng thử 14 ngày.",
    "policy": "Hoàn tiền trong 7 ngày, trừ gói đã dùng quá 80%.",
    "technical": "Email 24h, điện thoại 8h–18h các ngày làm việc.",
}

DELAY = 0.3  # giây, giả lập một lần gọi API


class State(TypedDict):
    question: str
    topics: list[str]
    findings: Annotated[list[str], operator.add]
    summary: str


def supervisor(state: State) -> dict:
    """Chọn việc nào cần chạy. Trong thực tế đây là LLM + structured output."""
    question = state["question"].lower()
    topics = []
    if any(word in question for word in ("giá", "bao nhiêu", "gói")):
        topics.append("pricing")
    if any(word in question for word in ("hoàn tiền", "chính sách", "đổi trả")):
        topics.append("policy")
    if any(word in question for word in ("hỗ trợ", "kỹ thuật", "liên hệ")):
        topics.append("technical")
    return {"topics": topics or ["policy"]}


def fan_out(state: State) -> list[Send]:
    """Mỗi topic thành một nhánh chạy song song."""
    return [
        Send("worker", {"topic": topic, "question": state["question"]})
        for topic in state["topics"]
    ]


async def worker(state: dict) -> dict:
    """Mỗi worker chỉ thấy đúng việc của mình, không thấy việc của người khác."""
    topic = state["topic"]
    await asyncio.sleep(DELAY)  # giả lập gọi API; ba worker ngủ cùng lúc
    return {"findings": [f"[{topic}] {ANSWERS[topic]}"]}


def aggregate(state: State) -> dict:
    """Chạy một lần sau khi tất cả nhánh xong (nhờ defer=True)."""
    ordered = sorted(state["findings"])
    lines = "\n".join(f"- {finding}" for finding in ordered)
    return {"summary": f"Tổng hợp {len(ordered)} nguồn:\n{lines}"}


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
    question = "Cho tôi biết giá các gói, chính sách hoàn tiền và kênh hỗ trợ kỹ thuật."

    start = time.monotonic()
    result = asyncio.run(
        graph.ainvoke(
            {"question": question, "topics": [], "findings": [], "summary": ""}
        )
    )
    elapsed = time.monotonic() - start

    print(f"Hỏi: {question}\n")
    print("Các nhánh đã chạy:", result["topics"])
    print()
    print(result["summary"])
    print(f"\nThời gian: {elapsed:.2f}s cho {len(result['topics'])} nhánh.")
    print(f"Nếu chạy tuần tự: khoảng {DELAY * len(result['topics']):.2f}s.")
    print("\nChú ý: findings được gộp bằng operator.add — thứ tự không đảm bảo.")
    print("Muốn thứ tự cố định thì sort trong aggregate, như file này làm.")
