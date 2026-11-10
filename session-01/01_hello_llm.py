"""Bài 01 — Model chỉ là một hàm: văn bản vào, văn bản ra.

Chạy:  python 01_hello_llm.py

Điều duy nhất cần nhớ sau bài này:
    Model KHÔNG tự làm gì cả. Bạn đưa chữ vào, nó trả chữ ra.
    Mọi thứ "thần kỳ" còn lại là do harness (phần mềm bọc quanh model) làm.
"""

from common.llm import chat, text, usage_line

messages = [
    {"role": "user", "content": "Giải thích trong đúng 2 câu: AI agent là gì?"}
]

response = chat(messages)

print("=== Model trả lời ===")
print(text(response))
print()
print("=== Chi phí của lần gọi này ===")
print(usage_line(response))
