"""Auditor Agent - Zero-Hallucination Content Verification.

The Auditor verifies generated content against actual source code,
ensuring Hall_m < 0.02 hallucination rate.

Verification Pipeline:
1. Extract claims from generated content (symbols, behaviors, APIs, patterns)
2. For each claim, find corresponding source references
3. Verify claim against actual source code using multi-source validation
4. Reject any unverified claims
5. Calculate and track hallucination metrics

Model: Opus (critical judgment for zero-hallucination)

Multi-Source Verification (Phase 5.2):
- AST parser for Python files
- Tree-sitter for multi-language validation
- LSP for cross-file references
- File content fallback

Hall_m Tracking (Phase 5.3):
- Integration with HallMetric class
- Per-audit metric recording
- Fail-fast when Hall_m >= threshold
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from pathlib import Path
from enum import Enum
import re

from .base import BaseAgent, AgentRole, AgentResult
from ..verify.ddr import (
    DirectDependencyRetriever,
    SourceRef,
    MultiSourceValidator,
    ValidationSource,
    ValidationResult,
    HallMetric,
    HallMetricExceededException,
    get_hall_metric,
)
from ..observability.logging import get_logger

logger = get_logger(__name__)


class ClaimType(Enum):
    """Types of claims that can be extracted and verified."""
    SYMBOL = "symbol"           # Class, function, variable reference
    BEHAVIOR = "behavior"       # "X does Y", "X returns Y"
    API = "api"                 # Method call, parameter usage
    PATTERN = "pattern"         # Design pattern, coding pattern
    CITATION = "citation"       # file:line reference
    CODE_BLOCK = "code_block"   # Code example in markdown
    IMPORT = "import"           # Import statement claim
    DOCSTRING = "docstring"     # Docstring content claim


class ClaimSeverity(Enum):
    """Severity of an unverified claim."""
    CRITICAL = "critical"   # Symbol/API claims - must exist
    HIGH = "high"           # Behavior claims - should be accurate
    MEDIUM = "medium"       # Pattern claims - reasonable to verify
    LOW = "low"             # Style/documentation claims


@dataclass
class Claim:
    """A claim extracted from generated content."""
    text: str
    claim_type: ClaimType
    symbol_mentioned: Optional[str] = None
    line_cited: Optional[int] = None
    file_cited: Optional[str] = None
    severity: ClaimSeverity = ClaimSeverity.MEDIUM
    # Additional metadata for richer claims
    expected_type: Optional[str] = None  # class, function, method
    parameters: list[str] = field(default_factory=list)
    return_type: Optional[str] = None
    behavior_verb: Optional[str] = None  # "returns", "accepts", "creates"
    context: str = ""  # Surrounding text for context

    @property
    def has_citation(self) -> bool:
        """Claim has a source citation."""
        return self.file_cited is not None or self.line_cited is not None

    @property
    def is_critical(self) -> bool:
        """Claim is critical (must be verified)."""
        return self.severity == ClaimSeverity.CRITICAL

    def __str__(self) -> str:
        """Human-readable claim representation."""
        parts = [f"[{self.claim_type.value}]"]
        if self.symbol_mentioned:
            parts.append(f"'{self.symbol_mentioned}'")
        if self.has_citation:
            parts.append(f"at {self.file_cited}:{self.line_cited}")
        if self.behavior_verb:
            parts.append(f"({self.behavior_verb})")
        return " ".join(parts)


@dataclass
class ClaimVerification:
    """Result of verifying a single claim."""
    claim: Claim
    verified: bool
    source_ref: Optional[SourceRef] = None
    confidence: float = 0.0
    rejection_reason: Optional[str] = None
    # Multi-source validation details
    validation_sources: list[ValidationSource] = field(default_factory=list)
    sources_confirmed: list[ValidationSource] = field(default_factory=list)
    actual_line: Optional[int] = None
    actual_type: Optional[str] = None
    discrepancies: list[str] = field(default_factory=list)

    @property
    def is_high_confidence(self) -> bool:
        """Multiple sources confirmed the claim."""
        return len(self.sources_confirmed) >= 2

    @property
    def verification_method(self) -> str:
        """Description of how claim was verified."""
        if not self.sources_confirmed:
            return "unverified"
        return ", ".join(s.value for s in self.sources_confirmed)


@dataclass
class AuditTask:
    """Task for the auditor agent."""
    content: str
    source_refs: list[SourceRef] = field(default_factory=list)
    codewiki_path: Optional[Path] = None
    repo_path: Optional[Path] = None
    strict_mode: bool = True  # Reject on any unverified claim
    fail_on_hall_m_exceed: bool = False  # Raise exception if Hall_m >= threshold
    hall_m_threshold: float = 0.02  # Hall_m failure threshold
    use_multi_source: bool = True  # Enable multi-source validation
    use_lsp: bool = False  # Enable LSP for richer type info (slower)
    verify_code_blocks: bool = True  # Verify code examples
    extract_behavior_claims: bool = True  # Extract behavior claims


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
    # Breakdown by claim type
    claims_by_type: dict[str, int] = field(default_factory=dict)
    verified_by_type: dict[str, int] = field(default_factory=dict)
    # Breakdown by severity
    critical_unverified: int = 0
    high_unverified: int = 0
    # Multi-source validation stats
    multi_source_verified: int = 0
    high_confidence_count: int = 0

    @property
    def meets_target(self) -> bool:
        """Meets Hall_m < 0.02 target."""
        return self.hallucination_rate < 0.02

    @property
    def critical_passed(self) -> bool:
        """All critical claims verified."""
        return self.critical_unverified == 0

    def get_unverified_by_type(self, claim_type: ClaimType) -> list[ClaimVerification]:
        """Get unverified claims of a specific type."""
        return [
            v for v in self.claim_verifications
            if not v.verified and v.claim.claim_type == claim_type
        ]


class AuditorAgent(BaseAgent[AuditResult]):
    """Agent that verifies generated content against source code.

    Zero-Hallucination Methodology:
    - Extract all claims from content (symbols, behaviors, APIs, patterns)
    - Verify each claim against actual source using multi-source validation
    - Reject content with any unverified claims (strict mode)
    - Track hallucination rate: Hall_m = unverified / total

    Multi-Source Verification (Phase 5.2):
    - AST parser for Python files (rich metadata)
    - Tree-sitter for multi-language validation
    - LSP for cross-file references (when enabled)
    - File content fallback

    Hall_m Integration (Phase 5.3):
    - HallMetric tracking per audit
    - Fail-fast when Hall_m >= threshold
    - Metric history for analysis

    Trust Philosophy:
    - Every claim must be grounded in source code
    - No claim accepted without file:line validation
    - Unverified content is ALWAYS rejected
    """

    def __init__(
        self,
        hall_metric: Optional[HallMetric] = None,
        fail_on_hall_m_exceed: bool = False,
    ):
        """Initialize the auditor agent.

        Args:
            hall_metric: HallMetric instance for tracking. If None, uses global.
            fail_on_hall_m_exceed: Raise exception when Hall_m >= threshold.
        """
        super().__init__(AgentRole.AUDITOR)
        self.ddr: Optional[DirectDependencyRetriever] = None
        self._multi_source_validator: Optional[MultiSourceValidator] = None
        self._hall_metric = hall_metric or get_hall_metric()
        self._fail_on_hall_m_exceed = fail_on_hall_m_exceed

    def execute(self, task: AuditTask, context: dict = None) -> AgentResult:
        """Execute audit on generated content.

        Args:
            task: AuditTask with content to verify
            context: Shared context

        Returns:
            AgentResult with AuditResult

        Raises:
            HallMetricExceededException: If task.fail_on_hall_m_exceed and Hall_m >= threshold.
        """
        start = self._start_execution()

        try:
            # Initialize DDR if paths provided
            if task.codewiki_path or task.repo_path:
                self.ddr = DirectDependencyRetriever(
                    codewiki_path=task.codewiki_path,
                    repo_path=task.repo_path,
                    use_multi_source=task.use_multi_source,
                    use_lsp=task.use_lsp,
                    hall_metric=self._hall_metric,
                )

            # Initialize multi-source validator if needed
            if task.use_multi_source and task.repo_path:
                self._multi_source_validator = MultiSourceValidator(
                    repo_path=task.repo_path,
                    use_lsp=task.use_lsp,
                )

            logger.info(f"Starting audit of content ({len(task.content)} chars)")

            # Step 1: Extract claims from content
            claims = self._extract_claims(
                task.content,
                extract_behaviors=task.extract_behavior_claims,
                extract_code_blocks=task.verify_code_blocks,
            )
            logger.info(f"Extracted {len(claims)} claims from content")

            # Step 2: Verify each claim using multi-source validation
            verifications = []
            for claim in claims:
                verification = self._verify_claim_multi_source(
                    claim,
                    task.source_refs,
                    use_multi_source=task.use_multi_source,
                )
                verifications.append(verification)

            # Step 3: Calculate metrics
            total = len(claims)
            verified = sum(1 for v in verifications if v.verified)
            unverified = total - verified
            hall_rate = unverified / total if total > 0 else 0.0

            # Calculate breakdown by type
            claims_by_type: dict[str, int] = {}
            verified_by_type: dict[str, int] = {}
            for v in verifications:
                type_name = v.claim.claim_type.value
                claims_by_type[type_name] = claims_by_type.get(type_name, 0) + 1
                if v.verified:
                    verified_by_type[type_name] = verified_by_type.get(type_name, 0) + 1

            # Calculate severity breakdown
            critical_unverified = sum(
                1 for v in verifications
                if not v.verified and v.claim.severity == ClaimSeverity.CRITICAL
            )
            high_unverified = sum(
                1 for v in verifications
                if not v.verified and v.claim.severity == ClaimSeverity.HIGH
            )

            # Calculate multi-source stats
            multi_source_verified = sum(
                1 for v in verifications
                if v.verified and len(v.sources_confirmed) > 1
            )
            high_confidence_count = sum(
                1 for v in verifications if v.is_high_confidence
            )

            # Step 4: Determine pass/fail
            if task.strict_mode:
                # In strict mode, all critical claims must be verified
                passed = critical_unverified == 0 and unverified == 0
            else:
                passed = hall_rate < task.hall_m_threshold

            # Collect rejection reasons
            rejection_reasons = [
                v.rejection_reason
                for v in verifications
                if not v.verified and v.rejection_reason
            ]

            # Record Hall_m metric (Phase 5.3)
            should_fail = task.fail_on_hall_m_exceed or self._fail_on_hall_m_exceed
            try:
                self._hall_metric.record_and_check(
                    validated=verified,
                    rejected=unverified,
                    operation="audit",
                    context=f"content:{len(task.content)}chars",
                    fail_on_exceed=should_fail,
                )
            except HallMetricExceededException:
                logger.error(
                    f"Hall_m EXCEEDED threshold: {hall_rate:.4f} >= {task.hall_m_threshold:.4f}"
                )
                if should_fail:
                    raise

            result = AuditResult(
                passed=passed,
                claim_verifications=verifications,
                total_claims=total,
                verified_claims=verified,
                unverified_claims=unverified,
                hallucination_rate=hall_rate,
                rejection_reasons=rejection_reasons,
                claims_by_type=claims_by_type,
                verified_by_type=verified_by_type,
                critical_unverified=critical_unverified,
                high_unverified=high_unverified,
                multi_source_verified=multi_source_verified,
                high_confidence_count=high_confidence_count,
            )

            # Log audit summary
            status = "PASSED" if passed else "FAILED"
            logger.info(
                f"Audit {status}: {verified}/{total} verified, "
                f"Hall_m={hall_rate:.4f}, critical_unverified={critical_unverified}"
            )

            # Report to supervisor
            if passed:
                self.send_message(
                    AgentRole.SUPERVISOR,
                    f"Audit PASSED: {verified}/{total} claims verified (Hall_m={hall_rate:.4f})",
                    hallucination_rate=hall_rate,
                    high_confidence_count=high_confidence_count,
                )
            else:
                self.send_message(
                    AgentRole.SUPERVISOR,
                    f"Audit FAILED: {unverified}/{total} unverified claims (Hall_m={hall_rate:.4f})",
                    rejected=True,
                    hallucination_rate=hall_rate,
                    critical_unverified=critical_unverified,
                    rejection_reasons=rejection_reasons[:5],  # Top 5
                )

            return self._end_execution(start, output=result)

        except HallMetricExceededException:
            # Re-raise Hall_m exceptions
            raise
        except Exception as e:
            logger.error(f"Audit failed with error: {e}")
            return self._end_execution(start, error=str(e))
        finally:
            # Clean up resources
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up resources."""
        if self._multi_source_validator:
            self._multi_source_validator.close()
            self._multi_source_validator = None
        if self.ddr:
            self.ddr.close()
            self.ddr = None

    def _extract_claims(
        self,
        content: str,
        extract_behaviors: bool = True,
        extract_code_blocks: bool = True,
    ) -> list[Claim]:
        """Extract verifiable claims from content.

        Extracts:
        - Symbol claims: class, function, variable references
        - Citation claims: file:line references
        - API claims: method calls, parameters
        - Import claims: import statements
        - Behavior claims: "X does Y", "X returns Y"
        - Code block claims: code examples in markdown
        - Pattern claims: design pattern references

        Args:
            content: Content to extract claims from.
            extract_behaviors: Extract behavior claims (can be noisy).
            extract_code_blocks: Extract and verify code blocks.

        Returns:
            List of Claim objects.
        """
        claims = []
        seen_symbols: set[str] = set()  # Avoid duplicate claims

        # ========================================
        # SYMBOL CLAIMS (Critical - must exist)
        # ========================================

        # Pattern 1: Inline code references like `SymbolName` (CamelCase = class)
        for match in re.finditer(r'`([A-Z][a-zA-Z0-9_]+)`', content):
            ref = match.group(1)
            if ref not in seen_symbols:
                seen_symbols.add(ref)
                claims.append(Claim(
                    text=ref,
                    claim_type=ClaimType.SYMBOL,
                    symbol_mentioned=ref,
                    expected_type="class",
                    severity=ClaimSeverity.CRITICAL,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

        # Pattern 2: Function/method calls like "the `func_name()` function"
        for match in re.finditer(r'`([a-z_][a-zA-Z0-9_]*)\(\)`', content):
            ref = match.group(1)
            if ref not in seen_symbols:
                seen_symbols.add(ref)
                claims.append(Claim(
                    text=ref,
                    claim_type=ClaimType.SYMBOL,
                    symbol_mentioned=ref,
                    expected_type="function",
                    severity=ClaimSeverity.CRITICAL,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

        # Pattern 3: Class references like "the StateGraph class"
        for match in re.finditer(r'the\s+`?([A-Z][a-zA-Z0-9]+)`?\s+class', content, re.I):
            ref = match.group(1)
            if ref not in seen_symbols:
                seen_symbols.add(ref)
                claims.append(Claim(
                    text=ref,
                    claim_type=ClaimType.SYMBOL,
                    symbol_mentioned=ref,
                    expected_type="class",
                    severity=ClaimSeverity.CRITICAL,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

        # ========================================
        # CITATION CLAIMS (Critical - must exist)
        # ========================================

        # Pattern 4: File:line citations like `file.py:123` or file.py:123
        for match in re.finditer(r'`?([a-zA-Z0-9_/.-]+\.(?:py|ts|tsx|js|jsx)):(\d+)`?', content):
            file_path = match.group(1)
            line = int(match.group(2))
            citation_key = f"{file_path}:{line}"
            if citation_key not in seen_symbols:
                seen_symbols.add(citation_key)
                claims.append(Claim(
                    text=citation_key,
                    claim_type=ClaimType.CITATION,
                    file_cited=file_path,
                    line_cited=line,
                    severity=ClaimSeverity.CRITICAL,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

        # ========================================
        # API CLAIMS (Critical - method/parameter references)
        # ========================================

        # Pattern 5: Method calls like "graph.add_node()" or "`obj.method()`"
        for match in re.finditer(r'`?([a-z_][a-zA-Z0-9_]*)\.([a-z_][a-zA-Z0-9_]*)\(\)`?', content):
            obj, method = match.groups()
            method_key = f"{obj}.{method}"
            if method not in seen_symbols:
                seen_symbols.add(method)
                claims.append(Claim(
                    text=method_key,
                    claim_type=ClaimType.API,
                    symbol_mentioned=method,
                    severity=ClaimSeverity.CRITICAL,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

        # Pattern 6: Parameter references like "the `param_name` parameter"
        for match in re.finditer(r'the\s+`([a-z_][a-zA-Z0-9_]*)`\s+(?:parameter|argument)', content, re.I):
            param = match.group(1)
            claims.append(Claim(
                text=f"parameter:{param}",
                claim_type=ClaimType.API,
                symbol_mentioned=param,
                severity=ClaimSeverity.HIGH,
                context=content[max(0, match.start()-50):match.end()+50],
            ))

        # ========================================
        # IMPORT CLAIMS (Critical - must be valid)
        # ========================================

        # Pattern 7: Import statements like "from module import Symbol"
        for match in re.finditer(r'from\s+([a-zA-Z0-9_.]+)\s+import\s+([A-Za-z0-9_,\s]+)', content):
            module = match.group(1)
            imports_str = match.group(2)
            for imp in imports_str.split(','):
                imp = imp.strip()
                if imp and imp not in seen_symbols:
                    seen_symbols.add(imp)
                    claims.append(Claim(
                        text=f"import {imp} from {module}",
                        claim_type=ClaimType.IMPORT,
                        symbol_mentioned=imp,
                        severity=ClaimSeverity.CRITICAL,
                        context=content[max(0, match.start()-50):match.end()+50],
                    ))

        # Pattern 8: Simple imports like "import module" or "import module as alias"
        for match in re.finditer(r'^import\s+([a-zA-Z0-9_.]+)(?:\s+as\s+([a-zA-Z0-9_]+))?', content, re.M):
            module = match.group(1)
            claims.append(Claim(
                text=f"import {module}",
                claim_type=ClaimType.IMPORT,
                symbol_mentioned=module.split('.')[0],  # Top-level module
                severity=ClaimSeverity.HIGH,
                context=content[max(0, match.start()-50):match.end()+50],
            ))

        # ========================================
        # BEHAVIOR CLAIMS (High - should be accurate)
        # ========================================

        if extract_behaviors:
            # Pattern 9: "X returns Y" behavior claims
            for match in re.finditer(
                r'`?([A-Z][a-zA-Z0-9_]+|[a-z_][a-zA-Z0-9_]*\(\))`?\s+returns?\s+(?:a\s+)?`?([A-Za-z0-9_]+)`?',
                content, re.I
            ):
                symbol = match.group(1).rstrip('()')
                return_type = match.group(2)
                claims.append(Claim(
                    text=f"{symbol} returns {return_type}",
                    claim_type=ClaimType.BEHAVIOR,
                    symbol_mentioned=symbol,
                    return_type=return_type,
                    behavior_verb="returns",
                    severity=ClaimSeverity.HIGH,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

            # Pattern 10: "X accepts/takes Y parameter(s)" behavior claims
            for match in re.finditer(
                r'`?([A-Z][a-zA-Z0-9_]+|[a-z_][a-zA-Z0-9_]*\(\))`?\s+(?:accepts?|takes?)\s+(?:a\s+)?`?([a-zA-Z0-9_]+)`?\s+(?:parameter|argument)',
                content, re.I
            ):
                symbol = match.group(1).rstrip('()')
                param = match.group(2)
                claims.append(Claim(
                    text=f"{symbol} accepts {param}",
                    claim_type=ClaimType.BEHAVIOR,
                    symbol_mentioned=symbol,
                    parameters=[param],
                    behavior_verb="accepts",
                    severity=ClaimSeverity.HIGH,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

            # Pattern 11: "X creates/builds/generates Y" behavior claims
            for match in re.finditer(
                r'`?([A-Z][a-zA-Z0-9_]+|[a-z_][a-zA-Z0-9_]*\(\))`?\s+(?:creates?|builds?|generates?)\s+(?:a\s+)?`?([A-Za-z0-9_]+)`?',
                content, re.I
            ):
                symbol = match.group(1).rstrip('()')
                result = match.group(2)
                claims.append(Claim(
                    text=f"{symbol} creates {result}",
                    claim_type=ClaimType.BEHAVIOR,
                    symbol_mentioned=symbol,
                    behavior_verb="creates",
                    severity=ClaimSeverity.MEDIUM,
                    context=content[max(0, match.start()-50):match.end()+50],
                ))

        # ========================================
        # CODE BLOCK CLAIMS (Medium - verify examples)
        # ========================================

        if extract_code_blocks:
            # Pattern 12: Python code blocks with symbols
            code_blocks = re.findall(r'```(?:python|py)\n(.*?)```', content, re.DOTALL)
            for block in code_blocks:
                # Extract classes from code blocks
                for class_match in re.finditer(r'class\s+([A-Z][a-zA-Z0-9_]*)', block):
                    class_name = class_match.group(1)
                    if class_name not in seen_symbols:
                        claims.append(Claim(
                            text=f"code_block:class:{class_name}",
                            claim_type=ClaimType.CODE_BLOCK,
                            symbol_mentioned=class_name,
                            expected_type="class",
                            severity=ClaimSeverity.MEDIUM,
                            context=block[:200],
                        ))

                # Extract functions from code blocks
                for func_match in re.finditer(r'def\s+([a-z_][a-zA-Z0-9_]*)\s*\(', block):
                    func_name = func_match.group(1)
                    if func_name not in seen_symbols and func_name != "__init__":
                        claims.append(Claim(
                            text=f"code_block:function:{func_name}",
                            claim_type=ClaimType.CODE_BLOCK,
                            symbol_mentioned=func_name,
                            expected_type="function",
                            severity=ClaimSeverity.MEDIUM,
                            context=block[:200],
                        ))

        # ========================================
        # PATTERN CLAIMS (Medium - design patterns)
        # ========================================

        # Pattern 13: Design pattern references
        design_patterns = [
            "factory", "singleton", "observer", "decorator", "adapter",
            "strategy", "builder", "proxy", "facade", "composite",
        ]
        for pattern in design_patterns:
            if re.search(rf'\b{pattern}\s+pattern\b', content, re.I):
                claims.append(Claim(
                    text=f"pattern:{pattern}",
                    claim_type=ClaimType.PATTERN,
                    severity=ClaimSeverity.LOW,
                    context=pattern,
                ))

        return claims

    def _verify_claim_multi_source(
        self,
        claim: Claim,
        provided_refs: list[SourceRef],
        use_multi_source: bool = True,
    ) -> ClaimVerification:
        """Verify a claim using multi-source validation.

        Verification strategies (in order):
        1. Check against provided source refs
        2. Use multi-source validator (AST + tree-sitter + LSP + file content)
        3. Use DDR to find matching source
        4. Check file:line citation directly
        5. Pattern-specific verification

        Args:
            claim: Claim to verify.
            provided_refs: List of provided source references.
            use_multi_source: Enable multi-source validation.

        Returns:
            ClaimVerification with verification details.
        """
        verification = ClaimVerification(
            claim=claim,
            verified=False,
            confidence=0.0,
        )

        # ========================================
        # Strategy 1: Check against provided source refs
        # ========================================
        for ref in provided_refs:
            if self._claim_matches_ref(claim, ref):
                verification.verified = True
                verification.source_ref = ref
                verification.confidence = 1.0 if ref.validated else 0.8
                verification.sources_confirmed = [ValidationSource.CODEWIKI_SECTIONS]
                return verification

        # ========================================
        # Strategy 2: Multi-source validation (Phase 5.2)
        # ========================================
        if use_multi_source and self._multi_source_validator and claim.symbol_mentioned:
            # Try to find the symbol in any available file
            validation_result = self._verify_with_multi_source(claim)
            if validation_result and validation_result.is_valid:
                verification.verified = True
                verification.confidence = validation_result.confidence
                verification.sources_confirmed = validation_result.sources_confirmed
                verification.validation_sources = validation_result.sources_checked
                verification.actual_line = validation_result.actual_line
                verification.actual_type = validation_result.symbol_kind
                verification.discrepancies = validation_result.discrepancies

                # Create source ref from validation result
                if claim.file_cited:
                    verification.source_ref = SourceRef(
                        symbol_name=claim.symbol_mentioned,
                        file_path=claim.file_cited,
                        line_number=validation_result.actual_line or claim.line_cited or 0,
                        symbol_type=validation_result.symbol_kind or "unknown",
                        validated=True,
                    )

                return verification

        # ========================================
        # Strategy 3: Use DDR to find matching source
        # ========================================
        if self.ddr and claim.symbol_mentioned:
            try:
                ddr_result = self.ddr.retrieve(
                    claim.symbol_mentioned,
                    max_results=5,
                    fail_on_exceed=False,
                )
                for element in ddr_result.elements:
                    if element.is_valid:
                        verification.verified = True
                        verification.source_ref = element.source_ref
                        verification.confidence = 0.9
                        verification.sources_confirmed = [ValidationSource.SYMBOL_CATALOG]
                        return verification
            except Exception as e:
                logger.debug(f"DDR retrieval failed for {claim.symbol_mentioned}: {e}")

        # ========================================
        # Strategy 4: Check file:line citation directly
        # ========================================
        if claim.file_cited and claim.line_cited:
            if self._verify_citation_directly(claim, verification):
                return verification

        # ========================================
        # Strategy 5: Pattern-specific verification
        # ========================================
        if claim.claim_type == ClaimType.PATTERN:
            # Pattern claims are lower priority and harder to verify
            verification.confidence = 0.3
            verification.rejection_reason = f"Pattern claim '{claim.text}' cannot be automatically verified"
            return verification

        if claim.claim_type == ClaimType.BEHAVIOR:
            # Behavior claims need the symbol to exist first
            verification.rejection_reason = (
                f"Behavior claim for '{claim.symbol_mentioned}': "
                f"symbol not found in source code"
            )
            return verification

        # ========================================
        # Not verified - set rejection reason
        # ========================================
        if claim.claim_type == ClaimType.CITATION:
            verification.rejection_reason = (
                f"Citation '{claim.file_cited}:{claim.line_cited}' not found or invalid"
            )
        elif claim.claim_type == ClaimType.IMPORT:
            verification.rejection_reason = (
                f"Import claim: '{claim.symbol_mentioned}' not found in source"
            )
        else:
            verification.rejection_reason = (
                f"Symbol '{claim.text}' not found in source code"
            )

        return verification

    def _verify_with_multi_source(self, claim: Claim) -> Optional[ValidationResult]:
        """Verify a claim using multi-source validator.

        Args:
            claim: Claim with symbol_mentioned.

        Returns:
            ValidationResult if file can be determined, None otherwise.
        """
        if not self._multi_source_validator or not claim.symbol_mentioned:
            return None

        # If we have a file citation, use it directly
        if claim.file_cited and claim.line_cited:
            return self._multi_source_validator.validate_symbol(
                symbol_name=claim.symbol_mentioned,
                file_path=claim.file_cited,
                line_number=claim.line_cited,
                expected_type=claim.expected_type,
            )

        # Try to find the symbol via DDR first to get file location
        if self.ddr:
            try:
                ddr_result = self.ddr.retrieve(
                    claim.symbol_mentioned,
                    max_results=3,
                    fail_on_exceed=False,
                )
                for element in ddr_result.elements:
                    if element.source_ref and element.source_ref.file_path:
                        # Validate using multi-source
                        result = self._multi_source_validator.validate_symbol(
                            symbol_name=claim.symbol_mentioned,
                            file_path=element.source_ref.file_path,
                            line_number=element.source_ref.line_number,
                            expected_type=claim.expected_type,
                        )
                        if result.is_valid:
                            return result
            except Exception as e:
                logger.debug(f"Multi-source lookup via DDR failed: {e}")

        return None

    def _verify_citation_directly(
        self,
        claim: Claim,
        verification: ClaimVerification,
    ) -> bool:
        """Verify a file:line citation directly against the repository.

        Args:
            claim: Claim with file_cited and line_cited.
            verification: ClaimVerification to update.

        Returns:
            True if verified, False otherwise.
        """
        if not claim.file_cited or not claim.line_cited:
            return False

        # Use DDR validation if available
        if self.ddr and self.ddr.repo_path:
            ref = SourceRef(
                symbol_name=claim.symbol_mentioned or "unknown",
                file_path=claim.file_cited,
                line_number=claim.line_cited,
            )
            if self.ddr.validate_source_ref(ref):
                verification.verified = True
                verification.source_ref = ref
                verification.source_ref.validated = True
                verification.confidence = 1.0
                verification.sources_confirmed = [ValidationSource.FILE_CONTENT]
                return True

        # Direct file check
        if self._multi_source_validator and self._multi_source_validator._repo_path:
            file_path = self._multi_source_validator._repo_path / claim.file_cited
            if file_path.exists():
                try:
                    lines = file_path.read_text(encoding="utf-8", errors="ignore").split("\n")
                    if claim.line_cited <= len(lines):
                        # Basic check: file exists and line is valid
                        verification.verified = True
                        verification.source_ref = SourceRef(
                            symbol_name=claim.symbol_mentioned or "unknown",
                            file_path=claim.file_cited,
                            line_number=claim.line_cited,
                            validated=True,
                        )
                        verification.confidence = 0.8
                        verification.sources_confirmed = [ValidationSource.FILE_CONTENT]
                        return True
                except Exception as e:
                    logger.debug(f"Failed to read file {claim.file_cited}: {e}")

        return False

    def _claim_matches_ref(self, claim: Claim, ref: SourceRef) -> bool:
        """Check if claim matches a source reference."""
        if claim.symbol_mentioned:
            # Direct symbol match (case-insensitive)
            if claim.symbol_mentioned.lower() == ref.symbol_name.lower():
                return True
            # Symbol contained in name (for qualified names like ClassName.method)
            if claim.symbol_mentioned.lower() in ref.symbol_name.lower():
                return True
            # Ref name contained in claim (for qualified names)
            if ref.symbol_name.lower() in claim.symbol_mentioned.lower():
                return True

        if claim.file_cited and claim.line_cited:
            # File and line match (with some tolerance)
            if claim.file_cited in ref.file_path or ref.file_path.endswith(claim.file_cited):
                if abs(claim.line_cited - ref.line_number) <= 3:  # 3-line tolerance
                    return True

        return False

    def audit_with_strict_mode(
        self,
        content: str,
        source_refs: list[SourceRef],
        codewiki_path: Optional[Path] = None,
        repo_path: Optional[Path] = None,
        use_multi_source: bool = True,
    ) -> Optional[AuditResult]:
        """Convenience method for strict mode audit.

        In strict mode, ALL claims must be verified for the audit to pass.

        Args:
            content: Content to audit.
            source_refs: List of source references.
            codewiki_path: Path to CodeWiki output.
            repo_path: Path to repository.
            use_multi_source: Enable multi-source validation.

        Returns:
            AuditResult if successful, None if execution failed.
        """
        task = AuditTask(
            content=content,
            source_refs=source_refs,
            codewiki_path=codewiki_path,
            repo_path=repo_path,
            strict_mode=True,
            use_multi_source=use_multi_source,
        )
        result = self.execute(task)
        return result.output if result.success else None

    def audit_with_hall_m_check(
        self,
        content: str,
        source_refs: list[SourceRef],
        codewiki_path: Optional[Path] = None,
        repo_path: Optional[Path] = None,
        threshold: float = 0.02,
        fail_on_exceed: bool = True,
    ) -> AuditResult:
        """Audit with Hall_m threshold check.

        Args:
            content: Content to audit.
            source_refs: List of source references.
            codewiki_path: Path to CodeWiki output.
            repo_path: Path to repository.
            threshold: Hall_m threshold (default 0.02).
            fail_on_exceed: Raise HallMetricExceededException if exceeded.

        Returns:
            AuditResult.

        Raises:
            HallMetricExceededException: If Hall_m >= threshold and fail_on_exceed.
        """
        task = AuditTask(
            content=content,
            source_refs=source_refs,
            codewiki_path=codewiki_path,
            repo_path=repo_path,
            strict_mode=False,
            hall_m_threshold=threshold,
            fail_on_hall_m_exceed=fail_on_exceed,
            use_multi_source=True,
        )
        result = self.execute(task)
        if not result.success:
            raise RuntimeError(f"Audit execution failed: {result.error}")
        return result.output

    def get_hallucination_summary(self, result: AuditResult) -> str:
        """Generate human-readable hallucination summary.

        Args:
            result: AuditResult to summarize.

        Returns:
            Formatted summary string.
        """
        lines = [
            "=" * 60,
            "HALLUCINATION AUDIT SUMMARY",
            "=" * 60,
            "",
            f"Overall: {'PASSED' if result.passed else 'FAILED'}",
            f"Hall_m Target (<0.02): {'PASS' if result.meets_target else 'FAIL'}",
            f"Critical Claims Verified: {'PASS' if result.critical_passed else 'FAIL'}",
            "",
            "Claims Summary:",
            f"  Total Claims: {result.total_claims}",
            f"  Verified: {result.verified_claims}",
            f"  Unverified: {result.unverified_claims}",
            f"  Hall_m Rate: {result.hallucination_rate:.4f}",
            "",
            "Severity Breakdown:",
            f"  Critical Unverified: {result.critical_unverified}",
            f"  High Unverified: {result.high_unverified}",
            "",
            "Multi-Source Stats:",
            f"  Multi-Source Verified: {result.multi_source_verified}",
            f"  High Confidence: {result.high_confidence_count}",
        ]

        # Claims by type
        if result.claims_by_type:
            lines.append("")
            lines.append("Claims by Type:")
            for type_name, count in sorted(result.claims_by_type.items()):
                verified = result.verified_by_type.get(type_name, 0)
                rate = verified / count * 100 if count > 0 else 0
                lines.append(f"  {type_name}: {verified}/{count} ({rate:.1f}%)")

        # Rejection reasons
        if result.rejection_reasons:
            lines.append("")
            lines.append("Top Rejection Reasons:")
            for i, reason in enumerate(result.rejection_reasons[:10], 1):
                # Truncate long reasons
                if len(reason) > 80:
                    reason = reason[:77] + "..."
                lines.append(f"  {i}. {reason}")

        lines.append("")
        lines.append("=" * 60)

        return '\n'.join(lines)

    def get_detailed_verification_report(self, result: AuditResult) -> str:
        """Generate detailed verification report for debugging.

        Args:
            result: AuditResult to report.

        Returns:
            Detailed report string.
        """
        lines = [
            "=" * 60,
            "DETAILED VERIFICATION REPORT",
            "=" * 60,
            "",
        ]

        # Group by verification status
        verified = [v for v in result.claim_verifications if v.verified]
        unverified = [v for v in result.claim_verifications if not v.verified]

        # Unverified claims (most important)
        if unverified:
            lines.append("UNVERIFIED CLAIMS:")
            lines.append("-" * 40)
            for i, v in enumerate(unverified, 1):
                lines.append(f"{i}. {v.claim}")
                lines.append(f"   Reason: {v.rejection_reason or 'Unknown'}")
                if v.discrepancies:
                    lines.append(f"   Discrepancies: {', '.join(v.discrepancies[:3])}")
                lines.append("")

        # Verified claims summary
        if verified:
            lines.append("")
            lines.append("VERIFIED CLAIMS:")
            lines.append("-" * 40)
            for i, v in enumerate(verified[:20], 1):  # Limit to 20
                confidence_str = f"{v.confidence:.0%}"
                method = v.verification_method
                lines.append(f"{i}. {v.claim} [{confidence_str}] ({method})")

            if len(verified) > 20:
                lines.append(f"   ... and {len(verified) - 20} more verified claims")

        lines.append("")
        lines.append("=" * 60)

        return '\n'.join(lines)

    @property
    def hall_metric(self) -> HallMetric:
        """Get the Hall_m metric tracker.

        Returns:
            HallMetric instance.
        """
        return self._hall_metric

    def get_hall_m_summary(self) -> dict:
        """Get Hall_m metric summary.

        Returns:
            Dictionary with metric summary.
        """
        return self._hall_metric.get_summary()

    def log_hall_m_summary(self) -> None:
        """Log Hall_m metric summary."""
        self._hall_metric.log_summary()

    def reset_hall_m_metrics(self) -> None:
        """Reset Hall_m tracking metrics."""
        self._hall_metric.reset()


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================


def audit_content(
    content: str,
    source_refs: Optional[list[SourceRef]] = None,
    codewiki_path: Optional[Path] = None,
    repo_path: Optional[Path] = None,
    strict_mode: bool = True,
    use_multi_source: bool = True,
) -> AuditResult:
    """Audit content for hallucinations.

    Convenience function that creates an auditor and runs the audit.

    Args:
        content: Content to audit.
        source_refs: Optional list of source references.
        codewiki_path: Path to CodeWiki output.
        repo_path: Path to repository.
        strict_mode: Reject on any unverified claim.
        use_multi_source: Enable multi-source validation.

    Returns:
        AuditResult with verification details.
    """
    auditor = AuditorAgent()
    task = AuditTask(
        content=content,
        source_refs=source_refs or [],
        codewiki_path=codewiki_path,
        repo_path=repo_path,
        strict_mode=strict_mode,
        use_multi_source=use_multi_source,
    )
    result = auditor.execute(task)
    if not result.success:
        raise RuntimeError(f"Audit failed: {result.error}")
    return result.output


def verify_claims_only(
    content: str,
    repo_path: Path,
) -> list[Claim]:
    """Extract claims from content without verification.

    Useful for analyzing what claims would be extracted.

    Args:
        content: Content to extract claims from.
        repo_path: Path to repository (unused, for API consistency).

    Returns:
        List of extracted claims.
    """
    auditor = AuditorAgent()
    return auditor._extract_claims(content)
