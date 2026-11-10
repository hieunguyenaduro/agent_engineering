"""Tạo slide Buổi 6.

Chạy:  python slides/build_slides.py   (cần python-pptx)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from pptx.enum.text import PP_ALIGN  # noqa: E402
from deck import (  # noqa: E402
    ACCENT, ACCENT_SOFT, CONTENT_W, INK, MARGIN, MUTED, NAVY, PANEL, WHITE, Deck,
)

d = Deck(session="Agent Engineering · Buổi 6", out=Path(__file__).with_name("slides.pptx"))

# --- 1. Bìa -----------------------------------------------------------------
d.title(
    "Agent Engineering · Buổi 6/10",
    "Multi-agent\nSystems",
    "Subagent · Supervisor · Song song · Handoff",
    "120 phút · 55 phút lý thuyết & demo · 60 phút thực hành",
    notes="""Buổi trước agent có một kho tri thức. Hôm nay tách nó thành nhiều agent.
Câu hỏi mở đầu: khi nào nhiều agent tốt hơn một agent? Không phải lúc nào cũng tốt.
Ba kiểu quan hệ sẽ học: gọi như tool, supervisor điều phối, handoff chuyển quyền.""",
)

# --- 2. Statement -----------------------------------------------------------
d.statement(
    "Nguyên tắc",
    "Multi-agent là cách\nchia việc, không phải\ncách thông minh hơn.",
    "Tách đúng thì nhanh và rõ. Tách sai thì chậm hơn, đắt hơn,\nkhó debug hơn — mà vẫn trả lời sai.",
    notes="""Câu này lặp lại ở cuối buổi. Đừng để lớp nghĩ nhiều agent luôn tốt hơn.
Tách chỉ có lợi khi có lý do cụ thể: prompt quá tải, tool quá nhiều, việc song song được, hoặc cần chuyển ca.""",
)

# --- 3. Khi nào tách --------------------------------------------------------
s = d.content("Quyết định", "Bốn dấu hiệu nên tách", notes="""Hỏi lớp: agent hiện tại của bạn có mấy tool? Nếu hơn 10, đó là dấu hiệu đầu tiên.
Mỗi dòng là một lý do kỹ thuật, không phải sở thích.
Nếu không có dòng nào đúng, đừng tách.""")
d.table(
    s,
    ["Dấu hiệu", "Vì sao tách"],
    [
        ["Một prompt phải làm 3–4 việc", "Mỗi agent một nhiệm vụ, prompt ngắn hơn"],
        ["Mỗi việc cần bộ tool riêng", "Giảm số tool model phải chọn"],
        ["Các việc chạy song song được", "Giảm thời gian chờ"],
        ["Cần chuyển cho người/bộ phận", "Handoff giữ nguyên ngữ cảnh"],
    ],
    top=2.1, col_widths=[5.0, 6.6], size=17, row_height=0.8,
)

# --- 4. Section 1 -----------------------------------------------------------
d.section("01", "Subagent như một tool", "Cách tách rẻ nhất, nên thử đầu tiên.", notes="""Phần này 12 phút. Đây là kiểu tách đơn giản nhất và hay được dùng nhất trong thực tế.
Graph con được bọc trong một hàm @tool.""")

# --- 5. Sơ đồ subagent ------------------------------------------------------
s = d.content("Cấu trúc", "Một graph lồng trong một tool", notes="""Vẽ lên bảng: graph chính ở trên, graph con ở dưới, nối bằng một mũi tên tool.
Agent chính không thấy bên trong. Nó chỉ thấy input/output.
Đây chính là encapsulation.""")
d.panel(s, MARGIN, 2.2, 3.3, 1.6, ACCENT_SOFT)
d.text(s, MARGIN + 0.25, 2.45, 2.8, 0.5, "agent chính", 20, NAVY, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 0.25, 3.0, 2.8, 0.5, "chỉ thấy tool", 14, MUTED, align=PP_ALIGN.CENTER)

d.text(s, MARGIN + 3.6, 2.6, 1.2, 0.7, "→", 34, ACCENT, bold=True)

d.panel(s, MARGIN + 4.9, 2.2, 3.3, 1.6, PANEL)
d.text(s, MARGIN + 5.15, 2.45, 2.8, 0.5, "tools", 20, INK, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 5.15, 3.0, 2.8, 0.5, "research(query)", 14, MUTED, align=PP_ALIGN.CENTER)

d.text(s, MARGIN + 3.6, 4.15, 1.2, 0.7, "↓", 34, ACCENT, bold=True)

d.panel(s, MARGIN + 4.9, 4.55, 3.3, 1.7, NAVY)
d.text(s, MARGIN + 5.15, 4.75, 2.8, 0.5, "graph con", 18, WHITE, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 5.15, 5.3, 2.8, 0.7, "gather → summarize", 14, "9DB2CE", align=PP_ALIGN.CENTER)
d.text(s, MARGIN, 5.35, 4.4, 1.0, "Bên trong có thể là\n5 bước, 3 tool, 2 model.\nBên ngoài chỉ là một hàm.", 15, MUTED, line_spacing=1.4)

# --- 6. Code subagent -------------------------------------------------------
s = d.content("Demo · 01_subagent_as_tool.py", "Bọc graph con bằng @tool", notes="""Chạy live. Chỉ vào ba dòng: compile, @tool, invoke.
Nhấn: invoke là ranh giới. Mọi thứ bên trong không rò ra ngoài trừ chuỗi trả về.
Đây là chỗ dễ đặt log và đo chi phí nhất.""")
d.code(
    s,
    '''researcher = research_builder.compile()

@tool
def research(query: str) -> str:
    """Giao câu hỏi cho subagent và nhận báo cáo ngắn."""
    result = researcher.invoke({
        "query": query, "notes": [], "report": "",
    })
    return result["report"]''',
    top=2.0, height=2.75, size=15,
)
d.text(s, MARGIN, 5.05, CONTENT_W, 0.9, "Với agent chính, subagent chỉ là function nhận chuỗi, trả chuỗi.", 17, MUTED)

# --- 7. Được và mất ---------------------------------------------------------
s = d.content("Đánh đổi", "Subagent-as-tool được gì, mất gì?", notes="""Được: tách biệt, dễ test, thay subagent không sửa agent chính.
Mất: thêm một lần gọi model, và kết quả trả về phải tự đủ nghĩa.
Nếu kết quả không đủ nghĩa, agent chính sẽ hỏi lại — tốn thêm lần nữa.""")
d.table(
    s,
    ["Được", "Mất"],
    [
        ["Tách biệt hoàn toàn, dễ test", "Không thấy bên trong nếu không log"],
        ["Agent chính không bị nhiễu tool", "Thêm một lần gọi model"],
        ["Thay subagent không sửa agent chính", "Kết quả trả về phải tự đủ nghĩa"],
    ],
    top=2.1, col_widths=[5.8, 5.8], size=17, row_height=0.85,
)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.8, "Nếu kết quả không đủ nghĩa, agent chính sẽ hỏi lại — tốn thêm một vòng.", 17, MUTED)

# --- 8. Section 2 -----------------------------------------------------------
d.section("02", "Supervisor", "Một agent chỉ làm một việc: chọn đúng người.", notes="""Phần này 12 phút. Supervisor là pattern phổ biến nhất khi có 3+ agent.
Điểm dễ sai: supervisor tự làm việc thay vì chỉ định tuyến.""")

# --- 9. Sơ đồ supervisor ----------------------------------------------------
s = d.content("Cấu trúc", "Supervisor không tự trả lời", notes="""Vẽ: supervisor ở giữa, ba worker xung quanh, một node tổng hợp.
Mũi tên từ supervisor là quyết định, không phải công việc.
Hỏi lớp: nếu supervisor tự trả lời thì sao? Nó thành agent ôm đồm — mất lý do tách.""")
d.panel(s, MARGIN + 3.6, 2.2, 3.4, 1.3, NAVY)
d.text(s, MARGIN + 3.85, 2.45, 2.9, 0.5, "supervisor", 20, WHITE, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 3.85, 2.95, 2.9, 0.4, "chọn người + ghi lý do", 12, "9DB2CE", align=PP_ALIGN.CENTER)

for i, (name, color) in enumerate([("billing", ACCENT_SOFT), ("technical", PANEL), ("general", PANEL)]):
    x = MARGIN + i * 3.9
    d.panel(s, x, 4.3, 3.4, 1.3, color)
    d.text(s, x + 0.2, 4.55, 3.0, 0.5, name, 18, INK, bold=True, align=PP_ALIGN.CENTER)
    d.text(s, x + 0.2, 5.0, 3.0, 0.4, "worker", 12, MUTED, align=PP_ALIGN.CENTER)

d.text(s, MARGIN + 3.6, 3.65, 3.4, 0.4, "↓  ↓  ↓", 22, ACCENT, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 8.6, 5.95, 3.4, 0.5, "→ summarize → END", 13, MUTED)

# --- 10. Code supervisor ----------------------------------------------------
s = d.content("Demo · 02_supervisor.py", "Định tuyến là một quyết định có ghi vết", notes="""Chạy live ba câu, chỉ vào log: ai nhận, vì sao.
Nhấn dòng return: supervisor chỉ trả route và log, không trả answer.
Production thay if/else bằng LLM structured output, code xung quanh giữ nguyên.""")
d.code(
    s,
    '''class Route(BaseModel):
    route: Literal["billing", "technical", "general"]
    reason: str

def supervisor(state):
    decision = llm.with_structured_output(Route).invoke([
        SystemMessage("Chọn bộ phận phù hợp. Không tự trả lời."),
        HumanMessage(state["task"]),
    ])
    return {"route": decision.route, "log": [decision.reason]}''',
    top=2.0, height=3.0, size=14,
)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.8, "Trong file demo, phần này là if/else để bạn thấy rõ logic — không có gì huyền bí.", 16, MUTED)

# --- 11. Ba nguyên tắc ------------------------------------------------------
s = d.content("Thiết kế", "Ba nguyên tắc cho supervisor", notes="""Một: không tự làm việc. Hai: luôn có fallback. Ba: ghi lại quyết định.
Fallback là dòng dễ bỏ nhất và gây lỗi lặng lẽ nhất — câu hỏi lạ rơi vào hư không.
Log là thứ giúp debug khi agent trả lời sai.""")
d.bullets(s, [
    "Không tự làm việc — chỉ chọn người và ghi lý do",
    "Luôn có nhánh fallback cho câu hỏi ngoài phạm vi",
    "Ghi lại quyết định: ai nhận, vì sao, lúc nào",
    "Không để supervisor gọi chính nó — đó là dấu hiệu nó đang làm việc của worker",
], top=2.2, size=21, gap=20)

# --- 12. Section 3 ----------------------------------------------------------
d.section("03", "Chạy song song", "Send, reducer, defer — và một cái bẫy async.", notes="""Phần này 12 phút. Đây là phần kỹ thuật nhất buổi.
Ba khái niệm: reducer, Send, defer. Thiếu cái nào cũng sai.""")

# --- 13. Sơ đồ Send ---------------------------------------------------------
s = d.content("Cơ chế", "Một supervisor, ba nhánh", notes="""Vẽ: supervisor phát ba Send, ba worker chạy, aggregate gộp một lần.
Nhấn defer=True: nếu không có, aggregate chạy sau từng worker.
Reducer operator.add là thứ cho phép ba worker cùng ghi vào findings.""")
d.panel(s, MARGIN, 2.2, 2.4, 1.2, NAVY)
d.text(s, MARGIN + 0.2, 2.45, 2.0, 0.5, "supervisor", 15, WHITE, bold=True, align=PP_ALIGN.CENTER)

for i, label in enumerate(["pricing", "policy", "technical"]):
    y = 1.95 + i * 1.25
    d.panel(s, MARGIN + 4.6, y, 2.8, 1.0, PANEL)
    d.text(s, MARGIN + 4.8, y + 0.25, 2.4, 0.5, label, 16, INK, bold=True, align=PP_ALIGN.CENTER)
    d.text(s, MARGIN + 2.55, y + 0.25, 1.9, 0.5, "Send →", 14, ACCENT, bold=True)

d.panel(s, MARGIN + 8.7, 2.9, 2.6, 1.5, ACCENT_SOFT)
d.text(s, MARGIN + 8.9, 3.2, 2.2, 0.5, "aggregate", 16, NAVY, bold=True, align=PP_ALIGN.CENTER)
d.text(s, MARGIN + 8.9, 3.7, 2.2, 0.5, "chạy 1 lần", 12, MUTED, align=PP_ALIGN.CENTER)
d.text(s, MARGIN, 5.85, CONTENT_W, 0.6, "Ba worker ghi vào cùng một list nhờ reducer — không ghi đè nhau.", 16, MUTED)

# --- 14. Code Send ----------------------------------------------------------
s = d.content("Demo · 03_parallel_fanout.py", "Ba dòng quyết định", notes="""Chỉ vào ba chỗ: Annotated list operator.add, Send trong fan_out, defer=True ở aggregate.
Hỏi lớp: bỏ defer thì aggregate chạy mấy lần? Trả lời: một lần mỗi worker xong.
Đây là lỗi rất khó thấy vì output cuối có thể vẫn đúng.""")
d.code(
    s,
    '''class State(TypedDict):
    findings: Annotated[list[str], operator.add]   # 1. reducer

def fan_out(state):
    return [Send("worker", {"topic": t}) for t in state["topics"]]  # 2. Send

builder.add_node("aggregate", aggregate, defer=True)   # 3. chạy 1 lần
builder.add_conditional_edges("supervisor", fan_out, ["worker"])
builder.add_edge("worker", "aggregate")''',
    top=2.0, height=2.95, size=14,
)

# --- 15. Cái bẫy async ------------------------------------------------------
s = d.content("Cái bẫy", "Send không tự làm code chạy song song", notes="""Đây là hiểu nhầm phổ biến nhất. Send tạo nhánh logic, nhưng hàm sync chạy lần lượt.
Muốn thật song song: async def + ainvoke.
Chỉ vào số đo trong file: 0.32s cho 3 nhánh 0.3s, so với 0.9s tuần tự.
Nếu thấy 0.9s, kiểm tra lại worker có async không.""")
d.table(
    s,
    ["Cách viết", "Send tạo nhánh", "Chạy thật song song"],
    [
        ["def worker + invoke", "Có", "Không — chạy lần lượt"],
        ["async def worker + ainvoke", "Có", "Có"],
    ],
    top=2.1, col_widths=[4.8, 3.4, 3.4], size=17, row_height=0.85,
)
d.code(
    s,
    '''async def worker(state):
    await asyncio.sleep(0.3)
    return {"findings": [...]}

result = asyncio.run(graph.ainvoke(inputs))''',
    top=4.2, height=1.65, size=14,
)

# --- 16. Section 4 ----------------------------------------------------------
d.section("04", "Handoff", "Chuyển ca, không phải chuyển việc.", notes="""Phần này 12 phút. Handoff khác subagent ở chỗ: agent sau tiếp tục hội thoại.
Dùng khi cần chuyển hẳn cho bộ phận khác, không quay lại.""")

# --- 17. Code handoff -------------------------------------------------------
s = d.content("Demo · 04_handoff.py", "Command: vừa chuyển node, vừa ghi state", notes="""Chạy live. Chỉ vào chuỗi handoff in ra ở cuối.
Nhấn: refund_agent đọc toàn bộ messages, nên không hỏi lại khách.
Command là một bước nguyên tử: không có khoảng trống giữa 'chuyển' và 'ghi state'.""")
d.code(
    s,
    '''from langgraph.types import Command

def triage(state) -> Command[Literal["billing_agent", "technical_agent"]]:
    target = "billing_agent" if "hoàn tiền" in state["messages"][0].content else "technical_agent"

    return Command(
        goto=target,
        update={
            "assigned_to": target,
            "messages": [AIMessage(content=f"[triage] Chuyển tới {target}.")],
        },
    )''',
    top=1.95, height=3.8, size=13,
)

# --- 18. So sánh ------------------------------------------------------------
s = d.content("So sánh", "Subagent và handoff", notes="""Bảng này là câu trả lời cho 'khi nào dùng cái nào'.
Subagent: việc phụ, lấy dữ liệu, agent chính vẫn nói câu cuối.
Handoff: chuyển hẳn ca, agent sau nói câu cuối, giữ toàn bộ ngữ cảnh.
Không có cái nào tốt hơn — chỉ có cái phù hợp hơn.""")
d.table(
    s,
    ["", "Subagent as tool", "Handoff"],
    [
        ["Ai nói câu cuối", "Agent gọi", "Agent được chuyển tới"],
        ["Ngữ cảnh", "Chỉ tham số truyền vào", "Toàn bộ messages"],
        ["Quay lại agent cũ", "Có", "Không"],
        ["Dùng khi", "Việc phụ, lấy dữ liệu", "Chuyển hẳn ca làm việc"],
    ],
    top=2.1, col_widths=[3.0, 4.6, 4.6], size=16, row_height=0.75,
)

# --- 19. Cảnh báo vòng lặp --------------------------------------------------
s = d.content("Cảnh báo", "Handoff có thể thành vòng lặp", notes="""A chuyển B, B chuyển A — graph không dừng.
Luôn đếm số handoff trong state và có luật dừng.
Bài tập 5 yêu cầu làm đúng việc này.
Đây là lỗi production thật, không phải ví dụ lý thuyết.""")
d.bullets(s, [
    "A → B → A → B ... nếu không có luật dừng",
    "Đếm tổng số handoff trong state, đặt trần cứng",
    "Mỗi agent chỉ được handoff một lần, hoặc chuyển người thật",
    "Ghi log mọi lần chuyển — vòng lặp thường lộ ra ở log",
], top=2.2, size=21, gap=20)

# --- 20. Section 5 ----------------------------------------------------------
d.section("05", "Một nhánh chết", "Cả câu trả lời không được chết.", notes="""Phần này 10 phút. Đây là phần phân biệt demo với production.
Multi-agent làm tăng số thứ có thể hỏng: worker, tool, API, timeout.""")

# --- 21. Code xử lý lỗi -----------------------------------------------------
s = d.content("Demo · 05_partial_failure.py", "Biến lỗi thành dữ liệu", notes="""Chạy live. Chỉ vào hai dòng errors: refund lỗi, legacy timeout.
Nhấn: worker tự bắt lỗi của mình, không để bay lên.
Aggregator quyết định trả lời một phần hay báo lỗi toàn bộ — tuỳ loại câu hỏi.""")
d.code(
    s,
    '''async def worker(state):
    topic = state["topic"]
    try:
        answer = await asyncio.wait_for(call_service(topic), timeout=TIMEOUT)
        return {"findings": [f"[{topic}] {answer}"]}
    except asyncio.TimeoutError:
        return {"errors": [f"[{topic}] timeout sau {TIMEOUT}s"]}
    except Exception as exc:
        return {"errors": [f"[{topic}] lỗi: {exc}"]}''',
    top=2.0, height=3.0, size=14,
)
d.text(s, MARGIN, 5.25, CONTENT_W, 0.8, "Worker không được phép làm sập cả request vì một dịch vụ ngoài.", 17, MUTED)

# --- 22. Ba mức xử lý lỗi ---------------------------------------------------
s = d.content("Thiết kế", "Ba mức xử lý lỗi", notes="""Mức 1 không chấp nhận được: người dùng nhận 500 và không biết gì.
Mức 2 là mặc định: trả lời phần lấy được, ghi rõ phần thiếu.
Mức 3 chỉ khi biết chắc lỗi tạm thời và có nguồn dự phòng.
Đừng retry vô hạn — ba lần rồi bỏ.""")
d.table(
    s,
    ["Mức", "Cách làm", "Khi nào dùng"],
    [
        ["1", "Để exception bay lên", "Không bao giờ"],
        ["2", "Bắt lỗi, trả lời một phần", "Mặc định cho agent nhiều nguồn"],
        ["3", "Retry + fallback", "Khi biết chắc lỗi tạm thời"],
    ],
    top=2.15, col_widths=[1.2, 4.8, 5.6], size=17, row_height=0.85,
)

# --- 23. Section 6 ----------------------------------------------------------
d.section("06", "Chi phí", "Không đo thì không biết mình đang mua gì.", notes="""Phần này 8 phút. Ngắn nhưng hay bị bỏ qua.
Mỗi lần giao việc là một lần gọi model. Ba worker + aggregator = bốn lần.""")

# --- 24. Budget code --------------------------------------------------------
s = d.content("Demo · 06_cost_budget.py", "Đếm trước khi phát việc", notes="""Chỉ vào chỗ giữ slot cho aggregate. Đây là lỗi thiết kế rất dễ mắc.
Nếu worker ăn hết ngân sách, bước tổng hợp vượt trần — và bạn không có câu trả lời.
Hỏi lớp: nên đặt trần theo số lần gọi hay theo USD? Trả lời: cả hai, tuỳ rủi ro.""")
d.code(
    s,
    '''@dataclass
class Budget:
    max_calls: int
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

def supervisor(state):
    remaining = max(0, BUDGET.max_calls - BUDGET.calls - 1)  # giữ 1 slot
    return {"topics": TOPICS[:remaining], "skipped": TOPICS[remaining:]}

def worker(state):
    BUDGET.charge(f"worker:{state['topic']}", prompt_tokens, completion_tokens)''',
    top=1.95, height=4.35, size=13,
)

# --- 25. Đọc bảng chi phí ---------------------------------------------------
s = d.content("Đọc kết quả", "Ba con số cần nhìn", notes="""Số lần gọi tăng tuyến tính — dễ đoán nhất.
Token: mỗi worker mang ngữ cảnh riêng, không chia sẻ.
USD: chỉ là ước lượng, giá thật phải kiểm tra lại.
Với tác vụ nhỏ multi-agent có thể rẻ hơn; với tác vụ lớn thường đắt hơn. Phải đo.""")
d.table(
    s,
    ["Con số", "Nói gì"],
    [
        ["Số lần gọi", "Tăng tuyến tính theo số worker"],
        ["Token", "Mỗi worker mang ngữ cảnh riêng, không chia sẻ"],
        ["USD", "Ước lượng — luôn kiểm tra lại bảng giá hiện hành"],
    ],
    top=2.15, col_widths=[3.2, 8.4], size=17, row_height=0.85,
)
d.text(s, MARGIN, 5.2, CONTENT_W, 0.9, "Không có câu trả lời chung: đo trên workload của bạn trước khi chọn kiến trúc.", 17, MUTED)

# --- 26. Lab ----------------------------------------------------------------
d.section("Lab", "60 phút thực hành", "Tách agent của bạn thành hai.", notes="""25 phút chạy 6 file, 35 phút tách agent buổi 5 thành researcher + responder.
Đi vòng quanh, hỏi mỗi nhóm: vì sao chọn subagent hay handoff?""")

# --- 27. Lab roadmap --------------------------------------------------------
s = d.content("Lab", "Hai phần", notes="""Phần A đọc code. Phần B là bài thật: tách agent của bạn.
Yêu cầu tối thiểu: log ai nhận việc, xử lý khi researcher không có dữ liệu, đếm số lần gọi model.
Ai xong sớm: thử chạy song song researcher và responder nếu độc lập.""")
d.panel(s, MARGIN, 2.2, 5.2, 2.9, PANEL)
d.text(s, MARGIN + 0.3, 2.4, 4.6, 0.4, "25 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 0.3, 2.8, 4.6, 0.6, "Chạy 6 file", 21, NAVY, bold=True)
d.text(s, MARGIN + 0.3, 3.45, 4.6, 1.5, "Mỗi file trả lời một câu hỏi\nvề tách việc, song song,\nhandoff hoặc chi phí.", 15, INK, line_spacing=1.35)

d.panel(s, MARGIN + 5.6, 2.2, 5.2, 2.9, ACCENT_SOFT)
d.text(s, MARGIN + 5.9, 2.4, 4.6, 0.4, "35 PHÚT", 12, ACCENT, bold=True)
d.text(s, MARGIN + 5.9, 2.8, 4.6, 0.6, "Tách agent của bạn", 21, NAVY, bold=True)
d.text(s, MARGIN + 5.9, 3.45, 4.6, 1.5, "Researcher + responder.\nChọn subagent hoặc handoff,\nghi lại vì sao.", 15, INK, line_spacing=1.35)

# --- 28. Bài tập ------------------------------------------------------------
s = d.content("Về nhà", "Bài tập bắt buộc", notes="""Bài 1 đo chi phí thật. Bài 4 là bài quan trọng nhất: hai cách xử lý lỗi.
Ai làm bài 4 xong sẽ hiểu vì sao 'partial result' là một quyết định sản phẩm, không chỉ là kỹ thuật.""")
d.bullets(s, [
    "Bài 1 — đếm số lần gọi model của một câu hỏi, bằng số thật",
    "Bài 4 — cùng input, hai chế độ partial và strict, giải thích khi nào dùng cái nào",
], top=2.2, size=21, gap=20)
d.text(s, MARGIN, 3.8, CONTENT_W, 1.6, "Nộp: bảng số + giải thích lựa chọn kiến trúc.\nTiêu chí: giải thích được, không chỉ chạy được.", 17, MUTED, line_spacing=1.5)

# --- 29. Tổng kết -----------------------------------------------------------
s = d.content("Tổng kết", "Năm câu mang về", notes="""Đọc chậm. Dừng ở câu 4 — câu async là câu hay bị hiểu sai nhất.
Câu 5 là câu nối sang buổi 7: lỗi và chi phí phải đo được.""")
d.bullets(s, [
    "Multi-agent là cách chia việc, không phải cách thông minh hơn.",
    "Subagent-as-tool là kiểu tách rẻ nhất; handoff khi cần giữ hội thoại.",
    "Supervisor chỉ chọn người, luôn có fallback và ghi lý do.",
    "Song song chỉ thật khi worker async; defer=True để tổng hợp một lần.",
    "Lỗi của một nhánh là dữ liệu; chi phí phải được đo trước khi nhân bản.",
], top=2.05, size=20, gap=16)

# --- 30. Buổi sau -----------------------------------------------------------
s = d.content("Buổi 7", "Tiếp theo: Observability và Evaluation", notes="""Nhắc nộp bài. Buổi 7 trả lời: làm sao biết agent tốt lên hay tệ đi, bằng số.
Mang theo một failure case thật.
Mời lớp đặt câu hỏi.""")
d.bullets(s, [
    "Trace theo từng bước: ai gọi ai, mất bao lâu, tốn bao nhiêu",
    "Eval dataset từ failure case thật",
    "Code evaluator, LLM-as-judge, human review",
    "Regression: chặn merge khi chất lượng tụt",
], top=2.15, size=20, gap=16)
d.text(s, MARGIN, 5.3, CONTENT_W, 0.9, "Chuẩn bị: ghi lại một câu agent của bạn từng trả lời sai.", 17, MUTED)

d.save()
