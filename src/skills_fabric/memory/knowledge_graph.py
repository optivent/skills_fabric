"""Knowledge Graph - Enhanced graph storage with memory features.

Inspired by Supermemory:
- Persistent memory across sessions
- Smart forgetting with decay
- Recency bias for relevance
- Semantic similarity relationships

Graph Schema Extensions:
- Memory nodes with access tracking
- SIMILAR_TO relationships with similarity scores
- LEARNED_FROM relationships for failure tracking
- Decay factors for smart forgetting
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import math


class MemoryType(Enum):
    """Types of memories in the knowledge graph."""
    SKILL = "skill"
    CONCEPT = "concept"
    SYMBOL = "symbol"
    FAILURE = "failure"
    SESSION = "session"


@dataclass
class Memory:
    """A memory node in the knowledge graph."""
    id: str
    content: Any
    memory_type: MemoryType
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 1
    decay_factor: float = 1.0
    metadata: dict = field(default_factory=dict)

    def access(self) -> None:
        """Record an access to this memory."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    @property
    def relevance_score(self) -> float:
        """Calculate relevance score based on recency and access."""
        # Recency factor (exponential decay)
        hours_since_access = (datetime.now() - self.last_accessed).total_seconds() / 3600
        recency = math.exp(-0.1 * hours_since_access)

        # Access factor (logarithmic growth)
        access_factor = math.log(1 + self.access_count) / math.log(10)

        # Combined score with decay
        return (0.6 * recency + 0.4 * access_factor) * self.decay_factor


@dataclass
class MemoryLink:
    """A relationship between memories."""
    source_id: str
    target_id: str
    link_type: str  # SIMILAR_TO, LEARNED_FROM, RELATES_TO, etc.
    weight: float = 1.0
    metadata: dict = field(default_factory=dict)


class KnowledgeGraph:
    """Enhanced knowledge graph with memory features.

    Features:
    - Persistent storage in KuzuDB
    - Smart forgetting with decay
    - Recency-biased retrieval
    - Similarity-based linking

    Usage:
        kg = KnowledgeGraph()
        kg.add_memory(Memory(id="skill-1", content=skill, memory_type=MemoryType.SKILL))
        kg.link_memories("skill-1", "concept-1", "TEACHES")

        # Retrieve with recency bias
        relevant = kg.get_relevant_memories(query="state management", limit=10)
    """

    def __init__(self):
        from ..core.database import db
        self.db = db
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure memory schema exists in database."""
        try:
            self.db.execute("""
                CREATE NODE TABLE IF NOT EXISTS Memory(
                    id STRING PRIMARY KEY,
                    memory_type STRING,
                    content STRING,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INT64,
                    decay_factor DOUBLE
                )
            """)

            self.db.execute("""
                CREATE REL TABLE IF NOT EXISTS SIMILAR_TO(
                    FROM Memory TO Memory,
                    similarity DOUBLE
                )
            """)

            self.db.execute("""
                CREATE REL TABLE IF NOT EXISTS LEARNED_FROM(
                    FROM Memory TO Memory,
                    iteration INT64
                )
            """)

            self.db.execute("""
                CREATE REL TABLE IF NOT EXISTS RELATES_TO(
                    FROM Memory TO Memory,
                    relation_type STRING
                )
            """)
        except Exception:
            pass  # Tables may already exist

    def add_memory(self, memory: Memory) -> bool:
        """Add a memory to the knowledge graph."""
        try:
            self.db.execute(
                """
                CREATE (m:Memory {
                    id: $id,
                    memory_type: $memory_type,
                    content: $content,
                    created_at: $created_at,
                    last_accessed: $last_accessed,
                    access_count: $access_count,
                    decay_factor: $decay_factor
                })
                """,
                {
                    "id": memory.id,
                    "memory_type": memory.memory_type.value,
                    "content": str(memory.content)[:5000],
                    "created_at": memory.created_at.isoformat(),
                    "last_accessed": memory.last_accessed.isoformat(),
                    "access_count": memory.access_count,
                    "decay_factor": memory.decay_factor
                }
            )
            return True
        except Exception:
            return False

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID and update access."""
        try:
            res = self.db.execute(
                """
                MATCH (m:Memory {id: $id})
                RETURN m.memory_type, m.content, m.created_at, m.last_accessed,
                       m.access_count, m.decay_factor
                """,
                {"id": memory_id}
            )

            if res.has_next():
                row = res.get_next()
                memory = Memory(
                    id=memory_id,
                    memory_type=MemoryType(row[0]),
                    content=row[1],
                    created_at=datetime.fromisoformat(row[2]) if row[2] else datetime.now(),
                    last_accessed=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
                    access_count=row[4] or 1,
                    decay_factor=row[5] or 1.0
                )

                # Update access
                self._update_access(memory_id)
                return memory

            return None
        except Exception:
            return None

    def _update_access(self, memory_id: str) -> None:
        """Update access timestamp and count."""
        try:
            self.db.execute(
                """
                MATCH (m:Memory {id: $id})
                SET m.last_accessed = $now, m.access_count = m.access_count + 1
                """,
                {"id": memory_id, "now": datetime.now().isoformat()}
            )
        except Exception:
            pass

    def link_memories(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        weight: float = 1.0
    ) -> bool:
        """Create a relationship between memories."""
        try:
            if link_type == "SIMILAR_TO":
                self.db.execute(
                    """
                    MATCH (s:Memory {id: $source}), (t:Memory {id: $target})
                    CREATE (s)-[:SIMILAR_TO {similarity: $weight}]->(t)
                    """,
                    {"source": source_id, "target": target_id, "weight": weight}
                )
            elif link_type == "LEARNED_FROM":
                self.db.execute(
                    """
                    MATCH (s:Memory {id: $source}), (t:Memory {id: $target})
                    CREATE (s)-[:LEARNED_FROM {iteration: $weight}]->(t)
                    """,
                    {"source": source_id, "target": target_id, "weight": int(weight)}
                )
            else:
                self.db.execute(
                    """
                    MATCH (s:Memory {id: $source}), (t:Memory {id: $target})
                    CREATE (s)-[:RELATES_TO {relation_type: $type}]->(t)
                    """,
                    {"source": source_id, "target": target_id, "type": link_type}
                )
            return True
        except Exception:
            return False

    def get_similar_memories(
        self,
        memory_id: str,
        limit: int = 10
    ) -> list[tuple[Memory, float]]:
        """Get memories similar to the given one."""
        try:
            res = self.db.execute(
                """
                MATCH (m:Memory {id: $id})-[r:SIMILAR_TO]->(s:Memory)
                RETURN s.id, r.similarity
                ORDER BY r.similarity DESC
                LIMIT $limit
                """,
                {"id": memory_id, "limit": limit}
            )

            results = []
            while res.has_next():
                row = res.get_next()
                memory = self.get_memory(row[0])
                if memory:
                    results.append((memory, row[1]))

            return results
        except Exception:
            return []

    def apply_decay(self, hours_threshold: int = 24) -> int:
        """Apply decay to memories not accessed recently.

        Smart Forgetting: Reduce relevance of stale memories.
        """
        threshold = datetime.now() - timedelta(hours=hours_threshold)
        decay_rate = 0.95  # 5% decay per application

        try:
            res = self.db.execute(
                """
                MATCH (m:Memory)
                WHERE m.last_accessed < $threshold
                SET m.decay_factor = m.decay_factor * $rate
                RETURN count(m)
                """,
                {"threshold": threshold.isoformat(), "rate": decay_rate}
            )

            if res.has_next():
                return res.get_next()[0]
            return 0
        except Exception:
            return 0

    def prune_forgotten(self, min_decay: float = 0.1) -> int:
        """Remove memories with very low decay factor.

        These memories have been "forgotten" through disuse.
        """
        try:
            res = self.db.execute(
                """
                MATCH (m:Memory)
                WHERE m.decay_factor < $min_decay
                DELETE m
                RETURN count(m)
                """,
                {"min_decay": min_decay}
            )

            if res.has_next():
                return res.get_next()[0]
            return 0
        except Exception:
            return 0

    def get_relevant_memories(
        self,
        memory_type: MemoryType = None,
        limit: int = 20
    ) -> list[Memory]:
        """Get most relevant memories based on recency and access.

        Uses relevance scoring that combines:
        - Recency (when was it last accessed)
        - Frequency (how often accessed)
        - Decay (smart forgetting factor)
        """
        try:
            if memory_type:
                res = self.db.execute(
                    """
                    MATCH (m:Memory {memory_type: $type})
                    RETURN m.id, m.memory_type, m.content, m.created_at,
                           m.last_accessed, m.access_count, m.decay_factor
                    ORDER BY m.last_accessed DESC, m.access_count DESC
                    LIMIT $limit
                    """,
                    {"type": memory_type.value, "limit": limit * 2}
                )
            else:
                res = self.db.execute(
                    """
                    MATCH (m:Memory)
                    RETURN m.id, m.memory_type, m.content, m.created_at,
                           m.last_accessed, m.access_count, m.decay_factor
                    ORDER BY m.last_accessed DESC, m.access_count DESC
                    LIMIT $limit
                    """,
                    {"limit": limit * 2}
                )

            memories = []
            while res.has_next():
                row = res.get_next()
                memories.append(Memory(
                    id=row[0],
                    memory_type=MemoryType(row[1]),
                    content=row[2],
                    created_at=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
                    last_accessed=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                    access_count=row[5] or 1,
                    decay_factor=row[6] or 1.0
                ))

            # Sort by relevance score
            memories.sort(key=lambda m: m.relevance_score, reverse=True)
            return memories[:limit]

        except Exception:
            return []
