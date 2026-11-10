"""05 — Memory dài hạn: facts bền vững trong sqlite, có nguồn và hạn dùng.

Chạy: python 05_long_memory.py
Không cần server, không cần API key. File data/memory.db được tạo lại mỗi lần chạy
để kết quả lặp lại được; trong sản phẩm thật bạn không xoá file này.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common.tokens import print_table, shorten

DB_PATH = Path(__file__).with_name("data") / "memory.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS facts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL,
    key        TEXT NOT NULL,
    value      TEXT NOT NULL,
    source     TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    confidence REAL NOT NULL DEFAULT 1.0,
    UNIQUE (user_id, key)
)
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds")


def remember(conn, user_id, key, value, source, ttl_days=None, now=None):
    """Ghi hoặc cập nhật một fact. Không có nguồn thì không có fact."""
    if not source:
        raise ValueError("fact phải có nguồn")
    now = now or datetime.now(timezone.utc)
    expires = iso(now + timedelta(days=ttl_days)) if ttl_days else None
    conn.execute(
        """
        INSERT INTO facts (user_id, key, value, source, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (user_id, key) DO UPDATE SET
            value = excluded.value, source = excluded.source,
            created_at = excluded.created_at, expires_at = excluded.expires_at
        """,
        (user_id, key, str(value), source, iso(now), expires),
    )
    conn.commit()


def recall(conn, user_id, now=None) -> list:
    """Chỉ trả về facts còn hạn. Fact hết hạn vẫn nằm trong DB để audit."""
    now = iso(now or datetime.now(timezone.utc))
    rows = conn.execute(
        "SELECT * FROM facts WHERE user_id = ? AND (expires_at IS NULL OR expires_at > ?) "
        "ORDER BY key",
        (user_id, now),
    ).fetchall()
    return rows


def forget_expired(conn, now=None) -> int:
    now = iso(now or datetime.now(timezone.utc))
    cursor = conn.execute("DELETE FROM facts WHERE expires_at IS NOT NULL AND expires_at <= ?", (now,))
    conn.commit()
    return cursor.rowcount


def show(conn, user_id, title):
    rows = conn.execute("SELECT * FROM facts WHERE user_id = ? ORDER BY key", (user_id,)).fetchall()
    now = iso(datetime.now(timezone.utc))
    print(f"\n{title}")
    if not rows:
        print("  (trống)")
        return
    print_table(
        ["key", "value", "nguồn", "tạo", "hết hạn", "trạng thái"],
        [[r["key"], shorten(r["value"], 22), r["source"], r["created_at"][:10],
          (r["expires_at"] or "—")[:10], "hết hạn" if r["expires_at"] and r["expires_at"] <= now else "còn"]
         for r in rows],
        widths=[12, 24, 14, 11, 11, 9],
    )


def main():
    DB_PATH.unlink(missing_ok=True)
    conn = connect()
    now = datetime.now(timezone.utc)

    print("[1] Ghi facts cho user-A")
    remember(conn, "user-A", "ten", "Minh", "chat#12", ttl_days=365)
    remember(conn, "user-A", "don_hang", "1234", "order_api#9")
    remember(conn, "user-A", "dien_thoai", "0909 123 456", "chat#12", ttl_days=30)
    remember(conn, "user-A", "ngon_ngu", "tiếng Việt", "chat#12")
    # Fact cũ 40 ngày, hạn 30 ngày: phải biến mất khỏi recall nhưng còn trong DB.
    remember(conn, "user-A", "goi_cu", "dùng thử Pro", "chat#3", ttl_days=30,
             now=now - timedelta(days=40))
    show(conn, "user-A", "Toàn bộ DB của user-A (kể cả fact hết hạn)")

    fresh = recall(conn, "user-A")
    print(f"\n[2] recall(user-A) → {len(fresh)} facts còn hạn: "
          f"{[r['key'] for r in fresh]}")
    print("    Fact 'goi_cu' không được trả về vì đã hết hạn.")

    removed = forget_expired(conn)
    print(f"[3] forget_expired() → xoá {removed} fact hết hạn.")
    show(conn, "user-A", "DB sau khi dọn")

    # Đóng rồi mở lại: mô phỏng process restart, memory vẫn còn.
    conn.close()
    conn = connect()
    print(f"\n[4] Mở lại DB (giả lập restart) → user-A còn {len(recall(conn, 'user-A'))} facts.")
    print("    Đây là khác biệt giữa memory dài hạn và biến trong RAM.")

    remember(conn, "user-B", "ten", "Lan", "chat#1", ttl_days=365)
    print(f"\n[5] user-B có {len(recall(conn, 'user-B'))} fact; "
          f"user-A có {len(recall(conn, 'user-A'))} fact.")
    print("    Không truy vấn nào trả về dữ liệu của người kia — vì WHERE user_id.")

    print("\n[6] Fact có hạn và có nguồn trả lời được hai câu hỏi:")
    print("    'Bạn biết điều này từ đâu?' → source.")
    print("    'Bao lâu thì phải kiểm tra lại?' → expires_at.")
    print("\n[done] Memory không phải một dict không đáy. Nó là bảng có cột.")


if __name__ == "__main__":
    main()
