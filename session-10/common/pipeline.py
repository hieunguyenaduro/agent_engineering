"""Pipeline capstone: retrieve -> chọn câu -> trả lời có trích dẫn -> đo.

Một hàm `answer()` duy nhất để mọi bài khác gọi. Nhờ vậy failure drill,
eval và cost dùng đúng cùng một hệ thống, không phải ba bản khác nhau.
"""

import re
import time

from common.knowledge import RetrievalError, retrieve, tokens

MIN_SCORE = 0.12
INPUT_PRICE = 0.15     # USD / 1M token, ví dụ
OUTPUT_PRICE = 0.60
BUDGET_USD = 0.0005


class BudgetExceeded(RuntimeError):
    pass


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _best_sentence(question: str, doc: str) -> str:
    query = set(tokens(question))
    scored = [(len(query & set(tokens(sentence))), sentence) for sentence in _sentences(doc)]
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1] if scored and scored[0][0] else _sentences(doc)[0]


def answer(question: str, tenant: str = "shop-a", fail: str | None = None) -> dict:
    """Trả dict thay vì chuỗi: người gọi cần nguồn, chi phí, trạng thái."""
    started = time.perf_counter()
    spans = []
    result = {
        "question": question,
        "tenant": tenant,
        "status": "ok",
        "answer": "",
        "sources": [],
        "spans": spans,
        "tokens": 0,
        "cost_usd": 0.0,
        "latency_ms": 0.0,
    }

    # --- retrieve -----------------------------------------------------------
    step = time.perf_counter()
    try:
        hits = retrieve(question, tenant, k=2, fail=fail)
        spans.append({"name": "retrieve", "ms": round((time.perf_counter() - step) * 1000, 1),
                      "status": "ok", "detail": f"{len(hits)} tài liệu"})
    except RetrievalError as exc:
        spans.append({"name": "retrieve", "ms": round((time.perf_counter() - step) * 1000, 1),
                      "status": "error", "detail": str(exc)})
        result.update(
            status="degraded",
            answer="Hệ thống tra cứu đang bảo trì. Bạn thử lại sau ít phút hoặc gọi hotline.",
        )
        result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        return result

    if not hits or hits[0]["score"] < MIN_SCORE:
        spans.append({"name": "guard", "ms": 0.0, "status": "refused",
                      "detail": "không đủ dữ liệu"})
        result.update(
            status="refused",
            answer="Mình không tìm thấy tài liệu đủ liên quan, nên không thể trả lời chắc chắn.",
        )
        result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        return result

    # --- generation ---------------------------------------------------------
    step = time.perf_counter()
    if fail == "model_error":
        spans.append({"name": "generate", "ms": 0.0, "status": "error",
                      "detail": "model trả 500"})
        result.update(status="error", answer="Có lỗi khi tạo câu trả lời. Vui lòng thử lại.")
        result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        return result

    if fail == "slow_model":
        time.sleep(0.35)

    top = hits[0]
    sentence = _best_sentence(question, top["text"])
    reply = f"{sentence} [nguon: {top['source']}]"
    spans.append({"name": "generate", "ms": round((time.perf_counter() - step) * 1000, 1),
                  "status": "ok", "detail": f"{len(reply.split())} từ"})

    # --- guard chi phí ------------------------------------------------------
    input_tokens = (len(question) + sum(len(hit["text"]) for hit in hits)) // 4
    output_tokens = len(reply) // 4
    cost = (input_tokens * INPUT_PRICE + output_tokens * OUTPUT_PRICE) / 1_000_000
    if cost > BUDGET_USD:
        raise BudgetExceeded(f"vượt ngân sách: {cost:.6f} > {BUDGET_USD}")

    result.update(
        answer=reply,
        sources=[{"source": hit["source"], "score": hit["score"]} for hit in hits],
        tokens=input_tokens + output_tokens,
        cost_usd=round(cost, 8),
    )
    result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
    return result
