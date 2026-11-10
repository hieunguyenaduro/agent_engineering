"""Lưu phiên trong RAM — đủ để học, không đủ cho production.

Production: Redis/Postgres, có TTL, có mã hoá, có backup.
Điều quan trọng nhất ở đây là **mọi truy cập đều đi qua user_id**.
"""

from datetime import datetime, timezone

# API key -> thông tin người dùng. Không bao giờ hardcode key thật.
USERS = {
    "key-an": {"user_id": "u-an", "name": "An"},
    "key-binh": {"user_id": "u-binh", "name": "Bình"},
}

# (user_id, session_id) -> danh sách lượt
SESSIONS: dict[tuple[str, str], list[dict]] = {}


def authenticate(api_key: str | None) -> dict | None:
    if not api_key:
        return None
    return USERS.get(api_key)


def history(user_id: str, session_id: str) -> list[dict]:
    return SESSIONS.setdefault((user_id, session_id), [])


def append(user_id: str, session_id: str, role: str, content: str) -> None:
    history(user_id, session_id).append(
        {
            "role": role,
            "content": content,
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )


def load(user_id: str, session_id: str) -> list[dict] | None:
    """Chỉ trả phiên nếu đúng chủ. Không có khái niệm 'đọc hộ'."""
    return SESSIONS.get((user_id, session_id))


def reset() -> None:
    SESSIONS.clear()
