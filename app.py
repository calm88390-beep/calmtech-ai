from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
from google import genai
from google.genai import types

CFG = types.GenerateContentConfig(
    system_instruction=(
        "You are CALMTECH, a fast, helpful AI assistant. Current year: 2026. "
        "The current President of Ghana is John Dramani Mahama (inaugurated January 7, 2025), and the Vice President is Jane Naana Opoku-Agyemang. "
        "NEVER introduce yourself, say your name, or mention your creator unless asked who created, built, or owns you. "
        "If asked who created, built, or owns you, state that you were created by Samuel Frimpong. "
        "Give clear, direct, helpful answers, analyze uploaded images in detail, and share full clickable URLs like https://example.com when helpful."
    ),
    thinking_config=types.ThinkingConfig(thinking_budget=0)
)
MODELS = ["gemini-3.8-flash"]
SESS = {}
CLIENT = None

def get_client():
    global CLIENT
    if CLIENT is None:
        CLIENT = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "").strip())
    return CLIENT

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/google8163534a1c5e7fe2.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"google-site-verification: google8163534a1c5e7fe2.html")
            return
        with open("index.html", "rb") as f:
            html = f.read()
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html)

    def do_POST(self):
        if self.path == "/chat":
            try:
                length = int(self.headers.get("Content-Length", 0))
                d = json.loads(self.rfile.read(length).decode("utf-8"))
                msg = d.get("message", "")
                sid = d.get("session_id", "default")
                media = d.get("media")
                client = get_client()

                hist = SESS.setdefault(sid, [])[-6:]
                parts = [types.Part.from_bytes(data=base64.b64decode(media["data"]), mime_type=media["mime"])] if media else []
                parts.append(types.Part.from_text(text=msg))
                hist.append(types.Content(role="user", parts=parts))

                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()

                full_reply = ""
                for chunk in client.models.generate_content_stream(model=MODELS[0], contents=hist, config=CFG):
                    if chunk.text:
                        full_reply += chunk.text
                        self.wfile.write(chunk.text.encode("utf-8"))
                        self.wfile.flush()

                hist[-1] = types.Content(role="user", parts=[types.Part.from_text(text=msg)])
                hist.append(types.Content(role="model", parts=[types.Part.from_text(text=full_reply)]))
                SESS[sid] = hist
            except Exception as e:
                try:
                    self.wfile.write(("Error: " + str(e)).encode("utf-8"))
                except Exception:
                    pass

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
