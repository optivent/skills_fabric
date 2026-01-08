"""Unit tests for GLM client API integration.

This module tests the GLM client implementation:
- Coding endpoint configuration (https://api.z.ai/api/coding/paas/v4)
- Thinking mode toggle (enabled, disabled, preserved)
- Response parsing (content, thinking, token usage)
- Error handling and fallback behavior

Test coverage includes:
- GLMConfig dataclass and from_env()
- GLMClient endpoint configuration
- TokenUsage calculations
- GLMResponse properties
- Thinking budget handling
- ReasoningFailureType detection
- Fallback to non-thinking mode
- GLMCodingAgent multi-turn conversations
- Streaming support (StreamChunk, StreamingStats)
"""
from __future__ import annotations

import importlib.util
import os
import sys
import json
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Import glm_client module directly to avoid heavy dependencies from skills_fabric.__init__
_src_path = Path(__file__).parent.parent / "src"

# First, ensure observability.logging is available (glm_client may depend on it via logger)
_logging_path = _src_path / "skills_fabric" / "observability" / "logging.py"
if _logging_path.exists():
    _logging_spec = importlib.util.spec_from_file_location("skills_fabric.observability.logging", _logging_path)
    _logging_module = importlib.util.module_from_spec(_logging_spec)
    sys.modules["skills_fabric.observability.logging"] = _logging_module
    _logging_spec.loader.exec_module(_logging_module)

# Now import the glm_client module
_glm_client_path = _src_path / "skills_fabric" / "llm" / "glm_client.py"
_spec = importlib.util.spec_from_file_location("skills_fabric.llm.glm_client", _glm_client_path)
_glm_client_module = importlib.util.module_from_spec(_spec)
sys.modules["skills_fabric.llm.glm_client"] = _glm_client_module
_spec.loader.exec_module(_glm_client_module)

# Import classes we need to test
GLMClient = _glm_client_module.GLMClient
GLMConfig = _glm_client_module.GLMConfig
GLMResponse = _glm_client_module.GLMResponse
GLMCodingAgent = _glm_client_module.GLMCodingAgent
GLMOpenAIWrapper = _glm_client_module.GLMOpenAIWrapper
TokenUsage = _glm_client_module.TokenUsage
ThinkingMode = _glm_client_module.ThinkingMode
ReasoningFailureType = _glm_client_module.ReasoningFailureType
ReasoningMetrics = _glm_client_module.ReasoningMetrics
StreamChunk = _glm_client_module.StreamChunk
StreamingStats = _glm_client_module.StreamingStats
StreamInterruptionType = _glm_client_module.StreamInterruptionType
CODING_BASE_URL = _glm_client_module.CODING_BASE_URL
GENERAL_BASE_URL = _glm_client_module.GENERAL_BASE_URL


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_api_response() -> dict:
    """Create a mock API response."""
    return {
        "id": "cmpl-test-123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "glm-4.7",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a test response.",
                "reasoning_content": "I analyzed the input and determined the answer.",
            },
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "thinking_tokens": 200,
            "total_tokens": 350,
        },
    }


@pytest.fixture
def mock_api_response_no_thinking() -> dict:
    """Create a mock API response without thinking content."""
    return {
        "id": "cmpl-test-456",
        "model": "glm-4.7",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Simple response without thinking.",
            },
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80,
        },
    }


@pytest.fixture
def mock_api_error_response() -> dict:
    """Create a mock API error response."""
    return {
        "error": {
            "message": "Invalid API key",
            "type": "authentication_error",
            "code": "invalid_api_key",
        },
    }


@pytest.fixture
def sample_messages() -> list[dict]:
    """Create sample messages for API calls."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain this code."},
    ]


@pytest.fixture
def glm_config() -> GLMConfig:
    """Create a GLMConfig with test values."""
    return GLMConfig(
        api_key="test-api-key-12345",
        base_url=CODING_BASE_URL,
        model="glm-4.7",
        use_coding_endpoint=True,
        max_tokens=4096,
        temperature=1.0,
        top_p=0.95,
        timeout=120,
        thinking_mode=ThinkingMode.ENABLED,
        thinking_budget=16000,
    )


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("ZAI_API_KEY", "env-test-api-key")
    monkeypatch.setenv("GLM_MODEL", "glm-4.7-test")
    monkeypatch.setenv("GLM_THINKING_BUDGET", "24000")


@pytest.fixture
def clean_env_vars(monkeypatch):
    """Remove API key environment variables."""
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.delenv("GLM_API_KEY", raising=False)


# =============================================================================
# GLMConfig Tests
# =============================================================================


class TestGLMConfig:
    """Test GLMConfig dataclass and configuration."""

    def test_default_config_values(self):
        """Test GLMConfig default values."""
        config = GLMConfig()

        assert config.api_key == ""
        assert config.base_url == CODING_BASE_URL
        assert config.model == "glm-4.7"
        assert config.use_coding_endpoint is True
        assert config.max_tokens == 4096
        assert config.temperature == 1.0
        assert config.top_p == 0.95
        assert config.timeout == 120
        assert config.thinking_mode == ThinkingMode.ENABLED
        assert config.thinking_budget == 16000

    def test_config_custom_values(self, glm_config: GLMConfig):
        """Test GLMConfig with custom values."""
        assert glm_config.api_key == "test-api-key-12345"
        assert glm_config.base_url == CODING_BASE_URL
        assert glm_config.model == "glm-4.7"
        assert glm_config.thinking_budget == 16000

    def test_config_from_env(self, mock_env_vars):
        """Test GLMConfig.from_env() loads from environment."""
        config = GLMConfig.from_env()

        assert config.api_key == "env-test-api-key"
        assert config.model == "glm-4.7-test"
        assert config.thinking_budget == 24000

    def test_config_from_env_without_api_key(self, clean_env_vars):
        """Test GLMConfig.from_env() without API key."""
        config = GLMConfig.from_env()

        assert config.api_key == ""

    def test_config_from_env_coding_endpoint(self, mock_env_vars):
        """Test GLMConfig.from_env() uses coding endpoint by default."""
        config = GLMConfig.from_env(use_coding_endpoint=True)

        assert config.use_coding_endpoint is True
        assert CODING_BASE_URL in config.base_url

    def test_config_from_env_general_endpoint(self, mock_env_vars):
        """Test GLMConfig.from_env() can use general endpoint."""
        config = GLMConfig.from_env(use_coding_endpoint=False)

        assert config.use_coding_endpoint is False
        assert GENERAL_BASE_URL in config.base_url


class TestCodingEndpointConfiguration:
    """Test that the CODING endpoint is used correctly."""

    def test_coding_base_url_value(self):
        """Test that CODING_BASE_URL has correct value."""
        assert CODING_BASE_URL == "https://api.z.ai/api/coding/paas/v4"

    def test_general_base_url_value(self):
        """Test that GENERAL_BASE_URL has correct value."""
        assert GENERAL_BASE_URL == "https://api.z.ai/api/paas/v4"

    def test_default_endpoint_is_coding(self):
        """Test that default endpoint is coding endpoint."""
        config = GLMConfig(api_key="test")
        assert config.base_url == CODING_BASE_URL

    def test_client_uses_coding_endpoint_by_default(self):
        """Test that GLMClient uses coding endpoint by default."""
        client = GLMClient(api_key="test-key")

        assert CODING_BASE_URL in client.endpoint
        assert "/chat/completions" in client.endpoint

    def test_client_endpoint_property(self):
        """Test client endpoint property returns full URL."""
        client = GLMClient(api_key="test-key")
        expected = f"{CODING_BASE_URL}/chat/completions"

        assert client.endpoint == expected


# =============================================================================
# TokenUsage Tests
# =============================================================================


class TestTokenUsage:
    """Test TokenUsage dataclass and calculations."""

    def test_token_usage_defaults(self):
        """Test TokenUsage default values."""
        usage = TokenUsage()

        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.thinking_tokens == 0
        assert usage.total_tokens == 0
        assert usage.thinking_budget == 0

    def test_token_usage_with_values(self):
        """Test TokenUsage with actual values."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            thinking_tokens=200,
            total_tokens=350,
            thinking_budget=16000,
        )

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.thinking_tokens == 200
        assert usage.total_tokens == 350
        assert usage.thinking_budget == 16000

    def test_cost_usd_calculation(self):
        """Test cost calculation in USD."""
        usage = TokenUsage(
            prompt_tokens=1_000_000,  # 1M input tokens
            completion_tokens=500_000,  # 500K output tokens
            thinking_tokens=500_000,  # 500K thinking tokens
        )

        # Input: 1M * $0.60/M = $0.60
        # Output: 1M * $2.20/M = $2.20
        # Total: $2.80
        expected_cost = 0.60 + 2.20
        assert abs(usage.cost_usd - expected_cost) < 0.01

    def test_thinking_budget_used_pct_calculation(self):
        """Test thinking budget percentage calculation."""
        usage = TokenUsage(
            thinking_tokens=8000,
            thinking_budget=16000,
        )

        assert usage.thinking_budget_used_pct == 50.0

    def test_thinking_budget_used_pct_no_budget(self):
        """Test thinking budget percentage when no budget set."""
        usage = TokenUsage(
            thinking_tokens=1000,
            thinking_budget=0,
        )

        assert usage.thinking_budget_used_pct == 0.0

    def test_thinking_budget_used_pct_cap_at_100(self):
        """Test thinking budget percentage caps at 100%."""
        usage = TokenUsage(
            thinking_tokens=20000,  # Over budget
            thinking_budget=16000,
        )

        assert usage.thinking_budget_used_pct == 100.0

    def test_thinking_budget_exhausted_true(self):
        """Test thinking_budget_exhausted when budget is used up."""
        usage = TokenUsage(
            thinking_tokens=15500,  # > 95% of 16000
            thinking_budget=16000,
        )

        assert usage.thinking_budget_exhausted is True

    def test_thinking_budget_exhausted_false(self):
        """Test thinking_budget_exhausted when budget has room."""
        usage = TokenUsage(
            thinking_tokens=8000,  # 50% of budget
            thinking_budget=16000,
        )

        assert usage.thinking_budget_exhausted is False

    def test_thinking_budget_exhausted_no_budget(self):
        """Test thinking_budget_exhausted when no budget."""
        usage = TokenUsage(thinking_budget=0)

        assert usage.thinking_budget_exhausted is False


# =============================================================================
# GLMResponse Tests
# =============================================================================


class TestGLMResponse:
    """Test GLMResponse dataclass and properties."""

    def test_response_defaults(self):
        """Test GLMResponse default values."""
        response = GLMResponse(content="Test content")

        assert response.content == "Test content"
        assert response.thinking is None
        assert response.finish_reason == "stop"
        assert response.model == "glm-4.7"
        assert response.latency_ms == 0.0
        assert response.used_fallback is False
        assert response.fallback_reason == ReasoningFailureType.NONE

    def test_has_thinking_true(self):
        """Test has_thinking property when thinking present."""
        response = GLMResponse(
            content="Test",
            thinking="Reasoning content here",
        )

        assert response.has_thinking is True

    def test_has_thinking_false_none(self):
        """Test has_thinking property when thinking is None."""
        response = GLMResponse(content="Test", thinking=None)

        assert response.has_thinking is False

    def test_has_thinking_false_empty(self):
        """Test has_thinking property when thinking is empty."""
        response = GLMResponse(content="Test", thinking="")

        assert response.has_thinking is False

    def test_thinking_truncated_property(self):
        """Test thinking_truncated delegates to usage."""
        usage = TokenUsage(thinking_tokens=15500, thinking_budget=16000)
        response = GLMResponse(content="Test", usage=usage)

        assert response.thinking_truncated is True

    def test_reasoning_quality_excellent(self):
        """Test reasoning_quality returns 'excellent' when budget has room."""
        usage = TokenUsage(thinking_tokens=8000, thinking_budget=16000)  # 50%
        response = GLMResponse(
            content="Test",
            thinking="Reasoning...",
            usage=usage,
        )

        assert response.reasoning_quality == "excellent"

    def test_reasoning_quality_good(self):
        """Test reasoning_quality returns 'good' when >80% budget used."""
        usage = TokenUsage(thinking_tokens=13000, thinking_budget=16000)  # 81%
        response = GLMResponse(
            content="Test",
            thinking="Reasoning...",
            usage=usage,
        )

        assert response.reasoning_quality == "good"

    def test_reasoning_quality_degraded(self):
        """Test reasoning_quality returns 'degraded' when budget exhausted."""
        usage = TokenUsage(thinking_tokens=15500, thinking_budget=16000)  # 97%
        response = GLMResponse(
            content="Test",
            thinking="Reasoning...",
            usage=usage,
        )

        assert response.reasoning_quality == "degraded"

    def test_reasoning_quality_failed_fallback(self):
        """Test reasoning_quality returns 'failed' when fallback used."""
        response = GLMResponse(
            content="Test",
            thinking="Some thinking",
            used_fallback=True,
        )

        assert response.reasoning_quality == "failed"

    def test_reasoning_quality_failed_no_thinking(self):
        """Test reasoning_quality returns 'failed' when no thinking."""
        response = GLMResponse(content="Test", thinking=None)

        assert response.reasoning_quality == "failed"


# =============================================================================
# Thinking Mode Toggle Tests
# =============================================================================


class TestThinkingModeToggle:
    """Test thinking mode enable/disable functionality."""

    def test_thinking_mode_enum_values(self):
        """Test ThinkingMode enum has expected values."""
        assert ThinkingMode.DISABLED.value == "disabled"
        assert ThinkingMode.ENABLED.value == "enabled"
        assert ThinkingMode.PRESERVED.value == "preserved"

    def test_generate_payload_thinking_enabled(self, glm_config: GLMConfig, sample_messages):
        """Test that generate builds correct payload with thinking enabled."""
        client = GLMClient(config=glm_config)

        # Mock the HTTP request
        with patch.object(client, "_request_httpx") as mock_request:
            mock_request.return_value = {
                "choices": [{"message": {"content": "test"}, "finish_reason": "stop"}],
                "usage": {},
            }

            client.generate(sample_messages, thinking=True)

            # Get the payload sent to the API
            call_args = mock_request.call_args[0][0]

            assert "thinking" in call_args
            assert call_args["thinking"]["type"] == "enabled"
            assert "budget_tokens" in call_args["thinking"]

    def test_generate_payload_thinking_disabled(self, glm_config: GLMConfig, sample_messages):
        """Test that generate builds correct payload with thinking disabled."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "_request_httpx") as mock_request:
            mock_request.return_value = {
                "choices": [{"message": {"content": "test"}, "finish_reason": "stop"}],
                "usage": {},
            }

            client.generate(sample_messages, thinking=False)

            call_args = mock_request.call_args[0][0]

            assert "thinking" in call_args
            assert call_args["thinking"]["type"] == "disabled"

    def test_generate_payload_thinking_preserved(self, glm_config: GLMConfig, sample_messages):
        """Test that generate builds correct payload with preserved thinking."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "_request_httpx") as mock_request:
            mock_request.return_value = {
                "choices": [{"message": {"content": "test"}, "finish_reason": "stop"}],
                "usage": {},
            }

            client.generate(sample_messages, thinking=True, preserve_thinking=True)

            call_args = mock_request.call_args[0][0]

            assert "thinking" in call_args
            assert call_args["thinking"]["type"] == "enabled"
            assert "chat_template_kwargs" in call_args
            assert call_args["chat_template_kwargs"]["enable_thinking"] is True
            assert call_args["chat_template_kwargs"]["clear_thinking"] is False

    def test_generate_custom_thinking_budget(self, glm_config: GLMConfig, sample_messages):
        """Test that custom thinking_budget is used."""
        client = GLMClient(config=glm_config)
        custom_budget = 32000

        with patch.object(client, "_request_httpx") as mock_request:
            mock_request.return_value = {
                "choices": [{"message": {"content": "test"}, "finish_reason": "stop"}],
                "usage": {"thinking_tokens": 5000},
            }

            client.generate(sample_messages, thinking=True, thinking_budget=custom_budget)

            call_args = mock_request.call_args[0][0]

            assert call_args["thinking"]["budget_tokens"] == custom_budget


# =============================================================================
# Response Parsing Tests
# =============================================================================


class TestResponseParsing:
    """Test response parsing from API."""

    def test_parse_response_with_thinking(
        self, glm_config: GLMConfig, mock_api_response: dict
    ):
        """Test parsing response with reasoning_content."""
        client = GLMClient(config=glm_config)

        response = client._parse_response(mock_api_response, latency_ms=100.0, thinking_budget=16000)

        assert response.content == "This is a test response."
        assert response.thinking == "I analyzed the input and determined the answer."
        assert response.finish_reason == "stop"
        assert response.usage.prompt_tokens == 100
        assert response.usage.completion_tokens == 50
        assert response.usage.thinking_tokens == 200
        assert response.usage.thinking_budget == 16000
        assert response.latency_ms == 100.0

    def test_parse_response_without_thinking(
        self, glm_config: GLMConfig, mock_api_response_no_thinking: dict
    ):
        """Test parsing response without thinking content."""
        client = GLMClient(config=glm_config)

        response = client._parse_response(mock_api_response_no_thinking, latency_ms=50.0)

        assert response.content == "Simple response without thinking."
        assert response.thinking is None
        assert response.usage.prompt_tokens == 50
        assert response.usage.thinking_tokens == 0

    def test_parse_response_fallback_to_thinking(self, glm_config: GLMConfig):
        """Test parsing response where content is empty but thinking exists."""
        client = GLMClient(config=glm_config)

        api_response = {
            "choices": [{
                "message": {
                    "content": "",  # Empty content
                    "reasoning_content": "Reasoning only response",
                },
                "finish_reason": "stop",
            }],
            "usage": {},
        }

        response = client._parse_response(api_response, latency_ms=50.0)

        # Should use thinking as content when content is empty
        assert response.content == "Reasoning only response"

    def test_parse_response_thinking_field_alternative(self, glm_config: GLMConfig):
        """Test parsing response with 'thinking' field instead of 'reasoning_content'."""
        client = GLMClient(config=glm_config)

        api_response = {
            "choices": [{
                "message": {
                    "content": "Main content",
                    "thinking": "Alternative thinking field",
                },
                "finish_reason": "stop",
            }],
            "usage": {},
        }

        response = client._parse_response(api_response, latency_ms=50.0)

        assert response.thinking == "Alternative thinking field"

    def test_parse_response_tracks_cumulative_usage(self, glm_config: GLMConfig):
        """Test that response parsing tracks cumulative usage."""
        client = GLMClient(config=glm_config)

        # First response
        client._parse_response({
            "choices": [{"message": {"content": "First"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }, latency_ms=50.0)

        # Second response
        client._parse_response({
            "choices": [{"message": {"content": "Second"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 80, "completion_tokens": 40, "total_tokens": 120},
        }, latency_ms=50.0)

        total_usage = client.get_total_usage()

        assert total_usage.prompt_tokens == 180
        assert total_usage.completion_tokens == 90
        assert total_usage.total_tokens == 270


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling and fallback behavior."""

    def test_client_requires_api_key(self, clean_env_vars):
        """Test that client raises ValueError without API key."""
        with pytest.raises(ValueError) as excinfo:
            GLMClient()

        assert "API key required" in str(excinfo.value)

    def test_reasoning_failure_type_enum(self):
        """Test ReasoningFailureType enum values."""
        assert ReasoningFailureType.NONE.value == "none"
        assert ReasoningFailureType.BUDGET_EXHAUSTED.value == "budget_exhausted"
        assert ReasoningFailureType.EMPTY_THINKING.value == "empty_thinking"
        assert ReasoningFailureType.API_ERROR.value == "api_error"
        assert ReasoningFailureType.TIMEOUT.value == "timeout"
        assert ReasoningFailureType.MALFORMED_RESPONSE.value == "malformed_response"
        assert ReasoningFailureType.TRUNCATED_OUTPUT.value == "truncated_output"

    def test_detect_reasoning_failure_none(self, glm_config: GLMConfig):
        """Test _detect_reasoning_failure returns NONE for good response."""
        client = GLMClient(config=glm_config)

        usage = TokenUsage(thinking_tokens=8000, thinking_budget=16000)
        response = GLMResponse(
            content="Good content",
            thinking="Valid thinking",
            usage=usage,
        )

        failure = client._detect_reasoning_failure(response)

        assert failure == ReasoningFailureType.NONE

    def test_detect_reasoning_failure_budget_exhausted(self, glm_config: GLMConfig):
        """Test _detect_reasoning_failure detects budget exhaustion."""
        client = GLMClient(config=glm_config)

        usage = TokenUsage(thinking_tokens=15500, thinking_budget=16000)  # > 95%
        response = GLMResponse(
            content="Content",
            thinking="Thinking",
            usage=usage,
        )

        failure = client._detect_reasoning_failure(response)

        assert failure == ReasoningFailureType.BUDGET_EXHAUSTED

    def test_detect_reasoning_failure_empty_thinking(self, glm_config: GLMConfig):
        """Test _detect_reasoning_failure detects empty thinking."""
        client = GLMClient(config=glm_config)

        usage = TokenUsage(thinking_budget=16000)  # Budget set but no thinking used
        response = GLMResponse(
            content="Content",
            thinking=None,  # No thinking returned
            usage=usage,
        )

        failure = client._detect_reasoning_failure(response)

        assert failure == ReasoningFailureType.EMPTY_THINKING

    def test_detect_reasoning_failure_truncated_output(self, glm_config: GLMConfig):
        """Test _detect_reasoning_failure detects truncated output."""
        client = GLMClient(config=glm_config)

        response = GLMResponse(
            content="Partial content",
            thinking="Thinking",
            finish_reason="length",  # Indicates truncation
        )

        failure = client._detect_reasoning_failure(response)

        assert failure == ReasoningFailureType.TRUNCATED_OUTPUT

    def test_detect_reasoning_failure_malformed(self, glm_config: GLMConfig):
        """Test _detect_reasoning_failure detects malformed response."""
        client = GLMClient(config=glm_config)

        response = GLMResponse(
            content="",  # Empty content
            thinking=None,
        )

        failure = client._detect_reasoning_failure(response)

        assert failure == ReasoningFailureType.MALFORMED_RESPONSE

    def test_generate_with_fallback_success(self, glm_config: GLMConfig, sample_messages):
        """Test generate_with_fallback returns response on success."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="Success",
                thinking="Valid thinking",
                usage=TokenUsage(thinking_tokens=8000, thinking_budget=16000),
            )

            response = client.generate_with_fallback(sample_messages)

            assert response.content == "Success"
            assert response.used_fallback is False

    def test_generate_with_fallback_on_empty_thinking(
        self, glm_config: GLMConfig, sample_messages
    ):
        """Test generate_with_fallback falls back on empty thinking."""
        client = GLMClient(config=glm_config)

        # First call: thinking enabled but empty
        # Second call: fallback without thinking
        call_count = 0

        def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First call with thinking enabled returns empty thinking
                return GLMResponse(
                    content="Content",
                    thinking=None,
                    usage=TokenUsage(thinking_budget=16000),
                )
            else:
                # Fallback call without thinking
                return GLMResponse(
                    content="Fallback content",
                    thinking=None,
                )

        with patch.object(client, "generate", side_effect=mock_generate):
            response = client.generate_with_fallback(sample_messages)

            assert response.content == "Fallback content"
            assert response.used_fallback is True
            assert response.fallback_reason == ReasoningFailureType.EMPTY_THINKING

    def test_generate_with_fallback_on_api_error(
        self, glm_config: GLMConfig, sample_messages
    ):
        """Test generate_with_fallback falls back on API error."""
        client = GLMClient(config=glm_config)

        call_count = 0

        def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1 and kwargs.get("thinking", True):
                raise Exception("API error")
            else:
                return GLMResponse(content="Fallback after error")

        with patch.object(client, "generate", side_effect=mock_generate):
            response = client.generate_with_fallback(sample_messages)

            assert response.content == "Fallback after error"
            assert response.used_fallback is True
            assert response.fallback_reason == ReasoningFailureType.API_ERROR


# =============================================================================
# ReasoningMetrics Tests
# =============================================================================


class TestReasoningMetrics:
    """Test ReasoningMetrics dataclass."""

    def test_metrics_defaults(self):
        """Test ReasoningMetrics default values."""
        metrics = ReasoningMetrics()

        assert metrics.total_requests == 0
        assert metrics.thinking_requests == 0
        assert metrics.fallback_requests == 0
        assert metrics.successful_thinking == 0
        assert metrics.failed_thinking == 0

    def test_thinking_success_rate(self):
        """Test thinking_success_rate calculation."""
        metrics = ReasoningMetrics(
            thinking_requests=10,
            successful_thinking=8,
            failed_thinking=2,
        )

        assert metrics.thinking_success_rate == 80.0

    def test_thinking_success_rate_no_requests(self):
        """Test thinking_success_rate with zero requests."""
        metrics = ReasoningMetrics(thinking_requests=0)

        assert metrics.thinking_success_rate == 100.0

    def test_fallback_rate(self):
        """Test fallback_rate calculation."""
        metrics = ReasoningMetrics(
            total_requests=20,
            fallback_requests=4,
        )

        assert metrics.fallback_rate == 20.0

    def test_fallback_rate_no_requests(self):
        """Test fallback_rate with zero requests."""
        metrics = ReasoningMetrics(total_requests=0)

        assert metrics.fallback_rate == 0.0

    def test_avg_budget_utilization(self):
        """Test avg_budget_utilization calculation."""
        metrics = ReasoningMetrics(
            total_thinking_tokens=8000,
            total_thinking_budget=16000,
        )

        assert metrics.avg_budget_utilization == 50.0

    def test_to_dict(self):
        """Test ReasoningMetrics.to_dict() serialization."""
        metrics = ReasoningMetrics(
            total_requests=10,
            thinking_requests=8,
            fallback_requests=2,
        )

        result = metrics.to_dict()

        assert "total_requests" in result
        assert "thinking_success_rate_pct" in result
        assert "fallback_rate_pct" in result


# =============================================================================
# GLMCodingAgent Tests
# =============================================================================


class TestGLMCodingAgent:
    """Test GLMCodingAgent multi-turn conversation support."""

    def test_agent_initialization(self, glm_config: GLMConfig):
        """Test GLMCodingAgent initialization."""
        client = GLMClient(config=glm_config)
        agent = GLMCodingAgent(client=client, thinking_budget=24000)

        assert agent.client == client
        assert agent.thinking_budget == 24000
        assert len(agent.messages) == 1  # System prompt
        assert agent.messages[0]["role"] == "system"

    def test_agent_custom_system_prompt(self, glm_config: GLMConfig):
        """Test GLMCodingAgent with custom system prompt."""
        client = GLMClient(config=glm_config)
        custom_prompt = "You are a code reviewer."
        agent = GLMCodingAgent(client=client, system_prompt=custom_prompt)

        assert agent.system_prompt == custom_prompt
        assert agent.messages[0]["content"] == custom_prompt

    def test_agent_send_message(self, glm_config: GLMConfig):
        """Test sending a message to the agent."""
        client = GLMClient(config=glm_config)
        agent = GLMCodingAgent(client=client)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="Agent response",
                thinking="Agent reasoning",
                thinking_budget_used=5000,
            )

            response = agent.send("Explain this code")

            assert response.content == "Agent response"
            assert len(agent.messages) == 3  # system + user + assistant

    def test_agent_tracks_thinking_history(self, glm_config: GLMConfig):
        """Test that agent tracks thinking history."""
        client = GLMClient(config=glm_config)
        agent = GLMCodingAgent(client=client)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="Response",
                thinking="Reasoning content",
                thinking_budget_used=3000,
            )

            agent.send("First message")
            agent.send("Second message")

            assert len(agent.thinking_history) == 2
            assert agent.total_thinking_tokens == 6000

    def test_agent_reset(self, glm_config: GLMConfig):
        """Test agent reset clears history."""
        client = GLMClient(config=glm_config)
        agent = GLMCodingAgent(client=client)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="Response",
                thinking="Reasoning",
                thinking_budget_used=1000,
            )

            agent.send("Message")
            agent.reset()

            assert len(agent.messages) == 1  # Only system prompt
            assert len(agent.thinking_history) == 0
            assert agent.total_thinking_tokens == 0

    def test_agent_get_thinking_usage(self, glm_config: GLMConfig):
        """Test get_thinking_usage returns correct stats."""
        client = GLMClient(config=glm_config)
        agent = GLMCodingAgent(client=client)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="Response",
                thinking="Reasoning",
                thinking_budget_used=5000,
            )

            agent.send("Message 1")
            agent.send("Message 2")

            usage = agent.get_thinking_usage()

            assert usage["total_thinking_tokens"] == 10000
            assert usage["thinking_turns"] == 2
            assert usage["average_per_turn"] == 5000

    def test_agent_with_fallback(self, glm_config: GLMConfig):
        """Test agent with fallback enabled."""
        client = GLMClient(config=glm_config)
        agent = GLMCodingAgent(client=client, use_fallback=True)

        with patch.object(client, "generate_with_fallback") as mock_fallback:
            mock_fallback.return_value = GLMResponse(
                content="Fallback response",
                used_fallback=True,
                fallback_reason=ReasoningFailureType.EMPTY_THINKING,
            )

            response = agent.send("Message")

            assert response.used_fallback is True
            assert agent.fallback_count == 1


# =============================================================================
# Streaming Support Tests
# =============================================================================


class TestStreamChunk:
    """Test StreamChunk dataclass."""

    def test_stream_chunk_defaults(self):
        """Test StreamChunk default values."""
        chunk = StreamChunk()

        assert chunk.content == ""
        assert chunk.thinking == ""
        assert chunk.finish_reason is None
        assert chunk.is_final is False
        assert chunk.chunk_index == 0
        assert chunk.interrupted is False
        assert chunk.interruption_type == StreamInterruptionType.NONE

    def test_stream_chunk_with_content(self):
        """Test StreamChunk with content."""
        chunk = StreamChunk(
            content="Partial content",
            chunk_index=5,
            completion_tokens=10,
        )

        assert chunk.content == "Partial content"
        assert chunk.chunk_index == 5
        assert chunk.completion_tokens == 10

    def test_stream_chunk_final(self):
        """Test StreamChunk marked as final."""
        chunk = StreamChunk(
            content="Final",
            is_final=True,
            finish_reason="stop",
            prompt_tokens=100,
            completion_tokens=50,
        )

        assert chunk.is_final is True
        assert chunk.finish_reason == "stop"

    def test_stream_chunk_interrupted(self):
        """Test StreamChunk with interruption."""
        chunk = StreamChunk(
            interrupted=True,
            interruption_type=StreamInterruptionType.TIMEOUT,
            error_message="Request timed out",
        )

        assert chunk.interrupted is True
        assert chunk.interruption_type == StreamInterruptionType.TIMEOUT
        assert chunk.error_message == "Request timed out"


class TestStreamingStats:
    """Test StreamingStats dataclass."""

    def test_streaming_stats_defaults(self):
        """Test StreamingStats default values."""
        stats = StreamingStats()

        assert stats.total_chunks == 0
        assert stats.content_length == 0
        assert stats.prompt_tokens == 0
        assert stats.completion_tokens == 0

    def test_total_tokens_property(self):
        """Test total_tokens calculation."""
        stats = StreamingStats(
            prompt_tokens=100,
            completion_tokens=50,
            thinking_tokens=200,
        )

        assert stats.total_tokens == 350

    def test_time_to_first_token_ms(self):
        """Test time_to_first_token_ms calculation."""
        stats = StreamingStats(
            start_time=1000.0,
            first_chunk_time=1000.5,  # 500ms later
        )

        assert stats.time_to_first_token_ms == 500.0

    def test_time_to_first_token_ms_no_chunks(self):
        """Test time_to_first_token_ms with no chunks."""
        stats = StreamingStats(start_time=1000.0, first_chunk_time=0)

        assert stats.time_to_first_token_ms == 0.0

    def test_total_duration_ms(self):
        """Test total_duration_ms calculation."""
        stats = StreamingStats(
            start_time=1000.0,
            end_time=1002.0,  # 2 seconds later
        )

        assert stats.total_duration_ms == 2000.0

    def test_tokens_per_second(self):
        """Test tokens_per_second calculation."""
        stats = StreamingStats(
            start_time=1000.0,
            end_time=1001.0,  # 1 second
            completion_tokens=100,
        )

        assert stats.tokens_per_second == 100.0

    def test_tokens_per_second_zero_duration(self):
        """Test tokens_per_second with zero duration."""
        stats = StreamingStats(
            start_time=1000.0,
            end_time=1000.0,  # No duration
            completion_tokens=100,
        )

        assert stats.tokens_per_second == 0.0

    def test_to_dict(self):
        """Test StreamingStats.to_dict() serialization."""
        stats = StreamingStats(
            total_chunks=10,
            content_length=500,
            prompt_tokens=100,
            completion_tokens=200,
        )

        result = stats.to_dict()

        assert result["total_chunks"] == 10
        assert result["content_length"] == 500
        assert "time_to_first_token_ms" in result
        assert "tokens_per_second" in result


class TestStreamInterruptionType:
    """Test StreamInterruptionType enum."""

    def test_interruption_type_values(self):
        """Test StreamInterruptionType enum values."""
        assert StreamInterruptionType.NONE.value == "none"
        assert StreamInterruptionType.TIMEOUT.value == "timeout"
        assert StreamInterruptionType.CONNECTION_ERROR.value == "connection_error"
        assert StreamInterruptionType.SERVER_ERROR.value == "server_error"
        assert StreamInterruptionType.CLIENT_CANCELLED.value == "client_cancelled"
        assert StreamInterruptionType.MALFORMED_DATA.value == "malformed_data"


class TestSSEParsing:
    """Test SSE (Server-Sent Events) parsing."""

    def test_parse_sse_line_content(self, glm_config: GLMConfig):
        """Test parsing SSE line with content."""
        client = GLMClient(config=glm_config)
        stats = StreamingStats(start_time=time.time())

        data = {
            "choices": [{
                "delta": {"content": "Hello"},
                "finish_reason": None,
            }],
        }
        line = f"data: {json.dumps(data)}"

        chunk = client._parse_sse_line(line, 0, stats, "", "", thinking_budget=16000)

        assert chunk is not None
        assert chunk.content == "Hello"
        assert chunk.is_final is False

    def test_parse_sse_line_done(self, glm_config: GLMConfig):
        """Test parsing SSE [DONE] marker."""
        client = GLMClient(config=glm_config)
        stats = StreamingStats(start_time=time.time())

        chunk = client._parse_sse_line("data: [DONE]", 5, stats, "content", "thinking", 16000)

        assert chunk is not None
        assert chunk.is_final is True
        assert chunk.finish_reason == "stop"

    def test_parse_sse_line_invalid_json(self, glm_config: GLMConfig):
        """Test parsing SSE line with invalid JSON."""
        client = GLMClient(config=glm_config)
        stats = StreamingStats(start_time=time.time())

        chunk = client._parse_sse_line("data: invalid json", 0, stats, "", "", 16000)

        assert chunk is not None
        assert chunk.interrupted is True
        assert chunk.interruption_type == StreamInterruptionType.MALFORMED_DATA

    def test_parse_sse_line_non_data_prefix(self, glm_config: GLMConfig):
        """Test parsing SSE line without data: prefix."""
        client = GLMClient(config=glm_config)
        stats = StreamingStats()

        chunk = client._parse_sse_line(": heartbeat", 0, stats, "", "", 16000)

        assert chunk is None

    def test_parse_sse_line_with_thinking(self, glm_config: GLMConfig):
        """Test parsing SSE line with thinking content."""
        client = GLMClient(config=glm_config)
        stats = StreamingStats(start_time=time.time())

        data = {
            "choices": [{
                "delta": {
                    "content": "",
                    "reasoning_content": "Thinking step",
                },
                "finish_reason": None,
            }],
        }
        line = f"data: {json.dumps(data)}"

        chunk = client._parse_sse_line(line, 0, stats, "", "", 16000)

        assert chunk is not None
        assert chunk.thinking == "Thinking step"


# =============================================================================
# Convenience Method Tests
# =============================================================================


class TestConvenienceMethods:
    """Test convenience methods on GLMClient."""

    def test_chat_method(self, glm_config: GLMConfig):
        """Test chat() convenience method."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(content="Chat response")

            response = client.chat("Hello, how are you?")

            assert response.content == "Chat response"
            mock_generate.assert_called_once()

            # Check that messages were built correctly
            call_args = mock_generate.call_args[0][0]
            assert len(call_args) == 1
            assert call_args[0]["role"] == "user"
            assert call_args[0]["content"] == "Hello, how are you?"

    def test_chat_with_system_prompt(self, glm_config: GLMConfig):
        """Test chat() with system prompt."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(content="Response")

            client.chat("User message", system_prompt="You are helpful.")

            call_args = mock_generate.call_args[0][0]
            assert len(call_args) == 2
            assert call_args[0]["role"] == "system"
            assert call_args[0]["content"] == "You are helpful."

    def test_explain_code_method(self, glm_config: GLMConfig):
        """Test explain_code() convenience method."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="This code does...",
                thinking="Analyzing the function...",
            )

            response = client.explain_code(
                code="def foo(): pass",
                language="python",
                detail_level="comprehensive",
            )

            assert response.content == "This code does..."
            mock_generate.assert_called_once()

    def test_explain_code_with_fallback(self, glm_config: GLMConfig):
        """Test explain_code() with fallback enabled."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "generate_with_fallback") as mock_fallback:
            mock_fallback.return_value = GLMResponse(content="Explanation")

            response = client.explain_code(
                code="def bar(): pass",
                language="python",
                use_fallback=True,
            )

            mock_fallback.assert_called_once()

    def test_code_generation_method(self, glm_config: GLMConfig):
        """Test code_generation() convenience method."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "chat") as mock_chat:
            mock_chat.return_value = GLMResponse(content="def generated(): pass")

            response = client.code_generation(
                prompt="Write a function to add two numbers",
                language="python",
            )

            assert "def generated" in response.content


# =============================================================================
# GLMOpenAIWrapper Tests
# =============================================================================


class TestGLMOpenAIWrapper:
    """Test OpenAI-compatible wrapper."""

    def test_wrapper_initialization(self):
        """Test GLMOpenAIWrapper initialization."""
        wrapper = GLMOpenAIWrapper(api_key="test-key")

        assert wrapper._client is not None
        assert wrapper.chat is not None

    def test_wrapper_chat_create(self):
        """Test wrapper chat.create() method."""
        wrapper = GLMOpenAIWrapper(api_key="test-key")

        with patch.object(wrapper._client, "generate") as mock_generate:
            mock_generate.return_value = GLMResponse(
                content="OpenAI-style response",
                usage=TokenUsage(prompt_tokens=50, completion_tokens=30, total_tokens=80),
                finish_reason="stop",
            )

            result = wrapper.chat.create(
                model="glm-4.7",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert "choices" in result
            assert result["choices"][0]["message"]["content"] == "OpenAI-style response"
            assert result["usage"]["total_tokens"] == 80


# =============================================================================
# Client Property Tests
# =============================================================================


class TestClientProperties:
    """Test GLMClient properties and state."""

    def test_headers_property(self, glm_config: GLMConfig):
        """Test headers property returns correct headers."""
        client = GLMClient(config=glm_config)

        headers = client.headers

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-api-key-12345"
        assert headers["Content-Type"] == "application/json"

    def test_reset_usage(self, glm_config: GLMConfig):
        """Test reset_usage clears cumulative usage."""
        client = GLMClient(config=glm_config)

        # Simulate some usage
        client._total_usage.prompt_tokens = 1000
        client._total_usage.completion_tokens = 500

        client.reset_usage()

        assert client._total_usage.prompt_tokens == 0
        assert client._total_usage.completion_tokens == 0

    def test_reset_reasoning_metrics(self, glm_config: GLMConfig):
        """Test reset_reasoning_metrics clears metrics."""
        client = GLMClient(config=glm_config)

        # Simulate some metrics
        client._reasoning_metrics.total_requests = 10
        client._reasoning_metrics.fallback_requests = 2

        client.reset_reasoning_metrics()

        assert client._reasoning_metrics.total_requests == 0
        assert client._reasoning_metrics.fallback_requests == 0

    def test_get_reasoning_metrics(self, glm_config: GLMConfig):
        """Test get_reasoning_metrics returns metrics object."""
        client = GLMClient(config=glm_config)
        client._reasoning_metrics.total_requests = 5

        metrics = client.get_reasoning_metrics()

        assert metrics.total_requests == 5


# =============================================================================
# Integration-Style Tests (With Mocked HTTP)
# =============================================================================


class TestHTTPIntegration:
    """Test HTTP request handling."""

    def test_request_httpx(self, glm_config: GLMConfig, mock_api_response: dict):
        """Test _request_httpx makes correct HTTP call."""
        client = GLMClient(config=glm_config)

        # Patch httpx directly via the module we imported
        with patch.object(_glm_client_module, "httpx") as mock_httpx:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_api_response
            mock_response.raise_for_status = MagicMock()

            mock_client_instance = MagicMock()
            mock_client_instance.post.return_value = mock_response
            mock_client_instance.__enter__ = MagicMock(return_value=mock_client_instance)
            mock_client_instance.__exit__ = MagicMock(return_value=False)

            mock_httpx.Client.return_value = mock_client_instance

            result = client._request_httpx({"model": "glm-4.7"}, stream=False)

            assert result == mock_api_response
            mock_client_instance.post.assert_called_once()

    def test_generate_end_to_end(
        self, glm_config: GLMConfig, sample_messages, mock_api_response: dict
    ):
        """Test full generate flow with mocked HTTP."""
        client = GLMClient(config=glm_config)

        with patch.object(client, "_request_httpx") as mock_request:
            mock_request.return_value = mock_api_response

            response = client.generate(sample_messages, thinking=True)

            assert response.content == "This is a test response."
            assert response.thinking is not None
            assert response.usage.thinking_tokens == 200
