"""Brave Search API Client for Skills Fabric.

Provides web and news search for documentation and code discovery.
Based on the older_project pattern (older_project/andreea_tools/discovery/brave_client.py).

Features:
- Web search with freshness filters (pd, pw, pm, py)
- News search endpoint
- Academic/technical source filtering
- Rate limiting with exponential backoff
- Relevance scoring for results
- Max 20 results per query (API limit)

IMPORTANT: Uses X-Subscription-Token header (NOT Authorization).

Usage:
    from skills_fabric.retrievals import BraveSearchClient

    # Basic web search
    client = BraveSearchClient()
    results = await client.search("LangGraph StateGraph tutorial")
    for result in results:
        print(f"{result.title}: {result.url}")

    # Fresh results (past week)
    results = await client.search(
        "Python async patterns",
        freshness=Freshness.WEEK,
        count=10
    )

    # News search
    news = await client.search_news("AI frameworks 2025")

    # Academic/technical sources
    results = await client.search_technical("LangGraph documentation")

    # Synchronous interface
    results = client.search_sync("Python dataclasses")

API Reference: https://api.search.brave.com/app/documentation
"""
from __future__ import annotations

import os
import asyncio
import random
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum

# Get logger for this module
logger = logging.getLogger(__name__)

# Try to import httpx for async support
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    import requests


class Freshness(Enum):
    """Time filter for search results.

    Brave Search supports filtering results by recency:
    - DAY: Past 24 hours
    - WEEK: Past 7 days
    - MONTH: Past 30 days
    - YEAR: Past 365 days
    """
    DAY = "pd"    # Past day (24 hours)
    WEEK = "pw"   # Past week
    MONTH = "pm"  # Past month
    YEAR = "py"   # Past year


class SafeSearch(Enum):
    """SafeSearch filtering level.

    Controls adult content filtering:
    - OFF: No filtering
    - MODERATE: Filter explicit content
    - STRICT: Maximum filtering
    """
    OFF = "off"
    MODERATE = "moderate"
    STRICT = "strict"


class ResultSource(Enum):
    """Source type for search results."""
    WEB = "brave_web"
    NEWS = "brave_news"
    IMAGES = "brave_images"
    ACADEMIC = "brave_academic"


@dataclass
class SearchResult:
    """A search result from Brave Search API.

    Contains the result metadata plus relevance scoring.
    """
    title: str
    url: str
    description: str
    source: ResultSource = ResultSource.WEB
    date: Optional[str] = None  # Age of the result (e.g., "2 days ago")
    relevance_score: float = 0.0  # 0.0-1.0, higher is more relevant
    language: Optional[str] = None
    family_friendly: bool = True
    extra_snippets: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "source": self.source.value,
            "date": self.date,
            "relevance_score": self.relevance_score,
            "language": self.language,
            "family_friendly": self.family_friendly,
            "extra_snippets": self.extra_snippets,
            "metadata": self.metadata,
        }

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""


@dataclass
class BraveSearchResponse:
    """Response from a Brave Search query.

    Contains results, query metadata, and search statistics.
    """
    query: str
    results: list[SearchResult] = field(default_factory=list)
    total_results: int = 0
    latency_ms: float = 0.0
    query_type: str = "web"  # web, news, images
    altered_query: Optional[str] = None  # If query was auto-corrected

    @property
    def result_count(self) -> int:
        """Get number of results."""
        return len(self.results)

    @property
    def urls(self) -> list[str]:
        """Get list of result URLs."""
        return [r.url for r in self.results]

    @property
    def has_results(self) -> bool:
        """Check if search returned results."""
        return len(self.results) > 0

    def get_top_results(self, n: int = 5) -> list[SearchResult]:
        """Get top N results by relevance score."""
        sorted_results = sorted(self.results, key=lambda r: r.relevance_score, reverse=True)
        return sorted_results[:n]

    def filter_by_domain(self, domains: list[str]) -> list[SearchResult]:
        """Filter results to specific domains."""
        domains_lower = [d.lower() for d in domains]
        return [r for r in self.results if r.domain in domains_lower]

    def to_dict(self) -> dict:
        """Convert response to dictionary."""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "latency_ms": self.latency_ms,
            "query_type": self.query_type,
            "result_count": self.result_count,
        }


@dataclass
class BraveConfig:
    """Configuration for Brave Search client.

    Can be loaded from environment variables via from_env().
    """
    api_key: str = ""
    base_url: str = "https://api.search.brave.com/res/v1"
    timeout: float = 30.0
    # Rate limiting
    max_retries: int = 3
    initial_retry_delay: float = 1.0  # seconds
    max_retry_delay: float = 30.0  # seconds
    retry_multiplier: float = 2.0  # exponential backoff

    @classmethod
    def from_env(cls) -> "BraveConfig":
        """Create config from environment variables.

        Environment variables:
            BRAVE_API_KEY: API key (required)
            BRAVE_TIMEOUT: Request timeout in seconds (default: 30)
        """
        return cls(
            api_key=os.getenv("BRAVE_API_KEY", ""),
            timeout=float(os.getenv("BRAVE_TIMEOUT", "30")),
        )


class BraveSearchClient:
    """Client for Brave Search API.

    Uses the X-Subscription-Token header for authentication (NOT Authorization).
    Supports web search, news search, and specialized technical/academic filtering.

    Example:
        # Basic usage
        client = BraveSearchClient()
        results = await client.search("Python type hints")

        # With freshness filter
        results = await client.search(
            "LangGraph tutorial",
            freshness=Freshness.MONTH,
            count=15
        )

        # News search
        news = await client.search_news("AI developments", count=10)

        # Technical sources only
        results = await client.search_technical("async await patterns")
    """

    # Maximum results per query (API limit)
    MAX_RESULTS_PER_QUERY = 20

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[BraveConfig] = None,
    ):
        """Initialize Brave Search client.

        Args:
            api_key: Brave API key (or set BRAVE_API_KEY env var)
            config: Optional full configuration
        """
        if config:
            self.config = config
        else:
            self.config = BraveConfig.from_env()
            if api_key:
                self.config.api_key = api_key

        if not self.config.api_key:
            raise ValueError(
                "Brave Search API key required. "
                "Set BRAVE_API_KEY env var or pass api_key parameter."
            )

        if not HTTPX_AVAILABLE:
            logger.warning(
                "httpx not available. Async methods will use synchronous fallback. "
                "Install httpx for better async support: pip install httpx"
            )

        self._request_count = 0
        self._retry_count = 0
        self._total_latency_ms = 0.0

    @property
    def headers(self) -> dict:
        """Get request headers.

        IMPORTANT: Uses X-Subscription-Token (NOT Authorization) per Brave API spec.
        """
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.config.api_key,
        }

    async def search(
        self,
        query: str,
        count: int = 10,
        freshness: Optional[Freshness] = None,
        safesearch: SafeSearch = SafeSearch.MODERATE,
        country: str = "us",
        search_lang: str = "en",
        text_decorations: bool = False,
    ) -> BraveSearchResponse:
        """Search the web using Brave Search API.

        Args:
            query: Search query (max 400 characters)
            count: Number of results (1-20, default 10)
            freshness: Time filter - DAY, WEEK, MONTH, YEAR
            safesearch: Content filter level
            country: Country code (e.g., "us", "uk", "de")
            search_lang: Language code (e.g., "en", "es", "fr")
            text_decorations: Include bold/italic markers in snippets

        Returns:
            BraveSearchResponse with search results
        """
        params = {
            "q": query[:400],  # Trim to max length
            "count": min(count, self.MAX_RESULTS_PER_QUERY),
            "safesearch": safesearch.value,
            "country": country,
            "search_lang": search_lang,
            "text_decorations": str(text_decorations).lower(),
        }

        if freshness:
            params["freshness"] = freshness.value

        response = await self._request_with_retry(
            endpoint="/web/search",
            params=params,
        )

        return self._parse_web_response(query, response)

    async def search_news(
        self,
        query: str,
        count: int = 10,
        freshness: Optional[Freshness] = Freshness.MONTH,  # Default to past month for news
        country: str = "us",
    ) -> BraveSearchResponse:
        """Search news articles using Brave Search API.

        Args:
            query: Search query
            count: Number of results (1-20)
            freshness: Time filter (defaults to past month for news)
            country: Country code

        Returns:
            BraveSearchResponse with news results
        """
        params = {
            "q": query,
            "count": min(count, self.MAX_RESULTS_PER_QUERY),
            "country": country,
        }

        if freshness:
            params["freshness"] = freshness.value

        response = await self._request_with_retry(
            endpoint="/news/search",
            params=params,
        )

        return self._parse_news_response(query, response)

    async def search_technical(
        self,
        query: str,
        count: int = 10,
        freshness: Optional[Freshness] = None,
    ) -> BraveSearchResponse:
        """Search for technical/documentation content.

        Filters results to known technical/academic sources like:
        - GitHub, GitLab
        - Official documentation sites
        - Stack Overflow
        - Academic sources (arxiv, papers)

        Args:
            query: Search query
            count: Number of results
            freshness: Time filter

        Returns:
            BraveSearchResponse filtered to technical sources
        """
        # Enhance query with technical site filters
        technical_sites = [
            "site:github.com",
            "site:docs.python.org",
            "site:readthedocs.io",
            "site:stackoverflow.com",
            "site:dev.to",
            "site:medium.com",
            "site:arxiv.org",
            "site:langchain.com",
        ]

        # Build OR query for technical sites
        site_filter = " OR ".join(technical_sites)
        enhanced_query = f"({query}) ({site_filter})"

        response = await self.search(
            enhanced_query,
            count=count,
            freshness=freshness,
        )

        # Update source type
        for result in response.results:
            result.source = ResultSource.ACADEMIC

        return response

    async def search_documentation(
        self,
        library_name: str,
        topic: Optional[str] = None,
        count: int = 10,
    ) -> BraveSearchResponse:
        """Search for library documentation.

        Optimized for finding API docs, tutorials, and examples.

        Args:
            library_name: Name of the library (e.g., "LangGraph", "FastAPI")
            topic: Optional specific topic within the library
            count: Number of results

        Returns:
            BraveSearchResponse with documentation results
        """
        if topic:
            query = f"{library_name} {topic} documentation OR tutorial OR example"
        else:
            query = f"{library_name} official documentation OR API reference OR getting started"

        return await self.search(query, count=count, freshness=Freshness.YEAR)

    async def _request_with_retry(
        self,
        endpoint: str,
        params: dict,
    ) -> dict:
        """Make request with exponential backoff retry.

        Args:
            endpoint: API endpoint (e.g., "/web/search")
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            Exception: If all retries fail
        """
        last_error = None
        delay = self.config.initial_retry_delay

        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._make_request(endpoint, params)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check if this is a retryable error
                is_rate_limit = "429" in str(e) or "rate" in error_str
                is_server_error = any(code in str(e) for code in ["500", "502", "503", "504"])
                is_timeout = "timeout" in error_str

                if not (is_rate_limit or is_server_error or is_timeout):
                    # Non-retryable error
                    logger.error(f"Brave API error (non-retryable): {e}")
                    raise

                if attempt < self.config.max_retries:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0.5, 1.5)
                    sleep_time = min(delay * jitter, self.config.max_retry_delay)

                    logger.warning(
                        f"Brave request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    self._retry_count += 1

                    await asyncio.sleep(sleep_time)
                    delay *= self.config.retry_multiplier
                else:
                    logger.error(
                        f"Brave request failed after {self.config.max_retries + 1} attempts: {e}"
                    )

        raise last_error or Exception("Request failed with no error details")

    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make a single API request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Parsed JSON response
        """
        start_time = time.time()
        self._request_count += 1

        url = f"{self.config.base_url}{endpoint}"

        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
        else:
            # Fallback to synchronous requests
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = (time.time() - start_time) * 1000
        self._total_latency_ms += latency_ms

        logger.debug(
            f"Brave API request: {endpoint} [{latency_ms:.0f}ms] "
            f"query={params.get('q', '')[:50]}..."
        )

        return data

    def _parse_web_response(self, query: str, data: dict) -> BraveSearchResponse:
        """Parse web search response.

        Args:
            query: Original query
            data: Raw API response

        Returns:
            BraveSearchResponse
        """
        results = []
        web_results = data.get("web", {}).get("results", [])

        for i, item in enumerate(web_results):
            # Calculate relevance score based on position
            # Higher rank = higher score (position 0 = 1.0, decreasing)
            relevance = 1.0 - (i / max(len(web_results), 1))

            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                source=ResultSource.WEB,
                date=item.get("age"),  # Brave returns "age" field
                relevance_score=relevance,
                language=item.get("language"),
                family_friendly=item.get("family_friendly", True),
                extra_snippets=item.get("extra_snippets", []),
                metadata={
                    "page_age": item.get("page_age"),
                    "profile": item.get("profile", {}),
                },
            ))

        return BraveSearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            latency_ms=0,  # Set by caller
            query_type="web",
            altered_query=data.get("query", {}).get("altered"),
        )

    def _parse_news_response(self, query: str, data: dict) -> BraveSearchResponse:
        """Parse news search response.

        Args:
            query: Original query
            data: Raw API response

        Returns:
            BraveSearchResponse with news results
        """
        results = []
        news_results = data.get("results", [])

        for i, item in enumerate(news_results):
            relevance = 1.0 - (i / max(len(news_results), 1))

            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                source=ResultSource.NEWS,
                date=item.get("age"),
                relevance_score=relevance,
                metadata={
                    "source_name": item.get("meta_url", {}).get("hostname"),
                    "thumbnail": item.get("thumbnail", {}).get("src"),
                },
            ))

        return BraveSearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            latency_ms=0,
            query_type="news",
        )

    # Synchronous wrappers
    def search_sync(
        self,
        query: str,
        **kwargs,
    ) -> BraveSearchResponse:
        """Synchronous wrapper for search().

        Args:
            query: Search query
            **kwargs: Additional arguments passed to search()

        Returns:
            BraveSearchResponse
        """
        return asyncio.run(self.search(query, **kwargs))

    def search_news_sync(
        self,
        query: str,
        **kwargs,
    ) -> BraveSearchResponse:
        """Synchronous wrapper for search_news()."""
        return asyncio.run(self.search_news(query, **kwargs))

    def search_technical_sync(
        self,
        query: str,
        **kwargs,
    ) -> BraveSearchResponse:
        """Synchronous wrapper for search_technical()."""
        return asyncio.run(self.search_technical(query, **kwargs))

    def search_documentation_sync(
        self,
        library_name: str,
        topic: Optional[str] = None,
        **kwargs,
    ) -> BraveSearchResponse:
        """Synchronous wrapper for search_documentation()."""
        return asyncio.run(self.search_documentation(library_name, topic, **kwargs))

    def get_stats(self) -> dict:
        """Get client statistics."""
        return {
            "total_requests": self._request_count,
            "total_retries": self._retry_count,
            "total_latency_ms": self._total_latency_ms,
            "avg_latency_ms": self._total_latency_ms / max(self._request_count, 1),
        }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self._request_count = 0
        self._retry_count = 0
        self._total_latency_ms = 0.0


# Test function
async def _test_brave() -> None:
    """Test Brave Search client."""
    client = BraveSearchClient()

    print("=== Web Search Test ===")
    response = await client.search("Python type hints tutorial", count=5)
    print(f"Query: {response.query}")
    print(f"Results: {response.result_count}")
    for r in response.results[:3]:
        print(f"  - {r.title[:60]}...")
        print(f"    URL: {r.url}")
        print(f"    Score: {r.relevance_score:.2f}")
    print()

    print("=== Fresh Results (past week) ===")
    response = await client.search("AI news", freshness=Freshness.WEEK, count=3)
    for r in response.results:
        print(f"  - {r.title[:60]}...")
        print(f"    Date: {r.date}")
    print()

    print("=== News Search Test ===")
    response = await client.search_news("machine learning", count=3)
    for r in response.results:
        print(f"  - {r.title[:60]}...")
        print(f"    Source: {r.metadata.get('source_name', 'unknown')}")
    print()

    print("=== Technical Search Test ===")
    response = await client.search_technical("LangGraph StateGraph", count=3)
    for r in response.results:
        print(f"  - {r.title[:60]}...")
        print(f"    Domain: {r.domain}")
    print()

    print("=== Stats ===")
    stats = client.get_stats()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Total retries: {stats['total_retries']}")
    print(f"Avg latency: {stats['avg_latency_ms']:.0f}ms")


def _cli() -> None:
    """CLI entry point for Brave Search client."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Brave Search API Client - Web and news search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Basic web search
  python -m skills_fabric.retrievals.brave_search_client -q "Python async patterns"

  # Search news from past week
  python -m skills_fabric.retrievals.brave_search_client -q "AI developments" --news --freshness pw

  # Search with freshness filter
  python -m skills_fabric.retrievals.brave_search_client -q "LangGraph" --freshness pm

  # Technical/documentation search
  python -m skills_fabric.retrievals.brave_search_client -q "FastAPI tutorial" --technical

  # Output as JSON
  python -m skills_fabric.retrievals.brave_search_client -q "REST API" --json

FRESHNESS OPTIONS:
  pd = past day (24 hours)
  pw = past week
  pm = past month
  py = past year

ENVIRONMENT:
  BRAVE_API_KEY: Required. Get from https://api.search.brave.com

NOTE:
  Maximum 20 results per query (API limit)
  Uses X-Subscription-Token header for authentication
"""
    )
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of results (max 20)")
    parser.add_argument("--news", action="store_true", help="Search news instead of web")
    parser.add_argument("--technical", action="store_true", help="Filter to technical sources")
    parser.add_argument("--freshness", choices=["pd", "pw", "pm", "py"],
                       help="Time filter: pd=day, pw=week, pm=month, py=year")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--test", action="store_true", help="Run test suite")

    args = parser.parse_args()

    if args.test:
        asyncio.run(_test_brave())
        return

    # Map freshness string to enum
    freshness_map = {
        "pd": Freshness.DAY,
        "pw": Freshness.WEEK,
        "pm": Freshness.MONTH,
        "py": Freshness.YEAR,
    }
    freshness = freshness_map.get(args.freshness) if args.freshness else None

    async def run() -> None:
        client = BraveSearchClient()

        if args.technical:
            response = await client.search_technical(args.query, count=args.count, freshness=freshness)
        elif args.news:
            response = await client.search_news(args.query, count=args.count, freshness=freshness)
        else:
            response = await client.search(args.query, count=args.count, freshness=freshness)

        if args.json:
            print(json.dumps(response.to_dict(), indent=2))
        else:
            print(f"Search: {response.query}")
            print(f"Results: {response.result_count}")
            print()
            for i, r in enumerate(response.results, 1):
                print(f"{i}. {r.title}")
                print(f"   URL: {r.url}")
                if r.date:
                    print(f"   Date: {r.date}")
                print(f"   {r.description[:100]}...")
                print(f"   Relevance: {r.relevance_score:.2f}")
                print()

    asyncio.run(run())


if __name__ == "__main__":
    _cli()
