"""
Voice AI Assistant - Telemetry & LLM Observability with Langfuse
Copyright (c) 2026 Vikash Kumar (@vik1989). All rights reserved.
Author: Vikash Kumar <vvik10072@gmail.com>
Repository: https://github.com/vik1989/voice-ai-app
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

logger = logging.getLogger("voice_ai.telemetry")

# Lazy-loaded Langfuse client singleton
_langfuse_client = None
_client_initialized = False

def get_client():
    global _langfuse_client, _client_initialized
    if _client_initialized:
        return _langfuse_client

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").strip()

    if not public_key or not secret_key:
        _langfuse_client = None
        _client_initialized = True
        return None

    try:
        from langfuse import Langfuse
        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        logger.info(f"Langfuse client initialized successfully with host: {host}")
    except Exception as e:
        logger.warning(f"Failed to initialize Langfuse client: {e}")
        _langfuse_client = None

    _client_initialized = True
    return _langfuse_client

def reload_client():
    """Forces reloading credentials and re-initializing the client."""
    global _langfuse_client, _client_initialized
    _client_initialized = False
    _langfuse_client = None
    return get_client()

def is_enabled() -> bool:
    return get_client() is not None

def get_telemetry_status() -> Dict[str, Any]:
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").strip()

    is_configured = bool(public_key and secret_key)
    masked_key = (
        f"{public_key[:6]}...{public_key[-4:]}"
        if len(public_key) > 10
        else ("Configured" if public_key else "Not Set")
    )

    return {
        "enabled": is_configured,
        "host": host,
        "public_key_masked": masked_key,
        "cloud_dashboard_url": f"{host.rstrip('/')}/project" if host.startswith("http") else None
    }

def log_turn(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    prompt_input: Any = None,
    response_text: Optional[str] = None,
    latency_ms: Optional[int] = None,
    usage: Optional[Dict[str, int]] = None,
    error: Optional[str] = None,
    client_info: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Logs an LLM generation and trace to Langfuse.
    Returns the trace_id if successful, or None if Langfuse is unconfigured or failed.
    Guaranteed non-blocking and safe from throwing uncaught exceptions.
    """
    client = get_client()
    if not client:
        return None

    try:
        from langfuse import propagate_attributes

        tags = [provider, "voice-ai"]
        if client_info and client_info.get("client_type"):
            tags.append(str(client_info["client_type"]))

        metadata = dict(client_info or {})
        if latency_ms is not None:
            metadata["latency_ms"] = latency_ms

        # Map usage dictionary to Langfuse standard usage keys ('input', 'output', 'total')
        usage_details = None
        if usage:
            usage_details = {}
            if "prompt_tokens" in usage:
                usage_details["input"] = usage["prompt_tokens"]
            elif "input" in usage:
                usage_details["input"] = usage["input"]

            if "completion_tokens" in usage:
                usage_details["output"] = usage["completion_tokens"]
            elif "output" in usage:
                usage_details["output"] = usage["output"]

            if "total_tokens" in usage:
                usage_details["total"] = usage["total_tokens"]
            elif "total" in usage:
                usage_details["total"] = usage["total"]
            elif "input" in usage_details and "output" in usage_details:
                usage_details["total"] = usage_details["input"] + usage_details["output"]

        with propagate_attributes(
            user_id=user_id or "anonymous-user",
            session_id=session_id,
            tags=tags,
            trace_name="voice_chat",
            metadata=metadata
        ):
            obs = client.start_observation(
                name=f"{provider}_inference",
                as_type="generation",
                input=prompt_input,
                model=model,
                metadata=metadata
            )

            if error:
                obs.update(
                    level="ERROR",
                    status_message=str(error)
                )
            else:
                obs.update(
                    output=response_text or "",
                    usage_details=usage_details
                )

            obs.end()
            return obs.trace_id

    except Exception as e:
        logger.warning(f"Error logging trace to Langfuse: {e}")
        return None

def record_feedback(trace_id: str, score: float, comment: Optional[str] = None) -> bool:
    """
    Records a user feedback score (1.0 = positive/thumbs up, 0.0 = negative/thumbs down) on a trace.
    Returns True if successfully recorded, False otherwise.
    """
    client = get_client()
    if not client or not trace_id:
        return False

    try:
        client.create_score(
            name="user_feedback",
            value=float(score),
            trace_id=trace_id,
            comment=comment
        )
        return True
    except Exception as e:
        logger.warning(f"Error submitting feedback score to Langfuse: {e}")
        return False
