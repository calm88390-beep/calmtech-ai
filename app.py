from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import io
import json
import os
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
    text_m = next((m for m in all_ids if "qwen" in m.id.lower() or "llama" in m.id.lower()), all_ids if all_ids else "qwen/qwen3.8-27b")
    vis_m = next((m for m in all_ids if "vision" in m.id.lower() or "vl" in m.id.lower() or "scout" in m.id.lower() or "maverick" in m.id.lower()), text_m)
    return text_m, vis_m

def generate_real_img(prompt):
    hf_key = "".join(os.environ.get("HF_TOKEN", "").split())
    clean = prompt
    for prefix in ("/image", "generate an image of", "generate a picture of", "create an image of", "create a picture of", "make an image of", "make a picture of", "draw a", "draw an", "draw", "generate image of", "create image of"):
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    if "of ur choice" in clean.lower() or "of your choice" in clean.lower():
        clean = "A breathtaking futuristic skyline of Accra, Ghana at golden sunset, ultra detailed digital art"
    clean = clean or prompt

    if not hf_key.startswith("hf_"):
        return None, clean, "Please add your free HF_TOKEN in Render Environment variables to enable real AI image generation."

    models = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0"
    ]
    last_err = ""
    hf = InferenceClient(api_key=hf_key)
    for m in models:
        try:
            pil_img = hf.text_to_image(clean, model=m)
            buf = io.BytesIO()
            pil_img.save(buf, format="JPEG", quality=88)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return "data:image/jpeg;base64," + b64, clean, ""
        except Exception as e:
            last_err = str(e)
            continue
    return None, clean, "Image generation error: " + last_err[:120]

def ask_groq(hist, media):
    key = "".join(os.environ.get("GROQ_API_KEY", "").split())
    if not key.startswith("gsk_"):
        return {"reply": "Your GROQ_API_KEY on Render does not look right (it should start with gsk_). Please double-check it in Render Environment settings."}

    last_text = hist[-1]["text"]
    if not media and is_img_req(last_text):
        img_url, clean_pr, err = generate_real_img(last_text)
        if img_url:
            return {"reply": "Here is your image for: " + clean_pr, "img": img_url}
        return {"reply": err}

    client = Groq(api_key=key)
    text_m, vis_m = pick_models(client)
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
