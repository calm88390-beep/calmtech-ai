from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64, json, os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

CALMTECH_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "You are CALMTECH, a helpful AI assistant. NEVER introduce yourself, say your name, "
        "or mention your creator unless asked who created, built, or owns you. "
        "If asked who created, built, or owns you, state clearly that you were created by Samuel Frimpong. "
        "Analyze uploaded photos and videos in detail, answer questions clearly, and format links as [Name](https://url)."
    )
)

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
user_sessions = {}

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CALMTECH AI</title>
<style>
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;max-width:780px;margin:0 auto;padding:12px;min-height:100vh;background:linear-gradient(135deg,#090d16 0%,#1e1145 50%,#0c2e4e 100%);color:#f8fafc}
header{display:flex;justify-content:space-between;align-items:center;padding:8px 4px}
h1{margin:0;font-size:26px;font-weight:900;letter-spacing:2px;background:linear-gradient(90deg,#38bdf8,#a855f7,#ec4899,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.badge{background:rgba(168,85,247,0.2);color:#e0f2fe;padding:4px 12px;border-radius:20px;font-size:12px;border:1px solid rgba(168,85,247,0.5)}
.ad-slot{background:rgba(15,23,42,0.8);border:1px solid rgba(99,102,241,0.4);padding:6px;text-align:center;margin:8px 0;border-radius:12px;min-height:62px;display:flex;align-items:center;justify-content:center;overflow:hidden}
#chat-box{background:rgba(15,23,42,0.82);height:54vh;overflow-y:auto;padding:15px;border-radius:16px;border:1px solid rgba(139,92,246,0.4);display:flex;flex-direction:column;gap:12px}
.msg{padding:12px 15px;border-radius:16px;max-width:85%;line-height:1.5;font-size:15px;word-wrap:break-word;white-space:pre-wrap}
.user{background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;align-self:flex-end;border-bottom-right-radius:4px}
.bot{background:linear-gradient(135deg,#1e293b,#2e1d59);color:#f1f5f9;align-self:flex-start;border-bottom-left-radius:4px;border:1px solid rgba(168,85,247,0.25)}
.bot a{color:#38bdf8;font-weight:bold;text-decoration:underline}
.msg img,.msg video{max-width:100%;max-height:200px;border-radius:10px;margin-bottom:6px;display:block}
.thinking{font-style:italic;color:#c084fc}
#preview-bar{display:none;align-items:center;justify-content:space-between;background:rgba(124,58,237,0.25);border:1px solid #a855f7;padding:6px 12px;border-radius:12px;margin-top:8px;font-size:13px}
.rm-btn{background:#ef4444;color:#fff;border:none;border-radius:50%;width:22px;height:22px;cursor:pointer;font-weight:bold}
#input-area{display:flex;gap:6px;margin-top:10px;align-items:center}
.media-btn{padding:12px 13px;background:linear-gradient(135deg,#ec4899,#8b5cf6);color:#fff;border:none;border-radius:24px;font-weight:bold;cursor:pointer;font-size:13px;white-space:nowrap}
input[type="text"]{flex:1;padding:12px 15px;border-radius:24px;border:1px solid rgba(139,92,246,0.5);background:rgba(15,23,42,0.9);color:#fff;font-size:15px;outline:none}
#send-btn{padding:12px 20px;background:linear-gradient(135deg,#06b6d4,#3b82f6);color:#fff;border:none;border-radius:24px;font-weight:bold;cursor:pointer}
button:disabled{opacity:0.5;cursor:not-allowed}
.share-bar{background:rgba(15,23,42,0.75);border:1px solid rgba(56,189,248,0.3);padding:9px;text-align:center;margin:8px 0 4px;border-radius:12px;font-size:13px;color:#cbd5e1}
.share-btn{display:inline-block;margin-left:8px;padding:5px 12px;background:linear-gradient(135deg,#10b981,#059669);color:#fff;border-radius:14px;text-decoration:none;font-weight:bold;font-size:12px}
footer{text-align:center;font-size:12px;color:#94a3b8;margin-top:4px}
</style>
</head>
<body>
<header><h1>CALMTECH</h1><span class="badge">Text • Photo • Video AI</span></header>
<div class="ad-slot" id="top-ad">
<script>atOptions={'key':'ed327d85d05c1d6a827737110edd99bb','format':'iframe','height':50,'width':320,'params':{}};</script>
<script src="https://bauval.org"></script>
</div>
<div id="chat-box"><div class="msg bot">How can I help you today? Ask any question or attach a photo or short video!</div></div>
<div id="preview-bar"><span id="file-label">Attached</span><button class="rm-btn" onclick="clearMedia()">×</button></div>
<div id="input-area">
<input type="file" id="media-input" accept="image/*,video/*" style="display:none" onchange="handleFileSelect(event)">
<button class="media-btn" id="media-btn" onclick="document.getElementById('media-input').click()">+ Photo/Video</button>
<input type="text" id="user-input" placeholder="Ask anything or attach media..." onkeypress="if(event.key==='Enter') sendMessage()">
<button id="send-btn" onclick="sendMessage()">Send</button>
</div>
<div class="share-bar">Share with friends:<a class="share-btn" href="https://whatsapp.com" target="_blank">Share on WhatsApp</a></div>
<footer>CALMTECH AI</footer>
<script>
const sessionId="user_"+Math.random().toString(36).substring(2,12);
let selectedMedia=null;
function handleFileSelect(e){
  const file=e.target.files;if(!file)return;
  if(file.size>15*1024*1024){alert("Please select a photo or video under 15 MB.");e.target.value="";return;}
  const r=new FileReader();
  r.onload=function(ev){
    const d=ev.target.result;
    selectedMedia={name:file.name,mime_type:file.type,data:d.split(","),preview_url:d};
    document.getElementById("file-label").textContent="Attached: "+file.name;
    document.getElementById("preview-bar").style.display="flex";
  };
  r.readAsDataURL(file);
}
function clearMedia(){selectedMedia=null;document.getElementById("media-input").value="";document.getElementById("preview-bar").style.display="none";}
function formatText(t){
  let s=t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  s=s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  s=s.replace(/(^|[\s(>])(https?:\/\/[^\s<)]+)/g,'$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
  return s.replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>");
}
async function sendMessage(){
  const inp=document.getElementById("user-input"),btn=document.getElementById("send-btn"),mBtn=document.getElementById("media-btn"),box=document.getElementById("chat-box");
  const text=inp.value.trim();if((!text&&!selectedMedia)||btn.disabled)return;
  inp.disabled=btn.disabled=mBtn.disabled=true;
  const uDiv=document.createElement("div");uDiv.className="msg user";
  if(selectedMedia){
    const el=document.createElement(selectedMedia.mime_type.startsWith("video/")?"video":"img");
    el.src=selectedMedia.preview_url;if(el.tagName==="VIDEO")el.controls=true;uDiv.appendChild(el);
  }
  const tDiv=document.createElement("div");tDiv.textContent=text||(selectedMedia?"Analyze this media":"");uDiv.appendChild(tDiv);
  box.appendChild(uDiv);
  const mediaPayload=selectedMedia?{mime_type:selectedMedia.mime_type,data:selectedMedia.data}:null;
  inp.value="";clearMedia();
  const thDiv=document.createElement("div");thDiv.className="msg bot thinking";thDiv.textContent=mediaPayload?"Analyzing media...":"Thinking...";
  box.appendChild(thDiv);box.scrollTop=box.scrollHeight;
  try{
    const res=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text||"Analyze this image or video in detail.",session_id:sessionId,media:mediaPayload})});
    const data=await res.json();thDiv.className="msg bot";thDiv.innerHTML=formatText(data.reply);
  }catch(err){thDiv.className="msg bot";thDiv.textContent="Error: "+err.message;}
  inp.disabled=btn.disabled=mBtn.disabled=false;inp.focus();box.scrollTop=box.scrollHeight;
}
</script>
<script data-cfasync="false" src="https://bauval.org"></script>
</body></html>"""

class CalmTechHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path == "/chat":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            msg = data.get("message", "")
            sid = data.get("session_id", "default")
            media = data.get("media")
            hist = user_sessions.setdefault(sid, [])[-10:]
            parts = []
            if media and media.get("data") and media.get("mime_type"):
                parts.append(types.Part.from_bytes(data=base64.b64decode(media["data"]), mime_type=media["mime_type"]))
            parts.append(types.Part.from_text(text=msg))
            hist.append(types.Content(role="user", parts=parts))
            reply = "Servers are busy. Please try again in a moment."
            for m in MODELS:
                try:
                    res = client.models.generate_content(model=m, contents=hist, config=CALMTECH_CONFIG)
                    reply = res.text
                    hist[-1] = types.Content(role="user", parts=[types.Part.from_text(text=msg)])
                    hist.append(types.Content(role="model", parts=[types.Part.from_text(text=reply)]))
                    user_sessions[sid] = hist
                    break
                except Exception as e:
                    if "503" in str(e) or "429" in str(e):
                        continue
                    reply = f"Connection error: {str(e)}"
