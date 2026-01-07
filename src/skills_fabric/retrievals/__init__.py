"""Retrieval clients for Skills Fabric.

Provides research and search APIs for:
- Perplexity AI (sonar model) - Research queries with citations
- Brave Search - Web and news search with freshness filters

Features:
- Citation extraction and validation
- Rate limiting with exponential backoff
- Iterative research loop with query refinement
- Multiple refinement strategies (RELATED, REFINE, VALIDATE, COMPREHENSIVE, CITATIONS)
- Research depth and convergence tracking
- Related questions for follow-up research
- Web and news search (Brave)
- Freshness filtering (pd, pw, pm, py)
- Technical/academic source filtering
"""
from .perplexity_client import (
    PerplexityClient,
    PerplexityConfig,
    PerplexityResponse,
    SonarModel,
    SearchDomain,
    Citation,
    RelatedQuestion,
    ResearchFinding,
    ResearchResult,
    TokenUsage,
    # New iterative research types
    RefinementStrategy,
    ResearchStopReason,
    CitationValidation,
    ResearchMetrics,
    RefinedQuery,
)

from .brave_search_client import (
    BraveSearchClient,
    BraveConfig,
    BraveSearchResponse,
    SearchResult,
    Freshness,
    SafeSearch,
    ResultSource,
    # Enhanced result parsing
    ContentType,
    DomainAuthority,
    RelevanceScorer,
)

__all__ = [
    # Perplexity Client
    "PerplexityClient",
    "PerplexityConfig",
    "PerplexityResponse",
    # Perplexity Models
    "SonarModel",
    "SearchDomain",
    # Research strategies and tracking
    "RefinementStrategy",
    "ResearchStopReason",
    # Perplexity Data classes
    "Citation",
    "CitationValidation",
    "RelatedQuestion",
    "ResearchFinding",
    "ResearchResult",
    "ResearchMetrics",
    "RefinedQuery",
    "TokenUsage",
    # Brave Search Client
    "BraveSearchClient",
    "BraveConfig",
    "BraveSearchResponse",
    "SearchResult",
    "Freshness",
    "SafeSearch",
    "ResultSource",
    # Enhanced result parsing
    "ContentType",
    "DomainAuthority",
    "RelevanceScorer",
]
