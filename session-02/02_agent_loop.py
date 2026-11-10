"""Bài 02 — Vòng lặp agent bằng LangGraph.

Chạy:  python 02_agent_loop.py

So với 06_mini_harness.py của buổi 1:
    - vòng for  ->  hai node "agent" và "tools" nối thành vòng
    - if tool_calls -> tools_condition (một hàm có sẵn của LangGraph)
    - text()/tool_calls() -> AIMessage của LangChain

Cấu trúc:
    START → agent ─┬─(có tool_calls)→ tools → agent ...
                   └─(không)────────→ END
"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common.llm import get_model
from common.shop import TOOLS

model = get_model(TOOLS)


def agent_node(state: MessagesState) -> dict:
    """Một bước suy nghĩ: model nhìn toàn bộ hội thoại và quyết định làm gì."""
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))       # tự chạy mọi tool_calls

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # có tool_calls -> "tools"
builder.add_edge("tools", "agent")                        # xong tool -> quay lại agent

graph = builder.compile()


def print_trace(messages):
    for message in messages:
        kind = type(message).__name__
        if isinstance(message, AIMessage) and message.tool_calls:
            for call in message.tool_calls:
                print(f"  [think] {kind}: muốn gọi {call['name']}({call['args']})")
        elif isinstance(message, ToolMessage):
            print(f"  [act]   {kind}: {message.content}")
        elif isinstance(message, AIMessage):
            print(f"  [done]  {kind}: {message.content}")
        else:
            print(f"  [input] {kind}: {message.content}")


if __name__ == "__main__":
    question = "Đơn 1234 của tôi đang ở đâu, và tai nghe có được đổi trả không?"
    result = graph.invoke({"messages": [HumanMessage(question)]})

    print(f"Hỏi: {question}\n")
    print_trace(result["messages"])
