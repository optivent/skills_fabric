#!/usr/bin/env python3
"""
GLM-4.7 Research Assistant - Anchored to Coding Plan

This module provides convenience functions for research tasks using
Z.ai's GLM-4.7 thinking model via the Coding Plan endpoint.

Usage:
    from glm_research import research_query, web_search

    # Research with thinking mode (16K token budget)
    response = research_query("Relationship between diabetes and dry eye disease")

    # Web search
    results = web_search("latest diabetes ocular complications 2025")
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

# Import Z.ai SDK - try installed package first, then local path
try:
    from zai import ZaiClient
    from zai.cost_tracker import cost_from_response, CostBreakdown
except ImportError:
    # Fall back to local SDK path for development
    SDK_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'zai-sdk', 'src')
    if os.path.exists(SDK_PATH):
        sys.path.insert(0, os.path.abspath(SDK_PATH))
        from zai import ZaiClient
        from zai.cost_tracker import cost_from_response, CostBreakdown
    else:
        raise ImportError(
            "Z.ai SDK not found. Install it with 'pip install zai' "
            f"or ensure {SDK_PATH} exists."
        )

# Initialize client (uses Coding Plan endpoint by default now)
_client = None


def get_client() -> ZaiClient:
    """Get or create the ZaiClient singleton."""
    global _client
    if _client is None:
        _client = ZaiClient()
    return _client


def research_query(
    prompt: str,
    thinking_budget: int = 16000,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    show_cost: bool = True
) -> dict:
    """
    Research query with GLM-4.7 thinking mode.

    Args:
        prompt: Research question or task
        thinking_budget: Max tokens for reasoning (default 16K)
        max_tokens: Max output tokens
        temperature: Sampling temperature
        show_cost: Print cost breakdown

    Returns:
        dict with 'content', 'reasoning', 'cost', 'usage'
    """
    client = get_client()

    response = client.chat.completions.create(
        model="glm-4.7",
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "enabled", "budget_tokens": thinking_budget},
        max_tokens=max_tokens,
        temperature=temperature
    )

    # Extract content and reasoning
    message = response.choices[0].message
    content = message.content or ""
    reasoning = getattr(message, 'reasoning_content', "") or ""

    # GLM-4.7: If content is empty but reasoning exists, use reasoning as content
    if not content and reasoning:
        content = reasoning

    # Calculate cost
    cost = cost_from_response(response)

    if show_cost and cost:
        logger.info(f"\n{'='*60}")
        logger.info(str(cost))

    return {
        "content": content,
        "reasoning": reasoning,
        "cost": cost,
        "usage": response.usage,
        "model": response.model
    }


def web_search(
    query: str,
    count: int = 10,
    show_cost: bool = True
) -> dict:
    """
    Web search via GLM-4.7.

    Args:
        query: Search query
        count: Number of results
        show_cost: Print cost breakdown

    Returns:
        dict with search results
    """
    client = get_client()

    response = client.web_search.web_search(
        search_query=query,
        count=count
    )

    return response


def quick_answer(
    question: str,
    max_tokens: int = 500,
    show_cost: bool = True
) -> str:
    """
    Quick answer without extended thinking (faster, cheaper).

    Args:
        question: Simple question
        max_tokens: Max output tokens
        show_cost: Print cost breakdown

    Returns:
        Answer string
    """
    client = get_client()

    response = client.chat.completions.create(
        model="glm-4.7",
        messages=[{"role": "user", "content": question}],
        max_tokens=max_tokens
    )

    content = response.choices[0].message.content or ""

    if show_cost:
        cost = cost_from_response(response)
        if cost:
            logger.info(f"\n{'='*60}")
            logger.info(str(cost))

    return content


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GLM-4.7 Research Assistant")
    parser.add_argument("prompt", help="Research question or query")
    parser.add_argument("--web-search", "-w", action="store_true",
                        help="Use web search mode")
    parser.add_argument("--quick", "-q", action="store_true",
                        help="Quick answer without thinking mode")
    parser.add_argument("--thinking-budget", "-t", type=int, default=16000,
                        help="Thinking token budget (default: 16000)")
    parser.add_argument("--max-tokens", "-m", type=int, default=4000,
                        help="Max output tokens (default: 4000)")

    args = parser.parse_args()

    if args.web_search:
        result = web_search(args.prompt)
        print(result)
    elif args.quick:
        answer = quick_answer(args.prompt, max_tokens=args.max_tokens)
        print(answer)
    else:
        result = research_query(
            args.prompt,
            thinking_budget=args.thinking_budget,
            max_tokens=args.max_tokens
        )
        if result["reasoning"]:
            print("\n=== REASONING ===")
            print(result["reasoning"][:500] + "..." if len(result["reasoning"]) > 500 else result["reasoning"])
        print("\n=== ANSWER ===")
        print(result["content"])
