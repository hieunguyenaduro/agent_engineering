# Buổi 1 — Hệ thống agent hiện đại và harness

> Mục tiêu duy nhất của buổi này: bạn nhìn một agent và **chỉ ra được cái gì là model, cái gì là phần mềm bạn viết**. Mọi thứ còn lại của khóa học chỉ là làm dày phần mềm đó lên.

**Thời lượng:** 120 phút — 55 phút giảng + demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Sau buổi này bạn làm được gì

1. Giải thích được vì sao model một mình không phải agent.
2. Đọc được một đoạn code gọi tool và biết chính xác dòng nào do model quyết định, dòng nào do bạn quyết định.
3. Tự viết một agent ~100 dòng có loop, tool, memory, trace — bản nháp của agent sẽ hoàn thiện trong 9 buổi còn lại.
4. Biết khi nào **không** nên dùng agent.

---

## 1. Chuẩn bị (5 phút)

```bash
cd session-01
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # mở .env, dán OPENAI_API_KEY
python 01_hello_llm.py
```

Không có key vẫn học được: thêm `FAKE=1` trước mỗi lệnh.

```bash
FAKE=1 python 04_tool_calling.py
```

Chế độ `FAKE=1` dùng một model giả lập để bạn thấy **luồng chạy**. Nó không thông minh, nên đừng dùng nó để đánh giá chất lượng câu trả lời.

---

## 2. Model chỉ là một hàm (15 phút)

### Cách nghĩ đúng

Một model ngôn ngữ là một hàm:

```
văn bản vào  ──►  model  ──►  văn bản ra
```

Hết. Nó không có bộ nhớ, không có tay chân, không truy cập được file, không biết hôm nay là thứ mấy.

Ví dụ dễ hình dung: một chuyên gia rất giỏi nhưng bị nhốt trong phòng kín, không có điện thoại, không có máy tính, chỉ có một khe giấy để nhận câu hỏi và trả lời. Muốn anh ta làm được việc thật, bạn phải **xây hệ thống giấy tờ, ống nói, cửa ra vào** quanh anh ta. Hệ thống đó gọi là **harness**.

Chạy `01_hello_llm.py`:

```python
messages = [{"role": "user", "content": "Giải thích trong đúng 2 câu: AI agent là gì?"}]
response = chat(messages)
print(text(response))
```

Điều đáng chú ý: chương trình của bạn **không hề có trạng thái**. Biến duy nhất là `messages`.

### Không có trí nhớ

Chạy `02_stateless.py`. Cùng một câu hỏi "Mình tên gì?", hai kết quả khác nhau:

| Cách gửi | Model thấy gì | Kết quả |
|---|---|---|
| Chỉ câu hỏi | `["Mình tên gì?"]` | Không biết |
| Kèm lịch sử | `["Mình tên Minh", "Chào Minh", "Mình tên gì?"]` | "Minh" |

**Không có trí nhớ nào cả.** Chỉ là bạn gửi lại đoạn hội thoại dài hơn. Cái mà sản phẩm gọi là "memory" chính là một danh sách messages được lưu và gửi lại mỗi lần. Đây là ý quan trọng nhất của cả khóa: **context là thứ bạn chủ động xây, không phải model tự có.**

> **Một câu chốt:** model không nhớ, harness nhớ hộ.

---

## 3. Suy nghĩ là một khoản ngân sách (10 phút)

Có hai loại model:

- **Model thường** (`gpt-4o-mini`): trả lời ngay, nhanh, rẻ.
- **Model reasoning** (`gpt-5`, `o`-series...): dành thêm thời gian "nghĩ" trước khi trả lời, đúng hơn với bài toán nhiều bước, đắt hơn và chậm hơn.

Chạy `03_reasoning.py` với câu đố con ốc sên (đáp án đúng: **8 ngày**, không phải 10). Script chạy ba cách:

| Cách | Việc bạn làm | Kết quả thường thấy |
|---|---|---|
| A | "Chỉ trả lời đáp án" | Nhanh nhưng dễ ra 10 |
| B | Thêm "hãy suy nghĩ từng bước" | Đúng hơn, tốn thêm chút token |
| C | Đổi sang model reasoning | Đúng nhất, tốn nhất |

Bài học không phải "luôn dùng model xịn". Bài học là:

> **Mỗi lần bật suy nghĩ là một lần trả tiền và chờ.** Việc dễ thì trả lời thẳng.

Quy tắc thực dụng:

- Phân loại, trích xuất, viết lại câu → model thường.
- Tính toán nhiều bước, lập kế hoạch, debug logic → model reasoning.
- Việc lặp đi lặp lại mỗi ngày → model thường, đo lại chất lượng định kỳ.

Câu B cũng cho thấy một điều sẽ học ở buổi 4: **cùng một model, chỉ thay cách viết prompt mà kết quả đổi**. Đó là context engineering.

---

## 4. Tool calling — model xin phép, bạn mới là người chạy (20 phút)

Đây là phần quan trọng nhất buổi hôm nay. Chạy `04_tool_calling.py` rồi đọc kỹ output.

### Chuyện gì thật sự xảy ra

```
Bạn: "Thời tiết Hà Nội thế nào?"
 │
 ├─► Lần gọi 1: bạn gửi câu hỏi + DANH SÁCH TOOL
 │      model trả về: content = None
 │                    tool_calls = [get_weather(city="Hà Nội")]
 │      ▲ model KHÔNG trả lời, cũng KHÔNG chạy gì. Nó chỉ nói nó muốn gì.
 │
 ├─► Bạn: json.loads(...)  →  get_weather("Hà Nội")  →  "28°C, nhiều mây"
 │      ▲ đây là code Python của bạn chạy, trên máy bạn
 │
 └─► Lần gọi 2: bạn gửi lại câu hỏi + yêu cầu gọi tool + kết quả
        model trả về: "Hà Nội hôm nay 28°C, nhiều mây."
```

Ba dòng cuối file là toàn bộ bí mật của tool calling:

```python
messages.append(message)                                              # model xin gọi
messages.append({"role": "tool", "tool_call_id": call.id, "content": ket_qua})  # bạn chạy
second = chat(messages, tools=TOOLS)                                  # model viết câu trả lời
```

### Ba hiểu nhầm hay gặp

| Hiểu nhầm | Sự thật |
|---|---|
| "Model tự chạy code của tôi" | Không. Nó chỉ sinh ra JSON mô tả hàm muốn gọi. |
| "Model biết kết quả tool là đúng" | Không. Nó tin bạn. Tool trả sai thì agent sai. |
| "Có tool là agent tự biết dùng" | Chỉ khi `description` của tool đủ rõ và tham số đủ dễ điền. |

Chính vì điểm thứ ba, **viết mô tả tool là một kỹ năng** — đó là nội dung buổi 3.

> **Một câu chốt:** model là bộ não nghĩ ra hành động; harness là đôi tay thực sự làm.

---

## 5. Workflow hay agent? Chọn mức thấp nhất đủ dùng (15 phút)

Chạy `05_workflow_vs_agent.py`. Cùng một câu hỏi khách hàng, hai cách viết:

**Workflow** — bạn biết trước cần gì, viết thẳng ra:

```python
don = get_order_status("1234")            # luôn chạy
chinh_sach = check_return_policy("tai nghe")  # luôn chạy
tra_loi = chat([...])                     # model chỉ viết câu trả lời
```

**Agent** — bạn đưa mục tiêu + tool, model tự chọn:

```python
for _ in range(max_buoc):
    response = chat(messages, tools=TOOLS)
    if not response.choices[0].message.tool_calls:
        return text(response)             # model thấy đủ thì dừng
    # ... chạy tool, nối kết quả vào messages, lặp lại
```

### Thang 5 mức, từ chắc chắn đến linh hoạt

| Mức | Tên | Ví dụ | Ai quyết định |
|---|---|---|---|
| 1 | Prompt đơn | Viết lại email | Không ai cả |
| 2 | Chain | Dịch → tóm tắt → kiểm tra | Bạn (thứ tự cố định) |
| 3 | Routing | Câu hỏi về hoá đơn → nhánh hoá đơn | Model chọn nhánh, bạn vẽ nhánh |
| 4 | Orchestrator | Chia việc cho nhiều nhánh chạy song song | Model chọn việc, bạn kiểm soát |
| 5 | Agent | Tự lập kế hoạch, tự gọi tool, tự sửa | Model |

Nguyên tắc chọn:

- Đoán được mọi tình huống → mức 2. Rẻ, dễ test, chạy ổn định.
- Có vài loại yêu cầu rõ ràng → mức 3.
- Không đoán được thứ tự bước → mức 5, và chấp nhận phải đầu tư vào eval (buổi 7).

> **Một câu chốt:** agent là công cụ đắt và khó đoán. Đừng dùng nó khi một `if` là đủ.

---

## 6. Agent = Model + Harness (20 phút)

Chạy `06_mini_harness.py`. Đây là **agent thật đầu tiên** của bạn, và cũng là bộ xương của agent cuối khóa.

```
┌─────────────────────────── HARNESS ───────────────────────────┐
│                                                               │
│   system prompt ──┐                                           │
│   history ────────┼──► [ MODEL ] ──► muốn gọi tool? ──► không ──► trả lời
│   câu hỏi ────────┘         ▲                    │            │
│                             │                    │ có         │
│                        kết quả tool  ◄──── chạy tool          │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

Sáu phần, đúng sáu phần này sẽ được làm dày trong 9 buổi:

| # | Thành phần | Trong `06_mini_harness.py` | Buổi làm dày |
|---|---|---|---|
| 1 | Model | `chat()` | 1–2 |
| 2 | Tools | `common/shop.py` + `TOOLS` | 3 |
| 3 | Loop | `for step in range(1, MAX_STEPS+1)` | 2 |
| 4 | Context | `SYSTEM_PROMPT` + `messages` | 4 |
| 5 | Memory | `self.history` | 4 |
| 6 | Observability | `self.trace` + `traces/last_run.json` | 7 |

### Vòng lặp 4 bước

```
OBSERVE  →  nhận câu hỏi, nhận kết quả tool
THINK    →  model quyết định: trả lời hay gọi tool?
ACT      →  harness chạy tool
VERIFY   →  câu trả lời có dùng đúng dữ liệu không?
```

Trong file, `VERIFY` là hàm `_finish()`: nếu câu trả lời không có con số nào trong khi đã tra được dữ liệu, harness nhắc model sửa một lần. Đơn giản, nhưng đúng bản chất — **kiểm tra là việc của harness, không phải của model.**

### Vì sao ChatGPT, Claude Code, Cursor khác nhau?

Vì model có thể giống nhau, nhưng harness khác nhau:

| | ChatGPT | Claude Code | Cursor |
|---|---|---|---|
| Tools | web, python, ảnh, file | đọc/ghi file, chạy shell, git | đọc/sửa file, terminal, LSP |
| Context | hội thoại + memory | tự đọc file liên quan, nén lịch sử | file đang mở, index codebase |
| Nơi chạy | server của họ | máy bạn | máy bạn |
| Kiểm soát | ít | hỏi trước khi chạy lệnh nguy hiểm | hỏi trước khi sửa file |

Cùng một "bộ não", khác "cơ thể" thì hành vi khác hẳn. Đó là lý do khóa học này xây harness chứ không huấn luyện model.

> **Một câu chốt:** muốn agent giỏi hơn, hãy sửa harness trước khi đổi model.

---

## 7. Lab (60 phút)

### Phần A — Chạy hết 6 bài (20 phút)

Chạy lần lượt, với mỗi file trả lời được hai câu:

1. Dòng nào **model** quyết định?
2. Dòng nào **tôi** quyết định?

| File | Câu hỏi cần trả lời được |
|---|---|
| `01_hello_llm.py` | Vì sao nói model là hàm thuần? |
| `02_stateless.py` | "Memory" nằm ở đâu trong code? |
| `03_reasoning.py` | Khi nào **không** nên bật suy nghĩ? |
| `04_tool_calling.py` | Nếu bỏ `messages.append(message)` thì sao? |
| `05_workflow_vs_agent.py` | Đổi câu hỏi thành "đơn 9999" thì cách nào phải sửa code? |
| `06_mini_harness.py` | Mở `traces/last_run.json`, đọc lại từng bước |

### Phần B — Quan sát một harness có sẵn (20 phút)

Dùng Claude Code, ChatGPT, Cursor hoặc bất kỳ agent nào bạn có. Giao một việc nhỏ ("tìm file lớn nhất trong thư mục này", "tóm tắt repo này"). Điền `worksheet.md`.

Mục đích: thấy bằng mắt rằng agent thật cũng chỉ chạy đúng vòng lặp bạn vừa viết, chỉ có nhiều tool và context phong phú hơn.

### Phần C — Sửa harness (20 phút)

Chọn ít nhất 2 bài trong `exercises.md`, làm ngay tại lớp.

---

## 8. Bài tập về nhà

Xem `exercises.md`. Tối thiểu làm bài 1 và bài 4 trước buổi 2.

---

## 9. Tổng kết — 5 câu mang về

1. Model là hàm văn bản → văn bản. Không nhớ, không làm.
2. "Memory" là messages được gửi lại. Context là thứ bạn thiết kế.
3. Tool calling = model xin gọi, harness chạy thật. Model không có quyền gì trên máy bạn.
4. Chọn mức đơn giản nhất đủ dùng: workflow trước, agent sau.
5. Muốn agent tốt hơn: sửa harness (tool, context, verify), không chỉ đổi model.

---

## 10. Chuẩn bị buổi 2

- Cài `langgraph` và `langchain-openai` (sẽ có `requirements.txt` riêng).
- Đọc lại `06_mini_harness.py` cho đến khi giải thích được vòng `for` mà không cần mở file.
- Buổi 2: thay vòng `for` tự viết bằng LangGraph, thêm checkpoint, streaming và human-in-the-loop.

---

## Phụ lục — Cấu trúc thư mục

```
session-01/
├── README.md              ← tài liệu này
├── slides/
│   ├── slides.pptx        ← slide buổi giảng
│   └── build_slides.py    ← script tạo slide
├── 01_hello_llm.py
├── 02_stateless.py
├── 03_reasoning.py
├── 04_tool_calling.py
├── 05_workflow_vs_agent.py
├── 06_mini_harness.py
├── common/
│   ├── llm.py             ← nơi duy nhất gọi model
│   └── shop.py            ← dữ liệu + tool giả lập
├── worksheet.md           ← phiếu quan sát agent có sẵn
├── exercises.md           ← bài tập
├── requirements.txt
└── .env.example
```
