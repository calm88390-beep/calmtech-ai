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
EDIT_MODELS = ["gemini-2.5-flash-image", "gemini-2.0-flash-exp-image-generation", "gemini-2.0-flash-exp"]
SESS = {}

def is_edit_req(text):
    low = text.lower().strip()
    words = ("edit", "change", "remove", "add", "replace", "turn", "make", "put", "color", "background", "cartoon", "anime", "filter", "dress", "wear", "style")
    return any(w in low for w in words)

def edit_photo(client, img_bytes, mime_type, prompt):
    img_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
    for m in EDIT_MODELS:
        try:
            res = client.models.generate_content(
                model=m,
                contents=[img_part, prompt],
                config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
            )
            if res.candidates and res.candidates[0].content:
                for p in res.candidates[0].content.parts:
                    if p.inline_data:
                        out_mime = p.inline_data.mime_type or "image/png"
                        b64 = base64.b64encode(p.inline_data.data).decode("utf-8")
                        return "data:" + out_mime + ";base64," + b64
        except Exception:
            continue
    return None

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
            d = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
            msg, sid, media = d.get("message", ""), d.get("session_id", "default"), d.get("media")
            try:
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "").strip())
                if media and is_edit_req(msg):
                    raw_img = base64.b64decode(media["data"])
                    edited_url = edit_photo(client, raw_img, media["mime"], msg)
                    if edited_url:
                        out = {"reply": "Here is your edited photo:", "img": edited_url}
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(out).encode("utf-8"))
                        return

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
