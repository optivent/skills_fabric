"""
Brave Search API Client for MARO v2.0

Provides web and news search for grey literature discovery:
- Clinical guidelines
- Government reports
- News/preprints
- Conference proceedings

Uses Brave Search API (https://api.search.brave.com)
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class WebResult:
    """A web search result."""
    title: str
    url: str
    description: str
    source: str = "brave"
    date: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BraveSearchClient:
    """
    Brave Search API client for web and news search.

    Useful for finding grey literature not indexed in academic databases:
    - Clinical practice guidelines
    - Government health reports
    - News articles on recent findings
    - Conference proceedings
    - Preprint discussions

    Example:
        client = BraveSearchClient()
        results = await client.search("dry eye disease treatment guidelines 2024")
        for r in results:
            print(f"{r.title}: {r.url}")
    """

    BASE_URL = "https://api.search.brave.com/res/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Brave Search client.

        Args:
            api_key: Brave Search API key (or reads from BRAVE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Brave Search API key not found. "
                "Set BRAVE_API_KEY environment variable."
            )

        if not HTTPX_AVAILABLE:
            raise ImportError("httpx required for BraveSearchClient. Install: pip install httpx")

    async def search(
        self,
        query: str,
        count: int = 20,
        freshness: Optional[str] = None,
        safesearch: str = "moderate",
        text_decorations: bool = False
    ) -> List[WebResult]:
        """
        Search the web for grey literature.

        Args:
            query: Search query (e.g., "diabetes treatment guidelines 2024")
            count: Number of results (1-20, default 20)
            freshness: Time filter - "pd" (24h), "pw" (week), "pm" (month), "py" (year)
            safesearch: "off", "moderate", "strict"
            text_decorations: Include bold/italic markers in snippets

        Returns:
            List of WebResult objects
        """
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

        params = {
            "q": query,
            "count": min(count, 20),
            "safesearch": safesearch,
            "text_decorations": str(text_decorations).lower(),
        }

        if freshness:
            params["freshness"] = freshness

        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/web/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()

                # Parse web results
                web_results = data.get("web", {}).get("results", [])
                for i, item in enumerate(web_results):
                    results.append(WebResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        description=item.get("description", ""),
                        source="brave_web",
                        date=item.get("page_age"),
                        relevance_score=1.0 - (i / len(web_results)),  # Higher rank = higher score
                        metadata={
                            "language": item.get("language"),
                            "family_friendly": item.get("family_friendly"),
                            "extra_snippets": item.get("extra_snippets", []),
                        }
                    ))

                logger.info(f"Brave web search returned {len(results)} results for: {query[:50]}")

            except httpx.HTTPStatusError as e:
                logger.error(f"Brave API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Brave search error: {e}")
                raise

        return results

    async def search_news(
        self,
        query: str,
        count: int = 20,
        freshness: Optional[str] = "pm",  # Default to past month for news
    ) -> List[WebResult]:
        """
        Search news articles for recent research coverage.

        Args:
            query: Search query
            count: Number of results (1-20)
            freshness: Time filter - "pd" (24h), "pw" (week), "pm" (month)

        Returns:
            List of WebResult objects
        """
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

        params = {
            "q": query,
            "count": min(count, 20),
        }

        if freshness:
            params["freshness"] = freshness

        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/news/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()

                # Parse news results
                news_results = data.get("results", [])
                for i, item in enumerate(news_results):
                    results.append(WebResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        description=item.get("description", ""),
                        source="brave_news",
                        date=item.get("age"),
                        relevance_score=1.0 - (i / max(len(news_results), 1)),
                        metadata={
                            "source_name": item.get("meta_url", {}).get("hostname"),
                            "thumbnail": item.get("thumbnail", {}).get("src"),
                        }
                    ))

                logger.info(f"Brave news search returned {len(results)} results for: {query[:50]}")

            except httpx.HTTPStatusError as e:
                logger.error(f"Brave News API error: {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Brave news search error: {e}")
                raise

        return results

    async def search_academic(
        self,
        query: str,
        count: int = 20,
    ) -> List[WebResult]:
        """
        Search for academic/medical content via web search with academic filters.

        Adds site filters for known academic sources:
        - PubMed, NIH, WHO, CDC, FDA
        - Medical journals
        - University sites

        Args:
            query: Search query
            count: Number of results

        Returns:
            List of WebResult objects from academic sources
        """
        # Enhance query with academic site filters
        academic_sites = [
            "site:pubmed.ncbi.nlm.nih.gov",
            "site:nih.gov",
            "site:who.int",
            "site:cdc.gov",
            "site:fda.gov",
            "site:cochrane.org",
            "site:nature.com",
            "site:sciencedirect.com",
            "site:jamanetwork.com",
            "site:bmj.com",
            "site:thelancet.com",
        ]

        # Build OR query for academic sites
        site_filter = " OR ".join(academic_sites)
        enhanced_query = f"({query}) ({site_filter})"

        return await self.search(enhanced_query, count=count)

    async def search_guidelines(
        self,
        topic: str,
        country: Optional[str] = None,
        count: int = 10,
    ) -> List[WebResult]:
        """
        Search specifically for clinical practice guidelines.

        Args:
            topic: Medical topic (e.g., "dry eye disease", "diabetic retinopathy")
            country: Optional country filter (e.g., "USA", "UK", "EU")
            count: Number of results

        Returns:
            List of WebResult objects for guidelines
        """
        # Build guideline-specific query
        query_parts = [
            topic,
            "clinical practice guideline OR treatment guideline OR management guideline",
        ]

        if country:
            country_orgs = {
                "USA": "AAO OR AAFP OR ADA OR site:aao.org OR site:guidelines.gov",
                "UK": "NICE OR NHS OR site:nice.org.uk",
                "EU": "EMA OR ESCRS OR site:ema.europa.eu",
            }
            if country.upper() in country_orgs:
                query_parts.append(country_orgs[country.upper()])

        query = " ".join(query_parts)
        return await self.search(query, count=count, freshness="py")  # Past year

    def search_sync(self, query: str, **kwargs) -> List[WebResult]:
        """Synchronous wrapper for search()."""
        return asyncio.run(self.search(query, **kwargs))

    def search_news_sync(self, query: str, **kwargs) -> List[WebResult]:
        """Synchronous wrapper for search_news()."""
        return asyncio.run(self.search_news(query, **kwargs))


# Test function
async def _test_brave():
    """Test Brave Search client."""
    client = BraveSearchClient()

    print("=== Web Search Test ===")
    results = await client.search("dry eye disease treatment 2024", count=5)
    for r in results:
        print(f"- {r.title[:60]}...")
        print(f"  URL: {r.url}")
        print()

    print("=== News Search Test ===")
    results = await client.search_news("ophthalmology research", count=3)
    for r in results:
        print(f"- {r.title[:60]}...")
        print(f"  Date: {r.date}")
        print()


def _cli():
    """CLI entry point for Brave Search."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Brave Search CLI - Search web and news for grey literature",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Basic web search
  python -m discovery.brave_client -q "dry eye disease treatment guidelines"

  # Search news from past week
  python -m discovery.brave_client -q "ophthalmology research" --news --freshness pw

  # Search clinical guidelines (USA)
  python -m discovery.brave_client -q "diabetic retinopathy" --guidelines

  # Filter to academic sources only
  python -m discovery.brave_client -q "VEGF inhibitors" --academic -n 20

  # Output as JSON for piping
  python -m discovery.brave_client -q "dry eye" --json | jq '.[] | .title'

FRESHNESS OPTIONS:
  pd = past day (24 hours)
  pw = past week
  pm = past month
  py = past year

ENVIRONMENT:
  BRAVE_API_KEY: Required. Get from https://api.search.brave.com

USE CASES:
  - Finding clinical practice guidelines not in PubMed
  - Discovering grey literature (government reports, WHO guidelines)
  - Monitoring recent news about medical research
  - Finding conference proceedings and preprints
"""
    )
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of results (max 20)")
    parser.add_argument("--news", action="store_true", help="Search news instead of web")
    parser.add_argument("--guidelines", action="store_true", help="Search for clinical guidelines")
    parser.add_argument("--academic", action="store_true", help="Filter to academic sources")
    parser.add_argument("--freshness", choices=["pd", "pw", "pm", "py"], help="Time filter: pd=day, pw=week, pm=month, py=year")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--test", action="store_true", help="Run test suite")

    args = parser.parse_args()

    if args.test:
        asyncio.run(_test_brave())
        return

    async def run():
        client = BraveSearchClient()

        if args.guidelines:
            results = await client.search_guidelines(args.query, count=args.count)
        elif args.academic:
            results = await client.search_academic(args.query, count=args.count)
        elif args.news:
            results = await client.search_news(args.query, count=args.count, freshness=args.freshness)
        else:
            results = await client.search(args.query, count=args.count, freshness=args.freshness)

        if args.json:
            output = [{"title": r.title, "url": r.url, "description": r.description, "date": r.date} for r in results]
            print(json.dumps(output, indent=2))
        else:
            for i, r in enumerate(results, 1):
                print(f"{i}. {r.title}")
                print(f"   URL: {r.url}")
                if r.date:
                    print(f"   Date: {r.date}")
                print(f"   {r.description[:100]}...")
                print()

    asyncio.run(run())


if __name__ == "__main__":
    _cli()
