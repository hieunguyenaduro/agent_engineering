"""Bài 05 — Cô lập tenant: kiểm tra quyền ở tầng dữ liệu.

Chạy: python 05_tenant_isolation.py

Kịch bản: agent phục vụ hai công ty. Công ty A không được đọc dữ liệu của B.
Cách duy nhất đúng: mọi hàm truy cập dữ liệu nhận tenant_id đã xác thực và tự
lọc. Câu "chỉ trả lời dữ liệu của công ty A" trong prompt không phải quyền.
"""

from common.tenant_store import (
    AccessDenied,
    Document,
    TenantStore,
    tenant_from_session,
)

DOCS = [
    Document("acme-1", "acme", "Bảng giá nội bộ", "Giá sỉ sản phẩm X: 100.000đ"),
    Document("acme-2", "acme", "Quy trình hoàn tiền", "Hoàn trong 7 ngày làm việc"),
    Document("beta-1", "beta", "Hợp đồng khung", "Giá sỉ sản phẩm X: 200.000đ"),
    Document("beta-2", "beta", "Danh sách khách", "Khách B-01, B-02 đang chờ"),
]


def show_search(store: TenantStore) -> None:
    print("### 1. Tìm kiếm có tenant (đúng)")
    for doc in store.search("acme", "giá"):
        print(f"  [allow] {doc.id:8} tenant={doc.tenant_id:5} {doc.title}")

    print("\n### 2. Nếu quên lọc tenant (lỗi rất hay gặp)")
    for doc in store.unsafe_search("giá"):
        print(f"  [leak ] {doc.id:8} tenant={doc.tenant_id:5} {doc.title}")


def show_idor(store: TenantStore) -> None:
    print("\n### 3. IDOR: đổi doc_id trong request")
    for tenant, doc_id in (("acme", "acme-1"), ("acme", "beta-1")):
        try:
            doc = store.get_document(tenant, doc_id)
            print(f"  [allow] {tenant} đọc {doc.id}: {doc.body}")
        except AccessDenied as exc:
            print(f"  [block] {tenant} đọc {doc_id}: {exc}")


def show_memory(store: TenantStore) -> None:
    print("\n### 4. Memory cũng phải có tenant")
    store.remember("beta", "u-beta", "giá_sàn", "180.000đ")
    print("  beta đọc của beta:", store.recall("beta", "u-beta", "giá_sàn"))
    print("  acme đọc của beta:", store.recall("acme", "u-beta", "giá_sàn"))
    print("  acme đọc của acme:", store.recall("acme", "u-acme", "giá_sàn"))


def show_payload() -> None:
    print("\n### 5. Tenant đến từ phiên, không từ body")
    for payload in ({"tenant_id": "acme"}, {"tenant_id": "beta"}, {}):
        try:
            tenant = tenant_from_session("acme", payload)
            print(f"  [allow] payload={payload} -> tenant={tenant}")
        except AccessDenied as exc:
            print(f"  [block] payload={payload} -> {exc}")


if __name__ == "__main__":
    store = TenantStore(DOCS)
    show_search(store)
    show_idor(store)
    show_memory(store)
    show_payload()

    print("\nBài học: kiểm tra quyền ở nơi dữ liệu được đọc, không ở nơi model")
    print("được dặn. Prompt có thể bị lách; hàm truy vấn thì không.")
