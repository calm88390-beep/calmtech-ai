from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from groq import Groq

SYS_PROMPT = (
    "You are CALMTECH, a fast, helpful AI assistant. Current year: 2026. "
    "The current President of Ghana is John Dramani Mahama (inaugurated January 7, 2025), and the Vice President is Jane Naana Opoku-Agyemang. "
    "NEVER introduce yourself, say your name, or mention your creator unless asked who created, built, or owns you. "
    "If asked who created, built, or owns you, state that you were created by Samuel Frimpong. "
    "Give clear, direct, helpful answers, analyze uploaded images in detail, and share full clickable URLs like https://example.com when helpful."
)
SESS = {}

def ask_groq(hist, media):
    key = "".join(os.environ.get("GROQ_API_KEY", "").split())
    if not key.startswith("gsk_"):
        return "Your GROQ_API_KEY on Render does not look right (it should start with gsk_). Please double-check it in Render Environment settings."

    client = Groq(api_key=key)
    msgs = [{"role": "system", "content": SYS_PROMPT}]
    for h in hist[:-1]:
        msgs.append({"role": h["role"], "content": h["text"]})
    last_text = hist[-1]["text"]

    if media:
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
        data_url = "data:" + media["mime"] + ";base64," + media["data"]
        msgs.append({
            "role": "user",
            "content": [
                {"type": "text", "text": last_text},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        })
    else:
        model = "llama-3.3-70b-versatile"
        msgs.append({"role": "user", "content": last_text})

    res = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=0.7
    )
    return res.choices[0].message.content

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
            out = {"reply": "Servers are busy. Please try again."}
            try:
                length = int(self.headers.get("Content-Length", 0))
                d = json.loads(self.rfile.read(length).decode("utf-8"))
                msg = d.get("message", "")
                sid = d.get("session_id", "default")
                media = d.get("media")
                hist = SESS.setdefault(sid, [])[-8:]
                hist.append({"role": "user", "text": msg})

                if os.environ.get("GROQ_API_KEY", "").strip():
                    reply = ask_groq(hist, media)
                else:
                    reply = "Please add your free GROQ_API_KEY in Render Environment variables for ultra-fast replies!"

                hist.append({"role": "assistant", "text": reply})
                SESS[sid] = hist
                out = {"reply": reply}
            except Exception as e:
                out = {"reply": "Connection error: " + str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
