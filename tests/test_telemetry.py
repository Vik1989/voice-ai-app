"""
Unit tests for Voice AI Assistant Langfuse telemetry module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import telemetry

class TestTelemetryModule(unittest.TestCase):

    def setUp(self):
        # Reset telemetry client before each test
        telemetry.reload_client()

    def test_unconfigured_fallback(self):
        with patch.dict(os.environ, {"LANGFUSE_PUBLIC_KEY": "", "LANGFUSE_SECRET_KEY": ""}):
            telemetry.reload_client()
            self.assertFalse(telemetry.is_enabled())
            status = telemetry.get_telemetry_status()
            self.assertFalse(status["enabled"])
            self.assertEqual(status["public_key_masked"], "Not Set")

            # Calling log_turn should return None gracefully without raising
            trace_id = telemetry.log_turn(
                session_id="test-session",
                user_id="test-user",
                provider="local",
                model="qwen2.5-coder:3b",
                prompt_input="Hello",
                response_text="Hi there!",
                latency_ms=120,
                usage={"prompt_tokens": 5, "completion_tokens": 8}
            )
            self.assertIsNone(trace_id)

            # Calling feedback should return False gracefully
            feedback_result = telemetry.record_feedback("fake-trace-id", 1.0)
            self.assertFalse(feedback_result)

    def test_telemetry_status_masked_key(self):
        with patch.dict(os.environ, {
            "LANGFUSE_PUBLIC_KEY": "pk-lf-1234567890abcdef",
            "LANGFUSE_SECRET_KEY": "sk-lf-abcdef1234567890",
            "LANGFUSE_HOST": "https://us.cloud.langfuse.com"
        }):
            status = telemetry.get_telemetry_status()
            self.assertTrue(status["enabled"])
            self.assertEqual(status["host"], "https://us.cloud.langfuse.com")
            self.assertTrue(status["public_key_masked"].startswith("pk-lf-"))
            self.assertTrue(status["public_key_masked"].endswith("cdef"))

    @patch("langfuse.Langfuse")
    def test_log_turn_when_configured(self, mock_langfuse_cls):
        mock_client = MagicMock()
        mock_obs = MagicMock()
        mock_obs.trace_id = "trace_abc_123"
        mock_client.start_observation.return_value = mock_obs
        mock_langfuse_cls.return_value = mock_client

        with patch.dict(os.environ, {
            "LANGFUSE_PUBLIC_KEY": "pk-lf-test",
            "LANGFUSE_SECRET_KEY": "sk-lf-test"
        }):
            telemetry.reload_client()
            self.assertTrue(telemetry.is_enabled())

            trace_id = telemetry.log_turn(
                session_id="sess_1",
                user_id="user_1",
                provider="gemini",
                model="gemini-2.0-flash",
                prompt_input=[{"role": "user", "content": "What is the weather?"}],
                response_text="It is sunny.",
                latency_ms=450,
                usage={"prompt_tokens": 12, "completion_tokens": 6},
                client_info={"client_type": "mobile"}
            )

            self.assertEqual(trace_id, "trace_abc_123")
            mock_client.start_observation.assert_called_once()
            mock_obs.update.assert_called_once()
            mock_obs.end.assert_called_once()

            # Test feedback scoring
            success = telemetry.record_feedback("trace_abc_123", 1.0, "Great answer")
            self.assertTrue(success)
            mock_client.create_score.assert_called_once_with(
                name="user_feedback",
                value=1.0,
                trace_id="trace_abc_123",
                comment="Great answer"
            )

if __name__ == "__main__":
    unittest.main()
