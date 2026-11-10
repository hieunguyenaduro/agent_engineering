# Buổi 5 — Retrieval và Knowledge Engineering

> Agent ở buổi 1–4 chỉ biết những gì nằm trong context. Buổi này cho nó một **kho tri thức** để tra trước khi trả lời: cắt tài liệu, nhúng thành vector, tìm kiếm có lọc, và đo xem tìm có đúng không.

**Thời lượng:** 120 phút — 55 phút giảng + demo, 60 phút thực hành, 5 phút tổng kết.

---

## 0. Chuẩn bị

```bash
cd session-05
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # dán OPENAI_API_KEY nếu có
python 01_chunking.py         # không cần key
python 03_qdrant_basic.py
```

Không có key:

```bash
FAKE=1 python 03_qdrant_basic.py
```

Chế độ `FAKE=1` dùng embedding giả bằng hash từ. Nó chạy được toàn bộ luồng nhưng **chỉ khớp theo từ khoá** — không hiểu từ đồng nghĩa. Dùng nó để học cơ chế, không dùng để đánh giá chất lượng retrieval.

Qdrant chạy trong RAM (`QdrantClient(location=":memory:")`), không cần Docker. Khi lên production chỉ đổi sang URL server, phần còn lại giữ nguyên.

---

## 1. Vì sao cần retrieval? (5 phút)

Model không biết dữ liệu riêng của bạn: chính sách đổi trả hôm nay, giá sản phẩm, hợp đồng của khách. Có ba cách đưa dữ liệu vào context:

| Cách | Vấn đề |
|---|---|
| Nhồi tất cả vào system prompt | Tốn token, vượt context window, dữ liệu cũ |
| Fine-tune model | Đắt, chậm, vẫn không cập nhật theo ngày |
| Retrieve đúng phần cần | Phải làm tốt chunking, embedding, xếp hạng |

Retrieval không phải "tìm kiếm cho vui". Nó là **bước chọn dữ liệu** — và nếu chọn sai, mọi bước sau đều sai theo.

> **Một câu chốt:** agent không thể trả lời đúng từ tài liệu nó không đọc.

---

## 2. Chunking: cắt trước khi nhúng (12 phút)

Chạy `01_chunking.py`. Tài liệu dài được cắt thành các đoạn `CHUNK_SIZE` từ, chồng lấn `OVERLAP` từ.

```python
def chunk_text(text, size=60, overlap=15):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
        start += size - overlap
    return chunks
```

Ba câu hỏi phải trả lời khi chọn kích thước chunk:

1. **Chunk quá nhỏ** → mất ngữ cảnh, câu trả lời nằm nửa này nửa kia.
2. **Chunk quá lớn** → tìm ra nhưng chứa nhiều thông tin nhiễu, tốn token.
3. **Overlap để làm gì?** → để câu nằm ở ranh giới vẫn xuất hiện trọn vẹn trong ít nhất một chunk.

Trong ví dụ, tài liệu ngắn ra 1 chunk, tài liệu dài ra 5 chunk. Đó là hành vi đúng: không cắt vụn thứ đã đủ nhỏ.

> **Một câu chốt:** chunking sai thì retrieval sai, và mọi thứ phía sau sai theo.

---

## 3. Embedding: biến chữ thành vector (10 phút)

Chạy `02_embeddings.py`. Mỗi câu thành một vector; câu giống nhau thì vector gần nhau.

```python
from common.knowledge import embed_texts

vectors = embed_texts(["Chính sách đổi trả trong 7 ngày", "Khách được trả hàng trong một tuần"])
```

| Chế độ | Cách hoạt động | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| OpenAI `text-embedding-3-small` | Học từ dữ liệu lớn | Hiểu đồng nghĩa, ngữ cảnh | Tốn tiền, cần mạng |
| Hash giả lập | Băm từng từ vào vector | Miễn phí, offline | Chỉ khớp từ khoá |

Điểm tương đồng dùng cosine: gần 1 là giống, gần 0 là khác.

**Điều quan trọng:** đừng đánh giá retrieval bằng chế độ hash. Nó sẽ khiến bạn tưởng hệ thống tệ (hoặc tốt) trong khi vấn đề thật nằm ở embedding.

> **Một câu chốt:** embedding là cách đo "gần nghĩa", không phải cách đo "đúng".

---

## 4. Vector database: Qdrant (10 phút)

Chạy `03_qdrant_basic.py`.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

client = QdrantClient(location=":memory:")
client.create_collection("knowledge", vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
client.upsert("knowledge", points=[PointStruct(id=1, vector=vec, payload={...})])
```

`payload` là phần cực kỳ quan trọng: nó chứa `doc_id`, `tenant`, `source`, `text`. Không có payload thì bạn chỉ có một đống số vô nghĩa.

Kết quả trả về có `score`. Đọc kỹ: **score cao nghĩa là đoạn văn giống câu hỏi, không có nghĩa là câu trả lời đúng.** Một đoạn nói "không được đổi trả" có thể giống câu hỏi "được đổi trả không?" hơn cả đoạn trả lời đúng.

> **Một câu chốt:** vector database tìm "giống", không tìm "đúng".

---

## 5. Lọc theo người dùng: kiểm tra ở tầng dữ liệu (12 phút)

Chạy `04_filter_by_user.py`. Đây là bài quan trọng nhất buổi về bảo mật.

Cách sai:

```python
hits = client.query_points("knowledge", query=vec, limit=4)   # không lọc
# rồi dặn model: "đừng tiết lộ dữ liệu của công ty khác"
```

Cách đúng:

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

hits = client.query_points(
    "knowledge",
    query=vec,
    query_filter=Filter(must=[FieldCondition(key="tenant", match=MatchValue(value="shop-a"))]),
)
```

Vì sao cách sai nguy hiểm: dữ liệu của tenant khác **đã nằm trong context** trước khi model kịp "vâng lời". Một prompt injection trong tài liệu là đủ để lộ. Kiểm tra quyền phải nằm ở nơi dữ liệu rời khỏi database, không phải ở prompt.

Trong ví dụ, cùng câu hỏi, `shop-b` chỉ thấy đúng một tài liệu của `shop-b`.

Một chi tiết đáng chú ý: `shop-a` trả về ba chunk của cùng một tài liệu. Đó là lý do thực tế cần **giới hạn số chunk mỗi tài liệu** hoặc gộp theo `doc_id` — nếu không, một tài liệu dài sẽ chiếm hết top-k và đẩy tài liệu khác ra ngoài.

> **Một câu chốt:** quyền truy cập kiểm tra ở tầng dữ liệu, không phải ở lời dặn model.

---

## 6. Retrieval thành tool của agent (10 phút)

Chạy `05_rag_tool.py`. Đây là chỗ RAG cổ điển và agent khác nhau:

| RAG cổ điển | Retrieval as tool |
|---|---|
| Luôn retrieve trước mọi câu hỏi | Model tự quyết định có cần tra |
| Không có nguồn trong câu trả lời | Tool trả về `source` + `score` |
| Không biết khi nào thiếu dữ liệu | Tool trả `KHONG_DU_DU_LIEU` |

```python
@tool
def search_knowledge(query: str) -> str:
    """Tìm trong kho tri thức của cửa hàng..."""
    hits = search(client, query, tenant=tenant, limit=3)
    if not hits or hits[0].score < SCORE_TOI_THIEU:
        return "KHONG_DU_DU_LIEU: không tìm thấy tài liệu phù hợp."
    return "\n---\n".join(f"[nguon: {h['source']} | diem: {h['score']:.2f}]\n{h['text']}" for h in hits)
```

Hai điểm thiết kế:

1. **Tool được đóng cứng theo tenant** — `make_search_tool(tenant)` tạo tool chỉ thấy dữ liệu của tenant đó. Model không có tham số để đổi tenant.
2. **Ngưỡng score là một phần của tool**, không phải của prompt. Ngưỡng phải hiệu chỉnh theo embedding đang dùng.

Khi tool nói không đủ dữ liệu, agent phải nói thẳng là không biết. Đó là hành vi đúng — và là thứ khiến người dùng tin agent hơn.

> **Một câu chốt:** retrieval tốt không chỉ tìm ra tài liệu, mà còn biết khi nào không có tài liệu.

---

## 7. Đánh giá retrieval (10 phút)

Chạy `06_eval_retrieval.py`. Hai chỉ số đơn giản:

| Chỉ số | Công thức | Đọc thế nào |
|---|---|---|
| **Hit@k** | tỉ lệ câu hỏi có tài liệu đúng trong k kết quả đầu | gần 100% là tốt |
| **MRR** | trung bình `1/rank` của tài liệu đúng | 1.0 là luôn đứng đầu |

```python
CASES = [("Được đổi trả trong bao nhiêu ngày?", "doi-tra"), ...]

for question, expected in CASES:
    ids = [hit.payload["doc_id"] for hit in search(client, question, tenant="shop-a", limit=3)]
    if expected in ids:
        rr += 1 / (ids.index(expected) + 1)
```

Cách đọc:

- **Hit@1 thấp, Hit@3 cao** → tài liệu đúng có trong kho, nhưng xếp hạng chưa tốt. Thử rerank hoặc cải thiện chunk.
- **Cả hai đều thấp** → vấn đề ở chunking, embedding, hoặc tài liệu không có thông tin.
- **Hit cao nhưng câu trả lời vẫn sai** → retrieval đúng, generation sai. Đó là bài của buổi 7.

Bộ test phải lấy từ câu hỏi thật của người dùng, không phải câu hỏi bạn tự nghĩ ra cho dễ.

> **Một câu chốt:** không đo được retrieval thì không biết mình đang cải thiện hay phá.

---

## 8. Lab (60 phút)

### Phần A — Chạy và đọc (25 phút)

| File | Câu hỏi phải trả lời được |
|---|---|
| `01_chunking.py` | Vì sao tài liệu ngắn không bị cắt? Overlap giải quyết vấn đề gì? |
| `02_embeddings.py` | Vì sao hai câu đồng nghĩa lại xa nhau ở chế độ hash? |
| `03_qdrant_basic.py` | Score cao có nghĩa là câu trả lời đúng không? |
| `04_filter_by_user.py` | Nếu bỏ filter, dữ liệu nào rò rỉ và qua đường nào? |
| `05_rag_tool.py` | Vì sao tool phải nói `KHONG_DU_DU_LIEU` thay vì trả chuỗi rỗng? |
| `06_eval_retrieval.py` | Hit@1 và Hit@3 khác nhau ở đâu, khi nào cần cả hai? |

### Phần B — Nâng cấp kho tri thức (35 phút)

Thêm một tài liệu thật của bạn (chính sách, FAQ, ghi chú sản phẩm) và làm đủ bốn bước:

1. Cắt chunk với hai cấu hình khác nhau, ghi lại số chunk.
2. Nạp vào Qdrant, chạy 5 câu hỏi thật.
3. Viết 5 case eval, đo Hit@3 trước và sau khi đổi cấu hình.
4. Ghi lại kết luận: cấu hình nào tốt hơn và **vì sao**, không chỉ vì điểm cao hơn.

Làm theo `exercises.md` nếu cần gợi ý từng bước.

---

## 9. Bài tập về nhà

Xem `exercises.md`. Bắt buộc bài 1 và bài 3.

---

## 10. Tổng kết — 5 câu mang về

1. Chunking sai thì retrieval sai, và mọi bước sau sai theo.
2. Embedding đo "gần nghĩa", không đo "đúng".
3. Vector database tìm "giống", không tìm "đúng" — score cao chưa chắc là câu trả lời.
4. Kiểm tra quyền ở tầng dữ liệu, không phải ở prompt.
5. Retrieval tốt phải biết nói "không đủ dữ liệu", và phải đo được bằng Hit@k / MRR.

---

## 11. Chuẩn bị buổi 6

- Đọc lại `05_rag_tool.py`: để ý agent chỉ có **một** tool.
- Buổi 6 sẽ có nhiều agent, mỗi agent có tool riêng — và câu hỏi khó hơn: ai quyết định agent nào làm việc gì.
- Mang theo một quy trình nghiệp vụ có thể tách thành 2–3 bước độc lập.

---

## Phụ lục — Cấu trúc thư mục

```
session-05/
├── README.md
├── slides/
│   ├── slides.pptx
│   └── build_slides.py
├── 01_chunking.py
├── 02_embeddings.py
├── 03_qdrant_basic.py
├── 04_filter_by_user.py
├── 05_rag_tool.py
├── 06_eval_retrieval.py
├── common/
│   ├── knowledge.py    ← tài liệu, chunking, embedding, Qdrant
│   ├── llm.py          ← chọn OpenAI hay model giả
│   └── fake_model.py   ← model giả luôn gọi search
├── exercises.md
├── requirements.txt
└── .env.example
```
