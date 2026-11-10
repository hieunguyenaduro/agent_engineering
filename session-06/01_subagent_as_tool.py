"""Bài 01 — Subagent như một tool.

Chạy:  python 01_subagent_as_tool.py

Ý tưởng:
    Agent chính không tự tra cứu. Nó gọi một subagent — một graph riêng —
    qua giao diện tool. Với agent chính, subagent chỉ là một function.

    main graph:  agent ──(gọi research)──> tools ──> agent ──> END
    research:    START ──> gather ──> summarize ──> END   (graph lồng bên trong)

Đây là cách rẻ nhất để tách việc: không cần framework riêng, chỉ cần
một hàm invoke graph con và trả về chuỗi.
"""

from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common.llm import get_model

# ---------------------------------------------------------------------------
# Graph con: "nhà nghiên cứu"
# ---------------------------------------------------------------------------
NOTES = {
    "giá": "Gói cơ bản 199k/tháng, gói pro 499k/tháng, dùng thử 14 ngày.",
    "chính sách": "Hoàn tiền trong 7 ngày, không cần lý do, trừ gói đã dùng quá 80%.",
    "kỹ thuật": "Hỗ trợ qua email 24h, qua điện thoại 8h-18h các ngày làm việc.",
}


class ResearchState(TypedDict):
    query: str
    notes: list[str]
    report: str


def gather(state: ResearchState) -> dict:
    """Bước 1: thu thập. Ở production đây là nơi gọi search/DB."""
    query = state["query"].lower()
    found = [text for key, text in NOTES.items() if key in query]
    if not found:
        found = ["Không tìm thấy ghi chú nội bộ nào liên quan."]
    return {"notes": found}


def summarize(state: ResearchState) -> dict:
    """Bước 2: nén thành báo cáo ngắn cho agent chính."""
    lines = "\n".join(f"- {note}" for note in state["notes"])
    return {"report": f"Báo cáo nghiên cứu:\n{lines}"}


research_builder = StateGraph(ResearchState)
research_builder.add_node("gather", gather)
research_builder.add_node("summarize", summarize)
research_builder.add_edge(START, "gather")
research_builder.add_edge("gather", "summarize")
research_builder.add_edge("summarize", END)
researcher = research_builder.compile()


# ---------------------------------------------------------------------------
# Bọc graph con thành tool
# ---------------------------------------------------------------------------
@tool
def research(query: str) -> str:
    """Giao một câu hỏi cho subagent nghiên cứu và nhận báo cáo ngắn.

    Dùng khi cần thông tin nội bộ về giá, chính sách hoặc hỗ trợ kỹ thuật.
    """
    result = researcher.invoke({"query": query, "notes": [], "report": ""})
    return result["report"]


# ---------------------------------------------------------------------------
# Graph chính
# ---------------------------------------------------------------------------
model = get_model([research])


def agent_node(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode([research]))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()


if __name__ == "__main__":
    question = "Giá gói pro là bao nhiêu?"
    result = graph.invoke({"messages": [HumanMessage(question)]})

    print(f"Hỏi: {question}\n")
    for message in result["messages"]:
        if isinstance(message, AIMessage) and message.tool_calls:
            call = message.tool_calls[0]
            print(f"[main]  gọi subagent {call['name']}({call['args']})")
        elif isinstance(message, ToolMessage):
            print("[sub]   trả về:")
            for line in message.content.split("\n"):
                print(f"        {line}")
        elif isinstance(message, AIMessage) and message.content:
            print("[main]  trả lời cuối:")
            for line in message.content.split("\n"):
                print(f"        {line}")

    print("\nĐiểm cần thấy: agent chính không hề biết bên trong research có mấy bước.")
    print("Nó chỉ thấy một tool nhận chuỗi, trả chuỗi — đó là hợp đồng.")
