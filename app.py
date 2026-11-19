from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
import re
from groq import Groq

SYS_PROMPT = (
    "You are CALMTECH, a fast, helpful AI assistant. Current year: 2026. "
    "The current President of Ghana is John Dramani Mahama (inaugurated January 7, 2025), and the Vice President is Jane Naana Opoku-Agyemang. "
    "NEVER introduce yourself, say your name, or mention your creator unless asked who created, built, or owns you. "
    "If asked who created, built, or owns you, state that you were created by Samuel Frimpong. "
    "Give clear, direct, helpful answers, analyze uploaded images in detail, and share full clickable URLs like https://example.com when helpful."
)
SESS = {}

def is_img_req(text):
    low = text.lower().strip()
    triggers = ("/image", "generate an image", "generate a picture", "create an image", "create a picture", "draw ", "make an image", "make a picture", "generate image", "create image")
    return any(low.startswith(t) or (" " + t) in low for t in triggers)

def pick_models(client):
    try:
        all_ids = [m.id for m in client.models.list().data if "whisper" not in m.id.lower() and "tts" not in m.id.lower() and "guard" not in m.id.lower()]
    except Exception:
        all_ids = []
    text_m = next((m for m in all_ids if "70b" in m or "llama-4" in m or "qwen" in m or "llama-3" in m), "llama-3.1-8b-instant")
    vis_m = next((m for m in all_ids if "scout" in m or "maverick" in m or "vision" in m), text_m)
    return text_m, vis_m

def create_svg_img(client, model, prompt):
    clean = prompt
    for prefix in ("/image", "generate an image of", "generate a picture of", "create an image of", "create a picture of", "make an image of", "make a picture of", "draw a", "draw an", "draw", "generate image of", "create image of"):
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    clean = clean or prompt
    svg_prompt = (
        f"Create a detailed, colorful, high-quality vector illustration in SVG format for: '{clean}'. "
        "Output ONLY valid raw <svg xmlns='http://w3.org' viewBox='0 0 512 512' width='512' height='512'>...</svg> code. "
        "Include vibrant gradients, background scenery, shadows, and clear recognizable shapes. Do not output markdown fences or any text outside the <svg> tag."
    )
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": svg_prompt}],
        temperature=0.6
    )
    raw = res.choices.pop(0).message.content or ""
    match = re.search(r"<svg[\s\S]*?</svg>", raw, re.IGNORECASE)
    if match:
        svg_code = match.group(0)
        if "xmlns=" not in svg_code:
            svg_code = svg_code.replace("<svg", '<svg xmlns="http://w3.org"', 1)
        b64 = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
        return "data:image/svg+xml;base64," + b64, clean
    return None, clean

def ask_groq(hist, media):
    key = "".join(os.environ.get("GROQ_API_KEY", "").split())
    if not key.startswith("gsk_"):
        return {"reply": "Your GROQ_API_KEY on Render does not look right (it should start with gsk_). Please double-check it in Render Environment settings."}

    client = Groq(api_key=key)
    text_m, vis_m = pick_models(client)
    last_text = hist[-1]["text"]

    if not media and is_img_req(last_text):
        img_url, clean_pr = create_svg_img(client, text_m, last_text)
        if img_url:
            return {"reply": "Here is your image for: " + clean_pr, "img": img_url}
        return {"reply": "Could not render that image right now. Try describing it in a simpler way!"}

    msgs = [{"role": "system", "content": SYS_PROMPT}]
    for h in hist[:-1]:
        msgs.append({"role": h["role"], "content": h["text"]})

    if media:
        data_url = "data:" + media["mime"] + ";base64," + media["data"]
        msgs.append({
            "role": "user",
            "content": [
                {"type": "text", "text": last_text},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        })
        model = vis_m
    else:
        msgs.append({"role": "user", "content": last_text})
        model = text_m

    res = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=0.7
    )
    return {"reply": res.choices.pop(0).message.content}

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
                    out = ask_groq(hist, media)
                else:
                    out = {"reply": "Please add your free GROQ_API_KEY in Render Environment variables for ultra-fast replies!"}

                hist.append({"role": "assistant", "text": out["reply"]})
                SESS[sid] = hist
            except Exception as e:
                out = {"reply": "Connection error: " + str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
