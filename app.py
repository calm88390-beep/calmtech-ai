from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
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

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]

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
.hdr-btns { display: flex; gap: 8px; }
.nav-btn {
    background: rgba(139, 92, 246, 0.25);
    color: #e0f2fe;
    border: 1px solid rgba(139, 92, 246, 0.5);
    padding: 6px 13px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}
.nav-btn:hover { background: rgba(139, 92, 246, 0.45); }
.ad-banner {
    background: rgba(9, 13, 22, 0.9);
    border-bottom: 1px solid rgba(99, 102, 241, 0.25);
    min-height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
}
#history-panel {
    display: none;
    position: fixed;
    top: 56px;
    right: 14px;
    width: 290px;
    max-height: 68vh;
    overflow-y: auto;
    background: #131936;
    border: 1px solid rgba(139, 92, 246, 0.6);
    border-radius: 16px;
    padding: 12px;
    z-index: 100;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
}
.hist-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: 700;
    color: #38bdf8;
}
.hist-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 10px;
    margin-bottom: 6px;
    background: rgba(30, 41, 59, 0.85);
    border-radius: 10px;
    cursor: pointer;
    font-size: 13px;
    border: 1px solid transparent;
}
.hist-item.active { border-color: #38bdf8; background: rgba(56, 189, 248, 0.15); }
.hist-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.del-chat { color: #f87171; font-weight: bold; margin-left: 8px; padding: 2px 6px; }
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
    gap: 8px;
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
#btn {
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    color: #fff;
    border: none;
    padding: 10px 20px;
    border-radius: 22px;
    font-weight: 700;
    cursor: pointer;
}
#btn:disabled { opacity: 0.45; }
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
    <div class="hdr-btns">
        <button class="nav-btn" onclick="toggleHistory()">History</button>
        <button class="nav-btn" onclick="resetChat()">+ New Chat</button>
    </div>
</header>

<div id="history-panel">
    <div class="hist-head"><span>Previous Chats</span><span style="cursor:pointer" onclick="toggleHistory()">✕</span></div>
    <div id="hist-list"></div>
</div>

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

<div id="chat"></div>

<div class="bottom">
    <div class="in-wrap">
        <input id="inp" placeholder="Message CALMTECH..." onkeypress="if(event.key==='Enter')send()">
        <button id="btn" onclick="send()">Send</button>
    </div>
    <div class="foot">
        <span>CALMTECH AI</span>
        <a class="share" href="https://whatsapp.com" target="_blank">Share on WhatsApp</a>
    </div>
</div>

<script>
let allChats = JSON.parse(localStorage.getItem("calmtech_chats") || "{}");
let sid = "u_" + Math.random().toString(36).slice(2, 11);

function saveStore() {
    localStorage.setItem("calmtech_chats", JSON.stringify(allChats));
    renderHistory();
}

function toggleHistory() {
    const p = document.getElementById("history-panel");
    p.style.display = p.style.display === "block" ? "none" : "block";
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById("hist-list");
    const ids = Object.keys(allChats).reverse();
    if (!ids.length) {
        list.innerHTML = '<div style="color:#94a3b8;font-size:13px;">No saved chats yet.</div>';
        return;
    }
    list.innerHTML = ids.map(id => {
        const title = (allChats[id].title || "Chat").replace(/</g, "&lt;");
        const active = id === sid ? " active" : "";
        return `<div class="hist-item${active}" onclick="loadChat('${id}')"><span class="hist-title">${title}</span><span class="del-chat" onclick="delChat(event,'${id}')">×</span></div>`;
    }).join("");
}

function loadChat(id) {
    sid = id;
    document.getElementById("history-panel").style.display = "none";
    const box = document.getElementById("chat");
    box.innerHTML = "";
    const msgs = (allChats[id] && allChats[id].messages) || [];
    msgs.forEach(m => {
        if (m.role === "u") {
            box.innerHTML += `<div class="row u"><div class="msg">${m.text.replace(/&/g,"&amp;").replace(/</g,"&lt;")}</div></div>`;
        } else {
            box.innerHTML += `<div class="row b"><div class="msg">${fmt(m.text)}</div></div>`;
        }
    });
    box.scrollTop = box.scrollHeight;
}

function delChat(e, id) {
    e.stopPropagation();
    delete allChats[id];
    saveStore();
    if (id === sid) resetChat();
}

function resetChat() {
    sid = "u_" + Math.random().toString(36).slice(2, 11);
    document.getElementById("history-panel").style.display = "none";
    document.getElementById("chat").innerHTML = '<div class="welcome" id="w"><div class="w-title">How can I help you today?</div><div class="w-sub">Ask anything—coding, business ideas, writing, or everyday questions.</div><div class="chips"><div class="chip" onclick="ask(\'Give me 5 profitable online business ideas in Ghana\')">Business Ideas</div><div class="chip" onclick="ask(\'Write a professional CV summary for me\')">Write a CV</div><div class="chip" onclick="ask(\'Give me useful websites for learning free skills\')">Useful Links</div></div></div>';
}

function ask(q) {
    document.getElementById("inp").value = q;
    send();
}

function fmt(t) {
    let s = t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
