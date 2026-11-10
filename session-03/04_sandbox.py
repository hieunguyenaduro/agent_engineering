"""Bài 04 — Sandbox: chạy code lạ trong subprocess có giới hạn.

Chạy:  python 04_sandbox.py

Bốn lớp trong ví dụ này:
    1. kiểm tra tĩnh  - AST: đường dẫn ngoài thư mục, import bị cấm
    2. subprocess     - chạy bằng python -I -S, cách ly môi trường
    3. giới hạn tài nguyên - CPU, kích thước file, timeout tường
    4. chặn mạng      - prelude thay socket bằng hàm ném lỗi

Đây là giảm thiệt hại, KHÔNG phải sandbox tuyệt đối. Kẻ tấn công giỏi có thể
vượt qua kiểm tra tĩnh; production cần container/seccomp/gVisor ở tầng dưới.
"""

import ast
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT = 2.0
MAX_OUTPUT = 800
BLOCKED_IMPORTS = {"subprocess", "socket", "ctypes", "multiprocessing"}

# Chạy trước code người dùng, bên trong tiến trình con.
PRELUDE = """
import resource
resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
resource.setrlimit(resource.RLIMIT_FSIZE, (1_000_000, 1_000_000))

import socket as _socket
def _blocked(*args, **kwargs):
    raise RuntimeError("Mạng bị chặn trong sandbox")
_socket.socket = _blocked
_socket.create_connection = _blocked
"""


def _looks_like_path(value: str) -> bool:
    return value.startswith(("/", "~")) or "/" in value or "\\" in value


def check_code(code: str, sandbox: Path) -> str | None:
    """Trả về thông báo lỗi, hoặc None nếu qua được kiểm tra tĩnh."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"LỖI: code sai cú pháp: {exc.msg}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "").split(".")[0]]
        else:
            names = []
        for name in names:
            if name in BLOCKED_IMPORTS:
                return f"LỖI: import bị chặn trong sandbox: {name}"

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if not _looks_like_path(value):
                continue
            target = Path(value).expanduser()
            if not target.is_absolute():
                target = sandbox / target
            if not target.resolve().is_relative_to(sandbox.resolve()):
                return f"LỖI: đường dẫn ngoài sandbox bị chặn: {value}"
    return None


def run_code(code: str, timeout: float = TIMEOUT) -> str:
    """Chạy code trong thư mục tạm. Luôn trả về chuỗi, không raise."""
    with tempfile.TemporaryDirectory(prefix="sandbox_") as tmp:
        sandbox = Path(tmp)
        error = check_code(code, sandbox)
        if error:
            return error + "\n     (chặn trước khi chạy — không tốn tiến trình)"

        (sandbox / "main.py").write_text(PRELUDE + "\n" + code, encoding="utf-8")
        env = {
            "PATH": "/usr/bin:/bin",
            "HOME": str(sandbox),
            "TMPDIR": str(sandbox),
            "PYTHONIOENCODING": "utf-8",
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", "main.py"],
                cwd=sandbox, env=env, capture_output=True, text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"LỖI: chạy quá {timeout:g}s — tiến trình đã bị kill."

        if proc.returncode != 0:
            tail = (proc.stderr or "").strip().splitlines()[-1:]
            return f"LỖI: tiến trình thoát mã {proc.returncode}: {' '.join(tail)}"
        return (proc.stdout or "").strip()[:MAX_OUTPUT] or "(không in gì)"


def main():
    demos = [
        ("Code bình thường",
         "print(sum(i * i for i in range(10)))"),
        ("Vòng lặp vô hạn",
         "while True:\n    pass"),
        ("Đọc file ngoài thư mục",
         "print(open('/etc/hosts').read()[:80])"),
        ("Thử mở mạng (lách kiểm tra tĩnh bằng __import__)",
         "__import__('socket').create_connection(('example.com', 80), timeout=1)"),
    ]

    for title, code in demos:
        print(f"\n--- {title} ---")
        print("code:", code.replace("\n", " / "))
        print("kết quả:", run_code(code))

    print("\nBài học:")
    print("  - Kiểm tra tĩnh chỉ bắt được cái ngây thơ; nó không phải hàng rào.")
    print("  - Timeout + thư mục tạm + không mạng là mức tối thiểu nên có.")
    print("  - Cần cách ly thật thì dùng container, seccomp, hoặc dịch vụ sandbox.")


if __name__ == "__main__":
    main()
