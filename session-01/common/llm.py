"""Một chỗ duy nhất để gọi model.

Cả 6 ví dụ trong buổi đều đi qua hàm chat() này, nên bạn chỉ cần đọc file này một lần.

Cài đặt:
    pip install -r requirements.txt
    cp .env.example .env      # rồi dán OPENAI_API_KEY của bạn vào .env

Chạy thử:
    python 01_hello_llm.py

Nếu chưa có API key (hoặc đang mất mạng), chạy với FAKE=1 để xem luồng chạy
bằng một model giả lập. Model giả lập chỉ để hiểu cơ chế, không phản ánh
chất lượng thật của model.
"""

import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REASONING_MODEL = os.getenv("OPENAI_REASONING_MODEL", "gpt-5-mini")
USE_FAKE = os.getenv("FAKE") == "1"

_client = None


def chat(messages, tools=None, model=None, **kwargs):
    """Gửi messages tới model và trả về response nguyên bản của OpenAI SDK.

    messages: list các dict {"role": ..., "content": ...}
    tools:    list mô tả công cụ (định dạng JSON schema của OpenAI)
    """
    if USE_FAKE:
        return _fake_chat(messages, tools)

    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI()  # tự đọc OPENAI_API_KEY từ môi trường

    return _client.chat.completions.create(
        model=model or MODEL,
        messages=messages,
        tools=tools or None,
        **kwargs,
    )


def text(response) -> str:
    """Lấy phần chữ model trả lời."""
    return response.choices[0].message.content or ""


def tool_calls(response):
    """Lấy danh sách công cụ mà model XIN ĐƯỢC GỌI (chưa ai chạy cả)."""
    return response.choices[0].message.tool_calls or []


def usage_line(response) -> str:
    """In ra số token đã dùng, để thấy mỗi lần gọi là một lần tốn tiền."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return "(không có thông tin token)"
    return f"{usage.prompt_tokens} token vào / {usage.completion_tokens} token ra"


# ---------------------------------------------------------------------------
# Phần dưới đây chỉ phục vụ chế độ FAKE=1 (không có API key vẫn chạy được demo).
# Bạn không cần đọc phần này để hiểu bài.
# ---------------------------------------------------------------------------

import json  # noqa: E402
from types import SimpleNamespace  # noqa: E402


def _fake_chat(messages, tools):
    user_text = _last_user_text(messages)
    da_goi = _called_tools(messages)
    prompt_tokens = _estimate_prompt(messages)

    if tools:
        call = _fake_pick_tool(tools, user_text, da_goi)
        if call is not None:
            return _fake_response(tool_calls=[call], prompt_tokens=prompt_tokens)

    if _role(messages[-1]) == "tool":
        data = "\n".join(c for c in (_content(m) for m in messages if _role(m) == "tool"))
        return _fake_response(
            content=f"(giả lập) Dựa trên dữ liệu vừa tra:\n{data}",
            prompt_tokens=prompt_tokens,
        )

    return _fake_response(
        content=f"(giả lập) Mình chưa gọi công cụ nào. Câu hỏi nhận được: {user_text}",
        prompt_tokens=prompt_tokens,
    )


def _estimate_prompt(messages) -> int:
    chars = sum(len(str(_content(m) or "")) for m in messages)
    return max(1, chars // 4)


def _fake_pick_tool(tools, user_text, da_goi):
    for tool in tools:
        name = tool["function"]["name"]
        if name in da_goi or not _relevant(name, user_text):
            continue
        args = _fake_args(tool, user_text)
        return SimpleNamespace(
            id=f"call_fake_{name}",
            type="function",
            function=SimpleNamespace(name=name, arguments=json.dumps(args, ensure_ascii=False)),
        )
    return None


def _relevant(name: str, user_text: str) -> bool:
    """Đoán xem tool nào có liên quan tới câu hỏi (chỉ dùng cho chế độ giả lập)."""
    lowered = user_text.lower()
    if "weather" in name:
        return any(w in lowered for w in ("thời tiết", "weather", "nắng", "mưa"))
    if "order" in name:
        return any(ch.isdigit() for ch in user_text) or "đơn" in lowered
    if "policy" in name:
        return any(w in lowered for w in ("đổi trả", "policy", "bảo hành", "hoàn"))
    if "refund" in name:
        return any(w in lowered for w in ("hoàn", "refund", "tiền"))
    return False


def _role(message):
    return message.get("role") if isinstance(message, dict) else getattr(message, "role", None)


def _content(message):
    return message.get("content") if isinstance(message, dict) else getattr(message, "content", "")


def _called_tools(messages):
    names = []
    for message in messages:
        calls = (
            message.get("tool_calls")
            if isinstance(message, dict)
            else getattr(message, "tool_calls", None)
        )
        for call in calls or []:
            names.append(call.function.name)
    return names


def _fake_args(tool, user_text):
    props = tool["function"].get("parameters", {}).get("properties", {})
    digits = "".join(ch for ch in user_text if ch.isdigit())
    lowered = user_text.lower()
    args = {}
    for key in props:
        if "order" in key:
            args[key] = digits[:4] or "1234"
        elif key in ("city", "location"):
            args[key] = "Hà Nội"
        elif key == "expression":
            args[key] = "2 + 3 * 4"
        elif key in ("amount", "price"):
            args[key] = 250000
        elif "product" in key:
            args[key] = next(
                (p for p in ("tai nghe", "bàn phím") if p in lowered),
                "tai nghe",
            )
        elif "topic" in key or "question" in key:
            args[key] = user_text
        else:
            args[key] = "demo"
    return args


def _last_user_text(messages):
    for message in reversed(messages):
        if _role(message) == "user":
            return _content(message) or ""
    return ""


def _fake_response(content=None, tool_calls=None, prompt_tokens=0):
    completion_tokens = 20 + (len(content) // 4 if content else 0)
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens
        ),
    )
