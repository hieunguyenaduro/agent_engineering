# Buổi 2 — Agent Loop Engineering với LangGraph

> Buổi 1 bạn tự viết vòng `for`. Buổi này thay nó bằng một graph có state, checkpoint, streaming và chỗ dừng cho con người. Code không ngắn hơn nhiều, nhưng **quan sát được** và **chịu lỗi** tốt hơn hẳn.

**Thời lượng:** 120 phút — 55 phút giảng + demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-02
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # dán OPENAI_API_KEY
python 01_graph_basics.py     # không cần key
python 02_agent_loop.py
```

Không có key: thêm `FAKE=1`.

```bash
FAKE=1 python 02_agent_loop.py
```

`FAKE=1` dùng `FakeToolModel` — một chat model giả lập nói đúng giao thức LangChain. Nó đủ để graph, checkpoint, interrupt, streaming chạy thật. Nó **không** đủ để đánh giá chất lượng câu trả lời.

---

## 1. Vì sao cần graph? (5 phút)

Vòng `for` ở buổi 1 có bốn vấn đề khi lên production:

| Vấn đề | Hậu quả |
|---|---|
| State nằm trong biến local | Process chết là mất sạch |
| Không có điểm dừng | Không thể chèn bước xin phép |
| Không quan sát được từng bước | Debug bằng `print`, không tái hiện được |
| Không resume được | Chạy lại từ đầu, tốn tiền gấp đôi |

LangGraph biến vòng lặp thành một **máy trạng thái có lưu vết**. Mỗi bước là một node, mỗi lần chuyển là một edge, state sau mỗi bước được lưu thành checkpoint.

---

## 2. Ba khái niệm (15 phút)

Chạy `01_graph_basics.py` — file này **không gọi model**, chỉ để thấy graph là gì.

```python
class State(TypedDict):
    question: str
    route: str
    answer: str

def classify(state: State) -> dict:
    return {"route": "billing"}      # chỉ trả về phần cần cập nhật

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_conditional_edges("classify", lambda s: s["route"], {...})
graph = builder.compile()
```

| Khái niệm | Nghĩa | Ví dụ trong file |
|---|---|---|
| **State** | Dữ liệu đi qua graph, có kiểu rõ ràng | `question`, `route`, `answer` |
| **Node** | Hàm nhận state, trả về phần state muốn sửa | `classify`, `billing` |
| **Edge** | Bước tiếp theo, có thể có điều kiện | `add_conditional_edges` |
| **Compile** | Biến định nghĩa thành thứ chạy được | `builder.compile()` |

Điểm dễ sai: node **không sửa state tại chỗ**, nó trả về dict và LangGraph merge dict đó vào state.

Cuối file in ra `draw_mermaid()`. Dán vào [mermaid.live](https://mermaid.live) sẽ thấy hình graph — dùng để review thiết kế với người không đọc code.

> **Một câu chốt:** graph là cách vẽ vòng lặp ra giấy, rồi để máy chạy đúng bản vẽ đó.

---

## 3. Agent loop thành graph (15 phút)

Chạy `02_agent_loop.py`. So với `06_mini_harness.py` của buổi 1:

| Buổi 1 | Buổi 2 |
|---|---|
| `for step in range(MAX_STEPS)` | hai node nối thành vòng |
| `if not message.tool_calls: break` | `tools_condition` |
| `TOOL_FUNCTIONS[name](**args)` | `ToolNode(TOOLS)` |
| `messages.append(...)` thủ công | state tự merge |

```python
builder.add_node("agent", agent_node)     # model quyết định
builder.add_node("tools", ToolNode(TOOLS))# chạy tool
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")        # quay lại agent
```

`ToolNode` tự chạy **mọi** tool trong `tool_calls`, tự tạo `ToolMessage` với đúng `tool_call_id`. Đây là phần dễ viết sai nhất khi tự làm — và cũng là lý do nên dùng thư viện.

> **Một câu chốt:** graph không làm agent thông minh hơn; nó làm agent **hiểu được**.

---

## 4. Checkpoint: ngủ dậy vẫn nhớ (15 phút)

Chạy `03_checkpoint.py`:

```python
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "khach-A"}}
graph.invoke({"messages": [...]}, config)
```

Ba điều cần nhớ:

1. **`thread_id` là danh tính cuộc hội thoại.** Cùng id → nối tiếp. Khác id → tách biệt hoàn toàn. Đây là nền của multi-user ở buổi 9.
2. **Checkpoint là ảnh chụp sau mỗi bước**, không phải sau mỗi câu trả lời.
3. **Resume không chạy lại từ đầu.** Graph biết bước tiếp theo là gì nhờ `snapshot.next`.

Đổi `InMemorySaver` thành `SqliteSaver` (hoặc Postgres) là có persistence thật. Ở production, đây là thứ giúp agent sống sót qua deploy và restart.

Xem lịch sử:

```python
for snapshot in graph.get_state_history(config):
    print(snapshot.values["messages"], snapshot.next)
```

> **Một câu chốt:** state không nằm trong RAM của bạn, state nằm trong checkpoint.

---

## 5. Streaming (10 phút)

Chạy `04_streaming.py`. Hai chế độ:

| Chế độ | Trả về | Dùng cho |
|---|---|---|
| `stream_mode="updates"` | mỗi node một event | hiện tiến độ: "đang tra đơn..." |
| `stream_mode="messages"` | từng mẩu chữ | hiện câu trả lời chạy như ChatGPT |

```python
for event in graph.stream(inputs, stream_mode="updates"):
    for node_name, update in event.items():
        print(node_name, update)

for chunk, metadata in graph.stream(inputs, stream_mode="messages"):
    print(chunk.content, end="", flush=True)
```

Streaming không chỉ để cho đẹp. Nó là cách duy nhất để người dùng biết agent đang làm gì trong 20 giây chờ đợi — và là nền của SSE ở buổi 9.

> **Một câu chốt:** agent im lặng 20 giây bị coi là agent hỏng.

---

## 6. Human-in-the-loop (15 phút)

Chạy `05_human_in_the_loop.py`. Kịch bản: agent muốn hoàn tiền — hành động không thể hoàn tác.

```python
def approval_node(state):
    call = state["messages"][-1].tool_calls[0]

    decision = interrupt({                 # graph DỪNG tại đây
        "tool": call["name"],
        "args": call["args"],
    })

    if decision == "approve":
        content = issue_refund.invoke(call["args"])
    else:
        content = "Người dùng đã từ chối."
    return {"messages": [ToolMessage(content=content, tool_call_id=call["id"])]}
```

Chạy lần một, graph trả về `__interrupt__` thay vì câu trả lời. Chương trình của bạn hiện nút Duyệt/Từ chối. Chạy tiếp:

```python
graph.invoke(Command(resume="approve"), config)
```

Graph chạy tiếp **từ đúng chỗ dừng**. Không gọi lại model, không làm lại các bước trước — vì checkpoint đã lưu.

Ba mức kiểm soát, tăng dần:

1. **Xin phép trước mọi tool** — an toàn nhất, phiền nhất.
2. **Chỉ xin phép tool nguy hiểm** (hoàn tiền, gửi mail, xoá file) — mức nên dùng.
3. **Cho chạy, nhưng ghi audit để hoàn tác** — chỉ khi hoàn tác được thật.

> **Một câu chốt:** interrupt là ranh giới giữa "agent tự làm" và "agent đề nghị".

---

## 7. Chặn vòng lặp chạy mãi (10 phút)

Chạy `06_guard_loop.py`. File có hai graph: một graph cố tình hỏng, một graph có phanh.

| Lớp | Cơ chế | Ưu / nhược |
|---|---|---|
| A. `recursion_limit` | LangGraph chặn cứng | Rẻ, nhưng người dùng nhận exception xấu |
| B. Ngân sách bước | Đếm trong state, dừng và trả lời | Tốt, cần thiết kế câu trả lời khi hết lượt |
| C. Phát hiện lặp | Hai hành động giống nhau liên tiếp → dừng | Bắt được lặp "thông minh", dễ báo nhầm |

```python
def next_step(state):
    if state["steps"] >= MAX_STEPS:
        return "stop"
    ...
```

Bài học thực tế: **A luôn bật, B luôn viết, C chỉ khi có dữ liệu cho thấy cần.**

> **Một câu chốt:** đừng để lớp bảo vệ duy nhất là một exception.

---

## 8. Lab (60 phút)

### Phần A — Chạy và đọc (25 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_graph_basics.py` | Node trả về gì? Ai merge vào state? |
| `02_agent_loop.py` | Bỏ `add_edge("tools","agent")` thì chuyện gì xảy ra? |
| `03_checkpoint.py` | Đổi `thread_id` thì memory thay đổi thế nào? |
| `04_streaming.py` | UI cần event nào để hiện "đang tra đơn"? |
| `05_human_in_the_loop.py` | Nếu process chết lúc đang chờ duyệt thì sao? |
| `06_guard_loop.py` | Phanh nào bắt được lặp, phanh nào chỉ bắt được "chạy lâu"? |

### Phần B — Nâng cấp harness của bạn (35 phút)

Lấy `06_mini_harness.py` của buổi 1 và chuyển sang LangGraph. Yêu cầu tối thiểu:

- Có `StateGraph` với node agent + node tools.
- Có checkpointer và `thread_id`.
- Có streaming `updates`.
- Có ít nhất một tool cần con người duyệt.

Làm theo `exercises.md` nếu cần gợi ý từng bước.

---

## 9. Bài tập về nhà

Xem `exercises.md`. Bắt buộc bài 1 và bài 3.

---

## 10. Tổng kết — 5 câu mang về

1. Graph = state + node + edge. Node trả về phần state cần sửa, không sửa tại chỗ.
2. `thread_id` là danh tính hội thoại; checkpoint là ảnh chụp sau mỗi bước.
3. Streaming là yêu cầu về trải nghiệm, không phải tính năng phụ.
4. `interrupt` biến hành động nguy hiểm thành đề nghị.
5. Luôn có ít nhất hai lớp chống lặp: giới hạn cứng và ngân sách bước.

---

## 11. Chuẩn bị buổi 3

- Cài `mcp` và `fastapi` (có trong `requirements.txt` của buổi 3).
- Đọc lại `common/shop.py`: để ý `@tool` và docstring — buổi 3 sẽ nói vì sao docstring là một phần của API.
- Mang theo một ý tưởng tool mà agent của bạn sẽ cần.

---

## Phụ lục — Cấu trúc thư mục

```
session-02/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_graph_basics.py
├── 02_agent_loop.py
├── 03_checkpoint.py
├── 04_streaming.py
├── 05_human_in_the_loop.py
├── 06_guard_loop.py
├── common/
│   ├── llm.py          ← chọn OpenAI hay model giả
│   ├── fake_model.py   ← model giả để chạy offline / viết test
│   └── shop.py         ← dữ liệu + tool
├── exercises.md
├── requirements.txt
└── .env.example
```
