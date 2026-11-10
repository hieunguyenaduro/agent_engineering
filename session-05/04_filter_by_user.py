"""Bài 04 — Lọc theo người dùng: kiểm tra ở tầng dữ liệu.

Chạy:  python 04_filter_by_user.py

Đây là bài quan trọng nhất buổi về mặt bảo mật.

Sai lầm phổ biến: retrieve tất cả rồi dặn model "đừng tiết lộ dữ liệu của
công ty khác". Model có thể vâng lời, nhưng dữ liệu đã nằm trong context —
một prompt injection là đủ để lộ.

Đúng: lọc ngay trong truy vấn vector, trước khi dữ liệu rời khỏi database.
"""

from common.knowledge import build_index, embed_one, search

client = build_index()
query = "Chính sách đổi trả trong bao nhiêu ngày?"


# ---------------------------------------------------------------------------
# CÁCH SAI: tìm trên toàn bộ kho, rồi mới lọc bằng prompt.
# ---------------------------------------------------------------------------
def bad_search(query: str, limit: int = 4):
    """Không truyền filter — trả về cả dữ liệu của tenant khác."""
    from common.knowledge import COLLECTION

    try:
        result = client.query_points(
            COLLECTION, query=embed_one(query), limit=limit, with_payload=True
        )
        return result.points
    except AttributeError:
        return client.search(COLLECTION, query_vector=embed_one(query), limit=limit)


# ---------------------------------------------------------------------------
# CÁCH ĐÚNG: filter nằm trong truy vấn.
# ---------------------------------------------------------------------------
def good_search(query: str, tenant: str, limit: int = 4):
    return search(client, query, tenant=tenant, limit=limit)


print("=== SAI: không lọc ===")
for hit in bad_search(query):
    print(f"  {hit.payload['tenant']:8} {hit.payload['source']}")

print("\n=== ĐÚNG: lọc theo tenant ===")
for tenant in ("shop-a", "shop-b"):
    print(f"\n[{tenant}]")
    for hit in good_search(query, tenant):
        print(f"  {hit.score:.3f}  {hit.payload['source']}")

print()
print("Với cùng câu hỏi, shop-b chỉ thấy tài liệu của shop-b.")
print("Dữ liệu của shop-a không bao giờ rời khỏi database trong truy vấn của shop-b.")
