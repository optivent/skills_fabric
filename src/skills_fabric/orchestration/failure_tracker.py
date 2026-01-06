"""Failure Tracker - Learn from failures to adjust strategy.

Based on Ralph Wiggum philosophy: "Failures are data."

Each failed iteration provides information that can be used to:
1. Adjust search strategy (deeper, broader, different sources)
2. Modify generation parameters
3. Change verification approach
4. Report patterns to operators

BMAD Integration:
- Reflection: Analyze failures before next attempt
- Optimized: Use failure data to improve, not just retry
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
from enum import Enum
from collections import Counter


class FailureType(Enum):
    """Categories of failures for pattern analysis."""
    SOURCE_NOT_FOUND = "source_not_found"
    SANDBOX_FAILED = "sandbox_failed"
    LOW_CONFIDENCE = "low_confidence"
    HALLUCINATION = "hallucination"
    TIMEOUT = "timeout"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


@dataclass
class FailureRecord:
    """Record of a single failure."""
    iteration: int
    failure_type: FailureType
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict = field(default_factory=dict)
    value: Any = None  # The failed result, if available

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "iteration": self.iteration,
            "failure_type": self.failure_type.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class StrategyAdjustment:
    """Recommended adjustment based on failure analysis."""
    parameter: str
    old_value: Any
    new_value: Any
    reason: str


class FailureTracker:
    """Track and analyze failures to inform strategy adjustments.

    Key Features:
    - Categorize failures by type
    - Identify patterns (same failure repeating)
    - Recommend strategy adjustments
    - Report to operators

    Example:
        tracker = FailureTracker()
        tracker.record(FailureRecord(
            iteration=1,
            failure_type=FailureType.SOURCE_NOT_FOUND,
            message="File not found: langgraph/state.py"
        ))

        adjustments = tracker.suggest_adjustments()
        # -> [StrategyAdjustment(parameter="search_depth", old=1, new=2, reason="...")]
    """

    def __init__(self):
        self.failures: list[FailureRecord] = []
        self.current_strategy: dict = {
            "search_depth": 1,
            "require_exact_match": False,
            "fallback_to_ast": False,
            "timeout_seconds": 10,
            "retry_external_services": True,
            "min_confidence": 0.7,
        }

    def record(self, failure: FailureRecord) -> None:
        """Record a new failure."""
        self.failures.append(failure)

    def record_from_exception(
        self,
        iteration: int,
        exception: Exception,
        value: Any = None
    ) -> FailureRecord:
        """Create and record a failure from an exception."""
        failure_type = self._classify_exception(exception)
        record = FailureRecord(
            iteration=iteration,
            failure_type=failure_type,
            message=str(exception),
            details={"exception_type": type(exception).__name__},
            value=value
        )
        self.record(record)
        return record

    def _classify_exception(self, exc: Exception) -> FailureType:
        """Classify exception into failure type."""
        from ..core.exceptions import (
            ValidationError, VerificationError, HallucinationError,
            SandboxError, ExternalServiceError
        )

        if isinstance(exc, ValidationError):
            return FailureType.SOURCE_NOT_FOUND
        elif isinstance(exc, SandboxError):
            return FailureType.SANDBOX_FAILED
        elif isinstance(exc, HallucinationError):
            return FailureType.HALLUCINATION
        elif isinstance(exc, ExternalServiceError):
            return FailureType.EXTERNAL_SERVICE
        elif "timeout" in str(exc).lower():
            return FailureType.TIMEOUT
        else:
            return FailureType.UNKNOWN

    def get_failure_counts(self) -> Counter:
        """Get counts of each failure type."""
        return Counter(f.failure_type for f in self.failures)

    def get_dominant_failure(self) -> Optional[FailureType]:
        """Get the most common failure type."""
        counts = self.get_failure_counts()
        if counts:
            return counts.most_common(1)[0][0]
        return None

    def suggest_adjustments(self) -> list[StrategyAdjustment]:
        """Analyze failures and suggest strategy adjustments.

        BMAD Principle: Use failure data to improve strategy.
        """
        adjustments = []
        counts = self.get_failure_counts()

        # Pattern: Repeated source not found -> increase search depth
        if counts[FailureType.SOURCE_NOT_FOUND] >= 2:
            new_depth = min(5, self.current_strategy["search_depth"] + 1)
            if new_depth != self.current_strategy["search_depth"]:
                adjustments.append(StrategyAdjustment(
                    parameter="search_depth",
                    old_value=self.current_strategy["search_depth"],
                    new_value=new_depth,
                    reason=f"{counts[FailureType.SOURCE_NOT_FOUND]} source-not-found failures"
                ))
                self.current_strategy["search_depth"] = new_depth

        # Pattern: Sandbox failures -> maybe try AST-only extraction
        if counts[FailureType.SANDBOX_FAILED] >= 3:
            if not self.current_strategy["fallback_to_ast"]:
                adjustments.append(StrategyAdjustment(
                    parameter="fallback_to_ast",
                    old_value=False,
                    new_value=True,
                    reason=f"{counts[FailureType.SANDBOX_FAILED]} sandbox failures"
                ))
                self.current_strategy["fallback_to_ast"] = True

        # Pattern: Low confidence -> require exact match
        if counts[FailureType.LOW_CONFIDENCE] >= 2:
            if not self.current_strategy["require_exact_match"]:
                adjustments.append(StrategyAdjustment(
                    parameter="require_exact_match",
                    old_value=False,
                    new_value=True,
                    reason=f"{counts[FailureType.LOW_CONFIDENCE]} low-confidence failures"
                ))
                self.current_strategy["require_exact_match"] = True

        # Pattern: Timeouts -> increase timeout
        if counts[FailureType.TIMEOUT] >= 2:
            new_timeout = min(60, self.current_strategy["timeout_seconds"] * 2)
            if new_timeout != self.current_strategy["timeout_seconds"]:
                adjustments.append(StrategyAdjustment(
                    parameter="timeout_seconds",
                    old_value=self.current_strategy["timeout_seconds"],
                    new_value=new_timeout,
                    reason=f"{counts[FailureType.TIMEOUT]} timeout failures"
                ))
                self.current_strategy["timeout_seconds"] = new_timeout

        # Pattern: External service failures -> disable retries
        if counts[FailureType.EXTERNAL_SERVICE] >= 3:
            if self.current_strategy["retry_external_services"]:
                adjustments.append(StrategyAdjustment(
                    parameter="retry_external_services",
                    old_value=True,
                    new_value=False,
                    reason=f"{counts[FailureType.EXTERNAL_SERVICE]} external service failures"
                ))
                self.current_strategy["retry_external_services"] = False

        return adjustments

    def get_adjusted_strategy(self) -> dict:
        """Get current strategy with all adjustments applied."""
        self.suggest_adjustments()  # Apply any pending adjustments
        return self.current_strategy.copy()

    def generate_report(self) -> str:
        """Generate human-readable failure report.

        BMAD Principle: Report honestly - gaps are findings.
        """
        lines = [
            "=" * 60,
            "FAILURE ANALYSIS REPORT",
            "=" * 60,
            "",
            f"Total Failures: {len(self.failures)}",
            "",
            "Failure Type Breakdown:",
        ]

        counts = self.get_failure_counts()
        for failure_type, count in counts.most_common():
            lines.append(f"  - {failure_type.value}: {count}")

        lines.extend([
            "",
            "Strategy Adjustments Made:",
        ])

        adjustments = self.suggest_adjustments()
        if adjustments:
            for adj in adjustments:
                lines.append(f"  - {adj.parameter}: {adj.old_value} -> {adj.new_value}")
                lines.append(f"    Reason: {adj.reason}")
        else:
            lines.append("  (none)")

        lines.extend([
            "",
            "Current Strategy:",
        ])
        for param, value in self.current_strategy.items():
            lines.append(f"  - {param}: {value}")

        lines.extend([
            "",
            "=" * 60,
        ])

        return "\n".join(lines)

    def reset(self) -> None:
        """Reset tracker state."""
        self.failures = []
        self.current_strategy = {
            "search_depth": 1,
            "require_exact_match": False,
            "fallback_to_ast": False,
            "timeout_seconds": 10,
            "retry_external_services": True,
            "min_confidence": 0.7,
        }
