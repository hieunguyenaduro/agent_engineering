"""Bài 04 — Tool calling: model KHÔNG chạy code. Nó chỉ xin phép.

Chạy:  python 04_tool_calling.py

Luồng thật sự diễn ra 3 bước:
    1. Ta đưa model danh sách tool + câu hỏi.
    2. Model trả về "tôi muốn gọi get_weather(city='Hà Nội')" — không có chữ nào.
    3. TA tự chạy hàm Python, gửi kết quả lại, model mới viết câu trả lời.

Bước 2 là chỗ hay bị hiểu nhầm nhất. Model không có quyền chạy gì trên máy bạn.
"""

import json

from common.llm import chat, text, tool_calls, usage_line

# ---------------------------------------------------------------------------
# 1. Mô tả tool cho model biết nó có thể xin gọi những gì.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Lấy thời tiết hiện tại của một thành phố.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Tên thành phố, ví dụ Hà Nội"}
                },
                "required": ["city"],
            },
        },
    }
]


# ---------------------------------------------------------------------------
# 2. Hàm Python thật. Chỉ có ta chạy được nó.
# ---------------------------------------------------------------------------
def get_weather(city: str) -> str:
    du_lieu_gia = {"Hà Nội": "28°C, nhiều mây", "Đà Nẵng": "31°C, nắng"}
    return du_lieu_gia.get(city, "Không có dữ liệu")


# ---------------------------------------------------------------------------
# 3. Bước 1: hỏi model, kèm danh sách tool.
# ---------------------------------------------------------------------------
messages = [{"role": "user", "content": "Thời tiết Hà Nội hôm nay thế nào?"}]
first = chat(messages, tools=TOOLS)

message = first.choices[0].message
print("=== Model trả về gì ở lần gọi đầu ===")
print(f"content: {message.content!r}   <-- rỗng, chưa có câu trả lời nào")
for call in tool_calls(first):
    print(f"model xin gọi: {call.function.name}({call.function.arguments})")
print(usage_line(first))
print()

# ---------------------------------------------------------------------------
# 4. Bước 2: TA chạy hàm. Model không hề chạy gì cả.
# ---------------------------------------------------------------------------
call = tool_calls(first)[0]
args = json.loads(call.function.arguments)
ket_qua = get_weather(**args)
print(f"=== Ta tự chạy get_weather(city={args['city']!r}) ===")
print(f"kết quả: {ket_qua}")
print()

# ---------------------------------------------------------------------------
# 5. Bước 3: gửi kết quả lại cho model để nó viết câu trả lời cuối.
# ---------------------------------------------------------------------------
messages.append(message)                                  # lượt "xin gọi tool"
messages.append(
    {"role": "tool", "tool_call_id": call.id, "content": ket_qua}
)
second = chat(messages, tools=TOOLS)

print("=== Câu trả lời cuối cùng ===")
print(text(second))
print(usage_line(second))
