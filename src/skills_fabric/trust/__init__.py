"""Trust module for Skills Fabric.

Implements the Miessler-aligned PAI Trust Hierarchy:

| Level | Content Type   | Trust | Source                           |
|-------|---------------|-------|----------------------------------|
| **1** | HardContent   | 100%  | AST, SCIP, regex - ZERO LLM      |
| **2** | VerifiedSoft  | 95%   | LLM output grounded + sandbox    |
| **3** | Unverified    | 0%    | Pure LLM - REJECTED, never used  |

Key Components:
- TrustLevel: Enum of trust levels
- HardContentVerifier: Level 1 verification (AST, SCIP, regex)
- VerifiedSoftVerifier: Level 2 verification (sandbox, grounding)
- CrossLayerVerifier: Complete cross-layer verification engine

Usage:
    from skills_fabric.trust import verify_skill_trust, TrustLevel

    result = verify_skill_trust(my_skill)
    if result.overall_passed:
        print(f"Verified at {result.overall_trust.name} level")
"""
from .hierarchy import (
    TrustLevel,
    TrustResult,
    TrustMetadata,
    TrustedContent,
    TrustEnforcer,
    hard_content_result,
    verified_soft_result,
    unverified_result,
)
from .hard_content import (
    HardContentVerifier,
    VerifiedSymbol,
    RegexExtractor,
)
from .verified_soft import (
    VerifiedSoftVerifier,
    SkillVerifier,
    GroundingCheck,
)
from .cross_layer import (
    CrossLayerVerifier,
    CrossLayerResult,
    LayerResult,
    VerificationLayer,
    verify_skill_trust,
    quick_trust_check,
)

__all__ = [
    # Trust Hierarchy
    "TrustLevel",
    "TrustResult",
    "TrustMetadata",
    "TrustedContent",
    "TrustEnforcer",
    "hard_content_result",
    "verified_soft_result",
    "unverified_result",
    # Hard Content (Level 1)
    "HardContentVerifier",
    "VerifiedSymbol",
    "RegexExtractor",
    # Verified Soft (Level 2)
    "VerifiedSoftVerifier",
    "SkillVerifier",
    "GroundingCheck",
    # Cross-Layer Verification
    "CrossLayerVerifier",
    "CrossLayerResult",
    "LayerResult",
    "VerificationLayer",
    "verify_skill_trust",
    "quick_trust_check",
]
