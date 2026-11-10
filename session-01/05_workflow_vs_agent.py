"""Bài 05 — Cùng một việc, hai cách làm: workflow hay agent?

Chạy:  python 05_workflow_vs_agent.py

Workflow = bạn viết cứng thứ tự các bước. Model chỉ làm từng bước nhỏ.
Agent    = bạn đưa mục tiêu + tool, model tự quyết gọi cái nào, khi nào.

Cả hai đều đúng. Câu hỏi không phải "cái nào xịn hơn" mà là
"bài toán này có cần model tự quyết không?".
"""

import json

from common.llm import chat, text, usage_line
from common.shop import TOOL_FUNCTIONS, TOOLS, check_return_policy, get_order_status

CAU_HOI = "Đơn 1234 của tôi đang ở đâu, và tai nghe tôi mua có được đổi trả không?"


# ---------------------------------------------------------------------------
# CÁCH 1: WORKFLOW — ta biết trước cần làm gì, viết thẳng ra.
# ---------------------------------------------------------------------------
def workflow():
    buoc = []

    don = get_order_status("1234")            # bước 1: luôn luôn chạy
    buoc.append("get_order_status(1234)")

    chinh_sach = check_return_policy("tai nghe")  # bước 2: luôn luôn chạy
    buoc.append("check_return_policy(tai nghe)")

    response = chat(                            # bước 3: model chỉ viết câu trả lời
        [
            {
                "role": "user",
                "content": (
                    f"Khách hỏi: {CAU_HOI}\n"
                    f"Dữ liệu tra được:\n- {don}\n- {chinh_sach}\n"
                    "Hãy trả lời ngắn gọn, thân thiện."
                ),
            }
        ]
    )
    return text(response), buoc, response


# ---------------------------------------------------------------------------
# CÁCH 2: AGENT — model tự chọn tool, ta chỉ chạy vòng lặp.
# ---------------------------------------------------------------------------
def agent(max_buoc=5):
    messages = [{"role": "user", "content": CAU_HOI}]
    buoc = []

    for _ in range(max_buoc):
        response = chat(messages, tools=TOOLS)
        message = response.choices[0].message

        if not message.tool_calls:          # model thấy đủ thông tin -> trả lời
            return text(response), buoc, response

        messages.append(message)
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            ket_qua = TOOL_FUNCTIONS[call.function.name](**args)
            buoc.append(f"{call.function.name}({args})")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": ket_qua}
            )

    return "(hết lượt)", buoc, None


print("=== CÁCH 1: WORKFLOW ===")
tra_loi_1, buoc_1, resp_1 = workflow()
print(tra_loi_1)
print(f"các bước: {buoc_1}")
print(usage_line(resp_1))
print()

print("=== CÁCH 2: AGENT ===")
tra_loi_2, buoc_2, resp_2 = agent()
print(tra_loi_2)
print(f"các bước: {buoc_2}")
print(usage_line(resp_2) if resp_2 else "")
print()

print("=== SO SÁNH ===")
print(f"{'':22} {'workflow':<22} {'agent':<22}")
print(f"{'ai quyết định':22} {'bạn (code cứng)':<22} {'model':<22}")
print(f"{'số bước':22} {len(buoc_1):<22} {len(buoc_2):<22}")
print()
print("Workflow: đoán trước được, dễ test, rẻ. Nhưng đổi yêu cầu là phải sửa code.")
print("Agent:    linh hoạt, chịu được câu hỏi lạ. Nhưng khó đoán và khó test hơn.")
print()
print("Quy tắc: chọn mức thấp nhất đủ dùng. Chỉ lên agent khi workflow bó tay.")
