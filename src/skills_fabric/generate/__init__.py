"""Generation module - Skill content generation with citations.

Components:
- SkillFactory: Generate skill content from source
- LLMClient: Interface to Claude models
- Citations: Add file:line references for zero-hallucination
"""
from .citations import (
    CitationSystem,
    CitationConfig,
    CitationResult,
    add_citations,
    extract_cited_symbols,
    verify_citations,
)

__all__ = [
    "CitationSystem",
    "CitationConfig",
    "CitationResult",
    "add_citations",
    "extract_cited_symbols",
    "verify_citations",
]
