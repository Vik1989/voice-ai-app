#!/usr/bin/env bash
# Launcher for Voice AI Assistant
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Get local IP on Mac
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")

echo "============================================================"
echo "🎙️  Starting Voice AI Assistant Server..."
echo "============================================================"
echo "💻 Laptop Browser:   http://localhost:8000"
echo "📱 Phone (Local Wi-Fi): http://$LOCAL_IP:8000"
echo ""
echo "💡 Mobile Tip: To use your phone's microphone seamlessly,"
echo "   run in a separate terminal: npx localtunnel --port 8000"
echo "   and open the generated https:// link on your phone!"
echo "============================================================"

source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
