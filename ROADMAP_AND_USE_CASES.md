# 🧠 Voice AI Assistant: Permanent Memory & Project Blueprint

This document preserves the complete technical architecture, security safeguards, mobile access workflows, and future capability roadmap for **Voice AI Assistant**.

---

## 📌 Project Summary & Quick Links

* **GitHub Repository:** [https://github.com/vik1989/voice-ai-app](https://github.com/vik1989/voice-ai-app)
* **Active Branches:**
  * `main` — 🔒 Production-ready release branch (Protected: No deletions, No force-pushes, Secret scanning enabled).
  * `develop` — 🌿 Active development branch (All day-to-day coding happens here).
* **Local Project Path:** [`/Users/vikashkumar/voice-ai-app/`](file:///Users/vikashkumar/voice-ai-app/)
* **Local Web Address:** [http://localhost:8000](http://localhost:8000) (and `http://192.168.1.9:8000` on Wi-Fi).
* **Launcher Script:** [`~/voice-ai-app/run.sh`](file:///Users/vikashkumar/voice-ai-app/run.sh)

---

## 🏛️ System Architecture

```
                               ┌─── [Microphone Audio] ───┐
                               │                          │
                               ▼                          ▼
                     [Speech Recognition]       [Audio Visualizer]
                               │                          │
                               ▼                          │
                     ┌──────────────────┐                 │
                     │ Engine Switcher  │                 │
                     └────────┬─────────┘                 │
                              │                           │
            ┌─────────────────┴─────────────────┐         │
            ▼                                   ▼         │
  [🖥️ Local Device Mode]              [☁️ Cloud API Mode] │
  • Auto-detects local Ollama        • Google Gemini /    │
  • e.g. qwen2.5-coder:3b             OpenAI API         │
  • 100% Free & Offline              • Sub-second cloud   │
            │                                   │         │
            └─────────────────┬─────────────────┘         │
                              ▼                           │
                     [Text-to-Speech (TTS)]               │
                              │                           │
                              ▼                           ▼
                     ┌─── [Speaker Audio Output] ◄────────┘
```

---

## 🔒 Security & Ownership Safeguards

1. **API Keys Isolation:**
   * Keys are stored exclusively in `.env` (configured for Google Gemini or OpenAI).
   * `.gitignore` explicitly excludes `.env` — **it will never be tracked or committed to GitHub**.
   * `.env.example` serves as the public template.
2. **Authorship & Legal Protection:**
   * Standard [**`NOTICE`**](file:///Users/vikashkumar/voice-ai-app/NOTICE) file and [**`LICENSE`**](file:///Users/vikashkumar/voice-ai-app/LICENSE) asserting copyright:
     `Copyright (c) 2026 Vikash Kumar (@vik1989) <vvik10072@gmail.com>`
   * Embedded code headers in [`server.py`](file:///Users/vikashkumar/voice-ai-app/server.py) and author meta tags in [`static/index.html`](file:///Users/vikashkumar/voice-ai-app/static/index.html).
3. **GitHub Branch Protection:**
   * `allow_deletions: false` (cannot delete `main`).
   * `allow_force_pushes: false` (history cannot be overwritten).
   * `secret_scanning_push_protection: enabled` (GitHub rejects any push containing exposed secrets).

---

## 📱 Mobile Setup & Microphone Solutions

Mobile browsers (Chrome/Safari) block microphone access on plain HTTP IP addresses (`http://192.168.1.9:8000`).

### Proven Workarounds:
* **Option A (Local Wi-Fi Only - 30s Setup):**
  1. On Android Chrome, open: `chrome://flags/#unsafely-treat-insecure-origin-as-secure`
  2. Add: `http://192.168.1.9:8000`
  3. Set to **Enabled** and tap **Relaunch**.
  4. Microphone permissions will now be prompted and allowed!
* **Option B (Zero Phone Setup via Mac Tunnel):**
  1. In a Mac terminal, run: `ssh -R 80:localhost:8000 nokey@localhost.run`
  2. Open the resulting `https://...` link on your phone.
* **PWA Install:** In mobile Chrome, tap **three dots (⋮)** $\rightarrow$ **"Add to Home screen"** to install as an app icon.

---

## 🗺️ Future Capabilities Roadmap (Top 6 Use Cases)

When returning to this project, here are the ready-to-build capability modules:

| # | Use Case | Description | Tech Strategy |
| :--- | :--- | :--- | :--- |
| **1** | **👨‍💻 Hands-Free Dev & Git** | Inspect git commits, check build error logs, or trigger test runs by voice while pacing. | Python tool calling (`git log`, `pytest`, `cat`) |
| **2** | **📝 Smart Voice Notes & Standup** | Dictate voice memos, store in local SQLite/Markdown, and auto-generate daily 3-bullet standup summaries. | SQLite / Markdown storage in `~/voice-ai-app/notes/` |
| **3** | **🌐 Live Web Search Grounding** | Voice search for live weather, breaking news, stock prices, or current tech facts. | Gemini Google Search grounding / DuckDuckGo API |
| **4** | **🗣️ Language Tutor & Mock Interview** | Spoken roleplay (e.g. practicing Spanish at a cafe, or Senior System Design interview prep). | Persona system prompts + multilingual TTS |
| **5** | **📚 "Talk to Your Documents"** | Drop a PDF/whitepaper on the Mac and converse about it by voice on your phone. | Text extraction + Semantic RAG pipeline |
| **6** | **💻 Mac System & Media Commander** | Voice control Mac volume, Spotify playback, or set countdown timers. | macOS `osascript` (AppleScript) bridge |

---

## ⚡ Quick Cheat Sheet to Resume

```bash
# 1. Start the Voice AI Server:
~/voice-ai-app/run.sh

# 2. Daily development workflow:
cd ~/voice-ai-app
git checkout develop
# ... make edits ...
git add .
git commit -m "Add new feature"
git push origin develop

# 3. Release to production (main):
# Open a Pull Request at: https://github.com/Vik1989/voice-ai-app/pull/new/develop
```
