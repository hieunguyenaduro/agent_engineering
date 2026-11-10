"""06 — Cô lập người dùng: mỗi người một workspace, một memory, một namespace.

Chạy: python 06_isolation.py
Không cần API key. Toàn bộ dữ liệu demo nằm trong data/ và được tạo lại mỗi lần chạy.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).with_name("data")
WORKSPACES = BASE / "workspaces"
MEMORY = BASE / "memory"
AUDIT = BASE / "audit.log"

RULES = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
    (re.compile(r"\b\d{12}\b"), "[CCCD]"),
    (re.compile(r"\b0\d{3}[ .]?\d{3}[ .]?\d{3}\b"), "[SĐT]"),
]
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def redact(text: str) -> str:
    """Che PII khi hiển thị. Đây là giảm thiểu rò rỉ, không phải hàng rào truy cập."""
    for pattern, replacement in RULES:
        text = pattern.sub(replacement, text)
    return text


def check_id(user_id: str) -> str:
    # user_id đi vào tên thư mục, nên phải chặn '../' và mọi ký tự lạ.
    if not SAFE_ID.fullmatch(user_id):
        raise ValueError(f"user_id không hợp lệ: {user_id!r}")
    return user_id


def audit(user_id: str, action: str, result: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {user_id} {action} {result}\n"
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(line)


class Workspace:
    def __init__(self, user_id: str):
        self.user_id = check_id(user_id)
        self.root = (WORKSPACES / user_id).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, relative: str, content: str) -> Path:
        target = self._resolve(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def read(self, relative: str) -> str:
        target = self._resolve(relative)
        try:
            return redact(target.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise FileNotFoundError(f"không có file {relative}") from None

    def _resolve(self, relative: str) -> Path:
        # resolve() xử lý cả '..' và symlink; sau đó mới kiểm tra ranh giới.
        target = (self.root / relative).resolve()
        if not target.is_relative_to(self.root):
            audit(self.user_id, f"read:{relative}", "BLOCKED ngoài workspace")
            raise PermissionError(f"bị chặn: {relative} nằm ngoài workspace của {self.user_id}")
        return target


class UserMemory:
    def __init__(self, user_id: str):
        self.user_id = check_id(user_id)
        self.path = MEMORY / f"{self.user_id}.json"

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def put(self, key: str, value: str) -> None:
        data = self._load()
        data[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, key: str):
        return self._load().get(key)


def attempt(label, fn):
    try:
        result = fn()
        print(f"  {label} → OK: {result[:70]}")
    except Exception as exc:
        print(f"  {label} → CHẶN: {exc}")


def main():
    for path in (WORKSPACES, MEMORY):
        if path.exists():
            for child in sorted(path.rglob("*"), reverse=True):
                child.unlink() if child.is_file() else child.rmdir()
            path.rmdir()
    AUDIT.unlink(missing_ok=True)

    a = Workspace("user-A")
    b = Workspace("user-B")
    a.write("notes.md", "Khách Minh, SĐT 0909 123 456, email minh@example.com, CCCD 079123456789.")
    a.write("orders/1234.md", "Đơn 1234: tai nghe SoundMax X2, giao quận 7.")
    b.write("secret.md", "user-B: Lan, SĐT 0912 345 678, email lan@example.com. Giá vốn: 320.000đ.")
    print("[1] Đã tạo hai workspace riêng:", a.root.name, "và", b.root.name)

    print("\n[2] user-A đọc file của chính mình (PII được che):")
    print("   ", a.read("notes.md"))

    print("\n[3] user-A thử đọc dữ liệu của user-B:")
    attempt("đọc ../user-b/secret.md", lambda: a.read("../user-b/secret.md"))
    attempt("đọc đường dẫn tuyệt đối /etc/passwd", lambda: a.read("/etc/passwd"))
    attempt("đọc ../../memory/user-B.json", lambda: a.read("../../memory/user-B.json"))

    mem_a, mem_b = UserMemory("user-A"), UserMemory("user-B")
    mem_a.put("ten", "Minh")
    mem_b.put("ten", "Lan")
    mem_a.put("so_thich", "thích nhạc lo-fi")
    print("\n[4] Memory tách theo user:")
    print("   user-A:", mem_a._load())
    print("   user-B:", mem_b._load())
    attempt("tạo memory với user_id='../user-B'", lambda: UserMemory("../user-B").get("ten"))

    print("\n[5] Audit log (chỉ ghi hành vi bị chặn):")
    print(AUDIT.read_text(encoding="utf-8").rstrip())

    print("\n[done] Redact che PII khi hiển thị. Workspace và user_id chặn truy cập chéo.")
    print("       Hai lớp này độc lập: thiếu lớp nào cũng đủ để lộ dữ liệu.")


if __name__ == "__main__":
    main()
