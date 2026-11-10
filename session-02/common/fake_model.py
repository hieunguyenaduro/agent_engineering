"""Một chat model giả lập để chạy ví dụ khi không có API key.

Nó không thông minh: chỉ nhìn từ khoá để quyết định gọi tool nào. Nhưng nó nói
đúng giao thức của LangChain, nên graph, checkpoint, streaming, interrupt đều
chạy y như với model thật.

Đây cũng là cách viết test cho agent mà không tốn tiền gọi API.
"""

import json
from typing import Any, List, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field


class FakeToolModel(BaseChatModel):
    tool_names: List[str] = Field(default_factory=list)
    mode: str = "normal"  # "normal" hoặc "loop" (cố tình gọi tool mãi)

    @property
    def _llm_type(self) -> str:
        return "fake-tool-model"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "FakeToolModel":
        names = []
        for tool in tools:
            if isinstance(tool, dict):
                names.append(tool.get("function", {}).get("name") or tool.get("name"))
            else:
                names.append(getattr(tool, "name", str(tool)))
        return self.model_copy(update={"tool_names": names})

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        reply = self._reply(messages)
        return ChatResult(generations=[ChatGeneration(message=reply)])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ):
        """Stream từng từ để bài 04 có thứ để hiển thị."""
        reply = self._reply(messages)
        if reply.tool_calls:
            yield ChatGenerationChunk(
                message=AIMessageChunk(
                    content="",
                    tool_call_chunks=[
                        {
                            "name": call["name"],
                            "args": json.dumps(call["args"]),
                            "id": call["id"],
                            "index": i,
                        }
                        for i, call in enumerate(reply.tool_calls)
                    ],
                )
            )
            return

        for word in reply.content.split(" "):
            yield ChatGenerationChunk(message=AIMessageChunk(content=word + " "))

    # -- logic giả lập ------------------------------------------------------
    def _reply(self, messages: List[BaseMessage]) -> AIMessage:
        last = messages[-1]
        text = last.content if isinstance(last.content, str) else str(last.content)

        if isinstance(last, ToolMessage) and self.mode != "loop":
            return AIMessage(content=f"(giả lập) Dựa trên dữ liệu vừa tra: {last.content}")

        lowered = text.lower()
        digits = "".join(ch for ch in text if ch.isdigit())[:4]

        if "issue_refund" in self.tool_names and any(
            w in lowered for w in ("hoàn tiền", "refund", "trả lại tiền")
        ):
            return self._call("issue_refund", {"order_id": digits or "1234", "amount": 250000})

        if "get_order_status" in self.tool_names and digits:
            return self._call("get_order_status", {"order_id": digits})

        if "check_return_policy" in self.tool_names and any(
            w in lowered for w in ("đổi trả", "bảo hành", "policy")
        ):
            product = "tai nghe" if "tai nghe" in lowered else "bàn phím"
            return self._call("check_return_policy", {"product": product})

        return AIMessage(
            content=f"(giả lập) Mình chưa gọi tool nào. Câu hỏi nhận được: {text}"
        )

    def _call(self, name: str, args: dict) -> AIMessage:
        return AIMessage(
            content="",
            tool_calls=[{"name": name, "args": args, "id": f"call_{name}", "type": "tool_call"}],
        )
