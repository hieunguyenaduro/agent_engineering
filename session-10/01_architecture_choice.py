"""Bài 01 — Chọn kiến trúc bằng bảng điểm, không bằng cảm giác.

Chạy:  python 01_architecture_choice.py

Ba phương án cho cùng một bài toán chăm sóc khách hàng:
    A. Một agent + retrieval
    B. Supervisor + hai worker (retrieval, response)
    C. Handoff chain (triage -> retrieval -> response)

Mỗi tiêu chí có trọng số. Điểm 1–5. Tổng = trung bình có trọng số.
Đây không phải công thức chân lý — nó là cách buộc bạn nói ra mình đang đánh đổi gì.
"""

# Trọng số phải cộng lại = 1.0
CRITERIA = {
    "chat_luong": (0.30, "Chất lượng câu trả lời"),
    "do_tre": (0.20, "Độ trễ thấp"),
    "chi_phi": (0.20, "Chi phí thấp"),
    "don_gian": (0.15, "Dễ xây và dễ hiểu"),
    "debug": (0.15, "Dễ debug khi sai"),
}

OPTIONS = {
    "A. Một agent + retrieval": {
        "chat_luong": 4, "do_tre": 5, "chi_phi": 5, "don_gian": 5, "debug": 5,
        "ghi_chu": "Một prompt, một vòng lặp, một tool search.",
    },
    "B. Supervisor + 2 worker": {
        "chat_luong": 5, "do_tre": 3, "chi_phi": 3, "don_gian": 2, "debug": 3,
        "ghi_chu": "Tách tra cứu và soạn câu trả lời; supervisor chọn nhánh.",
    },
    "C. Handoff chain": {
        "chat_luong": 4, "do_tre": 2, "chi_phi": 2, "don_gian": 2, "debug": 2,
        "ghi_chu": "Chuyển hẳn ngữ cảnh qua ba agent; tốt khi cần chuyên trách.",
    },
}


def score(option: dict) -> float:
    return sum(weight * option[key] for key, (weight, _) in CRITERIA.items())


def show_table() -> None:
    headers = ["Phương án", "Chất lượng", "Độ trễ", "Chi phí", "Đơn giản", "Debug", "Điểm"]
    widths = [28, 12, 9, 9, 11, 9, 7]

    print("".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("-" * sum(widths))
    for name, option in OPTIONS.items():
        cells = [name] + [str(option[key]) for key in CRITERIA] + [f"{score(option):.2f}"]
        print("".join(c.ljust(w) for c, w in zip(cells, widths)))


def sensitivity() -> None:
    """Đổi trọng số thì kết luận có đổi không? Nếu có, đó là điểm yếu của lựa chọn."""
    print("\n=== Kiểm tra độ nhạy ===")
    scenarios = {
        "Cân bằng (mặc định)": dict(CRITERIA),
        "Ưu tiên độ trễ gấp đôi": {
            **CRITERIA, "do_tre": (0.40, "Độ trễ thấp"), "chat_luong": (0.20, "Chất lượng")},
        "Ưu tiên chất lượng gấp đôi": {
            **CRITERIA, "chat_luong": (0.50, "Chất lượng"), "do_tre": (0.10, "Độ trễ thấp")},
    }

    for label, weights in scenarios.items():
        total = sum(weight for weight, _ in weights.values())
        ranking = sorted(
            (
                (name, sum(weight * option[key] for key, (weight, _) in weights.items()) / total)
                for name, option in OPTIONS.items()
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        winner = ranking[0]
        print(f"  {label:32} -> {winner[0]} ({winner[1]:.2f})")


if __name__ == "__main__":
    print("=== Bảng điểm kiến trúc ===\n")
    show_table()

    best_name = max(OPTIONS, key=lambda name: score(OPTIONS[name]))
    best = OPTIONS[best_name]
    print(f"\nĐề xuất: {best_name} — {best['ghi_chu']}")

    print("\nVì sao không chọn đơn giản nhất hoặc mạnh nhất:")
    print("- A đơn giản nhất, nhưng chất lượng thấp hơn khi câu hỏi cần cả tra cứu lẫn soạn.")
    print("- B chất lượng cao nhất, nhưng tốn thêm một lần gọi model và khó debug hơn.")
    print("- C chỉ thắng khi cần chuyển hẳn ngữ cảnh cho người/bộ phận khác.")

    sensitivity()

    print("\nĐiểm quan trọng: bảng này là công cụ để tranh luận, không phải để che giấu.")
    print("Nếu đổi trọng số mà người thắng đổi, hãy nói rõ bạn đang ưu tiên gì.")
