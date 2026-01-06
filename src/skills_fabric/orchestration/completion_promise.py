"""Completion Promise - Exit conditions for autonomous loops.

Based on Ralph Wiggum methodology: Define clear exit conditions
that must be met before the loop terminates successfully.

Trust Hierarchy Integration:
- Promises can enforce Trust Level requirements
- source_url_exists -> Trust Level 1 (HardContent)
- sandbox_passes -> Trust Level 2 (VerifiedSoft)
- No Trust Level 3 content -> Never accept ungrounded output
"""
from dataclasses import dataclass, field
from typing import Callable, TypeVar, Generic, Any
from enum import Enum

T = TypeVar('T')


class PromiseStatus(Enum):
    """Status of a completion promise check."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PromiseResult:
    """Result of checking a completion promise."""
    status: PromiseStatus
    message: str
    details: dict = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == PromiseStatus.PASSED


@dataclass
class CompletionPromise(Generic[T]):
    """A completion promise that must be met for loop exit.

    Combines description, check function, and optional metadata.

    Example:
        promise = CompletionPromise(
            name="source_exists",
            description="Source URL points to real file",
            check=lambda skill: os.path.exists(skill.source_url),
            trust_level=1
        )
    """
    name: str
    description: str
    check: Callable[[T], bool]
    trust_level: int = 2  # Default to VerifiedSoft level
    required: bool = True  # If False, failure is a warning not error
    error_message: str = None

    def evaluate(self, value: T) -> PromiseResult:
        """Evaluate the promise against a value."""
        try:
            passed = self.check(value)
            if passed:
                return PromiseResult(
                    status=PromiseStatus.PASSED,
                    message=f"✓ {self.name}: {self.description}",
                    details={"trust_level": self.trust_level}
                )
            else:
                return PromiseResult(
                    status=PromiseStatus.FAILED,
                    message=self.error_message or f"✗ {self.name}: {self.description}",
                    details={"trust_level": self.trust_level, "required": self.required}
                )
        except Exception as e:
            return PromiseResult(
                status=PromiseStatus.FAILED,
                message=f"✗ {self.name}: Check failed with error: {e}",
                details={"error": str(e), "trust_level": self.trust_level}
            )


@dataclass
class CompletionPromiseSet(Generic[T]):
    """A collection of promises that must all pass.

    Allows combining multiple exit conditions with AND/OR logic.
    """
    promises: list[CompletionPromise[T]] = field(default_factory=list)
    require_all: bool = True  # AND vs OR logic

    def add(self, promise: CompletionPromise[T]) -> "CompletionPromiseSet[T]":
        """Add a promise to the set."""
        self.promises.append(promise)
        return self

    def evaluate(self, value: T) -> tuple[bool, list[PromiseResult]]:
        """Evaluate all promises.

        Returns:
            Tuple of (all_passed, list of results)
        """
        results = [p.evaluate(value) for p in self.promises]

        if self.require_all:
            # AND logic: all required promises must pass
            required_results = [r for r, p in zip(results, self.promises) if p.required]
            all_passed = all(r.passed for r in required_results)
        else:
            # OR logic: at least one must pass
            all_passed = any(r.passed for r in results)

        return all_passed, results

    def describe(self) -> str:
        """Generate human-readable description."""
        joiner = " AND " if self.require_all else " OR "
        return joiner.join(p.description for p in self.promises)


# =============================================================================
# Pre-built Promise Factories
# =============================================================================

def source_exists_promise() -> CompletionPromise:
    """Promise: source_url points to an existing file.

    Trust Level 1 (HardContent) - Verifies real source code exists.
    """
    import os

    return CompletionPromise(
        name="source_exists",
        description="Source URL points to real file",
        check=lambda skill: hasattr(skill, 'source_url') and os.path.exists(skill.source_url),
        trust_level=1,
        required=True,
        error_message="Source file does not exist - cannot ground skill in code"
    )


def sandbox_passes_promise() -> CompletionPromise:
    """Promise: code executes successfully in sandbox.

    Trust Level 2 (VerifiedSoft) - Verifies code is executable.
    """
    return CompletionPromise(
        name="sandbox_passes",
        description="Code executes in sandbox without error",
        check=lambda skill: hasattr(skill, 'verified') and skill.verified,
        trust_level=2,
        required=True,
        error_message="Code failed sandbox execution"
    )


def proven_confidence_promise(min_confidence: float = 0.7) -> CompletionPromise:
    """Promise: PROVEN link has sufficient confidence.

    Trust Level 1-2 - Verifies doc-to-code link quality.
    """
    return CompletionPromise(
        name="proven_confidence",
        description=f"PROVEN link confidence >= {min_confidence}",
        check=lambda skill: (
            hasattr(skill, 'proven_confidence') and
            skill.proven_confidence >= min_confidence
        ),
        trust_level=2,
        required=True,
        error_message=f"PROVEN link confidence below {min_confidence}"
    )


def no_hallucination_promise() -> CompletionPromise:
    """Promise: No Trust Level 3 (unverified) content.

    This is the core zero-hallucination check.
    """
    return CompletionPromise(
        name="no_hallucination",
        description="No ungrounded/hallucinated content",
        check=lambda skill: not (hasattr(skill, 'has_unverified_content') and skill.has_unverified_content),
        trust_level=3,
        required=True,
        error_message="REJECTED: Contains ungrounded content (Trust Level 3)"
    )


def skill_complete_promise() -> CompletionPromise:
    """Promise: Skill has all required fields."""
    return CompletionPromise(
        name="skill_complete",
        description="Skill has question, code, and source_url",
        check=lambda skill: all([
            hasattr(skill, 'question') and skill.question,
            hasattr(skill, 'code') and skill.code,
            hasattr(skill, 'source_url') and skill.source_url,
        ]),
        trust_level=1,
        required=True,
        error_message="Skill missing required fields"
    )


def default_skill_promises() -> CompletionPromiseSet:
    """Default promise set for skill generation.

    Combines all standard verification checks.
    """
    return CompletionPromiseSet(
        promises=[
            skill_complete_promise(),
            source_exists_promise(),
            sandbox_passes_promise(),
            proven_confidence_promise(0.7),
            no_hallucination_promise(),
        ],
        require_all=True
    )
