"""Brave Search API Client for Skills Fabric.

Provides web and news search for documentation and code discovery.
Based on the older_project pattern (older_project/andreea_tools/discovery/brave_client.py).

Features:
- Web search with freshness filters (pd, pw, pm, py)
- News search endpoint
- Academic/technical source filtering
- Rate limiting with exponential backoff
- Enhanced relevance scoring (query matching, domain authority, freshness)
- Full metadata extraction (snippets, dates, source info)
- Academic and guideline search filtering
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

    # Academic sources (arxiv, papers, research)
    results = await client.search_academic("transformer architecture")

    # Clinical guidelines (medical)
    results = await client.search_guidelines("diabetes treatment", country="USA")

    # Enhanced relevance scoring
    scorer = RelevanceScorer()
    score = scorer.calculate_relevance(
        result=result,
        query="LangGraph tutorial",
        position=0,
        total_results=10
    )

    # Synchronous interface
    results = client.search_sync("Python dataclasses")

API Reference: https://api.search.brave.com/app/documentation
"""
from __future__ import annotations

import os
import asyncio
import random
import re
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from enum import Enum
from urllib.parse import urlparse

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
    GUIDELINE = "brave_guideline"


class ContentType(Enum):
    """Detected content type for search results."""
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    API_REFERENCE = "api_reference"
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    ACADEMIC_PAPER = "academic_paper"
    GUIDELINE = "guideline"
    FORUM_POST = "forum_post"
    VIDEO = "video"
    REPOSITORY = "repository"
    UNKNOWN = "unknown"


@dataclass
class DomainAuthority:
    """Domain authority and trust scoring.

    Provides trust scores for known domains used in relevance calculation.
    """
    domain: str
    category: str  # "technical", "academic", "official", "news", "general"
    trust_score: float  # 0.0-1.0
    is_primary_source: bool = False  # Official docs, original sources

    # Known high-authority domains for technical content
    AUTHORITY_SCORES: dict[str, tuple[str, float, bool]] = {
        # Official documentation (highest trust)
        "docs.python.org": ("official", 0.98, True),
        "langchain.com": ("official", 0.95, True),
        "python.langchain.com": ("official", 0.95, True),
        "api.python.langchain.com": ("official", 0.96, True),
        "docs.anthropic.com": ("official", 0.98, True),
        "openai.com": ("official", 0.95, True),
        "react.dev": ("official", 0.97, True),
        "fastapi.tiangolo.com": ("official", 0.95, True),
        "pydantic.dev": ("official", 0.95, True),
        "pydantic-docs.helpmanual.io": ("official", 0.94, True),

        # Code repositories (very high trust for code)
        "github.com": ("technical", 0.92, True),
        "gitlab.com": ("technical", 0.88, True),
        "bitbucket.org": ("technical", 0.85, False),

        # Academic sources (high trust)
        "arxiv.org": ("academic", 0.94, True),
        "scholar.google.com": ("academic", 0.85, False),
        "pubmed.ncbi.nlm.nih.gov": ("academic", 0.96, True),
        "nih.gov": ("academic", 0.95, True),
        "nature.com": ("academic", 0.93, True),
        "sciencedirect.com": ("academic", 0.90, False),
        "ieee.org": ("academic", 0.92, True),
        "acm.org": ("academic", 0.91, True),

        # Technical community (medium-high trust)
        "stackoverflow.com": ("technical", 0.82, False),
        "readthedocs.io": ("technical", 0.88, True),
        "readthedocs.org": ("technical", 0.88, True),
        "dev.to": ("technical", 0.70, False),
        "realpython.com": ("technical", 0.82, False),
        "python.org": ("official", 0.96, True),
        "pypi.org": ("official", 0.90, True),

        # Guideline sources (medical)
        "who.int": ("official", 0.97, True),
        "cdc.gov": ("official", 0.96, True),
        "fda.gov": ("official", 0.95, True),
        "nice.org.uk": ("official", 0.94, True),
        "aao.org": ("official", 0.93, True),
        "cochrane.org": ("academic", 0.94, True),

        # General tech media (medium trust)
        "medium.com": ("general", 0.55, False),
        "towardsdatascience.com": ("technical", 0.68, False),
        "hackernews.com": ("general", 0.60, False),
        "reddit.com": ("general", 0.45, False),

        # News sources
        "techcrunch.com": ("news", 0.72, False),
        "wired.com": ("news", 0.70, False),
        "arstechnica.com": ("news", 0.75, False),
        "theverge.com": ("news", 0.65, False),
    }

    @classmethod
    def from_url(cls, url: str) -> "DomainAuthority":
        """Create DomainAuthority from a URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            # Check exact match first
            if domain in cls.AUTHORITY_SCORES:
                category, score, is_primary = cls.AUTHORITY_SCORES[domain]
                return cls(domain, category, score, is_primary)

            # Check subdomain matches (e.g., docs.python.org)
            for known_domain, (category, score, is_primary) in cls.AUTHORITY_SCORES.items():
                if domain.endswith("." + known_domain) or domain == known_domain:
                    return cls(domain, category, score, is_primary)

            # Check if it's a known pattern
            if ".gov" in domain:
                return cls(domain, "official", 0.80, True)
            elif ".edu" in domain:
                return cls(domain, "academic", 0.75, False)
            elif ".org" in domain:
                return cls(domain, "general", 0.55, False)
            elif "docs." in domain or "api." in domain or "documentation" in domain:
                return cls(domain, "technical", 0.70, True)

            # Unknown domain
            return cls(domain, "general", 0.40, False)
        except Exception:
            return cls("unknown", "general", 0.30, False)


class RelevanceScorer:
    """Calculate relevance scores for search results.

    Uses multiple signals:
    - Position-based scoring (rank in results)
    - Query term matching (title, description overlap)
    - Domain authority scoring
    - Freshness scoring (recency of content)
    - Content type matching

    Example:
        scorer = RelevanceScorer()
        score = scorer.calculate_relevance(
            result=result,
            query="LangGraph StateGraph tutorial",
            position=0,
            total_results=10
        )
    """

    # Weights for different scoring components
    POSITION_WEIGHT = 0.25
    QUERY_MATCH_WEIGHT = 0.35
    DOMAIN_AUTHORITY_WEIGHT = 0.25
    FRESHNESS_WEIGHT = 0.15

    def __init__(
        self,
        position_weight: float = POSITION_WEIGHT,
        query_match_weight: float = QUERY_MATCH_WEIGHT,
        domain_authority_weight: float = DOMAIN_AUTHORITY_WEIGHT,
        freshness_weight: float = FRESHNESS_WEIGHT,
    ):
        """Initialize the relevance scorer.

        Args:
            position_weight: Weight for position-based score (0-1)
            query_match_weight: Weight for query term matching (0-1)
            domain_authority_weight: Weight for domain trust score (0-1)
            freshness_weight: Weight for content freshness (0-1)
        """
        self.position_weight = position_weight
        self.query_match_weight = query_match_weight
        self.domain_authority_weight = domain_authority_weight
        self.freshness_weight = freshness_weight

        # Normalize weights to sum to 1.0
        total = self.position_weight + self.query_match_weight + self.domain_authority_weight + self.freshness_weight
        if total > 0:
            self.position_weight /= total
            self.query_match_weight /= total
            self.domain_authority_weight /= total
            self.freshness_weight /= total

    def calculate_relevance(
        self,
        result: "SearchResult",
        query: str,
        position: int,
        total_results: int,
    ) -> float:
        """Calculate combined relevance score for a search result.

        Args:
            result: The search result to score
            query: Original search query
            position: Position in search results (0-indexed)
            total_results: Total number of results

        Returns:
            Relevance score between 0.0 and 1.0
        """
        # Position score: Higher rank = higher score
        position_score = self._calculate_position_score(position, total_results)

        # Query match score: How well title/description match query terms
        query_match_score = self._calculate_query_match_score(result, query)

        # Domain authority score
        domain_auth = DomainAuthority.from_url(result.url)
        domain_score = domain_auth.trust_score

        # Freshness score (if date available)
        freshness_score = self._calculate_freshness_score(result.date, result.metadata.get("page_age"))

        # Combine with weights
        combined_score = (
            self.position_weight * position_score +
            self.query_match_weight * query_match_score +
            self.domain_authority_weight * domain_score +
            self.freshness_weight * freshness_score
        )

        return min(1.0, max(0.0, combined_score))

    def _calculate_position_score(self, position: int, total_results: int) -> float:
        """Calculate score based on result position.

        Uses exponential decay: earlier results score much higher.
        """
        if total_results <= 0:
            return 0.5

        # Exponential decay based on position
        # Position 0 = 1.0, position n = e^(-0.2*n)
        import math
        return math.exp(-0.2 * position)

    def _calculate_query_match_score(self, result: "SearchResult", query: str) -> float:
        """Calculate score based on query term matching.

        Checks how many query terms appear in title and description.
        """
        # Tokenize query into significant words (skip common words)
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or", "with", "how", "what", "when", "where", "why"}
        query_terms = set(
            word.lower() for word in re.findall(r'\b\w+\b', query.lower())
            if word.lower() not in stopwords and len(word) > 2
        )

        if not query_terms:
            return 0.5  # Neutral score if no significant terms

        # Check title and description
        title_lower = result.title.lower()
        desc_lower = result.description.lower()
        combined_text = f"{title_lower} {desc_lower}"

        # Count matches with position weighting (title matches worth more)
        title_matches = sum(1 for term in query_terms if term in title_lower)
        desc_matches = sum(1 for term in query_terms if term in desc_lower and term not in title_lower)

        # Title matches weighted 2x
        weighted_matches = (title_matches * 2) + desc_matches
        max_possible = len(query_terms) * 2  # If all terms in title

        return min(1.0, weighted_matches / max_possible) if max_possible > 0 else 0.5

    def _calculate_freshness_score(self, date_str: Optional[str], page_age: Optional[str] = None) -> float:
        """Calculate score based on content freshness.

        More recent content scores higher.
        """
        # Default to neutral if no date info
        if not date_str and not page_age:
            return 0.5

        # Try to parse age strings like "2 days ago", "1 week ago", etc.
        age_text = page_age or date_str or ""
        age_lower = age_text.lower()

        # Map age to freshness score
        if any(x in age_lower for x in ["hour", "minute", "just now"]):
            return 1.0  # Very fresh
        elif "day" in age_lower:
            # Extract number of days if possible
            match = re.search(r'(\d+)\s*day', age_lower)
            days = int(match.group(1)) if match else 1
            return max(0.6, 1.0 - (days * 0.05))  # Decay over days
        elif "week" in age_lower:
            match = re.search(r'(\d+)\s*week', age_lower)
            weeks = int(match.group(1)) if match else 1
            return max(0.4, 0.8 - (weeks * 0.1))
        elif "month" in age_lower:
            match = re.search(r'(\d+)\s*month', age_lower)
            months = int(match.group(1)) if match else 1
            return max(0.2, 0.6 - (months * 0.05))
        elif "year" in age_lower:
            match = re.search(r'(\d+)\s*year', age_lower)
            years = int(match.group(1)) if match else 1
            return max(0.1, 0.4 - (years * 0.1))

        return 0.5  # Default neutral

    def detect_content_type(self, result: "SearchResult") -> ContentType:
        """Detect the type of content from URL and title patterns.

        Args:
            result: Search result to analyze

        Returns:
            Detected ContentType enum value
        """
        url_lower = result.url.lower()
        title_lower = result.title.lower()
        desc_lower = result.description.lower()
        combined = f"{url_lower} {title_lower} {desc_lower}"

        # Check URL patterns first
        if "github.com" in url_lower or "gitlab.com" in url_lower:
            return ContentType.REPOSITORY
        elif "youtube.com" in url_lower or "vimeo.com" in url_lower:
            return ContentType.VIDEO
        elif "stackoverflow.com" in url_lower or "stackexchange.com" in url_lower:
            return ContentType.FORUM_POST
        elif "arxiv.org" in url_lower or "papers" in url_lower or "pubmed" in url_lower:
            return ContentType.ACADEMIC_PAPER

        # Check content patterns
        if any(x in combined for x in ["guideline", "clinical practice", "treatment protocol", "recommendation"]):
            return ContentType.GUIDELINE
        elif any(x in combined for x in ["tutorial", "how to", "getting started", "step by step", "learn"]):
            return ContentType.TUTORIAL
        elif any(x in combined for x in ["api reference", "api documentation", "method reference", "class reference"]):
            return ContentType.API_REFERENCE
        elif any(x in combined for x in ["documentation", "docs.", "/docs/", "official guide"]):
            return ContentType.DOCUMENTATION
        elif result.source == ResultSource.NEWS or any(x in combined for x in ["news", "announced", "released", "launches"]):
            return ContentType.NEWS_ARTICLE
        elif any(x in url_lower for x in ["blog", "medium.com", "dev.to", "hashnode"]):
            return ContentType.BLOG_POST

        return ContentType.UNKNOWN


@dataclass
class SearchResult:
    """A search result from Brave Search API.

    Contains the result metadata plus enhanced relevance scoring.

    Attributes:
        title: Result title
        url: Full URL of the result
        description: Snippet/description text
        source: Source type (web, news, academic, etc.)
        date: Age of the result (e.g., "2 days ago")
        relevance_score: Combined relevance score 0.0-1.0
        language: Content language code
        family_friendly: SafeSearch flag
        extra_snippets: Additional text snippets from page
        metadata: Additional metadata from API
        content_type: Detected content type (tutorial, docs, etc.)
        domain_authority: Domain trust score info
        position_score: Score from search position
        query_match_score: Score from query term matching
        freshness_score: Score from content freshness
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
    # Enhanced fields
    content_type: ContentType = ContentType.UNKNOWN
    domain_authority: Optional[DomainAuthority] = None
    position_score: float = 0.0
    query_match_score: float = 0.0
    freshness_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert result to dictionary with full metadata."""
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
            "domain": self.domain,
            "content_type": self.content_type.value,
            "domain_authority": {
                "domain": self.domain_authority.domain,
                "category": self.domain_authority.category,
                "trust_score": self.domain_authority.trust_score,
                "is_primary_source": self.domain_authority.is_primary_source,
            } if self.domain_authority else None,
            "score_breakdown": {
                "position": self.position_score,
                "query_match": self.query_match_score,
                "freshness": self.freshness_score,
                "domain_authority": self.domain_authority.trust_score if self.domain_authority else 0.0,
            },
        }

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(self.url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    @property
    def is_primary_source(self) -> bool:
        """Check if this is a primary/official source."""
        return self.domain_authority.is_primary_source if self.domain_authority else False

    @property
    def trust_score(self) -> float:
        """Get the domain trust score."""
        return self.domain_authority.trust_score if self.domain_authority else 0.0

    @property
    def all_snippets(self) -> list[str]:
        """Get all text snippets including description."""
        snippets = [self.description] if self.description else []
        snippets.extend(self.extra_snippets)
        return snippets

    @property
    def snippet_text(self) -> str:
        """Get all snippets as a single text."""
        return " ".join(self.all_snippets)

    def matches_content_type(self, content_type: ContentType) -> bool:
        """Check if this result matches the specified content type."""
        return self.content_type == content_type

    def is_high_quality(self, min_relevance: float = 0.6) -> bool:
        """Check if this is a high-quality result based on relevance and trust."""
        return self.relevance_score >= min_relevance and self.trust_score >= 0.5


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

    async def search_academic(
        self,
        query: str,
        count: int = 20,
        freshness: Optional[Freshness] = None,
    ) -> BraveSearchResponse:
        """Search for academic/research content via web search with academic filters.

        Filters results to known academic and research sources:
        - ArXiv, Nature, IEEE, ACM
        - PubMed, NIH, Scholar
        - University sites (.edu)
        - Research papers and preprints

        Args:
            query: Search query
            count: Number of results (max 20)
            freshness: Optional time filter

        Returns:
            BraveSearchResponse with academic results
        """
        # Academic site filters for research content
        academic_sites = [
            "site:arxiv.org",
            "site:pubmed.ncbi.nlm.nih.gov",
            "site:nih.gov",
            "site:nature.com",
            "site:sciencedirect.com",
            "site:ieee.org",
            "site:acm.org",
            "site:springer.com",
            "site:scholar.google.com",
            "site:researchgate.net",
            "site:semanticscholar.org",
        ]

        # Build OR query for academic sites
        site_filter = " OR ".join(academic_sites)
        enhanced_query = f"({query}) ({site_filter})"

        response = await self.search(
            enhanced_query,
            count=count,
            freshness=freshness,
        )

        # Update source and content type for academic results
        for result in response.results:
            result.source = ResultSource.ACADEMIC
            if result.content_type == ContentType.UNKNOWN:
                result.content_type = ContentType.ACADEMIC_PAPER

        return response

    async def search_guidelines(
        self,
        topic: str,
        domain: str = "software",
        country: Optional[str] = None,
        count: int = 10,
        freshness: Optional[Freshness] = Freshness.YEAR,
    ) -> BraveSearchResponse:
        """Search for guidelines, best practices, and standards.

        Supports multiple domains:
        - software: API design, coding standards, architectural patterns
        - medical: Clinical practice guidelines, treatment protocols
        - security: Security best practices, compliance standards
        - devops: CI/CD, infrastructure, deployment patterns
        - data_science: ML/AI best practices, data engineering patterns

        Args:
            topic: Topic area (e.g., "REST API design", "diabetes treatment")
            domain: Domain type - "software", "medical", "security", "devops", "data_science"
            country: Optional country filter for medical domain (e.g., "USA", "UK", "EU")
            count: Number of results
            freshness: Time filter (defaults to past year)

        Returns:
            BraveSearchResponse with guideline results
        """
        # Domain-specific guideline query patterns
        domain_patterns = {
            "software": {
                "query_suffix": "best practice OR style guide OR design guideline OR coding standard OR architectural pattern",
                "sites": [
                    "site:google.github.io/styleguide",
                    "site:docs.microsoft.com",
                    "site:developer.mozilla.org",
                    "site:martin.fowler.com",
                    "site:refactoring.guru",
                    "site:12factor.net",
                ],
            },
            "medical": {
                "query_suffix": "clinical practice guideline OR treatment guideline OR management guideline OR standard of care",
                "sites": [
                    "site:cdc.gov",
                    "site:nih.gov",
                    "site:who.int",
                    "site:nice.org.uk",
                    "site:cochrane.org",
                ],
            },
            "security": {
                "query_suffix": "security best practice OR security guideline OR compliance standard OR security framework",
                "sites": [
                    "site:owasp.org",
                    "site:nist.gov",
                    "site:cisecurity.org",
                    "site:sans.org",
                    "site:cisa.gov",
                ],
            },
            "devops": {
                "query_suffix": "best practice OR pattern OR guideline OR infrastructure as code",
                "sites": [
                    "site:kubernetes.io",
                    "site:docker.com",
                    "site:terraform.io",
                    "site:aws.amazon.com/architecture",
                    "site:cloud.google.com/architecture",
                ],
            },
            "data_science": {
                "query_suffix": "best practice OR guideline OR pattern OR MLOps",
                "sites": [
                    "site:scikit-learn.org",
                    "site:tensorflow.org",
                    "site:pytorch.org",
                    "site:ml-ops.org",
                    "site:papers.nips.cc",
                ],
            },
        }

        # Get domain pattern or default to software
        domain_lower = domain.lower() if domain else "software"
        pattern = domain_patterns.get(domain_lower, domain_patterns["software"])

        # Build query
        query_parts = [topic, pattern["query_suffix"]]

        # Add site filters
        if pattern["sites"]:
            site_filter = " OR ".join(pattern["sites"])
            query_parts.append(f"({site_filter})")

        # Add country-specific filters for medical domain
        if domain_lower == "medical" and country:
            country_orgs = {
                "USA": "AAO OR AAFP OR ADA OR AMA OR site:aao.org OR site:guidelines.gov OR site:cdc.gov OR site:fda.gov",
                "UK": "NICE OR NHS OR site:nice.org.uk OR site:nhs.uk",
                "EU": "EMA OR ESCRS OR site:ema.europa.eu",
                "WHO": "site:who.int OR World Health Organization",
            }
            if country.upper() in country_orgs:
                query_parts.append(country_orgs[country.upper()])

        query = " ".join(query_parts)

        response = await self.search(query, count=count, freshness=freshness)

        # Update source and content type for guideline results
        for result in response.results:
            result.source = ResultSource.GUIDELINE
            if result.content_type == ContentType.UNKNOWN:
                result.content_type = ContentType.GUIDELINE

        return response

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

    def _parse_web_response(
        self,
        query: str,
        data: dict,
        use_enhanced_scoring: bool = True,
    ) -> BraveSearchResponse:
        """Parse web search response with enhanced metadata extraction.

        Args:
            query: Original query
            data: Raw API response
            use_enhanced_scoring: Whether to use multi-signal relevance scoring

        Returns:
            BraveSearchResponse with parsed results
        """
        results = []
        web_results = data.get("web", {}).get("results", [])
        total_results = len(web_results)

        scorer = RelevanceScorer() if use_enhanced_scoring else None

        for i, item in enumerate(web_results):
            # Extract all available metadata
            url = item.get("url", "")
            title = item.get("title", "")
            description = item.get("description", "")
            extra_snippets = item.get("extra_snippets", [])
            page_age = item.get("page_age")
            age = item.get("age")

            # Get domain authority info
            domain_auth = DomainAuthority.from_url(url)

            # Create preliminary result for scoring
            result = SearchResult(
                title=title,
                url=url,
                description=description,
                source=ResultSource.WEB,
                date=age,
                language=item.get("language"),
                family_friendly=item.get("family_friendly", True),
                extra_snippets=extra_snippets,
                metadata={
                    "page_age": page_age,
                    "profile": item.get("profile", {}),
                    "page_fetched": item.get("page_fetched"),
                    "deep_results": item.get("deep_results", {}),
                    "thumbnail": item.get("thumbnail", {}).get("src"),
                },
                domain_authority=domain_auth,
            )

            # Calculate relevance scores
            if scorer:
                # Calculate individual score components
                import math
                position_score = math.exp(-0.2 * i)
                query_match_score = scorer._calculate_query_match_score(result, query)
                freshness_score = scorer._calculate_freshness_score(age, page_age)

                # Calculate combined score
                relevance = scorer.calculate_relevance(result, query, i, total_results)

                # Detect content type
                content_type = scorer.detect_content_type(result)

                # Update result with scores
                result.relevance_score = relevance
                result.position_score = position_score
                result.query_match_score = query_match_score
                result.freshness_score = freshness_score
                result.content_type = content_type
            else:
                # Simple position-based scoring fallback
                result.relevance_score = 1.0 - (i / max(total_results, 1))

            results.append(result)

        return BraveSearchResponse(
            query=query,
            results=results,
            total_results=total_results,
            latency_ms=0,  # Set by caller
            query_type="web",
            altered_query=data.get("query", {}).get("altered"),
        )

    def _parse_news_response(
        self,
        query: str,
        data: dict,
        use_enhanced_scoring: bool = True,
    ) -> BraveSearchResponse:
        """Parse news search response with enhanced metadata extraction.

        Args:
            query: Original query
            data: Raw API response
            use_enhanced_scoring: Whether to use multi-signal relevance scoring

        Returns:
            BraveSearchResponse with news results
        """
        results = []
        news_results = data.get("results", [])
        total_results = len(news_results)

        scorer = RelevanceScorer() if use_enhanced_scoring else None

        for i, item in enumerate(news_results):
            # Extract all available metadata
            url = item.get("url", "")
            title = item.get("title", "")
            description = item.get("description", "")
            age = item.get("age")
            meta_url = item.get("meta_url", {})
            thumbnail = item.get("thumbnail", {})

            # Get domain authority info
            domain_auth = DomainAuthority.from_url(url)

            # Create preliminary result for scoring
            result = SearchResult(
                title=title,
                url=url,
                description=description,
                source=ResultSource.NEWS,
                date=age,
                metadata={
                    "source_name": meta_url.get("hostname"),
                    "source_url": meta_url.get("scheme", "https") + "://" + meta_url.get("hostname", "") if meta_url.get("hostname") else None,
                    "thumbnail": thumbnail.get("src"),
                    "thumbnail_height": thumbnail.get("height"),
                    "thumbnail_width": thumbnail.get("width"),
                    "page_age": item.get("page_age"),
                },
                domain_authority=domain_auth,
                content_type=ContentType.NEWS_ARTICLE,
            )

            # Calculate relevance scores
            if scorer:
                import math
                position_score = math.exp(-0.2 * i)
                query_match_score = scorer._calculate_query_match_score(result, query)
                freshness_score = scorer._calculate_freshness_score(age, item.get("page_age"))

                # For news, freshness is weighted higher
                relevance = scorer.calculate_relevance(result, query, i, total_results)

                # Update result with scores
                result.relevance_score = relevance
                result.position_score = position_score
                result.query_match_score = query_match_score
                result.freshness_score = freshness_score
            else:
                result.relevance_score = 1.0 - (i / max(total_results, 1))

            results.append(result)

        return BraveSearchResponse(
            query=query,
            results=results,
            total_results=total_results,
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

    def search_academic_sync(
        self,
        query: str,
        **kwargs,
    ) -> BraveSearchResponse:
        """Synchronous wrapper for search_academic()."""
        return asyncio.run(self.search_academic(query, **kwargs))

    def search_guidelines_sync(
        self,
        topic: str,
        domain: str = "software",
        country: Optional[str] = None,
        **kwargs,
    ) -> BraveSearchResponse:
        """Synchronous wrapper for search_guidelines()."""
        return asyncio.run(self.search_guidelines(topic, domain=domain, country=country, **kwargs))

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

  # Academic/scholarly search
  python -m skills_fabric.retrievals.brave_search_client -q "transformer architecture" --academic

  # Guidelines search (software or medical domain)
  python -m skills_fabric.retrievals.brave_search_client -q "REST API design" --guidelines --domain software
  python -m skills_fabric.retrievals.brave_search_client -q "diabetes treatment" --guidelines --domain medical --country USA

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
    parser.add_argument("--academic", action="store_true", help="Filter to academic/scholarly sources")
    parser.add_argument("--guidelines", action="store_true", help="Search for guidelines and best practices")
    parser.add_argument("--domain", choices=["software", "medical", "security", "devops", "data_science"],
                       default="software", help="Domain for guidelines search (default: software)")
    parser.add_argument("--country", help="Country filter for medical guidelines (USA, UK, EU)")
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

        if args.guidelines:
            response = await client.search_guidelines(
                args.query, domain=args.domain, country=args.country,
                count=args.count, freshness=freshness
            )
        elif args.academic:
            response = await client.search_academic(args.query, count=args.count, freshness=freshness)
        elif args.technical:
            response = await client.search_technical(args.query, count=args.count, freshness=freshness)
        elif args.news:
            response = await client.search_news(args.query, count=args.count, freshness=freshness)
        else:
            response = await client.search(args.query, count=args.count, freshness=freshness)

        if args.json:
            print(json.dumps(response.to_dict(), indent=2))
        else:
            # Determine search type for header
            search_type = "Guidelines" if args.guidelines else "Academic" if args.academic else "Technical" if args.technical else "News" if args.news else "Web"
            print(f"Search ({search_type}): {response.query}")
            print(f"Results: {response.result_count}")
            print()
            for i, r in enumerate(response.results, 1):
                print(f"{i}. {r.title}")
                print(f"   URL: {r.url}")
                print(f"   Domain: {r.domain}", end="")
                if r.domain_authority:
                    print(f" ({r.domain_authority.category})", end="")
                    if r.is_primary_source:
                        print(" ★", end="")
                print()
                if r.date:
                    print(f"   Date: {r.date}")
                if r.content_type != ContentType.UNKNOWN:
                    print(f"   Type: {r.content_type.value}")
                desc = r.description[:120] + "..." if len(r.description) > 120 else r.description
                print(f"   {desc}")
                # Show relevance with score breakdown
                print(f"   Relevance: {r.relevance_score:.3f}", end="")
                if r.position_score > 0 or r.query_match_score > 0:
                    print(f" [pos={r.position_score:.2f}, match={r.query_match_score:.2f}, "
                          f"fresh={r.freshness_score:.2f}, trust={r.trust_score:.2f}]", end="")
                print()
                print()

    asyncio.run(run())


if __name__ == "__main__":
    _cli()
