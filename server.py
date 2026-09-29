"""
Voice AI Assistant - Dual-Engine Voice Application
Copyright (c) 2026 Vikash Kumar (@vik1989). All rights reserved.
Author: Vikash Kumar <vvik10072@gmail.com>
Repository: https://github.com/vik1989/voice-ai-app
"""

import os
import time
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv, set_key
import telemetry

# Load environment variables from .env
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_FILE)

app = FastAPI(title="Voice AI Assistant Server")

# Serve static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "gemini"  # "gemini", "openai", or "local"
    model: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = []
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    client_type: Optional[str] = "web"

class ConfigUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_provider: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: Optional[str] = None

class FeedbackRequest(BaseModel):
    trace_id: str
    score: float  # 1.0 (thumbs up) or 0.0 (thumbs down)
    comment: Optional[str] = None

def get_local_ollama_models(ollama_url: str) -> List[str]:
    try:
        req = urllib.request.Request(f"{ollama_url}/api/tags")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

VOICE_SYSTEM_PROMPT = (
    "You are a friendly, intelligent voice AI assistant. "
    "Your responses will be read aloud by Text-to-Speech (TTS). "
    "Keep answers conversational, clear, helpful, and concise (usually 1-3 sentences unless asked for details). "
    "Avoid markdown tables, asterisks, bullet lists, or formatting that sounds robotic when spoken aloud."
)

@app.get("/api/status")
def get_system_status():
    load_dotenv(ENV_FILE)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    ollama_url = os.getenv("LOCAL_OLLAMA_URL", "http://localhost:11434")

    local_models = get_local_ollama_models(ollama_url)
    
    # Masked keys for security preview
    gemini_masked = f"{gemini_key[:4]}...{gemini_key[-4:]}" if len(gemini_key) > 8 else ("Configured" if gemini_key else "Not Set")
    openai_masked = f"{openai_key[:3]}...{openai_key[-4:]}" if len(openai_key) > 7 else ("Configured" if openai_key else "Not Set")

    default_prov = os.getenv("DEFAULT_PROVIDER", "gemini")
    # If gemini is not configured but local is available, smart default to local
    if default_prov == "gemini" and not gemini_key and local_models:
        default_prov = "local"

    return {
        "gemini_configured": bool(gemini_key),
        "gemini_masked": gemini_masked,
        "openai_configured": bool(openai_key),
        "openai_masked": openai_masked,
        "local_available": len(local_models) > 0,
        "local_models": local_models,
        "default_provider": default_prov,
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "local_model": os.getenv("LOCAL_MODEL", "qwen2.5-coder:3b"),
        "langfuse": telemetry.get_telemetry_status()
    }

@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    if req.gemini_api_key is not None:
        set_key(ENV_FILE, "GEMINI_API_KEY", req.gemini_api_key.strip())
    if req.openai_api_key is not None:
        set_key(ENV_FILE, "OPENAI_API_KEY", req.openai_api_key.strip())
    if req.default_provider is not None:
        set_key(ENV_FILE, "DEFAULT_PROVIDER", req.default_provider.strip())
    if req.langfuse_public_key is not None:
        set_key(ENV_FILE, "LANGFUSE_PUBLIC_KEY", req.langfuse_public_key.strip())
    if req.langfuse_secret_key is not None:
        set_key(ENV_FILE, "LANGFUSE_SECRET_KEY", req.langfuse_secret_key.strip())
    if req.langfuse_host is not None:
        set_key(ENV_FILE, "LANGFUSE_HOST", req.langfuse_host.strip())
    
    # Reload environment and telemetry client
    load_dotenv(ENV_FILE, override=True)
    telemetry.reload_client()
    return {"status": "success", "message": "Configuration updated successfully."}

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    success = telemetry.record_feedback(req.trace_id, req.score, req.comment)
    return {
        "status": "success" if success else "unconfigured",
        "message": "Feedback recorded." if success else "Langfuse is not configured or trace not found."
    }

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    load_dotenv(ENV_FILE)
    t0 = time.time()
    provider = (req.provider or os.getenv("DEFAULT_PROVIDER", "gemini")).lower()
    user_query = req.message.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    client_info = {"client_type": req.client_type or "web"}

    # 1. LOCAL OLLAMA ROUTE
    if provider == "local":
        ollama_url = os.getenv("LOCAL_OLLAMA_URL", "http://localhost:11434")
        model = req.model or os.getenv("LOCAL_MODEL", "qwen2.5-coder:3b")
        
        messages = [{"role": "system", "content": VOICE_SYSTEM_PROMPT}]
        for h in req.history[-6:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": user_query})

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.5}
        }).encode("utf-8")

        try:
            r = urllib.request.Request(f"{ollama_url}/api/chat", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(r, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data.get("message", {}).get("content", "")
                elapsed_ms = int((time.time() - t0) * 1000)

                prompt_tokens = data.get("prompt_eval_count", 0)
                completion_tokens = data.get("eval_count", 0)
                usage = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }

                trace_id = telemetry.log_turn(
                    session_id=req.session_id,
                    user_id=req.user_id,
                    provider="local",
                    model=model,
                    prompt_input=messages,
                    response_text=reply_text,
                    latency_ms=elapsed_ms,
                    usage=usage,
                    client_info=client_info
                )

                return {
                    "response": reply_text,
                    "provider": "Local Device (Ollama)",
                    "model": model,
                    "latency_ms": elapsed_ms,
                    "trace_id": trace_id
                }
        except Exception as e:
            telemetry.log_turn(
                session_id=req.session_id,
                user_id=req.user_id,
                provider="local",
                model=model,
                prompt_input=messages,
                latency_ms=int((time.time() - t0) * 1000),
                error=str(e),
                client_info=client_info
            )
            raise HTTPException(status_code=502, detail=f"Local Ollama error: {e}. Is Ollama running?")

    # 2. GOOGLE GEMINI CLOUD ROUTE
    elif provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY is not configured in .env. Please add it to use Cloud Mode.")

        model = req.model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"

        # Construct contents with history
        contents = []
        # Add system instruction as prefix or content
        contents.append({
            "role": "user",
            "parts": [{"text": f"SYSTEM INSTRUCTION: {VOICE_SYSTEM_PROMPT}"}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. I will answer as a voice assistant concisely and naturally."}]
        })

        for h in req.history[-6:]:
            role = "user" if h.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})
        
        contents.append({"role": "user", "parts": [{"text": user_query}]})

        payload = json.dumps({
            "contents": contents,
            "generationConfig": {
                "temperature": 0.6,
                "maxOutputTokens": 400
            }
        }).encode("utf-8")

        try:
            r = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(r, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError("No response returned from Gemini API.")
                reply_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                elapsed_ms = int((time.time() - t0) * 1000)

                usage_meta = data.get("usageMetadata", {})
                usage = {
                    "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                    "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                    "total_tokens": usage_meta.get("totalTokenCount", 0)
                }

                trace_id = telemetry.log_turn(
                    session_id=req.session_id,
                    user_id=req.user_id,
                    provider="gemini",
                    model=model,
                    prompt_input=contents,
                    response_text=reply_text,
                    latency_ms=elapsed_ms,
                    usage=usage,
                    client_info=client_info
                )

                return {
                    "response": reply_text,
                    "provider": "Google Gemini",
                    "model": model,
                    "latency_ms": elapsed_ms,
                    "trace_id": trace_id
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            telemetry.log_turn(
                session_id=req.session_id,
                user_id=req.user_id,
                provider="gemini",
                model=model,
                prompt_input=contents,
                latency_ms=int((time.time() - t0) * 1000),
                error=f"Gemini API Error {e.code}: {err_body}",
                client_info=client_info
            )
            raise HTTPException(status_code=e.code, detail=f"Gemini API Error: {err_body}")
        except Exception as e:
            telemetry.log_turn(
                session_id=req.session_id,
                user_id=req.user_id,
                provider="gemini",
                model=model,
                prompt_input=contents,
                latency_ms=int((time.time() - t0) * 1000),
                error=str(e),
                client_info=client_info
            )
            raise HTTPException(status_code=500, detail=f"Gemini Request Failed: {e}")

    # 3. OPENAI CLOUD ROUTE
    elif provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_key:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured in .env.")

        model = req.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = "https://api.openai.com/v1/chat/completions"

        messages = [{"role": "system", "content": VOICE_SYSTEM_PROMPT}]
        for h in req.history[-6:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": user_query})

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 300
        }).encode("utf-8")

        try:
            r = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            })
            with urllib.request.urlopen(r, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                elapsed_ms = int((time.time() - t0) * 1000)

                usage_meta = data.get("usage", {})
                usage = {
                    "prompt_tokens": usage_meta.get("prompt_tokens", 0),
                    "completion_tokens": usage_meta.get("completion_tokens", 0),
                    "total_tokens": usage_meta.get("total_tokens", 0)
                }

                trace_id = telemetry.log_turn(
                    session_id=req.session_id,
                    user_id=req.user_id,
                    provider="openai",
                    model=model,
                    prompt_input=messages,
                    response_text=reply_text,
                    latency_ms=elapsed_ms,
                    usage=usage,
                    client_info=client_info
                )

                return {
                    "response": reply_text,
                    "provider": "OpenAI",
                    "model": model,
                    "latency_ms": elapsed_ms,
                    "trace_id": trace_id
                }
        except Exception as e:
            telemetry.log_turn(
                session_id=req.session_id,
                user_id=req.user_id,
                provider="openai",
                model=model,
                prompt_input=messages,
                latency_ms=int((time.time() - t0) * 1000),
                error=str(e),
                client_info=client_info
            )
            raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")

    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider '{provider}'")
