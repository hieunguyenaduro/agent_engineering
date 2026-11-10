"""Agent giả lập chạy hoàn toàn offline: retrieve → tool → answer.

Agent này không gọi LLM. Nó dùng luật từ khoá để chọn hành động, nhờ vậy kết quả
lặp lại được — điều kiện tiên quyết để viết eval và regression test.
Chạy thử:  python 01_trace_local.py
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from common.tracer import Tracer

ORDERS = {
    "1234": {"trang_thai": "đang giao", "du_kien": "mai 15:00", "mon_hang": "tai nghe"},
    "5678": {"trang_thai": "đã giao", "du_kien": "hôm qua", "mon_hang": "bàn phím"},
}
POLICIES = {
    "tai nghe": "Tai nghe được đổi trả trong 7 ngày nếu còn hộp.",
    "bàn phím": "Bàn phím được đổi trả trong 30 ngày nếu chưa bóc seal.",
}
DOCS = [
    {"id": "doc-order-status", "text": "Trạng thái đơn hàng tra bằng mã đơn, ví dụ 1234.", "tags": ["đơn", "order", "giao"]},
    {"id": "doc-policy-tai-nghe", "text": POLICIES["tai nghe"], "tags": ["tai nghe", "đổi trả", "policy"]},
    {"id": "doc-policy-ban-phim", "text": POLICIES["bàn phím"], "tags": ["bàn phím", "đổi trả", "policy"]},
    {"id": "doc-refund", "text": "Hoàn tiền phải do nhân viên duyệt; agent không tự hoàn.", "tags": ["hoàn tiền", "refund", "an toàn"]},
    {"id": "doc-scope", "text": "Cửa hàng chỉ hỗ trợ đơn hàng và đổi trả.", "tags": ["phạm vi", "scope"]},
]


@dataclass
class RunResult:
    question: str
    answer: str
    tool_calls: list[str] = field(default_factory=list)
    retrieved: list[str] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    scenario: str = "normal"


def _words(text: str) -> set[str]:
    return {word for word in re.findall(r"\w+", text.lower()) if len(word) > 2}

def retrieve(question: str) -> list[tuple[int, str]]:
    """Xếp hạng tài liệu bằng trùng từ khoá — thay cho vector search thật."""
    query = _words(question)
    scored = [
        (len(query & (_words(doc["text"]) | {tag.lower() for tag in doc["tags"]})), doc["id"])
        for doc in DOCS
    ]
    scored = [item for item in scored if item[0]]
    return sorted(scored, key=lambda item: (-item[0], item[1]))[:2]


def _order_id(question: str) -> str | None:
    match = re.search(r"\d{3,}", question)
    return match.group(0) if match else None
def _decide(question: str) -> tuple[str, str | None, dict]:
    lowered = question.lower()
    if any(key in lowered for key in ("hoàn tiền", "refund", "trả lại tiền")):
        return "refund_guard", None, {}
    order_id = _order_id(question)
    if order_id:
        return "tool", "get_order_status", {"order_id": order_id}
    if any(key in lowered for key in ("đổi trả", "bảo hành", "chính sách")):
        product = "tai nghe" if "tai nghe" in lowered else "bàn phím" if "bàn phím" in lowered else ""
        return "tool", "check_return_policy", {"product": product}
    if "chào" in lowered:
        return "smalltalk", None, {}
    return "out_of_scope", None, {}

def _get_order_status(order_id: str) -> str:
    order = ORDERS.get(order_id)
    if order is None:
        return f"Không tìm thấy đơn {order_id}."
    return f"Đơn {order_id}: {order['trang_thai']}, dự kiến {order['du_kien']}, món {order['mon_hang']}."
def _check_return_policy(product: str) -> str:
    return POLICIES.get(product, f"Chưa có chính sách đổi trả cho {product or 'sản phẩm này'}.")
def _issue_refund(order_id: str, amount: int) -> str:
    return f"Đã hoàn {amount:,} đồng cho đơn {order_id}."

_TOOLS = {"get_order_status": _get_order_status, "check_return_policy": _check_return_policy, "issue_refund": _issue_refund}
def _compose(action: str, tool_name: str | None, tool_result: str) -> str:
    if action == "refund_guard":
        return "Mình không thể tự hoàn tiền. Việc này cần nhân viên duyệt để tránh sai sót."
    if action == "smalltalk":
        return "Xin chào! Bạn muốn tra đơn hàng hay xem chính sách đổi trả?"
    if action == "out_of_scope":
        return "Mình chỉ hỗ trợ câu hỏi về đơn hàng và đổi trả, không hỗ trợ thời tiết."
    if action == "answer_direct":
        return "Mình chưa tra được dữ liệu, bạn thử lại sau nhé."
    if tool_name == "check_return_policy":
        return f"Theo chính sách: {tool_result}"
    if tool_name == "issue_refund":
        return f"{tool_result} (Đây là hành động không thể hoàn tác.)"
    return f"{tool_result} Bạn cần mình kiểm tra thêm gì không?"

def run_agent(question: str, scenario: str = "normal", tracer: Tracer | None = None) -> RunResult:
    """Chạy một lượt và ghi lại toàn bộ đường đi vào tracer."""
    tracer = tracer or Tracer("noop")
    started = time.perf_counter()
    action, tool_name, args = _decide(question)

    # Hai scenario cố tình hỏng, dùng ở bài 04 và 06 để thử evaluator.
    if scenario == "unsafe_refund" and action == "refund_guard":
        action, tool_name = "tool", "issue_refund"
        args = {"order_id": _order_id(question) or "1234", "amount": 250000}
    if scenario == "skip_tool" and action == "tool":
        action, tool_name, args = "answer_direct", None, {}

    result = RunResult(question=question, answer="", scenario=scenario)
    with tracer.span("agent.run", question=question, scenario=scenario) as root:
        with tracer.span("retrieve", query=question) as retrieve_span:
            hits = retrieve(question)
            with tracer.span("vector.search", collection="support-docs", top_k=2) as search_span:
                search_span.attributes["hits"] = [doc_id for _, doc_id in hits]
            retrieve_span.attributes["docs"] = [doc_id for _, doc_id in hits]
            retrieve_span.attributes["scores"] = [score for score, _ in hits]
        with tracer.span("llm.plan", action=action, tool=tool_name or "none"):
            pass
        tool_result = ""
        if tool_name:
            with tracer.span(f"tool.{tool_name}", tool=tool_name, args=args) as tool_span:
                try:
                    tool_result = _TOOLS[tool_name](**args)
                    tool_span.attributes["ok"] = True
                except Exception as exc:  # tool lỗi không được làm sập cả trace
                    tool_result = f"Tool lỗi: {exc}"
                    tool_span.attributes["ok"] = False
                tool_span.attributes["result"] = tool_result
            result.tool_calls.append(tool_name)
        result.tokens_in = len(question.split()) + 40
        with tracer.span("answer", tokens_in=result.tokens_in) as answer_span:
            if scenario == "slow":
                time.sleep(0.4)  # mô phỏng model chậm để evaluator latency bắt được
            result.answer = _compose(action, tool_name, tool_result)
            result.tokens_out = len(result.answer.split())
            answer_span.attributes["tokens_out"] = result.tokens_out
            answer_span.attributes["preview"] = result.answer[:60]
        result.retrieved = [doc_id for _, doc_id in hits]
        root.attributes["tool_calls"] = result.tool_calls
        root.attributes["docs"] = result.retrieved
        root.attributes["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)

    result.latency_ms = (time.perf_counter() - started) * 1000
    return result
