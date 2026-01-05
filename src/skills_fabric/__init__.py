"""Skills Fabric - Zero-Hallucination Claude Skill Generation Pipeline.

A comprehensive system for generating Claude skills that are fully grounded
in verified source code, implementing the Miessler-aligned PAI Trust Hierarchy.

Core Principles:
- Zero Hallucination: Never trust LLM output unless grounded in verified source code
- Trust Hierarchy: HardContent (100%) > VerifiedSoft (95%) > Unverified (REJECTED)
- BMAD C.O.R.E.: Collaboration, Optimized, Reflection, Engine
- Ralph Wiggum Loop: Autonomous iteration until completion promises are met

Key Modules:
- core: Database, configuration, exception hierarchy
- trust: Trust hierarchy verification (HardContent, VerifiedSoft, cross-layer)
- orchestration: Ralph Wiggum autonomous loop, completion promises
- agents: Multi-agent orchestration (Supervisor, Miner, Linker, Verifier, Writer)
- memory: Supermemory-style persistent knowledge graph
- patterns: Fabric pattern library (IDENTITY → STEPS → OUTPUT → CONSTRAINTS)
- intelligence: Code embeddings, call graph analysis
- observability: Metrics, structured logging, distributed tracing
- generate: Skill factory with LangGraph orchestration
- verify: Sandbox execution, cross-layer verification
- ingest: Source code and documentation ingestion (GitClone + CodeWiki)
- link: PROVEN doc-to-code linking
- store: KuzuDB skill storage

Quick Start:
    from skills_fabric import AutonomousSkillFactory, TrustLevel

    factory = AutonomousSkillFactory()
    result = factory.generate("langgraph", max_iterations=10)

    if result.success:
        print(f"Generated {result.value.skills_created} skills")

Advanced Usage:
    from skills_fabric.agents import SupervisorAgent
    from skills_fabric.memory import KnowledgeGraph, SemanticSearch
    from skills_fabric.patterns import PatternExecutor, PatternRegistry
    from skills_fabric.intelligence import CodeSimilaritySearch, CallGraph
    from skills_fabric.observability import SkillsMetrics, SkillsLogger
"""

__version__ = "0.3.0"
__author__ = "Skills Fabric Team"

# Core exports
from .core import db, KuzuDatabase
from .core.exceptions import SkillsFabricError

# Trust hierarchy
from .trust import (
    TrustLevel,
    verify_skill_trust,
    quick_trust_check,
)

# Orchestration
from .orchestration import (
    RalphWiggumLoop,
    AutonomousSkillFactory,
    run_with_retry,
)

# Agents
from .agents import (
    SupervisorAgent,
    AgentRole,
)

# Memory
from .memory import (
    KnowledgeGraph,
    SemanticSearch,
)

# Patterns
from .patterns import (
    PatternExecutor,
    PatternRegistry,
)

# Intelligence
from .intelligence import (
    CodeSimilaritySearch,
    CallGraph,
)

# Observability
from .observability import (
    SkillsMetrics,
    SkillsLogger,
    configure_logging,
)

# Ingest
from .ingest import (
    GitCloner,
    CodeWikiCrawler,
    IntegratedIngestor,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "db",
    "KuzuDatabase",
    "SkillsFabricError",
    # Trust
    "TrustLevel",
    "verify_skill_trust",
    "quick_trust_check",
    # Orchestration
    "RalphWiggumLoop",
    "AutonomousSkillFactory",
    "run_with_retry",
    # Agents
    "SupervisorAgent",
    "AgentRole",
    # Memory
    "KnowledgeGraph",
    "SemanticSearch",
    # Patterns
    "PatternExecutor",
    "PatternRegistry",
    # Intelligence
    "CodeSimilaritySearch",
    "CallGraph",
    # Observability
    "SkillsMetrics",
    "SkillsLogger",
    "configure_logging",
    # Ingest
    "GitCloner",
    "CodeWikiCrawler",
    "IntegratedIngestor",
]
