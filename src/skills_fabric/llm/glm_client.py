"""GLM-4.7 SDK Client for Skills Fabric.

Connects to Z.ai API for GLM-4.7 coding model access.
Supports preserved thinking for multi-turn coding agents.

IMPORTANT: Two separate endpoints exist:
- Coding endpoint: https://api.z.ai/api/coding/paas/v4 (for Coding Plan)
- General endpoint: https://api.z.ai/api/paas/v4 (for standard API)

This client defaults to the CODING endpoint for use with coding tools.

Features:
- OpenAI-compatible API
- Preserved thinking mode (reasoning persists across turns)
- thinking_budget parameter for controlling reasoning token limits
- Thinking metrics tracking and logging
- Reasoning fallback: automatic retry without thinking when reasoning fails
- Streaming support
- Cost tracking (Coding Plan: reduced rates)

Usage:
    from skills_fabric.llm import GLMClient

    # Coding Plan (default)
    client = GLMClient(api_key="your-key")

    # Or explicitly use general API
    client = GLMClient(api_key="your-key", use_coding_endpoint=False)

    # With custom thinking budget for reasoning tasks
    response = client.generate(
        messages=[{"role": "user", "content": "Explain this code"}],
        thinking=True,
        thinking_budget=32000  # Up to 32K reasoning tokens
    )

    # Code explanation with thinking
    response = client.explain_code(
        code="def foo(): pass",
        language="python"
    )
    print(f"Thinking tokens used: {response.usage.thinking_tokens}")
    print(f"Budget used: {response.usage.thinking_budget_used_pct:.1f}%")

    # With automatic fallback when reasoning fails
    response = client.generate_with_fallback(
        messages=[{"role": "user", "content": "Explain this code"}],
        thinking_budget=16000
    )
    if response.used_fallback:
        print("Reasoning failed, used non-thinking fallback")

    # Multi-turn agent with preserved thinking
    agent = GLMCodingAgent(thinking_budget=24000)
    response = agent.send("Explain this function")
    print(agent.get_thinking_usage())
"""
from dataclasses import dataclass, field
from typing import Optional, Iterator, Any, AsyncIterator, Union
from enum import Enum
import os
import json
import time
import logging
import asyncio

# Get logger for this module
logger = logging.getLogger(__name__)

# Try to import httpx for async support, fall back to requests
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    import requests


class StreamInterruptionType(Enum):
    """Types of stream interruptions."""
    NONE = "none"  # No interruption
    TIMEOUT = "timeout"  # Stream timed out
    CONNECTION_ERROR = "connection_error"  # Connection was lost
    SERVER_ERROR = "server_error"  # Server sent an error
    CLIENT_CANCELLED = "client_cancelled"  # Client cancelled the stream
    MALFORMED_DATA = "malformed_data"  # Received invalid SSE data


@dataclass
class StreamChunk:
    """A single chunk from a streaming response.

    Represents one SSE event from the GLM API stream.
    """
    content: str = ""
    thinking: str = ""
    finish_reason: Optional[str] = None
    is_final: bool = False
    chunk_index: int = 0
    # Token counts (may be partial during stream)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    thinking_tokens: int = 0
    # Timing
    latency_ms: float = 0.0
    # Interruption handling
    interrupted: bool = False
    interruption_type: StreamInterruptionType = StreamInterruptionType.NONE
    error_message: Optional[str] = None


@dataclass
class StreamingStats:
    """Statistics collected during streaming.

    Tracks tokens, timing, and interruptions during a streaming response.
    """
    total_chunks: int = 0
    content_length: int = 0
    thinking_length: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    thinking_tokens: int = 0
    start_time: float = 0.0
    first_chunk_time: float = 0.0
    end_time: float = 0.0
    interrupted: bool = False
    interruption_type: StreamInterruptionType = StreamInterruptionType.NONE
    error_message: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.prompt_tokens + self.completion_tokens + self.thinking_tokens

    @property
    def time_to_first_token_ms(self) -> float:
        """Time from start to first chunk in milliseconds."""
        if self.first_chunk_time == 0 or self.start_time == 0:
            return 0.0
        return (self.first_chunk_time - self.start_time) * 1000

    @property
    def total_duration_ms(self) -> float:
        """Total streaming duration in milliseconds."""
        if self.end_time == 0 or self.start_time == 0:
            return 0.0
        return (self.end_time - self.start_time) * 1000

    @property
    def tokens_per_second(self) -> float:
        """Tokens generated per second."""
        duration_s = self.total_duration_ms / 1000
        if duration_s <= 0:
            return 0.0
        return self.completion_tokens / duration_s

    def to_dict(self) -> dict:
        """Convert stats to dictionary for logging."""
        return {
            "total_chunks": self.total_chunks,
            "content_length": self.content_length,
            "thinking_length": self.thinking_length,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "thinking_tokens": self.thinking_tokens,
            "total_tokens": self.total_tokens,
            "time_to_first_token_ms": round(self.time_to_first_token_ms, 2),
            "total_duration_ms": round(self.total_duration_ms, 2),
            "tokens_per_second": round(self.tokens_per_second, 2),
            "interrupted": self.interrupted,
            "interruption_type": self.interruption_type.value if self.interrupted else None,
        }


class ThinkingMode(Enum):
    """GLM-4.7 thinking modes."""
    DISABLED = "disabled"
    ENABLED = "enabled"
    PRESERVED = "preserved"  # Keeps thinking across turns


class ReasoningFailureType(Enum):
    """Types of reasoning failures that can trigger fallback."""
    NONE = "none"  # No failure
    BUDGET_EXHAUSTED = "budget_exhausted"  # Thinking budget fully consumed
    EMPTY_THINKING = "empty_thinking"  # Thinking enabled but no reasoning returned
    API_ERROR = "api_error"  # API returned an error during thinking
    TIMEOUT = "timeout"  # Request timed out during reasoning
    MALFORMED_RESPONSE = "malformed_response"  # Response format unexpected
    TRUNCATED_OUTPUT = "truncated_output"  # Output appears cut off


@dataclass
class ReasoningMetrics:
    """Metrics for reasoning/thinking operations.

    Tracks performance and success rates for thinking mode operations.
    Useful for monitoring and debugging reasoning quality.
    """
    total_requests: int = 0
    thinking_requests: int = 0
    fallback_requests: int = 0
    successful_thinking: int = 0
    failed_thinking: int = 0
    total_thinking_tokens: int = 0
    total_thinking_budget: int = 0
    budget_exhausted_count: int = 0
    empty_thinking_count: int = 0
    api_error_count: int = 0
    timeout_count: int = 0

    @property
    def thinking_success_rate(self) -> float:
        """Percentage of thinking requests that succeeded."""
        if self.thinking_requests == 0:
            return 100.0
        return (self.successful_thinking / self.thinking_requests) * 100

    @property
    def fallback_rate(self) -> float:
        """Percentage of requests that fell back to non-thinking mode."""
        if self.total_requests == 0:
            return 0.0
        return (self.fallback_requests / self.total_requests) * 100

    @property
    def avg_budget_utilization(self) -> float:
        """Average percentage of thinking budget used."""
        if self.total_thinking_budget == 0:
            return 0.0
        return (self.total_thinking_tokens / self.total_thinking_budget) * 100

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for logging/serialization."""
        return {
            "total_requests": self.total_requests,
            "thinking_requests": self.thinking_requests,
            "fallback_requests": self.fallback_requests,
            "thinking_success_rate_pct": round(self.thinking_success_rate, 2),
            "fallback_rate_pct": round(self.fallback_rate, 2),
            "avg_budget_utilization_pct": round(self.avg_budget_utilization, 2),
            "budget_exhausted_count": self.budget_exhausted_count,
            "empty_thinking_count": self.empty_thinking_count,
            "api_error_count": self.api_error_count,
            "timeout_count": self.timeout_count,
        }


@dataclass
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0
    thinking_budget: int = 0  # Allocated thinking budget

    @property
    def cost_usd(self) -> float:
        """Calculate cost in USD (Z.ai Coding Plan rates)."""
        input_cost = (self.prompt_tokens / 1_000_000) * 0.60
        output_cost = ((self.completion_tokens + self.thinking_tokens) / 1_000_000) * 2.20
        return input_cost + output_cost

    @property
    def thinking_budget_used_pct(self) -> float:
        """Percentage of thinking budget used."""
        if self.thinking_budget <= 0:
            return 0.0
        return min(100.0, (self.thinking_tokens / self.thinking_budget) * 100)

    @property
    def thinking_budget_exhausted(self) -> bool:
        """Check if thinking budget was fully consumed (reasoning may be truncated)."""
        if self.thinking_budget <= 0:
            return False
        # Consider exhausted if >95% used (buffer for estimation variance)
        return self.thinking_tokens >= (self.thinking_budget * 0.95)


@dataclass
class GLMResponse:
    """Response from GLM-4.7 API."""
    content: str
    thinking: Optional[str] = None
    finish_reason: str = "stop"
    usage: TokenUsage = field(default_factory=TokenUsage)
    model: str = "glm-4.7"
    latency_ms: float = 0.0
    thinking_budget_used: int = 0  # How many thinking tokens were used
    # Fallback-related fields
    used_fallback: bool = False  # True if fell back to non-thinking mode
    fallback_reason: ReasoningFailureType = ReasoningFailureType.NONE
    original_error: Optional[str] = None  # Error message if fallback was triggered

    @property
    def has_thinking(self) -> bool:
        """Check if response includes thinking content."""
        return self.thinking is not None and len(self.thinking) > 0

    @property
    def thinking_truncated(self) -> bool:
        """Check if thinking may have been truncated due to budget limits."""
        return self.usage.thinking_budget_exhausted

    @property
    def reasoning_quality(self) -> str:
        """Assess the quality of reasoning in this response.

        Returns:
            'excellent': Full thinking with budget room to spare
            'good': Thinking completed but used significant budget
            'degraded': Budget exhausted, reasoning may be incomplete
            'failed': No thinking (fallback used or disabled)
        """
        if self.used_fallback:
            return "failed"
        if not self.has_thinking:
            return "failed"
        if self.thinking_truncated:
            return "degraded"
        if self.usage.thinking_budget_used_pct > 80:
            return "good"
        return "excellent"


# API Endpoints
CODING_BASE_URL = "https://api.z.ai/api/coding/paas/v4"
GENERAL_BASE_URL = "https://api.z.ai/api/paas/v4"


@dataclass
class GLMConfig:
    """Configuration for GLM client."""
    api_key: str = ""
    base_url: str = CODING_BASE_URL  # Default to coding endpoint
    model: str = "glm-4.7"
    use_coding_endpoint: bool = True  # Use coding endpoint by default
    max_tokens: int = 4096
    temperature: float = 1.0
    top_p: float = 0.95
    timeout: int = 120
    thinking_mode: ThinkingMode = ThinkingMode.ENABLED
    thinking_budget: int = 16000  # Max reasoning tokens (default 16K for GLM-4.7)

    @classmethod
    def from_env(cls, use_coding_endpoint: bool = True) -> "GLMConfig":
        """Create config from environment variables.

        Args:
            use_coding_endpoint: Use coding endpoint (default True)

        Environment variables:
            ZAI_API_KEY or GLM_API_KEY: API key
            ZAI_BASE_URL: Override base URL
            ZAI_USE_CODING: Set to "false" to use general endpoint
            GLM_MODEL: Model name (default glm-4.7)
            GLM_THINKING_BUDGET: Max reasoning tokens (default 16000)
        """
        # Check env var for endpoint preference
        env_use_coding = os.getenv("ZAI_USE_CODING", "true").lower() != "false"
        use_coding = use_coding_endpoint and env_use_coding

        # Determine base URL
        default_url = CODING_BASE_URL if use_coding else GENERAL_BASE_URL
        base_url = os.getenv("ZAI_BASE_URL", default_url)

        # Get thinking budget from env (default 16K)
        thinking_budget = int(os.getenv("GLM_THINKING_BUDGET", "16000"))

        return cls(
            api_key=os.getenv("ZAI_API_KEY", os.getenv("GLM_API_KEY", "")),
            base_url=base_url,
            model=os.getenv("GLM_MODEL", "glm-4.7"),
            use_coding_endpoint=use_coding,
            thinking_budget=thinking_budget,
        )


class GLMClient:
    """Client for GLM-4.7 API.

    Supports both sync and async operations.
    Compatible with OpenAI message format.

    Uses the CODING endpoint by default for Coding Plan subscribers.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[GLMConfig] = None,
        use_coding_endpoint: bool = True,
    ):
        """Initialize GLM client.

        Args:
            api_key: Z.ai API key (or set ZAI_API_KEY env var)
            config: Optional full configuration
            use_coding_endpoint: Use coding endpoint (default True)
        """
        if config:
            self.config = config
        else:
            self.config = GLMConfig.from_env(use_coding_endpoint=use_coding_endpoint)
            if api_key:
                self.config.api_key = api_key

        if not self.config.api_key:
            raise ValueError(
                "API key required. Set ZAI_API_KEY env var or pass api_key parameter."
            )

        self._session = None
        self._total_usage = TokenUsage()
        self._reasoning_metrics = ReasoningMetrics()

    @property
    def headers(self) -> dict:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    @property
    def endpoint(self) -> str:
        """Get chat completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    def generate(
        self,
        messages: list[dict],
        thinking: bool = True,
        preserve_thinking: bool = False,
        thinking_budget: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        **kwargs,
    ) -> GLMResponse:
        """Generate a response from GLM-4.7.

        Args:
            messages: List of messages in OpenAI format
            thinking: Enable thinking mode
            preserve_thinking: Keep thinking across turns (for agents)
            thinking_budget: Max tokens for reasoning (uses config default if not set)
            max_tokens: Override max tokens
            temperature: Override temperature
            stream: Enable streaming (returns iterator)
            **kwargs: Additional parameters

        Returns:
            GLMResponse with content and optional thinking
        """
        # Build request payload
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "top_p": self.config.top_p,
            "stream": stream,
        }

        # Use provided budget or config default
        budget = thinking_budget or self.config.thinking_budget

        # Configure thinking mode with budget_tokens (Z.ai format)
        if thinking:
            if preserve_thinking:
                payload["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": budget,
                }
                payload["chat_template_kwargs"] = {
                    "enable_thinking": True,
                    "clear_thinking": False,  # Preserve across turns
                }
            else:
                payload["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": budget,
                }
        else:
            payload["thinking"] = {"type": "disabled"}

        # Add any extra parameters
        payload.update(kwargs)

        # Make request
        start_time = time.time()

        if HTTPX_AVAILABLE:
            response = self._request_httpx(payload, stream)
        else:
            response = self._request_requests(payload, stream)

        latency_ms = (time.time() - start_time) * 1000

        if stream:
            return self._parse_stream(response, latency_ms)
        else:
            # Pass the thinking budget for tracking
            return self._parse_response(
                response, latency_ms, thinking_budget=budget if thinking else 0
            )

    def generate_with_fallback(
        self,
        messages: list[dict],
        thinking_budget: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        auto_increase_budget: bool = False,
        **kwargs,
    ) -> GLMResponse:
        """Generate response with automatic fallback on reasoning failure.

        Tries thinking mode first. If reasoning fails or is truncated,
        automatically retries without thinking mode to ensure a response.

        Args:
            messages: List of messages in OpenAI format
            thinking_budget: Max tokens for reasoning (uses config default if not set)
            max_tokens: Override max tokens
            temperature: Override temperature
            auto_increase_budget: If True and budget exhausted, retry with 2x budget
                                  before falling back to non-thinking
            **kwargs: Additional parameters

        Returns:
            GLMResponse with content. Check used_fallback and fallback_reason
            to determine if fallback was triggered.

        Example:
            response = client.generate_with_fallback(
                messages=[{"role": "user", "content": "Explain this code"}],
                thinking_budget=16000
            )
            if response.used_fallback:
                print(f"Fallback used: {response.fallback_reason.value}")
            else:
                print(f"Reasoning quality: {response.reasoning_quality}")
        """
        budget = thinking_budget or self.config.thinking_budget

        # Update metrics
        self._reasoning_metrics.total_requests += 1
        self._reasoning_metrics.thinking_requests += 1

        # First attempt: with thinking
        try:
            response = self.generate(
                messages=messages,
                thinking=True,
                thinking_budget=budget,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                **kwargs,
            )

            # Check for reasoning failure
            failure_type = self._detect_reasoning_failure(response)

            if failure_type == ReasoningFailureType.NONE:
                # Success - log and return
                self._reasoning_metrics.successful_thinking += 1
                self._reasoning_metrics.total_thinking_tokens += response.usage.thinking_tokens
                self._reasoning_metrics.total_thinking_budget += budget
                self._log_reasoning_metrics(response, "success")
                return response

            # Handle budget exhaustion with optional retry at higher budget
            if failure_type == ReasoningFailureType.BUDGET_EXHAUSTED:
                self._reasoning_metrics.budget_exhausted_count += 1

                if auto_increase_budget and budget < 64000:
                    # Retry with 2x budget before giving up
                    new_budget = min(budget * 2, 64000)
                    logger.info(
                        f"Reasoning budget exhausted ({budget} tokens). "
                        f"Retrying with increased budget ({new_budget} tokens)."
                    )
                    return self.generate_with_fallback(
                        messages=messages,
                        thinking_budget=new_budget,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        auto_increase_budget=False,  # Only retry once
                        **kwargs,
                    )

                # Budget exhausted but response exists - return with warning
                self._reasoning_metrics.failed_thinking += 1
                self._log_reasoning_metrics(
                    response, "degraded", f"budget_exhausted ({response.usage.thinking_tokens}/{budget})"
                )
                return response  # Return degraded response, not fallback

            # Handle empty thinking
            if failure_type == ReasoningFailureType.EMPTY_THINKING:
                self._reasoning_metrics.empty_thinking_count += 1
                logger.warning(
                    "Thinking mode enabled but no reasoning returned. "
                    "Falling back to non-thinking mode."
                )

            # Fallback to non-thinking mode
            return self._execute_fallback(
                messages=messages,
                failure_type=failure_type,
                original_error=None,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

        except Exception as e:
            # API error or timeout - fallback to non-thinking
            error_msg = str(e)

            # Categorize the error
            if "timeout" in error_msg.lower():
                failure_type = ReasoningFailureType.TIMEOUT
                self._reasoning_metrics.timeout_count += 1
            else:
                failure_type = ReasoningFailureType.API_ERROR
                self._reasoning_metrics.api_error_count += 1

            logger.warning(
                f"Thinking request failed with error: {error_msg}. "
                f"Falling back to non-thinking mode."
            )

            return self._execute_fallback(
                messages=messages,
                failure_type=failure_type,
                original_error=error_msg,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

    def _detect_reasoning_failure(self, response: GLMResponse) -> ReasoningFailureType:
        """Detect type of reasoning failure in a response.

        Args:
            response: GLMResponse to analyze

        Returns:
            ReasoningFailureType indicating the failure (or NONE if successful)
        """
        # Check for budget exhaustion (may still have valid response)
        if response.thinking_truncated:
            return ReasoningFailureType.BUDGET_EXHAUSTED

        # Check for empty thinking when it was expected
        if not response.has_thinking and response.usage.thinking_budget > 0:
            # Thinking was enabled but no reasoning returned
            return ReasoningFailureType.EMPTY_THINKING

        # Check for truncated output (finish_reason indicates cutoff)
        if response.finish_reason == "length":
            return ReasoningFailureType.TRUNCATED_OUTPUT

        # Check for malformed/empty content
        if not response.content or not response.content.strip():
            return ReasoningFailureType.MALFORMED_RESPONSE

        return ReasoningFailureType.NONE

    def _execute_fallback(
        self,
        messages: list[dict],
        failure_type: ReasoningFailureType,
        original_error: Optional[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> GLMResponse:
        """Execute fallback request without thinking mode.

        Args:
            messages: List of messages
            failure_type: Why fallback was triggered
            original_error: Original error message if any
            max_tokens: Override max tokens
            temperature: Override temperature
            **kwargs: Additional parameters

        Returns:
            GLMResponse with fallback information
        """
        self._reasoning_metrics.failed_thinking += 1
        self._reasoning_metrics.fallback_requests += 1

        try:
            # Make request without thinking
            response = self.generate(
                messages=messages,
                thinking=False,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                **kwargs,
            )

            # Mark as fallback
            response.used_fallback = True
            response.fallback_reason = failure_type
            response.original_error = original_error

            self._log_reasoning_metrics(
                response, "fallback", f"{failure_type.value}: {original_error or 'N/A'}"
            )

            return response

        except Exception as e:
            # Even fallback failed - create error response
            logger.error(f"Fallback request also failed: {e}")
            raise

    def _log_reasoning_metrics(
        self,
        response: GLMResponse,
        status: str,
        detail: Optional[str] = None,
    ) -> None:
        """Log reasoning metrics for observability.

        Args:
            response: The GLMResponse
            status: 'success', 'degraded', or 'fallback'
            detail: Optional detail message
        """
        metrics = {
            "status": status,
            "thinking_tokens": response.usage.thinking_tokens,
            "thinking_budget": response.usage.thinking_budget,
            "budget_used_pct": round(response.usage.thinking_budget_used_pct, 1),
            "latency_ms": round(response.latency_ms, 1),
            "model": response.model,
        }

        if detail:
            metrics["detail"] = detail

        if response.used_fallback:
            metrics["fallback_reason"] = response.fallback_reason.value

        if status == "success":
            logger.debug(f"Reasoning metrics: {metrics}")
        elif status == "degraded":
            logger.warning(f"Reasoning degraded: {metrics}")
        else:
            logger.info(f"Reasoning fallback: {metrics}")

    def get_reasoning_metrics(self) -> ReasoningMetrics:
        """Get cumulative reasoning metrics.

        Returns:
            ReasoningMetrics with statistics about thinking operations
        """
        return self._reasoning_metrics

    def reset_reasoning_metrics(self) -> None:
        """Reset reasoning metrics to initial state."""
        self._reasoning_metrics = ReasoningMetrics()

    def log_reasoning_summary(self) -> None:
        """Log a summary of reasoning metrics."""
        metrics = self._reasoning_metrics.to_dict()
        logger.info(f"Reasoning summary: {json.dumps(metrics, indent=2)}")

    def _request_httpx(self, payload: dict, stream: bool) -> Any:
        """Make request using httpx."""
        with httpx.Client(timeout=self.config.timeout) as client:
            response = client.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def _request_requests(self, payload: dict, stream: bool) -> Any:
        """Make request using requests library."""
        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json=payload,
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _parse_response(
        self, data: dict, latency_ms: float, thinking_budget: int = 0
    ) -> GLMResponse:
        """Parse API response into GLMResponse.

        Args:
            data: Raw API response data
            latency_ms: Request latency in milliseconds
            thinking_budget: The thinking budget that was used for this request
        """
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})

        # Extract content and thinking (GLM-4.7 uses reasoning_content)
        content = message.get("content", "")
        thinking = None

        # Check for thinking in message (GLM-4.7 format: reasoning_content)
        if "thinking" in message:
            thinking = message["thinking"]
        elif "reasoning_content" in message:
            thinking = message["reasoning_content"]

        # GLM-4.7: If content is empty but reasoning exists, use reasoning as content
        # This is a known behavior of GLM thinking models
        if not content and thinking:
            content = thinking

        # Parse usage with thinking_budget tracking
        usage_data = data.get("usage", {})
        thinking_tokens = usage_data.get("thinking_tokens", 0)
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            thinking_tokens=thinking_tokens,
            total_tokens=usage_data.get("total_tokens", 0),
            thinking_budget=thinking_budget,  # Track allocated budget
        )

        # Track cumulative usage
        self._total_usage.prompt_tokens += usage.prompt_tokens
        self._total_usage.completion_tokens += usage.completion_tokens
        self._total_usage.thinking_tokens += usage.thinking_tokens
        self._total_usage.total_tokens += usage.total_tokens
        self._total_usage.thinking_budget += thinking_budget

        return GLMResponse(
            content=content,
            thinking=thinking,
            finish_reason=choice.get("finish_reason", "stop"),
            usage=usage,
            model=data.get("model", self.config.model),
            latency_ms=latency_ms,
            thinking_budget_used=thinking_tokens,  # Track actual usage
        )

    def _parse_stream(self, response: Any, latency_ms: float) -> Iterator[str]:
        """Parse streaming response."""
        # Streaming implementation would go here
        # For now, yield the full response
        yield response.get("choices", [{}])[0].get("message", {}).get("content", "")

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        thinking: bool = True,
        thinking_budget: Optional[int] = None,
    ) -> GLMResponse:
        """Simple chat interface.

        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            thinking: Enable thinking mode
            thinking_budget: Max tokens for reasoning (uses config default if not set)

        Returns:
            GLMResponse
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_message})

        return self.generate(messages, thinking=thinking, thinking_budget=thinking_budget)

    def code_generation(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> GLMResponse:
        """Generate code with GLM-4.7.

        Args:
            prompt: Code generation prompt
            language: Target language
            context: Optional code context

        Returns:
            GLMResponse with generated code
        """
        system_prompt = f"""You are an expert {language} programmer.
Generate clean, well-documented code.
Include type hints and docstrings.
Follow best practices for {language}."""

        if context:
            prompt = f"Context:\n```{language}\n{context}\n```\n\nTask: {prompt}"

        return self.chat(
            user_message=prompt,
            system_prompt=system_prompt,
            thinking=True,
        )

    def explain_code(
        self,
        code: str,
        language: str = "python",
        thinking_budget: Optional[int] = None,
        detail_level: str = "comprehensive",
        use_fallback: bool = False,
        auto_increase_budget: bool = False,
    ) -> GLMResponse:
        """Explain code using GLM-4.7 with thinking mode.

        Uses extended thinking budget to provide deep code analysis.
        This is a reasoning-intensive task that benefits from higher thinking budgets.

        Args:
            code: The source code to explain
            language: Programming language of the code
            thinking_budget: Max reasoning tokens (default: 24000 for explanation tasks)
            detail_level: "brief", "moderate", or "comprehensive"
            use_fallback: If True, use generate_with_fallback for automatic
                         fallback to non-thinking mode on failures
            auto_increase_budget: If True with use_fallback, retry with 2x budget
                                  before falling back to non-thinking

        Returns:
            GLMResponse with explanation and thinking process

        Example:
            response = client.explain_code(
                code=\"\"\"
                def quicksort(arr):
                    if len(arr) <= 1:
                        return arr
                    pivot = arr[len(arr) // 2]
                    left = [x for x in arr if x < pivot]
                    middle = [x for x in arr if x == pivot]
                    right = [x for x in arr if x > pivot]
                    return quicksort(left) + middle + quicksort(right)
                \"\"\",
                language="python",
                thinking_budget=32000,
                use_fallback=True  # Automatically fallback if reasoning fails
            )
            print(f"Thinking used: {response.usage.thinking_budget_used_pct:.1f}%")
            if response.used_fallback:
                print(f"Fallback reason: {response.fallback_reason.value}")
            print(response.content)
        """
        # Use higher default budget for explanation tasks (reasoning-heavy)
        budget = thinking_budget or 24000

        # Customize prompt based on detail level
        detail_instructions = {
            "brief": "Provide a concise summary of what this code does (2-3 sentences).",
            "moderate": "Explain the code's purpose, key functions, and general flow.",
            "comprehensive": """Provide a comprehensive explanation including:
1. Overall purpose and functionality
2. Step-by-step breakdown of the logic
3. Key data structures and algorithms used
4. Potential edge cases or limitations
5. Suggestions for improvement (if applicable)""",
        }

        instruction = detail_instructions.get(detail_level, detail_instructions["comprehensive"])

        system_prompt = f"""You are an expert code analyst specializing in {language}.
Your task is to explain code clearly and thoroughly.
Use your thinking process to analyze the code deeply before explaining.
{instruction}"""

        user_message = f"""Please explain this {language} code:

```{language}
{code}
```"""

        # Log the reasoning task
        logger.debug(
            f"explain_code: language={language}, detail={detail_level}, "
            f"budget={budget}, code_len={len(code)}, use_fallback={use_fallback}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Use fallback method if requested
        if use_fallback:
            response = self.generate_with_fallback(
                messages=messages,
                thinking_budget=budget,
                auto_increase_budget=auto_increase_budget,
            )
        else:
            response = self.generate(
                messages=messages,
                thinking=True,
                thinking_budget=budget,
            )

        # Log thinking metrics
        if response.used_fallback:
            logger.info(
                f"explain_code: Used fallback mode. "
                f"Reason: {response.fallback_reason.value}. "
                f"Original error: {response.original_error or 'N/A'}"
            )
        elif response.usage.thinking_budget_exhausted:
            logger.warning(
                f"explain_code: Thinking budget exhausted "
                f"({response.usage.thinking_tokens}/{budget} tokens). "
                f"Response may be truncated. Consider increasing thinking_budget."
            )
        else:
            logger.debug(
                f"explain_code: Thinking used {response.usage.thinking_budget_used_pct:.1f}% "
                f"of budget ({response.usage.thinking_tokens}/{budget} tokens)"
            )

        return response

    def get_total_usage(self) -> TokenUsage:
        """Get cumulative token usage."""
        return self._total_usage

    def reset_usage(self):
        """Reset usage tracking."""
        self._total_usage = TokenUsage()

    # =========================================================================
    # Tool Calling / Function Calling
    # =========================================================================

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        tool_choice: str = "auto",
        **kwargs,
    ) -> GLMResponse:
        """Generate response with tool/function calling.

        Args:
            messages: Conversation messages
            tools: List of tool definitions (OpenAI format)
            tool_choice: "auto", "none", or specific tool name
            **kwargs: Additional parameters

        Returns:
            GLMResponse (check for tool_calls in response)

        Example tool definition:
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                }
            }
        """
        return self.generate(
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            thinking=True,
            **kwargs,
        )

    # =========================================================================
    # Web Search API (uses general endpoint, not coding endpoint)
    # =========================================================================

    def web_search(
        self,
        query: str,
        search_engine: str = "search_std",
        search_result_depth: str = "basic",
    ) -> dict:
        """Search the web using Z.ai's LLM-optimized search.

        Args:
            query: Search query
            search_engine: "search_std" (standard) or "search_pro" (detailed)
            search_result_depth: "basic" or "advanced"

        Returns:
            Search results with titles, URLs, summaries

        Note: Uses general endpoint as web_search is not available on coding endpoint.
        """
        # Web search uses general endpoint, not coding endpoint
        endpoint = f"{GENERAL_BASE_URL}/web_search"

        payload = {
            "search_engine": search_engine,
            "search_result_depth": search_result_depth,
            "query": query,
        }

        if HTTPX_AVAILABLE:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(endpoint, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
        else:
            response = requests.post(
                endpoint, headers=self.headers, json=payload, timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # Web Reader API (uses general endpoint, not coding endpoint)
    # =========================================================================

    def read_url(
        self,
        url: str,
        return_format: str = "markdown",
        cache: bool = True,
        generate_summary: bool = False,
    ) -> dict:
        """Read and parse content from a URL.

        Args:
            url: URL to read
            return_format: "markdown", "html", or "text"
            cache: Use cached version if available
            generate_summary: Include AI-generated summary

        Returns:
            Parsed content with title, content, and optional summary

        Note: Uses general endpoint as reader is not available on coding endpoint.
        """
        # Reader uses general endpoint, not coding endpoint
        endpoint = f"{GENERAL_BASE_URL}/reader"

        payload = {
            "url": url,
            "return_format": return_format,
            "cache": cache,
            "generate_summary": generate_summary,
        }

        if HTTPX_AVAILABLE:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(endpoint, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
        else:
            response = requests.post(
                endpoint, headers=self.headers, json=payload, timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # Tokenizer API (uses general endpoint, not coding endpoint)
    # =========================================================================

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to tokenize

        Returns:
            Token count

        Note: Uses general endpoint as tokenizer is not available on coding endpoint.
        """
        # Tokenizer uses general endpoint, not coding endpoint
        endpoint = f"{GENERAL_BASE_URL}/tokenizer"

        payload = {
            "model": self.config.model,
            "input": text,
        }

        if HTTPX_AVAILABLE:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(endpoint, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
        else:
            response = requests.post(
                endpoint, headers=self.headers, json=payload, timeout=self.config.timeout
            )
            response.raise_for_status()
            data = response.json()

        return data.get("total_tokens", 0)

    # =========================================================================
    # Research Helper (combines web search + chat)
    # =========================================================================

    def research(
        self,
        query: str,
        follow_up_question: Optional[str] = None,
    ) -> GLMResponse:
        """Research a topic using web search + GLM analysis.

        Args:
            query: Research query
            follow_up_question: Optional specific question about results

        Returns:
            GLMResponse with synthesized research
        """
        # First, search the web
        search_results = self.web_search(query)

        # Format results for context
        context_parts = ["Web search results:\n"]
        for result in search_results.get("results", [])[:5]:
            title = result.get("title", "")
            url = result.get("url", "")
            summary = result.get("summary", "")
            context_parts.append(f"- {title}\n  URL: {url}\n  {summary}\n")

        context = "\n".join(context_parts)

        # Generate response with context
        prompt = follow_up_question or f"Based on the search results, provide a comprehensive answer about: {query}"

        return self.chat(
            user_message=f"{context}\n\n{prompt}",
            thinking=True,
        )


class GLMCodingAgent:
    """Coding agent using GLM-4.7 with preserved thinking.

    Maintains conversation history and thinking state
    across multiple turns for complex coding tasks.

    Example:
        agent = GLMCodingAgent(thinking_budget=32000)
        response = agent.send("Explain how this code works")
        print(f"Thinking used: {response.thinking_budget_used} tokens")
        print(f"Response: {response.content}")

        # With automatic fallback on reasoning failures
        agent = GLMCodingAgent(thinking_budget=16000, use_fallback=True)
        response = agent.send("Explain this complex algorithm")
        if response.used_fallback:
            print(f"Fallback triggered: {response.fallback_reason.value}")
    """

    def __init__(
        self,
        client: Optional[GLMClient] = None,
        system_prompt: Optional[str] = None,
        thinking_budget: int = 16000,
        use_fallback: bool = False,
        auto_increase_budget: bool = False,
    ):
        """Initialize coding agent.

        Args:
            client: GLM client instance
            system_prompt: Custom system prompt
            thinking_budget: Max tokens for reasoning per turn (default 16K)
            use_fallback: If True, automatically fallback to non-thinking mode
                         when reasoning fails
            auto_increase_budget: If True with use_fallback, retry with 2x budget
                                  before falling back
        """
        self.client = client or GLMClient()
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.thinking_budget = thinking_budget
        self.use_fallback = use_fallback
        self.auto_increase_budget = auto_increase_budget
        self.messages: list[dict] = []
        self.thinking_history: list[str] = []
        self.total_thinking_tokens: int = 0  # Track cumulative thinking usage
        self.fallback_count: int = 0  # Track how many times fallback was used

        # Initialize with system prompt
        self.messages.append({
            "role": "system",
            "content": self.system_prompt,
        })

    def _default_system_prompt(self) -> str:
        return """You are an expert software engineer helping with coding tasks.

When writing code:
- Use clear, descriptive names
- Add type hints (Python) or types (TypeScript)
- Include docstrings/comments for complex logic
- Follow the existing code style
- Consider edge cases and error handling

When analyzing code:
- Identify potential bugs or issues
- Suggest improvements
- Explain your reasoning

Think step by step before providing solutions."""

    def send(
        self,
        message: str,
        preserve_thinking: bool = True,
        thinking_budget: Optional[int] = None,
        use_fallback: Optional[bool] = None,
    ) -> GLMResponse:
        """Send a message and get response.

        Args:
            message: User message
            preserve_thinking: Keep thinking across turns
            thinking_budget: Override thinking budget for this turn
            use_fallback: Override use_fallback setting for this turn
                         (uses instance default if not specified)

        Returns:
            GLMResponse
        """
        # Add user message
        self.messages.append({
            "role": "user",
            "content": message,
        })

        # Use provided budget or instance default
        budget = thinking_budget or self.thinking_budget

        # Determine whether to use fallback
        should_fallback = use_fallback if use_fallback is not None else self.use_fallback

        # Generate response
        if should_fallback:
            response = self.client.generate_with_fallback(
                messages=self.messages,
                thinking_budget=budget,
                auto_increase_budget=self.auto_increase_budget,
            )
        else:
            response = self.client.generate(
                messages=self.messages,
                thinking=True,
                preserve_thinking=preserve_thinking,
                thinking_budget=budget,
            )

        # Add assistant response to history
        self.messages.append({
            "role": "assistant",
            "content": response.content,
        })

        # Track thinking
        if response.thinking:
            self.thinking_history.append(response.thinking)
        self.total_thinking_tokens += response.thinking_budget_used

        # Track fallback usage
        if response.used_fallback:
            self.fallback_count += 1
            logger.info(
                f"GLMCodingAgent: Turn {len(self.thinking_history) + self.fallback_count} "
                f"used fallback. Reason: {response.fallback_reason.value}"
            )

        return response

    def reset(self):
        """Reset conversation history."""
        self.messages = [{
            "role": "system",
            "content": self.system_prompt,
        }]
        self.thinking_history = []
        self.total_thinking_tokens = 0
        self.fallback_count = 0

    def get_conversation(self) -> list[dict]:
        """Get full conversation history."""
        return self.messages.copy()

    def get_thinking_usage(self) -> dict:
        """Get thinking token usage for this conversation.

        Returns:
            dict with thinking usage metrics including fallback statistics
        """
        total_turns = len(self.thinking_history) + self.fallback_count
        return {
            "total_thinking_tokens": self.total_thinking_tokens,
            "thinking_turns": len(self.thinking_history),
            "fallback_turns": self.fallback_count,
            "total_turns": total_turns,
            "average_per_turn": (
                self.total_thinking_tokens / len(self.thinking_history)
                if self.thinking_history else 0
            ),
            "fallback_rate_pct": (
                (self.fallback_count / total_turns * 100)
                if total_turns > 0 else 0.0
            ),
        }


# OpenAI-compatible wrapper for drop-in replacement
class GLMOpenAIWrapper:
    """OpenAI-compatible wrapper for GLM-4.7.

    Use this as a drop-in replacement for OpenAI client
    in existing codebases.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._client = GLMClient(api_key=api_key)
        self.chat = self._ChatCompletions(self._client)

    class _ChatCompletions:
        def __init__(self, client: GLMClient):
            self._client = client

        def create(
            self,
            model: str = "glm-4.7",
            messages: list[dict] = None,
            **kwargs,
        ) -> dict:
            """Create chat completion (OpenAI-compatible)."""
            response = self._client.generate(
                messages=messages or [],
                **kwargs,
            )

            # Return OpenAI-compatible format
            return {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content,
                    },
                    "finish_reason": response.finish_reason,
                }],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }
