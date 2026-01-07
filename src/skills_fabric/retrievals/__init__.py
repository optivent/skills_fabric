"""Retrieval clients for Skills Fabric.

Provides research and search APIs for:
- Perplexity AI (sonar model) - Research queries with citations
- Brave Search - Web and news search (coming in 4.3-4.4)

Features:
- Citation extraction and validation
- Rate limiting with exponential backoff
- Research loop pattern for iterative refinement
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
)

__all__ = [
    # Client
    "PerplexityClient",
    "PerplexityConfig",
    "PerplexityResponse",
    # Models
    "SonarModel",
    "SearchDomain",
    # Data classes
    "Citation",
    "RelatedQuestion",
    "ResearchFinding",
    "ResearchResult",
    "TokenUsage",
]
