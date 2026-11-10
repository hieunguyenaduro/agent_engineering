"""Bài 06 — Đếm chi phí trước khi nhân bản agent.

Chạy:  python 06_cost_budget.py

Multi-agent không miễn phí. Mỗi lần supervisor giao việc là một lần gọi model,
cộng thêm một lần tổng hợp. Ba worker = bốn lần gọi, chưa kể retry.

Bài này làm ba việc:
    1. Mỗi worker ghi lại token và tiền vào một budget dùng chung.
    2. Supervisor kiểm tra ngân sách TRƯỚC khi phát việc; hết thì bỏ việc phụ.
    3. In bảng chi phí theo agent, so với phương án một agent.

Giá trong file là ví dụ. Luôn kiểm tra lại bảng giá hiện hành của nhà cung cấp.
"""

import asyncio
import operator
from dataclasses import dataclass, field
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

# Giá ví dụ cho một model nhỏ: USD / 1 triệu token.
INPUT_PRICE = 0.15
OUTPUT_PRICE = 0.60

MAX_CALLS = 3                 # ngân sách số lần gọi model
TOPICS = ["pricing", "policy", "technical", "billing", "shipping"]


@dataclass
class Budget:
    max_calls: int
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    by_agent: dict = field(default_factory=dict)

    def can_spend(self) -> bool:
        return self.calls < self.max_calls

    def charge(self, agent: str, input_tokens: int, output_tokens: int) -> None:
        self.calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        row = self.by_agent.setdefault(agent, {"calls": 0, "usd": 0.0, "tokens": 0})
        usd = (input_tokens * INPUT_PRICE + output_tokens * OUTPUT_PRICE) / 1_000_000
        row["calls"] += 1
        row["tokens"] += input_tokens + output_tokens
        row["usd"] += usd

    @property
    def usd(self) -> float:
        return (self.input_tokens * INPUT_PRICE + self.output_tokens * OUTPUT_PRICE) / 1_000_000


BUDGET = Budget(max_calls=MAX_CALLS)


class State(TypedDict):
    question: str
    topics: list[str]
    skipped: list[str]
    findings: Annotated[list[str], operator.add]
    summary: str


def supervisor(state: State) -> dict:
    """Chỉ phát việc khi còn ngân sách. Hết thì ghi lại việc bị bỏ.

    Giữ lại một slot cho bước tổng hợp — nếu không, worker ăn hết ngân sách
    và aggregate sẽ vượt trần.
    """
    remaining = max(0, BUDGET.max_calls - BUDGET.calls - 1)
    topics = TOPICS[:remaining]
    skipped = TOPICS[remaining:]
    return {"topics": topics, "skipped": skipped}


def fan_out(state: State) -> list[Send]:
    return [Send("worker", {"topic": topic}) for topic in state["topics"]]


async def worker(state: dict) -> dict:
    topic = state["topic"]
    prompt_tokens = 120 + len(topic) * 10
    completion_tokens = 60

    BUDGET.charge(f"worker:{topic}", prompt_tokens, completion_tokens)
    await asyncio.sleep(0.01)  # giả lập gọi API
    return {"findings": [f"[{topic}] đã xử lý ({prompt_tokens}+{completion_tokens} token)"]}


def aggregate(state: State) -> dict:
    # Lần tổng hợp cũng là một lần gọi model — phải tính tiền.
    BUDGET.charge("aggregate", 300, 150)

    lines = [f"- {finding}" for finding in sorted(state["findings"])]
    if state["skipped"]:
        lines.append(f"- Bỏ qua vì hết ngân sách: {', '.join(state['skipped'])}")
    return {"summary": "\n".join(lines)}


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
    result = asyncio.run(
        graph.ainvoke(
            {"question": "Tổng hợp mọi thông tin", "topics": [], "skipped": [],
             "findings": [], "summary": ""}
        )
    )

    print("Kết quả:")
    print(result["summary"])

    print(f"\nNgân sách: tối đa {MAX_CALLS} lần gọi model")
    print(f"{'agent':22} {'calls':>6} {'tokens':>8} {'USD':>10}")
    for agent, row in sorted(BUDGET.by_agent.items()):
        print(f"{agent:22} {row['calls']:6d} {row['tokens']:8d} {row['usd']:10.6f}")
    print(f"{'TỔNG':22} {BUDGET.calls:6d} "
          f"{BUDGET.input_tokens + BUDGET.output_tokens:8d} {BUDGET.usd:10.6f}")

    # So sánh ba con số: thực chi, nếu chạy đủ việc, và một agent tự làm.
    single_usd = (900 * INPUT_PRICE + 400 * OUTPUT_PRICE) / 1_000_000
    full_usd = sum(
        ((120 + len(topic) * 10) * INPUT_PRICE + 60 * OUTPUT_PRICE) / 1_000_000
        for topic in TOPICS
    ) + (300 * INPUT_PRICE + 150 * OUTPUT_PRICE) / 1_000_000

    print(f"\nThực chi (bị ngân sách chặn): {BUDGET.calls} lần gọi, {BUDGET.usd:.6f} USD.")
    print(f"Nếu chạy đủ {len(TOPICS)} việc:      {len(TOPICS) + 1} lần gọi, ~{full_usd:.6f} USD.")
    print(f"Một agent tự làm:              1 lần gọi, ~{single_usd:.6f} USD.")
    print("\nSố lần gọi tăng tuyến tính theo số worker — đó là lý do phải có ngân sách.")
    print("Với tác vụ lớn, mỗi worker còn phải mang ngữ cảnh riêng, nên chênh lệch")
    print("thường lớn hơn ví dụ này. Chi phí không phải lý do để tránh multi-agent,")
    print("nhưng phải được đo trước khi chọn.")
