#!/usr/bin/env python3
"""
arXiv Paper Retrieval Client with Docling Integration

Features:
- Search arXiv's 2M+ paper database
- Download papers (PDF and source)
- Convert to AI-ready format with Docling
- Extract structured content (sections, equations, references)
- Category-based browsing

arXiv API: https://arxiv.org/help/api/
Docling: For PDF to markdown conversion

Categories:
- cs.AI, cs.LG, cs.CL (AI, ML, NLP)
- stat.ML (Machine Learning Statistics)
- math.* (Mathematics)
- physics.* (Physics)
"""

import os
import re
import asyncio
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Iterator
from datetime import datetime
import logging
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class Author:
    """Paper author."""
    name: str
    affiliation: str = ""


@dataclass
class ArxivPaper:
    """An arXiv paper with metadata."""
    id: str  # e.g., "2301.00001"
    title: str
    authors: List[Author]
    abstract: str
    categories: List[str]
    published: datetime
    updated: datetime
    pdf_url: str
    source_url: str
    doi: str = ""
    journal_ref: str = ""
    comment: str = ""

    @property
    def arxiv_url(self) -> str:
        return f"https://arxiv.org/abs/{self.id}"

    @property
    def primary_category(self) -> str:
        return self.categories[0] if self.categories else ""


@dataclass
class ProcessedPaper:
    """Paper processed with Docling."""
    paper: ArxivPaper
    markdown: str
    sections: List[Dict[str, str]] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    equations: List[str] = field(default_factory=list)
    figures: List[str] = field(default_factory=list)


class ArxivClient:
    """
    arXiv paper retrieval with Docling processing.

    Usage:
        client = ArxivClient()

        # Search for papers
        papers = await client.search("transformer attention mechanism", max_results=10)

        # Get by ID
        paper = await client.get_paper("2301.00001")

        # Download and process with Docling
        processed = await client.process_paper(paper, output_dir="./papers")

        # Search by category
        papers = await client.search_category("cs.AI", max_results=20)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("./arxiv_papers")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check for arxiv package
        try:
            import arxiv
            self._arxiv = arxiv
        except ImportError:
            logger.warning("arxiv package not installed. Run: pip install arxiv")
            self._arxiv = None

    async def search(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ) -> List[ArxivPaper]:
        """
        Search arXiv papers.

        Args:
            query: Search query (supports arXiv query syntax)
            max_results: Maximum papers to return
            sort_by: "relevance", "lastUpdatedDate", "submittedDate"
            sort_order: "ascending" or "descending"

        Returns:
            List of matching papers
        """
        if not self._arxiv:
            raise RuntimeError("arxiv package not installed")

        # Map sort options
        sort_map = {
            "relevance": self._arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": self._arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": self._arxiv.SortCriterion.SubmittedDate,
        }
        order_map = {
            "ascending": self._arxiv.SortOrder.Ascending,
            "descending": self._arxiv.SortOrder.Descending,
        }

        search = self._arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_map.get(sort_by, self._arxiv.SortCriterion.Relevance),
            sort_order=order_map.get(sort_order, self._arxiv.SortOrder.Descending),
        )

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: list(search.results())
        )

        return [self._convert_result(r) for r in results]

    async def search_category(
        self,
        category: str,
        max_results: int = 20,
        days_back: int = 7,
    ) -> List[ArxivPaper]:
        """
        Search papers by category.

        Args:
            category: arXiv category (e.g., "cs.AI", "cs.LG", "stat.ML")
            max_results: Maximum papers
            days_back: Only papers from last N days

        Returns:
            Recent papers in category
        """
        query = f"cat:{category}"
        return await self.search(
            query,
            max_results=max_results,
            sort_by="submittedDate",
            sort_order="descending"
        )

    async def get_paper(self, arxiv_id: str) -> Optional[ArxivPaper]:
        """
        Get a specific paper by arXiv ID.

        Args:
            arxiv_id: arXiv ID (e.g., "2301.00001" or "2301.00001v2")

        Returns:
            Paper if found, None otherwise
        """
        if not self._arxiv:
            raise RuntimeError("arxiv package not installed")

        search = self._arxiv.Search(id_list=[arxiv_id])

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: list(search.results())
        )

        return self._convert_result(results[0]) if results else None

    async def download_pdf(
        self,
        paper: ArxivPaper,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """
        Download paper PDF.

        Args:
            paper: Paper to download
            output_dir: Output directory

        Returns:
            Path to downloaded PDF
        """
        if not self._arxiv:
            raise RuntimeError("arxiv package not installed")

        output_dir = output_dir or self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from ID and title
        safe_title = re.sub(r'[^\w\s-]', '', paper.title)[:50]
        filename = f"{paper.id}_{safe_title}.pdf"
        output_path = output_dir / filename

        if output_path.exists():
            logger.info(f"PDF already exists: {output_path}")
            return output_path

        # Download using arxiv library
        search = self._arxiv.Search(id_list=[paper.id])

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: list(search.results())
        )

        if results:
            await loop.run_in_executor(
                None,
                lambda: results[0].download_pdf(dirpath=str(output_dir), filename=filename)
            )

        return output_path

    async def process_paper(
        self,
        paper: ArxivPaper,
        output_dir: Optional[Path] = None,
        use_docling: bool = True,
    ) -> ProcessedPaper:
        """
        Download and process paper with Docling.

        Args:
            paper: Paper to process
            output_dir: Output directory
            use_docling: Use Docling for conversion (if available)

        Returns:
            ProcessedPaper with markdown content and extracted elements
        """
        output_dir = output_dir or self.output_dir

        # Download PDF
        pdf_path = await self.download_pdf(paper, output_dir)

        # Convert with Docling
        markdown = ""
        sections = []
        references = []
        equations = []
        figures = []

        if use_docling:
            try:
                markdown, sections, references, equations, figures = await self._process_with_docling(pdf_path)
            except Exception as e:
                logger.warning(f"Docling processing failed: {e}")
                # Fallback to basic text extraction
                markdown = f"# {paper.title}\n\n{paper.abstract}"

        return ProcessedPaper(
            paper=paper,
            markdown=markdown,
            sections=sections,
            references=references,
            equations=equations,
            figures=figures,
        )

    async def _process_with_docling(
        self,
        pdf_path: Path,
    ) -> tuple:
        """Process PDF with Docling."""
        try:
            from docling.document_converter import DocumentConverter
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import PdfFormatOption

            # Create converter
            converter = DocumentConverter()

            # Convert PDF
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: converter.convert(str(pdf_path))
            )

            # Extract markdown
            markdown = result.document.export_to_markdown()

            # Extract sections
            sections = []
            for item in result.document.iterate_items():
                if hasattr(item, 'text') and hasattr(item, 'label'):
                    sections.append({
                        "label": str(item.label),
                        "text": item.text
                    })

            # Extract references (look for bibliography section)
            references = []
            in_references = False
            for section in sections:
                if "reference" in section.get("label", "").lower() or "bibliography" in section.get("label", "").lower():
                    in_references = True
                if in_references and section.get("text"):
                    references.append(section["text"])

            # Extract equations (basic pattern matching)
            equations = re.findall(r'\$\$(.+?)\$\$|\\\[(.+?)\\\]', markdown, re.DOTALL)
            equations = [eq[0] or eq[1] for eq in equations]

            # Extract figure captions
            figures = re.findall(r'Figure \d+[:\.]?\s*(.+?)(?:\n|$)', markdown)

            return markdown, sections, references, equations, figures

        except ImportError:
            logger.warning("docling not installed. Run: pip install docling")
            return "", [], [], [], []

    def _convert_result(self, result) -> ArxivPaper:
        """Convert arxiv.Result to ArxivPaper."""
        return ArxivPaper(
            id=result.entry_id.split("/")[-1],
            title=result.title,
            authors=[Author(name=a.name) for a in result.authors],
            abstract=result.summary,
            categories=result.categories,
            published=result.published,
            updated=result.updated,
            pdf_url=result.pdf_url,
            source_url=result.entry_id,
            doi=result.doi or "",
            journal_ref=result.journal_ref or "",
            comment=result.comment or "",
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_client: Optional[ArxivClient] = None


def get_client() -> ArxivClient:
    """Get the default arXiv client."""
    global _default_client
    if _default_client is None:
        _default_client = ArxivClient()
    return _default_client


async def search(query: str, **kwargs) -> List[ArxivPaper]:
    """Search arXiv papers."""
    return await get_client().search(query, **kwargs)


async def get_paper(arxiv_id: str) -> Optional[ArxivPaper]:
    """Get paper by ID."""
    return await get_client().get_paper(arxiv_id)


async def process_paper(paper: ArxivPaper, **kwargs) -> ProcessedPaper:
    """Download and process paper."""
    return await get_client().process_paper(paper, **kwargs)


# =============================================================================
# CLI DEMO
# =============================================================================

async def demo():
    """Demonstrate arXiv client capabilities."""
    print("=" * 70)
    print("arXiv Paper Retrieval Client Demo")
    print("=" * 70)

    client = ArxivClient()

    # Search for papers
    print("\n1. Search for Papers")
    print("-" * 40)
    papers = await client.search("transformer attention mechanism", max_results=5)
    print(f"Found {len(papers)} papers:")
    for paper in papers:
        print(f"\n  [{paper.id}] {paper.title[:60]}...")
        print(f"    Authors: {', '.join(a.name for a in paper.authors[:3])}")
        print(f"    Categories: {', '.join(paper.categories[:3])}")
        print(f"    Published: {paper.published.strftime('%Y-%m-%d')}")

    # Search by category
    print("\n2. Recent Papers in cs.AI")
    print("-" * 40)
    ai_papers = await client.search_category("cs.AI", max_results=3)
    for paper in ai_papers:
        print(f"  [{paper.id}] {paper.title[:50]}...")

    # Get specific paper
    print("\n3. Get Specific Paper")
    print("-" * 40)
    if papers:
        paper = await client.get_paper(papers[0].id)
        if paper:
            print(f"  Title: {paper.title}")
            print(f"  Abstract: {paper.abstract[:200]}...")
            print(f"  PDF: {paper.pdf_url}")

    # Process with Docling (if available)
    print("\n4. Process Paper with Docling")
    print("-" * 40)
    if papers:
        try:
            processed = await client.process_paper(papers[0])
            print(f"  Markdown length: {len(processed.markdown)} chars")
            print(f"  Sections: {len(processed.sections)}")
            print(f"  References: {len(processed.references)}")
            print(f"  Equations: {len(processed.equations)}")
        except Exception as e:
            print(f"  Processing error: {e}")

    print("\n" + "=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
