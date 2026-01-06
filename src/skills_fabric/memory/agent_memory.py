#!/usr/bin/env python3
"""
Agent Memory Architecture for Coding Agents

Implements a 4-layer memory system based on 2026 research:

1. BEADS - Work Orchestration (Temporal Dependency Graph)
   - Task tracking with dependency edges
   - Ready-set computation for task selection
   - Git-backed durability

2. MIRIX - Agent Learning (6 Memory Types)
   - Core: Agent identity and preferences
   - Episodic: Time-stamped crawl sessions
   - Semantic: Abstract facts about code
   - Procedural: Learned workflows
   - Resource: Codebases, PRs, docs
   - Knowledge Vault: Sensitive state

3. ADK - Context Compilation (Multi-Agent)
   - Tiered storage (identity, session, working, memory, artifacts)
   - Compiled context pipeline
   - Efficient multi-agent handoff

4. COGNEE - Code Understanding (Knowledge Graph)
   - AST-based dependency extraction
   - Direct invocation analysis
   - Transitive closure queries

Research Sources:
- Beads: https://debugg.ai/resources/beads-memory-ai-coding-agents
- MIRIX: https://arxiv.org/html/2507.07957v1
- ADK: https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/
- Cognee: https://www.cognee.ai/blog/deep-dives/repo-to-knowledge-graph
"""

import json
import sqlite3
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set
from pathlib import Path
from datetime import datetime
from enum import Enum, auto
import uuid


# =============================================================================
# BEADS: Work Orchestration Layer
# =============================================================================

class BeadStatus(Enum):
    """Status of a work bead."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class BeadPriority(Enum):
    """Priority levels for beads."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Bead:
    """
    A single unit of work in the temporal dependency graph.

    Based on Beads pattern for coding agents:
    - Explicit dependency edges (blocks/blocked_by)
    - Causal discovery path (discovered_from)
    - Append-only event trail
    """
    id: str
    title: str
    status: BeadStatus
    priority: BeadPriority = BeadPriority.MEDIUM

    # Content
    description: str = ""
    labels: List[str] = field(default_factory=list)

    # Dependencies
    blocks: List[str] = field(default_factory=list)  # IDs this bead blocks
    blocked_by: List[str] = field(default_factory=list)  # IDs blocking this bead
    discovered_from: Optional[str] = None  # Parent bead that discovered this

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assignee: Optional[str] = None

    # Events trail (append-only)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict."""
        d = asdict(self)
        d["status"] = self.status.value
        d["priority"] = self.priority.value
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Bead":
        """Create from dict."""
        d["status"] = BeadStatus(d["status"])
        d["priority"] = BeadPriority(d["priority"])
        d["created_at"] = datetime.fromisoformat(d["created_at"])
        d["updated_at"] = datetime.fromisoformat(d["updated_at"])
        return cls(**d)

    def add_event(self, event_type: str, data: Dict[str, Any] = None):
        """Add an event to the trail."""
        self.events.append({
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        })
        self.updated_at = datetime.now()


class BeadsStore:
    """
    Git-backed work queue with dependency tracking.

    Key capability: Ready-set computation
    - Returns tasks with no open blocked_by edges
    - Agents query ready set at session start
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.beads_file = self.storage_path / "beads.jsonl"
        self.cache_db = self.storage_path / "beads_cache.db"

        # Initialize SQLite cache for fast queries
        self._init_cache()

        # Load existing beads
        self.beads: Dict[str, Bead] = {}
        self._load_beads()

    def _init_cache(self):
        """Initialize SQLite cache for fast queries."""
        conn = sqlite3.connect(self.cache_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS beads (
                id TEXT PRIMARY KEY,
                title TEXT,
                status TEXT,
                priority INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                bead_id TEXT,
                blocks_id TEXT,
                FOREIGN KEY (bead_id) REFERENCES beads(id)
            )
        """)
        conn.commit()
        conn.close()

    def _load_beads(self):
        """Load beads from JSONL file."""
        if not self.beads_file.exists():
            return

        with open(self.beads_file, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    bead = Bead.from_dict(data)
                    self.beads[bead.id] = bead

    def _save_bead(self, bead: Bead):
        """Append bead to JSONL file."""
        with open(self.beads_file, "a") as f:
            f.write(json.dumps(bead.to_dict()) + "\n")

        # Update cache
        conn = sqlite3.connect(self.cache_db)
        conn.execute("""
            INSERT OR REPLACE INTO beads VALUES (?, ?, ?, ?, ?, ?)
        """, (
            bead.id, bead.title, bead.status.value,
            bead.priority.value, bead.created_at.isoformat(),
            bead.updated_at.isoformat()
        ))

        # Update dependencies
        conn.execute("DELETE FROM dependencies WHERE bead_id = ?", (bead.id,))
        for blocks_id in bead.blocks:
            conn.execute(
                "INSERT INTO dependencies VALUES (?, ?)",
                (bead.id, blocks_id)
            )

        conn.commit()
        conn.close()

    def create(
        self,
        title: str,
        description: str = "",
        priority: BeadPriority = BeadPriority.MEDIUM,
        labels: List[str] = None,
        discovered_from: str = None,
        blocked_by: List[str] = None,
    ) -> Bead:
        """Create a new bead."""
        bead_id = str(uuid.uuid4())[:8]

        bead = Bead(
            id=bead_id,
            title=title,
            description=description,
            status=BeadStatus.OPEN,
            priority=priority,
            labels=labels or [],
            discovered_from=discovered_from,
            blocked_by=blocked_by or [],
        )

        bead.add_event("created", {"title": title})

        # Update blocks relationships
        for blocked_id in bead.blocked_by:
            if blocked_id in self.beads:
                self.beads[blocked_id].blocks.append(bead_id)

        self.beads[bead_id] = bead
        self._save_bead(bead)

        return bead

    def update_status(self, bead_id: str, status: BeadStatus):
        """Update bead status."""
        if bead_id not in self.beads:
            raise KeyError(f"Bead {bead_id} not found")

        bead = self.beads[bead_id]
        old_status = bead.status
        bead.status = status
        bead.add_event("status_changed", {
            "from": old_status.value,
            "to": status.value
        })
        self._save_bead(bead)

    def get_ready_set(self) -> List[Bead]:
        """
        Get all beads ready for work.

        Ready = status in {OPEN} AND no open blocked_by edges
        """
        ready = []

        for bead in self.beads.values():
            if bead.status != BeadStatus.OPEN:
                continue

            # Check if any blocking beads are not done
            blocked = False
            for blocked_by_id in bead.blocked_by:
                if blocked_by_id in self.beads:
                    if self.beads[blocked_by_id].status != BeadStatus.DONE:
                        blocked = True
                        break

            if not blocked:
                ready.append(bead)

        # Sort by priority, then by creation date
        ready.sort(key=lambda b: (b.priority.value, b.created_at))

        return ready

    def select_next(self) -> Optional[Bead]:
        """Select the highest priority ready bead."""
        ready = self.get_ready_set()
        return ready[0] if ready else None

    def get_discovery_tree(self, bead_id: str) -> Dict[str, Any]:
        """Get the discovery tree rooted at a bead."""
        if bead_id not in self.beads:
            return {}

        bead = self.beads[bead_id]
        children = [
            self.get_discovery_tree(b.id)
            for b in self.beads.values()
            if b.discovered_from == bead_id
        ]

        return {
            "id": bead.id,
            "title": bead.title,
            "status": bead.status.value,
            "children": children
        }


# =============================================================================
# MIRIX: Agent Learning Layer (6 Memory Types)
# =============================================================================

class MemoryType(Enum):
    """MIRIX memory types for agent learning."""
    CORE = "core"           # Agent identity and preferences
    EPISODIC = "episodic"   # Time-stamped crawl sessions
    SEMANTIC = "semantic"   # Abstract facts about code
    PROCEDURAL = "procedural"  # Learned workflows
    RESOURCE = "resource"   # Codebases, PRs, docs
    KNOWLEDGE_VAULT = "vault"  # Sensitive state


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    memory_type: MemoryType
    content: str
    topic: str  # For retrieval
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["memory_type"] = self.memory_type.value
        d["timestamp"] = self.timestamp.isoformat()
        return d


class MIRIXMemory:
    """
    Multi-type memory system for agent learning.

    Based on MIRIX architecture:
    - 6 specialized memory types
    - Active retrieval by topic
    - Cross-memory search
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Separate storage per memory type
        self.memories: Dict[MemoryType, Dict[str, MemoryEntry]] = {
            mt: {} for mt in MemoryType
        }

        self._load_memories()

    def _load_memories(self):
        """Load memories from storage."""
        for memory_type in MemoryType:
            file_path = self.storage_path / f"{memory_type.value}.jsonl"
            if file_path.exists():
                with open(file_path, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            data["memory_type"] = MemoryType(data["memory_type"])
                            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                            entry = MemoryEntry(**data)
                            self.memories[memory_type][entry.id] = entry

    def _save_entry(self, entry: MemoryEntry):
        """Save a memory entry."""
        file_path = self.storage_path / f"{entry.memory_type.value}.jsonl"
        with open(file_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def add(
        self,
        memory_type: MemoryType,
        content: str,
        topic: str,
        metadata: Dict[str, Any] = None,
    ) -> MemoryEntry:
        """Add a new memory entry."""
        entry_id = hashlib.md5(
            f"{memory_type.value}:{topic}:{content[:50]}".encode()
        ).hexdigest()[:12]

        entry = MemoryEntry(
            id=entry_id,
            memory_type=memory_type,
            content=content,
            topic=topic,
            metadata=metadata or {},
        )

        self.memories[memory_type][entry_id] = entry
        self._save_entry(entry)

        return entry

    def retrieve_by_topic(
        self,
        topic: str,
        memory_types: List[MemoryType] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """
        Retrieve memories by topic (active retrieval).

        Searches across specified memory types (or all).
        """
        if memory_types is None:
            memory_types = list(MemoryType)

        results = []

        for mt in memory_types:
            for entry in self.memories[mt].values():
                # Simple topic matching (could be enhanced with embeddings)
                if topic.lower() in entry.topic.lower():
                    results.append(entry)
                elif topic.lower() in entry.content.lower():
                    results.append(entry)

        # Sort by timestamp (most recent first)
        results.sort(key=lambda e: e.timestamp, reverse=True)

        return results[:limit]

    # Convenience methods for specific memory types

    def add_episodic(self, session_id: str, content: str, metadata: Dict = None):
        """Add an episodic memory (crawl session)."""
        return self.add(
            MemoryType.EPISODIC,
            content,
            topic=session_id,
            metadata={**(metadata or {}), "session_id": session_id}
        )

    def add_semantic(self, fact: str, topic: str):
        """Add a semantic memory (abstract fact)."""
        return self.add(MemoryType.SEMANTIC, fact, topic=topic)

    def add_procedural(self, workflow: str, task_type: str):
        """Add a procedural memory (learned workflow)."""
        return self.add(MemoryType.PROCEDURAL, workflow, topic=task_type)

    def get_agent_context(self, topic: str) -> str:
        """
        Get formatted context for agent prompt injection.

        Retrieves from all 6 memory types and formats for LLM.
        """
        memories = self.retrieve_by_topic(topic, limit=20)

        if not memories:
            return ""

        sections = []

        # Group by type
        by_type: Dict[MemoryType, List[MemoryEntry]] = {}
        for mem in memories:
            if mem.memory_type not in by_type:
                by_type[mem.memory_type] = []
            by_type[mem.memory_type].append(mem)

        for mt, entries in by_type.items():
            section = f"<{mt.value}_memories>\n"
            for entry in entries[:5]:
                section += f"- {entry.content}\n"
            section += f"</{mt.value}_memories>"
            sections.append(section)

        return "\n\n".join(sections)


# =============================================================================
# ADK: Context Compilation Layer
# =============================================================================

class ContextTier(Enum):
    """ADK context tiers."""
    IDENTITY = "identity"       # Agent persona, instructions
    SESSION = "session"         # Metadata, state, events
    WORKING = "working"         # Ephemeral, rebuilt per call
    MEMORY = "memory"           # Long-term searchable
    ARTIFACTS = "artifacts"     # Large objects (PRs, codebases)


@dataclass
class ContextBlock:
    """A block of context."""
    tier: ContextTier
    key: str
    content: str
    priority: int = 0  # Higher = more important
    token_estimate: int = 0


@dataclass
class CompiledContext:
    """Compiled context ready for LLM."""
    blocks: List[ContextBlock]
    total_tokens: int
    truncated: bool = False


class ADKContextManager:
    """
    Context compilation for multi-agent systems.

    Based on Google ADK architecture:
    - Tiered storage (separation of storage from presentation)
    - Compiled context pipeline
    - Efficient multi-agent handoff
    """

    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens

        # Storage by tier
        self.storage: Dict[ContextTier, Dict[str, ContextBlock]] = {
            tier: {} for tier in ContextTier
        }

        # Artifact handles (loaded on demand)
        self.artifact_handles: Dict[str, Path] = {}

    def add_identity(self, key: str, content: str, priority: int = 100):
        """Add identity context (always included)."""
        self._add_block(ContextTier.IDENTITY, key, content, priority)

    def add_session(self, key: str, content: str, priority: int = 50):
        """Add session context."""
        self._add_block(ContextTier.SESSION, key, content, priority)

    def add_working(self, key: str, content: str, priority: int = 30):
        """Add working context (ephemeral)."""
        self._add_block(ContextTier.WORKING, key, content, priority)

    def add_memory(self, key: str, content: str, priority: int = 20):
        """Add memory context."""
        self._add_block(ContextTier.MEMORY, key, content, priority)

    def register_artifact(self, key: str, path: Path):
        """Register artifact handle (loaded on demand)."""
        self.artifact_handles[key] = path

    def load_artifact(self, key: str) -> Optional[str]:
        """Load artifact content."""
        if key not in self.artifact_handles:
            return None

        path = self.artifact_handles[key]
        if path.exists():
            return path.read_text()
        return None

    def _add_block(self, tier: ContextTier, key: str, content: str, priority: int):
        """Add a context block."""
        # Rough token estimate: 4 chars per token
        token_estimate = len(content) // 4

        block = ContextBlock(
            tier=tier,
            key=key,
            content=content,
            priority=priority,
            token_estimate=token_estimate
        )

        self.storage[tier][key] = block

    def compile(
        self,
        include_tiers: List[ContextTier] = None,
        max_tokens: int = None,
    ) -> CompiledContext:
        """
        Compile context for LLM call.

        Returns blocks sorted by priority, truncated if needed.
        """
        if include_tiers is None:
            include_tiers = list(ContextTier)

        if max_tokens is None:
            max_tokens = self.max_tokens

        # Gather all blocks from requested tiers
        blocks = []
        for tier in include_tiers:
            blocks.extend(self.storage[tier].values())

        # Sort by priority (highest first)
        blocks.sort(key=lambda b: b.priority, reverse=True)

        # Truncate to fit token limit
        selected = []
        total_tokens = 0
        truncated = False

        for block in blocks:
            if total_tokens + block.token_estimate <= max_tokens:
                selected.append(block)
                total_tokens += block.token_estimate
            else:
                truncated = True

        return CompiledContext(
            blocks=selected,
            total_tokens=total_tokens,
            truncated=truncated
        )

    def compile_for_subagent(
        self,
        task_description: str,
        include_recent_artifacts: int = 2,
    ) -> CompiledContext:
        """
        Compile scoped context for sub-agent handoff.

        Prevents token explosion in multi-agent systems.
        """
        # Sub-agents get: identity + task + limited session
        self.add_working("task", task_description, priority=100)

        # Include only most recent artifacts
        artifact_keys = list(self.artifact_handles.keys())[-include_recent_artifacts:]

        for key in artifact_keys:
            content = self.load_artifact(key)
            if content:
                # Truncate large artifacts
                if len(content) > 10000:
                    content = content[:10000] + "\n... [truncated]"
                self.add_working(f"artifact_{key}", content, priority=10)

        return self.compile(
            include_tiers=[ContextTier.IDENTITY, ContextTier.WORKING],
            max_tokens=50000  # Smaller budget for sub-agents
        )

    def to_prompt(self, compiled: CompiledContext) -> str:
        """Convert compiled context to prompt string."""
        sections = []

        for block in compiled.blocks:
            sections.append(f"<{block.tier.value}:{block.key}>\n{block.content}\n</{block.tier.value}:{block.key}>")

        return "\n\n".join(sections)


# =============================================================================
# INTEGRATED AGENT MEMORY SYSTEM
# =============================================================================

class AgentMemorySystem:
    """
    Integrated 4-layer memory system for coding agents.

    Combines:
    - Beads: Work orchestration
    - MIRIX: Agent learning (6 types)
    - ADK: Context compilation
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize layers
        self.beads = BeadsStore(storage_path / "beads")
        self.mirix = MIRIXMemory(storage_path / "mirix")
        self.adk = ADKContextManager()

        # Set up identity
        self.adk.add_identity("system", """
You are a coding agent with access to a 4-layer memory system:
1. Beads: Track work items and dependencies
2. MIRIX: Learn from past sessions (episodic, semantic, procedural)
3. ADK: Efficient context management
4. Cognee: Code knowledge graph (if available)

Use these systems to avoid re-discovering work and to learn from experience.
""")

    def start_session(self, session_id: str, task: str):
        """Start a new work session."""
        # Log to episodic memory
        self.mirix.add_episodic(
            session_id,
            f"Session started: {task}",
            {"task": task}
        )

        # Add to ADK session context
        self.adk.add_session("current_task", task)

        # Get ready beads
        ready = self.beads.get_ready_set()
        if ready:
            ready_str = "\n".join([f"- [{b.id}] {b.title}" for b in ready[:5]])
            self.adk.add_session("ready_beads", f"Ready work items:\n{ready_str}")

        # Inject relevant memories
        memories = self.mirix.get_agent_context(task)
        if memories:
            self.adk.add_memory("relevant_memories", memories)

    def end_session(self, session_id: str, summary: str):
        """End a work session."""
        self.mirix.add_episodic(
            session_id,
            f"Session ended: {summary}",
            {"summary": summary}
        )

    def discover_work(
        self,
        title: str,
        description: str = "",
        parent_bead: str = None,
    ) -> Bead:
        """Discover new work during a session."""
        bead = self.beads.create(
            title=title,
            description=description,
            discovered_from=parent_bead,
            blocked_by=[parent_bead] if parent_bead else [],
        )

        # Log discovery
        self.mirix.add_episodic(
            "work_discovery",
            f"Discovered: {title} (from {parent_bead})",
            {"bead_id": bead.id, "parent": parent_bead}
        )

        return bead

    def complete_work(self, bead_id: str, learnings: str = None):
        """Complete a work item."""
        self.beads.update_status(bead_id, BeadStatus.DONE)

        if learnings:
            # Store as procedural memory
            bead = self.beads.beads.get(bead_id)
            if bead:
                self.mirix.add_procedural(
                    learnings,
                    task_type=bead.labels[0] if bead.labels else "general"
                )

    def get_context_for_task(self, task: str) -> str:
        """Get compiled context for a task."""
        # Add task to working context
        self.adk.add_working("current_task", task, priority=100)

        # Compile and return
        compiled = self.adk.compile()
        return self.adk.to_prompt(compiled)

    def get_status(self) -> Dict[str, Any]:
        """Get memory system status."""
        return {
            "beads": {
                "total": len(self.beads.beads),
                "ready": len(self.beads.get_ready_set()),
                "in_progress": len([
                    b for b in self.beads.beads.values()
                    if b.status == BeadStatus.IN_PROGRESS
                ]),
                "done": len([
                    b for b in self.beads.beads.values()
                    if b.status == BeadStatus.DONE
                ]),
            },
            "mirix": {
                mt.value: len(self.mirix.memories[mt])
                for mt in MemoryType
            },
            "adk": {
                "context_blocks": sum(
                    len(blocks) for blocks in self.adk.storage.values()
                ),
                "artifacts": len(self.adk.artifact_handles),
            }
        }


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate the agent memory system."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Path(tmpdir)

        print("=" * 60)
        print("Agent Memory System Demo")
        print("=" * 60)

        # Initialize
        memory = AgentMemorySystem(storage)

        # Start session
        print("\n1. Starting session...")
        memory.start_session("session_001", "Update LangGraph dependency tree")

        # Create initial work
        print("\n2. Creating work items...")
        parent = memory.discover_work(
            "Update requests library across repo",
            description="requests 3.0 has breaking changes"
        )
        print(f"   Created: [{parent.id}] {parent.title}")

        # Discover child work
        child1 = memory.discover_work(
            "Update requests in auth module",
            parent_bead=parent.id
        )
        print(f"   Discovered: [{child1.id}] {child1.title}")

        child2 = memory.discover_work(
            "Update requests in utils module",
            parent_bead=parent.id
        )
        print(f"   Discovered: [{child2.id}] {child2.title}")

        # Check ready set
        print("\n3. Ready set (work not blocked):")
        ready = memory.beads.get_ready_set()
        for bead in ready:
            print(f"   - [{bead.id}] {bead.title}")

        # Complete child work
        print("\n4. Completing child work...")
        memory.complete_work(
            child1.id,
            learnings="When updating requests, check for Session API changes first"
        )
        memory.complete_work(child2.id)

        # Check ready set again
        print("\n5. Ready set after completing children:")
        ready = memory.beads.get_ready_set()
        for bead in ready:
            print(f"   - [{bead.id}] {bead.title}")

        # Add semantic memory
        print("\n6. Adding semantic memory...")
        memory.mirix.add_semantic(
            "requests 3.0 deprecated Session.get() in favor of Session.request()",
            topic="requests library"
        )

        # Get context for new task
        print("\n7. Getting context for related task:")
        context = memory.get_context_for_task("Update HTTP client library")
        print(f"   Context length: {len(context)} chars")
        print(f"   Preview: {context[:200]}...")

        # Status
        print("\n8. Memory system status:")
        status = memory.get_status()
        print(f"   Beads: {status['beads']}")
        print(f"   MIRIX: {status['mirix']}")
        print(f"   ADK: {status['adk']}")

        # End session
        memory.end_session("session_001", "Updated 2 modules, 1 parent task ready")

        print("\n" + "=" * 60)
        print("Demo complete!")
        print("=" * 60)


if __name__ == "__main__":
    demo()
