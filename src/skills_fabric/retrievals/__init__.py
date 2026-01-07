"""Retrieval clients for Skills Fabric.

Provides research and search APIs for:
- Perplexity AI (sonar model) - Research queries with citations
- Brave Search - Web and news search (coming in 4.3-4.4)

Features:
- Citation extraction and validation
- Rate limiting with exponential backoff
- Iterative research loop with query refinement
- Multiple refinement strategies (RELATED, REFINE, VALIDATE, COMPREHENSIVE, CITATIONS)
- Research depth and convergence tracking
- Related questions for follow-up research
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

__all__ = [
    # Client
    "PerplexityClient",
    "PerplexityConfig",
    "PerplexityResponse",
    # Models
    "SonarModel",
    "SearchDomain",
    # Research strategies and tracking
    "RefinementStrategy",
    "ResearchStopReason",
    # Data classes
    "Citation",
    "CitationValidation",
    "RelatedQuestion",
    "ResearchFinding",
    "ResearchResult",
    "ResearchMetrics",
    "RefinedQuery",
    "TokenUsage",
]
