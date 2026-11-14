from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

CALMTECH_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "You are CALMTECH, a helpful, intelligent, and versatile AI assistant. "
        "NEVER introduce yourself, say your name, or mention your creator's name unless the user "
        "specifically asks who you are or who created, built, or owns you. "
        "Only if asked who created, built, or owns you, state clearly that you were created by Samuel Frimpong. "
        "Answer any question directly and clearly, analyze uploaded photos and videos in detail, "
        "help users solve problems, write code, and brainstorm ideas. "
        "When sharing helpful websites or resources, always format them as clickable markdown links like [Site Name](https://example.com). "
        "Use clear bullet points and bold headings when helpful."
    )
)

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
user_sessions = {}

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CALMTECH AI</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 780px;
            margin: 0 auto;
            padding: 12px;
            min-height: 100vh;
            background: linear-gradient(135deg, #090d16 0%, #17123b 45%, #0f2942 100%);
            color: #f8fafc;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 6px;
        }
        h1 {
            margin: 0;
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 2px;
            background: linear-gradient(90deg, #38bdf8, #a855f7, #ec4899, #f59e0b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .badge {
            background: linear-gradient(90deg, rgba(56,189,248,0.18), rgba(168,85,247,0.18));
            color: #e0f2fe;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(168,85,247,0.45);
        }
        .ad-slot {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(99, 102, 241, 0.35);
            padding: 6px;
            text-align: center;
            margin: 8px 0;
            border-radius: 12px;
            min-height: 62px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        #chat-box {
            background: rgba(15, 23, 42, 0.78);
            backdrop-filter: blur(12px);
            height: 55vh;
            overflow-y: auto;
            padding: 16px;
            border-radius: 18px;
            border: 1px solid rgba(139, 92, 246, 0.35);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg {
            padding: 12px 16px;
            border-radius: 16px;
            max-width: 85%;
            line-height: 1.5;
            font-size: 15px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        .user {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.35);
        }
        .bot {
            background: linear-gradient(135deg, #1e293b, #28214d);
            color: #f1f5f9;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }
        .bot a { color: #38bdf8; font-weight: bold; text-decoration: underline; }
        .msg img, .msg video {
            max-width: 100%;
            max-height: 220px;
            border-radius: 10px;
            margin-bottom: 6px;
            display: block;
        }
        .thinking { font-style: italic; color: #c084fc; }
        #preview-bar {
            display: none;
            align-items: center;
            justify-content: space-between;
            background: rgba(124, 58, 237, 0.25);
            border: 1px solid #a855f7;
            padding: 6px 12px;
            border-radius: 12px;
            margin-top: 8px;
            font-size: 13px;
            color: #f3e8ff;
        }
        .remove-file {
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 50%;
            width: 22px;
            height: 22px;
            cursor: pointer;
            font-weight: bold;
            padding: 0;
        }
        #input-area {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            align-items: center;
        }
        .media-btn {
            padding: 12px 14px;
            background: linear-gradient(135deg, #ec4899, #8b5cf6);
            color: white;
            border: none;
            border-radius: 24px;
            font-weight: bold;
            cursor: pointer;
            font-size: 14px;
            white-space: nowrap;
        }
        input[type="text"] {
            flex: 1;
            padding: 13px 16px;
            border-radius: 24px;
            border: 1px solid rgba(139, 92, 246, 0.5);
            background: rgba(15, 23, 42, 0.85);
            color: white;
            font-size: 15px;
            outline: none;
        }
        input[type="text"]:focus { border-color: #38bdf8; }
        #send-btn {
            padding: 12px 22px;
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            color: white;
            border: none;
            border-radius: 24px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .share-bar {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 10px;
            text-align: center;
            margin: 10px 0 6px 0;
            border-radius: 12px;
            font-size: 13px;
            color: #cbd5e1;
        }
        .share-btn {
            display: inline-block;
            margin-left: 8px;
            padding: 6px 14px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border-radius: 16px;
            text-decoration: none;
            font-weight: bold;
            font-size: 12px;
        }
        footer { text-align: center; font-size: 12px; color: #94a3b8; margin-top: 6px; }
    </style>
</head>
<body>
    <header>
        <h1>CALMTECH</h1>
        <span class="badge">Text • Photo • Video AI</span>
    </header>

    <!-- AD 1: ADSTERRA 320x50 TOP BANNER -->
    <div class="ad-slot" id="top-ad">
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

    <div id="chat-box">
        <div class="msg bot">How can I help you today? You can ask any question or upload a photo or short video!</div>
    </div>

    <!-- SELECTED PHOTO/VIDEO PREVIEW -->
    <div id="preview-bar">
        <span id="file-label">Selected file</span>
        <button class="remove-file" onclick="clearMedia()" title="Remove">×</button>
    </div>

    <div id="input-area">
        <input type="file" id="media-input" accept="image/*,video/*" style="display:none" onchange="handleFileSelect(event)" />
        <button class="media-btn" id="media-btn" onclick="document.getElementById('media-input').click()">+ Photo/Video</button>
        <input type="text" id="user-input" placeholder="Ask anything or describe your photo/video..." onkeypress="if(event.key==='Enter') sendMessage()" />
        <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>

    <!-- VIRAL SHARE BAR -->
    <div class="share-bar">
        Share with friends:
        <a class="share-btn" href="https://whatsapp.com" target="_blank">Share on WhatsApp</a>
    </div>

    <footer>CALMTECH AI</footer>

    <script>
        const sessionId = "user_" + Math.random().toString(36).substring(2, 12);
        let selectedMedia = null;

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            if (file.size > 15 * 1024 * 1024) {
                alert("Please choose a photo or short video under 15 MB.");
                event.target.value = "";
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                const dataUrl = e.target.result;
                const base64Data = dataUrl.split(",")[1];
                selectedMedia = {
                    name: file.name,
                    mime_type: file.type,
                    data: base64Data,
                    preview_url: dataUrl
                };
                document.getElementById("file-label").textContent = "Attached: " + file.name;
                document.getElementById("preview-bar").style.display = "flex";
            };
            reader.readAsDataURL(file);
        }

