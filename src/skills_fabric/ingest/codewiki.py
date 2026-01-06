"""CodeWiki Crawler - Documentation ingestion for Skills Fabric.

Integrates with GitClone for complete repository + documentation ingestion:
- Crawl documentation sites (GitHub wiki, CodeWiki, docs sites)
- Clean and segment markdown into concepts
- Store concepts in KuzuDB for PROVEN linking

Based on research artifacts from older_project/research_artifacts/codewiki_ingest.py

Usage:
    from skills_fabric.ingest import CodeWikiCrawler, GitCloner

    # Clone repo and crawl docs together
    cloner = GitCloner()
    repo_path = cloner.clone("https://github.com/langchain-ai/langgraph")

    crawler = CodeWikiCrawler()
    concepts = await crawler.crawl_repo_docs("langgraph")
    crawler.store_concepts(concepts)

    # Now PROVEN linker can work
    from skills_fabric.link import ProvenLinker
    linker = ProvenLinker()
    linker.link_all()  # Concept → Symbol links created
"""
import asyncio
import re
import os
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from ..core.config import config
from ..core.database import db


# =============================================================================
# Configuration
# =============================================================================

MAX_CHARS = 24000  # Max characters per concept chunk
MAX_LINES = 500    # Max lines per concept chunk


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class Concept:
    """A documentation concept extracted from CodeWiki.

    Represents a semantic unit of documentation that can be
    linked to source code symbols via PROVEN relationships.
    """
    name: str
    content: str
    source_doc: str
    library: str = ""
    section_path: str = ""  # e.g., "Getting Started > Quick Start"
    char_count: int = 0
    line_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self.char_count = len(self.content)
        self.line_count = len(self.content.splitlines())


@dataclass
class CrawlResult:
    """Result of a CodeWiki crawl operation."""
    success: bool
    url: str
    concepts: list[Concept] = field(default_factory=list)
    raw_markdown: str = ""
    error: str = ""
    duration_ms: float = 0


# =============================================================================
# Markdown Processing
# =============================================================================

class MarkdownProcessor:
    """Clean and segment markdown documentation.

    Processing pipeline:
    1. Clean: Remove UI artifacts, normalize whitespace
    2. Segment: Split by H2/H3 headers into concept chunks
    3. Extract: Create Concept objects with metadata
    """

    def __init__(self, max_chars: int = MAX_CHARS, max_lines: int = MAX_LINES):
        self.max_chars = max_chars
        self.max_lines = max_lines

    def clean(self, raw_md: str) -> str:
        """Clean raw markdown from crawler.

        Removes:
        - UI artifacts (copy code buttons, zoom icons)
        - Excessive whitespace
        - Common navigation elements
        """
        cleaned = raw_md

        # Remove UI artifacts
        ui_patterns = [
            r'copy code',
            r'zoom_in',
            r'fullscreen',
            r'filter_center_focus',
            r'\[edit\]',
            r'\[source\]',
            r'Skip to content',
            r'Table of contents',
        ]
        for pattern in ui_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Normalize whitespace (3+ newlines → 2)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Remove empty links
        cleaned = re.sub(r'\[\s*\]\([^)]*\)', '', cleaned)

        return cleaned.strip()

    def segment(self, clean_md: str, source_doc: str, library: str = "") -> list[Concept]:
        """Segment markdown into concept chunks.

        Strategy:
        1. Split by H2 (##) headers first
        2. If section too large, split by H3 (###)
        3. If still too large, split by paragraphs

        Returns:
            List of Concept objects
        """
        concepts = []

        # Split by H2 headers
        parts = re.split(r'(^## .*)', clean_md, flags=re.MULTILINE)

        # Handle introduction (content before first ##)
        if parts[0].strip():
            concepts.append(Concept(
                name="Introduction",
                content=parts[0].strip(),
                source_doc=source_doc,
                library=library,
                section_path="Introduction"
            ))

        # Process H2 sections
        it = iter(parts[1:])
        for header in it:
            try:
                content = next(it)
            except StopIteration:
                content = ""

            full_block = header + content
            title = header.strip().lstrip('#').strip()

            if self._fits_limits(full_block):
                concepts.append(Concept(
                    name=title,
                    content=full_block,
                    source_doc=source_doc,
                    library=library,
                    section_path=title
                ))
            else:
                # Split by H3
                concepts.extend(self._split_by_h3(
                    title, full_block, source_doc, library
                ))

        return concepts

    def _fits_limits(self, text: str) -> bool:
        """Check if text fits within size limits."""
        return len(text) <= self.max_chars and len(text.splitlines()) <= self.max_lines

    def _split_by_h3(
        self,
        h2_title: str,
        h2_content: str,
        source_doc: str,
        library: str
    ) -> list[Concept]:
        """Split an H2 section by H3 headers."""
        concepts = []
        parts = re.split(r'(^### .*)', h2_content, flags=re.MULTILINE)

        current_chunk = ""
        current_part = 1

        # Handle preamble
        if parts[0].strip():
            current_chunk = parts[0]

        it = iter(parts[1:])
        for header in it:
            try:
                content = next(it)
            except StopIteration:
                content = ""

            full_section = header + content

            if len(current_chunk) + len(full_section) > self.max_chars:
                # Save current chunk
                if current_chunk:
                    h3_title = self._extract_h3_title(current_chunk) or f"{h2_title} (Part {current_part})"
                    concepts.append(Concept(
                        name=h3_title,
                        content=current_chunk,
                        source_doc=source_doc,
                        library=library,
                        section_path=f"{h2_title} > {h3_title}"
                    ))
                    current_part += 1

                # Check if single section is too big
                if not self._fits_limits(full_section):
                    concepts.extend(self._split_by_paragraph(
                        header.strip().lstrip('#').strip(),
                        full_section, source_doc, library, h2_title
                    ))
                    current_chunk = ""
                else:
                    current_chunk = full_section
            else:
                current_chunk += full_section

        # Save remainder
        if current_chunk:
            h3_title = self._extract_h3_title(current_chunk) or f"{h2_title} (Part {current_part})"
            concepts.append(Concept(
                name=h3_title,
                content=current_chunk,
                source_doc=source_doc,
                library=library,
                section_path=f"{h2_title} > {h3_title}"
            ))

        return concepts

    def _split_by_paragraph(
        self,
        title: str,
        content: str,
        source_doc: str,
        library: str,
        parent_section: str
    ) -> list[Concept]:
        """Split content by paragraphs as last resort."""
        concepts = []
        paragraphs = re.split(r'(\n{2,})', content)

        current_chunk = ""
        current_part = 1

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.max_chars:
                if current_chunk:
                    concepts.append(Concept(
                        name=f"{title} (Part {current_part})",
                        content=current_chunk,
                        source_doc=source_doc,
                        library=library,
                        section_path=f"{parent_section} > {title}"
                    ))
                    current_part += 1
                    current_chunk = para
                else:
                    # Single paragraph is too big - just save it
                    concepts.append(Concept(
                        name=f"{title} (Part {current_part})",
                        content=para,
                        source_doc=source_doc,
                        library=library,
                        section_path=f"{parent_section} > {title}"
                    ))
                    current_part += 1
            else:
                current_chunk += para

        if current_chunk:
            concepts.append(Concept(
                name=f"{title} (Part {current_part})",
                content=current_chunk,
                source_doc=source_doc,
                library=library,
                section_path=f"{parent_section} > {title}"
            ))

        return concepts

    def _extract_h3_title(self, content: str) -> Optional[str]:
        """Extract first H3 title from content."""
        match = re.search(r'^### (.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None


# =============================================================================
# CodeWiki Crawler
# =============================================================================

class CodeWikiCrawler:
    """Crawl documentation and create Concept nodes.

    Supports multiple documentation sources:
    - GitHub wiki pages
    - CodeWiki.google proxied docs
    - Local markdown directories
    - README files from cloned repos

    Integration with GitCloner:
        cloner = GitCloner()
        repo_path = cloner.clone(url)

        crawler = CodeWikiCrawler()
        concepts = crawler.crawl_local_docs(repo_path, library="langgraph")
        crawler.store_concepts(concepts)
    """

    def __init__(self):
        self.processor = MarkdownProcessor()
        self._crawl4ai_available = self._check_crawl4ai()

    def _check_crawl4ai(self) -> bool:
        """Check if crawl4ai is available."""
        try:
            from crawl4ai import AsyncWebCrawler
            return True
        except ImportError:
            return False

    async def crawl_url(self, url: str, library: str = "") -> CrawlResult:
        """Crawl a documentation URL.

        Args:
            url: URL to crawl (GitHub wiki, docs site, etc.)
            library: Library name for metadata

        Returns:
            CrawlResult with extracted concepts
        """
        if not self._crawl4ai_available:
            return CrawlResult(
                success=False,
                url=url,
                error="crawl4ai not installed. Run: pip install crawl4ai"
            )

        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

        start_time = datetime.now()

        # Convert GitHub URLs to CodeWiki
        target_url = self._normalize_url(url)

        browser_conf = BrowserConfig(headless=True)
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
            wait_until="networkidle",
            delay_before_return_html=5.0,
            js_code="window.scrollTo(0, document.body.scrollHeight);"
        )

        try:
            async with AsyncWebCrawler(config=browser_conf) as crawler:
                result = await crawler.arun(url=target_url, config=run_conf)

                if not result.success:
                    return CrawlResult(
                        success=False,
                        url=target_url,
                        error=result.error_message
                    )

                # Process markdown
                clean_md = self.processor.clean(result.markdown)
                concepts = self.processor.segment(clean_md, target_url, library)

                duration = (datetime.now() - start_time).total_seconds() * 1000

                return CrawlResult(
                    success=True,
                    url=target_url,
                    concepts=concepts,
                    raw_markdown=clean_md,
                    duration_ms=duration
                )

        except Exception as e:
            return CrawlResult(
                success=False,
                url=target_url,
                error=str(e)
            )

    def crawl_local_docs(
        self,
        repo_path: Path,
        library: str = "",
        doc_patterns: list[str] = None
    ) -> list[Concept]:
        """Crawl documentation from a local repository.

        Searches for:
        - README.md (root and subdirectories)
        - docs/ directory
        - wiki/ directory (if cloned)
        - *.md files in common locations

        Args:
            repo_path: Path to cloned repository
            library: Library name for metadata
            doc_patterns: Additional glob patterns for docs

        Returns:
            List of Concept objects
        """
        concepts = []
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return concepts

        # Default patterns
        patterns = doc_patterns or [
            "README.md",
            "README.rst",
            "docs/**/*.md",
            "doc/**/*.md",
            "documentation/**/*.md",
            "wiki/**/*.md",
            "*.md",
        ]

        # Find all doc files
        doc_files = set()
        for pattern in patterns:
            doc_files.update(repo_path.glob(pattern))

        # Filter out non-documentation
        exclude_patterns = [
            "node_modules", "__pycache__", ".git",
            "venv", "env", ".venv", "dist", "build",
            "CHANGELOG", "CONTRIBUTING", "LICENSE"
        ]

        for doc_file in sorted(doc_files):
            # Skip excluded paths
            if any(excl in str(doc_file) for excl in exclude_patterns):
                continue

            try:
                content = doc_file.read_text(encoding='utf-8')
                if len(content.strip()) < 100:  # Skip tiny files
                    continue

                # Clean and segment
                clean_md = self.processor.clean(content)
                source_doc = str(doc_file.relative_to(repo_path))

                file_concepts = self.processor.segment(clean_md, source_doc, library)
                concepts.extend(file_concepts)

            except Exception:
                continue  # Skip files that can't be read

        return concepts

    async def crawl_github_wiki(self, repo_url: str) -> CrawlResult:
        """Crawl a GitHub repository's wiki.

        Args:
            repo_url: GitHub repo URL (e.g., https://github.com/owner/repo)

        Returns:
            CrawlResult with wiki concepts
        """
        # Construct wiki URL
        wiki_url = repo_url.rstrip('/') + '/wiki'
        library = repo_url.split('/')[-1]

        return await self.crawl_url(wiki_url, library=library)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for crawling.

        Converts GitHub URLs to CodeWiki proxy if needed.
        """
        if "github.com" in url and "codewiki.google" not in url:
            clean_url = url.replace("https://", "").replace("http://", "")
            return f"https://codewiki.google/{clean_url}"
        return url

    def store_concepts(self, concepts: list[Concept]) -> int:
        """Store concepts in KuzuDB.

        Creates Concept nodes that can be linked to Symbol nodes
        via the PROVEN relationship.

        Args:
            concepts: List of Concept objects

        Returns:
            Number of concepts stored
        """
        stored = 0

        for concept in concepts:
            try:
                # Use parameterized query to prevent injection
                db.execute(
                    """
                    MERGE (c:Concept {name: $name})
                    SET c.content = $content,
                        c.source_doc = $source_doc,
                        c.library = $library,
                        c.section_path = $section_path,
                        c.char_count = $char_count,
                        c.line_count = $line_count
                    """,
                    {
                        "name": concept.name,
                        "content": concept.content,
                        "source_doc": concept.source_doc,
                        "library": concept.library,
                        "section_path": concept.section_path,
                        "char_count": concept.char_count,
                        "line_count": concept.line_count
                    }
                )
                stored += 1
            except Exception:
                continue

        return stored

    def get_concept_count(self, library: str = "") -> int:
        """Get count of stored concepts."""
        if library:
            result = db.execute(
                "MATCH (c:Concept {library: $library}) RETURN count(c) as cnt",
                {"library": library}
            )
        else:
            result = db.execute("MATCH (c:Concept) RETURN count(c) as cnt")

        return result[0]["cnt"] if result else 0


# =============================================================================
# Integrated Ingestion Pipeline
# =============================================================================

class IntegratedIngestor:
    """Complete ingestion pipeline: Git Clone + CodeWiki + Concept Storage.

    Combines GitCloner and CodeWikiCrawler for one-step ingestion.

    Usage:
        ingestor = IntegratedIngestor()
        result = await ingestor.ingest("https://github.com/langchain-ai/langgraph")

        print(f"Symbols: {result.symbol_count}")
        print(f"Concepts: {result.concept_count}")
        print(f"Ready for PROVEN linking!")
    """

    def __init__(self):
        from .gitclone import GitCloner
        self.cloner = GitCloner()
        self.crawler = CodeWikiCrawler()

    async def ingest(
        self,
        repo_url: str,
        crawl_wiki: bool = True,
        crawl_local: bool = True
    ) -> "IngestResult":
        """Full ingestion: clone + crawl + store.

        Args:
            repo_url: GitHub repository URL
            crawl_wiki: Whether to crawl wiki pages
            crawl_local: Whether to crawl local markdown files

        Returns:
            IngestResult with counts and status
        """
        result = IngestResult(repo_url=repo_url)

        # Extract library name
        library = repo_url.rstrip('/').split('/')[-1]
        result.library = library

        # 1. Clone repository
        repo_path = self.cloner.clone(repo_url)
        if not repo_path:
            result.success = False
            result.error = "Failed to clone repository"
            return result

        result.repo_path = repo_path

        # 2. Count source files (symbols will be extracted by analyze step)
        source_files = self.cloner.list_source_files(repo_path)
        result.source_file_count = len(source_files)

        # 3. Crawl local documentation
        concepts = []
        if crawl_local:
            local_concepts = self.crawler.crawl_local_docs(repo_path, library)
            concepts.extend(local_concepts)

        # 4. Crawl wiki if requested
        if crawl_wiki:
            wiki_result = await self.crawler.crawl_github_wiki(repo_url)
            if wiki_result.success:
                concepts.extend(wiki_result.concepts)

        # 5. Store concepts
        result.concept_count = self.crawler.store_concepts(concepts)
        result.success = True

        return result


@dataclass
class IngestResult:
    """Result of integrated ingestion."""
    repo_url: str
    library: str = ""
    repo_path: Optional[Path] = None
    source_file_count: int = 0
    concept_count: int = 0
    success: bool = False
    error: str = ""


# =============================================================================
# Convenience Functions
# =============================================================================

async def crawl_and_store(url: str, library: str = "") -> int:
    """Convenience function to crawl URL and store concepts.

    Args:
        url: Documentation URL to crawl
        library: Library name

    Returns:
        Number of concepts stored
    """
    crawler = CodeWikiCrawler()
    result = await crawler.crawl_url(url, library)

    if result.success:
        return crawler.store_concepts(result.concepts)
    return 0


def crawl_local_and_store(repo_path: Path, library: str = "") -> int:
    """Convenience function to crawl local docs and store concepts.

    Args:
        repo_path: Path to repository
        library: Library name

    Returns:
        Number of concepts stored
    """
    crawler = CodeWikiCrawler()
    concepts = crawler.crawl_local_docs(repo_path, library)
    return crawler.store_concepts(concepts)
