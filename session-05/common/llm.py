"""Model cho buổi 5: có key thì dùng OpenAI, không có thì dùng model giả."""

import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USE_FAKE = os.getenv("FAKE") == "1"


def get_model(tools=None):
    if USE_FAKE:
        from common.fake_model import FakeRagModel

        model = FakeRagModel()
    else:
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(model=MODEL, temperature=0)

    return model.bind_tools(tools) if tools else model
