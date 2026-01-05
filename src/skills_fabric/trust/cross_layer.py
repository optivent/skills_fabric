"""Cross-Layer Verification - Complete trust verification engine.

Implements the full Trust Hierarchy verification across all layers:

Layer 1 (Syntax): AST parsing, regex extraction
Layer 2 (Structure): Symbol graph, call relationships
Layer 3 (Behavior): Sandbox execution, runtime analysis
Layer 4 (Navigation): PROVEN links, documentation mapping
Layer 5 (Foundation): Source code grounding, file verification

BMAD C.O.R.E. Integration:
- Collaboration: Reports verification results clearly
- Optimized: Parallel verification where possible
- Reflection: Honest reporting of what passed/failed
- Engine: Systematic verification workflow
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime

from .hierarchy import (
    TrustLevel,
    TrustResult,
    TrustEnforcer,
    hard_content_result,
    verified_soft_result,
    unverified_result,
)
from .hard_content import HardContentVerifier, VerifiedSymbol
from .verified_soft import VerifiedSoftVerifier, SkillVerifier


class VerificationLayer(Enum):
    """Verification layers from the Progressive Iceberg Architecture."""
    SYNTAX = "syntax"           # Layer 1: AST, parsing
    STRUCTURE = "structure"     # Layer 2: Symbols, graph
    BEHAVIOR = "behavior"       # Layer 3: Execution, runtime
    NAVIGATION = "navigation"   # Layer 4: PROVEN links
    FOUNDATION = "foundation"   # Layer 5: Source grounding


@dataclass
class LayerResult:
    """Result from a single verification layer."""
    layer: VerificationLayer
    passed: bool
    trust_result: TrustResult
    details: dict = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass
class CrossLayerResult:
    """Complete cross-layer verification result."""
    overall_passed: bool
    overall_trust: TrustLevel
    layer_results: list[LayerResult]
    grounding_evidence: list[str]
    verification_time: datetime = field(default_factory=datetime.now)

    @property
    def confidence(self) -> float:
        """Calculate overall confidence from layer results."""
        if not self.layer_results:
            return 0.0

        passed = sum(1 for lr in self.layer_results if lr.passed)
        return passed / len(self.layer_results)

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "CROSS-LAYER VERIFICATION REPORT",
            "=" * 60,
            f"Overall: {'PASSED' if self.overall_passed else 'FAILED'}",
            f"Trust Level: {self.overall_trust.name}",
            f"Confidence: {self.confidence:.0%}",
            "",
            "Layer Results:",
        ]

        for lr in self.layer_results:
            status = "✓" if lr.passed else "✗"
            lines.append(f"  {status} {lr.layer.value}: {lr.trust_result.metadata.source}")
            if not lr.passed and lr.trust_result.rejection_reason:
                lines.append(f"      → {lr.trust_result.rejection_reason}")

        lines.extend([
            "",
            "Grounding Evidence:",
        ])
        for evidence in self.grounding_evidence[:10]:  # Limit output
            lines.append(f"  • {evidence}")

        lines.append("=" * 60)
        return "\n".join(lines)


class CrossLayerVerifier:
    """Complete cross-layer verification engine.

    Verifies content across all 5 layers of the Progressive Iceberg:
    1. Syntax: Can be parsed
    2. Structure: Symbols exist
    3. Behavior: Code executes
    4. Navigation: PROVEN links valid
    5. Foundation: Grounded in source

    Usage:
        verifier = CrossLayerVerifier()
        result = verifier.verify_skill(skill)

        if result.overall_passed:
            print("Skill verified!")
        else:
            print(result.summary())
    """

    def __init__(self, min_trust_level: TrustLevel = TrustLevel.VERIFIED_SOFT):
        self.hard_verifier = HardContentVerifier()
        self.soft_verifier = VerifiedSoftVerifier()
        self.skill_verifier = SkillVerifier()
        self.enforcer = TrustEnforcer(min_level=min_trust_level)

    def verify_skill(self, skill: Any) -> CrossLayerResult:
        """Verify a skill across all layers.

        Args:
            skill: Skill object or dict with question, code, source_url

        Returns:
            CrossLayerResult with complete verification details
        """
        layer_results = []
        grounding_evidence = []

        # Extract skill fields
        if isinstance(skill, dict):
            code = skill.get("code", "")
            source_url = skill.get("source_url", "")
            concept_name = skill.get("concept_name", "")
        else:
            code = getattr(skill, "code", "")
            source_url = getattr(skill, "source_url", "")
            concept_name = getattr(skill, "concept_name", "")

        # Layer 1: Syntax Verification
        start = datetime.now()
        syntax_result = self._verify_syntax(code)
        layer_results.append(LayerResult(
            layer=VerificationLayer.SYNTAX,
            passed=syntax_result.trusted,
            trust_result=syntax_result,
            details={"code_length": len(code)},
            duration_ms=(datetime.now() - start).total_seconds() * 1000
        ))
        grounding_evidence.extend(syntax_result.metadata.grounding_evidence)

        # Layer 2: Structure Verification
        start = datetime.now()
        structure_result = self._verify_structure(source_url)
        layer_results.append(LayerResult(
            layer=VerificationLayer.STRUCTURE,
            passed=structure_result.trusted,
            trust_result=structure_result,
            details={"source_url": source_url},
            duration_ms=(datetime.now() - start).total_seconds() * 1000
        ))
        grounding_evidence.extend(structure_result.metadata.grounding_evidence)

        # Layer 3: Behavior Verification
        start = datetime.now()
        behavior_result = self._verify_behavior(code)
        layer_results.append(LayerResult(
            layer=VerificationLayer.BEHAVIOR,
            passed=behavior_result.trusted,
            trust_result=behavior_result,
            details={},
            duration_ms=(datetime.now() - start).total_seconds() * 1000
        ))
        grounding_evidence.extend(behavior_result.metadata.grounding_evidence)

        # Layer 4: Navigation Verification
        start = datetime.now()
        navigation_result = self._verify_navigation(concept_name, source_url)
        layer_results.append(LayerResult(
            layer=VerificationLayer.NAVIGATION,
            passed=navigation_result.trusted,
            trust_result=navigation_result,
            details={"concept": concept_name},
            duration_ms=(datetime.now() - start).total_seconds() * 1000
        ))
        grounding_evidence.extend(navigation_result.metadata.grounding_evidence)

        # Layer 5: Foundation Verification
        start = datetime.now()
        foundation_result = self._verify_foundation(source_url, code)
        layer_results.append(LayerResult(
            layer=VerificationLayer.FOUNDATION,
            passed=foundation_result.trusted,
            trust_result=foundation_result,
            details={},
            duration_ms=(datetime.now() - start).total_seconds() * 1000
        ))
        grounding_evidence.extend(foundation_result.metadata.grounding_evidence)

        # Calculate overall result
        critical_layers = [VerificationLayer.SYNTAX, VerificationLayer.FOUNDATION]
        critical_passed = all(
            lr.passed for lr in layer_results
            if lr.layer in critical_layers
        )

        all_passed = all(lr.passed for lr in layer_results)

        if all_passed:
            overall_trust = TrustLevel.HARD_CONTENT
        elif critical_passed:
            overall_trust = TrustLevel.VERIFIED_SOFT
        else:
            overall_trust = TrustLevel.UNVERIFIED

        return CrossLayerResult(
            overall_passed=self.enforcer.accept(
                verified_soft_result("cross_layer", 0.95) if critical_passed
                else unverified_result("cross_layer", "Critical layers failed")
            ),
            overall_trust=overall_trust,
            layer_results=layer_results,
            grounding_evidence=list(set(grounding_evidence))
        )

    def _verify_syntax(self, code: str) -> TrustResult:
        """Layer 1: Syntax verification via AST parsing."""
        return self.hard_verifier.verify_code_parseable(code)

    def _verify_structure(self, source_url: str) -> TrustResult:
        """Layer 2: Structure verification - file and symbols exist."""
        if not source_url:
            return unverified_result("structure", "No source URL provided")

        file_result = self.hard_verifier.verify_file_exists(source_url)
        if not file_result.trusted:
            return file_result

        # Extract and verify symbols
        symbols, extract_result = self.hard_verifier.extract_verified_symbols(source_url)
        if not extract_result.trusted:
            return extract_result

        if not symbols:
            return unverified_result("structure", "No symbols found in source file")

        return hard_content_result(
            source="structure_verification",
            grounding_evidence=[
                f"file_exists:true",
                f"symbols_count:{len(symbols)}"
            ]
        )

    def _verify_behavior(self, code: str) -> TrustResult:
        """Layer 3: Behavior verification via sandbox execution."""
        if not code or not code.strip():
            # Empty code can't be verified for behavior
            return verified_soft_result(
                "behavior_skip",
                confidence=0.5,
                grounding_evidence=["code_empty:true"]
            )

        return self.soft_verifier.verify_with_sandbox(code)

    def _verify_navigation(
        self,
        concept_name: str,
        source_url: str
    ) -> TrustResult:
        """Layer 4: Navigation verification via PROVEN links."""
        if not concept_name:
            # No concept to verify navigation for
            return verified_soft_result(
                "navigation_skip",
                confidence=0.5,
                grounding_evidence=["no_concept:true"]
            )

        return self.soft_verifier.verify_with_proven_link(concept_name)

    def _verify_foundation(
        self,
        source_url: str,
        code: str
    ) -> TrustResult:
        """Layer 5: Foundation verification - ultimate source grounding."""
        evidence = []

        # Check source file exists
        if source_url:
            file_result = self.hard_verifier.verify_file_exists(source_url)
            if file_result.trusted:
                evidence.append(f"source_file_verified:{source_url}")
            else:
                return file_result

        # Check code has valid imports
        if code:
            import re
            imports = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+\S+', code, re.MULTILINE)
            imports = [i for i in imports if i]  # Filter empty

            for module in imports[:5]:  # Check first 5
                import_result = self.hard_verifier.verify_import_exists(module)
                if import_result.trusted:
                    evidence.append(f"import_verified:{module}")

        if evidence:
            return hard_content_result(
                source="foundation_verification",
                grounding_evidence=evidence
            )

        return unverified_result(
            "foundation",
            "No foundation grounding evidence found"
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def verify_skill_trust(skill: Any) -> CrossLayerResult:
    """Convenience function to verify a skill's trust level.

    Example:
        result = verify_skill_trust(my_skill)
        if result.overall_passed:
            print(f"Verified at {result.overall_trust.name} level")
        else:
            print(result.summary())
    """
    verifier = CrossLayerVerifier()
    return verifier.verify_skill(skill)


def quick_trust_check(
    code: str,
    source_url: str
) -> tuple[bool, TrustLevel]:
    """Quick trust check for code + source.

    Returns:
        Tuple of (passed, trust_level)
    """
    verifier = CrossLayerVerifier()
    result = verifier.verify_skill({
        "code": code,
        "source_url": source_url,
        "question": "Quick check"
    })
    return result.overall_passed, result.overall_trust
