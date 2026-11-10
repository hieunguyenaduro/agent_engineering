"""Bài 03 — SQL tool chỉ đọc: chặn trước, giới hạn sau.

Chạy:  python 03_sql_readonly.py

SQLite trong bộ nhớ, bảng đơn hàng mẫu. Hàm run_select() là "tool" mà agent
được phép gọi. Nó chỉ cho SELECT/WITH, chặn dấu ';', chặn từ khoá ghi/xoá,
tự thêm LIMIT, và cắt câu chạy quá lâu.

Demo 4 câu: 1 hợp lệ, 3 bị chặn. Cuối file kiểm tra bảng vẫn còn nguyên.
"""

import re
import sqlite3
import time

MAX_ROWS = 20          # trần số dòng trả về
TIME_BUDGET = 0.5      # giây, ví dụ; production nên đặt ở tầng database

# Chặn theo từ khoá. Đây là lớp thứ hai, không phải lớp duy nhất: quyền của
# user database mới là thứ không thể vượt qua bằng câu SQL khéo.
FORBIDDEN = (
    "insert", "update", "delete", "drop", "alter", "create", "replace",
    "attach", "detach", "pragma", "vacuum", "reindex", "trigger",
)

SCHEMA = """CREATE TABLE orders (
    id TEXT PRIMARY KEY, customer TEXT, product TEXT,
    amount INTEGER, status TEXT, created_at TEXT);"""

ROWS = [
    ("1001", "C-1042", "tai nghe", 850000, "đang giao", "2026-10-28"),
    ("1002", "C-1042", "bàn phím", 1200000, "đã giao", "2026-10-20"),
    ("1003", "C-2087", "chuột", 300000, "đã giao", "2026-09-30"),
    ("1004", "C-2087", "màn hình", 3200000, "đã huỷ", "2026-10-25"),
    ("1005", "C-3011", "tai nghe", 650000, "đã giao", "2026-10-22"),
    ("1006", "C-3011", "bàn phím", 990000, "đang giao", "2026-10-31"),
]


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", ROWS)
    conn.commit()
    return conn


_CONN = None


def get_conn():
    """Một kết nối dùng chung cho cả phiên, để run_select(sql) gọi được ngay."""
    global _CONN
    if _CONN is None:
        _CONN = make_db()
    return _CONN


def _format(rows, columns):
    if not rows:
        return "(không có dòng nào)"
    widths = [len(c) for c in columns]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))
    line = " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    out = [line, "-+-".join("-" * w for w in widths)]
    for row in rows:
        out.append(" | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)))
    return "\n".join(out)


def run_select(sql, conn=None, max_rows=MAX_ROWS):
    """Chạy một câu SELECT. Mọi lỗi trả về chuỗi bắt đầu bằng 'LỖI:'."""
    conn = conn or get_conn()
    text = sql.strip()
    if not text:
        return "LỖI: câu lệnh rỗng."

    # 1. Chặn multi-statement. Không chấp nhận cả dấu ';' ở cuối, để luật
    #    chỉ có một hình dạng và dễ kiểm tra.
    if ";" in text:
        return "LỖI: không cho phép ';' — tool này chỉ chạy một câu."

    # 2. Chặn từ khoá ghi/xoá trước khi xét loại câu, để thông báo rõ ràng.
    lowered = text.lower()
    for word in FORBIDDEN:
        if re.search(rf"\b{word}\b", lowered):
            return f"LỖI: từ khoá bị chặn: {word.upper()}."

    # 3. Chỉ SELECT hoặc WITH (WITH ... SELECT cũng là đọc).
    if not re.match(r"^(select|with)\b", lowered):
        return "LỖI: chỉ cho phép SELECT hoặc WITH."

    # 4. Luôn có LIMIT. Bọc truy vấn để áp trần cho cả WITH và ORDER BY.
    if not re.search(r"\blimit\b", lowered):
        text = f"SELECT * FROM ({text}) LIMIT {max_rows}"
        added = f"  [đã thêm LIMIT {max_rows}]"
    else:
        added = ""

    # 5. Giới hạn thời gian: SQLite không có statement_timeout, nên đếm
    #    opcode và ngắt khi quá hạn. Production dùng statement_timeout thật.
    deadline = time.monotonic() + TIME_BUDGET
    conn.set_progress_handler(
        lambda: 1 if time.monotonic() > deadline else 0, 1000
    )
    try:
        cursor = conn.execute(text)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
    except sqlite3.OperationalError as exc:
        if "interrupt" in str(exc):
            return f"LỖI: câu chạy quá {TIME_BUDGET:g}s, đã bị ngắt."
        return f"LỖI: {exc}"
    except sqlite3.Error as exc:
        return f"LỖI: {exc}"
    finally:
        conn.set_progress_handler(None, 1000)

    return _format(rows, columns) + added


def main():
    conn = get_conn()

    demos = [
        ("Hợp lệ, thiếu LIMIT", "SELECT id, product, amount FROM orders "
         "WHERE status = 'đã giao' ORDER BY amount DESC"),
        ("Có dấu ';' — thử chèn câu thứ hai",
         "SELECT id FROM orders; DROP TABLE orders"),
        ("Xoá dữ liệu", "DELETE FROM orders"),
        ("Xoá cả bảng", "DROP TABLE orders"),
    ]

    for title, sql in demos:
        print(f"\n--- {title} ---")
        print("SQL:", sql)
        print(run_select(sql))

    still_there = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"\n[verify]  bảng orders còn {still_there} dòng — lệnh xoá đã bị chặn.")
    print("Bài học: đừng tin lời nhắc trong prompt. Hãy chặn bằng code,")
    print("và cấp cho tool một user database chỉ có quyền SELECT.")


if __name__ == "__main__":
    main()
