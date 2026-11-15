<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CALMTECH AI</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:radial-gradient(circle at top left,#1e1b4b,#090d16 55%,#06283d);color:#f8fafc;height:100dvh;display:flex;flex-direction:column;overflow:hidden}
header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(15,23,42,.85);border-bottom:1px solid rgba(139,92,246,.3)}
.brand{font-size:22px;font-weight:900;letter-spacing:2px;background:linear-gradient(90deg,#38bdf8,#a855f7,#ec4899,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nbtn{background:rgba(139,92,246,.25);color:#e0f2fe;border:1px solid rgba(139,92,246,.5);padding:6px 12px;border-radius:20px;font-size:13px;font-weight:600;cursor:pointer;margin-left:6px}
#auth{position:fixed;inset:0;background:radial-gradient(circle at top,#1e1b4b,#090d16 70%);display:flex;align-items:center;justify-content:center;padding:16px;z-index:200}
.acard{width:100%;max-width:380px;background:rgba(15,23,42,.95);border:1px solid rgba(139,92,246,.5);border-radius:22px;padding:24px;box-shadow:0 20px 50px rgba(0,0,0,.7);text-align:center}
.atabs{display:flex;gap:8px;margin:16px 0}
.atab{flex:1;padding:9px;border-radius:14px;border:1px solid rgba(139,92,246,.4);background:#1e293b;color:#cbd5e1;font-weight:700;cursor:pointer}
.atab.on{background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;border-color:transparent}
.ainp{width:100%;padding:12px 14px;margin-bottom:10px;border-radius:14px;border:1px solid rgba(139,92,246,.45);background:#1e293b;color:#fff;font-size:14px;outline:none}
.abtn{width:100%;padding:12px;border:none;border-radius:16px;background:linear-gradient(135deg,#06b6d4,#6366f1);color:#fff;font-weight:800;font-size:15px;cursor:pointer;margin-top:4px}
.guest{margin-top:12px;font-size:13px;color:#38bdf8;cursor:pointer;text-decoration:underline;display:inline-block}
#aerr{color:#f87171;font-size:13px;margin-bottom:8px;min-height:18px}
#hp{display:none;position:fixed;top:56px;right:14px;width:270px;max-height:68vh;overflow-y:auto;background:#131936;border:1px solid #8b5cf6;border-radius:16px;padding:12px;z-index:100}
.hi{display:flex;justify-content:space-between;padding:8px 10px;margin-bottom:6px;background:#1e293b;border-radius:10px;cursor:pointer;font-size:13px}
.hi.act{border:1px solid #38bdf8}
.ad{background:rgba(9,13,22,.9);border-bottom:1px solid rgba(99,102,241,.25);min-height:58px;display:flex;align-items:center;justify-content:center;padding:4px}
#chat{flex:1;overflow-y:auto;padding:16px 14px;display:flex;flex-direction:column;gap:14px;max-width:820px;width:100%;margin:0 auto}
.w{margin:auto;text-align:center;padding:20px}
.wt{font-size:26px;font-weight:800;margin-bottom:8px;background:linear-gradient(90deg,#38bdf8,#c084fc,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.chip{display:inline-block;margin:4px;background:#1e293b;border:1px solid #8b5cf6;color:#e2e8f0;padding:8px 14px;border-radius:16px;font-size:13px;cursor:pointer}
.row{display:flex;width:100%}.u{justify-content:flex-end}.b{justify-content:flex-start}
.msg{padding:12px 16px;border-radius:18px;max-width:85%;line-height:1.55;font-size:15px;word-wrap:break-word;white-space:pre-wrap}
.u .msg{background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;border-bottom-right-radius:4px}
.b .msg{background:rgba(30,41,59,.88);color:#f1f5f9;border:1px solid rgba(148,163,184,.2);border-bottom-left-radius:4px}
.b a{color:#38bdf8;font-weight:600;text-decoration:underline}
.msg img{max-width:100%;max-height:240px;border-radius:12px;margin-bottom:6px;display:block}
.th{color:#c084fc;font-style:italic}
.bbar{background:rgba(15,23,42,.92);border-top:1px solid rgba(139,92,246,.3);padding:10px 14px 12px}
#pbar{display:none;max-width:820px;margin:0 auto 8px;background:rgba(124,58,237,.25);border:1px solid #a855f7;padding:5px 12px;border-radius:14px;font-size:13px;justify-content:space-between;align-items:center}
.iw{max-width:820px;margin:0 auto;display:flex;gap:6px;align-items:center;background:#1e293b;padding:6px 8px;border-radius:28px;border:1px solid rgba(139,92,246,.5)}
#pbtn{width:36px;height:36px;border-radius:50%;border:1px solid rgba(139,92,246,.6);background:rgba(139,92,246,.25);color:#fff;font-size:20px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#inp{flex:1;background:transparent;border:none;color:#fff;font-size:15px;outline:none;padding:0 4px}
#btn{background:linear-gradient(135deg,#06b6d4,#6366f1);color:#fff;border:none;padding:10px 18px;border-radius:22px;font-weight:700;cursor:pointer}
button:disabled{opacity:.45}
.foot{max-width:820px;margin:8px auto 0;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#94a3b8}
.share{background:linear-gradient(135deg,#10b981,#059669);color:#fff;padding:4px 12px;border-radius:12px;text-decoration:none;font-weight:700}
</style>
</head>
<body>
<div id="auth">
  <div class="acard">
    <div class="brand" style="font-size:28px">CALMTECH</div>
    <p style="color:#94a3b8;font-size:13px;margin-top:4px">Sign in to save your chats across sessions</p>
    <div class="atabs">
      <button id="t-in" class="atab on" onclick="setMode('in')">Log In</button>
      <button id="t-up" class="atab" onclick="setMode('up')">Sign Up</button>
    </div>
    <div id="aerr"></div>
    <input id="aname" class="ainp" placeholder="Full Name" style="display:none">
    <input id="aemail" class="ainp" type="email" placeholder="Email Address">
    <input id="apass" class="ainp" type="password" placeholder="Password" onkeypress="if(event.key==='Enter')doAuth()">
    <button id="asub" class="abtn" onclick="doAuth()">Log In</button>
    <div class="guest" onclick="useGuest()">Continue without account</div>
  </div>
</div>

<header>
  <div class="brand">CALMTECH</div>
  <div>
    <span id="uname" style="font-size:12px;color:#38bdf8;margin-right:4px"></span>
    <button class="nbtn" onclick="togH()">History</button>
    <button class="nbtn" onclick="newC()">+ New Chat</button>
  </div>
</header>

<div id="hp">
  <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-weight:700;color:#38bdf8">
    <span>Previous Chats</span>
    <span style="cursor:pointer" onclick="togH()">✕</span>
  </div>
  <div id="hl"></div>
  <button onclick="logout()" style="width:100%;margin-top:8px;padding:8px;border-radius:10px;border:1px solid #f87171;background:rgba(239,68,68,.15);color:#fca5a5;font-weight:700;cursor:pointer">Log Out / Switch Account</button>
</div>

<div class="ad">
  <script>
    atOptions = {'key':'ed327d85d05c1d6a827737110edd99bb','format':'iframe','height':50,'width':320,'params':{}};
  </script>
  <script src="https://bauval.org"></script>
</div>

<div id="chat"></div>

<div class="bbar">
  <div id="pbar">
    <span id="plbl">Image attached</span>
    <span style="cursor:pointer;color:#f87171;font-weight:bold;padding:0 6px" onclick="clrImg()">✕</span>
  </div>
  <div class="iw">
    <input type="file" id="fin" accept="image/*" style="display:none" onchange="pickImg(event)">
    <button id="pbtn" title="Upload image" onclick="document.getElementById('fin').click()">+</button>
    <input type="text" id="inp" placeholder="Ask anything or upload a photo..." onkeypress="if(event.key==='Enter')send()">
    <button id="btn" onclick="send()">Send</button>
  </div>
  <div class="foot">
    <span>CALMTECH AI</span>
    <a class="share" href="https://whatsapp.com" target="_blank">Share on WhatsApp</a>
  </div>
</div>

<script>
let mode = "in";
let curUser = localStorage.getItem("ct_active") || "";
let chats = {};
let sid = "u_" + Math.random().toString(36).slice(2, 10);
let upImg = null;

function setMode(m) {
  mode = m;
  document.getElementById("aerr").textContent = "";
  document.getElementById("t-in").className = "atab" + (m === "in" ? " on" : "");
  document.getElementById("t-up").className = "atab" + (m === "up" ? " on" : "");
  document.getElementById("aname").style.display = m === "up" ? "block" : "none";
  document.getElementById("asub").textContent = m === "up" ? "Create Account" : "Log In";
}

function doAuth() {
  const users = JSON.parse(localStorage.getItem("ct_users") || "{}");
  const em = document.getElementById("aemail").value.trim().toLowerCase();
  const pw = document.getElementById("apass").value;
  const nm = document.getElementById("aname").value.trim();
  const err = document.getElementById("aerr");
  if (!em || !pw) { err.textContent = "Please enter email and password."; return; }
  if (mode === "up") {
    if (!nm) { err.textContent = "Please enter your name."; return; }
    if (users[em]) { err.textContent = "Account already exists. Please log in."; return; }
    users[em] = { name: nm, pass: pw };
    localStorage.setItem("ct_users", JSON.stringify(users));
  } else {
    if (!users[em] || users[em].pass !== pw) { err.textContent = "Invalid email or password."; return; }
  }
  curUser = em;
  localStorage.setItem("ct_active", em);
  startApp();
}

function useGuest() {
  curUser = "guest";
  localStorage.setItem("ct_active", "guest");
  startApp();
}

function logout() {
  localStorage.removeItem("ct_active");
  curUser = "";
  document.getElementById("hp").style.display = "none";
  document.getElementById("auth").style.display = "flex";
}

function startApp() {
  const users = JSON.parse(localStorage.getItem("ct_users") || "{}");
  document.getElementById("auth").style.display = "none";
  document.getElementById("uname").textContent = curUser === "guest" ? "Guest" : (users[curUser]?.name || "");
  chats = JSON.parse(localStorage.getItem("ct_chats_" + curUser) || "{}");
  newC();
}

function pickImg(e) {
