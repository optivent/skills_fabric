"""LLM backends for Skills Fabric.

Supported models:
- GLM-4.7 (Z.ai) - Primary coding model with preserved thinking
- OpenAI compatible models via wrapper
"""
from .glm_client import (
    GLMClient,
    GLMConfig,
    GLMResponse,
    GLMCodingAgent,
    GLMOpenAIWrapper,
    ThinkingMode,
    TokenUsage,
)

__all__ = [
    'GLMClient',
    'GLMConfig',
    'GLMResponse',
    'GLMCodingAgent',
    'GLMOpenAIWrapper',
    'ThinkingMode',
    'TokenUsage',
]
