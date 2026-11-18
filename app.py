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
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
EDIT_MODELS = ["gemini-2.5-flash-image"]
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
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
            if res.candidates and res.candidates[0].content:
                for p in res.candidates[0].content.parts:
                    if p.inline_data:
                        out_mime = p.inline_data.mime_type or "image/png"
                        b64 = base64.b64encode(p.inline_data.data).decode("utf-8")
                        return "data:" + out_mime + ";base64," + b64, ""
        except Exception as e:
            return None, str(e)
    return None, "Model unavailable"

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
            out = {"reply": "Server error. Please try again."}
            try:
                length = int(self.headers.get("Content-Length", 0))
                d = json.loads(self.rfile.read(length).decode("utf-8"))
                msg = d.get("message", "")
                sid = d.get("session_id", "default")
                media = d.get("media")
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "").strip())

                if media and is_edit_req(msg):
                    raw_img = base64.b64decode(media["data"])
                    edited_url, err_msg = edit_photo(client, raw_img, media["mime"], msg)
                    if edited_url:
                        out = {"reply": "Here is your edited photo:", "img": edited_url}
                    else:
                        out = {"reply": "Image editing requires billing enabled on your Gemini API key (" + err_msg[:80] + "). Try asking me to describe or analyze the photo instead!"}
                else:
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
                out = {"reply": "Error: " + str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
