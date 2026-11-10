"""Dữ liệu và tool của cửa hàng giả lập (giống buổi 1, thêm tool hoàn tiền)."""

from langchain_core.tools import tool

ORDERS = {
    "1234": {"trang_thai": "đang giao", "du_kien": "mai 15:00", "mon_hang": "tai nghe"},
    "5678": {"trang_thai": "đã giao", "du_kien": "hôm qua", "mon_hang": "bàn phím"},
}

RETURN_POLICY = {
    "tai nghe": "Được đổi trả trong 7 ngày nếu còn hộp.",
    "bàn phím": "Được đổi trả trong 30 ngày nếu chưa bóc seal.",
}


@tool
def get_order_status(order_id: str) -> str:
    """Tra trạng thái một đơn hàng theo mã đơn, ví dụ 1234."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"Không tìm thấy đơn {order_id}."
    return (
        f"Đơn {order_id}: {order['trang_thai']}, dự kiến {order['du_kien']}, "
        f"món {order['mon_hang']}."
    )


@tool
def check_return_policy(product: str) -> str:
    """Xem chính sách đổi trả của một loại sản phẩm, ví dụ 'tai nghe'."""
    policy = RETURN_POLICY.get(product)
    if policy is None:
        return f"Chưa có chính sách đổi trả cho {product}."
    return f"{product}: {policy}"


@tool
def issue_refund(order_id: str, amount: int) -> str:
    """Hoàn tiền cho một đơn hàng. ĐÂY LÀ HÀNH ĐỘNG KHÔNG THỂ HOÀN TÁC."""
    return f"Đã hoàn {amount:,} đồng cho đơn {order_id}."


TOOLS = [get_order_status, check_return_policy, issue_refund]
TOOL_FUNCTIONS = {
    "get_order_status": get_order_status,
    "check_return_policy": check_return_policy,
    "issue_refund": issue_refund,
}
