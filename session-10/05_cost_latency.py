"""Bài 05 — Chi phí và độ trễ: con số trước khi hứa với ai.

Chạy:  python 05_cost_latency.py

Bài này chạy 40 request trên pipeline thật (offline) và tính:
    - p50 / p95 / p99 latency
    - token và USD mỗi request
    - chiếu chi phí theo lưu lượng

Lưu ý: đây là pipeline luật, không gọi model thật. Số tuyệt đối không
chuyển sang production được; nhưng cách đo thì chuyển được.
"""

from common.pipeline import answer

QUESTIONS = [
    ("Đổi trả trong bao nhiêu ngày?", "shop-a", None),
    ("Giao hàng nội thành mất bao lâu?", "shop-a", None),
    ("Tai nghe bảo hành mấy tháng?", "shop-a", None),
    ("Shop A có bán laptop không?", "shop-a", None),
    ("Chính sách đổi trả của Shop B là gì?", "shop-b", None),
    ("Đơn trên 500 nghìn có được miễn phí vận chuyển không?", "shop-a", None),
]


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(len(ordered) * ratio))
    return ordered[index]


if __name__ == "__main__":
    latencies: list[float] = []
    costs: list[float] = []
    tokens: list[int] = []
    statuses: dict[str, int] = {}

    for index in range(40):
        question, tenant, fail = QUESTIONS[index % len(QUESTIONS)]
        # Bốn request chậm ở cuối để thấy p95 bị kéo lên (top 10%).
        if index >= 36:
            fail = "slow_model"

        result = answer(question, tenant, fail=fail)
        latencies.append(result["latency_ms"])
        costs.append(result["cost_usd"])
        tokens.append(result["tokens"])
        statuses[result["status"]] = statuses.get(result["status"], 0) + 1

    total_cost = sum(costs)
    per_request = total_cost / len(costs)
    per_1k = per_request * 1_000
    per_month = per_request * 10_000 * 30

    print(f"=== {len(costs)} request ===")
    print("trạng thái:", statuses)
    print(f"token trung bình : {sum(tokens) / len(tokens):.0f}")
    print(f"chi phí/request  : ${per_request:.8f}")
    print(f"chi phí/1.000    : ${per_1k:.6f}")
    print(f"10k/ngày, 30 ngày: ${per_month:.2f}")

    print("\n=== Độ trễ (ms) ===")
    print(f"  p50 : {percentile(latencies, 0.50):8.1f}")
    print(f"  p95 : {percentile(latencies, 0.95):8.1f}")
    print(f"  p99 : {percentile(latencies, 0.99):8.1f}")
    print(f"  max : {max(latencies):8.1f}")

    without_slow = latencies[:36]
    print("\nNếu bỏ 4 request chậm cuối:")
    print(f"  p95 : {percentile(without_slow, 0.95):8.1f}")
    print("4 request chậm trong 40 làm p95 tăng hàng trăm lần — đó là lý do")
    print("phải nhìn p95, không chỉ trung bình.")

    print("\n=== Nếu dùng multi-agent (ước lượng) ===")
    print("Giả định mỗi request thêm 1 lần gọi điều phối và 1 lần tổng hợp: ~2.4× token.")
    multi_cost = per_request * 2.4
    print(f"  chi phí/request  : ${multi_cost:.8f}")
    print(f"  10k/ngày, 30 ngày: ${multi_cost * 10_000 * 30:.2f}")
    print("\nĐây là lý do phải đo trước khi chọn kiến trúc, không sau khi deploy.")
