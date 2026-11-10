"""Model giả cho bài 01: gọi subagent (tool research) rồi trả lời.

Nó không thông minh. Nó chỉ nói đúng giao thức tool-calling để graph chạy thật.
Đây cũng là cách viết test cho multi-agent mà không tốn tiền gọi API.
"""

from typing import Any, List, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class FakeResearchModel(BaseChatModel):
    tool_names: List[str] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "fake-research-model"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "FakeResearchModel":
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
        last = messages[-1]
        text = last.content if isinstance(last.content, str) else str(last.content)

        if isinstance(last, ToolMessage):
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=AIMessage(
                            content=(
                                "Tổng hợp từ subagent:\n"
                                f"{last.content}\n\n"
                                "Kết luận: đã đủ dữ liệu để trả lời người dùng."
                            )
                        )
                    )
                ]
            )

        if "research" in self.tool_names:
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=AIMessage(
                            content="",
                            tool_calls=[
                                {
                                    "name": "research",
                                    "args": {"query": text},
                                    "id": "call_research_1",
                                    "type": "tool_call",
                                }
                            ],
                        )
                    )
                ]
            )

        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=f"(giả lập) {text}"))]
        )
