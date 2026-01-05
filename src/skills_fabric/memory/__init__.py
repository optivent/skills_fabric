"""Memory module for Skills Fabric.

Inspired by Supermemory for persistent, intelligent memory:
- Knowledge Graph: Enhanced graph with memory features
- Session Memory: Track learning across sessions
- Embedding Search: Semantic similarity retrieval
- Smart Forgetting: Decay-based relevance

Key Features:
- Persistent storage across CLI sessions
- Recency bias for memory retrieval
- Cross-session strategy learning
- Semantic search for related skills

Usage:
    from skills_fabric.memory import (
        KnowledgeGraph, Memory, MemoryType,
        SessionMemory,
        SemanticSearch
    )

    # Knowledge graph
    kg = KnowledgeGraph()
    kg.add_memory(Memory(id="s1", content=skill, memory_type=MemoryType.SKILL))

    # Session memory
    sessions = SessionMemory()
    session = sessions.start_session("langgraph")
    best_strategy = sessions.get_best_strategy("langgraph")

    # Semantic search
    search = SemanticSearch()
    search.index("s1", "How to use state in LangGraph")
    results = search.search("state management")
"""
from .knowledge_graph import (
    KnowledgeGraph,
    Memory,
    MemoryType,
    MemoryLink,
)
from .session import (
    SessionMemory,
    SessionRecord,
)
from .embeddings import (
    SemanticSearch,
    EmbeddingResult,
    EmbeddingProvider,
    VoyageAIProvider,
    LocalEmbeddingProvider,
    EmbeddingCache,
)

__all__ = [
    # Knowledge Graph
    "KnowledgeGraph",
    "Memory",
    "MemoryType",
    "MemoryLink",
    # Session Memory
    "SessionMemory",
    "SessionRecord",
    # Embeddings
    "SemanticSearch",
    "EmbeddingResult",
    "EmbeddingProvider",
    "VoyageAIProvider",
    "LocalEmbeddingProvider",
    "EmbeddingCache",
]
