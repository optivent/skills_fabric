#!/usr/bin/env python3
"""
Semantic Scholar API Client with rate limiting and comprehensive endpoints.

Rate Limit: 1 request per second (with API key)
API Key: Set S2_API_KEY environment variable
Get key at: https://www.semanticscholar.org/product/api
"""

import os
import logging
import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RateLimiter:
    """Simple rate limiter for Semantic Scholar API (1 req/sec)."""
    requests_per_second: float = 1.0
    last_request_time: float = 0.0

    def wait_if_needed(self):
        """Block until enough time has passed since last request."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limit: waiting {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()


class SemanticScholarAPI:
    """Semantic Scholar Academic Graph API client."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar API client.

        Args:
            api_key: API key (defaults to S2_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv("S2_API_KEY")
        if not self.api_key:
            logger.warning("No S2_API_KEY set - API rate limits will be restrictive")

        self.rate_limiter = RateLimiter()
        self.headers = {"x-api-key": self.api_key} if self.api_key else {}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited API request."""
        self.rate_limiter.wait_if_needed()

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting 2s")
                time.sleep(2)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"HTTP error: {e}")
                return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    def search_paper(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        limit: int = 10,
        year: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Search for papers by keyword.

        Args:
            query: Search term (use quotes for exact match)
            fields: Fields to return (default: title, authors, year, citationCount, url, externalIds)
            limit: Max results (default 10, max 100)
            year: Filter by year (e.g., "2020-" for 2020 onwards)

        Returns:
            Dictionary with 'total', 'offset', 'next', 'data' keys
        """
        if fields is None:
            fields = ["paperId", "title", "authors", "year", "citationCount",
                     "url", "externalIds", "venue", "publicationDate", "abstract"]

        params = {
            "query": query,
            "fields": ",".join(fields),
            "limit": min(limit, 100)
        }
        if year:
            params["year"] = year

        logger.info(f"Searching: {query[:60]}...")
        return self._make_request("paper/search", params)

    def get_paper_by_id(
        self,
        paper_id: str,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Get paper details by ID.

        Args:
            paper_id: Paper ID (supports: SHA, CorpusId, DOI, ARXIV, MAG, ACL, PMID, PMCID, URL)
            fields: Fields to return

        Returns:
            Paper dictionary
        """
        if fields is None:
            fields = ["paperId", "title", "authors", "year", "citationCount",
                     "url", "externalIds", "venue", "publicationDate", "abstract",
                     "referenceCount", "citationStyles"]

        params = {"fields": ",".join(fields)}

        logger.info(f"Fetching paper: {paper_id[:40]}...")
        return self._make_request(f"paper/{paper_id}", params)

    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """Get paper by DOI."""
        # Clean DOI (remove https://doi.org/ prefix if present)
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
        return self.get_paper_by_id(f"DOI:{doi}")

    def search_by_title_author(
        self,
        title: str,
        author: Optional[str] = None,
        year: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Search for paper by title and optionally author/year.

        Returns best match using relevance search.
        """
        # Build query
        query_parts = [f'"{title}"']
        if author:
            query_parts.append(author)

        query = " ".join(query_parts)

        result = self.search_paper(query, limit=5, year=f"{year}" if year else None)

        if result and result.get("data"):
            return result["data"][0]  # Return top match
        return None

    def get_citations(
        self,
        paper_id: str,
        limit: int = 100,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Get papers that cite this paper.

        Args:
            paper_id: Paper identifier
            limit: Max citations to return (default 100, max 1000)
            fields: Fields for citing papers

        Returns:
            Dictionary with citation data
        """
        if fields is None:
            fields = ["paperId", "title", "authors", "year"]

        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 1000)
        }

        logger.info(f"Fetching citations for: {paper_id[:40]}...")
        return self._make_request(f"paper/{paper_id}/citations", params)

    def get_references(
        self,
        paper_id: str,
        limit: int = 100,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Get papers referenced by this paper."""
        if fields is None:
            fields = ["paperId", "title", "authors", "year"]

        params = {
            "fields": ",".join(fields),
            "limit": min(limit, 1000)
        }

        logger.info(f"Fetching references for: {paper_id[:40]}...")
        return self._make_request(f"paper/{paper_id}/references", params)

    def batch_search_papers(self, queries: List[str]) -> List[Optional[Dict]]:
        """Search multiple papers sequentially (respects rate limit)."""
        results = []
        for i, query in enumerate(queries, 1):
            logger.info(f"Batch search [{i}/{len(queries)}]")
            result = self.search_paper(query, limit=5)
            results.append(result)
        return results


# Utility functions for bibliography formatting
def format_bibtex_entry(paper: Dict, cite_key: str) -> str:
    """Format paper data as BibTeX entry."""
    authors = " and ".join([
        f"{a.get('name', 'Unknown')}"
        for a in paper.get('authors', [])
    ])

    # Extract DOI
    doi = ""
    ext_ids = paper.get('externalIds', {})
    if ext_ids and 'DOI' in ext_ids:
        doi = ext_ids['DOI']

    # Build entry
    entry = f"@article{{{cite_key},\n"
    entry += f"  author = {{{authors}}},\n"
    entry += f"  title = {{{paper.get('title', 'Unknown title')}}},\n"

    if paper.get('year'):
        entry += f"  year = {{{paper['year']}}},\n"

    if paper.get('venue'):
        entry += f"  journal = {{{paper['venue']}}},\n"

    if doi:
        entry += f"  doi = {{{doi}}},\n"

    if paper.get('url'):
        entry += f"  url = {{{paper['url']}}},\n"

    entry += "}\n"
    return entry


def main():
    """Test the API client."""
    api = SemanticScholarAPI()

    # Test search
    print("\n" + "="*70)
    print("TEST 1: Search for ICG sentinel lymph node papers")
    print("="*70)
    result = api.search_paper(
        "indocyanine green sentinel lymph node breast cancer",
        limit=3,
        year="2020-"
    )

    if result and result.get('data'):
        print(f"\n✓ Found {result.get('total', 0)} papers")
        for i, paper in enumerate(result['data'][:3], 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   Authors: {', '.join([a.get('name', '') for a in paper.get('authors', [])])}")
            print(f"   Year: {paper.get('year', 'N/A')}")
            print(f"   Citations: {paper.get('citationCount', 0)}")

    # Test DOI lookup
    print("\n" + "="*70)
    print("TEST 2: Lookup by DOI")
    print("="*70)
    paper = api.get_paper_by_doi("10.1245/s10434-020-09288-7")
    if paper:
        print(f"✓ Found: {paper.get('title', 'No title')}")
        print(f"  Authors: {', '.join([a.get('name', '') for a in paper.get('authors', [])])}")
        print(f"  Year: {paper.get('year', 'N/A')}")

    print("\n" + "="*70)
    print("✓ API client test completed")
    print("="*70)


if __name__ == "__main__":
    main()
