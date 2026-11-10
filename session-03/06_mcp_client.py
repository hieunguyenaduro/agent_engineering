"""Bài 06 — MCP client: khám phá capability rồi gọi tool.

Chạy:  python 06_mcp_client.py

Client tự khởi chạy 05_mcp_server.py qua stdio, nói lời chào (initialize),
liệt kê tool, gọi một tool, đọc một resource. Đây đúng là chuỗi bước mà một
host (Claude Desktop, IDE, agent runtime) làm khi kết nối tới MCP server.

Nếu máy chưa cài package `mcp`, file in hướng dẫn rồi thoát — không traceback.
"""

import asyncio
import sys
from pathlib import Path

SERVER = Path(__file__).with_name("05_mcp_server.py")

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None


async def demo() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER), "--serve"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            info = await session.initialize()
            server_info = getattr(info, "serverInfo", None)
            name = getattr(server_info, "name", "?")
            version = getattr(server_info, "version", "?")
            print(f"[mcp] đã kết nối: {name} {version}")

            print("\n=== Capability discovery: server có gì? ===")
            listed = await session.list_tools()
            for tool in listed.tools:
                first_line = (tool.description or "").strip().splitlines()[0]
                params = list((tool.inputSchema or {}).get("properties", {}))
                print(f"- {tool.name}({', '.join(params)})")
                print(f"    {first_line}")
                print(f"    schema: {tool.inputSchema}")

            print("\n=== Gọi tool ===")
            result = await session.call_tool(
                "get_order_status", {"order_id": "1234"}
            )
            for block in result.content:
                print(f"[tool] {getattr(block, 'text', block)}")

            print("\n=== Đọc resource ===")
            resource = await session.read_resource("policy://shop/returns")
            for block in resource.contents:
                text = getattr(block, "text", "")
                print(text.strip()[:400])

            print("\n[verify]  client không hề import code của server.")
            print("Nó chỉ biết tên tool, schema và URI resource — đó là toàn bộ MCP.")


def main() -> None:
    if ClientSession is None:
        print("Chưa có package 'mcp' nên chưa chạy được client.")
        print("Cài bằng:  pip install 'mcp>=1.2'")
        print("Sau đó chạy lại:  python 06_mcp_client.py")
        print()
        print("Server ở bài 05 vẫn đọc được mà không cần cài gì:")
        print("  python 05_mcp_server.py")
        return

    if not SERVER.exists():
        print(f"Không tìm thấy server: {SERVER}")
        return

    try:
        asyncio.run(asyncio.wait_for(demo(), timeout=25))
    except asyncio.TimeoutError:
        print("LỖI: client chờ quá 25s. Kiểm tra server có bị treo không.")
    except Exception as exc:                     # noqa: BLE001
        print(f"LỖI: không hoàn tất được phiên MCP: {type(exc).__name__}: {exc}")
        print("Gợi ý: chạy riêng 'python 05_mcp_server.py' để xem server báo gì,")
        print("và kiểm tra phiên bản mcp: pip show mcp")


if __name__ == "__main__":
    main()
