# Agent Engineering — bài giảng

Khóa 10 buổi, mỗi buổi 2 giờ: 55 phút lý thuyết & demo, 60 phút thực hành, 5 phút tổng kết.

Mỗi buổi là một thư mục độc lập, chạy được ngay. Tất cả ví dụ đều có **chế độ offline** (`FAKE=1`), không cần Docker, không cần dịch vụ ngoài.

| Buổi | Chủ đề | Thực hành | Trạng thái |
|---|---|---|---|
| [01](session-01/) | Hệ thống agent hiện đại và harness | Vòng lặp agent, tool, memory, mini harness | ✅ đã kiểm chứng offline |
| [02](session-02/) | Agent Loop Engineering với LangGraph | Graph, state, checkpoint, streaming | ✅ đã kiểm chứng offline |
| [03](session-03/) | Tool và MCP Engineering | Tool contract, lỗi, SQL read-only, sandbox, MCP server/client | ✅ đã kiểm chứng offline + MCP |
| [04](session-04/) | Context Engineering với Prompt, Skill và Memory | Ngân sách context, prompt tầng, skill loader, memory | ✅ đã kiểm chứng offline |
| [05](session-05/) | Retrieval và Knowledge Engineering | Chunking, embedding, Qdrant, lọc tenant, eval retrieval | ✅ đã kiểm chứng offline |
| [06](session-06/) | Multi-agent Systems | Subagent-as-tool, supervisor, Send, handoff, chi phí | ✅ đã kiểm chứng offline |
| [07](session-07/) | Observability và Evaluation Engineering | Trace, dataset, evaluator, LLM-judge, regression | ✅ đã kiểm chứng offline |
| [08](session-08/) | Security, Guardrails và Governance | Prompt injection, PII, tool guard, tenant isolation, test | ✅ 14/14 test pass |
| [09](session-09/) | Serving Agents: FastAPI, Streaming và Session | API, SSE, auth, health, client/UI | ✅ đã kiểm chứng offline |
| [10](session-10/) | Capstone: Ghép hệ thống và bảo vệ trước lớp | Kiến trúc, eval report, failure drill, cost, demo | ✅ đã kiểm chứng offline |

Mỗi thư mục có:

```
README.md          tài liệu giảng (250–400 dòng)
slides/            build_slides.py + slides.pptx (24–30 slide, có speaker notes)
01_....py          5–6 ví dụ chạy độc lập
common/            code dùng chung trong buổi
exercises.md       bài tập, ghi rõ bài bắt buộc
requirements.txt
.env.example
```

## Bắt đầu

```bash
cd session-02
cat README.md                 # đọc trước buổi
open slides/slides.pptx       # slide kèm speaker notes
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # dán OPENAI_API_KEY nếu có
python 01_first_graph.py
```

Không có API key:

```bash
FAKE=1 python 01_first_graph.py
```

Chế độ `FAKE=1` dùng model hoặc dịch vụ giả để chạy đúng luồng. Nó dạy cơ chế, không dùng để đánh giá chất lượng câu trả lời.

Buổi 9 và 10 chạy hoàn toàn offline — không cần key, không cần mạng. Buổi 3 cần `mcp>=1.2,<2` cho hai ví dụ MCP; thiếu package thì ví dụ in hướng dẫn cài và thoát sạch.

## Kiểm tra một buổi

```bash
cd session-05

# 1. Cú pháp
python -m py_compile 0*.py common/*.py

# 2. Chạy toàn bộ ví dụ offline
for f in 0*.py; do FAKE=1 python "$f" || echo "FAIL $f"; done

# 3. Sinh lại slide
python slides/build_slides.py
```

Mỗi README có bảng "file → câu hỏi phải trả lời được" ở phần Lab. Đó là tiêu chí kiểm tra nhanh sau khi chạy.

## Sửa slide

Slide được sinh từ code, không phải file nhị phân:

```bash
pip install python-pptx
python session-10/slides/build_slides.py
```

Sửa nội dung trong `slides/build_slides.py` rồi chạy lại. Không sửa trực tiếp `slides.pptx` — lần build sau sẽ ghi đè.

## Tài liệu soạn bài

- [`tools/deck.py`](tools/deck.py) — thư viện dựng slide dùng chung.
- [`tools/SESSION_TEMPLATE.md`](tools/SESSION_TEMPLATE.md) — cấu trúc, giọng văn và checklist trước khi giao.

## Ghi chú về môi trường

- Python 3.10+; repo đã kiểm chứng bằng Python 3.12.
- Không hardcode key. Mọi key đọc từ `.env`.
- Qdrant chạy `:memory:` — không cần Docker.
- Session 7 có nhánh Langfuse tuỳ chọn; không cài vẫn chạy bằng tracer local.
- Số liệu trong bài đều là số đo thật của ví dụ, không phải số minh hoạ bịa.
