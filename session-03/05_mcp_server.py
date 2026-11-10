"""Bài 05 — MCP server: biến tool thành dịch vụ dùng chung.

Chạy thường:   python 05_mcp_server.py
    -> in ra danh sách capability và cách chạy, không mở server (tiện cho lab).

Chạy thật:     python 05_mcp_server.py --serve
    -> server nói giao thức MCP qua stdio; client ở bài 06 sẽ gọi.

Server có 2 tool và 1 resource:
    tool      get_order_status(order_id)
    tool      quote_refund(order_id)
    resource  policy://shop/returns

Ghi chú bearer token khi chạy HTTP (không bắt buộc cho buổi này):
    mcp.run(transport="streamable-http") mở cổng mạng, khác hẳn stdio.
    Lúc đó phải thêm lớp xác thực: FastMCP nhận token_verifier + auth settings
    để kiểm tra Authorization: Bearer <token>, và bạn nên giới hạn scope theo
    từng tool (ví dụ chỉ role "support" được gọi quote_refund). Cú pháp cụ thể
    thay đổi theo phiên bản mcp — đọc mcp/server/fastmcp/server.py trước khi dùng.
    Với stdio, không có cổng mạng: quyền nằm ở tiến trình được phép khởi chạy.
    Token tĩnh chỉ đủ cho server nội bộ; ra Internet nên dùng OAuth 2.1.
"""

import sys
from datetime import datetime
from pathlib import Path

# Để client chạy server từ thư mục khác vẫn import được common/.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.shop import RETURN_POLICY_TEXT, order_line, refund_quote  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:                     # máy chưa cài mcp
    FastMCP = None


def audit(tool: str, **kwargs) -> None:
    """Audit log tối thiểu. Ghi ra stderr vì stdout là kênh giao thức."""
    stamp = datetime.now().isoformat(timespec="seconds")
    print(f"[audit] {stamp} tool={tool} args={kwargs}", file=sys.stderr)


def build_server():
    mcp = FastMCP("shop-tools")

    @mcp.tool()
    def get_order_status(order_id: str) -> str:
        """Tra trạng thái một đơn hàng theo mã đơn, ví dụ 1234."""
        audit("get_order_status", order_id=order_id)
        return order_line(order_id)

    @mcp.tool()
    def quote_refund(order_id: str) -> str:
        """Tính số tiền có thể hoàn cho một đơn. Chỉ báo giá, không chuyển tiền."""
        audit("quote_refund", order_id=order_id)
        return refund_quote(order_id)

    @mcp.resource("policy://shop/returns")
    def returns_policy() -> str:
        """Chính sách đổi trả, để client đọc làm ngữ cảnh."""
        return RETURN_POLICY_TEXT

    return mcp


def usage() -> None:
    print("MCP server của cửa hàng — 2 tool, 1 resource")
    print("  tool      get_order_status(order_id: str)")
    print("  tool      quote_refund(order_id: str)")
    print("  resource  policy://shop/returns")
    print()
    print("Chạy server thật (stdio):")
    print("  python 05_mcp_server.py --serve")
    print()
    print("Hoặc để client bài 06 tự khởi chạy:")
    print("  python 06_mcp_client.py")
    print()
    print("Khi chạy HTTP, nhớ thêm bearer token và phân quyền theo tool —")
    print("xem ghi chú ở đầu file này.")


def main() -> None:
    if FastMCP is None:
        print("Chưa có package 'mcp' nên chưa chạy được server.")
        print("Cài bằng:  pip install 'mcp>=1.2'")
        print("Sau đó chạy lại:  python 05_mcp_server.py")
        print()
        print("Phần còn lại của bài (hợp đồng tool, SQL, sandbox) không cần mcp.")
        return

    if "--serve" not in sys.argv:
        usage()
        return

    server = build_server()
    print("[mcp] shop-tools đang chạy qua stdio. Log đi stderr.", file=sys.stderr)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
