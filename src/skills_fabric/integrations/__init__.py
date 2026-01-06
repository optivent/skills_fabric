"""
Skills Fabric Integrations

Unified API management for optimal skill development tools:
- Intelligence: Anthropic Claude (Opus/Sonnet/Haiku)
- Memory: Mem0 (26% accuracy boost, 90% token savings)
- Embeddings: Voyage AI (13-16% better for code)
- Reranking: Jina (optimized for code search)
- Vector Store: Qdrant (Rust-based, fast)
- Research: Perplexity (F-score 0.858)
- Code Execution: E2B (secure sandboxes)
- Observability: LangSmith

Usage:
    from skills_fabric.integrations import UnifiedAPI

    api = UnifiedAPI()
    await api.initialize()

    # Memory-aware chat
    response = await api.chat("How do I use StateGraph?", user_id="dev1")

    # Code search
    results = await api.search_code("state machine", "langgraph_code")
"""

from .ultimate_stack import (
    OPTIMAL_STACK,
    CONFIGURATIONS,
    INTEGRATION_MATRIX,
    ToolCategory,
    Priority,
    ToolSpec,
    get_install_commands,
    get_env_template,
)

from .unified_api import (
    UnifiedAPI,
    APIConfig,
    SearchResult,
    MemoryEntry,
    ExecutionResult,
)

__all__ = [
    # Stack configuration
    "OPTIMAL_STACK",
    "CONFIGURATIONS",
    "INTEGRATION_MATRIX",
    "ToolCategory",
    "Priority",
    "ToolSpec",
    "get_install_commands",
    "get_env_template",
    # Unified API
    "UnifiedAPI",
    "APIConfig",
    "SearchResult",
    "MemoryEntry",
    "ExecutionResult",
]
