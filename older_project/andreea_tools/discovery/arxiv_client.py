"""
ArXiv API Client for MARO v2.0

Provides access to ArXiv preprint repository:
- Search preprints by topic, author, category
- Fetch paper metadata and abstracts
- Access PDF links

Uses the arxiv Python package (pip install arxiv)
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ArXivPaper:
    """An ArXiv paper result."""
    arxiv_id: str
    title: str
    abstract: str
    authors: List[str]
    published: datetime
    updated: Optional[datetime] = None
    categories: List[str] = field(default_factory=list)
    primary_category: str = ""
    pdf_url: str = ""
    doi: Optional[str] = None
    journal_ref: Optional[str] = None
    comment: Optional[str] = None
    source: str = "arxiv"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "published": self.published.isoformat() if self.published else None,
            "updated": self.updated.isoformat() if self.updated else None,
            "categories": self.categories,
            "primary_category": self.primary_category,
            "pdf_url": self.pdf_url,
            "doi": self.doi,
            "journal_ref": self.journal_ref,
            "source": self.source,
        }


class ArXivClient:
    """
    ArXiv API client for preprint search.

    Useful for finding cutting-edge research before peer review:
    - Machine learning in healthcare
    - Computational biology
    - Medical imaging
    - Biostatistics methods

    Example:
        client = ArXivClient()
        papers = await client.search("deep learning ophthalmology", max_results=10)
        for p in papers:
            print(f"{p.title} - {p.arxiv_id}")
    """

    # ArXiv categories relevant to medical/health research
    MEDICAL_CATEGORIES = [
        "q-bio.QM",   # Quantitative Methods in Biology
        "q-bio.NC",   # Neurons and Cognition
        "q-bio.TO",   # Tissues and Organs
        "stat.ML",    # Machine Learning (Statistics)
        "cs.CV",      # Computer Vision (medical imaging)
        "cs.LG",      # Machine Learning
        "cs.AI",      # Artificial Intelligence
        "stat.AP",    # Applications (Statistics)
        "physics.med-ph",  # Medical Physics
    ]

    def __init__(self):
        """Initialize ArXiv client."""
        if not ARXIV_AVAILABLE:
            raise ImportError(
                "arxiv package required. Install: pip install arxiv"
            )

    async def search(
        self,
        query: str,
        max_results: int = 20,
        sort_by: str = "relevance",
        categories: Optional[List[str]] = None,
    ) -> List[ArXivPaper]:
        """
        Search ArXiv for preprints.

        Args:
            query: Search query (supports ArXiv query syntax)
            max_results: Maximum number of results (default 20)
            sort_by: "relevance", "lastUpdatedDate", or "submittedDate"
            categories: Filter by ArXiv categories (e.g., ["cs.CV", "q-bio.QM"])

        Returns:
            List of ArXivPaper objects
        """
        # Build query
        search_query = query

        # Add category filter if specified
        if categories:
            cat_filter = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({query}) AND ({cat_filter})"

        # Map sort options
        sort_criterion = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate,
        }.get(sort_by, arxiv.SortCriterion.Relevance)

        # Create search client
        client = arxiv.Client()
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=sort_criterion,
        )

        # Run search (arxiv library is synchronous, wrap in executor)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: list(client.results(search))
        )

        # Convert to ArXivPaper objects
        papers = []
        for result in results:
            papers.append(ArXivPaper(
                arxiv_id=result.entry_id.split("/")[-1],
                title=result.title,
                abstract=result.summary,
                authors=[a.name for a in result.authors],
                published=result.published,
                updated=result.updated,
                categories=result.categories,
                primary_category=result.primary_category,
                pdf_url=result.pdf_url,
                doi=result.doi,
                journal_ref=result.journal_ref,
                comment=result.comment,
            ))

        logger.info(f"ArXiv search returned {len(papers)} results for: {query[:50]}")
        return papers

    async def fetch_paper(self, arxiv_id: str) -> Optional[ArXivPaper]:
        """
        Fetch a specific paper by ArXiv ID.

        Args:
            arxiv_id: ArXiv identifier (e.g., "2301.07041" or "arXiv:2301.07041")

        Returns:
            ArXivPaper object or None if not found
        """
        # Normalize ID
        arxiv_id = arxiv_id.replace("arXiv:", "").strip()

        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, lambda: list(client.results(search))
        )

        if results:
            result = results[0]
            return ArXivPaper(
                arxiv_id=result.entry_id.split("/")[-1],
                title=result.title,
                abstract=result.summary,
                authors=[a.name for a in result.authors],
                published=result.published,
                updated=result.updated,
                categories=result.categories,
                primary_category=result.primary_category,
                pdf_url=result.pdf_url,
                doi=result.doi,
                journal_ref=result.journal_ref,
                comment=result.comment,
            )

        return None

    async def search_medical_ai(
        self,
        query: str,
        max_results: int = 20,
    ) -> List[ArXivPaper]:
        """
        Search ArXiv specifically for medical AI/ML papers.

        Filters to relevant categories:
        - Computer Vision (medical imaging)
        - Machine Learning
        - Quantitative Biology
        - Medical Physics

        Args:
            query: Medical topic (e.g., "retinal imaging", "diabetic detection")
            max_results: Maximum results

        Returns:
            List of ArXivPaper objects
        """
        return await self.search(
            query,
            max_results=max_results,
            categories=self.MEDICAL_CATEGORIES,
            sort_by="lastUpdatedDate",
        )

    async def search_by_author(
        self,
        author_name: str,
        max_results: int = 50,
    ) -> List[ArXivPaper]:
        """
        Search for papers by author name.

        Args:
            author_name: Author name (e.g., "Yoshua Bengio")
            max_results: Maximum results

        Returns:
            List of ArXivPaper objects
        """
        query = f'au:"{author_name}"'
        return await self.search(query, max_results=max_results, sort_by="submittedDate")

    async def get_recent(
        self,
        category: str = "cs.CV",
        days: int = 7,
        max_results: int = 50,
    ) -> List[ArXivPaper]:
        """
        Get recent submissions in a category.

        Args:
            category: ArXiv category (e.g., "cs.CV", "q-bio.QM")
            days: Number of days to look back
            max_results: Maximum results

        Returns:
            List of ArXivPaper objects sorted by submission date
        """
        query = f"cat:{category}"
        return await self.search(
            query,
            max_results=max_results,
            sort_by="submittedDate",
        )

    def search_sync(self, query: str, **kwargs) -> List[ArXivPaper]:
        """Synchronous wrapper for search()."""
        return asyncio.run(self.search(query, **kwargs))


# Test function
async def _test_arxiv():
    """Test ArXiv client."""
    client = ArXivClient()

    print("=== General Search Test ===")
    papers = await client.search("deep learning retinal imaging", max_results=3)
    for p in papers:
        print(f"- {p.title[:60]}...")
        print(f"  ID: {p.arxiv_id}")
        print(f"  Authors: {', '.join(p.authors[:3])}")
        print(f"  Categories: {p.categories}")
        print()

    print("=== Medical AI Search Test ===")
    papers = await client.search_medical_ai("diabetic retinopathy detection", max_results=3)
    for p in papers:
        print(f"- {p.title[:60]}...")
        print(f"  Category: {p.primary_category}")
        print()

    print("=== Fetch Single Paper Test ===")
    paper = await client.fetch_paper("2301.07041")
    if paper:
        print(f"Title: {paper.title}")
        print(f"Abstract: {paper.abstract[:200]}...")


def _cli():
    """CLI entry point for ArXiv search."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="ArXiv Search CLI - Search preprints and fetch papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Search by topic
  python -m discovery.arxiv_client -q "deep learning retinal imaging" -n 20

  # Search medical AI papers specifically
  python -m discovery.arxiv_client -q "diabetic retinopathy detection" --medical-ai

  # Fetch specific paper by ArXiv ID
  python -m discovery.arxiv_client --fetch 2301.07041

  # Search by author
  python -m discovery.arxiv_client --author "Geoffrey Hinton" -n 50

  # Get recent papers in a category
  python -m discovery.arxiv_client --recent cs.CV -n 30

  # Output as JSON for processing
  python -m discovery.arxiv_client -q "transformer" --json > papers.json

MEDICAL AI CATEGORIES:
  When using --medical-ai, searches these ArXiv categories:
  - cs.CV (Computer Vision) - medical imaging
  - cs.LG (Machine Learning)
  - q-bio.QM (Quantitative Methods in Biology)
  - stat.ML (Machine Learning - Statistics)
  - physics.med-ph (Medical Physics)

SORT OPTIONS:
  relevance        - Most relevant first (default)
  lastUpdatedDate  - Recently updated first
  submittedDate    - Recently submitted first

USE CASES:
  - Finding cutting-edge ML methods before peer review
  - Tracking preprints from key researchers
  - Discovering medical AI innovations
  - Getting early access to methodological advances
"""
    )
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--max", "-n", type=int, default=10, help="Maximum results")
    parser.add_argument("--fetch", "-f", help="Fetch single paper by ArXiv ID")
    parser.add_argument("--author", "-a", help="Search by author name")
    parser.add_argument("--medical-ai", action="store_true", help="Filter to medical AI categories")
    parser.add_argument("--recent", help="Get recent papers in category (e.g., cs.CV)")
    parser.add_argument("--sort", choices=["relevance", "lastUpdatedDate", "submittedDate"], default="relevance")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--test", action="store_true", help="Run test suite")

    args = parser.parse_args()

    if args.test:
        asyncio.run(_test_arxiv())
        return

    async def run():
        client = ArXivClient()
        papers = []

        if args.fetch:
            paper = await client.fetch_paper(args.fetch)
            papers = [paper] if paper else []
        elif args.author:
            papers = await client.search_by_author(args.author, max_results=args.max)
        elif args.recent:
            papers = await client.get_recent(category=args.recent, max_results=args.max)
        elif args.medical_ai and args.query:
            papers = await client.search_medical_ai(args.query, max_results=args.max)
        elif args.query:
            papers = await client.search(args.query, max_results=args.max, sort_by=args.sort)
        else:
            parser.print_help()
            return

        if args.json:
            output = [p.to_dict() for p in papers]
            print(json.dumps(output, indent=2, default=str))
        else:
            for i, p in enumerate(papers, 1):
                print(f"{i}. {p.title}")
                print(f"   ArXiv ID: {p.arxiv_id}")
                print(f"   Authors: {', '.join(p.authors[:3])}{'...' if len(p.authors) > 3 else ''}")
                print(f"   Category: {p.primary_category}")
                print(f"   Published: {p.published.strftime('%Y-%m-%d') if p.published else 'N/A'}")
                print(f"   PDF: {p.pdf_url}")
                print()

    asyncio.run(run())


if __name__ == "__main__":
    _cli()
