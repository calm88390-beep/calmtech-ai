from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

CALMTECH_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "You are CALMTECH, a helpful, intelligent, and versatile AI assistant "
        "created by Samuel Frimpong. Whenever someone asks who created, built, "
        "or owns you, clearly state that you were created by Samuel Frimpong. "
        "Answer any question clearly, help users solve problems, write code, "
        "and brainstorm ideas without limitations on your knowledge. "
        "Use clear bullet points and bold headings when helpful."
    )
)

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
user_sessions = {}

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CALMTECH AI — Created by Samuel Frimpong</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 760px; margin: 0 auto; padding: 12px; background: #0f172a; color: #f8fafc; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 8px 4px; }
        h1 { color: #38bdf8; margin: 0; font-size: 22px; letter-spacing: 1.5px; }
        .badge { background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 12px; font-size: 12px; border: 1px solid #334155; }
        .ad-slot { background: #1e293b; border: 1px dashed #f59e0b; padding: 10px; text-align: center; margin: 8px 0; border-radius: 8px; font-size: 12px; color: #fbbf24; min-height: 55px; display: flex; align-items: center; justify-content: center; }
        #chat-box { background: #1e293b; height: 58vh; overflow-y: auto; padding: 16px; border-radius: 14px; border: 1px solid #334155; display: flex; flex-direction: column; gap: 12px; }
        .msg { padding: 12px 16px; border-radius: 14px; max-width: 85%; line-height: 1.5; font-size: 15px; word-wrap: break-word; white-space: pre-wrap; }
        .user { background: #2563eb; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #334155; color: #f1f5f9; align-self: flex-start; border-bottom-left-radius: 4px; }
        .thinking { font-style: italic; color: #94a3b8; }
        #input-area { display: flex; gap: 8px; margin-top: 10px; }
        input { flex: 1; padding: 13px 16px; border-radius: 24px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 15px; outline: none; }
        input:focus { border-color: #38bdf8; }
        button { padding: 12px 22px; background: #2563eb; color: white; border: none; border-radius: 24px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:disabled { background: #475569; cursor: not-allowed; }
        footer { text-align: center; font-size: 12px; color: #94a3b8; margin-top: 8px; }
    </style>
</head>
<body>
    <header>
        <h1>CALMTECH</h1>
        <span class="badge">By Samuel Frimpong</span>
    </header>

    <!-- TOP AD BANNER -->
    <div class="ad-slot" id="top-ad">CALMTECH Top Ad Space — Ready for Ad Code</div>

    <div id="chat-box">
        <div class="msg bot">Hello! I am <strong>CALMTECH</strong>, an AI assistant created by <strong>Samuel Frimpong</strong>. Ask me anything—from coding and business ideas to everyday questions!</div>
    </div>

    <div id="input-area">
        <input type="text" id="user-input" placeholder="Ask CALMTECH anything..." onkeypress="if(event.key==='Enter') sendMessage()" />
        <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>

    <!-- BOTTOM AD BANNER -->
    <div class="ad-slot" id="bottom-ad">CALMTECH Bottom Ad Space — Ready for Ad Code</div>

    <footer>Created by <strong>Samuel Frimpong</strong></footer>

    <script>
        const sessionId = "user_" + Math.random().toString(36).substring(2, 12);

        function formatText(text) {
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        }

        async function sendMessage() {
            const input = document.getElementById("user-input");
            const btn = document.getElementById("send-btn");
            const chatBox = document.getElementById("chat-box");
            const text = input.value.trim();
            if (!text || btn.disabled) return;

            input.disabled = true;
            btn.disabled = true;

            const userDiv = document.createElement("div");
            userDiv.className = "msg user";
            userDiv.textContent = text;
            chatBox.appendChild(userDiv);

            input.value = "";

            const thinkingDiv = document.createElement("div");
            thinkingDiv.className = "msg bot thinking";
            thinkingDiv.textContent = "CALMTECH is thinking...";
            chatBox.appendChild(thinkingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text, session_id: sessionId })
                });
                const data = await response.json();
                thinkingDiv.className = "msg bot";
                thinkingDiv.innerHTML = formatText(data.reply);
            } catch (err) {
                thinkingDiv.className = "msg bot";
                thinkingDiv.textContent = "Error: " + err.message;
            }

            input.disabled = false;
            btn.disabled = false;
            input.focus();
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

class CalmTechHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
            user_message = data.get("message", "")
            session_id = data.get("session_id", "default")

            if session_id not in user_sessions:
                user_sessions[session_id] = []
            history = user_sessions[session_id][-12:]

            history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
            ai_reply = "Servers are momentarily busy. Please try again in a few seconds."

            for model_name in MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=history,
                        config=CALMTECH_CONFIG
                    )
                    ai_reply = response.text
                    history.append(types.Content(role="model", parts=[types.Part.from_text(text=ai_reply)]))
                    user_sessions[session_id] = history
                    break
                except Exception as e:
                    if "503" in str(e) or "429" in str(e):
                        continue
                    ai_reply = f"Connection error: {str(e)}"
                    break

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": ai_reply}).encode("utf-8"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(("0.0.0.0", port), CalmTechHandler)
    print(f"CALMTECH is live on port {port}!")
    server.serve_forever()
