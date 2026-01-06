"""Memory module for Skills Fabric.

Two memory systems available:

1. LEGACY SYSTEM (Supermemory-inspired):
   - Knowledge Graph: Enhanced graph with memory features
   - Session Memory: Track learning across sessions
   - Embedding Search: Semantic similarity retrieval

2. AGENT MEMORY SYSTEM (2026 Research-backed):
   - Beads: Work orchestration with dependency tracking
   - MIRIX: 6-type agent learning memory
   - ADK: Context compilation for multi-agent
   - Cognee: Code knowledge graphs

Usage (Agent Memory - Recommended):
    from skills_fabric.memory import AgentMemorySystem
    from pathlib import Path

    memory = AgentMemorySystem(Path("./memory_storage"))
    memory.start_session("session_001", "Update dependency tree")
    bead = memory.discover_work("Fix auth module")
    memory.complete_work(bead.id, learnings="Check API changes first")

Usage (Legacy):
    from skills_fabric.memory import (
        KnowledgeGraph, Memory, MemoryType,
        SessionMemory,
        SemanticSearch
    )

    kg = KnowledgeGraph()
    kg.add_memory(Memory(id="s1", content=skill, memory_type=MemoryType.SKILL))
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

# Agent Memory System (2026)
from .agent_memory import (
    # Beads (Work Orchestration)
    Bead,
    BeadStatus,
    BeadPriority,
    BeadsStore,
    # MIRIX (Agent Learning)
    MemoryType as AgentMemoryType,  # Avoid collision with legacy MemoryType
    MemoryEntry,
    MIRIXMemory,
    # ADK (Context Compilation)
    ContextTier,
    ContextBlock,
    CompiledContext,
    ADKContextManager,
    # Integrated System
    AgentMemorySystem,
)

__all__ = [
    # Knowledge Graph (Legacy)
    "KnowledgeGraph",
    "Memory",
    "MemoryType",
    "MemoryLink",
    # Session Memory (Legacy)
    "SessionMemory",
    "SessionRecord",
    # Embeddings (Legacy)
    "SemanticSearch",
    "EmbeddingResult",
    "EmbeddingProvider",
    "VoyageAIProvider",
    "LocalEmbeddingProvider",
    "EmbeddingCache",
    # Agent Memory System (2026)
    "Bead",
    "BeadStatus",
    "BeadPriority",
    "BeadsStore",
    "AgentMemoryType",
    "MemoryEntry",
    "MIRIXMemory",
    "ContextTier",
    "ContextBlock",
    "CompiledContext",
    "ADKContextManager",
    "AgentMemorySystem",
]
