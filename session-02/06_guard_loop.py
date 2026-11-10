"""Bài 06 — Chặn vòng lặp chạy mãi.

Chạy:  python 06_guard_loop.py

Agent có thể lặp vì:
    1. model cứ gọi một tool mãi
    2. tool luôn trả lỗi, model cứ thử lại
    3. model không bao giờ thấy "đủ thông tin"

Ba lớp bảo vệ, từ thô đến tinh:
    A. recursion_limit  - chặn cứng của LangGraph
    B. ngân sách bước   - đếm trong state, tự dừng và trả lời được
    C. phát hiện lặp    - hai lần liên tiếp cùng một hành động thì dừng
"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from common.fake_model import FakeToolModel
from common.shop import TOOLS

MAX_STEPS = 4


# ---------------------------------------------------------------------------
# A. Graph "hỏng": model cố tình gọi tool mãi, không có bộ đếm
# ---------------------------------------------------------------------------
def build_bad_graph():
    loop_model = FakeToolModel(mode="loop").bind_tools(TOOLS)

    def agent_node(state: MessagesState) -> dict:
        return {"messages": [loop_model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    builder.add_edge("agent", "tools")
    builder.add_edge("tools", "agent")
    return builder.compile()


# ---------------------------------------------------------------------------
# B + C. Graph có phanh
# ---------------------------------------------------------------------------
class GuardedState(MessagesState):
    steps: int


def build_guarded_graph():
    loop_model = FakeToolModel(mode="loop").bind_tools(TOOLS)

    def agent_node(state: GuardedState) -> dict:
        return {
            "messages": [loop_model.invoke(state["messages"])],
            "steps": state.get("steps", 0) + 1,
        }

    def stop_node(state: GuardedState) -> dict:
        return {
            "messages": [
                AIMessage(content=f"Dừng sau {state['steps']} bước để tránh lặp vô hạn.")
            ]
        }

    def next_step(state: GuardedState) -> str:
        if state["steps"] >= MAX_STEPS:          # phanh B: hết ngân sách
            return "stop"
        messages = state["messages"]
        if len(messages) >= 3:
            prev, last = messages[-3], messages[-1]
            if (
                isinstance(prev, AIMessage)
                and isinstance(last, AIMessage)
                and prev.tool_calls
                and last.tool_calls
                and prev.tool_calls[0]["name"] == last.tool_calls[0]["name"]
            ):
                return "stop"                    # phanh C: lặp lại hành động
        return "tools" if messages[-1].tool_calls else END

    builder = StateGraph(GuardedState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("stop", stop_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", next_step, ["tools", "stop", END])
    builder.add_edge("tools", "agent")
    builder.add_edge("stop", END)
    return builder.compile()


if __name__ == "__main__":
    question = "Đơn 1234 đang ở đâu?"
    messages = [HumanMessage(question)]

    print("=== A. Không có phanh: dựa vào recursion_limit ===")
    bad = build_bad_graph()
    try:
        bad.invoke({"messages": messages}, {"recursion_limit": 6})
        print("Không lỗi (hiếm).")
    except GraphRecursionError:
        print("GraphRecursionError: graph bị chặn cứng, người dùng nhận lỗi xấu.")

    print("\n=== B + C. Có phanh ===")
    guarded = build_guarded_graph()
    result = guarded.invoke({"messages": messages})
    print(f"Số bước đã chạy: {result['steps']}")
    print("Kết quả:", result["messages"][-1].content)

    print("\nBài học: đừng để recursion_limit là lớp bảo vệ duy nhất.")
    print("Hãy đếm bước và tự dừng bằng một câu trả lời tử tế.")
