"""Verifier Agent - Trust hierarchy verification.

Specializes in:
- Cross-layer verification
- Sandbox execution
- Trust level assignment
- Rejection of unverified content

Model: Opus (complex judgment for verification)
"""
from dataclasses import dataclass
from typing import Any, Optional

from .base import BaseAgent, AgentRole, AgentResult
from ..trust import (
    TrustLevel,
    verify_skill_trust,
    CrossLayerResult,
)


@dataclass
class VerificationTask:
    """Task for the verifier agent."""
    skill: Any               # Skill to verify
    require_sandbox: bool = True
    min_trust_level: TrustLevel = TrustLevel.VERIFIED_SOFT
    timeout: int = 10


@dataclass
class VerificationResult:
    """Result from verification operation."""
    passed: bool
    trust_level: TrustLevel
    cross_layer_result: CrossLayerResult
    rejection_reason: Optional[str] = None


class VerifierAgent(BaseAgent[VerificationResult]):
    """Agent that verifies skills against trust hierarchy.

    Responsibilities:
    - Run cross-layer verification
    - Execute code in sandbox
    - Assign trust levels
    - Reject unverified content (Level 3)

    Trust Hierarchy:
    - Level 1 (HardContent): 100% trust - AST, SCIP verified
    - Level 2 (VerifiedSoft): 95% trust - Sandbox passed, grounded
    - Level 3 (Unverified): 0% trust - REJECTED
    """

    def __init__(self):
        super().__init__(AgentRole.VERIFIER)

    def execute(self, task: VerificationTask, context: dict = None) -> AgentResult:
        """Execute verification task.

        Args:
            task: VerificationTask with skill to verify
            context: Shared context

        Returns:
            AgentResult with VerificationResult
        """
        start = self._start_execution()

        try:
            # Run cross-layer verification
            cross_result = verify_skill_trust(task.skill)

            # Check if meets minimum trust level
            passed = (
                cross_result.overall_passed and
                cross_result.overall_trust <= task.min_trust_level
            )

            rejection_reason = None
            if not passed:
                if cross_result.overall_trust == TrustLevel.UNVERIFIED:
                    rejection_reason = "REJECTED: Content failed trust verification (Level 3)"
                else:
                    # Find specific failure
                    for lr in cross_result.layer_results:
                        if not lr.passed:
                            rejection_reason = f"Failed {lr.layer.value}: {lr.trust_result.rejection_reason}"
                            break

            result = VerificationResult(
                passed=passed,
                trust_level=cross_result.overall_trust,
                cross_layer_result=cross_result,
                rejection_reason=rejection_reason
            )

            # Report to supervisor
            if passed:
                self.send_message(
                    AgentRole.SUPERVISOR,
                    f"Verified at {result.trust_level.name} level",
                    trust_level=result.trust_level.value
                )
            else:
                self.send_message(
                    AgentRole.SUPERVISOR,
                    f"Verification FAILED: {rejection_reason}",
                    rejected=True
                )

            return self._end_execution(start, output=result)

        except Exception as e:
            return self._end_execution(start, error=str(e))

    def quick_verify(self, code: str, source_url: str) -> tuple[bool, TrustLevel]:
        """Quick verification of code + source."""
        from ..trust import quick_trust_check
        return quick_trust_check(code, source_url)

    def verify_batch(
        self,
        skills: list[Any],
        min_trust_level: TrustLevel = TrustLevel.VERIFIED_SOFT
    ) -> list[VerificationResult]:
        """Verify multiple skills."""
        results = []

        for skill in skills:
            task = VerificationTask(
                skill=skill,
                min_trust_level=min_trust_level
            )
            agent_result = self.execute(task)

            if agent_result.success:
                results.append(agent_result.output)
            else:
                # Create failed result
                results.append(VerificationResult(
                    passed=False,
                    trust_level=TrustLevel.UNVERIFIED,
                    cross_layer_result=None,
                    rejection_reason=agent_result.error
                ))

        return results
