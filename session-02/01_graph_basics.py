"""Bài 01 — Graph cơ bản: State, Node, Edge.

Chạy:  python 01_graph_basics.py     (không cần API key, không gọi model)

Một graph gồm:
    State  = dữ liệu đi qua các bước (một dict có kiểu)
    Node   = một hàm nhận state, trả về phần state cần cập nhật
    Edge   = bước tiếp theo; có thể có điều kiện

Đây chỉ là một máy trạng thái. Chưa có gì liên quan tới LLM.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    question: str
    route: str
    answer: str


def classify(state: State) -> dict:
    """Node 1: quyết định câu hỏi thuộc nhánh nào."""
    question = state["question"].lower()
    if any(word in question for word in ("đơn", "hoá đơn", "hoàn tiền")):
        return {"route": "billing"}
    return {"route": "technical"}


def billing(state: State) -> dict:
    return {"answer": "Chuyển tới bộ phận hoá đơn."}


def technical(state: State) -> dict:
    return {"answer": "Chuyển tới bộ phận kỹ thuật."}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing", billing)
builder.add_node("technical", technical)

builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify",
    lambda state: state["route"],
    {"billing": "billing", "technical": "technical"},
)
builder.add_edge("billing", END)
builder.add_edge("technical", END)

graph = builder.compile()


if __name__ == "__main__":
    for question in ["Đơn 1234 của tôi đâu?", "Cách đổi mật khẩu?"]:
        print(f"Hỏi: {question}")
        print(f"  -> {graph.invoke({'question': question})}")
        print()

    print("=== Graph nhìn từ trên xuống (dán vào mermaid.live để xem hình) ===")
    print(graph.get_graph().draw_mermaid())
