#!/usr/bin/env python3
"""
Perplexity API Client

Complete implementation of Perplexity's Sonar API with all features:
- All Sonar models (sonar, sonar-pro, sonar-reasoning, sonar-deep-research)
- Search domain filtering (allowlist/denylist)
- Search recency filtering (hour, day, week, month)
- Citation and image retrieval
- Search context size control
- Streaming support
- Async operations

API Reference: https://docs.perplexity.ai/

Models and Pricing (January 2026):
- sonar: $1/M input, $1/M output, $5-12/1K requests
- sonar-pro: $3/M input, $15/M output, best factuality (F=0.858)
- sonar-reasoning: Extended reasoning chains
- sonar-reasoning-pro: Advanced reasoning with citations
- sonar-deep-research: Multi-step research agent
"""

import os
import json
import asyncio
import httpx
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, AsyncIterator, Literal
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SonarModel(Enum):
    """Available Sonar models."""
    SONAR = "sonar"                          # Fast, cost-effective
    SONAR_PRO = "sonar-pro"                  # Best factuality (F=0.858)
    SONAR_REASONING = "sonar-reasoning"       # Reasoning chains
    SONAR_REASONING_PRO = "sonar-reasoning-pro"  # Advanced reasoning
    SONAR_DEEP_RESEARCH = "sonar-deep-research"  # Multi-step research


class SearchRecency(Enum):
    """Time filter for search results."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class SearchContextSize(Enum):
    """Context size for search results."""
    LOW = "low"      # Minimizes context, lower cost
    MEDIUM = "medium"  # Balanced (default)
    HIGH = "high"    # Maximizes context, higher cost


@dataclass
class PerplexityConfig:
    """Configuration for Perplexity API."""
    api_key: str
    base_url: str = "https://api.perplexity.ai"
    default_model: SonarModel = SonarModel.SONAR_PRO
    timeout: float = 60.0

    @classmethod
    def from_env(cls) -> "PerplexityConfig":
        """Load from environment variables."""
        api_key = os.getenv("PERPLEXITY_API_KEY", "")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        return cls(api_key=api_key)


@dataclass
class Citation:
    """A citation from search results."""
    url: str
    title: str = ""
    snippet: str = ""


@dataclass
class PerplexityResponse:
    """Response from Perplexity API."""
    content: str
    model: str
    citations: List[Citation] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    related_questions: List[str] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


class PerplexityClient:
    """
    Full-featured Perplexity API client.

    Usage:
        client = PerplexityClient()

        # Simple search
        response = await client.search("What is LangGraph?")

        # Deep research with domain filter
        response = await client.deep_research(
            "Latest advances in agentic AI",
            domains=["arxiv.org", "github.com"],
            recency="month"
        )

        # Streaming response
        async for chunk in client.stream("Explain transformers"):
            print(chunk, end="", flush=True)
    """

    def __init__(self, config: Optional[PerplexityConfig] = None):
        self.config = config or PerplexityConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def search(
        self,
        query: str,
        model: Optional[SonarModel] = None,
        system_prompt: Optional[str] = None,
        # Search parameters
        recency: Optional[SearchRecency] = None,
        context_size: SearchContextSize = SearchContextSize.MEDIUM,
        domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        # Response options
        return_citations: bool = True,
        return_images: bool = False,
        return_related_questions: bool = False,
        # Generation parameters
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_tokens: int = 4096,
    ) -> PerplexityResponse:
        """
        Perform a search query with Perplexity.

        Args:
            query: The search query
            model: Sonar model to use (default: sonar-pro)
            system_prompt: Custom system prompt
            recency: Filter results by time (hour, day, week, month)
            context_size: Amount of search context (low, medium, high)
            domains: Only include results from these domains (max 20)
            exclude_domains: Exclude results from these domains (prefix with -)
            return_citations: Include citation URLs in response
            return_images: Include images in response (Tier-2+ only)
            return_related_questions: Include related questions
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens in response

        Returns:
            PerplexityResponse with content, citations, images, etc.
        """
        client = await self._get_client()
        model = model or self.config.default_model

        # Build request
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        payload: Dict[str, Any] = {
            "model": model.value,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "return_citations": return_citations,
            "return_images": return_images,
            "return_related_questions": return_related_questions,
            "search_context_size": context_size.value,
        }

        # Add recency filter
        if recency:
            payload["search_recency_filter"] = recency.value

        # Add domain filter (allowlist or denylist, not both)
        if domains:
            # Allowlist mode
            payload["search_domain_filter"] = domains[:20]
        elif exclude_domains:
            # Denylist mode (prefix with -)
            payload["search_domain_filter"] = [f"-{d}" for d in exclude_domains[:20]]

        # Make request
        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        return self._parse_response(data)

    async def deep_research(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        domains: Optional[List[str]] = None,
        recency: Optional[SearchRecency] = None,
    ) -> PerplexityResponse:
        """
        Perform deep multi-step research.

        Uses sonar-deep-research model for comprehensive analysis.

        Args:
            query: Research question
            system_prompt: Custom instructions
            domains: Limit to specific domains
            recency: Time filter

        Returns:
            Comprehensive research response with citations
        """
        return await self.search(
            query=query,
            model=SonarModel.SONAR_DEEP_RESEARCH,
            system_prompt=system_prompt or """You are a research assistant.
            Provide comprehensive, well-cited answers with multiple perspectives.
            Structure your response with clear sections.""",
            domains=domains,
            recency=recency,
            context_size=SearchContextSize.HIGH,
            return_citations=True,
            return_related_questions=True,
            max_tokens=8192,
        )

    async def quick_search(
        self,
        query: str,
        recency: Optional[SearchRecency] = None,
    ) -> PerplexityResponse:
        """
        Fast, cost-effective search.

        Uses sonar model for quick lookups.
        """
        return await self.search(
            query=query,
            model=SonarModel.SONAR,
            recency=recency,
            context_size=SearchContextSize.LOW,
            max_tokens=1024,
        )

    async def reasoning_search(
        self,
        query: str,
        system_prompt: Optional[str] = None,
    ) -> PerplexityResponse:
        """
        Search with extended reasoning chains.

        Uses sonar-reasoning-pro for complex analysis.
        """
        return await self.search(
            query=query,
            model=SonarModel.SONAR_REASONING_PRO,
            system_prompt=system_prompt or """Think step by step.
            Show your reasoning process before providing conclusions.""",
            context_size=SearchContextSize.HIGH,
            max_tokens=4096,
        )

    async def stream(
        self,
        query: str,
        model: Optional[SonarModel] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream response chunks.

        Yields text chunks as they arrive.

        Usage:
            async for chunk in client.stream("Explain neural networks"):
                print(chunk, end="", flush=True)
        """
        client = await self._get_client()
        model = model or self.config.default_model

        messages = [{"role": "user", "content": query}]

        payload = {
            "model": model.value,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        async with client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    def _parse_response(self, data: Dict[str, Any]) -> PerplexityResponse:
        """Parse API response into structured format."""
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})

        # Parse citations
        citations = []
        for citation in data.get("citations", []):
            if isinstance(citation, str):
                citations.append(Citation(url=citation))
            elif isinstance(citation, dict):
                citations.append(Citation(
                    url=citation.get("url", ""),
                    title=citation.get("title", ""),
                    snippet=citation.get("snippet", "")
                ))

        return PerplexityResponse(
            content=message.get("content", ""),
            model=data.get("model", ""),
            citations=citations,
            images=data.get("images", []),
            related_questions=data.get("related_questions", []),
            usage=data.get("usage", {}),
            raw_response=data
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_client: Optional[PerplexityClient] = None


def get_client() -> PerplexityClient:
    """Get the default Perplexity client."""
    global _default_client
    if _default_client is None:
        _default_client = PerplexityClient()
    return _default_client


async def search(query: str, **kwargs) -> PerplexityResponse:
    """Quick search with default client."""
    return await get_client().search(query, **kwargs)


async def deep_research(query: str, **kwargs) -> PerplexityResponse:
    """Deep research with default client."""
    return await get_client().deep_research(query, **kwargs)


async def quick_search(query: str, **kwargs) -> PerplexityResponse:
    """Fast search with default client."""
    return await get_client().quick_search(query, **kwargs)


# =============================================================================
# CLI DEMO
# =============================================================================

async def demo():
    """Demonstrate Perplexity API capabilities."""
    print("=" * 70)
    print("Perplexity API Client Demo")
    print("=" * 70)

    client = PerplexityClient()

    try:
        # Quick search
        print("\n1. Quick Search (sonar)")
        print("-" * 40)
        response = await client.quick_search("What is the capital of France?")
        print(f"Answer: {response.content[:200]}...")
        print(f"Model: {response.model}")

        # Pro search with citations
        print("\n2. Pro Search with Citations (sonar-pro)")
        print("-" * 40)
        response = await client.search(
            "What are the latest advances in agentic AI?",
            model=SonarModel.SONAR_PRO,
            recency=SearchRecency.MONTH,
            return_citations=True,
        )
        print(f"Answer: {response.content[:300]}...")
        print(f"Citations: {len(response.citations)}")
        for citation in response.citations[:3]:
            print(f"  - {citation.url}")

        # Domain-filtered search
        print("\n3. Domain-Filtered Search")
        print("-" * 40)
        response = await client.search(
            "transformer architecture",
            domains=["arxiv.org", "github.com"],
            return_citations=True,
        )
        print(f"Answer: {response.content[:200]}...")
        print(f"Sources limited to: arxiv.org, github.com")

        # Streaming
        print("\n4. Streaming Response")
        print("-" * 40)
        print("Streaming: ", end="")
        async for chunk in client.stream("Explain machine learning in 50 words"):
            print(chunk, end="", flush=True)
        print("\n")

    finally:
        await client.close()

    print("=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
