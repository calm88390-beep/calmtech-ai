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
        "You are CALMTECH, a helpful AI assistant. NEVER introduce yourself, say your name, "
        "or mention your creator unless asked who created, built, or owns you. "
        "Only if asked who created, built, or owns you, state that you were created by Samuel Frimpong. "
        "Format helpful websites as [Site Name](https://url)."
    )
)

TEXT_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
IMG_MODELS = ["gemini-3.1-flash-lite-image", "gemini-3.1-flash-image"]
SESSIONS = {}

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CALMTECH AI</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, -apple-system, sans-serif;
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
    background: rgba(139, 92, 246, 0.25);
    color: #e0f2fe;
    border: 1px solid rgba(139, 92, 246, 0.5);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}
.ad-banner {
    background: rgba(9, 13, 22, 0.9);
    border-bottom: 1px solid rgba(99, 102, 241, 0.25);
    min-height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
}
#chat {
    flex: 1;
    overflow-y: auto;
    padding: 18px 14px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-width: 820px;
    width: 100%;
    margin: 0 auto;
}
.welcome { margin: auto; text-align: center; padding: 20px; }
.w-title {
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #38bdf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.w-sub { color: #94a3b8; font-size: 15px; margin-bottom: 18px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.chip {
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid rgba(139, 92, 246, 0.45);
    color: #e2e8f0;
    padding: 8px 14px;
    border-radius: 16px;
    font-size: 13px;
    cursor: pointer;
}
.row { display: flex; width: 100%; }
.row.u { justify-content: flex-end; }
.row.b { justify-content: flex-start; }
.msg {
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 85%;
    line-height: 1.55;
    font-size: 15px;
    word-wrap: break-word;
    white-space: pre-wrap;
}
.u .msg {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: #fff;
    border-bottom-right-radius: 4px;
}
.b .msg {
    background: rgba(30, 41, 59, 0.88);
    color: #f1f5f9;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-bottom-left-radius: 4px;
}
.b a { color: #38bdf8; font-weight: 600; text-decoration: underline; }
.b pre {
    background: #090d16;
    padding: 10px;
    border-radius: 10px;
    overflow-x: auto;
    margin: 8px 0;
    border: 1px solid #334155;
    font-family: monospace;
    font-size: 13px;
}
.b img {
    max-width: 100%;
    border-radius: 12px;
    margin-top: 8px;
    display: block;
    border: 1px solid rgba(168, 85, 247, 0.4);
}
.dl {
    display: inline-block;
    margin-top: 8px;
    color: #38bdf8;
    font-size: 13px;
    font-weight: bold;
    text-decoration: none;
}
.th { color: #c084fc; font-style: italic; }
.bottom {
    background: rgba(15, 23, 42, 0.92);
    border-top: 1px solid rgba(139, 92, 246, 0.3);
    padding: 10px 14px 12px;
}
.in-wrap {
    max-width: 820px;
    margin: 0 auto;
    display: flex;
    gap: 6px;
    background: #1e293b;
    padding: 6px 8px 6px 16px;
    border-radius: 28px;
    border: 1px solid rgba(139, 92, 246, 0.5);
}
input {
    flex: 1;
    background: transparent;
    border: none;
    color: #fff;
    font-size: 15px;
    outline: none;
}
#img-btn {
    background: linear-gradient(135deg, #ec4899, #8b5cf6);
    color: #fff;
    border: none;
    padding: 10px 14px;
    border-radius: 22px;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
}
#btn {
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    color: #fff;
    border: none;
    padding: 10px 18px;
    border-radius: 22px;
    font-weight: 700;
    cursor: pointer;
}
button:disabled { opacity: 0.45; }
.foot {
    max-width: 820px;
    margin: 8px auto 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #94a3b8;
}
.share {
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
    <button class="new-btn" onclick="resetChat()">+ New Chat</button>
</header>

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

<div id="chat">
    <div class="welcome" id="w">
        <div class="w-title">How can I help you today?</div>
        <div class="w-sub">Ask anything or describe a picture and click Image!</div>
        <div class="chips">
            <div class="chip" onclick="ask('Give me 5 profitable online business ideas in Ghana')">Business Ideas</div>
            <div class="chip" onclick="askImg('A futuristic sports car in Accra at sunset, realistic photo')">Create Car Image</div>
            <div class="chip" onclick="ask('Give me useful websites for learning free skills')">Useful Links</div>
        </div>
    </div>
</div>

<div class="bottom">
    <div class="in-wrap">
        <input id="inp" placeholder="Ask anything or describe an image..." onkeypress="if(event.key==='Enter')send(false)">
        <button id="img-btn" onclick="send(true)">Image</button>
        <button id="btn" onclick="send(false)">Send</button>
    </div>
    <div class="foot">
        <span>CALMTECH AI</span>
        <a class="share" href="https://whatsapp.com" target="_blank">Share on WhatsApp</a>
    </div>
</div>

<script>
let sid = "u_" + Math.random().toString(36).slice(2, 11);

function resetChat() {
    sid = "u_" + Math.random().toString(36).slice(2, 11);
    document.getElementById("chat").innerHTML = '<div class="welcome" id="w"><div class="w-title">How can I help you today?</div><div class="w-sub">New conversation started. Ask anything or create an image!</div></div>';
}

function ask(q) {
    document.getElementById("inp").value = q;
    send(false);
}

function askImg(q) {
    document.getElementById("inp").value = q;
    send(true);
}

function fmt(t) {
    let s = t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    s = s.replace(/```([\s\S]*?)```/g, "<pre>$1</pre>");
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    s = s.replace(/(^|[\s(>])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
    return s.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

async function send(makeImg) {
    const i = document.getElementById("inp");
    const b = document.getElementById("btn");
    const ib = document.getElementById("img-btn");
    const c = document.getElementById("chat");
    let t = i.value.trim();
    if (!t || b.disabled) return;

    if (makeImg && !t.toLowerCase().startsWith("/image")) {
        t = "/image " + t;
    }

    const w = document.getElementById("w");
    if (w) w.remove();

    i.disabled = b.disabled = ib.disabled = true;
    c.innerHTML += `<div class="row u"><div class="msg">${t.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</div></div>`;
    i.value = "";

    const isImg = t.toLowerCase().startsWith("/image");
    const id = "t" + Date.now();
    c.innerHTML += `<div class="row b" id="${id}"><div class="msg th">${isImg ? "Creating your image..." : "Thinking..."}</div></div>`;
    c.scrollTop = c.scrollHeight;

    try {
        const r = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: t, session_id: sid })
        });
        const d = await r.json();
        if (d.image_data) {
            document.getElementById(id).innerHTML = `<div class="msg">${fmt(d.reply)}<img src="${d.image_data}" alt="Generated"><a class="dl" href="${d.image_data}" download="calmtech-image.png">Download Image</a></div>`;
        } else {
            document.getElementById(id).innerHTML = `<div class="msg">${fmt(d.reply)}</div>`;
        }
    } catch (e) {
        document.getElementById(id).innerHTML = `<div class="msg">Error: ${e.message}</div>`;
    }

    i.disabled = b.disabled = ib.disabled = false;
    i.focus();
    c.scrollTop = c.scrollHeight;
}
</script>
