#!/usr/bin/env python3
"""
Brightdata Web Unlocker Client

Features:
- Server-side JavaScript rendering
- Anti-bot bypass
- Works in sandboxed environments (HTTP API)
- Perfect for CodeWiki and SPA scraping

API: https://brightdata.com/products/web-unlocker
"""

import os
import asyncio
import base64
import httpx
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


@dataclass
class BrightdataConfig:
    """Configuration for Brightdata API."""
    username: str
    password: str
    zone: str = "web_unlocker"
    host: str = "brd.superproxy.io"
    port: int = 22225

    @classmethod
    def from_env(cls) -> "BrightdataConfig":
        """Load from environment variables."""
        # Brightdata credentials format: username:password or full API key
        api_key = os.getenv("BRIGHTDATA_API_KEY", "")
        if not api_key:
            raise ValueError("BRIGHTDATA_API_KEY not set")

        if ":" in api_key:
            username, password = api_key.split(":", 1)
        else:
            username = api_key
            password = ""

        return cls(username=username, password=password)

    @property
    def proxy_url(self) -> str:
        """Get proxy URL for direct use."""
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"


@dataclass
class ScrapedPage:
    """A scraped web page."""
    url: str
    html: str
    status_code: int
    headers: Dict[str, str]
    final_url: str = ""


class BrightdataClient:
    """
    Brightdata Web Unlocker client.

    Usage:
        client = BrightdataClient()

        # Scrape a page with JS rendering
        page = await client.scrape("https://example.com/spa-page")

        # Scrape CodeWiki
        codewiki = await client.scrape_codewiki("langchain")

        # Extract text content
        text = await client.scrape_text("https://docs.example.com/api")
    """

    def __init__(self, config: Optional[BrightdataConfig] = None):
        self.config = config or BrightdataConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with proxy."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                proxy=self.config.proxy_url,
                timeout=60.0,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def scrape(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        render_js: bool = True,
    ) -> ScrapedPage:
        """
        Scrape a web page.

        Args:
            url: URL to scrape
            headers: Additional headers
            render_js: Enable JavaScript rendering

        Returns:
            ScrapedPage with HTML content
        """
        client = await self._get_client()

        request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            **(headers or {})
        }

        if render_js:
            # Add Brightdata JS rendering header
            request_headers["x-render-js"] = "true"

        try:
            response = await client.get(url, headers=request_headers)

            return ScrapedPage(
                url=url,
                html=response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
                final_url=str(response.url),
            )
        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
            raise

    async def scrape_text(
        self,
        url: str,
        render_js: bool = True,
    ) -> str:
        """
        Scrape and extract text content.

        Uses basic HTML to text conversion.

        Args:
            url: URL to scrape
            render_js: Enable JavaScript rendering

        Returns:
            Extracted text content
        """
        page = await self.scrape(url, render_js=render_js)

        # Basic HTML to text conversion
        import re

        text = page.html
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    async def scrape_codewiki(
        self,
        library: str,
    ) -> str:
        """
        Scrape CodeWiki documentation for a library.

        Args:
            library: Library name (e.g., "langchain", "langgraph")

        Returns:
            CodeWiki markdown content
        """
        url = f"https://codewiki.ai/{library}"

        page = await self.scrape(url, render_js=True)

        # Extract main content
        # CodeWiki uses specific content containers
        import re

        # Look for main content area
        content_match = re.search(
            r'<main[^>]*>(.*?)</main>',
            page.html,
            re.DOTALL
        )

        if content_match:
            html = content_match.group(1)
        else:
            html = page.html

        # Convert to markdown-like text
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

        # Convert common HTML to markdown
        text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', text)
        text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', text)
        text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', text)
        text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text)
        text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text)
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text)
        text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```\n', text, flags=re.DOTALL)
        text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text)

        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Clean whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        return text


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_client: Optional[BrightdataClient] = None


def get_client() -> BrightdataClient:
    """Get the default Brightdata client."""
    global _default_client
    if _default_client is None:
        _default_client = BrightdataClient()
    return _default_client


async def scrape(url: str, **kwargs) -> ScrapedPage:
    """Scrape a URL."""
    return await get_client().scrape(url, **kwargs)


async def scrape_text(url: str, **kwargs) -> str:
    """Scrape and extract text."""
    return await get_client().scrape_text(url, **kwargs)


async def scrape_codewiki(library: str) -> str:
    """Scrape CodeWiki documentation."""
    return await get_client().scrape_codewiki(library)


# =============================================================================
# CLI DEMO
# =============================================================================

async def demo():
    """Demonstrate Brightdata client capabilities."""
    print("=" * 70)
    print("Brightdata Web Unlocker Client Demo")
    print("=" * 70)

    try:
        client = BrightdataClient()

        # Scrape a simple page
        print("\n1. Scrape Simple Page")
        print("-" * 40)
        page = await client.scrape("https://example.com")
        print(f"  URL: {page.url}")
        print(f"  Status: {page.status_code}")
        print(f"  HTML length: {len(page.html)} chars")

        # Extract text
        print("\n2. Extract Text Content")
        print("-" * 40)
        text = await client.scrape_text("https://example.com")
        print(f"  Text preview: {text[:200]}...")

        await client.close()

    except ValueError as e:
        print(f"\nError: {e}")
        print("Set BRIGHTDATA_API_KEY environment variable to use this client.")

    print("\n" + "=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
