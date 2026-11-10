"""Dữ liệu và công cụ dùng chung cho bài 05 và 06.

Đây là một cửa hàng giả lập. Mỗi "tool" chỉ là một hàm Python bình thường —
không có gì thần kỳ. Phần lớn công việc của một agent engineer là viết
những hàm như thế này cho thật tốt.
"""

ORDERS = {
    "1234": {"trang_thai": "đang giao", "du_kien": "mai 15:00", "mon_hang": "tai nghe"},
    "5678": {"trang_thai": "đã giao", "du_kien": "hôm qua", "mon_hang": "bàn phím"},
}

RETURN_POLICY = {
    "tai nghe": "Được đổi trả trong 7 ngày nếu còn hộp.",
    "bàn phím": "Được đổi trả trong 30 ngày nếu chưa bóc seal.",
}


def get_order_status(order_id: str) -> str:
    order = ORDERS.get(order_id)
    if order is None:
        return f"Không tìm thấy đơn {order_id}."
    return (
        f"Đơn {order_id}: {order['trang_thai']}, dự kiến {order['du_kien']}, "
        f"món {order['mon_hang']}."
    )


def check_return_policy(product: str) -> str:
    policy = RETURN_POLICY.get(product)
    if policy is None:
        return f"Chưa có chính sách đổi trả cho {product}."
    return f"{product}: {policy}"


def calc_refund(amount: int) -> str:
    return f"Hoàn lại {amount:,} đồng (đã gồm phí vận chuyển)."


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Tra trạng thái một đơn hàng theo mã đơn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Mã đơn, ví dụ 1234"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_return_policy",
            "description": "Xem chính sách đổi trả của một loại sản phẩm.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Tên sản phẩm"}
                },
                "required": ["product"],
            },
        },
    },
]

# Tên hàm -> hàm Python thật. Harness dùng bảng này để chạy tool.
TOOL_FUNCTIONS = {
    "get_order_status": get_order_status,
    "check_return_policy": check_return_policy,
}
