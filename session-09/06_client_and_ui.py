"""Bài 06 — Client và UI tối giản.

Chạy server:  uvicorn 06_client_and_ui:app --reload --port 8000
Mở:           http://localhost:8000

Chạy demo:    python 06_client_and_ui.py

Hai phần:
    1. UI: một trang HTML gọi POST /chat/stream và đọc SSE bằng fetch + reader.
       Không cần React, không cần build. Đủ để thấy luồng thật.
    2. Client: gọi API từ process khác bằng httpx, đúng cách production dùng.

Điểm cần nhớ: UI không được gọi thẳng model. Nó chỉ nói chuyện với API.
API giữ key, giữ session, giữ quyền.
"""

import json

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from common.agent import stream_answer

app = FastAPI(title="Shop Agent API", version="0.6.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shop Agent</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 720px; margin: 48px auto; padding: 0 16px; }
  h1 { font-size: 22px; }
  #log { border: 1px solid #ddd; border-radius: 10px; padding: 16px; min-height: 180px;
         white-space: pre-wrap; background: #fafafa; }
  .row { display: flex; gap: 8px; margin-top: 12px; }
  input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 8px; }
  button { padding: 10px 18px; border: 0; border-radius: 8px; background: #2F6FED; color: white; }
  button:disabled { background: #9db2ce; }
</style>
</head>
<body>
  <h1>Shop Agent</h1>
  <div id="log">Sẵn sàng.</div>
  <div class="row">
    <input id="q" placeholder="Hỏi về đơn hàng, giá, hoàn tiền..." autocomplete="off">
    <button id="send">Gửi</button>
  </div>
<script>
const log = document.getElementById('log');
const input = document.getElementById('q');
const button = document.getElementById('send');

async function send() {
  const message = input.value.trim();
  if (!message) return;
  button.disabled = true;
  log.textContent = '';
  input.value = '';

  const response = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ message })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let cut;
    while ((cut = buffer.indexOf('\\n\\n')) >= 0) {
      const block = buffer.slice(0, cut);
      buffer = buffer.slice(cut + 2);
      let event = 'message', data = '';
      for (const line of block.split('\\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim();
        if (line.startsWith('data:')) data += line.slice(5).trim();
      }
      if (event === 'token' && data) log.textContent += JSON.parse(data).text;
      if (event === 'error' && data) log.textContent += '\\n[Lỗi] ' + JSON.parse(data).message;
    }
  }
  button.disabled = false;
  input.focus();
}

button.addEventListener('click', send);
input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    async def events():
        for piece in stream_answer(request.message):
            yield {"event": "token", "data": json.dumps({"text": piece}, ensure_ascii=False)}
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(events())


async def call_from_another_process() -> None:
    """Client thật: cùng giao thức, khác process."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://api") as client:
        async with client.stream(
            "POST", "/chat/stream", json={"message": "Đơn 1234 đâu?"}
        ) as response:
            print("client nhận content-type:", response.headers["content-type"])
            text = ""
            async for line in response.aiter_lines():
                if line.startswith("data:") and "text" in line:
                    text += json.loads(line[5:].strip())["text"]
            print("client ghép lại:", text.strip())


if __name__ == "__main__":
    import asyncio

    from fastapi.testclient import TestClient

    client = TestClient(app)
    page = client.get("/")
    print("GET / ->", page.status_code, "| có tiêu đề:", "Shop Agent" in page.text)

    print("\nGọi API như một client khác:")
    asyncio.run(call_from_another_process())

    print("\nChạy thật: uvicorn 06_client_and_ui:app --reload")
    print("Mở http://localhost:8000 để dùng UI.")
