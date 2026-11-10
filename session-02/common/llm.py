"""Model cho cả buổi 2: có key thì dùng OpenAI, không có thì dùng model giả.

Model giả không thông minh. Nó chỉ để bạn chạy được toàn bộ ví dụ khi không có
mạng hoặc không muốn tốn tiền — và để viết test mà không gọi API.
"""

import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USE_FAKE = os.getenv("FAKE") == "1"


def get_model(tools=None):
    """Trả về một chat model đã gắn tool (nếu có)."""
    if USE_FAKE:
        from common.fake_model import FakeToolModel

        model = FakeToolModel()
    else:
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(model=MODEL, temperature=0)

    return model.bind_tools(tools) if tools else model
