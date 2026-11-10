"""Bài 05 — Retrieval trở thành tool của agent.

Chạy:  python 05_rag_tool.py

Điểm khác biệt so với RAG cổ điển:
    - Không phải "luôn retrieve rồi trả lời"
    - Model tự quyết định có cần tra hay không
    - Tool trả về nguồn + điểm, để câu trả lời có trích dẫn
    - Nếu không đủ dữ liệu, tool nói thẳng để agent không bịa
"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common.knowledge import build_index, search
from common.llm import get_model

client = build_index()
# Ngưỡng này phải hiệu chỉnh theo embedding đang dùng: điểm của hash khác hẳn
# điểm của text-embedding-3-small. Đừng bê nguyên số của người khác.
SCORE_TOI_THIEU = 0.30


def make_search_tool(tenant: str):
    """Mỗi tenant có một tool riêng, đã đóng cứng phạm vi dữ liệu."""

    @tool
    def search_knowledge(query: str) -> str:
        """Tìm trong kho tri thức của cửa hàng.

        Dùng tool này trước khi trả lời mọi câu hỏi về chính sách đổi trả,
        vận chuyển, bảo hành. Không dùng để trả lời câu hỏi ngoài phạm vi.
        """
        hits = search(client, query, tenant=tenant, limit=3)
        if not hits or hits[0].score < SCORE_TOI_THIEU:
            return "KHONG_DU_DU_LIEU: không tìm thấy tài liệu phù hợp."
        return "\n---\n".join(
            f"[nguon: {hit.payload['source']} | diem: {hit.score:.2f}]\n{hit.payload['text']}"
            for hit in hits
        )

    return search_knowledge


def build_agent(tenant: str):
    search_tool = make_search_tool(tenant)
    model = get_model([search_tool])

    def agent_node(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode([search_tool]))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


def ask(graph, question: str):
    print(f"\n=== {question}")
    result = graph.invoke({"messages": [HumanMessage(question)]})
    for message in result["messages"]:
        if isinstance(message, AIMessage) and message.tool_calls:
            print(f"  [think] gọi {message.tool_calls[0]['name']}")
        elif isinstance(message, ToolMessage):
            first_line = message.content.split("\n")[0]
            print(f"  [act]   {first_line}")
        elif isinstance(message, AIMessage) and message.content:
            print(f"  [done]  {message.content.strip()[:300]}")


if __name__ == "__main__":
    graph = build_agent("shop-a")
    ask(graph, "Được đổi trả trong bao nhiêu ngày?")
    ask(graph, "Shop A có bán laptop không?")

    print("\nCâu thứ hai không có trong kho tài liệu.")
    print("Agent phải nói 'không đủ dữ liệu', không được bịa.")
