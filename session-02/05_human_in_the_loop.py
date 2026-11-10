"""Bài 05 — Human-in-the-loop: dừng lại xin phép trước hành động nguy hiểm.

Chạy:  python 05_human_in_the_loop.py

Luồng:
    agent muốn gọi issue_refund (hoàn tiền - không thể hoàn tác)
        → graph DỪNG, trả quyền điều khiển về cho chương trình
        → người dùng bấm duyệt/từ chối
        → graph chạy tiếp từ đúng chỗ dừng, nhờ checkpoint

Điểm mấu chốt: interrupt() không phải "hỏi model". Nó là graph tự dừng,
và state được lưu lại để hôm sau resume vẫn được.
"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt

from common.llm import get_model
from common.shop import TOOLS, issue_refund

model = get_model(TOOLS)


def agent_node(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


def needs_approval(state: MessagesState) -> str:
    last = state["messages"][-1]
    if not last.tool_calls:
        return END
    if any(call["name"] == "issue_refund" for call in last.tool_calls):
        return "approval"
    return "tools"


def approval_node(state: MessagesState) -> dict:
    call = state["messages"][-1].tool_calls[0]

    # ---- GRAPH DỪNG Ở ĐÂY ----
    decision = interrupt(
        {
            "canh_bao": "Hành động không thể hoàn tác",
            "tool": call["name"],
            "args": call["args"],
        }
    )

    if decision == "approve":
        content = issue_refund.invoke(call["args"])
    else:
        content = "Người dùng đã từ chối. Không hoàn tiền."

    return {"messages": [ToolMessage(content=content, tool_call_id=call["id"])]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_node("approval", approval_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", needs_approval, ["tools", "approval", END])
builder.add_edge("tools", "agent")
builder.add_edge("approval", "agent")

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "khach-hoan-tien"}}
    question = "Tôi muốn hoàn tiền cho đơn 1234."

    print(f"Hỏi: {question}\n")
    result = graph.invoke({"messages": [HumanMessage(question)]}, config)

    interrupt_data = result.get("__interrupt__")
    if not interrupt_data:
        print("Model không yêu cầu hoàn tiền nên không cần duyệt.")
        print("Trả lời:", result["messages"][-1].content)
    else:
        print("=== GRAPH ĐANG DỪNG, CHỜ NGƯỜI DUYỆT ===")
        print(interrupt_data[0].value)

        # Giả lập người dùng bấm nút. Đổi thành "reject" để xem nhánh từ chối.
        decision = "approve"
        print(f"\nNgười dùng chọn: {decision}\n")

        result = graph.invoke(Command(resume=decision), config)

        for message in result["messages"]:
            if isinstance(message, ToolMessage):
                print("[tool] ", message.content)
            elif isinstance(message, AIMessage) and message.content:
                print("[agent]", message.content)
