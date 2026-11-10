"""Dữ liệu nhiều công ty (tenant) với kiểm tra quyền ở tầng dữ liệu.

Bài học: câu "chỉ trả lời dữ liệu của công ty A" trong prompt không phải là
kiểm soát truy cập. Ai đó có thể đổi `doc_id` hoặc `tenant_id` trong request.
Vì vậy mọi hàm đọc/ghi ở đây **bắt buộc** nhận tenant_id đã xác thực và tự lọc.

`unsafe_search` cố tình viết sai để demo lỗi rò rỉ — không dùng trong production.
"""

from dataclasses import dataclass


class AccessDenied(Exception):
    """Không có quyền với tài nguyên, hoặc tài nguyên không tồn tại."""


@dataclass(frozen=True)
class Document:
    id: str
    tenant_id: str
    title: str
    body: str


class TenantStore:
    def __init__(self, documents=()):
        self._docs = {doc.id: doc for doc in documents}
        self._memory: dict[tuple[str, str, str], str] = {}

    def search(self, tenant_id: str, query: str) -> list[Document]:
        if not tenant_id:
            raise AccessDenied("thiếu tenant_id đã xác thực")
        needle = (query or "").lower()
        return [
            doc for doc in self._docs.values()
            if doc.tenant_id == tenant_id
            and (needle in doc.title.lower() or needle in doc.body.lower())
        ]

    def get_document(self, tenant_id: str, doc_id: str) -> Document:
        if not tenant_id:
            raise AccessDenied("thiếu tenant_id đã xác thực")
        doc = self._docs.get(doc_id)
        # Không phân biệt "không tồn tại" với "không có quyền": tránh dò id.
        if doc is None or doc.tenant_id != tenant_id:
            raise AccessDenied(f"không có quyền đọc tài liệu {doc_id}")
        return doc

    def remember(self, tenant_id: str, user_id: str, key: str, value: str) -> None:
        if not tenant_id or not user_id:
            raise AccessDenied("memory cần cả tenant_id và user_id")
        self._memory[(tenant_id, user_id, key)] = value

    def recall(self, tenant_id: str, user_id: str, key: str) -> str | None:
        if not tenant_id or not user_id:
            raise AccessDenied("memory cần cả tenant_id và user_id")
        return self._memory.get((tenant_id, user_id, key))

    def unsafe_search(self, query: str) -> list[Document]:
        """Cố tình quên lọc tenant — chỉ dùng để chứng minh lỗi."""
        needle = (query or "").lower()
        return [
            doc for doc in self._docs.values()
            if needle in doc.title.lower() or needle in doc.body.lower()
        ]


def tenant_from_session(authenticated_tenant: str, payload: dict) -> str:
    """Tenant lấy từ phiên đăng nhập, không lấy từ body request.

    Nếu body cố gắng chỉ định tenant khác, từ chối và để tầng audit ghi lại.
    Im lặng bỏ qua cũng được, nhưng từ chối giúp phát hiện tấn công sớm hơn.
    """
    requested = (payload or {}).get("tenant_id")
    if requested and requested != authenticated_tenant:
        raise AccessDenied(
            f"tenant trong payload ({requested}) không khớp phiên đăng nhập"
        )
    return authenticated_tenant
