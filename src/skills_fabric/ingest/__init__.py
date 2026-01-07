"""Ingest module - Source code and documentation ingestion.

Multi-source ingestion for Skills Fabric:
- GitCloner: Clone repositories for symbol extraction
- CodeWikiCrawler: Crawl documentation into Concept nodes
- Context7: Fetch library documentation via API
- ExaSearch: Semantic web search for examples
- Fusion: Multi-source fusion with consensus scoring

Complete Pipeline:
    from skills_fabric.ingest import IntegratedIngestor

    ingestor = IntegratedIngestor()
    result = await ingestor.ingest("https://github.com/langchain-ai/langgraph")

    # Symbols extracted from source code
    # Concepts extracted from documentation
    # Ready for PROVEN linking!

Individual Components:
    from skills_fabric.ingest import GitCloner, CodeWikiCrawler

    cloner = GitCloner()
    repo_path = cloner.clone(url)

    crawler = CodeWikiCrawler()
    concepts = crawler.crawl_local_docs(repo_path, library="langgraph")
    crawler.store_concepts(concepts)
"""
from .gitclone import GitCloner
from .codewiki import (
    Concept,
    CrawlResult,
    MarkdownProcessor,
    CodeWikiCrawler,
    IntegratedIngestor,
    IngestResult,
    crawl_and_store,
    crawl_local_and_store,
)
from .context7 import (
    Context7Client,
    Context7Doc,
    FetchStatus,
    FetchProgress,
    FetchResult,
    BatchFetchResult,
    LibraryResolutionStatus,
    LibraryResolutionResult,
)
from .exa_search import ExaSearchClient
from .fusion import MultiSourceFusion

__all__ = [
    # Git Clone
    "GitCloner",
    # CodeWiki
    "Concept",
    "CrawlResult",
    "MarkdownProcessor",
    "CodeWikiCrawler",
    "IntegratedIngestor",
    "IngestResult",
    "crawl_and_store",
    "crawl_local_and_store",
    # Context7
    "Context7Client",
    "Context7Doc",
    "FetchStatus",
    "FetchProgress",
    "FetchResult",
    "BatchFetchResult",
    "LibraryResolutionStatus",
    "LibraryResolutionResult",
    # Exa Search
    "ExaSearchClient",
    # Fusion
    "MultiSourceFusion",
]
