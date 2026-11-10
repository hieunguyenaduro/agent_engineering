"""Bài 03 — "Suy nghĩ" là một khoản ngân sách, không phải phép màu.

Chạy:  python 03_reasoning.py

Ba cách trả lời cùng một câu hỏi mẹo:
    A. Trả lời ngay          -> nhanh, rẻ, dễ sai
    B. Yêu cầu suy nghĩ từng bước -> cùng model, đúng hơn, tốn hơn một chút
    C. Model reasoning thật  -> đúng hơn nữa, tốn hơn nhiều (nếu key của bạn có)

Bài học: đừng bật "suy nghĩ" cho mọi việc. Việc dễ thì trả lời thẳng.
"""

from common.llm import MODEL, REASONING_MODEL, chat, text, usage_line

# Câu hỏi mẹo kinh điển: đáp án đúng là 8 ngày, không phải 10 ngày.
CAU_HOI = (
    "Một con ốc sên leo cái cột cao 10 mét. Ban ngày nó leo được 3 mét, "
    "ban đêm tụt xuống 2 mét. Hỏi sau bao nhiêu ngày thì nó lên tới đỉnh cột?"
)

print("=== A. Trả lời ngay ===")
a = chat([{"role": "user", "content": CAU_HOI + " Chỉ trả lời đáp án, không giải thích."}])
print(text(a))
print(usage_line(a))
print()

print("=== B. Yêu cầu suy nghĩ từng bước (vẫn model cũ) ===")
b = chat(
    [
        {
            "role": "user",
            "content": CAU_HOI + " Hãy suy nghĩ từng bước, rồi chốt đáp án.",
        }
    ]
)
print(text(b))
print(usage_line(b))
print()

print(f"=== C. Model reasoning thật ({REASONING_MODEL}) ===")
try:
    c = chat(
        [{"role": "user", "content": CAU_HOI}],
        model=REASONING_MODEL,
    )
    print(text(c))
    print(usage_line(c))
except Exception as error:  # key chưa có quyền dùng model này
    print(f"Bỏ qua phần C — key của bạn chưa gọi được {REASONING_MODEL}.")
    print(f"Lý do: {type(error).__name__}: {error}")

print()
print(f"(Model thường đang dùng: {MODEL})")
print("Quan sát: cùng một model, chỉ thêm câu 'suy nghĩ từng bước' mà kết quả khác.")
print("Đó là context engineering — bài của buổi 4.")
