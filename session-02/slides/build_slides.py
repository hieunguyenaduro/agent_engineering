"""Tạo slide Buổi 2.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from pptx.enum.text import PP_ALIGN  # noqa: E402
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, AMBER, CONTENT_W, GREEN, INK, MARGIN, MUTED, NAVY,
    PANEL, Deck,
)

d = Deck(session="Agent Engineering · Buổi 2", out=Path(__file__).with_name("slides.pptx"))

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 2/10",
    "Agent Loop\nvới LangGraph",
    "Graph · State · Checkpoint · Interrupt",
    "120 phút · 55 phút lý thuyết & demo · 60 phút thực hành",
    notes="""Buổi 1 các bạn tự viết vòng for. Hôm nay thay bằng graph.
Đừng nghĩ graph là công nghệ mới — nó chỉ là cách vẽ vòng lặp ra giấy rồi để máy chạy đúng bản vẽ.
Ba thứ mới thực sự: checkpoint, streaming, interrupt.""",
)

# --- 2. Vấn đề của vòng for -------------------------------------------------
s = d.content(
    "Vấn đề",
    "Vòng for ở buổi 1 chưa đủ để lên production",
    notes="""Đừng nói 'vòng for sai'. Nó đúng cho demo. Nó thiếu bốn thứ khi có người dùng thật.
Hỏi lớp: nếu process chết giữa lúc agent đang gọi tool thì chuyện gì xảy ra? Mất hết state.
Bốn dòng trong bảng là bốn động lực của buổi hôm nay.""",
)
d.table(
    s,
    ["Thiếu gì", "Hậu quả khi có người dùng thật"],
    [
        ["State nằm trong biến local", "Process chết là mất sạch hội thoại"],
        ["Không có điểm dừng", "Không thể chèn bước xin phép"],
        ["Không có vết từng bước", "Debug bằng print, không tái hiện được"],
        ["Không resume được", "Chạy lại từ đầu, tốn gấp đôi tiền"],
    ],
    top=2.1,
    col_widths=[4.6, 7.0],
    size=17,
    row_height=0.78,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.8, "LangGraph không làm agent thông minh hơn. Nó làm agent hiểu được.", 19, MUTED)

# --- 3. Section 1 -----------------------------------------------------------
d.section("01", "Graph là gì?", "State, Node, Edge — chưa có gì liên quan tới LLM.", notes="""Phần này 15 phút. Bắt đầu bằng graph thuần, không model.
Lý do: nếu hiểu graph bằng ví dụ có LLM, học viên sẽ nhầm graph với agent.""")

# --- 4. Statement -----------------------------------------------------------
d.statement(
    "Cách nghĩ",
    "Một máy trạng thái\ncó lưu vết.",
    "Bạn vẽ các bước ra giấy. Máy chạy đúng bản vẽ đó.\nMỗi bước để lại một ảnh chụp state.",
    notes="""Graph = máy trạng thái. Không hơn.
Điểm khác biệt so với vòng for: mỗi bước để lại dấu vết.
Câu này sẽ quay lại ở phần checkpoint.""",
)

# --- 5. Code 01 -------------------------------------------------------------
s = d.content(
    "Demo · 01_graph_basics.py",
    "Ba khái niệm, mười dòng",
    notes="""Chạy file này live. Không cần key.
Chỉ vào ba chỗ: State có kiểu, node trả về dict, conditional edge chọn nhánh.
Sau khi chạy, dán draw_mermaid() vào mermaid.live để lớp thấy hình.""",
)
d.code(
    s,
    '''class State(TypedDict):
    question: str
    route: str
    answer: str

def classify(state: State) -> dict:
    if "đơn" in state["question"]:
        return {"route": "billing"}      # chỉ phần cần sửa
    return {"route": "technical"}

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_conditional_edges("classify", lambda s: s["route"], {...})
graph = builder.compile()''',
    top=2.0, height=3.35, size=14,
)
d.text(s, MARGIN, 5.5, CONTENT_W, 0.8, "Node không sửa state. Nó trả về dict, LangGraph merge dict đó vào state.", 17, MUTED)

# --- 6. Bảng khái niệm ------------------------------------------------------
s = d.content("Khái niệm", "Bốn từ cần dùng đúng", notes="""Đọc nhanh bảng. Nhấn mạnh cột 'nghĩa' — học viên hay nói 'node là bước' nhưng không nói được nó nhận gì trả gì.
Hỏi: compile() để làm gì? Trả lời: biến định nghĩa thành thứ chạy được, giống build trước khi run.""")
d.table(
    s,
    ["Từ", "Nghĩa", "Trong file"],
    [
        ["State", "Dữ liệu đi qua graph, có kiểu", "question, route, answer"],
        ["Node", "Hàm nhận state, trả về phần cần sửa", "classify, billing"],
        ["Edge", "Bước tiếp theo, có thể có điều kiện", "add_conditional_edges"],
        ["Compile", "Biến định nghĩa thành thứ chạy được", "builder.compile()"],
    ],
    top=2.1, col_widths=[1.8, 6.2, 3.8], size=16, row_height=0.72,
)
d.text(s, MARGIN, 5.55, CONTENT_W, 0.7, "Dán graph.get_graph().draw_mermaid() vào mermaid.live để review thiết kế với người không đọc code.", 16, MUTED)

# --- 7. Section 2 -----------------------------------------------------------
d.section("02", "Agent loop bằng graph", "Vòng for trở thành hai node nối nhau.", notes="""Phần này 15 phút. Đây là chỗ nối trực tiếp với buổi 1.
Mở song song 06_mini_harness.py và 02_agent_loop.py nếu có thể.""")

# --- 8. Sơ đồ vòng lặp ------------------------------------------------------
s = d.content("Cấu trúc", "agent ⇄ tools", notes="""Vẽ lên bảng: START -> agent, agent rẽ nhánh.
Có tool_calls thì sang tools, hết tool thì END.
Mũi tên tools -> agent chính là vòng lặp. Đó là toàn bộ bí mật.""")
d.panel(s, MARGIN, 2.3, 3.2, 1.5, NAVY)
d.text(s, MARGIN + 0.25, 2.55, 2.7, 1.0, "START", 22, "FFFFFF", bold=True, align=PP_ALIGN.CENTER)
d.panel(s, MARGIN + 4.0, 2.3, 3.2, 1.5, ACCENT_SOFT)
d.text(s, MARGIN + 4.25, 2.55, 2.7, 1.0, "agent", 24, NAVY, bold=True, align=PP_ALIGN.CENTER)
d.panel(s, MARGIN + 8.0, 2.3, 3.2, 1.5, PANEL)
d.text(s, MARGIN + 8.25, 2.55, 2.7, 1.0, "tools", 24, INK, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 3.4, 2.65, 0.5, 0.6, "→", 30, ACCENT, bold=True)
d.text(s, MARGIN + 7.4, 2.65, 0.5, 0.6, "→", 30, ACCENT, bold=True)
d.text(s, MARGIN + 9.3, 2.2, 2.4, 0.6, "có tool_calls", 13, MUTED)
d.text(s, MARGIN + 4.3, 3.95, 4.0, 0.5, "không có → END", 13, MUTED)
d.text(s, MARGIN + 5.4, 4.9, 4.0, 0.5, "↺ quay lại agent", 16, ACCENT, bold=True)

# --- 9. Code 02 -------------------------------------------------------------
s = d.content("Demo · 02_agent_loop.py", "Mười dòng thay cho vòng for", notes="""Chạy live với FAKE=1 để không tốn tiền, hoặc key thật.
Chỉ vào ToolNode: nó tự chạy mọi tool, tự tạo ToolMessage đúng id.
Đây là phần dễ viết sai nhất khi tự làm — nên dùng thư viện.""")
d.code(
    s,
    '''builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")     # <-- chính là vòng lặp

graph = builder.compile()''',
    top=2.0, height=3.0, size=15,
)
d.text(s, MARGIN, 5.25, CONTENT_W, 0.8, "tools_condition: có tool_calls → 'tools', không → END.", 17, MUTED)

# --- 10. So sánh ------------------------------------------------------------
s = d.content("So sánh", "Buổi 1 và buổi 2", notes="""Bảng này để học viên thấy mình không học lại từ đầu, chỉ thay từng mảnh.
Nhấn: hành vi không đổi, khả năng quan sát đổi.""")
d.table(
    s,
    ["Buổi 1", "Buổi 2"],
    [
        ["for step in range(MAX_STEPS)", "hai node nối thành vòng"],
        ["if not tool_calls: break", "tools_condition"],
        ["TOOL_FUNCTIONS[name](**args)", "ToolNode(TOOLS)"],
        ["messages.append(...) thủ công", "state tự merge"],
    ],
    top=2.1, col_widths=[6.2, 5.4], size=16, row_height=0.72,
)
d.text(s, MARGIN, 5.5, CONTENT_W, 0.7, "Cùng một hành vi. Khác ở chỗ: giờ nhìn thấy và lưu lại được từng bước.", 17, MUTED)

# --- 11. Section 3 ----------------------------------------------------------
d.section("03", "Checkpoint", "State không nằm trong RAM của bạn.", notes="""Phần này 15 phút, quan trọng nhất buổi.
Checkpoint là nền của memory, resume, human-in-the-loop và multi-user.""")

# --- 12. Code checkpoint ----------------------------------------------------
s = d.content("Demo · 03_checkpoint.py", "Một dòng bật checkpoint", notes="""Chạy live. Hỏi hai lượt cùng thread, rồi đổi thread.
Chỉ vào chỗ state tăng dần và chỗ khach-B trống.
Lưu ý: InMemorySaver mất khi tắt process. Production dùng Postgres/Redis.""")
d.code(
    s,
    '''checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "khach-A"}}

graph.invoke({"messages": [HumanMessage("Đơn 1234?")]}, config)
graph.invoke({"messages": [HumanMessage("Còn 5678?")]}, config)   # nhớ lượt trước

graph.get_state(config)          # xem state hiện tại
graph.get_state_history(config)  # xem mọi ảnh chụp''',
    top=2.0, height=3.3, size=14,
)

# --- 13. thread_id ----------------------------------------------------------
s = d.content("Định danh", "thread_id là gì?", notes="""Đây là khái niệm sẽ quay lại ở buổi 4 (memory nhiều người dùng) và buổi 9 (API).
Nếu thread_id sai, người dùng A thấy dữ liệu của B — đó là lỗi bảo mật, không chỉ là lỗi logic.""")
d.bullets(s, [
    "Là danh tính của một cuộc hội thoại, không phải của một người dùng",
    "Cùng thread_id  →  nối tiếp lịch sử",
    "Khác thread_id  →  tách biệt hoàn toàn, không thấy gì của nhau",
    "Đổi thread_id là cách rẻ nhất để bắt đầu cuộc trò chuyện mới",
], top=2.2, size=21, gap=20)

# --- 14. Ba điều về checkpoint ----------------------------------------------
s = d.content("Ghi nhớ", "Checkpoint lưu sau mỗi bước", notes="""Ba dòng này là toàn bộ phần lý thuyết checkpoint.
Nhấn: ảnh chụp sau mỗi bước, không phải sau mỗi câu trả lời — nên interrupt giữa đường vẫn resume được.""")
d.table(
    s,
    ["Điều", "Nghĩa thực tế"],
    [
        ["Lưu sau mỗi node", "Chết giữa đường vẫn resume được"],
        ["Có snapshot.next", "Graph biết bước tiếp theo là gì"],
        ["Resume không chạy lại", "Không tốn tiền gọi lại model"],
    ],
    top=2.2, col_widths=[4.0, 7.4], size=17, row_height=0.8,
)
d.text(s, MARGIN, 5.4, CONTENT_W, 0.8, "Production: đổi InMemorySaver thành Postgres/Redis — một dòng, cùng API.", 17, MUTED)

# --- 15. Section 4 ----------------------------------------------------------
d.section("04", "Streaming", "Agent im lặng 20 giây bị coi là agent hỏng.", notes="""Phần này 10 phút. Ngắn nhưng ảnh hưởng lớn tới cảm nhận người dùng.""")

# --- 16. Hai chế độ ---------------------------------------------------------
s = d.content("Demo · 04_streaming.py", "Hai chế độ stream", notes="""updates: mỗi node một event — dùng để hiện 'đang tra đơn'.
messages: từng mẩu chữ — dùng để hiện câu trả lời chạy.
Cả hai đều đi qua cùng một graph, chỉ khác cách nhìn.""")
d.table(
    s,
    ["Chế độ", "Trả về", "Dùng cho"],
    [
        ["updates", "mỗi node một event", "hiện tiến độ, tool activity"],
        ["messages", "từng mẩu chữ", "hiện câu trả lời như ChatGPT"],
    ],
    top=2.1, col_widths=[2.6, 4.2, 4.6], size=17, row_height=0.8,
)
d.code(
    s,
    '''for event in graph.stream(inputs, stream_mode="updates"):
    for node_name, update in event.items():
        print(node_name, update)

for chunk, meta in graph.stream(inputs, stream_mode="messages"):
    print(chunk.content, end="", flush=True)''',
    top=4.15, height=1.75, size=13,
)

# --- 17. Section 5 ----------------------------------------------------------
d.section("05", "Human-in-the-loop", "Biến hành động nguy hiểm thành đề nghị.", notes="""Phần này 15 phút. Đây là thứ phân biệt agent dùng được với agent đồ chơi trong môi trường thật.""")

# --- 18. Luồng interrupt ----------------------------------------------------
s = d.content("Cơ chế", "Graph dừng, không phải model hỏi", notes="""Nhấn mạnh: interrupt không phải prompt 'hãy hỏi lại người dùng'.
Model không biết gì về việc dừng. Graph dừng, state được lưu, chương trình của bạn quyết định.""")
d.panel(s, MARGIN, 2.3, 3.3, 2.3, PANEL)
d.text(s, MARGIN + 0.25, 2.5, 2.9, 0.4, "1. AGENT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.25, 2.95, 2.9, 1.4, "muốn gọi\nissue_refund", 17, INK, line_spacing=1.3)
d.panel(s, MARGIN + 3.75, 2.3, 3.3, 2.3, ACCENT_SOFT)
d.text(s, MARGIN + 4.0, 2.5, 2.9, 0.4, "2. INTERRUPT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 4.0, 2.95, 2.9, 1.4, "graph dừng\nlưu checkpoint\nchờ người duyệt", 17, INK, line_spacing=1.3)
d.panel(s, MARGIN + 7.5, 2.3, 3.3, 2.3, PANEL)
d.text(s, MARGIN + 7.75, 2.5, 2.9, 0.4, "3. RESUME", 12, ACCENT, bold=True)
d.text(s, MARGIN + 7.75, 2.95, 2.9, 1.4, "duyệt / từ chối\nchạy tiếp từ đúng chỗ", 17, INK, line_spacing=1.3)
d.text(s, MARGIN, 5.0, CONTENT_W, 0.9, "Chương trình của bạn hiện nút bấm. Model không hề biết đã có một bước dừng.", 17, MUTED)

# --- 19. Code approval ------------------------------------------------------
s = d.content("Demo · 05_human_in_the_loop.py", "Dừng ở đâu, resume thế nào", notes="""Chạy live: lần invoke đầu trả về __interrupt__, không có câu trả lời.
Sau đó gọi Command(resume='approve'). Graph chạy tiếp, không gọi lại model cho các bước trước.
Thử đổi thành 'reject' để thấy nhánh từ chối.""")
d.code(
    s,
    '''def approval_node(state):
    call = state["messages"][-1].tool_calls[0]

    decision = interrupt({                # graph DỪNG tại đây
        "tool": call["name"],
        "args": call["args"],
    })

    if decision == "approve":
        content = issue_refund.invoke(call["args"])
    else:
        content = "Người dùng đã từ chối."
    return {"messages": [ToolMessage(content, tool_call_id=call["id"])]}

# resume
graph.invoke(Command(resume="approve"), config)''',
    top=1.98, height=3.9, size=13,
)

# --- 20. Ba mức kiểm soát ---------------------------------------------------
s = d.content("Thiết kế", "Xin phép ở mức nào?", notes="""Đừng chọn mức 1 cho mọi tool — người dùng sẽ bỏ cuộc.
Đừng chọn mức 3 cho tool không hoàn tác được.
Mức 2 là mặc định tốt: chỉ những tool đổi trạng thái thật mới cần duyệt.""")
d.table(
    s,
    ["Mức", "Cách làm", "Khi nào dùng"],
    [
        ["1", "Xin phép mọi tool", "Agent mới, chưa tin được"],
        ["2", "Chỉ tool nguy hiểm", "Mặc định nên dùng"],
        ["3", "Cho chạy + audit", "Chỉ khi hoàn tác được thật"],
    ],
    top=2.15, col_widths=[1.2, 4.6, 5.6], size=17, row_height=0.82,
)
d.text(s, MARGIN, 5.45, CONTENT_W, 0.7, "Tool nguy hiểm: hoàn tiền, gửi mail, xoá file, đổi quyền.", 16, MUTED)

# --- 21. Section 6 ----------------------------------------------------------
d.section("06", "Chặn vòng lặp", "Đừng để lớp bảo vệ duy nhất là một exception.", notes="""Phần này 10 phút. Ngắn, nhưng hay bị bỏ qua nhất khi làm agent thật.""")

# --- 22. Ba lớp phanh -------------------------------------------------------
s = d.content("Demo · 06_guard_loop.py", "Ba lớp phanh", notes="""Chạy live graph hỏng trước, cho lớp thấy exception xấu.
Rồi chạy graph có phanh, thấy câu trả lời tử tế.
Điểm cần nhấn: recursion_limit chỉ là lưới an toàn cuối, không phải thiết kế.""")
d.table(
    s,
    ["Lớp", "Cơ chế", "Ưu / nhược"],
    [
        ["A", "recursion_limit", "Rẻ, nhưng người dùng nhận lỗi xấu"],
        ["B", "ngân sách bước trong state", "Tốt, cần viết câu trả lời khi hết lượt"],
        ["C", "phát hiện hành động lặp", "Bắt lặp 'thông minh', dễ báo nhầm"],
    ],
    top=2.1, col_widths=[1.0, 4.4, 6.0], size=16, row_height=0.85,
)
d.text(s, MARGIN, 5.4, CONTENT_W, 0.8, "Luôn bật A. Luôn viết B. Chỉ thêm C khi có dữ liệu cho thấy cần.", 19, NAVY, bold=True)

# --- 23. Lab ----------------------------------------------------------------
d.section("Lab", "60 phút thực hành", "Chạy, làm hỏng, sửa lại.", notes="""25 phút chạy 6 file, 35 phút chuyển mini harness sang LangGraph.
Đi vòng quanh, hỏi mỗi nhóm: nếu bỏ add_edge('tools','agent') thì sao?""")

# --- 24. Lab roadmap --------------------------------------------------------
s = d.content("Lab", "Hai phần", notes="""Phần A là đọc code có hướng dẫn. Phần B là chuyển bài cũ sang graph.
Ai xong sớm: thêm SqliteSaver để state sống qua restart.""")
d.panel(s, MARGIN, 2.2, 5.2, 2.9, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.6, 0.4, "25 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.3, 2.8, 4.6, 0.6, "Chạy 6 file", 21, NAVY, bold=True)
d.text(s, MARGIN + 0.3, 3.45, 4.6, 1.5, "Mỗi file trả lời một câu hỏi\nvề state, checkpoint, interrupt,\nhoặc vòng lặp.", 15, INK, line_spacing=1.35)

d.panel(s, MARGIN + 5.6, 2.2, 5.2, 2.9, ACCENT_SOFT)
d.text(s, MARGIN + 5.9, 2.4, 4.6, 0.4, "35 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 5.9, 2.8, 4.6, 0.6, "Nâng cấp harness", 21, NAVY, bold=True)
d.text(s, MARGIN + 5.9, 3.45, 4.6, 1.5, "Chuyển 06_mini_harness.py\nsang LangGraph: state, checkpoint,\nstreaming, một tool cần duyệt.", 15, INK, line_spacing=1.35)

# --- 25. Bài tập ------------------------------------------------------------
s = d.content("Về nhà", "Bài tập bắt buộc", notes="""Bài 1 củng cố checkpoint. Bài 3 là bài khó nhất: thêm retry cho tool hỏng.
Ai làm bài 3 xong sẽ hiểu vì sao checkpoint quan trọng.""")
d.bullets(s, [
    "Bài 1 — thêm thread thứ ba, chứng minh ba khách không thấy dữ liệu của nhau",
    "Bài 3 — tool lỗi 2 lần rồi thành công: cần retry ở đâu, state nào phải giữ?",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 3.8, CONTENT_W, 1.6, "Nộp: file đã sửa + ảnh chụp state_history chứng minh resume đúng chỗ.\nTiêu chí: giải thích được, không chỉ chạy được.", 17, MUTED, line_spacing=1.5)

# --- 26. Tổng kết -----------------------------------------------------------
s = d.content("Tổng kết", "Năm câu mang về", notes="""Đọc chậm. Dừng ở câu 5.
Câu 5 là câu sẽ quay lại suốt khóa: agent không tự quan sát, harness quan sát hộ.""")
d.bullets(s, [
    "Graph = state + node + edge. Node trả về phần state cần sửa.",
    "thread_id là danh tính hội thoại; checkpoint là ảnh chụp sau mỗi bước.",
    "Streaming là yêu cầu trải nghiệm, không phải tính năng phụ.",
    "interrupt biến hành động nguy hiểm thành đề nghị.",
    "Luôn có hai lớp chống lặp: giới hạn cứng và ngân sách bước.",
], top=2.05, size=20, gap=16)

# --- 27. Buổi sau -----------------------------------------------------------
s = d.content("Buổi 3", "Tiếp theo: Tool và MCP Engineering", notes="""Nhắc nộp bài. Buổi 3 sẽ dùng chính common/shop.py — nên đọc trước @tool và docstring.
Mời lớp đặt câu hỏi.""")
d.bullets(s, [
    "Viết tool mà model chọn đúng, gọi đúng, và không phá dữ liệu",
    "SQL read-only, sandbox, timeout, retry",
    "MCP: biến tool thành server dùng chung cho nhiều agent",
    "Least privilege, authentication và audit cho tool",
], top=2.15, size=20, gap=16)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.9, "Chuẩn bị: đọc common/shop.py, để ý vì sao mỗi tool có docstring.", 17, MUTED)

d.save()
