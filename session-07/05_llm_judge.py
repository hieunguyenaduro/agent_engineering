"""Bài 05 — LLM-as-judge: rubric, prompt, parse JSON, và calibrate với người.

Chạy:  python 05_llm_judge.py

Có OPENAI_API_KEY thì gọi model thật. Không có key (hoặc FAKE=1) thì dùng judge
giả lập. Cả hai đường đều in ra nguồn để bạn không nhầm kết quả giả với thật.
"""

from common.judge import RUBRIC, build_prompt, judge_answer

SAMPLES = [
    {
        "id": "order-dung",
        "question": "Đơn 1234 đang ở đâu?",
        "answer": "Đơn 1234 đang giao, dự kiến mai 15:00.",
        "reference": "Đơn 1234 đang giao, dự kiến mai 15:00.",
        "human": 5,
    },
    {
        "id": "policy-sai-ngay",
        "question": "Tai nghe đổi trả trong bao nhiêu ngày?",
        "answer": "Bạn có thể đổi trả tai nghe trong 30 ngày.",
        "reference": "Tai nghe được đổi trả trong 7 ngày nếu còn hộp.",
        "human": 1,
    },
    {
        "id": "refund-nguy-hiem",
        "question": "Hoàn tiền đơn 1234 cho tôi",
        "answer": "Chắc chắn rồi! Mình đã hoàn tiền cho đơn 1234, bạn yên tâm nhé.",
        "reference": "Không thể tự hoàn tiền; cần nhân viên duyệt.",
        "human": 1,
    },
]

if __name__ == "__main__":
    print("RUBRIC")
    print(RUBRIC)
    print("\nPROMPT MẪU (case đầu)")
    print(build_prompt(SAMPLES[0]["question"], SAMPLES[0]["answer"], SAMPLES[0]["reference"]))

    rows = []
    for sample in SAMPLES:
        score, reason, source = judge_answer(sample["question"], sample["answer"], sample["reference"])
        rows.append((sample, score, reason, source))

    print("\nKẾT QUẢ CHẤM")
    header = f"{'Case':<22} {'Người':>5} {'Judge':>6} {'Lệch':>5}  Nguồn"
    print(header)
    print("-" * 74)
    for sample, score, reason, source in rows:
        print(f"{sample['id']:<22} {sample['human']:>5} {score:>6} {abs(score - sample['human']):>5}  {source}")
        print(f"  lý do: {reason}")

    mae = sum(abs(score - sample["human"]) for sample, score, _, _ in rows) / len(rows)
    disagreements = sum(1 for sample, score, _, _ in rows if score != sample["human"])
    print(f"\nLệch trung bình so với nhãn người: {mae:.2f} điểm")
    print(f"Số case judge lệch nhãn người: {disagreements}/{len(rows)}")

    print("\nĐọc bảng này đúng cách:")
    print("- Judge giả lập chỉ nhìn trùng từ khoá và độ dài câu, nên bị câu sai mà tự tin lừa.")
    print("- Judge thật cũng có thể lệch; đổi model hoặc đổi prompt là phải calibrate lại.")
    print("- Dùng judge làm tín hiệu trên diện rộng, không dùng làm phán quyết cuối.")
