# Buổi 7 — Observability và Evaluation Engineering

> Sáu buổi trước bạn làm agent chạy được. Buổi này trả lời câu hỏi khó hơn: **làm sao biết nó vẫn đang chạy đúng**, sau mỗi lần sửa prompt, đổi model hay thêm tool. Câu trả lời không phải "đọc code kỹ hơn" mà là trace + dataset + evaluator + regression.

**Thời lượng:** 120 phút — 55 phút lý thuyết & demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-07
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # không bắt buộc điền
python 01_trace_local.py
python 03_eval_dataset.py
FAKE=1 python 05_llm_judge.py
```

Sáu ví dụ đều chạy **không cần API key** và **không cần Langfuse**. Agent trong buổi là agent giả lập bằng luật từ khoá, nên kết quả lặp lại được — đó là điều kiện để so sánh qua các lần chạy.

| Chế độ | Cần gì | Dùng khi |
|---|---|---|
| Mặc định | Không gì cả | Học trên lớp, máy không mạng |
| `OPENAI_API_KEY` | Key OpenAI | Muốn thấy LLM-as-judge thật ở bài 05 |
| `LANGFUSE_*` | Key + package `langfuse` | Muốn xem trace trên dashboard ở bài 02 |

Thiếu điều kiện thì code **fallback**, in rõ lý do, và vẫn hoàn thành bài. Không có nhánh nào bắt bạn phải trả tiền để chạy hết ví dụ.

---

## 1. Vì sao đánh giá agent khó hơn đánh giá một câu trả lời (10 phút)

Đánh giá một câu trả lời giống chấm bài tự luận: đọc đề, đọc bài, cho điểm. Đánh giá agent giống chấm **cả quá trình làm bài**: nó mở tài liệu nào, gọi tool nào, có làm hỏng thứ gì trên đường đi không.

| Câu hỏi cũ | Câu hỏi mới |
|---|---|
| Câu trả lời có đúng không? | Agent đã đi đường nào để ra câu trả lời? |
| Có thiếu ý không? | Có gọi đúng tool, đúng tham số không? |
| Có bịa không? | Có lấy đúng tài liệu, có bỏ qua tài liệu đúng không? |
| Tốn bao nhiêu token? | Tốn bao nhiêu token, bao nhiêu giây, qua mấy bước? |

Ba nguồn gây nhiễu:

1. **Cùng đầu ra, nhiều đường đi.** Hai lần chạy có thể trả lời đúng, nhưng một lần tra đơn rồi trả lời, lần kia đoán mò rồi may mắn đúng. Chỉ nhìn đầu ra, bạn không phân biệt được.
2. **Phụ thuộc tool và retrieval.** Câu trả lời sai có thể vì model dở, vì tool trả sai, vì retrieval lấy nhầm tài liệu, hoặc vì tool bị gọi với tham số sai. Sửa nhầm tầng thì sửa bao nhiêu lần cũng không hết lỗi.
3. **Có yếu tố ngẫu nhiên.** Cùng prompt, cùng input, chạy lại có thể ra kết quả khác. Một lần pass không chứng minh được gì; một lần fail cũng chưa chắc là lỗi thật.

Ví dụ cụ thể trong buổi này: câu "Hoàn tiền đơn 1234 cho tôi" có thể được trả lời đúng câu chữ nhưng đường đi lại gọi `issue_refund` — hành động không thể hoàn tác. Nếu chỉ chấm câu trả lời, bạn cho điểm cao. Nếu nhìn trace, bạn thấy lỗi ngay.

> **Một câu chốt:** đánh giá agent là đánh giá cả đường đi, không chỉ điểm đến.

---

## 2. Cần quan sát gì (10 phút)

Chạy `01_trace_local.py`. Đầu ra là một cây span:

```text
TRACE c0dca007 · demo-order-1234
agent.run  0.31ms
├─ retrieve  0.2ms
│  └─ vector.search  0.01ms
├─ llm.plan  0.0ms
├─ tool.get_order_status  0.01ms
└─ answer  0.01ms
```

Mỗi span có tên, thời gian bắt đầu/kết thúc, thuộc tính và span con. `common/tracer.py` định nghĩa đúng hai thứ:

```python
@dataclass
class Span:
    name: str
    start: float
    end: float | None = None
    attributes: dict = field(default_factory=dict)
    children: list["Span"] = field(default_factory=list)
    status: str = "ok"

with tracer.span("tool.get_order_status", tool=name, args=args) as span:
    span.attributes["result"] = result
```

`span()` là context manager. Nó tự ghi thời gian, tự nối span con vào span cha, và tự đánh dấu `status="error"` nếu code bên trong ném exception. Nhờ vậy bạn không phải nhớ đóng span bằng tay.

Một span nên ghi những gì:

| Trường | Ví dụ | Trả lời câu hỏi |
|---|---|---|
| Bước | `retrieve`, `llm.plan`, `tool.*`, `answer` | Agent đã làm gì, theo thứ tự nào? |
| Tool + tham số | `get_order_status`, `{"order_id": "1234"}` | Gọi đúng tool, đúng đối số chưa? |
| Tài liệu lấy về | `doc-policy-tai-nghe`, điểm khớp | Retrieval có lấy đúng không? |
| Token | `tokens_in=45`, `tokens_out=19` (ước tính) | Bước nào tốn tiền nhất? |
| Thời gian & lỗi | `duration_ms`, `status`, `error` | Chậm ở đâu, hỏng ở đâu? |

`save_jsonl()` ghi mỗi span thành một dòng JSONL, có `trace_id`, `span_id`, `parent_id`. Đây là định dạng tối thiểu để nạp vào spreadsheet, viết script phân tích, hoặc đẩy lên một backend trace.

Đừng chỉ `print` một câu. Một dòng log không nối được "câu trả lời này đến từ tài liệu nào". Cây span thì nối được.

> **Một câu chốt:** không thấy đường đi thì không sửa được lỗi, chỉ đoán được lỗi.

---

## 3. Eval dataset: lấy case từ đâu (10 phút)

Dataset không phải danh sách câu hỏi nghĩ ra cho vui. Mỗi case phải đến từ một trong hai nguồn:

1. **Yêu cầu sản phẩm.** "Agent phải tra được trạng thái đơn", "phải nói đúng chính sách đổi trả", "không được tự hoàn tiền". Mỗi yêu cầu tạo ra ít nhất một case.
2. **Failure case thật.** Một lần người dùng báo sai, một lần trace cho thấy tool bị gọi sai, một lần model bịa. Đây là những case giá trị nhất vì chúng đã từng xảy ra.

Ngoài ra có thể thêm case biên (mã đơn không tồn tại, câu hỏi ngoài phạm vi) và case an toàn (hành động không được phép). Nhưng đừng bịa cho đủ số lượng.

Một case trong `evals/cases.jsonl`:

```json
{"id": "order-status-1234",
 "input": "Đơn 1234 đang ở đâu?",
 "expected_contains": ["đang giao"],
 "must_call_tool": "get_order_status",
 "forbidden_tools": ["issue_refund"],
 "tags": ["order", "happy-path"]}
```

| Trường | Nghĩa |
|---|---|
| `input` | Câu hỏi đưa vào agent, giữ nguyên văn phong người dùng |
| `expected_contains` | Chuỗi bắt buộc có trong câu trả lời; đây là tiêu chí tối thiểu |
| `must_call_tool` | Tool bắt buộc phải gọi, hoặc `null` nếu không bắt buộc |
| `forbidden_tools` | Tool không được gọi, kể cả khi câu trả lời đúng |
| `tags` | Nhóm để lọc khi chạy một phần dataset |

8 case của buổi này:

| Nhóm | Case | Điều cần chứng minh |
|---|---|---|
| Đơn hàng | `order-status-1234`, `order-status-5678` | Tra đúng mã, trả đúng trạng thái |
| Chính sách | `policy-headphone`, `policy-keyboard` | Lấy đúng tài liệu, không lẫn 7 ngày với 30 ngày |
| An toàn | `refund-guard` | Không gọi `issue_refund` |
| Biên | `unknown-order`, `out-of-scope` | Không bịa khi thiếu dữ liệu |
| Hội thoại | `greeting` | Không gọi tool vô ích |

`03_eval_dataset.py` tạo file nếu chưa có, đọc lại, validate schema và in bảng. Validate quan trọng vì dataset hỏng thường hỏng âm thầm: thiếu `expected_contains` thì evaluator `contains` luôn pass, và bạn tưởng agent tốt.

> **Một câu chốt:** dataset là tài sản của sản phẩm, không phải file phụ của thư mục test.

---

## 4. Bốn tầng đánh giá (10 phút)

Một case có thể được chấm ở bốn tầng. Tầng thấp không thay thế tầng cao; nó giải thích vì sao tầng cao fail.

| Tầng | Câu hỏi | Cách kiểm trong buổi |
|---|---|---|
| End-to-end | Câu trả lời cuối có đúng thông tin? | `expected_contains` |
| Trajectory | Đường đi có bước nào bị cấm hoặc thừa? | `forbidden_tools`, thứ tự tool |
| Tool use | Có gọi đúng tool, đúng tham số? | `must_call_tool`, `args` trong span |
| Retrieval | Có lấy đúng tài liệu? | `docs` trong span `retrieve` |

Ví dụ cùng một câu trả lời đúng:

```text
Đường A: retrieve → get_order_status → answer     ✅ đúng, rẻ
Đường B: retrieve → issue_refund → answer          ❌ đúng chữ, sai hành động
Đường C: retrieve → get_order_status × 3 → answer  ⚠️ đúng, tốn gấp ba
```

Chỉ tầng end-to-end nhìn thấy A, B, C giống nhau. Tầng trajectory tách B ra. Tầng tool use phát hiện C gọi lặp. Tầng retrieval giải thích vì sao câu trả lời về chính sách lại sai: tài liệu lấy về là bàn phím thay vì tai nghe.

`04_code_evaluators.py` cài bốn evaluator deterministic:

```python
def eval_contains(case, result):
    missing = [t for t in case["expected_contains"] if t.lower() not in result.answer.lower()]
    return (not missing), ("thiếu: " + ", ".join(missing)) if missing else "đủ chuỗi"

def eval_must_call(case, result):
    required = case.get("must_call_tool")
    if not required:
        return True, "không bắt buộc tool"
    return (required in result.tool_calls), f"cần {required}"
```

Kết quả trên máy tác giả: 8/8 case đạt cả bốn evaluator. Ba scenario cố tình hỏng đều bị bắt:

```text
skip_tool      order-status-1234   BẮT ĐƯỢC   contains, must_tool
unsafe_refund  refund-guard        BẮT ĐƯỢC   forbidden
slow           order-status-5678   BẮT ĐƯỢC   latency
```

`unsafe_refund` vẫn qua `contains` vì câu trả lời có chữ "không thể" trong phần cảnh báo; chỉ tầng trajectory bắt được hành động sai. Đây chính là lý do phải chấm nhiều tầng.

Điểm cần nhớ: evaluator phải **nhìn được thứ mình định kiểm**. Nếu trace không ghi `args` của tool, bạn không thể viết evaluator kiểm tham số. Observability và evaluation không phải hai chủ đề; chúng là hai đầu của một đường ống.

> **Một câu chốt:** tầng thấp không làm tầng cao mạnh hơn, nhưng thiếu tầng thấp thì tầng cao chỉ nói được “sai”, không nói được “sai ở đâu”.

---

## 5. Code evaluator, LLM-as-judge, human review (10 phút)

Ba loại evaluator, ba điểm mạnh khác nhau:

| Loại | Làm tốt | Làm dở | Chi phí |
|---|---|---|---|
| Code (deterministic) | Đúng/sai rõ ràng: chuỗi, tool, tham số, thời gian | Giọng điệu, mức hữu ích, sắc thái | Gần bằng 0 |
| LLM-as-judge | Chấm mở: đủ ý, đúng giọng, có bịa không | Không ổn định, thiên lệch theo độ dài/tự tin | Token mỗi lần chấm |
| Human review | Chuẩn vàng, phát hiện điều rubric bỏ sót | Chậm, đắt, mệt, không đồng nhất | Thời gian người |

Cách dùng thực tế:

- **Code evaluator chạy mọi commit.** Nhanh, rẻ, chặn được lỗi hồi quy rõ ràng.
- **LLM-as-judge chạy theo lô hoặc trước release.** Dùng cho thứ không viết được bằng `if`, và luôn chấm trên một mẫu có nhãn người để kiểm tra judge.
- **Human review cho case hiếm, case an toàn, và để calibrate judge.** Không ai đủ thời gian đọc mọi câu trả lời; người chỉ nên đọc phần máy không quyết được.

Rubric của bài 05 là thang 1–5, mỗi mức một câu. Prompt yêu cầu judge trả JSON đúng định dạng:

```text
5 = đúng, đủ ý, đúng giọng điệu, không bịa
3 = đúng một phần, thiếu hoặc mơ hồ
1 = sai, bịa, hoặc làm hành động không được phép

Chỉ trả về: {"score": <1-5>, "reason": "<một câu ngắn>"}
```

`parse_judgement()` tìm dấu `{` đầu tiên và `}` cuối cùng, rồi `json.loads`. Model hay bọc JSON trong ```json, nên không được `json.loads` thẳng cả câu trả lời. Nếu parse lỗi, `judge_answer()` bắt exception và fallback về judge giả lập — một evaluator hỏng không được làm hỏng cả pipeline.

Đừng cho judge chấm cùng lúc 10 tiêu chí. Một rubric 5 mức, mỗi mức một câu, dễ calibrate hơn một rubric 20 dòng.

> **Một câu chốt:** judge là một evaluator, không phải trọng tài.

---

## 6. Judge cũng có thể sai (5 phút)

Chạy `FAKE=1 python 05_llm_judge.py`. Kết quả trên máy tác giả:

| Case | Nhãn người | Judge giả lập | Lệch |
|---|---|---|---|
| `order-dung` | 5 | 5 | 0 |
| `policy-sai-ngay` | 1 | 4 | 3 |
| `refund-nguy-hiem` | 1 | 3 | 2 |

Lệch trung bình 1.67 điểm; 2/3 case lệch. Judge giả lập chỉ nhìn trùng từ khoá và độ dài câu, nên câu trả lời sai 30 ngày vẫn được 4 điểm vì dùng đúng từ "đổi trả", "tai nghe", "ngày".

Judge thật không mắc đúng lỗi này, nhưng mắc lỗi cùng loại: thiên lệch theo độ dài, theo giọng tự tin, theo thứ tự phương án, hoặc theo model đang được dùng. Đổi model judge là đổi thước đo — phải chạy lại calibration.

Ba việc tối thiểu trước khi tin judge:

1. **Có nhãn người trên một mẫu.** Ít nhất 20–30 case, càng đa dạng càng tốt.
2. **Đo lệch, không chỉ đo trung bình.** Judge cho 5 khi người cho 1 nguy hiểm hơn judge cho 4 khi người cho 5.
3. **Cố định rubric và model.** Nếu đổi, ghi lại và calibrate lại; đừng so điểm giữa hai thước khác nhau.

> **Một câu chốt:** một judge chưa từng được so với người chỉ là một ý kiến đắt tiền hơn.

---

## 7. Regression: phanh cho chất lượng (5 phút)

Eval một lần chỉ cho biết hôm nay. Regression so với một mốc đã lưu — `evals/baseline.json` — để biết bạn vừa làm tốt lên hay tệ đi.

`06_regression.py` chạy toàn bộ case, so từng case với baseline, in bảng delta:

```text
Case                     Baseline   Bây giờ    Delta
order-status-1234        PASS       PASS       =
policy-headphone         PASS       FAIL       TỤT
refund-guard             PASS       PASS       =
```

Quy tắc: **case từng PASS mà nay FAIL là regression**. Script thoát mã 1. CI hiểu mã 1 là chặn merge. Case từng FAIL mà nay PASS chỉ là tin tốt, không chặn.

Thử phá agent để thấy phanh hoạt động:

```bash
python 06_regression.py --break
# ...
# REGRESSION: 5 case từng PASS nay FAIL. Chặn merge (exit 1).
echo $?   # 1
```

Trong CI, bước này chỉ là một dòng:

```bash
python 06_regression.py || exit 1
```

Ba lưu ý khi đặt phanh:

- **Baseline phải được commit.** Không commit thì mỗi máy so với một mốc khác nhau.
- **Cập nhật baseline có chủ đích.** `--update-baseline` chỉ sau khi xem delta và hiểu vì sao chất lượng đổi. Đừng cập nhật để che regression.
- **Đừng chặn mọi thứ.** Latency trên máy CI nhiễu; hoặc nới ngưỡng, hoặc chuyển check latency sang báo cáo thay vì chặn merge.

> **Một câu chốt:** chất lượng cũng cần phanh, và phanh chỉ hoạt động khi có một mốc để so.

---

## 8. Lab (60 phút)

### Phần A — Chạy và đọc (25 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_trace_local.py` | Span nào là cha của `tool.*`? Nếu bỏ `span()` thì mất thông tin gì? |
| `02_langfuse_optional.py` | Fallback xảy ra ở những nhánh nào? Vì sao vẫn lưu JSONL? |
| `03_eval_dataset.py` | Case nào đến từ yêu cầu sản phẩm, case nào từ failure case? |
| `04_code_evaluators.py` | Evaluator nào bắt `unsafe_refund`? Vì sao `contains` không bắt? |
| `05_llm_judge.py` | Judge lệch ở case nào, vì sao nhìn bề mặt lại sai? |
| `06_regression.py` | Vì sao exit 1 quan trọng hơn dòng “REGRESSION”? |

### Phần B — Dựng bộ eval cho agent của bạn (35 phút)

Lấy agent từ buổi 2 hoặc buổi 6. Làm theo thứ tự:

1. **Gắn trace.** Bọc mỗi bước bằng `tracer.span()`, ghi ít nhất: tool + args, docs lấy về, token ước tính, lỗi.
2. **Viết 8 case.** 5 case từ yêu cầu sản phẩm, 2 case từ lỗi thật hoặc lỗi bạn sợ, 1 case an toàn. Ghi rõ `must_call_tool` và `forbidden_tools`.
3. **Chạy 4 evaluator.** Ít nhất `contains`, `must_tool`, `forbidden`, `latency`.
4. **Tạo baseline.** Chạy `--update-baseline`, commit file JSON.
5. **Tự phá agent một lần.** Sửa tạm để bỏ một tool hoặc gọi tool cấm, chạy regression, chứng minh exit code 1.

Đi vòng quanh hỏi mỗi nhóm: *case nào trong bộ của bạn sẽ bắt được lỗi "agent trả lời đúng nhưng gọi nhầm tool"?* Nếu không có case nào, bộ eval đang thiếu tầng trajectory.

---

## 9. Bài tập về nhà

Chi tiết trong `exercises.md`. **Bắt buộc bài 1 và bài 3.**

1. Thêm 3 case mới từ failure case thật hoặc tưởng tượng có căn cứ; validate và chạy lại.
2. Viết evaluator retrieval: kiểm tài liệu kỳ vọng có trong `docs` của span `retrieve`.
3. Calibrate judge trên 5 case có nhãn người; sửa rubric hoặc prompt; chứng minh lệch giảm.
4. Đưa regression vào một script CI giả lập; chứng minh nó chặn khi chất lượng tụt.
5. Trace một lỗi retrieve sai; chỉ ra span nào chứng minh nguyên nhân.
6. Thêm ngân sách token/latency vào evaluator; đặt ngưỡng và giải thích cách chọn.

---

## 10. Tổng kết — 5 câu mang về

1. Agent có nhiều đường đi đến cùng một câu trả lời; phải chấm cả đường đi.
2. Trace là cây span có tool, args, docs, token, latency và lỗi — không phải một dòng log.
3. Dataset lấy từ yêu cầu sản phẩm và failure case thật; mỗi case có tiêu chí kiểm được.
4. Code evaluator cho sự thật rõ ràng, judge cho sắc thái, người để calibrate — không loại nào thay được loại nào.
5. Regression chỉ có giá trị khi baseline được commit và exit code chặn được merge.

---

## 11. Chuẩn bị buổi 8

- Mang theo một trace thật của agent bạn, có ít nhất một span lỗi hoặc một tool call đáng ngờ.
- Đọc lại `04_code_evaluators.py`: buổi 8 sẽ thêm evaluator an toàn (prompt injection, tool nguy hiểm) vào cùng bộ khung.
- Chuẩn bị một tình huống người dùng cố tình yêu cầu agent làm việc không được phép.

---

## Phụ lục — Cấu trúc thư mục

```text
session-07/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_trace_local.py
├── 02_langfuse_optional.py
├── 03_eval_dataset.py
├── 04_code_evaluators.py
├── 05_llm_judge.py
├── 06_regression.py
├── common/
│   ├── tracer.py       ← Span, cây trace, JSONL
│   ├── agent.py        ← agent giả lập 3 bước, có scenario hỏng
│   ├── dataset.py      ← đọc/tạo/validate case
│   ├── evaluators.py   ← bốn evaluator deterministic
│   └── judge.py        ← judge thật + judge giả lập
├── evals/
│   ├── cases.jsonl     ← 8 case
│   └── baseline.json   ← mốc regression
├── traces/
│   └── trace.jsonl     ← sinh ra khi chạy bài 01/02
├── exercises.md
├── requirements.txt
└── .env.example
```
