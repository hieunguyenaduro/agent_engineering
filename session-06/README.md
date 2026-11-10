# Buổi 6 — Multi-agent Systems

> Một agent giỏi một việc thường tốt hơn một agent ôm đồm. Buổi này tách agent của bạn thành nhiều agent nhỏ, nối chúng bằng ba kiểu quan hệ: **gọi như tool**, **supervisor điều phối**, và **handoff chuyển quyền**. Kèm theo là hai câu hỏi luôn bị bỏ qua: nhánh nào chết thì sao, và tiền tăng bao nhiêu.

**Thời lượng:** 120 phút — 55 phút giảng + demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-06
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # dán OPENAI_API_KEY nếu có
FAKE=1 python 01_subagent_as_tool.py
```

Tất cả sáu ví dụ chạy **không cần API key, không cần Docker**. Bài 01 dùng model giả để đi đúng giao thức tool-calling; các bài còn lại dùng hàm Python đóng vai agent, để bạn nhìn rõ phần điều phối mà không bị nhiễu bởi chất lượng câu trả lời.

Khi có key:

```bash
python 01_subagent_as_tool.py     # dùng OpenAI thật
```

---

## 1. Khi nào nên tách nhiều agent? (5 phút)

Không phải lúc nào cũng nên. Tách chỉ có lợi khi:

| Dấu hiệu | Vì sao tách |
|---|---|
| Một prompt phải làm 3–4 việc khác nhau | Mỗi agent một nhiệm vụ, prompt ngắn hơn |
| Mỗi việc cần bộ tool riêng | Giảm số tool model phải chọn, giảm chọn sai |
| Các việc có thể chạy song song | Giảm thời gian chờ |
| Cần chuyển cho người/bộ phận khác | Handoff giữ nguyên ngữ cảnh |

Tách sai cách sẽ tạo ra **một hệ thống chậm hơn, đắt hơn, khó debug hơn** — mà vẫn trả lời sai.

> **Một câu chốt:** multi-agent là cách chia việc, không phải cách làm agent thông minh hơn.

---

## 2. Subagent như một tool (12 phút)

Chạy `01_subagent_as_tool.py`.

```
main graph:  agent ──(gọi research)──> tools ──> agent ──> END
research:    START ──> gather ──> summarize ──> END   (graph lồng bên trong)
```

Cách làm: build graph con, compile, rồi bọc trong một hàm có `@tool`.

```python
researcher = research_builder.compile()

@tool
def research(query: str) -> str:
    """Giao một câu hỏi cho subagent nghiên cứu và nhận báo cáo ngắn."""
    result = researcher.invoke({"query": query, "notes": [], "report": ""})
    return result["report"]
```

Với agent chính, `research` chỉ là một function nhận chuỗi, trả chuỗi. Nó không biết bên trong có mấy bước, dùng tool gì, gọi model mấy lần.

| Được | Mất |
|---|---|
| Tách biệt hoàn toàn, dễ test | Không quan sát được bên trong nếu không log |
| Agent chính không bị nhiễu bởi tool của subagent | Mỗi lần gọi là thêm một lần gọi model |
| Có thể thay subagent mà không sửa agent chính | Kết quả trả về phải tự đủ nghĩa |

Đây là kiểu tách **rẻ nhất** và nên dùng đầu tiên. Chỉ khi cần agent sau tiếp tục hội thoại mới chuyển sang handoff.

> **Một câu chốt:** subagent-as-tool biến "nhiều agent" thành "một tool", và đó thường là đủ.

---

## 3. Supervisor: một agent điều phối (12 phút)

Chạy `02_supervisor.py`.

```
START ──> supervisor ──┬──> billing  ──┐
                       ├──> technical ──┼──> summarize ──> END
                       └──> general  ──┘
```

Trong file, supervisor là hàm `if/else`. Ở production, nó là một LLM gọi structured output:

```python
class Route(BaseModel):
    route: Literal["billing", "technical", "general"]
    reason: str

decision = llm.with_structured_output(Route).invoke([...])
return {"route": decision.route}
```

Ba nguyên tắc thiết kế supervisor:

1. **Supervisor không tự làm việc.** Nó chỉ chọn người và ghi lý do.
2. **Luôn có nhánh fallback** (`general`). Không có nhánh này, câu hỏi lạ sẽ rơi vào hư không.
3. **Ghi lại quyết định** (`log`). Khi agent trả lời sai, câu hỏi đầu tiên là "ai đã nhận việc này?".

Đừng để supervisor gọi chính nó. Nếu supervisor cần suy nghĩ nhiều bước, đó là dấu hiệu nó đang làm việc của worker.

> **Một câu chốt:** supervisor giỏi nhất khi nó chỉ làm một việc: chọn đúng người.

---

## 4. Chạy song song với Send (12 phút)

Chạy `03_parallel_fanout.py`.

```python
class State(TypedDict):
    findings: Annotated[list[str], operator.add]

def fan_out(state):
    return [Send("worker", {"topic": t}) for t in state["topics"]]

builder.add_node("aggregate", aggregate, defer=True)
builder.add_conditional_edges("supervisor", fan_out, ["worker"])
builder.add_edge("worker", "aggregate")
```

Ba điểm kỹ thuật, thiếu cái nào cũng sai:

1. **Reducer** `Annotated[list, operator.add]`: nhiều worker cùng ghi vào một list. Không có nó, worker sau ghi đè worker trước.
2. **`Send`** phát một nhánh cho mỗi việc. Payload chỉ cần đúng phần worker cần đọc.
3. **`defer=True`** để `aggregate` chạy **một lần**, sau khi mọi nhánh xong. Không có nó, aggregate chạy sau từng worker và bạn tổng hợp dở dang.

Muốn chạy **thật** song song, worker phải là `async def` và gọi bằng `ainvoke`:

```python
async def worker(state):
    await asyncio.sleep(0.3)
    return {"findings": [...]}

result = asyncio.run(graph.ainvoke(inputs))
```

Nếu dùng hàm sync, LangGraph chạy lần lượt. `Send` vẫn đúng về logic nhưng không nhanh hơn — và đây là hiểu nhầm rất phổ biến.

Đo trong ví dụ: 3 nhánh × 0.3s, chạy song song khoảng 0.32s, tuần tự khoảng 0.9s.

> **Một câu chốt:** song song chỉ có thật khi code là async; còn lại chỉ là song song trên giấy.

---

## 5. Handoff: chuyển quyền, giữ ngữ cảnh (12 phút)

Chạy `04_handoff.py`.

```
START ──> triage ──Command──> billing_agent ──Command──> refund_agent ──> END
```

```python
from langgraph.types import Command

def triage(state) -> Command[Literal["billing_agent", "technical_agent"]]:
    return Command(
        goto="billing_agent",
        update={
            "assigned_to": "billing_agent",
            "messages": [AIMessage(content="[triage] Chuyển tới billing_agent.")],
        },
    )
```

Khác biệt cốt lõi với subagent-as-tool:

| | Subagent as tool | Handoff |
|---|---|---|
| Ai nói câu cuối | Agent gọi | Agent được chuyển tới |
| Ngữ cảnh | Chỉ tham số truyền vào | Toàn bộ messages |
| Quay lại agent cũ | Có | Không |
| Dùng khi | Việc phụ, lấy dữ liệu | Chuyển hẳn ca làm việc |

Trong ví dụ, `refund_agent` đọc được câu hỏi gốc và cả ghi chú của `billing_agent`. Nhờ vậy nó không hỏi lại khách "đơn của bạn là gì?" — điều mà khách rất ghét.

Cẩn thận: handoff có thể thành vòng lặp (`A -> B -> A`). Luôn có luật dừng, ví dụ mỗi agent chỉ được handoff một lần, hoặc đếm tổng số handoff.

> **Một câu chốt:** handoff là chuyển ca, không phải chuyển việc — người sau phải thấy đủ hồ sơ.

---

## 6. Một nhánh chết thì sao? (10 phút)

Chạy `05_partial_failure.py`.

Hai kịch bản trong file:

- `refund` ném `RuntimeError` — dịch vụ bảo trì.
- `legacy` chậm hơn `TIMEOUT` — bị `asyncio.wait_for` cắt.

Worker bắt cả hai và trả về **dữ liệu**, không để exception bay lên:

```python
async def worker(state):
    try:
        answer = await asyncio.wait_for(call_service(topic), timeout=TIMEOUT)
        return {"findings": [answer]}
    except asyncio.TimeoutError:
        return {"errors": [f"{topic}: timeout"]}
    except Exception as exc:
        return {"errors": [f"{topic}: {exc}"]}
```

Aggregator quyết định: trả lời một phần kèm lời thú nhận, hay báo lỗi toàn bộ. Trong file, nó trả lời phần lấy được và ghi rõ phần thiếu.

Ba mức xử lý lỗi, tăng dần:

1. **Để exception bay lên** — người dùng nhận 500, không biết gì. Không chấp nhận được.
2. **Bắt lỗi, trả lời một phần** — mặc định nên dùng cho agent có nhiều nguồn.
3. **Retry + fallback** — chỉ khi biết chắc lỗi tạm thời và có nguồn dự phòng.

Đừng retry vô hạn. Một worker lỗi ba lần thì nên bỏ và ghi lại, không giữ cả request.

> **Một câu chốt:** lỗi của một nhánh phải là dữ liệu của nhánh tổng hợp.

---

## 7. Chi phí: đo trước khi nhân bản (8 phút)

Chạy `06_cost_budget.py`.

Mỗi lần giao việc là một lần gọi model. Ba worker + một aggregator = bốn lần gọi, chưa kể retry. File này đếm thật:

```python
@dataclass
class Budget:
    max_calls: int
    calls: int = 0
    ...
    def charge(self, agent, input_tokens, output_tokens):
        ...
```

Supervisor giữ lại **một slot cho aggregate** trước khi phát việc:

```python
remaining = max(0, BUDGET.max_calls - BUDGET.calls - 1)
topics = TOPICS[:remaining]
skipped = TOPICS[remaining:]
```

Nếu không giữ slot, worker ăn hết ngân sách và bước tổng hợp vượt trần — lỗi thiết kế rất dễ mắc.

Đọc bảng kết quả:

| Con số | Nói gì |
|---|---|
| Số lần gọi | Tăng tuyến tính theo số worker |
| Token | Mỗi worker mang ngữ cảnh riêng, không chia sẻ |
| USD | Chỉ là ước lượng; giá thật kiểm tra lại |

Với tác vụ nhỏ, multi-agent có thể rẻ hơn một agent ôm đồm vì mỗi prompt ngắn hơn. Với tác vụ lớn, nó thường đắt hơn. Không có câu trả lời chung — phải đo trên workload của bạn.

> **Một câu chốt:** không đo chi phí thì không biết mình đang mua gì.

---

## 8. Lab (60 phút)

### Phần A — Chạy và đọc (25 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_subagent_as_tool.py` | Agent chính biết gì về bên trong subagent? |
| `02_supervisor.py` | Nếu bỏ nhánh `general` thì câu hỏi lạ đi đâu? |
| `03_parallel_fanout.py` | Bỏ `defer=True` thì aggregate chạy mấy lần? |
| `04_handoff.py` | `refund_agent` đọc được thông tin gì mà subagent-as-tool không có? |
| `05_partial_failure.py` | Nếu bỏ `try/except` trong worker thì người dùng thấy gì? |
| `06_cost_budget.py` | Vì sao phải giữ một slot cho aggregate? |

### Phần B — Tách agent của bạn (35 phút)

Lấy agent ở buổi 5 và tách thành hai agent:

1. **Researcher** — chỉ có tool tìm kiếm, trả về báo cáo ngắn.
2. **Responder** — nhận báo cáo, viết câu trả lời cho người dùng.

Chọn một trong hai cách: subagent-as-tool hoặc handoff. Ghi lại vì sao chọn cách đó.

Yêu cầu tối thiểu:

- Có log cho thấy ai nhận việc gì.
- Có xử lý khi researcher không tìm thấy dữ liệu.
- Có đếm số lần gọi model.

Làm theo `exercises.md` nếu cần gợi ý.

---

## 9. Bài tập về nhà

Xem `exercises.md`. Bắt buộc bài 1 và bài 4.

---

## 10. Tổng kết — 5 câu mang về

1. Multi-agent là cách chia việc, không phải cách làm agent thông minh hơn.
2. Subagent-as-tool là kiểu tách rẻ nhất; handoff chỉ khi cần giữ nguyên hội thoại.
3. Supervisor chỉ nên chọn người, luôn có nhánh fallback và ghi lý do.
4. Song song chỉ thật khi worker là async; `defer=True` để tổng hợp một lần.
5. Lỗi của một nhánh phải là dữ liệu, và chi phí phải được đo trước khi nhân bản.

---

## 11. Chuẩn bị buổi 7

- Đọc lại `05_partial_failure.py`: ghi lại ba thứ bạn muốn nhìn thấy khi một nhánh chậm.
- Buổi 7 sẽ trả lời: làm sao biết agent tốt lên hay tệ đi, bằng số.
- Mang theo một failure case thật mà agent của bạn từng trả lời sai.

---

## Phụ lục — Cấu trúc thư mục

```
session-06/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_subagent_as_tool.py
├── 02_supervisor.py
├── 03_parallel_fanout.py
├── 04_handoff.py
├── 05_partial_failure.py
├── 06_cost_budget.py
├── common/
│   ├── llm.py
│   └── fake_model.py
├── exercises.md
├── requirements.txt
└── .env.example
```
