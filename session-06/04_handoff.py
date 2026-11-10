"""Bài 04 — Handoff: chuyển quyền điều khiển, giữ nguyên hội thoại.

Chạy:  python 04_handoff.py

Handoff khác "gọi subagent rồi nhận kết quả" ở chỗ: agent sau tiếp tục
cuộc hội thoại, không quay lại agent trước.

    START ──> triage ──Command──> billing_agent ──Command──> refund_agent ──> END

`Command(goto=..., update=...)` vừa chuyển node vừa ghi state trong cùng
một bước. Vì state là MessagesState, toàn bộ lịch sử được giữ nguyên.

Đây là cách các hệ thống thật làm "chuyển cho nhân viên chuyên trách":
người tiếp nhận thấy đủ ngữ cảnh, không phải hỏi lại từ đầu.
"""

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command


class State(MessagesState):
    assigned_to: str
    handoffs: list[str]


def triage(state: State) -> Command[Literal["billing_agent", "technical_agent"]]:
    """Bước 1: phân loại. Sau đó chuyển hẳn quyền điều khiển."""
    text = state["messages"][-1].content.lower()

    if any(word in text for word in ("hoá đơn", "hóa đơn", "hoàn tiền", "thanh toán")):
        target = "billing_agent"
    else:
        target = "technical_agent"

    return Command(
        goto=target,
        update={
            "assigned_to": target,
            "handoffs": state.get("handoffs", []) + [f"triage -> {target}"],
            "messages": [AIMessage(content=f"[triage] Chuyển tới {target}.")],
        },
    )


def billing_agent(state: State) -> Command[Literal["refund_agent", END]]:
    """Bước 2: nếu liên quan hoàn tiền thì chuyển tiếp cho chuyên trách."""
    text = state["messages"][0].content.lower()

    if "hoàn tiền" in text:
        return Command(
            goto="refund_agent",
            update={
                "assigned_to": "refund_agent",
                "handoffs": state["handoffs"] + ["billing_agent -> refund_agent"],
                "messages": [
                    AIMessage(
                        content=(
                            "[billing] Đã xác minh đơn hàng. "
                            "Chuyển hồ sơ hoàn tiền cho chuyên trách."
                        )
                    )
                ],
            },
        )

    return Command(
        goto=END,
        update={
            "messages": [
                AIMessage(content="[billing] Đã kiểm tra hoá đơn, mọi thứ bình thường.")
            ]
        },
    )


def technical_agent(state: State) -> dict:
    return {
        "assigned_to": "technical_agent",
        "messages": [
            AIMessage(content="[technical] Bạn thử đăng xuất rồi đăng nhập lại giúp mình.")
        ],
    }


def refund_agent(state: State) -> dict:
    return {
        "assigned_to": "refund_agent",
        "messages": [
            AIMessage(
                content=(
                    "[refund] Mình thấy lịch sử trao đổi và đơn hàng đã xác minh. "
                    "Khoản hoàn tiền sẽ được xử lý trong 3–5 ngày làm việc."
                )
            )
        ],
    }


builder = StateGraph(State)
builder.add_node("triage", triage)
builder.add_node("billing_agent", billing_agent)
builder.add_node("technical_agent", technical_agent)
builder.add_node("refund_agent", refund_agent)

builder.add_edge(START, "triage")
builder.add_edge("technical_agent", END)
builder.add_edge("refund_agent", END)

graph = builder.compile()


if __name__ == "__main__":
    question = "Tôi muốn hoàn tiền cho hoá đơn 1234 vì sản phẩm lỗi."
    result = graph.invoke(
        {
            "messages": [HumanMessage(question)],
            "assigned_to": "",
            "handoffs": [],
        }
    )

    print(f"Hỏi: {question}\n")
    for message in result["messages"]:
        role = type(message).__name__.replace("Message", "").lower()
        print(f"  [{role}] {message.content}")

    print("\nChuỗi handoff:")
    for step in result["handoffs"]:
        print(f"  {step}")
    print(f"\nNgười xử lý cuối: {result['assigned_to']}")

    print("\nĐiểm cần thấy: refund_agent không nhận câu hỏi gốc từ đầu.")
    print("Nó đọc toàn bộ messages — nhờ vậy không hỏi lại khách lần nữa.")
