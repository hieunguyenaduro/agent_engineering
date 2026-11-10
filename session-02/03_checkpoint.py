"""Bài 03 — Checkpoint: agent ngủ dậy vẫn nhớ.

Chạy:  python 03_checkpoint.py

Checkpoint = ảnh chụp state sau mỗi bước, được lưu lại.
    - Cùng thread_id  -> nối tiếp cuộc hội thoại (memory)
    - Khác thread_id  -> người dùng khác, không thấy dữ liệu của nhau
    - Agent chết giữa đường -> chạy lại từ checkpoint cuối, không làm lại từ đầu

Ở production, checkpointer là Postgres/Redis. Ở đây dùng bộ nhớ RAM cho gọn.
"""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
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

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


def ask(question: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(question)]}, config)
    return result["messages"][-1].content


if __name__ == "__main__":
    # --- Cùng một khách, hai lượt hỏi -----------------------------------
    print("=== Cùng thread_id = cùng một cuộc hội thoại ===")
    print("Lượt 1:", ask("Đơn 1234 đang ở đâu?", "khach-A"))
    print("Lượt 2:", ask("Còn đơn 5678 thì sao?", "khach-A"))

    config_a = {"configurable": {"thread_id": "khach-A"}}
    state = graph.get_state(config_a)
    print(f"\nThread khach-A đang giữ {len(state.values['messages'])} message.")

    # --- Khách khác, cùng câu hỏi ----------------------------------------
    print("\n=== Khác thread_id = không thấy gì của nhau ===")
    config_b = {"configurable": {"thread_id": "khach-B"}}
    state_b = graph.get_state(config_b)  # chưa có gì
    print(f"Thread khach-B có state chưa? {bool(state_b.values)}")

    # --- Lịch sử các checkpoint ------------------------------------------
    print("\n=== Các checkpoint của khach-A (mới nhất trước) ===")
    for i, snapshot in enumerate(graph.get_state_history(config_a)):
        if i >= 4:
            break
        print(f"  bước {i}: {len(snapshot.values.get('messages', []))} message, "
              f"next={snapshot.next}")

    print("\nThử tưởng tượng: process bị kill ngay sau checkpoint cuối.")
    print("Chạy lại cùng thread_id -> graph tiếp tục từ đúng chỗ đó.")
