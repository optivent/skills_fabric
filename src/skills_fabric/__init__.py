"""Skills Fabric - Zero-Hallucination Claude Skill Generation Pipeline.

A comprehensive system for generating Claude skills that are fully grounded
in verified source code, implementing the Miessler-aligned PAI Trust Hierarchy.

Core Principles:
- Zero Hallucination: Never trust LLM output unless grounded in verified source code
- Trust Hierarchy: HardContent (100%) > VerifiedSoft (95%) > Unverified (REJECTED)
- BMAD C.O.R.E.: Collaboration, Optimized, Reflection, Engine

Key Modules:
- core: Database, configuration, exception hierarchy
- trust: Trust hierarchy verification (HardContent, VerifiedSoft)
- orchestration: Ralph Wiggum autonomous loop, completion promises
- generate: Skill factory with LangGraph orchestration
- verify: Sandbox execution, cross-layer verification
- ingest: Source code and documentation ingestion
- link: PROVEN doc-to-code linking
- store: KuzuDB skill storage

Quick Start:
    from skills_fabric.orchestration import AutonomousSkillFactory

    factory = AutonomousSkillFactory()
    result = factory.generate("langgraph", max_iterations=10)

    if result.success:
        print(f"Generated {result.value.skills_created} skills")
"""

__version__ = "0.2.0"
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
]
