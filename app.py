from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
from google import genai
from google.genai import types

CFG = types.GenerateContentConfig(
    system_instruction=(
        "You are CALMTECH, a helpful AI assistant. Current year: 2026. "
        "The current President of Ghana is John Dramani Mahama (inaugurated January 7, 2025), and the Vice President is Jane Naana Opoku-Agyemang. "
        "NEVER introduce yourself, say your name, or mention your creator unless asked who created, built, or owns you. "
        "If asked who created, built, or owns you, state that you were created by Samuel Frimpong. "
        "Analyze uploaded images in detail, answer questions accurately, and share full clickable URLs like https://example.com when helpful."
    )
)
MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
SESS = {}
USERS = {}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        with open("index.html", "rb") as f:
            html = f.read()
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html)

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        d = json.loads(self.rfile.read(length).decode("utf-8"))

        if self.path == "/auth":
            mode = d.get("mode", "in")
            em = d.get("email", "").strip().lower()
            pw = d.get("pass", "")
            nm = d.get("name", "").strip()
            if not em or not pw:
                out = {"ok": False, "msg": "Please enter both email and password."}
            elif mode == "up":
                if not nm:
                    out = {"ok": False, "msg": "Please enter your full name."}
                elif em in USERS:
                    out = {"ok": False, "msg": "Email already registered. Please Log In."}
                else:
                    USERS[em] = {"name": nm, "pass": pw}
                    out = {"ok": True, "name": nm, "email": em}
            else:
                if em not in USERS or USERS[em]["pass"] != pw:
                    out = {"ok": False, "msg": "Invalid email or password. Try Sign Up first!"}
                else:
                    out = {"ok": True, "name": USERS[em]["name"], "email": em}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))
            return

        if self.path == "/chat":
            msg, sid, media = d.get("message", ""), d.get("session_id", "default"), d.get("media")
            try:
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "").strip())
                hist = SESS.setdefault(sid, [])[-10:]
                parts = [types.Part.from_bytes(data=base64.b64decode(media["data"]), mime_type=media["mime"])] if media else []
                parts.append(types.Part.from_text(text=msg))
                hist.append(types.Content(role="user", parts=parts))
                reply = "Servers are busy. Please try again in a moment."
                for m in MODELS:
                    try:
                        res = client.models.generate_content(model=m, contents=hist, config=CFG)
                        reply = res.text
                        hist[-1] = types.Content(role="user", parts=[types.Part.from_text(text=msg)])
                        hist.append(types.Content(role="model", parts=[types.Part.from_text(text=reply)]))
                        SESS[sid] = hist
                        break
                    except Exception as e:
                        if "503" in str(e) or "429" in str(e):
                            continue
                        reply = "Connection error: " + str(e)
                        break
                out = {"reply": reply}
            except Exception as e:
                out = {"reply": "Configuration error: " + str(e)}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
