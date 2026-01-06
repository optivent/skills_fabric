"""GLM-4.7 SDK Client for Skills Fabric.

Connects to Z.ai API for GLM-4.7 coding model access.
Supports preserved thinking for multi-turn coding agents.

Features:
- OpenAI-compatible API
- Preserved thinking mode (reasoning persists across turns)
- Streaming support
- Cost tracking ($0.60/1M in, $2.20/1M out)

Usage:
    from skills_fabric.llm import GLMClient

    client = GLMClient(api_key="your-key")
    response = client.generate(
        messages=[{"role": "user", "content": "Write a function..."}],
        thinking=True,
    )
"""
from dataclasses import dataclass, field
from typing import Optional, Iterator, Any
from enum import Enum
import os
import json
import time

# Try to import httpx for async support, fall back to requests
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    import requests


class ThinkingMode(Enum):
    """GLM-4.7 thinking modes."""
    DISABLED = "disabled"
    ENABLED = "enabled"
    PRESERVED = "preserved"  # Keeps thinking across turns


@dataclass
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0

    @property
    def cost_usd(self) -> float:
        """Calculate cost in USD."""
        input_cost = (self.prompt_tokens / 1_000_000) * 0.60
        output_cost = ((self.completion_tokens + self.thinking_tokens) / 1_000_000) * 2.20
        return input_cost + output_cost


@dataclass
class GLMResponse:
    """Response from GLM-4.7 API."""
    content: str
    thinking: Optional[str] = None
    finish_reason: str = "stop"
    usage: TokenUsage = field(default_factory=TokenUsage)
    model: str = "glm-4.7"
    latency_ms: float = 0.0

    @property
    def has_thinking(self) -> bool:
        return self.thinking is not None and len(self.thinking) > 0


@dataclass
class GLMConfig:
    """Configuration for GLM client."""
    api_key: str = ""
    base_url: str = "https://api.z.ai/api/paas/v4"
    model: str = "glm-4.7"
    max_tokens: int = 4096
    temperature: float = 1.0
    top_p: float = 0.95
    timeout: int = 120
    thinking_mode: ThinkingMode = ThinkingMode.ENABLED

    @classmethod
    def from_env(cls) -> "GLMConfig":
        """Create config from environment variables."""
        return cls(
            api_key=os.getenv("ZAI_API_KEY", os.getenv("GLM_API_KEY", "")),
            base_url=os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4"),
            model=os.getenv("GLM_MODEL", "glm-4.7"),
        )


class GLMClient:
    """Client for GLM-4.7 API.

    Supports both sync and async operations.
    Compatible with OpenAI message format.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[GLMConfig] = None,
    ):
        """Initialize GLM client.

        Args:
            api_key: Z.ai API key (or set ZAI_API_KEY env var)
            config: Optional full configuration
        """
        if config:
            self.config = config
        else:
            self.config = GLMConfig.from_env()
            if api_key:
                self.config.api_key = api_key

        if not self.config.api_key:
            raise ValueError(
                "API key required. Set ZAI_API_KEY env var or pass api_key parameter."
            )

        self._session = None
        self._total_usage = TokenUsage()

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

        # Configure thinking mode
        if thinking:
            if preserve_thinking:
                payload["thinking"] = {"type": "enabled"}
                payload["chat_template_kwargs"] = {
                    "enable_thinking": True,
                    "clear_thinking": False,  # Preserve across turns
                }
            else:
                payload["thinking"] = {"type": "enabled"}
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
            return self._parse_response(response, latency_ms)

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

    def _parse_response(self, data: dict, latency_ms: float) -> GLMResponse:
        """Parse API response into GLMResponse."""
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})

        # Extract content and thinking
        content = message.get("content", "")
        thinking = None

        # Check for thinking in message
        if "thinking" in message:
            thinking = message["thinking"]
        elif "reasoning_content" in message:
            thinking = message["reasoning_content"]

        # Parse usage
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            thinking_tokens=usage_data.get("thinking_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        # Track cumulative usage
        self._total_usage.prompt_tokens += usage.prompt_tokens
        self._total_usage.completion_tokens += usage.completion_tokens
        self._total_usage.thinking_tokens += usage.thinking_tokens
        self._total_usage.total_tokens += usage.total_tokens

        return GLMResponse(
            content=content,
            thinking=thinking,
            finish_reason=choice.get("finish_reason", "stop"),
            usage=usage,
            model=data.get("model", self.config.model),
            latency_ms=latency_ms,
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
    ) -> GLMResponse:
        """Simple chat interface.

        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            thinking: Enable thinking mode

        Returns:
            GLMResponse
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_message})

        return self.generate(messages, thinking=thinking)

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

    def get_total_usage(self) -> TokenUsage:
        """Get cumulative token usage."""
        return self._total_usage

    def reset_usage(self):
        """Reset usage tracking."""
        self._total_usage = TokenUsage()


class GLMCodingAgent:
    """Coding agent using GLM-4.7 with preserved thinking.

    Maintains conversation history and thinking state
    across multiple turns for complex coding tasks.
    """

    def __init__(
        self,
        client: Optional[GLMClient] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize coding agent.

        Args:
            client: GLM client instance
            system_prompt: Custom system prompt
        """
        self.client = client or GLMClient()
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.messages: list[dict] = []
        self.thinking_history: list[str] = []

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
    ) -> GLMResponse:
        """Send a message and get response.

        Args:
            message: User message
            preserve_thinking: Keep thinking across turns

        Returns:
            GLMResponse
        """
        # Add user message
        self.messages.append({
            "role": "user",
            "content": message,
        })

        # Generate response
        response = self.client.generate(
            messages=self.messages,
            thinking=True,
            preserve_thinking=preserve_thinking,
        )

        # Add assistant response to history
        self.messages.append({
            "role": "assistant",
            "content": response.content,
        })

        # Track thinking
        if response.thinking:
            self.thinking_history.append(response.thinking)

        return response

    def reset(self):
        """Reset conversation history."""
        self.messages = [{
            "role": "system",
            "content": self.system_prompt,
        }]
        self.thinking_history = []

    def get_conversation(self) -> list[dict]:
        """Get full conversation history."""
        return self.messages.copy()


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
