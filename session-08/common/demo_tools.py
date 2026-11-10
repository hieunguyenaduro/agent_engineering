"""Tool mẫu và guard đã cấu hình — dùng cho bài 04 và bộ test.

Tool ở đây không chạm hệ thống thật. Chúng in ra/trả về chuỗi để bạn thấy
quyết định của guard, không phải để demo một API thật.
"""

from .audit import AuditLog
from .tool_guard import Actor, ToolGuard, ToolSpec

# Nhân viên CSKH: đọc đơn, hoàn tiền, đọc web nội bộ. Không được xoá khách,
# không được gửi email ra ngoài.
SUPPORT = Actor(
    user_id="u-100",
    tenant_id="acme",
    permissions=frozenset({"orders:read", "refund:write", "web:read"}),
)


def search_orders(query: str):
    return [
        {"order_id": "1234", "status": "đang giao", "query": query},
        {"order_id": "5678", "status": "đã giao", "query": query},
    ]


def refund(order_id: str, amount: int):
    formatted = f"{amount:,}".replace(",", ".")
    return f"Đã hoàn {formatted} đồng cho đơn {order_id}."


def delete_customer(customer_id: str):
    return f"Đã xoá khách {customer_id} (demo)."


def fetch_url(url: str):
    return f"(demo) Nội dung tải từ {url}"


def send_email(to: str, body: str):
    return f"(demo) Đã gửi email tới {to}."


def build_guard(audit_path=None, search_limit: int = 2):
    """Trả về (guard, audit) mới, để mỗi bài/test có trạng thái riêng."""
    audit = AuditLog(audit_path)
    specs = [
        ToolSpec("search_orders", "orders:read", search_orders,
                 rate_limit=search_limit),
        ToolSpec("refund", "refund:write", refund, risk="high",
                 requires_approval=True, rate_limit=5),
        ToolSpec("delete_customer", "customers:delete", delete_customer,
                 risk="critical", requires_approval=True, rate_limit=1),
        ToolSpec("fetch_url", "web:read", fetch_url, rate_limit=3,
                 allowed_hosts=("api.shop.example",)),
        ToolSpec("send_email", "email:send", send_email, risk="high",
                 requires_approval=True, rate_limit=2),
    ]
    return ToolGuard(specs, audit), audit
