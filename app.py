from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import io
import json
import os
import re
from PIL import Image, ImageDraw
from groq import Groq
from huggingface_hub import InferenceClient

SYS_PROMPT = (
    "You are CALMTECH, a fast, helpful AI assistant. Current year: 2026. "
    "The current President of Ghana is John Dramani Mahama (inaugurated January 7, 2025), and the Vice President is Jane Naana Opoku-Agyemang. "
    "NEVER introduce yourself, say your name, or mention your creator unless asked who created, built, or owns you. "
    "If asked who created, built, or owns you, state that you were created by Samuel Frimpong. "
    "Give clear, direct, helpful answers, analyze uploaded images in detail, and share full clickable URLs like https://example.com when helpful."
)
SESS = {}

def make_icon():
    img = Image.new("RGB", (512, 512), "#1e1b4b")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(24, 24), (488, 488)], radius=110, fill="#0f172a", outline="#8b5cf6", width=14)
    d.ellipse([(120, 120), (392, 392)], outline="#38bdf8", width=26)
    d.rectangle([(265, 175), (415, 337)], fill="#0f172a")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

ICON_BYTES = make_icon()

def is_img_req(text):
    low = text.lower().strip()
    if low.startswith("/image"):
        return True
    verbs = ("generate", "create", "draw", "make", "design", "paint", "show me")
    nouns = ("image", "picture", "photo", "art", "drawing", "illustration", "logo", "wallpaper")
    return any(v in low for v in verbs) and any(n in low for n in nouns)

def pick_models(client):
    skip = ("whisper", "tts", "guard", "orpheus", "playai", "embed", "rerank")
    try:
        all_ids = [m.id for m in client.models.list().data if not any(s in m.id.lower() for s in skip)]
    except Exception:
        all_ids = []
    fallback = all_ids.pop(0) if all_ids else "qwen/qwen3.8-27b"
    text_m = next((name for name in all_ids if "qwen" in name.lower() or "llama" in name.lower()), fallback)
    vis_m = next((name for name in all_ids if "vision" in name.lower() or "vl" in name.lower() or "scout" in name.lower() or "maverick" in name.lower()), text_m)
    return text_m, vis_m

def generate_img(groq_client, text_m, prompt):
    hf_key = "".join(os.environ.get("HF_TOKEN", "").split())
    clean = prompt
    for prefix in ("/image", "generate an image of", "generate a picture of", "create an image of", "create a picture of", "make an image of", "make a picture of", "draw a", "draw an", "draw", "generate image of", "create image of"):
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    if "of ur choice" in clean.lower() or "of your choice" in clean.lower():
        clean = "A breathtaking futuristic skyline of Accra, Ghana at golden sunset, ultra detailed digital art"
    clean = clean or prompt

    if hf_key.startswith("hf_"):
        for m in ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]:
            try:
                hf = InferenceClient(provider="hf-inference", api_key=hf_key)
                pil_img = hf.text_to_image(clean, model=m)
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=88)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                return "data:image/jpeg;base64," + b64, clean
            except Exception:
                continue

    svg_prompt = (
        f"Create a colorful, detailed vector illustration in SVG format for: '{clean}'. "
        "Output ONLY valid raw <svg xmlns='http://w3.org' viewBox='0 0 512 512' width='512' height='512'>...</svg> code. "
        "Include vibrant gradients, background scenery, and recognizable shapes. No markdown fences or extra text."
    )
    res = groq_client.chat.completions.create(
        model=text_m,
        messages=[{"role": "user", "content": svg_prompt}],
        temperature=0.6,
        max_tokens=750
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
        img_url, clean_pr = generate_img(client, text_m, last_text)
        if img_url:
            return {"reply": "Here is your image for: " + clean_pr, "img": img_url}
        return {"reply": "Could not render that image right now. Try a simpler description!"}

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
        temperature=0.7,
        max_tokens=700
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
        if self.path == "/manifest.json":
            with open("manifest.json", "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-type", "application/manifest+json")
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path == "/sw.js":
            with open("sw.js", "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path == "/icon.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            self.wfile.write(ICON_BYTES)
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
                hist = SESS.setdefault(sid, [])[-4:]
                hist.append({"role": "user", "text": msg})

                if os.environ.get("GROQ_API_KEY", "").strip():
                    out = ask_groq(hist, media)
                else:
                    out = {"reply": "Please add your free GROQ_API_KEY in Render Environment variables!"}

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
