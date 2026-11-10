"""Model giả lập để dạy prompt injection mà không cần API key.

Model thật không "chạy" câu lệnh; nó dự đoán token tiếp theo. Nhưng khi chỉ thị
và dữ liệu nằm chung một chuỗi token, model không có cách nào tự biết đâu là
mệnh lệnh hợp lệ. Lớp giả lập này cố tình làm theo câu có dạng mệnh lệnh nằm
trong ngữ cảnh — đúng thất bại mà ta muốn học cách chặn.

    model = SimulatedModel()                    # dễ bị lừa
    model = SimulatedModel(trust_boundary=True) # biết bỏ qua vùng <untrusted>
"""

import re
from dataclasses import dataclass, field

from .guards import SYSTEM_PROMPT, strip_untrusted

EXFIL = re.compile(
    r"(?:gửi|send|forward|chuyển).{0,120}?([\w.+-]+@[\w.-]+\.\w+)",
    re.I | re.S,
)
REVEAL = re.compile(
    r"(?:in ra|tiết lộ|reveal|show|print).{0,40}?"
    r"(system prompt|api[_ ]?key|bí mật)",
    re.I | re.S,
)


@dataclass
class Action:
    kind: str                      # "tool" hoặc "answer"
    tool: str = ""
    args: dict = field(default_factory=dict)
    text: str = ""
    why: str = ""


class SimulatedModel:
    def __init__(self, trust_boundary: bool = False):
        self.trust_boundary = trust_boundary

    def decide(self, user_text: str, context: str = "",
               tools: set[str] | None = None,
               secret: str = "sk-demo-SECRET-123") -> Action:
        tools = tools or set()

        # Chỉ thị hợp lệ chỉ đến từ người dùng. Nếu bật trust boundary,
        # phần nằm trong <untrusted> bị loại khỏi vùng ra quyết định.
        command_zone = user_text or ""
        if not self.trust_boundary:
            command_zone += "\n" + (context or "")
        else:
            command_zone += "\n" + strip_untrusted(context or "")

        exfil = EXFIL.search(command_zone)
        if exfil and "send_email" in tools:
            return Action(
                kind="tool",
                tool="send_email",
                args={
                    "to": exfil.group(1),
                    "body": f"Hội thoại + bí mật: {secret}",
                },
                why="thấy mệnh lệnh gửi dữ liệu trong vùng được coi là chỉ thị",
            )

        if REVEAL.search(command_zone):
            return Action(
                kind="answer",
                text=f"System prompt của tôi là: {SYSTEM_PROMPT}",
                why="làm theo yêu cầu tiết lộ",
            )

        return Action(
            kind="answer",
            text="Mình chỉ trả lời về đơn hàng, hoàn tiền và đổi trả.",
            why="không có chỉ thị lạ trong vùng tin cậy",
        )
