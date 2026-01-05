"""Orchestration module for Skills Fabric.

Implements the Ralph Wiggum autonomous loop methodology:
- Iteration over perfection
- Failures as data
- Completion promises as exit conditions

Key Components:
- RalphWiggumLoop: Core autonomous iteration loop
- CompletionPromise: Exit conditions for the loop
- FailureTracker: Learn from failures to adjust strategy
- AutonomousSkillFactory: Enhanced factory with Ralph Wiggum iteration
"""
from .ralph_wiggum import (
    RalphWiggumLoop,
    LoopResult,
    IterationResult,
    LoopStatus,
    run_with_retry,
)
from .completion_promise import (
    CompletionPromise,
    CompletionPromiseSet,
    PromiseResult,
    PromiseStatus,
    # Pre-built promises
    source_exists_promise,
    sandbox_passes_promise,
    proven_confidence_promise,
    no_hallucination_promise,
    skill_complete_promise,
    default_skill_promises,
)
from .failure_tracker import (
    FailureTracker,
    FailureRecord,
    FailureType,
    StrategyAdjustment,
)
from .autonomous_factory import (
    AutonomousSkillFactory,
    SkillGenerationResult,
    skill_generation_promises,
)

__all__ = [
    # Ralph Wiggum Loop
    "RalphWiggumLoop",
    "LoopResult",
    "IterationResult",
    "LoopStatus",
    "run_with_retry",
    # Completion Promises
    "CompletionPromise",
    "CompletionPromiseSet",
    "PromiseResult",
    "PromiseStatus",
    "source_exists_promise",
    "sandbox_passes_promise",
    "proven_confidence_promise",
    "no_hallucination_promise",
    "skill_complete_promise",
    "default_skill_promises",
    # Failure Tracking
    "FailureTracker",
    "FailureRecord",
    "FailureType",
    "StrategyAdjustment",
    # Autonomous Factory
    "AutonomousSkillFactory",
    "SkillGenerationResult",
    "skill_generation_promises",
]
