"""Model giả lập cho các ví dụ không có API key.

Nó nói đúng giao thức tool call ở mức dict: model trả về
{"role": "assistant", "tool_calls": [{"id", "name", "args"}]} và harness là
bên chạy hàm thật. Cùng ý tưởng với FakeToolModel của buổi 2, nhưng viết bằng
Python thuần để buổi 3 không phụ thuộc langchain-core.

Nó không thông minh: chỉ làm theo kịch bản, hoặc đoán theo từ khoá.
"""

import re


class FakeToolModel:
    def __init__(self, tool_names, plan=None):
        self.tool_names = list(tool_names)
        self.plan = list(plan or [])   # danh sách (tên_tool, args) cần gọi
        self._seq = 0

    def respond(self, messages):
        """Nhận lịch sử hội thoại, trả về một message của assistant."""
        last = messages[-1]

        # Đã có kết quả tool: tổng hợp thành câu trả lời cuối.
        if last["role"] == "tool" and not self.plan:
            return self._final_answer(last["content"])

        if self.plan:
            name, args = self.plan.pop(0)
            return self._call(name, args)

        text = last.get("content", "")
        digits = "".join(ch for ch in text if ch.isdigit())[:4]
        if "get_order_status" in self.tool_names and digits:
            return self._call("get_order_status", {"order_id": digits})

        return {
            "role": "assistant",
            "content": f"(giả lập) Mình chưa gọi tool nào. Câu hỏi: {text}",
        }

    # -- chi tiết -----------------------------------------------------------
    def _call(self, name, args):
        self._seq += 1
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": f"call_{name}_{self._seq}", "name": name, "args": args}
            ],
        }

    @staticmethod
    def _final_answer(tool_result):
        # Đây là chỗ dạy học viên: tool lỗi vẫn phải có câu trả lời tử tế.
        if tool_result.startswith("LỖI:"):
            reason = tool_result[len("LỖI:"):].strip().rstrip(".")
            return {
                "role": "assistant",
                "content": (
                    f"Mình chưa lấy được dữ liệu ({reason}). "
                    "Bạn thử lại sau ít phút, hoặc gửi mã đơn để mình kiểm tra lại."
                ),
            }
        return {
            "role": "assistant",
            "content": f"Dựa trên dữ liệu vừa tra: {tool_result}",
        }


def digits_of(text: str) -> str:
    """Tiện ích nhỏ để các ví dụ lấy mã đơn từ câu hỏi."""
    return "".join(re.findall(r"\d", text))[:4]
