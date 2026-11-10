"""Bài 04 — Eval report: chất lượng, độ trễ, chi phí trong một báo cáo.

Chạy:  python 04_eval_report.py

Báo cáo được ghi ra `reports/eval-report.md`. Đây là thứ bạn đính kèm khi
review một thay đổi — không phải ảnh chụp màn hình chat.

Bộ case nhỏ (6) để chạy nhanh. Bộ thật nên có 30–100 case, lấy từ câu hỏi
người dùng và failure case đã gặp.
"""

from datetime import datetime, timezone
from pathlib import Path

from common.pipeline import answer

CASES = [
    {
        "question": "Đổi trả trong bao nhiêu ngày?",
        "tenant": "shop-a",
        "expect_status": "ok",
        "expect_source": "chinh-sach-doi-tra.md",
        "must_contain": "7 ngày",
    },
    {
        "question": "Giao hàng nội thành mất bao lâu?",
        "tenant": "shop-a",
        "expect_status": "ok",
        "expect_source": "chinh-sach-van-chuyen.md",
        "must_contain": "24 giờ",
    },
    {
        "question": "Tai nghe bảo hành mấy tháng?",
        "tenant": "shop-a",
        "expect_status": "ok",
        "expect_source": "chinh-sach-bao-hanh.md",
        "must_contain": "6 tháng",
    },
    {
        "question": "Đơn trên 500 nghìn có được miễn phí vận chuyển không?",
        "tenant": "shop-a",
        "expect_status": "ok",
        "expect_source": "chinh-sach-van-chuyen.md",
        "must_contain": "miễn phí",
    },
    {
        "question": "Chính sách đổi trả của Shop B là gì?",
        "tenant": "shop-b",
        "expect_status": "ok",
        "expect_source": "shop-b-doi-tra.md",
        "must_contain": "3 ngày",
    },
    {
        "question": "Shop A có bán laptop không?",
        "tenant": "shop-a",
        "expect_status": "refused",
        "expect_source": None,
        "must_contain": "không tìm thấy",
    },
]


def evaluate(case: dict) -> dict:
    result = answer(case["question"], case["tenant"])
    sources = [source["source"] for source in result["sources"]]

    status_ok = result["status"] == case["expect_status"]
    source_ok = case["expect_source"] is None or case["expect_source"] in sources
    contains_ok = case["must_contain"].lower() in result["answer"].lower()

    return {
        **case,
        "result": result,
        "sources": sources,
        "status_ok": status_ok,
        "source_ok": source_ok,
        "contains_ok": contains_ok,
        "passed": status_ok and source_ok and contains_ok,
    }


def pct(part: int, total: int) -> str:
    return f"{part / total:.0%}" if total else "n/a"


if __name__ == "__main__":
    rows = [evaluate(case) for case in CASES]
    passed = sum(1 for row in rows if row["passed"])
    ok_rows = [row for row in rows if row["expect_status"] == "ok"]
    cited = sum(1 for row in ok_rows if row["sources"])
    refused_expected = [row for row in rows if row["expect_status"] == "refused"]
    refused_right = sum(1 for row in refused_expected if row["status_ok"])

    latencies = sorted(row["result"]["latency_ms"] for row in rows)
    total_cost = sum(row["result"]["cost_usd"] for row in rows)
    total_tokens = sum(row["result"]["tokens"] for row in rows)
    p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))]

    lines = [
        "# Eval report — Shop Agent",
        "",
        f"Sinh lúc: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Tóm tắt",
        "",
        f"- Case đạt: **{passed}/{len(rows)}** ({pct(passed, len(rows))})",
        f"- Câu trả lời có nguồn: **{cited}/{len(ok_rows)}**",
        f"- Từ chối đúng khi thiếu dữ liệu: **{refused_right}/{len(refused_expected)}**",
        f"- Độ trễ p95: **{p95:.1f} ms**",
        f"- Tổng token: **{total_tokens}**, tổng chi phí: **${total_cost:.8f}**",
        "",
        "## Chi tiết",
        "",
        "| # | Câu hỏi | Trạng thái | Nguồn | Đạt |",
        "|---|---|---|---|---|",
    ]

    for index, row in enumerate(rows, 1):
        sources = ", ".join(row["sources"]) or "—"
        mark = "✅" if row["passed"] else "❌"
        lines.append(
            f"| {index} | {row['question']} | {row['result']['status']} | {sources} | {mark} |"
        )

    failed = [row for row in rows if not row["passed"]]
    lines += ["", "## Case trượt", ""]
    if not failed:
        lines.append("Không có.")
    else:
        for row in failed:
            lines.append(
                f"- {row['question']}: status={row['result']['status']} "
                f"(mong {row['expect_status']}), nguồn={row['sources']}, "
                f"contains={row['contains_ok']}"
            )

    lines += [
        "",
        "## Đọc báo cáo",
        "",
        "- Chất lượng là cột Đạt, không phải cảm nhận.",
        "- p95 quan trọng hơn trung bình: người dùng nhớ lần chậm nhất.",
        "- Chi phí tính trên cùng bộ case; muốn biết chi phí tháng, nhân với lưu lượng.",
        "",
    ]

    report = Path(__file__).with_name("reports") / "eval-report.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines[:14]))
    print("...")
    print(f"\nĐã ghi báo cáo: {report}")
    print(f"Kết quả: {passed}/{len(rows)} case đạt.")
