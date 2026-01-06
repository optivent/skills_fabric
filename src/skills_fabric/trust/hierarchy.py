"""Trust Hierarchy - Core trust level definitions and verification.

Implements the Miessler-aligned PAI Trust Hierarchy:

| Level | Content Type   | Trust | Source                           |
|-------|---------------|-------|----------------------------------|
| **1** | HardContent   | 100%  | AST, SCIP, regex - ZERO LLM      |
| **2** | VerifiedSoft  | 95%   | LLM output grounded + sandbox    |
| **3** | Unverified    | 0%    | Pure LLM - REJECTED, never used  |

Key Principle:
> "If you can't prove it points to real code, don't generate a skill from it."
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import IntEnum
from datetime import datetime


class TrustLevel(IntEnum):
    """Trust levels for content verification.

    Higher level = lower trust.
    """
    HARD_CONTENT = 1      # 100% trust - AST, SCIP, compiler-verified
    VERIFIED_SOFT = 2     # 95% trust - LLM output with grounding
    UNVERIFIED = 3        # 0% trust - REJECTED


@dataclass
class TrustMetadata:
    """Metadata about trust verification."""
    level: TrustLevel
    source: str                    # e.g., "ast", "scip", "llm+sandbox"
    confidence: float             # 0.0 to 1.0
    verified_at: datetime = field(default_factory=datetime.now)
    verifier: str = "unknown"     # Which verification method was used
    grounding_evidence: list[str] = field(default_factory=list)


@dataclass
class TrustResult:
    """Result of trust verification."""
    trusted: bool
    level: TrustLevel
    metadata: TrustMetadata
    rejection_reason: Optional[str] = None

    @property
    def trust_percentage(self) -> int:
        """Get trust percentage based on level."""
        if self.level == TrustLevel.HARD_CONTENT:
            return 100
        elif self.level == TrustLevel.VERIFIED_SOFT:
            return 95
        else:
            return 0

    def to_dict(self) -> dict:
        return {
            "trusted": self.trusted,
            "level": self.level.name,
            "trust_percentage": self.trust_percentage,
            "confidence": self.metadata.confidence,
            "source": self.metadata.source,
            "verifier": self.metadata.verifier,
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class TrustedContent:
    """Content that has passed trust verification."""
    content: Any
    trust_result: TrustResult

    @property
    def is_hard_content(self) -> bool:
        return self.trust_result.level == TrustLevel.HARD_CONTENT

    @property
    def is_verified_soft(self) -> bool:
        return self.trust_result.level == TrustLevel.VERIFIED_SOFT


# =============================================================================
# Trust Level Factories
# =============================================================================

def hard_content_result(
    source: str,
    grounding_evidence: list[str] = None
) -> TrustResult:
    """Create a HardContent (Level 1) trust result.

    Use for:
    - AST-extracted symbols
    - SCIP-indexed definitions
    - Regex-extracted patterns
    - Verified file paths
    """
    return TrustResult(
        trusted=True,
        level=TrustLevel.HARD_CONTENT,
        metadata=TrustMetadata(
            level=TrustLevel.HARD_CONTENT,
            source=source,
            confidence=1.0,
            verifier="hard_content",
            grounding_evidence=grounding_evidence or []
        )
    )


def verified_soft_result(
    source: str,
    confidence: float,
    grounding_evidence: list[str] = None
) -> TrustResult:
    """Create a VerifiedSoft (Level 2) trust result.

    Use for:
    - LLM output that has been grounded in source code
    - LLM output that has passed sandbox execution
    - LLM output with verified citations
    """
    return TrustResult(
        trusted=True,
        level=TrustLevel.VERIFIED_SOFT,
        metadata=TrustMetadata(
            level=TrustLevel.VERIFIED_SOFT,
            source=source,
            confidence=confidence,
            verifier="verified_soft",
            grounding_evidence=grounding_evidence or []
        )
    )


def unverified_result(
    source: str,
    rejection_reason: str
) -> TrustResult:
    """Create an Unverified (Level 3) trust result - REJECTED.

    Use for:
    - Pure LLM output without grounding
    - Content that failed verification
    - Any content that cannot be traced to source code

    This content MUST be rejected and never used.
    """
    return TrustResult(
        trusted=False,
        level=TrustLevel.UNVERIFIED,
        metadata=TrustMetadata(
            level=TrustLevel.UNVERIFIED,
            source=source,
            confidence=0.0,
            verifier="rejected"
        ),
        rejection_reason=rejection_reason
    )


# =============================================================================
# Trust Level Enforcement
# =============================================================================

class TrustEnforcer:
    """Enforces trust hierarchy requirements.

    Ensures that only trusted content is accepted and
    unverified content is always rejected.
    """

    def __init__(self, min_level: TrustLevel = TrustLevel.VERIFIED_SOFT):
        """Initialize enforcer with minimum acceptable trust level.

        Args:
            min_level: Minimum trust level to accept.
                      Default is VERIFIED_SOFT (Level 2).
        """
        self.min_level = min_level
        self.rejection_log: list[TrustResult] = []

    def accept(self, result: TrustResult) -> bool:
        """Check if a trust result meets minimum requirements.

        Args:
            result: Trust verification result

        Returns:
            True if content is acceptable, False otherwise
        """
        # Level 3 (Unverified) is ALWAYS rejected
        if result.level == TrustLevel.UNVERIFIED:
            self.rejection_log.append(result)
            return False

        # Check if level meets minimum
        if result.level <= self.min_level:
            return True

        self.rejection_log.append(result)
        return False

    def require_hard_content(self, result: TrustResult) -> bool:
        """Require Level 1 (HardContent) - no LLM involved."""
        return result.level == TrustLevel.HARD_CONTENT

    def get_rejection_summary(self) -> str:
        """Get summary of rejected content."""
        if not self.rejection_log:
            return "No rejections"

        lines = [f"Rejected content: {len(self.rejection_log)}"]
        for r in self.rejection_log:
            lines.append(f"  - {r.metadata.source}: {r.rejection_reason}")
        return "\n".join(lines)
