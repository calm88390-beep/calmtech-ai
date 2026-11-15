from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
import random
import urllib.parse
import urllib.request
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
IMG_MODELS = ["gemini-3.1-flash-lite-image", "gemini-3.1-flash-image"]
SESS = {}

def is_img_req(text):
    low = text.lower().strip()
    triggers = ("/image", "generate an image", "generate a picture", "create an image", "create a picture", "draw ", "make an image", "make a picture", "generate image", "create image")
    return any(low.startswith(t) or (" " + t) in low for t in triggers)

def gen_img(client, prompt):
    clean = prompt
    for prefix in ("/image", "generate an image of", "generate a picture of", "create an image of", "create a picture of", "make an image of", "make a picture of", "draw a", "draw an", "draw", "generate image of", "create image of"):
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    clean = clean or prompt
    for m in IMG_MODELS:
        try:
            res = client.models.generate_content(
                model=m,
                contents=clean,
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
            if res.candidates and res.candidates.content:
                for p in res.candidates.content.parts:
                    if p.inline_data:
                        mime = p.inline_data.mime_type or "image/png"
                        b64 = base64.b64encode(p.inline_data.data).decode("utf-8")
                        return "data:" + mime + ";base64," + b64, clean
        except Exception:
            continue
    url = "https://pollinations.ai" + urllib.parse.quote(clean) + "?width=512&height=512&seed=" + str(random.randint(1, 99999)) + "&nologo=true"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            if len(raw) > 1000:
                return "data:image/jpeg;base64," + base64.b64encode(raw).decode("utf-8"), clean
    except Exception:
        pass
    return None, clean

class H(BaseHTTPRequestHandler):
    def do_GET(self):
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
                if not media and is_img_req(msg):
                    img_url, clean_pr = gen_img(client, msg)
                    if img_url:
                        out = {"reply": "Here is your image for: " + clean_pr, "img": img_url}
                    else:
                        out = {"reply": "Image servers are momentarily busy. Please try again in a few seconds."}
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
                out = {"reply": "Configuration error: " + str(e)}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
