#!/usr/bin/env python3
"""
Brave Search API Client

Complete implementation of Brave's Web Search API:
- Web search with 30B+ page index
- Freshness filtering (day, week, month, year)
- SafeSearch control
- Country and language filtering
- News, images, and videos endpoints
- Summarizer API (AI-powered summaries)

API Reference: https://api-dashboard.search.brave.com/app/documentation

Features:
- 100M+ daily page updates
- Privacy-focused (no user tracking)
- Fast response times
- Free tier available (2,000 queries/month)
"""

import os
import asyncio
import httpx
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Literal
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SafeSearch(Enum):
    """SafeSearch filtering levels."""
    OFF = "off"
    MODERATE = "moderate"
    STRICT = "strict"


class Freshness(Enum):
    """Time filter for search results."""
    DAY = "pd"      # Past day
    WEEK = "pw"     # Past week
    MONTH = "pm"    # Past month
    YEAR = "py"     # Past year


@dataclass
class BraveConfig:
    """Configuration for Brave Search API."""
    api_key: str
    base_url: str = "https://api.search.brave.com/res/v1"
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "BraveConfig":
        """Load from environment variables."""
        api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
        if not api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY not set")
        return cls(api_key=api_key)


@dataclass
class WebResult:
    """A web search result."""
    title: str
    url: str
    description: str
    age: str = ""
    language: str = ""
    family_friendly: bool = True
    extra_snippets: List[str] = field(default_factory=list)


@dataclass
class NewsResult:
    """A news search result."""
    title: str
    url: str
    description: str
    age: str = ""
    source: str = ""
    thumbnail: str = ""


@dataclass
class ImageResult:
    """An image search result."""
    title: str
    url: str
    source: str
    thumbnail: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BraveSearchResponse:
    """Response from Brave Search API."""
    query: str
    web_results: List[WebResult] = field(default_factory=list)
    news_results: List[NewsResult] = field(default_factory=list)
    image_results: List[ImageResult] = field(default_factory=list)
    infobox: Optional[Dict[str, Any]] = None
    discussions: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)


class BraveSearchClient:
    """
    Full-featured Brave Search API client.

    Usage:
        client = BraveSearchClient()

        # Web search
        response = await client.search("Python machine learning")

        # Fresh results only
        response = await client.search(
            "AI news",
            freshness=Freshness.DAY,
            count=20
        )

        # Country-specific
        response = await client.search(
            "local restaurants",
            country="us",
            search_lang="en"
        )

        # News search
        news = await client.news_search("technology", count=10)

        # Image search
        images = await client.image_search("neural network diagram")
    """

    def __init__(self, config: Optional[BraveConfig] = None):
        self.config = config or BraveConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={
                    "X-Subscription-Token": self.config.api_key,
                    "Accept": "application/json",
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
        count: int = 10,
        offset: int = 0,
        # Filtering
        safesearch: SafeSearch = SafeSearch.MODERATE,
        freshness: Optional[Freshness] = None,
        # Localization
        country: str = "us",
        search_lang: str = "en",
        ui_lang: str = "en-US",
        # Options
        text_decorations: bool = True,
        spellcheck: bool = True,
        result_filter: Optional[str] = None,
    ) -> BraveSearchResponse:
        """
        Perform a web search.

        Args:
            query: Search query (max 400 chars, 50 words)
            count: Number of results (1-20, default 10)
            offset: Result offset for pagination
            safesearch: Content filter level
            freshness: Time filter (day, week, month, year)
            country: Country code for results (e.g., "us", "gb", "de")
            search_lang: Language of search results
            ui_lang: UI language
            text_decorations: Include bold/italic markers
            spellcheck: Enable spell checking
            result_filter: Filter result types (e.g., "web,news")

        Returns:
            BraveSearchResponse with web results and metadata
        """
        client = await self._get_client()

        # Build query params
        params: Dict[str, Any] = {
            "q": query[:400],  # Max 400 chars
            "count": min(count, 20),
            "offset": offset,
            "safesearch": safesearch.value,
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "text_decorations": text_decorations,
            "spellcheck": spellcheck,
        }

        if freshness:
            params["freshness"] = freshness.value

        if result_filter:
            params["result_filter"] = result_filter

        response = await client.get("/web/search", params=params)
        response.raise_for_status()
        data = response.json()

        return self._parse_web_response(query, data)

    async def news_search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        freshness: Optional[Freshness] = None,
        country: str = "us",
    ) -> List[NewsResult]:
        """
        Search for news articles.

        Args:
            query: Search query
            count: Number of results
            offset: Pagination offset
            freshness: Time filter
            country: Country code

        Returns:
            List of news results
        """
        client = await self._get_client()

        params: Dict[str, Any] = {
            "q": query,
            "count": min(count, 20),
            "offset": offset,
            "country": country,
        }

        if freshness:
            params["freshness"] = freshness.value

        response = await client.get("/news/search", params=params)
        response.raise_for_status()
        data = response.json()

        return self._parse_news_results(data.get("results", []))

    async def image_search(
        self,
        query: str,
        count: int = 10,
        safesearch: SafeSearch = SafeSearch.MODERATE,
        country: str = "us",
    ) -> List[ImageResult]:
        """
        Search for images.

        Args:
            query: Search query
            count: Number of results
            safesearch: Content filter
            country: Country code

        Returns:
            List of image results
        """
        client = await self._get_client()

        params = {
            "q": query,
            "count": min(count, 20),
            "safesearch": safesearch.value,
            "country": country,
        }

        response = await client.get("/images/search", params=params)
        response.raise_for_status()
        data = response.json()

        return self._parse_image_results(data.get("results", []))

    async def summarize(
        self,
        query: str,
        summary_key: Optional[str] = None,
    ) -> str:
        """
        Get AI-powered summary for a search query.

        Requires Summarizer API access.

        Args:
            query: Search query
            summary_key: Optional summary key from prior search

        Returns:
            AI-generated summary text
        """
        client = await self._get_client()

        params: Dict[str, Any] = {"q": query}
        if summary_key:
            params["key"] = summary_key

        response = await client.get("/summarizer/search", params=params)
        response.raise_for_status()
        data = response.json()

        return data.get("summary", [{}])[0].get("data", "")

    def _parse_web_response(self, query: str, data: Dict[str, Any]) -> BraveSearchResponse:
        """Parse web search response."""
        web_results = []
        for result in data.get("web", {}).get("results", []):
            web_results.append(WebResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                description=result.get("description", ""),
                age=result.get("age", ""),
                language=result.get("language", ""),
                family_friendly=result.get("family_friendly", True),
                extra_snippets=result.get("extra_snippets", []),
            ))

        news_results = self._parse_news_results(data.get("news", {}).get("results", []))
        image_results = self._parse_image_results(data.get("images", {}).get("results", []))

        return BraveSearchResponse(
            query=query,
            web_results=web_results,
            news_results=news_results,
            image_results=image_results,
            infobox=data.get("infobox"),
            discussions=data.get("discussions", {}).get("results", []),
            raw_response=data,
        )

    def _parse_news_results(self, results: List[Dict]) -> List[NewsResult]:
        """Parse news results."""
        return [
            NewsResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                description=r.get("description", ""),
                age=r.get("age", ""),
                source=r.get("meta_url", {}).get("netloc", ""),
                thumbnail=r.get("thumbnail", {}).get("src", ""),
            )
            for r in results
        ]

    def _parse_image_results(self, results: List[Dict]) -> List[ImageResult]:
        """Parse image results."""
        return [
            ImageResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                source=r.get("source", ""),
                thumbnail=r.get("thumbnail", {}).get("src", ""),
                properties=r.get("properties", {}),
            )
            for r in results
        ]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_client: Optional[BraveSearchClient] = None


def get_client() -> BraveSearchClient:
    """Get the default Brave Search client."""
    global _default_client
    if _default_client is None:
        _default_client = BraveSearchClient()
    return _default_client


async def search(query: str, **kwargs) -> BraveSearchResponse:
    """Quick search with default client."""
    return await get_client().search(query, **kwargs)


async def news_search(query: str, **kwargs) -> List[NewsResult]:
    """News search with default client."""
    return await get_client().news_search(query, **kwargs)


async def image_search(query: str, **kwargs) -> List[ImageResult]:
    """Image search with default client."""
    return await get_client().image_search(query, **kwargs)


# =============================================================================
# CLI DEMO
# =============================================================================

async def demo():
    """Demonstrate Brave Search API capabilities."""
    print("=" * 70)
    print("Brave Search API Client Demo")
    print("=" * 70)

    client = BraveSearchClient()

    try:
        # Basic web search
        print("\n1. Web Search")
        print("-" * 40)
        response = await client.search("Python machine learning libraries")
        print(f"Query: {response.query}")
        print(f"Results: {len(response.web_results)}")
        for result in response.web_results[:3]:
            print(f"  - {result.title}")
            print(f"    {result.url}")

        # Fresh results
        print("\n2. Fresh Results (past week)")
        print("-" * 40)
        response = await client.search(
            "AI news",
            freshness=Freshness.WEEK,
            count=5
        )
        for result in response.web_results[:3]:
            print(f"  - {result.title} ({result.age})")

        # News search
        print("\n3. News Search")
        print("-" * 40)
        news = await client.news_search("technology", count=5)
        for article in news[:3]:
            print(f"  - {article.title}")
            print(f"    Source: {article.source}")

        # Image search
        print("\n4. Image Search")
        print("-" * 40)
        images = await client.image_search("neural network", count=5)
        for img in images[:3]:
            print(f"  - {img.title}")
            print(f"    {img.url}")

    finally:
        await client.close()

    print("\n" + "=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
