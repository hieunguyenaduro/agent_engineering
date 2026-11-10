"""Dữ liệu và luật nghiệp vụ của cửa hàng, dùng chung cho cả buổi 3.

Không phụ thuộc thư viện ngoài. Nhờ vậy các ví dụ vẫn chạy khi máy chưa cài
langchain hay mcp. Hàm nào cũng trả về chuỗi: lỗi là dữ liệu, không phải
exception — đúng nguyên tắc của buổi này.
"""

ORDERS = {
    "1234": {
        "status": "đang giao",
        "eta": "mai 15:00",
        "product": "tai nghe",
        "amount": 850_000,
        "days_since_delivery": None,
    },
    "5678": {
        "status": "đã giao",
        "eta": "3 ngày trước",
        "product": "bàn phím",
        "amount": 1_200_000,
        "days_since_delivery": 3,
    },
    "9012": {
        "status": "đã giao",
        "eta": "10 ngày trước",
        "product": "tai nghe",
        "amount": 650_000,
        "days_since_delivery": 10,
    },
    "3456": {
        "status": "đã giao",
        "eta": "40 ngày trước",
        "product": "chuột",
        "amount": 300_000,
        "days_since_delivery": 40,
    },
}

# Số ngày được đổi trả của từng loại sản phẩm.
RETURN_WINDOW = {"tai nghe": 7, "bàn phím": 30, "chuột": 30}

RETURN_POLICY_TEXT = """Chính sách đổi trả của cửa hàng

- Tai nghe: đổi trả trong 7 ngày kể từ khi giao, còn đủ hộp.
- Bàn phím: đổi trả trong 30 ngày, chưa bóc seal.
- Chuột: đổi trả trong 30 ngày, còn tem bảo hành.
- Quá hạn: hoàn tối đa 50% nếu còn trong gấp đôi thời hạn, sau đó không hoàn.
- Đơn chưa giao: chưa thể hoàn tiền, chỉ được huỷ đơn.
"""


def vnd(amount: int) -> str:
    """Định dạng tiền theo kiểu Việt Nam: 850.000 thay vì 850,000."""
    return f"{amount:,}".replace(",", ".") + " đồng"


def order_line(order_id: str) -> str:
    """Trả về một dòng mô tả đơn, hoặc chuỗi bắt đầu bằng 'LỖI:'."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"LỖI: không tìm thấy đơn {order_id}."
    return (
        f"Đơn {order_id}: {order['status']}, {order['eta']}, "
        f"món {order['product']}, {vnd(order['amount'])}."
    )


def refund_quote(order_id: str) -> str:
    """Tính số tiền có thể hoàn, kèm lý do. Không thực hiện chuyển tiền."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"LỖI: không tìm thấy đơn {order_id}."

    days = order["days_since_delivery"]
    if days is None:
        return f"LỖI: đơn {order_id} chưa giao, chưa thể hoàn tiền."

    window = RETURN_WINDOW.get(order["product"], 7)
    if days <= window:
        amount, rule = order["amount"], f"trong hạn {window} ngày"
    elif days <= window * 2:
        amount, rule = order["amount"] // 2, f"quá hạn {window} ngày, còn trong gấp đôi"
    else:
        amount, rule = 0, f"quá hạn {window} ngày"

    return (
        f"Đơn {order_id} ({order['product']}, giao {days} ngày trước): "
        f"hoàn {vnd(amount)} — {rule}."
    )
