"""Agent tối giản dùng cho các bài API.

Không gọi model: mục tiêu buổi 9 là tầng phục vụ, không phải chất lượng câu trả lời.
Khi lên thật, thay `answer()` bằng graph.invoke và `stream_answer()` bằng
graph.stream(stream_mode="messages").
"""

import re
import time
from typing import Iterator


class AgentError(RuntimeError):
    """Lỗi nghiệp vụ có thể trả cho người dùng bằng thông điệp an toàn."""


ORDERS = {
    "1234": "đang giao, dự kiến mai 15:00",
    "5678": "đã giao hôm qua",
}


def answer(question: str, history: list[dict] | None = None) -> str:
    """Trả lời theo luật. Đây là chỗ bạn thay bằng agent thật."""
    text = question.lower().strip()
    if not text:
        raise AgentError("Câu hỏi rỗng.")

    match = re.search(r"\b(\d{4})\b", text)
    if match and any(word in text for word in ("đơn", "order", "giao")):
        order_id = match.group(1)
        status = ORDERS.get(order_id)
        if status is None:
            return f"Mình không tìm thấy đơn {order_id}."
        return f"Đơn {order_id}: {status}."

    if "hoàn tiền" in text:
        return "Mình đã ghi nhận yêu cầu hoàn tiền. Bộ phận chăm sóc khách hàng sẽ liên hệ trong 24h."

    if "giá" in text:
        return "Gói cơ bản 199k/tháng, gói pro 499k/tháng."

    turns = len(history or [])
    return f"Mình đã nhận câu hỏi: {question} (lượt thứ {turns + 1} trong phiên)."


def stream_answer(question: str) -> Iterator[str]:
    """Sinh từng mẩu chữ để bài SSE có dữ liệu thật."""
    for word in answer(question).split(" "):
        time.sleep(0.01)
        yield word + " "
