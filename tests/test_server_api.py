"""
API endpoint integration tests for Voice AI Assistant.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import server

class TestServerEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(server.app)

    def test_status_endpoint_includes_langfuse(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("langfuse", data)
        self.assertIn("enabled", data["langfuse"])
        self.assertIn("host", data["langfuse"])

    def test_feedback_endpoint_when_unconfigured(self):
        # When unconfigured, feedback endpoint should return unconfigured without crashing
        response = self.client.post("/api/feedback", json={
            "trace_id": "nonexistent_trace_123",
            "score": 1.0,
            "comment": "Nice voice"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "unconfigured")

    @patch("server.telemetry.log_turn")
    @patch("urllib.request.urlopen")
    def test_chat_endpoint_local_calls_telemetry(self, mock_urlopen, mock_log_turn):
        mock_log_turn.return_value = "mock_trace_789"
        
        # Mock Ollama HTTP response
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"message": {"content": "Hello Vikash!"}, "prompt_eval_count": 8, "eval_count": 14}'
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = None
        mock_urlopen.return_value = mock_resp

        response = self.client.post("/api/chat", json={
            "message": "Hello assistant",
            "provider": "local",
            "model": "qwen2.5-coder:3b",
            "session_id": "test_sess_1",
            "user_id": "test_user_1",
            "client_type": "mobile"
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "Hello Vikash!")
        self.assertEqual(data["provider"], "Local Device (Ollama)")
        self.assertEqual(data["trace_id"], "mock_trace_789")

        # Verify telemetry was called with exact token usage
        mock_log_turn.assert_called_once()
        _, kwargs = mock_log_turn.call_args
        self.assertEqual(kwargs["provider"], "local")
        self.assertEqual(kwargs["session_id"], "test_sess_1")
        self.assertEqual(kwargs["user_id"], "test_user_1")
        self.assertEqual(kwargs["usage"]["prompt_tokens"], 8)
        self.assertEqual(kwargs["usage"]["completion_tokens"], 14)
        self.assertEqual(kwargs["usage"]["total_tokens"], 22)

    @patch("server.telemetry.record_feedback")
    def test_feedback_endpoint_when_configured(self, mock_record_feedback):
        mock_record_feedback.return_value = True

        response = self.client.post("/api/feedback", json={
            "trace_id": "mock_trace_789",
            "score": 1.0,
            "comment": "Super fast!"
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        mock_record_feedback.assert_called_once_with("mock_trace_789", 1.0, "Super fast!")

if __name__ == "__main__":
    unittest.main()
