"""Verified Soft Content - Trust Level 2 (95% Trust).

Verifies LLM output through grounding checks:
- Sandbox execution: Code runs without error
- Source citation: Claims point to real files
- PROVEN link: Documentation connected to code
- Output schema: Response matches expected structure

BMAD Principle:
> "VerifiedSoft has 95% trust because while LLM is involved,
>  the output is grounded in verifiable source code."

Miessler PAI Philosophy:
> "Schema enforcement at every external boundary."
"""
from dataclasses import dataclass
from typing import Any, Optional, Callable
import json

from .hierarchy import (
    TrustResult,
    TrustLevel,
    verified_soft_result,
    unverified_result,
)
from .hard_content import HardContentVerifier


@dataclass
class GroundingCheck:
    """A grounding check for LLM output."""
    name: str
    check: Callable[[Any], bool]
    error_message: str
    weight: float = 1.0  # Contribution to confidence score


class VerifiedSoftVerifier:
    """Verifies LLM output through grounding (Trust Level 2).

    All verification requires:
    1. At least one grounding check passes
    2. Source citation is verifiable
    3. Output matches expected schema (if provided)

    Returns:
    - VERIFIED_SOFT: LLM output with verified grounding
    - UNVERIFIED: Failed grounding, REJECTED
    """

    def __init__(self):
        self.hard_verifier = HardContentVerifier()

    def verify_with_sandbox(
        self,
        code: str,
        timeout: int = 10
    ) -> TrustResult:
        """Verify code by executing in sandbox.

        Grounding: If code executes without error in isolated sandbox,
        we have evidence it's functional (not hallucinated syntax).
        """
        from ..verify.sandbox import BubblewrapSandbox, ExecutionResult

        if not code or not code.strip():
            return unverified_result(
                source="sandbox",
                rejection_reason="Empty code"
            )

        sandbox = BubblewrapSandbox()
        result = sandbox.execute_python(code, timeout=timeout)

        if result.success:
            return verified_soft_result(
                source="sandbox_execution",
                confidence=0.95,
                grounding_evidence=[
                    "sandbox_passed:true",
                    f"exit_code:{result.exit_code}"
                ]
            )

        return unverified_result(
            source="sandbox",
            rejection_reason=f"Sandbox execution failed: {result.stderr[:200]}"
        )

    def verify_with_source_citation(
        self,
        content: Any,
        source_field: str = "source_url"
    ) -> TrustResult:
        """Verify content has valid source citation.

        Grounding: If content cites a real file that exists,
        it has evidence of being grounded in source.
        """
        # Extract source citation
        if isinstance(content, dict):
            source = content.get(source_field)
        elif hasattr(content, source_field):
            source = getattr(content, source_field)
        else:
            return unverified_result(
                source="citation_check",
                rejection_reason=f"No '{source_field}' field found"
            )

        if not source:
            return unverified_result(
                source="citation_check",
                rejection_reason="Empty source citation"
            )

        # Verify source exists (HardContent check)
        file_result = self.hard_verifier.verify_file_exists(source)

        if file_result.trusted:
            return verified_soft_result(
                source="source_citation",
                confidence=0.90,
                grounding_evidence=[
                    f"cited_source:{source}",
                    "file_verified:true"
                ]
            )

        return unverified_result(
            source="citation_check",
            rejection_reason=f"Source citation invalid: {file_result.rejection_reason}"
        )

    def verify_with_proven_link(
        self,
        concept_name: str,
        min_confidence: float = 0.7
    ) -> TrustResult:
        """Verify through PROVEN doc-to-code link.

        Grounding: If concept has PROVEN relationship to symbol
        with sufficient confidence, it's grounded in code.
        """
        from ..core.database import db

        try:
            result = db.execute(
                """
                MATCH (c:Concept {name: $concept_name})-[:PROVEN]->(s:Symbol)
                RETURN s.name, s.file_path
                """,
                {"concept_name": concept_name}
            )

            if result.has_next():
                row = result.get_next()
                symbol_name, file_path = row

                # Verify linked file exists
                file_result = self.hard_verifier.verify_file_exists(file_path)

                if file_result.trusted:
                    return verified_soft_result(
                        source="proven_link",
                        confidence=min_confidence,
                        grounding_evidence=[
                            f"concept:{concept_name}",
                            f"symbol:{symbol_name}",
                            f"file:{file_path}",
                            "proven_link:verified"
                        ]
                    )

            return unverified_result(
                source="proven_link",
                rejection_reason=f"No valid PROVEN link for concept: {concept_name}"
            )

        except Exception as e:
            return unverified_result(
                source="proven_link",
                rejection_reason=f"PROVEN link check failed: {e}"
            )

    def verify_with_schema(
        self,
        content: Any,
        schema: dict
    ) -> TrustResult:
        """Verify LLM output matches expected schema.

        Miessler PAI: Schema enforcement at boundaries.

        Args:
            content: LLM output to verify
            schema: JSON schema or field requirements

        Example schema:
            {
                "required": ["question", "code", "source_url"],
                "types": {"question": str, "code": str, "verified": bool}
            }
        """
        if not content:
            return unverified_result(
                source="schema_check",
                rejection_reason="Empty content"
            )

        # Check required fields
        required = schema.get("required", [])
        missing = []

        for field in required:
            if isinstance(content, dict):
                if field not in content or not content[field]:
                    missing.append(field)
            elif hasattr(content, field):
                if not getattr(content, field):
                    missing.append(field)
            else:
                missing.append(field)

        if missing:
            return unverified_result(
                source="schema_check",
                rejection_reason=f"Missing required fields: {missing}"
            )

        # Check types
        types = schema.get("types", {})
        type_errors = []

        for field, expected_type in types.items():
            if isinstance(content, dict):
                value = content.get(field)
            else:
                value = getattr(content, field, None)

            if value is not None and not isinstance(value, expected_type):
                type_errors.append(f"{field} should be {expected_type.__name__}")

        if type_errors:
            return unverified_result(
                source="schema_check",
                rejection_reason=f"Type errors: {type_errors}"
            )

        return verified_soft_result(
            source="schema_validation",
            confidence=0.90,
            grounding_evidence=[
                "schema_valid:true",
                f"required_fields:{len(required)}"
            ]
        )

    def verify_combined(
        self,
        content: Any,
        checks: list[GroundingCheck]
    ) -> TrustResult:
        """Run multiple grounding checks and combine results.

        Content is verified if at least one check passes.
        Confidence is weighted average of passing checks.
        """
        passed_checks = []
        failed_checks = []
        total_weight = sum(c.weight for c in checks)

        for check in checks:
            try:
                if check.check(content):
                    passed_checks.append(check)
                else:
                    failed_checks.append(check)
            except Exception as e:
                failed_checks.append(check)

        if not passed_checks:
            reasons = [f"{c.name}: {c.error_message}" for c in failed_checks]
            return unverified_result(
                source="combined_check",
                rejection_reason=f"All grounding checks failed: {'; '.join(reasons)}"
            )

        # Calculate weighted confidence
        passed_weight = sum(c.weight for c in passed_checks)
        confidence = 0.95 * (passed_weight / total_weight)

        return verified_soft_result(
            source="combined_grounding",
            confidence=confidence,
            grounding_evidence=[
                f"checks_passed:{len(passed_checks)}/{len(checks)}",
                f"passed:{','.join(c.name for c in passed_checks)}"
            ]
        )


# =============================================================================
# Skill-Specific Verification
# =============================================================================

class SkillVerifier:
    """Verifies generated skills meet trust requirements.

    Combines multiple verification methods:
    1. Source exists (HardContent)
    2. Code is valid syntax (HardContent)
    3. Code executes in sandbox (VerifiedSoft)
    4. Schema is valid (VerifiedSoft)
    """

    SKILL_SCHEMA = {
        "required": ["question", "code", "source_url"],
        "types": {
            "question": str,
            "code": str,
            "source_url": str,
            "verified": bool,
        }
    }

    def __init__(self):
        self.hard_verifier = HardContentVerifier()
        self.soft_verifier = VerifiedSoftVerifier()

    def verify_skill(self, skill: Any) -> TrustResult:
        """Fully verify a generated skill.

        Returns:
        - VERIFIED_SOFT if all checks pass
        - UNVERIFIED if any critical check fails
        """
        results = []
        grounding_evidence = []

        # 1. Schema check
        schema_result = self.soft_verifier.verify_with_schema(
            skill, self.SKILL_SCHEMA
        )
        results.append(("schema", schema_result))
        if not schema_result.trusted:
            return schema_result

        # 2. Source exists (HardContent)
        source_url = (
            skill.get("source_url") if isinstance(skill, dict)
            else getattr(skill, "source_url", None)
        )
        source_result = self.hard_verifier.verify_file_exists(source_url)
        results.append(("source", source_result))
        grounding_evidence.extend(source_result.metadata.grounding_evidence)

        # 3. Code syntax (HardContent)
        code = (
            skill.get("code") if isinstance(skill, dict)
            else getattr(skill, "code", None)
        )
        syntax_result = self.hard_verifier.verify_code_parseable(code)
        results.append(("syntax", syntax_result))
        grounding_evidence.extend(syntax_result.metadata.grounding_evidence)

        # 4. Sandbox execution (VerifiedSoft)
        sandbox_result = self.soft_verifier.verify_with_sandbox(code)
        results.append(("sandbox", sandbox_result))
        grounding_evidence.extend(sandbox_result.metadata.grounding_evidence)

        # Calculate overall result
        critical_passed = all(
            r.trusted for name, r in results
            if name in ["schema", "source"]
        )

        if not critical_passed:
            # Find first failure
            for name, r in results:
                if not r.trusted:
                    return r

        # Calculate confidence from passing checks
        passed = sum(1 for _, r in results if r.trusted)
        confidence = 0.95 * (passed / len(results))

        return verified_soft_result(
            source="skill_verification",
            confidence=confidence,
            grounding_evidence=grounding_evidence
        )
