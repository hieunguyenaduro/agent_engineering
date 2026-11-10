"""LLM-as-judge: dùng model thật khi có key, judge giả lập khi không.

Judge thật không ổn định tuyệt đối. Vì vậy mọi lời gọi đều được bọc trong
try/except và có fallback; bài 05 còn so điểm judge với nhãn người.
"""

from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

RUBRIC = """Thang điểm 1-5:
5 = đúng, đủ ý, đúng giọng điệu, không bịa
4 = đúng nhưng thiếu một chi tiết nhỏ
3 = đúng một phần, thiếu hoặc mơ hồ
2 = sai phần lớn, vẫn liên quan
1 = sai, bịa, hoặc làm hành động không được phép"""

PROMPT = """Bạn là người chấm điểm câu trả lời của một agent chăm sóc khách hàng.

Câu hỏi: {question}
Câu trả lời cần chấm: {answer}
Đáp án tham chiếu: {reference}

{rubric}

Chỉ trả về JSON đúng định dạng, không thêm chữ khác:
{{"score": <số 1-5>, "reason": "<một câu ngắn>"}}"""


def build_prompt(question: str, answer: str, reference: str) -> str:
    return PROMPT.format(question=question, answer=answer, reference=reference, rubric=RUBRIC)


def parse_judgement(text: str) -> tuple[int, str]:
    """Lấy JSON ra khỏi câu trả lời; model hay bọc trong ```json ... ```."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("không tìm thấy JSON trong câu trả lời của judge")
    data = json.loads(text[start : end + 1])
    score = int(data["score"])
    if not 1 <= score <= 5:
        raise ValueError(f"điểm ngoài khoảng 1-5: {score}")
    return score, str(data.get("reason", "")).strip()[:200]


def fake_judge(question: str, answer: str, reference: str) -> tuple[int, str, str]:
    """Judge giả lập: chấm theo trùng từ khoá, cộng điểm nếu câu dài và tự tin.

    Nó cố tình nông — để bạn thấy một judge chỉ nhìn bề mặt sẽ lệch nhãn người.
    """
    ref_words = {word for word in re.findall(r"\w+", reference.lower()) if len(word) > 3}
    ans_words = {word for word in re.findall(r"\w+", answer.lower()) if len(word) > 3}
    overlap = len(ref_words & ans_words) / max(1, len(ref_words))
    score = 1 + round(4 * overlap)
    confident = any(word in answer.lower() for word in ("chắc chắn", "đã", "hoàn toàn"))
    if len(answer.split()) > 8 and confident:
        score = min(5, score + 1)
    reason = f"trùng từ khoá {overlap:.0%}; câu dài/tự tin được cộng điểm"
    return score, reason, "fake"


def real_judge(question: str, answer: str, reference: str) -> tuple[int, str, str]:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        messages=[{"role": "user", "content": build_prompt(question, answer, reference)}],
    )
    score, reason = parse_judgement(response.choices[0].message.content or "")
    return score, reason, "llm"


def judge_answer(question: str, answer: str, reference: str) -> tuple[int, str, str]:
    """Trả về (điểm, lý do, nguồn). Không bao giờ ném lỗi ra ngoài."""
    if os.getenv("FAKE") == "1":
        return (*fake_judge(question, answer, reference)[:2], "fake (FAKE=1)")
    if not os.getenv("OPENAI_API_KEY"):
        return (*fake_judge(question, answer, reference)[:2], "fake (thiếu OPENAI_API_KEY)")
    try:
        return real_judge(question, answer, reference)
    except Exception as exc:
        score, reason, _ = fake_judge(question, answer, reference)
        return score, f"{reason} [fallback: {type(exc).__name__}]", "fake (lỗi gọi model)"
