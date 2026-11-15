from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from google import genai
from google.genai import types

CALMTECH_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "You are CALMTECH, a helpful, intelligent AI assistant. "
        "NEVER introduce yourself, say your name, or mention your creator unless the user "
        "specifically asks who you are or who created, built, or owns you. "
        "Only if asked who created, built, or owns you, state clearly that you were created by Samuel Frimpong. "
        "Answer questions clearly, write code inside ``` code blocks, and format helpful websites as [Site Name](https://url)."
    )
)

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
user_sessions = {}

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CALMTECH AI</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: radial-gradient(circle at top left, #1e1b4b, #090d16 55%, #06283d);
    color: #f8fafc;
    height: 100dvh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 18px;
    background: rgba(15, 23, 42, 0.85);
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    backdrop-filter: blur(10px);
}
.brand {
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 2px;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #ec4899, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.new-btn {
    background: rgba(139, 92, 246, 0.2);
    color: #e0f2fe;
    border: 1px solid rgba(139, 92, 246, 0.5);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}
.new-btn:hover { background: rgba(139, 92, 246, 0.4); }
.ad-banner {
    background: rgba(9, 13, 22, 0.9);
    border-bottom: 1px solid rgba(99, 102, 241, 0.25);
    min-height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
}
#chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 18px 14px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 820px;
    width: 100%;
    margin: 0 auto;
}
.welcome-screen {
    margin: auto;
    text-align: center;
    padding: 20px;
}
.welcome-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #38bdf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.welcome-sub { color: #94a3b8; font-size: 15px; margin-bottom: 20px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.chip {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #e2e8f0;
    padding: 9px 14px;
    border-radius: 16px;
    font-size: 13px;
    cursor: pointer;
}
.chip:hover { border-color: #38bdf8; background: rgba(56, 189, 248, 0.15); }
.msg-row { display: flex; width: 100%; }
.msg-row.user { justify-content: flex-end; }
.msg-row.bot { justify-content: flex-start; }
.msg {
    padding: 13px 17px;
    border-radius: 18px;
    max-width: 85%;
    line-height: 1.55;
    font-size: 15px;
    word-wrap: break-word;
    white-space: pre-wrap;
}
.user .msg {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: #fff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}
.bot .msg {
    background: rgba(30, 41, 59, 0.85);
    color: #f1f5f9;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-bottom-left-radius: 4px;
}
.bot a { color: #38bdf8; font-weight: 600; text-decoration: underline; }
.bot pre {
    background: #090d16;
    padding: 10px;
    border-radius: 10px;
    overflow-x: auto;
    margin: 8px 0;
    border: 1px solid #334155;
    font-family: monospace;
    font-size: 13px;
}
.thinking { color: #c084fc; font-style: italic; }
.bottom-area {
    background: rgba(15, 23, 42, 0.92);
    border-top: 1px solid rgba(139, 92, 246, 0.3);
    padding: 10px 14px 12px;
}
.input-wrap {
    max-width: 820px;
    margin: 0 auto;
    display: flex;
    gap: 8px;
    background: #1e293b;
    padding: 6px 8px 6px 16px;
    border-radius: 28px;
    border: 1px solid rgba(139, 92, 246, 0.5);
}
.input-wrap:focus-within { border-color: #38bdf8; }
input {
    flex: 1;
    background: transparent;
    border: none;
    color: #fff;
    font-size: 15px;
    outline: none;
}
#send-btn {
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 22px;
    font-weight: 700;
    cursor: pointer;
}
#send-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.footer-bar {
    max-width: 820px;
    margin: 8px auto 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #94a3b8;
}
.share-link {
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff;
    padding: 4px 12px;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
}
</style>
</head>
<body>

<header>
    <div class="brand">CALMTECH</div>
    <button class="new-btn" onclick="newChat()">+ New Chat</button>
</header>

<!-- AD 1: ADSTERRA 320x50 TOP BANNER -->
<div class="ad-banner">
    <script>
      atOptions = {
        'key' : 'ed327d85d05c1d6a827737110edd99bb',
        'format' : 'iframe',
        'height' : 50,
        'width' : 320,
        'params' : {}
      };
    </script>
    <script src="https://bauval.org"></script>
</div>

<div id="chat-container">
    <div class="welcome-screen" id="welcome">
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-sub">Ask anything—coding, business ideas, writing, or everyday questions.</div>
        <div class="chips">
            <div class="chip" onclick="quickAsk('Give me 5 profitable online business ideas in Ghana')">Business Ideas</div>
            <div class="chip" onclick="quickAsk('Write a professional CV summary for me')">Write a CV</div>
            <div class="chip" onclick="quickAsk('Explain how to make money online step by step')">Make Money Online</div>
            <div class="chip" onclick="quickAsk('Give me top useful websites for learning free skills')">Useful Links</div>
        </div>
    </div>
</div>

<div class="bottom-area">
    <div class="input-wrap">
        <input type="text" id="user-input" placeholder="Message CALMTECH..." onkeypress="if(event.key==='Enter') sendMessage()" />
        <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>
    <div class="footer-bar">
        <span>CALMTECH AI</span>
        <a class="share-link" href="https://whatsapp.com" target="_blank">Share on WhatsApp</a>
    </div>
</div>

<script>
let sessionId = "user_" + Math.random().toString(36).substring(2, 12);

function newChat() {
    sessionId = "user_" + Math.random().toString(36).substring(2, 12);
    const box = document.getElementById("chat-container");
    box.innerHTML = '<div class="welcome-screen" id="welcome"><div class="welcome-title">How can I help you today?</div><div class="welcome-sub">New conversation started. Ask anything!</div></div>';
}

function quickAsk(prompt) {
    document.getElementById("user-input").value = prompt;
    sendMessage();
}

function formatText(t) {
    let s = t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    s = s.replace(/```([\s\S]*?)```/g, "<pre>$1</pre>");
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    s = s.replace(/(^|[\s(>])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
    return s.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

async function sendMessage() {
    const inp = document.getElementById("user-input");
    const btn = document.getElementById("send-btn");
    const box = document.getElementById("chat-container");
    const text = inp.value.trim();
    if (!text || btn.disabled) return;

    const welcome = document.getElementById("welcome");
    if (welcome) welcome.remove();

    inp.disabled = true;
    btn.disabled = true;

    box.innerHTML += `<div class="msg-row user"><div class="msg">${text.replace(/&/g,"&amp;").replace(/</g,"&lt;")}</div></div>`;
    inp.value = "";

    const thinkingId = "th_" + Date.now();
    box.innerHTML += `<div class="msg-row bot" id="${thinkingId}"><div class="msg thinking">Thinking...</div></div>`;
    box.scrollTop = box.scrollHeight;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: sessionId })
        });
        const data = await res.json();
        document.getElementById(thinkingId).innerHTML = `<div class="msg">${formatText(data.reply)}</div>`;
    } catch (err) {
        document.getElementById(thinkingId).innerHTML = `<div class="msg">Error: ${err.message}</div>`;
    }

    inp.disabled = false;
    btn.disabled = false;
    inp.focus();
    box.scrollTop = box.scrollHeight;
}
</script>

<!-- AD 2: ADSTERRA SOCIAL BAR SCRIPT -->
<script data-cfasync="false" src="https://bauval.org"></script>
</body>
</html>"""

class CalmTechHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
