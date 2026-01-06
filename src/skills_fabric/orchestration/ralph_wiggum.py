"""Ralph Wiggum Autonomous Loop.

Implementation of the Ralph Wiggum methodology for Skills Fabric:
- Iteration over perfection
- Failures as data
- Completion promises as exit conditions

Core Pattern:
    while not completion_promise_met:
        result = attempt_task()
        if result.failed:
            failures.append(result)
            adjust_strategy(failures)
        iterations += 1
        if iterations > max_iterations:
            escalate_to_human()

Integration with Trust Hierarchy:
- Each iteration produces a result that is verified against the Trust Hierarchy
- Trust Level 3 (Unverified) content is ALWAYS rejected
- Loop continues until Trust Level 1-2 requirements are met

BMAD C.O.R.E. Integration:
- Collaboration: Escalate to human when max iterations reached
- Optimized: No arbitrary limits on retries (configurable max)
- Reflection: Analyze failures before each retry
- Engine: Systematic loop with clear exit conditions
"""
from dataclasses import dataclass, field
from typing import Callable, TypeVar, Generic, Optional, Any
from datetime import datetime
from enum import Enum

from .completion_promise import CompletionPromise, CompletionPromiseSet, PromiseResult
from .failure_tracker import FailureTracker, FailureRecord, FailureType
from ..core.exceptions import MaxIterationsExceeded, CompletionPromiseNotMet

T = TypeVar('T')


class LoopStatus(Enum):
    """Status of the Ralph Wiggum loop."""
    RUNNING = "running"
    SUCCESS = "success"
    MAX_ITERATIONS = "max_iterations"
    ABORTED = "aborted"


@dataclass
class IterationResult(Generic[T]):
    """Result of a single iteration."""
    iteration: int
    value: Optional[T]
    success: bool
    promise_results: list[PromiseResult] = field(default_factory=list)
    error: Optional[Exception] = None
    duration_ms: float = 0.0
    strategy: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/storage."""
        return {
            "iteration": self.iteration,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "promise_results": [
                {"status": pr.status.value, "message": pr.message}
                for pr in self.promise_results
            ],
            "error": str(self.error) if self.error else None,
            "strategy": self.strategy,
        }


@dataclass
class LoopResult(Generic[T]):
    """Final result of the Ralph Wiggum loop."""
    status: LoopStatus
    value: Optional[T]
    total_iterations: int
    successful_iteration: Optional[int]
    all_iterations: list[IterationResult[T]]
    final_strategy: dict
    failure_report: str

    @property
    def success(self) -> bool:
        return self.status == LoopStatus.SUCCESS


class RalphWiggumLoop(Generic[T]):
    """Autonomous iteration loop with completion promises.

    Philosophy:
    - Iteration over perfection: Keep trying until it works
    - Failures as data: Each failure informs the next attempt
    - Operator skill matters: Quality of the task function matters

    Example:
        loop = RalphWiggumLoop(
            max_iterations=10,
            promises=default_skill_promises()
        )

        result = loop.run(
            task=lambda strategy: generate_skill(topic, strategy),
            on_iteration=lambda r: print(f"Iteration {r.iteration}: {r.success}")
        )

        if result.success:
            skill = result.value
        else:
            print(result.failure_report)
    """

    def __init__(
        self,
        max_iterations: int = 10,
        promises: CompletionPromiseSet[T] = None,
        initial_strategy: dict = None,
    ):
        self.max_iterations = max_iterations
        self.promises = promises or CompletionPromiseSet()
        self.initial_strategy = initial_strategy or {}
        self.failure_tracker = FailureTracker()

        # State
        self._status = LoopStatus.RUNNING
        self._iterations: list[IterationResult[T]] = []
        self._current_iteration = 0

    def run(
        self,
        task: Callable[[dict], T],
        on_iteration: Callable[[IterationResult[T]], None] = None,
        on_strategy_change: Callable[[dict], None] = None,
    ) -> LoopResult[T]:
        """Run the autonomous loop until completion or max iterations.

        Args:
            task: Function that takes strategy dict and returns result T.
                  Should raise exceptions on failure.
            on_iteration: Optional callback after each iteration.
            on_strategy_change: Optional callback when strategy is adjusted.

        Returns:
            LoopResult with final status, value, and analysis.
        """
        self._status = LoopStatus.RUNNING
        self._iterations = []
        self._current_iteration = 0
        self.failure_tracker.reset()

        # Apply initial strategy
        if self.initial_strategy:
            for key, value in self.initial_strategy.items():
                self.failure_tracker.current_strategy[key] = value

        while self._current_iteration < self.max_iterations:
            self._current_iteration += 1

            # Get current strategy (may be adjusted from previous failures)
            strategy = self.failure_tracker.get_adjusted_strategy()

            # Execute iteration
            iteration_result = self._execute_iteration(task, strategy)
            self._iterations.append(iteration_result)

            # Callback
            if on_iteration:
                on_iteration(iteration_result)

            # Check for success
            if iteration_result.success:
                self._status = LoopStatus.SUCCESS
                return self._build_result(iteration_result.value, self._current_iteration)

            # Record failure and get adjustments
            if iteration_result.error:
                self.failure_tracker.record_from_exception(
                    self._current_iteration,
                    iteration_result.error,
                    iteration_result.value
                )
            else:
                # Promise failure (no exception)
                self.failure_tracker.record(FailureRecord(
                    iteration=self._current_iteration,
                    failure_type=self._classify_promise_failure(iteration_result.promise_results),
                    message=self._summarize_promise_failures(iteration_result.promise_results),
                    value=iteration_result.value
                ))

            # Get strategy adjustments
            adjustments = self.failure_tracker.suggest_adjustments()
            if adjustments and on_strategy_change:
                on_strategy_change(self.failure_tracker.current_strategy)

        # Max iterations reached
        self._status = LoopStatus.MAX_ITERATIONS
        return self._build_result(None, None)

    def _execute_iteration(
        self,
        task: Callable[[dict], T],
        strategy: dict
    ) -> IterationResult[T]:
        """Execute a single iteration."""
        start_time = datetime.now()

        try:
            # Run the task
            value = task(strategy)

            # Check completion promises
            if self.promises.promises:
                all_passed, promise_results = self.promises.evaluate(value)
            else:
                all_passed = True
                promise_results = []

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            return IterationResult(
                iteration=self._current_iteration,
                value=value,
                success=all_passed,
                promise_results=promise_results,
                error=None,
                duration_ms=duration_ms,
                strategy=strategy.copy()
            )

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            return IterationResult(
                iteration=self._current_iteration,
                value=None,
                success=False,
                promise_results=[],
                error=e,
                duration_ms=duration_ms,
                strategy=strategy.copy()
            )

    def _classify_promise_failure(self, results: list[PromiseResult]) -> FailureType:
        """Classify the dominant failure type from promise results."""
        for result in results:
            if not result.passed:
                message = result.message.lower()
                if "source" in message or "file" in message:
                    return FailureType.SOURCE_NOT_FOUND
                elif "sandbox" in message:
                    return FailureType.SANDBOX_FAILED
                elif "confidence" in message:
                    return FailureType.LOW_CONFIDENCE
                elif "hallucin" in message or "ungrounded" in message:
                    return FailureType.HALLUCINATION
        return FailureType.UNKNOWN

    def _summarize_promise_failures(self, results: list[PromiseResult]) -> str:
        """Summarize failed promises into a message."""
        failed = [r.message for r in results if not r.passed]
        return "; ".join(failed) if failed else "Unknown failure"

    def _build_result(
        self,
        value: Optional[T],
        successful_iteration: Optional[int]
    ) -> LoopResult[T]:
        """Build the final loop result."""
        return LoopResult(
            status=self._status,
            value=value,
            total_iterations=self._current_iteration,
            successful_iteration=successful_iteration,
            all_iterations=self._iterations,
            final_strategy=self.failure_tracker.get_adjusted_strategy(),
            failure_report=self.failure_tracker.generate_report()
        )

    def abort(self) -> None:
        """Abort the loop (called externally)."""
        self._status = LoopStatus.ABORTED


# =============================================================================
# Convenience Functions
# =============================================================================

def run_with_retry(
    task: Callable[[dict], T],
    max_iterations: int = 10,
    promises: CompletionPromiseSet[T] = None,
    initial_strategy: dict = None,
    verbose: bool = True
) -> LoopResult[T]:
    """Convenience function to run a task with Ralph Wiggum retry logic.

    Example:
        result = run_with_retry(
            task=lambda s: generate_skill("langgraph state", s),
            max_iterations=5,
            promises=default_skill_promises(),
            verbose=True
        )
    """
    loop = RalphWiggumLoop(
        max_iterations=max_iterations,
        promises=promises,
        initial_strategy=initial_strategy
    )

    def on_iteration(r: IterationResult):
        if verbose:
            status = "✓" if r.success else "✗"
            print(f"[Ralph Wiggum] Iteration {r.iteration}: {status} ({r.duration_ms:.0f}ms)")
            if not r.success:
                if r.error:
                    print(f"  Error: {r.error}")
                for pr in r.promise_results:
                    if not pr.passed:
                        print(f"  {pr.message}")

    def on_strategy_change(strategy: dict):
        if verbose:
            print(f"[Ralph Wiggum] Strategy adjusted: {strategy}")

    return loop.run(task, on_iteration, on_strategy_change)
