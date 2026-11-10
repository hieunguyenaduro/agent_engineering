"""Bài 02 — Model không có trí nhớ. "Memory" là do harness gửi lại lịch sử.

Chạy:  python 02_stateless.py

Hai lần gọi giống hệt nhau về phía model. Khác biệt duy nhất là
lần thứ hai ta gửi kèm câu trước đó trong mảng messages.
"""

from common.llm import chat, text

# Lượt 1: người dùng giới thiệu tên
turn_1 = {"role": "user", "content": "Chào bạn, mình tên là Minh."}

# Lượt 2: hỏi lại tên
turn_2 = {"role": "user", "content": "Mình tên gì?"}

print("=== A. Gửi RIÊNG câu hỏi (model không thấy lượt 1) ===")
a = chat([turn_2])
print(text(a))
print()

print("=== B. Gửi KÈM lịch sử (harness tự nhớ giúp) ===")
b = chat([turn_1, {"role": "assistant", "content": "Chào Minh!"}, turn_2])
print(text(b))
print()

print("Kết luận: model không nhớ gì giữa hai lần gọi.")
print("'Trí nhớ' chỉ là mảng messages ngày càng dài do harness giữ và gửi lại.")
