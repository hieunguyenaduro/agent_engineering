"""Bài 04 — Streaming: người dùng thấy agent đang làm gì.

Chạy:  python 04_streaming.py

Hai chế độ hay dùng:
    stream_mode="updates"  -> mỗi node chạy xong in ra phần state nó cập nhật
    stream_mode="messages" -> từng mẩu chữ model sinh ra (token stream)

Với model thật, chế độ messages chạy từng token. Với FAKE=1, nó in từng message.
"""

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common.llm import get_model
from common.shop import TOOLS

model = get_model(TOOLS)


def agent_node(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()

QUESTION = "Đơn 1234 đang ở đâu?"


if __name__ == "__main__":
    print("=== 1. Tiến độ theo từng bước (updates) ===")
    for event in graph.stream({"messages": [HumanMessage(QUESTION)]}, stream_mode="updates"):
        for node_name, update in event.items():
            last = update["messages"][-1]
            if isinstance(last, AIMessage) and last.tool_calls:
                detail = f"gọi {[c['name'] for c in last.tool_calls]}"
            elif isinstance(last, ToolMessage):
                detail = last.content
            else:
                detail = getattr(last, "content", "")
            print(f"  [{node_name}] {detail}")

    print("\n=== 2. Từng mẩu chữ (messages) ===")
    print("  ", end="")
    for chunk, metadata in graph.stream(
        {"messages": [HumanMessage(QUESTION)]}, stream_mode="messages"
    ):
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            print(chunk.content, end="", flush=True)
    print()

    print("\nDùng cho UI: mỗi event là một dòng SSE để hiện 'đang tra đơn...' cho người dùng.")
