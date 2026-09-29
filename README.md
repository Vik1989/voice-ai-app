# 🎙️ Voice AI Assistant

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black.svg)](https://ollama.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Cloud%20AI-orange.svg)](https://aistudio.google.com/)
[![PWA Ready](https://img.shields.io/badge/PWA-Android%20%26%20iOS-purple.svg)](#-mobile-pwa-installation-android--ios)

A modern, responsive, voice-first AI assistant built with a **dual-engine architecture**:
* **🖥️ Local Device Mode:** Powered by on-device [Ollama](https://ollama.com/) (`qwen2.5-coder:3b`, `llama3.2`, etc.) for **100% free, private, offline** voice conversations on your laptop.
* **☁️ Cloud API Mode:** Powered by **Google Gemini** (or OpenAI) for fast, lightweight voice interactions when accessing from your mobile phone.
* **📱 Mobile-First PWA:** Open on Android Chrome or iOS Safari and tap **"Add to Home Screen"** to install it as an app icon with native full-screen support.

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

## ✨ Features

- **🎙️ Natural Voice Interaction:** Integrated Web Speech API for real-time speech-to-text and instant speech synthesis.
- **⚡ Dual-Engine Flexibility:** Auto-detects local Ollama models on your machine; falls back gracefully to Cloud APIs when roaming or using a phone.
- **🛑 Tap-to-Interrupt:** Interrupt the assistant at any moment while it is speaking by tapping the glowing voice orb.
- **💬 Dual-Mode Input:** Voice-first with a text input fallback for quiet or noisy environments.
- **🔒 Zero-Leak Security:** API keys are isolated in `.env` and strictly excluded by `.gitignore` — keys will never be committed to Git.
- **📱 PWA Ready:** Manifest included to install directly onto Android & iOS home screens.

---

## 🚀 Quick Start

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Vik1989/voice-ai-app.git
cd voice-ai-app

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy the template file:
```bash
cp .env.example .env
```
Open `.env` and insert your API keys (optional if running only with local Ollama):
```env
# Get a free API key at: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_key_here

# Optional: OpenAI key
OPENAI_API_KEY=your_openai_key_here

# Default Provider: "gemini", "local", or "openai"
DEFAULT_PROVIDER=gemini
```

### 3. Start the Server
```bash
chmod +x run.sh
./run.sh
```
The server will start at:
* **Local Laptop Browser:** `http://localhost:8000`
* **Local Network (Wi-Fi):** `http://<your-ip>:8000`

---

## 📱 Mobile PWA Installation (Android & iOS)

### Step 1: Secure Tunnel (Microphone Permissions)
Mobile browsers strictly enforce an HTTPS connection to grant microphone permissions. In a separate terminal, launch a secure tunnel:

```bash
# Using SSH (Zero-install, built into macOS/Linux):
ssh -R 80:localhost:8000 nokey@localhost.run

# OR using Cloudflare / Localtunnel:
npx localtunnel --port 8000
```

### Step 2: Install as a Mobile App
1. Open the generated `https://...` link in **Google Chrome** on your Android phone.
2. Tap the Chrome menu (**three dots** in the top right) $\rightarrow$ Tap **"Add to Home screen"** (or "Install app").
3. **Voice AI** will appear on your home screen. Tap it to launch full-screen like a native Android app!

---

## ⚙️ Configuration Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Key (from AI Studio) | `""` |
| `OPENAI_API_KEY` | OpenAI API Key (from OpenAI platform) | `""` |
| `DEFAULT_PROVIDER` | Initial active provider (`gemini`, `local`, `openai`) | `gemini` |
| `GEMINI_MODEL` | Gemini model variant | `gemini-2.0-flash` |
| `OPENAI_MODEL` | OpenAI model variant | `gpt-4o-mini` |
| `LOCAL_MODEL` | Local Ollama model name | `qwen2.5-coder:3b` |
| `LOCAL_OLLAMA_URL` | Local Ollama endpoint | `http://localhost:11434` |

---

## 🗺️ Roadmap (Phase 2)
- [ ] Tool calling / Function calling (Live weather, search, calculations).
- [ ] Dedicated neural TTS backend (Kokoro-82M / ElevenLabs) for studio voice quality.
- [ ] Wake-word detection ("Hey Assistant").
- [ ] Native Android APK build via Kotlin / Jetpack Compose.

---

## 👤 Author & Ownership

* **Creator & Maintainer:** **Vikash Kumar** ([@vik1989](https://github.com/vik1989))
* **Email:** [vvik10072@gmail.com](mailto:vvik10072@gmail.com)
* **GitHub Repository:** [https://github.com/vik1989/voice-ai-app](https://github.com/vik1989/voice-ai-app)
* **Copyright:** © 2026 Vikash Kumar. All rights reserved.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE) with attribution requirements described in the [NOTICE](NOTICE) file.
