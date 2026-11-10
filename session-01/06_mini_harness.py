"""Bài 06 — Mini harness: hạt giống của mọi agent.

Chạy:  python 06_mini_harness.py

Đây là một agent hoàn chỉnh ở mức nhỏ nhất, khoảng 100 dòng, gồm đủ 6 phần:

    1. Model          - gọi API
    2. Tools          - hàm Python + mô tả cho model
    3. Loop           - Observe -> Think -> Act -> Verify, có giới hạn số bước
    4. Context        - system prompt + lịch sử hội thoại
    5. Memory         - history được giữ giữa các lượt hỏi
    6. Observability  - in trace và lưu lại để xem sau

Cả khóa học sẽ làm dày đúng 6 phần này lên. Không có phép màu nào khác.
"""

import json
import os
from datetime import datetime

from common.llm import MODEL, chat, text
from common.shop import TOOL_FUNCTIONS, TOOLS

MAX_STEPS = 5  # chốt an toàn: không bao giờ cho agent chạy vô hạn

SYSTEM_PROMPT = """Bạn là trợ lý chăm sóc khách hàng của một cửa hàng phụ kiện máy tính.

Quy tắc:
- Luôn tra dữ liệu bằng tool trước khi trả lời. Không đoán.
- Nếu tool không tìm thấy thông tin, nói thật là không tìm thấy.
- Trả lời ngắn gọn, thân thiện, bằng tiếng Việt."""


class Harness:
    def __init__(self):
        self.history = []          # memory giữa các lượt
        self.trace = []            # nhật ký của lượt hiện tại
        self.total_in = 0
        self.total_out = 0

    # -- vòng lặp chính ----------------------------------------------------
    def ask(self, question: str) -> str:
        messages = (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + self.history
            + [{"role": "user", "content": question}]
        )
        self.trace = []
        evidence = []

        for step in range(1, MAX_STEPS + 1):
            self._log(f"--- Bước {step} ---")
            response = chat(messages, tools=TOOLS)
            self._count(response)
            message = response.choices[0].message

            if not message.tool_calls:
                answer = text(response)
                self._log(f"[done]    model trả lời: {answer[:80]}...")
                return self._finish(question, answer, evidence, messages)

            # THINK: model nói nó muốn gọi gì
            for call in message.tool_calls:
                self._log(f"[think]   muốn gọi {call.function.name}({call.function.arguments})")

            # ACT: ta chạy tool thật
            messages.append(message)
            for call in message.tool_calls:
                args = json.loads(call.function.arguments)
                result = TOOL_FUNCTIONS[call.function.name](**args)
                evidence.append(result)

                # OBSERVE: kết quả được đưa ngược lại vào context
                self._log(f"[act]     chạy -> {result}")
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": result}
                )

        # Hết số bước mà model vẫn chưa chịu trả lời
        return self._finish(question, "(dừng: quá số bước cho phép)", evidence, messages)

    # -- verify: kiểm tra câu trả lời có dùng đúng dữ kiện không ------------
    def _finish(self, question, answer, evidence, messages):
        if evidence and not any(ch.isdigit() for ch in answer):
            self._log("[verify]  câu trả lời thiếu dữ kiện -> nhắc model sửa một lần")
            messages = messages + [
                {"role": "user", "content": "Câu trả lời cần nêu rõ mã đơn và trạng thái."}
            ]
            response = chat(messages, tools=TOOLS)
            self._count(response)
            answer = text(response)
        else:
            self._log("[verify]  ok")

        self.history += [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
        return answer

    # -- observability -----------------------------------------------------
    def _log(self, line: str):
        print(line)
        self.trace.append(line)

    def _count(self, response):
        usage = getattr(response, "usage", None)
        if usage:
            self.total_in += usage.prompt_tokens
            self.total_out += usage.completion_tokens

    def save_trace(self, path="traces/last_run.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "model": MODEL,
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "steps": self.trace,
                    "history_turns": len(self.history) // 2,
                    "tokens": {"in": self.total_in, "out": self.total_out},
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"[trace]   đã lưu vào {path}")


if __name__ == "__main__":
    agent = Harness()

    print("=== Lượt 1 ===")
    print("Khách:", "Đơn 1234 của tôi đang ở đâu?")
    tra_loi = agent.ask("Đơn 1234 của tôi đang ở đâu?")
    print("Agent:", tra_loi)
    print()

    print("=== Lượt 2 (kiểm tra memory) ===")
    print("Khách:", "Còn đơn 5678 thì sao?")
    tra_loi = agent.ask("Còn đơn 5678 thì sao?")
    print("Agent:", tra_loi)
    print()

    agent.save_trace()
    print(f"Tổng token: {agent.total_in} vào / {agent.total_out} ra")
    print()
    print("Thử ngay: mở traces/last_run.json và đọc lại từng bước agent đã làm.")
