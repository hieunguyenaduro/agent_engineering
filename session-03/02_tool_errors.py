"""Bài 02 — Khi tool lỗi: timeout, retry, và lỗi là dữ liệu.

Chạy:  python 02_tool_errors.py

Hai kịch bản:
    A. Tool hỏng tạm thời (2 lần đầu), lần thứ 3 thành công -> retry cứu được.
    B. Tool treo vĩnh viễn -> timeout, trả chuỗi "LỖI: ...", agent vẫn trả lời.

Điểm cần thấy: model không bao giờ nhận exception. Nó nhận một chuỗi, và vì
vậy nó vẫn có thể nói với người dùng điều gì đã xảy ra.
"""

import queue
import threading
import time

from common.fake_model import FakeToolModel
from common.shop import order_line

TIMEOUT = 1.0          # giây, ví dụ nhỏ cho dễ thấy
MAX_ATTEMPTS = 3       # gồm cả lần đầu
ATTEMPTS = {"count": 0}  # đếm để giả lập tool hỏng tạm thời


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------
def get_order_status(order_id: str) -> str:
    """Tra đơn. Hai lần gọi đầu cố tình hỏng để thấy retry."""
    ATTEMPTS["count"] += 1
    if ATTEMPTS["count"] < 3:
        raise TimeoutError("máy chủ đơn hàng không phản hồi")
    return order_line(order_id)


def get_order_status_treo(order_id: str) -> str:
    """Tool treo: mô phỏng dịch vụ bên ngoài không bao giờ trả lời."""
    time.sleep(2)
    return order_line(order_id)


# ---------------------------------------------------------------------------
# Lớp bọc: timeout + retry
# ---------------------------------------------------------------------------
def call_with_timeout(fn, args, timeout=TIMEOUT):
    """Chạy fn trong thread riêng, không đợi quá timeout.

    Thread là daemon: nếu tool treo, tiến trình vẫn thoát được. Cách này chỉ
    bảo vệ phía gọi; muốn kill thật thì phải dùng subprocess — xem bài 04.
    """
    box = queue.Queue()

    def runner():
        try:
            box.put(("ok", fn(**args)))
        except Exception as exc:                      # noqa: BLE001
            box.put(("err", f"{type(exc).__name__}: {exc}"))

    threading.Thread(target=runner, daemon=True).start()
    try:
        kind, value = box.get(timeout=timeout)
    except queue.Empty:
        return f"LỖI: tool không trả lời sau {timeout:g}s (timeout)."
    if kind == "err":
        return f"LỖI: {value}"
    return value


def call_with_retry(fn, args, attempts=MAX_ATTEMPTS):
    """Thử lại có giới hạn. Lỗi cuối cùng trả về dưới dạng chuỗi."""
    result = ""
    for attempt in range(1, attempts + 1):
        result = call_with_timeout(fn, args)
        if not result.startswith("LỖI:"):
            return result
        print(f"[retry]   lần {attempt}/{attempts}: {result}")
        time.sleep(0.05 * attempt)                    # backoff nhỏ, có giới hạn
    return result


# ---------------------------------------------------------------------------
# Harness tối giản: model xin gọi, harness chạy
# ---------------------------------------------------------------------------
def run_agent(question, tool_fn, tool_name="get_order_status"):
    model = FakeToolModel([tool_name], plan=[(tool_name, {"order_id": "1234"})])
    messages = [{"role": "user", "content": question}]

    for step in range(1, 4):
        reply = model.respond(messages)
        messages.append(reply)
        calls = reply.get("tool_calls") or []
        if not calls:
            print(f"[done]    {reply['content']}")
            return reply["content"]

        for call in calls:
            print(f"[think]   bước {step}: muốn gọi {call['name']}({call['args']})")
            result = call_with_retry(tool_fn, call["args"])
            print(f"[act]     kết quả -> {result}")
            messages.append(
                {"role": "tool", "tool_call_id": call["id"], "content": result}
            )

    print("[done]    dừng: quá số bước")
    return ""


def main():
    question = "Đơn 1234 của tôi đang ở đâu?"

    print("=== A. Tool hỏng tạm thời rồi thành công ===")
    ATTEMPTS["count"] = 0
    run_agent(question, get_order_status)

    print("\n=== B. Tool treo vĩnh viễn: lỗi thành dữ liệu ===")
    answer = run_agent(question, get_order_status_treo)
    print("[verify]  agent vẫn trả lời, không traceback:", bool(answer))

    print("\nBài học:")
    print("  - Retry nằm trong lớp bọc quanh tool, không nằm trong model.")
    print("  - Timeout phải có, nếu không một tool treo sẽ treo cả agent.")
    print("  - Lỗi trả về là chuỗi để model đọc được; exception là để lập trình viên đọc.")


if __name__ == "__main__":
    main()
