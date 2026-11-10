"""Model giả cho buổi 5: luôn gọi search_knowledge trước khi trả lời."""

from typing import Any, List, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class FakeRagModel(BaseChatModel):
    tool_names: List[str] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "fake-rag-model"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "FakeRagModel":
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
            content = last.content if isinstance(last.content, str) else str(last.content)
            # Tool báo không đủ dữ liệu: model phải nói thẳng, không được bịa.
            if content.startswith("KHONG_DU_DU_LIEU"):
                return ChatResult(
                    generations=[
                        ChatGeneration(
                            message=AIMessage(
                                content=(
                                    "Mình không tìm thấy tài liệu nào trong kho phù hợp "
                                    "với câu hỏi này, nên không thể trả lời chắc chắn. "
                                    "Bạn liên hệ bộ phận chăm sóc khách hàng để được hỗ trợ."
                                )
                            )
                        )
                    ]
                )
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=AIMessage(content=f"Dựa trên tài liệu tìm được:\n{content}")
                    )
                ]
            )

        if "search_knowledge" in self.tool_names:
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=AIMessage(
                            content="",
                            tool_calls=[
                                {
                                    "name": "search_knowledge",
                                    "args": {"query": text},
                                    "id": "call_search_1",
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
