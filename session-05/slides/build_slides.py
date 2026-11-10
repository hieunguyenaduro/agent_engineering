"""Tạo slide Buổi 5.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from pptx.enum.text import PP_ALIGN  # noqa: E402
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, CONTENT_W, INK, MARGIN, MUTED, NAVY, PANEL, WHITE, Deck,
)

d = Deck(session="Agent Engineering · Buổi 5", out=Path(__file__).with_name("slides.pptx"))

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 5/10",
    "Retrieval và\nKnowledge Engineering",
    "Chunking · Embedding · Qdrant · Eval",
    "120 phút · 55 phút lý thuyết & demo · 60 phút thực hành",
    notes="""Buổi trước agent chỉ biết những gì nằm trong context. Hôm nay cho nó một kho tri thức.
Đừng gọi đây là 'RAG' rồi thôi — buổi này là bốn bước: cắt, nhúng, tìm, đo.
Câu hỏi xuyên suốt: làm sao biết mình tìm đúng?""",
)

# --- 2. Vấn đề --------------------------------------------------------------
s = d.content(
    "Vấn đề",
    "Model không biết dữ liệu riêng của bạn",
    notes="""Hỏi lớp: chính sách đổi trả của công ty bạn nằm ở đâu? Model có biết không?
Ba cách đưa dữ liệu vào context. Chỉ cách thứ ba scale được.
Nhấn: retrieval không phải tính năng phụ, nó là bước chọn dữ liệu.""",
)
d.table(
    s,
    ["Cách", "Vấn đề khi có dữ liệu thật"],
    [
        ["Nhồi hết vào system prompt", "Tốn token, vượt context, dữ liệu cũ"],
        ["Fine-tune model", "Đắt, chậm, vẫn không cập nhật theo ngày"],
        ["Retrieve đúng phần cần", "Phải làm tốt chunking, embedding, xếp hạng"],
    ],
    top=2.15, col_widths=[4.6, 7.0], size=17, row_height=0.85,
)
d.text(s, MARGIN, 5.6, CONTENT_W, 0.8, "Agent không thể trả lời đúng từ tài liệu nó không đọc.", 20, NAVY, bold=True)

# --- 3. Section 1 -----------------------------------------------------------
d.section("01", "Chunking", "Cắt tài liệu trước khi nhúng.", notes="""Phần này 12 phút. Đây là bước bị bỏ qua nhiều nhất.
Nếu chunk sai, mọi thứ phía sau đều sai — dù embedding có xịn đến đâu.""")

# --- 4. Statement -----------------------------------------------------------
d.statement(
    "Nguyên tắc",
    "Chunking sai\nthì retrieval sai.",
    "Và mọi bước phía sau — embedding, xếp hạng, câu trả lời —\nsai theo. Không có cách sửa nào ở cuối pipeline.",
    notes="""Câu này lặp lại nhiều lần trong buổi. Đừng đọc qua.
Ví dụ cụ thể: câu trả lời nằm nửa chunk này nửa chunk kia thì không chunk nào đủ nghĩa để tìm ra.""",
)

# --- 5. Demo chunking -------------------------------------------------------
s = d.content("Demo · 01_chunking.py", "Cắt theo từ, có overlap", notes="""Chạy live. Chỉ vào tài liệu ngắn ra 1 chunk, tài liệu dài ra 5 chunk.
Đó là hành vi đúng: không cắt vụn thứ đã đủ nhỏ.
Sau đó chỉ vào phần so sánh overlap — đây là chỗ lớp hiểu vì sao cần overlap.""")
d.code(
    s,
    '''def chunk_text(text, size=60, overlap=15):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
        start += size - overlap       # lùi lại để giữ ngữ cảnh
    return chunks''',
    top=2.0, height=2.85, size=15,
)
d.text(s, MARGIN, 5.15, CONTENT_W, 1.0, "Overlap để câu nằm ở ranh giới vẫn xuất hiện trọn vẹn trong ít nhất một chunk.", 17, MUTED)

# --- 6. Bảng chọn chunk size ------------------------------------------------
s = d.content("Thiết kế", "Chọn kích thước chunk thế nào?", notes="""Không có con số đúng cho mọi tài liệu. Hỏi lớp: tài liệu của bạn là gì?
Chính sách thì đoạn vừa; hợp đồng thì đoạn lớn hơn; FAQ thì câu hỏi là một chunk.
Nhấn: phải thử và đo, không chép số của người khác.""")
d.table(
    s,
    ["Chunk", "Được", "Mất"],
    [
        ["Quá nhỏ", "Tìm chính xác, ít nhiễu", "Mất ngữ cảnh, câu bị cắt đôi"],
        ["Quá lớn", "Giữ ngữ cảnh", "Nhiễu, tốn token, score loãng"],
        ["Có overlap", "Câu ở ranh giới vẫn trọn", "Tốn dung lượng, có bản trùng"],
    ],
    top=2.15, col_widths=[2.6, 5.0, 5.0], size=17, row_height=0.85,
)
d.text(s, MARGIN, 5.25, CONTENT_W, 0.8, "Bắt đầu ở 300–500 token, đo Hit@k, rồi điều chỉnh.", 18, MUTED)

# --- 7. Section 2 -----------------------------------------------------------
d.section("02", "Embedding", "Biến chữ thành vector để đo gần nghĩa.", notes="""Phần này 10 phút. Đừng đi sâu vào toán.
Chỉ cần hiểu: câu giống nghĩa thì vector gần nhau; cosine càng gần 1 càng giống.""")

# --- 8. Demo embedding ------------------------------------------------------
s = d.content("Demo · 02_embeddings.py", "Hai câu đồng nghĩa, hai mức giống", notes="""Chạy cả hai chế độ nếu có key. Không có key thì chạy hash.
Chỉ vào bảng cosine: câu 1 và câu 2 khác từ nhưng gần nhau khi dùng embedding thật.
Ở chế độ hash chúng chỉ gần vì trùng từ — đó là giới hạn, không phải bug.""")
d.table(
    s,
    ["Câu", "Embedding thật", "Hash giả lập"],
    [
        ["Đổi trả trong 7 ngày", "gần câu 2", "gần câu 2 (trùng từ)"],
        ["Trả hàng trong một tuần", "gần câu 1", "xa câu 1"],
        ["Thời tiết Hà Nội", "xa cả hai", "xa cả hai"],
    ],
    top=2.1, col_widths=[4.6, 4.0, 4.0], size=16, row_height=0.8,
)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.9, "Đừng đánh giá retrieval bằng chế độ hash — nó không hiểu từ đồng nghĩa.", 18, MUTED)

# --- 9. Section 3 -----------------------------------------------------------
d.section("03", "Vector database", "Qdrant: lưu vector, tìm hàng xóm gần nhất.", notes="""Phần này 10 phút. Qdrant chạy RAM, không cần Docker.
Điểm cần nhấn: payload quan trọng ngang vector.""")

# --- 10. Code Qdrant --------------------------------------------------------
s = d.content("Demo · 03_qdrant_basic.py", "Bốn dòng để có một kho", notes="""Chạy live. Chỉ vào payload: doc_id, tenant, source, text.
Không có payload thì kết quả chỉ là một đống số vô nghĩa.
Production chỉ đổi location thành URL server.""")
d.code(
    s,
    '''from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

client = QdrantClient(location=":memory:")       # production: url="http://..."
client.create_collection("knowledge",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

client.upsert("knowledge", points=[
    PointStruct(id=1, vector=vec, payload={
        "doc_id": "doi-tra", "tenant": "shop-a",
        "source": "chinh-sach-doi-tra.md", "text": chunk,
    }),
])''',
    top=1.98, height=3.6, size=13,
)
d.text(s, MARGIN, 5.75, CONTENT_W, 0.7, "Payload là phần biến con số thành tài liệu đọc được.", 17, MUTED)

# --- 11. Score warning ------------------------------------------------------
s = d.content("Đọc kết quả", "Score cao không có nghĩa là đúng", notes="""Ví dụ: câu hỏi 'được đổi trả không?'. Đoạn 'không được đổi trả' có thể giống câu hỏi hơn đoạn trả lời đúng.
Đây là lý do phải đọc nội dung, không chỉ nhìn score.
Và là lý do phải có eval ở phần cuối buổi.""")
d.bullets(s, [
    "Score đo độ giống câu hỏi, không đo tính đúng của câu trả lời",
    "Một đoạn phủ định có thể giống câu hỏi hơn đoạn khẳng định",
    "Luôn đọc nội dung chunk, đừng chỉ nhìn con số",
    "Phải có bộ câu hỏi và đáp án để biết tìm đúng hay không",
], top=2.2, size=21, gap=20)

# --- 12. Section 4 ----------------------------------------------------------
d.section("04", "Lọc theo người dùng", "Kiểm tra quyền ở tầng dữ liệu.", notes="""Phần này 12 phút. Đây là phần bảo mật quan trọng nhất buổi.
Nếu chỉ nhớ một slide của buổi này, nhớ slide tiếp theo.""")

# --- 13. Code filter --------------------------------------------------------
s = d.content("Demo · 04_filter_by_user.py", "Filter nằm trong truy vấn", notes="""Chạy live. So sánh hai khối output: SAI thấy dữ liệu shop-b, ĐÚNG thì không.
Nhấn: filter phải nằm trong query, trước khi dữ liệu rời database.
Chỉ thêm: nhiều chunk cùng một doc chiếm top-k — đó là lý do cần dedup.""")
d.code(
    s,
    '''from qdrant_client.models import Filter, FieldCondition, MatchValue

query_filter = Filter(
    must=[FieldCondition(key="tenant", match=MatchValue(value="shop-a"))]
)

hits = client.query_points(
    "knowledge",
    query=embed_one(question),
    query_filter=query_filter,      # <-- quyền nằm ở đây
    limit=3,
)''',
    top=1.95, height=3.75, size=13,
)

# --- 14. Vì sao prompt không đủ ---------------------------------------------
s = d.content("Bảo mật", "Vì sao không thể dặn model?", notes="""Hỏi lớp: nếu dữ liệu đã nằm trong context, điều gì đảm bảo model không nói ra?
Trả lời: không có gì. Prompt injection trong một tài liệu là đủ.
Nguyên tắc: dữ liệu không được rời database nếu người dùng không có quyền.""")
d.panel(s, MARGIN, 2.2, 5.3, 2.8, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.7, 0.4, "CÁCH SAI", 12, "B91C1C", bold=True)
d.text(s, MARGIN + 0.3, 2.85, 4.7, 1.9, "Retrieve tất cả\n→ nhồi vào context\n→ dặn 'đừng tiết lộ'\n\nDữ liệu đã ở trong context.", 16, INK, line_spacing=1.35)

d.panel(s, MARGIN + 5.9, 2.2, 5.3, 2.8, ACCENT_SOFT)
d.text(s, MARGIN + 6.2, 2.4, 4.7, 0.4, "CÁCH ĐÚNG", 12, ACCENT, bold=True)
d.text(s, MARGIN + 6.2, 2.85, 4.7, 1.9, "Filter theo tenant\nngay trong truy vấn\n\nDữ liệu không có quyền\nkhông bao giờ rời database.", 16, INK, line_spacing=1.35)

d.text(s, MARGIN, 5.35, CONTENT_W, 0.8, "Một prompt injection trong tài liệu là đủ để phá lời dặn.", 19, NAVY, bold=True)

# --- 15. Section 5 ----------------------------------------------------------
d.section("05", "Retrieval thành tool", "Để model tự quyết định khi nào cần tra.", notes="""Phần này 10 phút. Đây là chỗ agent khác RAG cổ điển.
RAG cổ điển luôn retrieve; agent chỉ retrieve khi thấy cần.""")

# --- 16. Code tool ----------------------------------------------------------
s = d.content("Demo · 05_rag_tool.py", "Tool đóng cứng theo tenant", notes="""Chạy live hai câu: một có dữ liệu, một không.
Chỉ vào sentinel KHONG_DU_DU_LIEU. Đó là hợp đồng giữa tool và agent.
Nhấn: ngưỡng score nằm trong tool, không nằm trong prompt.""")
d.code(
    s,
    '''def make_search_tool(tenant: str):
    @tool
    def search_knowledge(query: str) -> str:
        """Tìm trong kho tri thức của cửa hàng."""
        hits = search(client, query, tenant=tenant, limit=3)
        if not hits or hits[0].score < SCORE_TOI_THIEU:
            return "KHONG_DU_DU_LIEU: không tìm thấy tài liệu phù hợp."
        return "\\n---\\n".join(
            f"[nguon: {h.payload['source']} | diem: {h.score:.2f}]\\n{h.payload['text']}"
            for h in hits
        )
    return search_knowledge''',
    top=1.98, height=3.7, size=13,
)
d.text(s, MARGIN, 5.8, CONTENT_W, 0.7, "Model không có tham số để đổi tenant — quyền nằm trong closure.", 17, MUTED)

# --- 17. So sánh ------------------------------------------------------------
s = d.content("So sánh", "RAG cổ điển và retrieval-as-tool", notes="""Bảng này để lớp thấy đây không phải 'RAG mới hơn', mà là cách đặt quyết định ở đúng chỗ.
Agent quyết định có tra; tool quyết định trả gì; code quyết định ai được thấy gì.""")
d.table(
    s,
    ["", "RAG cổ điển", "Retrieval as tool"],
    [
        ["Khi nào tra", "Luôn tra", "Model tự quyết định"],
        ["Nguồn", "Không có trong câu trả lời", "Tool trả source + score"],
        ["Thiếu dữ liệu", "Vẫn trả lời, dễ bịa", "Tool nói KHONG_DU_DU_LIEU"],
        ["Quyền", "Dễ quên filter", "Đóng cứng trong tool"],
    ],
    top=2.1, col_widths=[2.8, 4.8, 5.2], size=16, row_height=0.75,
)

# --- 18. Statement ----------------------------------------------------------
d.statement(
    "Hành vi đúng",
    "Biết nói\n\"không đủ dữ liệu\".",
    "Một agent luôn trả lời được mọi câu hỏi là agent nguy hiểm.\nCâu trả lời 'mình không có thông tin' đáng tin hơn một câu bịa.",
    notes="""Đây là câu quan trọng nhất buổi về hành vi.
Hỏi lớp: lần cuối bạn thấy chatbot bịa là khi nào? Vì sao nó bịa? Vì nó không có đường lui.
Thiết kế đường lui là một phần của thiết kế agent.""",
)

# --- 19. Section 6 ----------------------------------------------------------
d.section("06", "Đánh giá retrieval", "Không đo thì không biết mình đang cải thiện hay phá.", notes="""Phần này 10 phút. Ngắn nhưng là phần sẽ quay lại ở buổi 7.
Hai chỉ số đơn giản đủ dùng cho hầu hết dự án.""")

# --- 20. Hai chỉ số ---------------------------------------------------------
s = d.content("Chỉ số", "Hit@k và MRR", notes="""Giải thích bằng ví dụ: 5 câu hỏi, 4 câu tìm đúng trong top 3 → Hit@3 = 80%.
MRR: đúng ở vị trí 1 → 1.0; vị trí 2 → 0.5; vị trí 3 → 0.33.
Hai chỉ số bổ sung nhau: Hit nói 'có tìm ra', MRR nói 'xếp hạng tốt không'.""")
d.table(
    s,
    ["Chỉ số", "Công thức", "Đọc thế nào"],
    [
        ["Hit@k", "tỉ lệ câu có đáp án trong k kết quả đầu", "gần 100% là tốt"],
        ["MRR", "trung bình 1/rank của đáp án đúng", "1.0 là luôn đứng đầu"],
    ],
    top=2.1, col_widths=[2.2, 5.6, 4.6], size=17, row_height=0.85,
)
d.text(s, MARGIN, 4.9, CONTENT_W, 1.2, "Bộ câu hỏi phải lấy từ người dùng thật.\nCâu hỏi tự nghĩ ra cho dễ sẽ cho điểm cao giả tạo.", 18, MUTED, line_spacing=1.4)

# --- 21. Code eval ----------------------------------------------------------
s = d.content("Demo · 06_eval_retrieval.py", "Đo bằng code, không bằng cảm giác", notes="""Chạy live. Chỉ vào CASES: mỗi dòng là một câu hỏi thật + doc_id đúng.
Hàm evaluate đơn giản đến mức có thể viết trong 10 dòng — đó là điểm mạnh.
Ai cũng đo được, nên không có lý do không đo.""")
d.code(
    s,
    '''CASES = [
    ("Được đổi trả trong bao nhiêu ngày?", "doi-tra"),
    ("Giao hàng nội thành mất bao lâu?", "van-chuyen"),
    ("Tai nghe bảo hành mấy tháng?", "bao-hanh"),
]

for question, expected in CASES:
    ids = [h.payload["doc_id"] for h in search(client, question, tenant="shop-a", limit=3)]
    if expected in ids:
        hits += 1
        rr += 1 / (ids.index(expected) + 1)''',
    top=2.0, height=3.2, size=14,
)

# --- 22. Cách đọc kết quả ---------------------------------------------------
s = d.content("Chẩn đoán", "Đọc kết quả thế nào?", notes="""Ba dòng này là bảng chẩn đoán.
Nếu Hit@1 thấp mà Hit@3 cao: tài liệu đúng có trong kho, chỉ xếp hạng chưa tốt → thử rerank.
Nếu cả hai thấp: vấn đề ở chunking/embedding/tài liệu.
Nếu Hit cao mà câu trả lời vẫn sai: retrieval đúng, generation sai → buổi 7.""")
d.table(
    s,
    ["Hiện tượng", "Nguyên nhân thường gặp", "Thử gì"],
    [
        ["Hit@1 thấp, Hit@3 cao", "Xếp hạng chưa tốt", "Rerank, cải thiện chunk"],
        ["Cả hai đều thấp", "Chunking / embedding / thiếu tài liệu", "Đổi chunk, thêm dữ liệu"],
        ["Hit cao, trả lời sai", "Retrieval đúng, generation sai", "Sửa prompt/tool (buổi 7)"],
    ],
    top=2.1, col_widths=[3.6, 4.8, 4.0], size=16, row_height=0.85,
)

# --- 23. Lab ----------------------------------------------------------------
d.section("Lab", "60 phút thực hành", "Chạy, đo, rồi phá.", notes="""25 phút chạy 6 file, 35 phút thêm tài liệu thật và đo lại.
Đi vòng quanh, hỏi mỗi nhóm: case nào trượt, và bạn nghĩ vì sao?""")

# --- 24. Lab roadmap --------------------------------------------------------
s = d.content("Lab", "Hai phần", notes="""Phần A là đọc code có hướng dẫn. Phần B là làm việc thật với tài liệu của bạn.
Ai xong sớm: thử dedup theo doc_id và đo lại Hit@k.""")
d.panel(s, MARGIN, 2.2, 5.2, 2.9, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.6, 0.4, "25 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.3, 2.8, 4.6, 0.6, "Chạy 6 file", 21, NAVY, bold=True)
d.text(s, MARGIN + 0.3, 3.45, 4.6, 1.5, "Mỗi file trả lời một câu hỏi\nvề chunk, embedding, quyền,\nhoặc chất lượng tìm kiếm.", 15, INK, line_spacing=1.35)

d.panel(s, MARGIN + 5.6, 2.2, 5.2, 2.9, ACCENT_SOFT)
d.text(s, MARGIN + 5.9, 2.4, 4.6, 0.4, "35 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 5.9, 2.8, 4.6, 0.6, "Kho tri thức của bạn", 21, NAVY, bold=True)
d.text(s, MARGIN + 5.9, 3.45, 4.6, 1.5, "Thêm tài liệu thật, viết 5 case eval,\nđo Hit@3 trước và sau\nkhi đổi cấu hình.", 15, INK, line_spacing=1.35)

# --- 25. Bài tập ------------------------------------------------------------
s = d.content("Về nhà", "Bài tập bắt buộc", notes="""Bài 1 củng cố chunking. Bài 3 là bài thật nhất: thêm dữ liệu luôn làm chỉ số tụt.
Ai làm bài 3 xong sẽ hiểu vì sao eval quan trọng hơn cảm giác.""")
d.bullets(s, [
    "Bài 1 — thử ba cấu hình chunk, chỉ ra một câu bị cắt đôi",
    "Bài 3 — thêm tài liệu + 3 case eval, chứng minh một case trượt rồi sửa được",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 3.8, CONTENT_W, 1.6, "Nộp: bảng Hit@1 trước/sau bằng số thật + giải thích vì sao.\nTiêu chí: giải thích được, không chỉ chạy được.", 17, MUTED, line_spacing=1.5)

# --- 26. Tổng kết -----------------------------------------------------------
s = d.content("Tổng kết", "Năm câu mang về", notes="""Đọc chậm. Dừng ở câu 4 — đó là câu bảo mật, sẽ quay lại buổi 8.
Câu 5 là câu nối sang buổi 6 và 7.""")
d.bullets(s, [
    "Chunking sai thì retrieval sai, và mọi bước sau sai theo.",
    "Embedding đo 'gần nghĩa', không đo 'đúng'.",
    "Vector database tìm 'giống', không tìm 'đúng' — score cao chưa chắc đúng.",
    "Kiểm tra quyền ở tầng dữ liệu, không phải ở prompt.",
    "Retrieval tốt phải biết nói 'không đủ dữ liệu' và phải đo được.",
], top=2.05, size=20, gap=16)

# --- 27. Buổi sau -----------------------------------------------------------
s = d.content("Buổi 6", "Tiếp theo: Multi-agent Systems", notes="""Nhắc nộp bài. Buổi 6 sẽ tách một agent thành nhiều agent.
Câu hỏi mở: khi nào nhiều agent tốt hơn một agent? Không phải lúc nào cũng tốt.
Mời lớp đặt câu hỏi.""")
d.bullets(s, [
    "Subagent như một tool: giao việc, nhận kết quả",
    "Supervisor: một agent điều phối nhiều agent",
    "Chạy song song và tổng hợp kết quả",
    "Handoff, timeout, và chi phí tăng theo số agent",
], top=2.15, size=20, gap=16)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.9, "Chuẩn bị: nghĩ một quy trình có thể tách thành 2–3 bước độc lập.", 17, MUTED)

d.save()
