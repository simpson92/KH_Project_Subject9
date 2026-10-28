from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()


html = """
<!DOCTYPE html>
<html>
  <head><title>Chat</title></head>
  <body>
    <h1>WebSocket Chat</h1>
    <form action="" onsubmit="sendMessage(event)">
        <input type="text" id="messageText" autocomplete="off"/>
        <button>Send</button>
    </form>
    <ul id='messages'></ul>

    <script>
        // 서버의 /ws 주소로 WebSocket 연결 (한 번 연결하면 계속 유지)
        const ws = new WebSocket("ws://localhost:8000/ws");

        // 서버가 보낸 메시지를 받으면 목록에 한 줄 추가
        ws.onmessage = function(event) {
            const messages = document.getElementById('messages');
            const message = document.createElement('li');
            message.appendChild(document.createTextNode(event.data));
            messages.appendChild(message);
        };

        // Send 버튼 → 입력한 글자를 서버로 전송
        function sendMessage(event) {
            const input = document.getElementById("messageText");
            ws.send(input.value);
            input.value = '';
            event.preventDefault();   // 페이지 새로고침 막기
        }
    </script>
  </body>
</html>
"""


# http://127.0.0.1:8000/ 에 접속하면 위 HTML을 돌려줌 (교재 4️⃣)
@app.get("/")
async def get():
    return HTMLResponse(html)


# WebSocket 연결 주소: ws://localhost:8000/ws (교재 2️⃣)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()                     # 연결 요청 수락
    while True:
        data = await websocket.receive_text()    # 메시지가 올 때까지 기다림
        await websocket.send_text(f"Message text was: {data}")   # 그대로 되돌려 줌 (Echo)