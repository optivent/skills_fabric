"""
Cost tracking utility for Z.ai GLM Coding Plan

Pricing as of January 2026 (per 1M tokens):
- GLM-4.7: $0.60 input, $2.20 output, $0.11 cached
- GLM-4.6: $0.60 input, $2.20 output, $0.11 cached
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for an API call"""
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    input_cost: float
    cached_cost: float
    output_cost: float
    total_cost: float

    def __str__(self):
        return (
            f"Cost Breakdown ({self.model}):\n"
            f"  Input: {self.input_tokens} tokens (${self.input_cost:.6f})\n"
            f"  Cached: {self.cached_tokens} tokens (${self.cached_cost:.6f})\n"
            f"  Output: {self.output_tokens} tokens (${self.output_cost:.6f})\n"
            f"  Total: ${self.total_cost:.6f}"
        )


# Pricing per 1M tokens (GLM Coding Plan)
PRICING = {
    "glm-4.7": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4.6": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4.5-air": {"input": 0.20, "output": 0.60, "cached": 0.04},
    "glm-4.5v": {"input": 0.60, "output": 1.80, "cached": 0.11},
    "glm-4.6v": {"input": 0.60, "output": 1.80, "cached": 0.11},
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0
) -> CostBreakdown:
    """
    Calculate cost for a GLM API call.

    Args:
        model: Model name (e.g., "glm-4.7")
        input_tokens: Total input tokens
        output_tokens: Total output tokens
        cached_tokens: Tokens served from cache (subset of input_tokens)

    Returns:
        CostBreakdown with detailed cost information
    """
    pricing = PRICING.get(model, PRICING["glm-4.7"])

    # Cached tokens get discounted rate
    non_cached_input = input_tokens - cached_tokens

    input_cost = (non_cached_input / 1_000_000) * pricing["input"]
    cached_cost = (cached_tokens / 1_000_000) * pricing["cached"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + cached_cost + output_cost

    return CostBreakdown(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        input_cost=input_cost,
        cached_cost=cached_cost,
        output_cost=output_cost,
        total_cost=total_cost
    )


def cost_from_response(response) -> Optional[CostBreakdown]:
    """
    Extract cost from a chat completion response.

    Args:
        response: ChatCompletion response object

    Returns:
        CostBreakdown or None if usage info not available
    """
    if not hasattr(response, 'usage') or response.usage is None:
        return None

    usage = response.usage
    model = getattr(response, 'model', 'glm-4.7')

    # Extract cached tokens if available
    cached_tokens = 0
    if hasattr(usage, 'prompt_tokens_details'):
        details = usage.prompt_tokens_details
        if hasattr(details, 'cached_tokens'):
            cached_tokens = details.cached_tokens or 0

    return calculate_cost(
        model=model,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        cached_tokens=cached_tokens
    )
