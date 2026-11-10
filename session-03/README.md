# Buổi 3 — Tool and MCP Engineering

> Buổi 1 và 2 cho bạn một vòng lặp chạy được. Nhưng agent chỉ giỏi bằng những gì nó **làm được**: tool là đôi tay của agent. Buổi này dạy viết đôi tay đó sao cho model chọn đúng, gọi đúng, và không phá dữ liệu — rồi đóng gói nó thành MCP server để nhiều agent dùng chung.

**Thời lượng:** 120 phút — 55 phút lý thuyết & demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-03
python 01_tool_contract.py
python 02_tool_errors.py
python 03_sql_readonly.py
python 04_sandbox.py
python 05_mcp_server.py
python 06_mcp_client.py
```

Không ví dụ nào gọi API thật, nên **không cần API key**. Vì vậy `FAKE=1` cũng không cần thiết — nếu bạn quen tay cứ đặt, code bỏ qua biến đó. Model giả trong `common/fake_model.py` nói đúng giao thức tool call ở mức dict, đủ để thấy harness chạy tool và nhận kết quả.

Muốn chạy phần MCP:

```bash
pip install -r requirements.txt      # trong đó có mcp>=1.2,<2
python 05_mcp_server.py --serve      # server nói chuyện qua stdio
python 06_mcp_client.py              # client tự khởi chạy server
```

Ghim `mcp<2` vì MCP 2.x đổi tên `FastMCP` thành `MCPServer` và đổi API; bài giảng viết theo API 1.x ổn định.

Chưa cài `mcp` thì hai file 05/06 in hướng dẫn rồi thoát, **không traceback**. Bốn file đầu vẫn chạy bình thường.

> **Một câu chốt:** buổi này không cần dịch vụ ngoài nào; mọi thứ chạy trên máy bạn.

---

## 1. Nhắc lại tool calling (5 phút)

Ở buổi 1, một lượt gọi tool có bốn bước:

| Bước | Ai làm | Dữ liệu |
|---|---|---|
| 1. Think | Model | Trả về `tool_calls: [{name, args}]` |
| 2. Act | **Harness** | Tra bảng tên → gọi hàm Python thật |
| 3. Observe | Harness | Đóng kết quả thành message `role="tool"` |
| 4. Think lại | Model | Đọc kết quả, quyết định trả lời hay gọi tiếp |

Điểm hay bị hiểu sai: **model không chạy tool**. Nó chỉ phát ra một đề nghị dạng JSON. Harness là bên kiểm tra tên, kiểm tra quyền, chạy hàm, bắt lỗi, và quyết định đưa gì ngược lại cho model.

Vì vậy mọi thứ bạn muốn chặn — quyền, timeout, SQL nguy hiểm — đều phải nằm ở harness hoặc ở tool. Không thể nằm trong prompt, vì prompt có thể bị thuyết phục.

> **Một câu chốt:** model chỉ xin gọi; quyền quyết định cuối cùng luôn thuộc về code của bạn.

---

## 2. Tool là một API contract (10 phút)

Chạy `01_tool_contract.py`. File in ra đúng khối JSON mà model nhận — không phải code Python.

Một tool có năm phần:

| Phần | Ví dụ tốt | Vì sao quan trọng |
|---|---|---|
| **Tên** | `search_orders` | Động từ + đối tượng; model phân biệt tool bằng tên |
| **Mô tả** | "Tìm đơn của một khách… Không dùng để hoàn tiền." | Nói cả khi nào dùng và khi nào **không** |
| **Tham số** | `customer_id` bắt buộc, `limit` có default | Ít tham số → ít chỗ đoán sai |
| **Kiểu trả về** | Chuỗi nhiều dòng, có ví dụ | Model biết kết quả trông thế nào |
| **Lỗi** | `"LỖI: không tìm thấy đơn 1234."` | Model đọc được và nói lại với người dùng |

```python
GOOD_TOOL = {
    "name": "search_orders",
    "description": "Tìm đơn của một khách... Không dùng để hoàn tiền.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "Mã khách, vd C-1042"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
        },
        "required": ["customer_id"],
    },
}
```

Cuối file chứng minh một điều khó chịu: hai hàm khác nhau, một đúng một sai, nhưng **cùng schema**. Model không đọc code nên không thể biết hàm nào hỏng. Schema chỉ là hợp đồng; test mới là thứ kiểm tra hợp đồng có được giữ.

> **Một câu chốt:** nếu model chọn sai tool, lỗi thường nằm ở mô tả — không nằm ở model.

---

## 3. Checklist thiết kế tool (12 phút)

Sáu điều, theo thứ tự hay vi phạm:

1. **Động từ rõ.** `get_order_status` tốt hơn `order`, `handle`, `do_stuff`. Tên là thứ model thấy đầu tiên.
2. **Tham số tối thiểu.** Mỗi tham số là một cơ hội để model điền sai. Cái gì suy ra được từ dữ liệu thì đừng bắt model truyền.
3. **Một việc một tool.** `get_order_and_refund` là hai hành động có hai mức rủi ro khác nhau; gộp lại là mất quyền kiểm soát.
4. **Trả về chuỗi dễ đọc.** Model đọc văn bản, không đọc object Python. `"Đơn 1234: đang giao, mai 15:00"` tốt hơn `{"o": {"st": 1}}`.
5. **Lỗi là dữ liệu, không phải exception.** Tool trả `"LỖI: ..."` để model xử lý. Exception chỉ dành cho lập trình viên và log.
6. **Idempotent khi có thể.** Gọi lại `get_order_status` không đổi gì. Gọi lại `issue_refund` thì đã trừ tiền hai lần — nếu buộc phải có, cần khoá idempotency.

| Dấu hiệu tool tệ | Sửa thành |
|---|---|
| `data: str` | Tách thành tham số có tên và kiểu |
| Mô tả "Xử lý dữ liệu" | Nói rõ đầu vào, đầu ra, khi nào dùng |
| Trả về `None` khi lỗi | Trả chuỗi `"LỖI: ..."` có lý do |
| Một tool làm 3 việc | Ba tool, ba mức quyền |

> **Một câu chốt:** tool tốt là tool mà một người mới đọc mô tả cũng gọi đúng — model cũng vậy.

---

## 4. Khi tool lỗi: timeout, retry, lỗi là dữ liệu (12 phút)

Chạy `02_tool_errors.py`. Hai kịch bản:

- **A.** Tool hỏng hai lần đầu, lần thứ ba trả dữ liệu → retry cứu được.
- **B.** Tool treo vĩnh viễn → timeout sau 1 giây, trả `"LỖI: ..."`, agent vẫn trả lời tử tế.

```python
def call_with_timeout(fn, args, timeout=1.0):
    box = queue.Queue()
    threading.Thread(target=lambda: box.put(fn(**args)), daemon=True).start()
    try:
        return box.get(timeout=timeout)
    except queue.Empty:
        return f"LỖI: tool không trả lời sau {timeout:g}s (timeout)."
```

Retry có kỷ luật:

| Tình huống | Có retry? | Vì sao |
|---|---|---|
| Timeout mạng, 503 | Có, 2–3 lần, backoff tăng dần | Lỗi tạm thời |
| 400, sai tham số | Không | Gọi lại vẫn sai |
| "Không tìm thấy đơn" | Không | Đây là kết quả nghiệp vụ, không phải lỗi |
| Hoàn tiền, gửi mail | Chỉ khi idempotent | Retry mù có thể trừ tiền hai lần |

Ba con số phải có: **số lần thử tối đa**, **thời gian chờ mỗi lần**, **tổng thời gian được phép**. Thiếu con số thứ ba, ba lần chờ 10 giây vẫn là 30 giây người dùng ngồi nhìn.

Lưu ý kỹ thuật: thread timeout chỉ bỏ được phía gọi, thread vẫn chạy. Muốn kill thật thì phải dùng subprocess — bài 04.

> **Một câu chốt:** tool lỗi không phải agent lỗi — trừ khi harness để lỗi đó thành exception.

---

## 5. Tool nguy hiểm: least privilege và SQL read-only (10 phút)

Bốn nguyên tắc, áp dụng cho mọi tool có thể đổi trạng thái:

| Nguyên tắc | Cách làm | Ví dụ |
|---|---|---|
| **Least privilege** | Tool chỉ có quyền tối thiểu | User database chỉ `SELECT` |
| **Allowlist** | Liệt kê việc được làm, không liệt kê việc bị cấm | Chỉ 3 bảng được truy vấn |
| **Giới hạn** | Timeout, trần số dòng, trần số tiền | `LIMIT 20`, hoàn tối đa 2 triệu |
| **Audit** | Ghi ai gọi gì, khi nào, kết quả | Log ra file riêng, không ghi vào prompt |

Chạy `03_sql_readonly.py`. Tool `run_select` có năm lớp:

1. Chặn dấu `;` → không có multi-statement.
2. Chặn từ khoá `INSERT/UPDATE/DELETE/DROP/ALTER/...`.
3. Chỉ cho câu bắt đầu bằng `SELECT` hoặc `WITH`.
4. Thiếu `LIMIT` thì bọc lại và thêm `LIMIT 20`.
5. Đếm opcode, ngắt câu chạy quá 0,5 giây.

Kết quả demo:

| Câu | Kết quả |
|---|---|
| `SELECT ... ORDER BY amount DESC` | Chạy, tự thêm `LIMIT 20` |
| `SELECT ...; DROP TABLE orders` | Chặn vì có `;` |
| `DELETE FROM orders` | Chặn vì từ khoá `DELETE` |
| `DROP TABLE orders` | Chặn vì từ khoá `DROP` |

Cuối file kiểm tra bảng vẫn còn 6 dòng. Đây là điểm quan trọng: **kiểm tra bằng dữ liệu thật**, không tin vào thông báo "đã chặn".

Nhưng lớp quan trọng nhất không nằm trong code Python: hãy cấp cho tool một user database chỉ có quyền `SELECT`. Khi đó dù câu SQL có lọt qua, database vẫn từ chối.

> **Một câu chốt:** đừng hỏi "prompt đã đủ an toàn chưa"; hãy hỏi "nếu prompt bị qua mặt, còn lớp nào chặn?".

---

## 6. Sandbox: chạy code lạ (8 phút)

Chạy `04_sandbox.py`. Bốn lớp:

| Lớp | Cách làm | Bắt được gì |
|---|---|---|
| Kiểm tra tĩnh | AST: đường dẫn, import bị cấm | Code ngây thơ, lỗi sớm |
| Cách ly tiến trình | `subprocess` + `python -I -S` | Biến môi trường, `PYTHONPATH` |
| Giới hạn tài nguyên | `RLIMIT_CPU`, `RLIMIT_FSIZE`, timeout | Treo, ghi file quá lớn |
| Chặn mạng | Thay `socket` bằng hàm ném lỗi | Gọi ra ngoài |

```python
proc = subprocess.run(
    [sys.executable, "-I", "-S", "main.py"],
    cwd=sandbox, env=minimal_env,
    capture_output=True, text=True, timeout=2.0,
)
```

Kết quả demo: code bình thường in `285`; vòng lặp vô hạn bị kill sau 2 giây; đọc `/etc/hosts` bị chặn trước khi chạy; mở mạng bị chặn ở runtime (dù đã lách kiểm tra tĩnh bằng `__import__`).

Điểm phải nói rõ với người học: **đây không phải sandbox tuyệt đối**. Kiểm tra AST có thể bị lách; chặn socket có thể bị lách; `subprocess` không phải ranh giới bảo mật. Nó chỉ giảm thiệt hại. Cách ly thật cần container, seccomp, user riêng, hoặc dịch vụ sandbox chuyên dụng.

> **Một câu chốt:** sandbox không làm code lạ an toàn; nó làm thiệt hại nhỏ hơn khi code lạ độc hại.

---

## 7. MCP: một giao thức cho tool (18 phút)

Trước MCP, mỗi agent có một cách khai báo tool riêng. Cùng một tool tra đơn phải viết lại cho ChatGPT, cho IDE, cho agent nội bộ. MCP (Model Context Protocol) chuẩn hoá cách nói đó.

Ba vai:

| Vai | Là gì | Ví dụ |
|---|---|---|
| **Host** | Ứng dụng có LLM | Claude Desktop, IDE, agent runtime của bạn |
| **Client** | Đầu nối trong host, giữ một phiên với server | `ClientSession` ở bài 06 |
| **Server** | Nơi expose capability | `05_mcp_server.py` |

Server expose ba loại capability:

| Loại | Ai quyết định dùng | Ví dụ |
|---|---|---|
| **Tools** | Model | `get_order_status`, `quote_refund` |
| **Resources** | Ứng dụng / người dùng | `policy://shop/returns` |
| **Prompts** | Người dùng chọn | mẫu "soạn mail xin lỗi" |

Khác biệt cốt lõi: tool là hành động, resource là dữ liệu chỉ đọc. Đừng nhồi chính sách đổi trả vào mô tả tool; để nó thành resource, client đọc một lần rồi đưa vào context.

Chạy:

```bash
python 05_mcp_server.py            # xem capability, không mở server
python 05_mcp_server.py --serve    # server stdio
python 06_mcp_client.py            # client: initialize -> list_tools -> call_tool -> read_resource
```

Client không import code của server. Nó chỉ biết tên, schema, URI — đó là toàn bộ giá trị của giao thức: **thay server mà không sửa client**.

### Bảo mật MCP

| Việc | Cách làm | Ghi chú |
|---|---|---|
| Xác thực | Bearer token khi chạy HTTP | `Authorization: Bearer <token>` |
| Phân quyền | Scope theo từng tool | Role `viewer` không được gọi `quote_refund` |
| Audit | Log mỗi lần gọi tool | Ghi ra stderr, không ghi stdout |
| Transport | stdio khi cùng máy | Không có cổng mạng, quyền ở tiến trình |

Với stdio, server là một tiến trình con do client khởi chạy — ai chạy được client thì đã có quyền của client. Với HTTP, server mở cổng mạng nên **bắt buộc** có xác thực. Đừng coi "đã có token" là đủ: token của khách A không được gọi tool của khách B, và mỗi lần gọi vẫn phải kiểm tra quyền.

Bearer token tĩnh đủ cho server nội bộ. Ra Internet, chuẩn MCP dùng OAuth 2.1: token vẫn đi trong header `Authorization`, nhưng có hạn, có scope, và có nơi cấp.

Một chi tiết dễ sai: trong server stdio, `stdout` là kênh giao thức. Mọi `print` debug phải ra `stderr`, nếu không client sẽ nhận rác và phiên hỏng.

> **Một câu chốt:** MCP không làm tool an toàn hơn; nó làm tool dùng lại được — nên lớp bảo mật càng phải đặt đúng chỗ.

---

## 8. Lab (60 phút)

### Phần A — Chạy và đọc (25 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_tool_contract.py` | Model thấy gì, không thấy gì? Hai hàm cùng schema khác nhau ở đâu? |
| `02_tool_errors.py` | Vì sao retry không nằm trong model? Timeout bảo vệ ai? |
| `03_sql_readonly.py` | Lớp nào chặn `;`? Nếu bỏ lớp đó thì sao? |
| `04_sandbox.py` | Kịch bản nào bị chặn tĩnh, kịch bản nào bị chặn runtime? |
| `05_mcp_server.py` | Tool và resource khác nhau ở quyền quyết định? |
| `06_mcp_client.py` | Client biết gì về server, và không biết gì? |

### Phần B — Viết tool của bạn (35 phút)

Chọn một việc agent của bạn cần làm, rồi:

1. Viết schema trước, code sau. Tên, mô tả, tham số, kiểu trả về, lỗi.
2. Viết hàm trả chuỗi; mọi lỗi bắt được thành `"LỖI: ..."`.
3. Bọc timeout + retry có giới hạn.
4. Viết 3 test: thành công, không tìm thấy, tool treo.
5. Nếu đã cài `mcp`: đóng gói thành server, thêm một resource chính sách.

Ai xong sớm: thêm audit log và thử chặn tool theo role.

> **Một câu chốt:** lab không kiểm tra bạn viết được hàm; lab kiểm tra bạn viết được hợp đồng.

---

## 9. Bài tập về nhà

Xem `exercises.md`. **Bắt buộc bài 1 và bài 5.**

- Bài 1: viết lại một tool tệ thành tool tốt.
- Bài 5: đóng gói tool thành MCP server + client đọc resource.

Bốn bài còn lại luyện SQL, sandbox, phân quyền và audit.

---

## 10. Tổng kết — 5 câu mang về

1. Model chỉ thấy hợp đồng: tên, mô tả, schema. Code và lỗi thật nằm phía harness.
2. Một tool một việc, tham số tối thiểu, trả chuỗi dễ đọc, lỗi là dữ liệu.
3. Timeout và retry phải có trần; retry mù trên hành động không idempotent là cách trừ tiền hai lần.
4. Quyền nên nằm ở tầng dữ liệu, không chỉ ở prompt: user `SELECT`-only, allowlist, audit.
5. MCP tách tool khỏi agent; đổi lại, xác thực và phân quyền phải làm ở server.

---

## 11. Chuẩn bị buổi 4

- Đọc lại `06_mcp_client.py`: để ý client không hề biết code server. Buổi 4 sẽ áp dụng cùng ý tưởng cho **context**: thứ gì được đưa vào cửa sổ context, thứ gì để ngoài.
- Mang theo một tool đã viết ở lab, kèm 3 test.
- Đọc trước `01_tool_contract.py` mục "Model nhìn thấy gì?" — buổi 4 sẽ nói vì sao mô tả tốt vẫn có thể bị chôn trong quá nhiều context.

---

## Phụ lục — Cấu trúc thư mục

```
session-03/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_tool_contract.py     ← schema tệ vs tốt, model thấy gì
├── 02_tool_errors.py       ← timeout, retry, lỗi là dữ liệu
├── 03_sql_readonly.py      ← SQL tool chỉ đọc, 5 lớp chặn
├── 04_sandbox.py           ← subprocess, thư mục tạm, không mạng
├── 05_mcp_server.py        ← 2 tool + 1 resource, stdio
├── 06_mcp_client.py        ← discovery, call tool, read resource
├── common/
│   ├── fake_model.py       ← model giả, giao thức tool call
│   └── shop.py             ← dữ liệu + luật nghiệp vụ
├── exercises.md
├── requirements.txt
└── .env.example
```
