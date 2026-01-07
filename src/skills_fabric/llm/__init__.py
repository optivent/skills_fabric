"""LLM backends for Skills Fabric.

Supported models:
- GLM-4.7 (Z.ai) - Primary coding model with preserved thinking
- OpenAI compatible models via wrapper

Features:
- Thinking/reasoning mode with budget control
- Automatic fallback to non-thinking mode on failures
- Reasoning metrics tracking
- Async streaming for long-running code analysis
- Stream interruption handling
"""
from .glm_client import (
    GLMClient,
    GLMConfig,
    GLMResponse,
    GLMCodingAgent,
    GLMOpenAIWrapper,
    ThinkingMode,
    TokenUsage,
    ReasoningFailureType,
    ReasoningMetrics,
    # Streaming support
    StreamChunk,
    StreamingStats,
    StreamInterruptionType,
)

__all__ = [
    'GLMClient',
    'GLMConfig',
    'GLMResponse',
    'GLMCodingAgent',
    'GLMOpenAIWrapper',
    'ThinkingMode',
    'TokenUsage',
    'ReasoningFailureType',
    'ReasoningMetrics',
    # Streaming support
    'StreamChunk',
    'StreamingStats',
    'StreamInterruptionType',
]
