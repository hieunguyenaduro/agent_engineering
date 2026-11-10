"""Bài 01 — Tool là một API contract.

Chạy:  python 01_tool_contract.py

File in ra đúng phần mà model nhìn thấy: tên, mô tả, JSON Schema tham số,
kiểu trả về. Không gọi API, không cần key. So sánh một tool tệ và một tool tốt,
rồi chứng minh: hai implementation khác nhau nhưng cùng schema thì model
không thể phân biệt.
"""

import json

# ---------------------------------------------------------------------------
# 1. Tool tệ: tên mơ hồ, một tham số vô nghĩa, không nói khi nào dùng.
# ---------------------------------------------------------------------------
BAD_TOOL = {
    "name": "do_stuff",
    "description": "Xử lý dữ liệu.",
    "parameters": {
        "type": "object",
        "properties": {"data": {"type": "string"}},
        "required": ["data"],
    },
    "returns": "string",
}

# ---------------------------------------------------------------------------
# 2. Tool tốt: động từ rõ, tham số tối thiểu, mô tả nói cả khi nào KHÔNG dùng.
# ---------------------------------------------------------------------------
GOOD_TOOL = {
    "name": "search_orders",
    "description": (
        "Tìm đơn hàng của một khách theo mã khách, lọc được theo trạng thái. "
        "Dùng khi người dùng hỏi 'đơn của tôi đâu'. "
        "Không dùng để hoàn tiền — việc đó có tool riêng."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Mã khách, ví dụ C-1042.",
            },
            "status": {
                "type": "string",
                "enum": ["đang giao", "đã giao", "đã huỷ"],
                "description": "Lọc theo trạng thái; bỏ trống để lấy tất cả.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "default": 5,
                "description": "Số đơn tối đa trả về.",
            },
        },
        "required": ["customer_id"],
        "additionalProperties": False,
    },
    "returns": (
        "Chuỗi nhiều dòng, mỗi dòng một đơn: mã đơn, trạng thái, ngày. "
        "Không có kết quả thì trả 'Không tìm thấy đơn nào.'"
    ),
}


def show(title, spec):
    print(f"\n=== {title} ===")
    print(json.dumps(spec, ensure_ascii=False, indent=2))


def main():
    print("Model KHÔNG nhận code Python. Nó nhận đúng khối JSON dưới đây.")
    show("TOOL TỆ", BAD_TOOL)
    show("TOOL TỐT", GOOD_TOOL)

    print("\n=== Model nhìn thấy gì? ===")
    for label, spec in (("tệ", BAD_TOOL), ("tốt", GOOD_TOOL)):
        params = ", ".join(spec["parameters"]["properties"])
        print(f"- {label:4} tên={spec['name']:14} tham số={params}")
        print(f"       mô tả={spec['description'][:70]}...")

    print("\n=== Cùng schema, khác code ===")
    orders = [{"id": "1234", "status": "đang giao"}]

    def search_orders_dung(customer_id, status=None, limit=5):
        return [o for o in orders if status is None or o["status"] == status][:limit]

    def search_orders_hong(customer_id, status=None, limit=5):
        return []          # bug: quên lọc, luôn trả rỗng

    for fn in (search_orders_dung, search_orders_hong):
        print(f"  {fn.__name__:22} -> {fn('C-1042')}")

    print("\nKết luận:")
    print("  - Schema của hai hàm giống hệt nhau, vì schema chỉ là hợp đồng.")
    print("  - Model không đọc được code, nên không biết hàm nào đúng.")
    print("  - Vì vậy: tên, mô tả, kiểu là thứ DUY NHẤT model dùng để chọn tool.")
    print("  - Còn code đúng hay sai thì phải kiểm bằng test, không bằng model.")


if __name__ == "__main__":
    main()
