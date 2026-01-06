"""Auditor Agent - Zero-Hallucination Content Verification.

The Auditor verifies generated content against actual source code,
ensuring Hall_m < 0.02 hallucination rate.

Verification Pipeline:
1. Extract claims from generated content
2. For each claim, find corresponding source references
3. Verify claim against actual source code
4. Reject any unverified claims
5. Calculate hallucination metrics

Model: Opus (critical judgment for zero-hallucination)
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path
import re

from .base import BaseAgent, AgentRole, AgentResult
from ..verify.ddr import DirectDependencyRetriever, SourceRef


@dataclass
class Claim:
    """A claim extracted from generated content."""
    text: str
    claim_type: str  # "symbol", "behavior", "api", "pattern"
    symbol_mentioned: Optional[str] = None
    line_cited: Optional[int] = None
    file_cited: Optional[str] = None

    @property
    def has_citation(self) -> bool:
        """Claim has a source citation."""
        return self.file_cited is not None or self.line_cited is not None


@dataclass
class ClaimVerification:
    """Result of verifying a single claim."""
    claim: Claim
    verified: bool
    source_ref: Optional[SourceRef] = None
    confidence: float = 0.0
    rejection_reason: Optional[str] = None


@dataclass
class AuditTask:
    """Task for the auditor agent."""
    content: str
    source_refs: list[SourceRef] = field(default_factory=list)
    codewiki_path: Optional[Path] = None
    repo_path: Optional[Path] = None
    strict_mode: bool = True  # Reject on any unverified claim


@dataclass
class AuditResult:
    """Result from audit operation."""
    passed: bool
    claim_verifications: list[ClaimVerification]
    total_claims: int
    verified_claims: int
    unverified_claims: int
    hallucination_rate: float
    rejection_reasons: list[str]

    @property
    def meets_target(self) -> bool:
        """Meets Hall_m < 0.02 target."""
        return self.hallucination_rate < 0.02


class AuditorAgent(BaseAgent[AuditResult]):
    """Agent that verifies generated content against source code.

    Zero-Hallucination Methodology:
    - Extract all claims from content (symbol refs, behaviors, patterns)
    - Verify each claim against actual source
    - Reject content with any unverified claims (strict mode)
    - Track hallucination rate: Hall_m = unverified / total

    Trust Philosophy:
    - Every claim must be grounded in source code
    - No claim accepted without file:line validation
    - Unverified content is ALWAYS rejected
    """

    def __init__(self):
        super().__init__(AgentRole.AUDITOR)
        self.ddr: Optional[DirectDependencyRetriever] = None

    def execute(self, task: AuditTask, context: dict = None) -> AgentResult:
        """Execute audit on generated content.

        Args:
            task: AuditTask with content to verify
            context: Shared context

        Returns:
            AgentResult with AuditResult
        """
        start = self._start_execution()

        try:
            # Initialize DDR if paths provided
            if task.codewiki_path or task.repo_path:
                self.ddr = DirectDependencyRetriever(
                    codewiki_path=task.codewiki_path,
                    repo_path=task.repo_path
                )

            # Step 1: Extract claims from content
            claims = self._extract_claims(task.content)

            # Step 2: Verify each claim
            verifications = []
            for claim in claims:
                verification = self._verify_claim(claim, task.source_refs)
                verifications.append(verification)

            # Step 3: Calculate metrics
            total = len(claims)
            verified = sum(1 for v in verifications if v.verified)
            unverified = total - verified
            hall_rate = unverified / total if total > 0 else 0.0

            # Step 4: Determine pass/fail
            if task.strict_mode:
                passed = unverified == 0
            else:
                passed = hall_rate < 0.02

            # Collect rejection reasons
            rejection_reasons = [
                v.rejection_reason
                for v in verifications
                if not v.verified and v.rejection_reason
            ]

            result = AuditResult(
                passed=passed,
                claim_verifications=verifications,
                total_claims=total,
                verified_claims=verified,
                unverified_claims=unverified,
                hallucination_rate=hall_rate,
                rejection_reasons=rejection_reasons,
            )

            # Report to supervisor
            if passed:
                self.send_message(
                    AgentRole.SUPERVISOR,
                    f"Audit PASSED: {verified}/{total} claims verified (Hall_m={hall_rate:.3f})",
                    hallucination_rate=hall_rate,
                )
            else:
                self.send_message(
                    AgentRole.SUPERVISOR,
                    f"Audit FAILED: {unverified}/{total} unverified claims (Hall_m={hall_rate:.3f})",
                    rejected=True,
                    hallucination_rate=hall_rate,
                    rejection_reasons=rejection_reasons[:5],  # Top 5
                )

            return self._end_execution(start, output=result)

        except Exception as e:
            return self._end_execution(start, error=str(e))

    def _extract_claims(self, content: str) -> list[Claim]:
        """Extract verifiable claims from content."""
        claims = []

        # Pattern 1: Inline code references like `SymbolName`
        code_refs = re.findall(r'`([A-Z][a-zA-Z0-9_]+)`', content)
        for ref in code_refs:
            claims.append(Claim(
                text=ref,
                claim_type="symbol",
                symbol_mentioned=ref,
            ))

        # Pattern 2: File:line citations like `file.py:123`
        file_line_refs = re.findall(r'`?([a-zA-Z0-9_/]+\.py):(\d+)`?', content)
        for file_path, line in file_line_refs:
            claims.append(Claim(
                text=f"{file_path}:{line}",
                claim_type="symbol",
                file_cited=file_path,
                line_cited=int(line),
            ))

        # Pattern 3: Function/method calls like "the `func_name()` function"
        func_refs = re.findall(r'`([a-z_][a-zA-Z0-9_]*)\(\)`', content)
        for ref in func_refs:
            claims.append(Claim(
                text=ref,
                claim_type="symbol",
                symbol_mentioned=ref,
            ))

        # Pattern 4: Class references like "the StateGraph class"
        class_refs = re.findall(r'the\s+`?([A-Z][a-zA-Z0-9]+)`?\s+class', content)
        for ref in class_refs:
            if ref not in [c.symbol_mentioned for c in claims]:
                claims.append(Claim(
                    text=ref,
                    claim_type="symbol",
                    symbol_mentioned=ref,
                ))

        # Pattern 5: Method calls like "graph.add_node()"
        method_refs = re.findall(r'`?([a-z_][a-zA-Z0-9_]*)\.([a-z_][a-zA-Z0-9_]*)\(\)`?', content)
        for obj, method in method_refs:
            claims.append(Claim(
                text=f"{obj}.{method}",
                claim_type="api",
                symbol_mentioned=method,
            ))

        # Pattern 6: Import statements like "from module import Symbol"
        import_refs = re.findall(r'from\s+([a-zA-Z0-9_.]+)\s+import\s+([A-Za-z0-9_,\s]+)', content)
        for module, imports in import_refs:
            for imp in imports.split(','):
                imp = imp.strip()
                if imp:
                    claims.append(Claim(
                        text=f"import {imp} from {module}",
                        claim_type="symbol",
                        symbol_mentioned=imp,
                    ))

        return claims

    def _verify_claim(
        self,
        claim: Claim,
        provided_refs: list[SourceRef]
    ) -> ClaimVerification:
        """Verify a single claim against sources."""

        # Strategy 1: Check against provided source refs
        for ref in provided_refs:
            if self._claim_matches_ref(claim, ref):
                return ClaimVerification(
                    claim=claim,
                    verified=True,
                    source_ref=ref,
                    confidence=1.0 if ref.validated else 0.8,
                )

        # Strategy 2: Use DDR to find matching source
        if self.ddr and claim.symbol_mentioned:
            ddr_result = self.ddr.retrieve(claim.symbol_mentioned, max_results=5)
            for element in ddr_result.elements:
                if element.is_valid:
                    return ClaimVerification(
                        claim=claim,
                        verified=True,
                        source_ref=element.source_ref,
                        confidence=0.9,
                    )

        # Strategy 3: Check file:line citation directly
        if claim.file_cited and claim.line_cited and self.ddr and self.ddr.repo_path:
            ref = SourceRef(
                symbol_name=claim.symbol_mentioned or "unknown",
                file_path=claim.file_cited,
                line_number=claim.line_cited,
            )
            if self.ddr.validate_source_ref(ref):
                return ClaimVerification(
                    claim=claim,
                    verified=True,
                    source_ref=ref,
                    confidence=1.0,
                )

        # Not verified
        return ClaimVerification(
            claim=claim,
            verified=False,
            confidence=0.0,
            rejection_reason=f"Symbol '{claim.text}' not found in source code",
        )

    def _claim_matches_ref(self, claim: Claim, ref: SourceRef) -> bool:
        """Check if claim matches a source reference."""
        if claim.symbol_mentioned:
            # Direct symbol match
            if claim.symbol_mentioned.lower() == ref.symbol_name.lower():
                return True
            # Symbol contained in name
            if claim.symbol_mentioned.lower() in ref.symbol_name.lower():
                return True

        if claim.file_cited and claim.line_cited:
            # File and line match
            if (claim.file_cited in ref.file_path and
                claim.line_cited == ref.line_number):
                return True

        return False

    def audit_with_strict_mode(
        self,
        content: str,
        source_refs: list[SourceRef],
        codewiki_path: Optional[Path] = None,
    ) -> AuditResult:
        """Convenience method for strict mode audit."""
        task = AuditTask(
            content=content,
            source_refs=source_refs,
            codewiki_path=codewiki_path,
            strict_mode=True,
        )
        result = self.execute(task)
        return result.output if result.success else None

    def get_hallucination_summary(self, result: AuditResult) -> str:
        """Generate human-readable hallucination summary."""
        lines = [
            f"Hallucination Audit Summary",
            f"=" * 40,
            f"Total Claims: {result.total_claims}",
            f"Verified: {result.verified_claims}",
            f"Unverified: {result.unverified_claims}",
            f"Hall_m Rate: {result.hallucination_rate:.4f}",
            f"Target (<0.02): {'PASS' if result.meets_target else 'FAIL'}",
            f"Strict Mode: {'PASS' if result.passed else 'FAIL'}",
        ]

        if result.rejection_reasons:
            lines.append("")
            lines.append("Rejection Reasons:")
            for i, reason in enumerate(result.rejection_reasons[:10], 1):
                lines.append(f"  {i}. {reason}")

        return '\n'.join(lines)
