"""Bài 02 — Supervisor: một agent điều phối nhiều agent.

Chạy:  python 02_supervisor.py

    START ──> supervisor ──┬──> billing  ──┐
                           ├──> technical ─┼──> summarize ──> END
                           └──> general  ──┘

Supervisor ở đây là hàm if/else để bạn thấy rõ quyết định định tuyến.
Ở production, supervisor là một LLM gọi structured output:

    {"route": "billing", "ly_do": "câu hỏi có số đơn và từ 'hoàn tiền'"}

Nhưng logic vẫn y như vậy: một node quyết định, các node khác làm việc.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

WORKERS = ("billing", "technical", "general")


class State(TypedDict):
    task: str
    route: str
    log: list[str]
    answer: str


# ---------------------------------------------------------------------------
# Supervisor
# ---------------------------------------------------------------------------
def supervisor(state: State) -> dict:
    """Quyết định ai làm việc. Không tự trả lời."""
    task = state["task"].lower()

    if any(word in task for word in ("hoá đơn", "hóa đơn", "hoàn tiền", "thanh toán")):
        route = "billing"
    elif any(word in task for word in ("lỗi", "cài đặt", "đăng nhập", "kỹ thuật")):
        route = "technical"
    else:
        route = "general"

    reason = f"supervisor: '{state['task']}' -> {route}"
    return {"route": route, "log": state.get("log", []) + [reason]}


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------
def billing(state: State) -> dict:
    return {
        "answer": "Bộ phận hoá đơn: đã kiểm tra, khoản hoàn tiền sẽ về trong 3–5 ngày.",
        "log": state["log"] + ["billing: tra cứu và xử lý hoàn tiền"],
    }


def technical(state: State) -> dict:
    return {
        "answer": "Bộ phận kỹ thuật: bạn thử đăng xuất rồi đăng nhập lại, nếu vẫn lỗi gửi mã đơn.",
        "log": state["log"] + ["technical: chạy checklist lỗi đăng nhập"],
    }


def general(state: State) -> dict:
    return {
        "answer": "Mình chưa xác định được bộ phận phù hợp, đã chuyển cho người trực.",
        "log": state["log"] + ["general: chuyển người thật"],
    }


def summarize(state: State) -> dict:
    return {"log": state["log"] + ["summarize: gộp kết quả và kết thúc"]}


WORKER_NODES = {"billing": billing, "technical": technical, "general": general}


def route(state: State) -> Literal["billing", "technical", "general"]:
    return state["route"]


builder = StateGraph(State)
builder.add_node("supervisor", supervisor)
for name, node in WORKER_NODES.items():
    builder.add_node(name, node)
builder.add_node("summarize", summarize)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route, list(WORKERS))
for name in WORKERS:
    builder.add_edge(name, "summarize")
builder.add_edge("summarize", END)

graph = builder.compile()


if __name__ == "__main__":
    tasks = [
        "Tôi muốn hoàn tiền cho hoá đơn tháng này.",
        "Tôi không đăng nhập được vào ứng dụng.",
        "Công ty có mở vào thứ bảy không?",
    ]

    for task in tasks:
        print(f"\n=== {task}")
        result = graph.invoke({"task": task, "route": "", "log": [], "answer": ""})
        for line in result["log"]:
            print(f"  - {line}")
        print(f"  => {result['answer']}")

    print("\nMỗi worker chỉ nhận đúng phần việc của mình.")
    print("Supervisor không làm việc — nó chỉ chọn người và ghi lý do.")
