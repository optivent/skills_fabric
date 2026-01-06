"""Combined Hallucination Metrics.

Based on research:
- Individual metrics: ~56-62% ROC-AUC (barely better than random)
- Combined metrics: 69-75% ROC-AUC (substantial improvement)

5 Categories of Hallucination:
1. Intent Conflicting - Code doesn't match request
2. Context Inconsistency - Contradicts provided context
3. Dead Code - Unreachable/unused code
4. Knowledge Conflicting - Wrong API/syntax
5. Package Hallucination - Non-existent packages
"""

from dataclasses import dataclass, field
from typing import Optional, Any
import re
from pathlib import Path


@dataclass
class HallucinationMetrics:
    """Comprehensive hallucination measurement metrics.

    Uses 5 categories with weighted composite scoring.
    """
    # Core metric (our original)
    hall_m: float = 0.0  # uncited_claims / total_claims

    # Extended metrics
    api_accuracy: float = 1.0     # % correct API calls
    package_validity: float = 1.0  # % real packages
    type_correctness: float = 1.0  # % type-valid code
    semantic_fidelity: float = 1.0 # similarity to source docs

    # Category-specific metrics
    intent_conflicts: int = 0      # Code doesn't match request
    context_inconsistencies: int = 0  # Contradicts context
    dead_code_instances: int = 0   # Unreachable code
    knowledge_conflicts: int = 0   # Wrong API/syntax
    package_hallucinations: int = 0  # Non-existent packages

    # Totals for calculation
    total_claims: int = 0
    verified_claims: int = 0
    unverified_claims: int = 0

    @property
    def composite_score(self) -> float:
        """Weighted composite hallucination score (0-1, higher is better)."""
        return (
            0.30 * (1 - self.hall_m) +
            0.25 * self.api_accuracy +
            0.20 * self.package_validity +
            0.15 * self.type_correctness +
            0.10 * self.semantic_fidelity
        )

    @property
    def meets_target(self) -> bool:
        """Meets Hall_m < 0.02 target."""
        return self.hall_m < 0.02

    @property
    def category_score(self) -> float:
        """Score based on category counts (0-1, higher is better)."""
        total_issues = (
            self.intent_conflicts +
            self.context_inconsistencies +
            self.dead_code_instances +
            self.knowledge_conflicts +
            self.package_hallucinations
        )
        # Assume max 10 issues per category for normalization
        max_expected = 50
        return max(0, 1 - (total_issues / max_expected))

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'hall_m': self.hall_m,
            'api_accuracy': self.api_accuracy,
            'package_validity': self.package_validity,
            'type_correctness': self.type_correctness,
            'semantic_fidelity': self.semantic_fidelity,
            'intent_conflicts': self.intent_conflicts,
            'context_inconsistencies': self.context_inconsistencies,
            'dead_code_instances': self.dead_code_instances,
            'knowledge_conflicts': self.knowledge_conflicts,
            'package_hallucinations': self.package_hallucinations,
            'total_claims': self.total_claims,
            'verified_claims': self.verified_claims,
            'unverified_claims': self.unverified_claims,
            'composite_score': self.composite_score,
            'meets_target': self.meets_target,
        }


class HallucinationAnalyzer:
    """Analyzes content for hallucinations across 5 categories."""

    def __init__(self, known_packages: Optional[set] = None):
        """Initialize analyzer.

        Args:
            known_packages: Set of known valid package names
        """
        self.known_packages = known_packages or self._get_common_packages()

    def _get_common_packages(self) -> set:
        """Return set of commonly known Python packages."""
        return {
            # Standard library
            'os', 'sys', 'json', 're', 'time', 'datetime', 'collections',
            'itertools', 'functools', 'pathlib', 'typing', 'dataclasses',
            'asyncio', 'threading', 'multiprocessing', 'subprocess',
            'logging', 'unittest', 'pytest', 'abc', 'enum', 'copy',
            # Common third-party
            'numpy', 'pandas', 'requests', 'flask', 'django', 'fastapi',
            'pydantic', 'sqlalchemy', 'pytest', 'black', 'mypy', 'ruff',
            'anthropic', 'openai', 'langchain', 'langgraph', 'docling',
            'transformers', 'torch', 'tensorflow', 'sklearn', 'scipy',
            'matplotlib', 'seaborn', 'plotly', 'boto3', 'google',
            'aiohttp', 'httpx', 'redis', 'celery', 'click', 'typer',
            'rich', 'loguru', 'structlog', 'tqdm', 'PIL', 'cv2',
            'yaml', 'toml', 'dotenv', 'cryptography', 'jwt', 'kuzu',
        }

    def analyze(self, content: str, context: dict = None) -> HallucinationMetrics:
        """Analyze content for hallucinations.

        Args:
            content: Content to analyze
            context: Additional context (source_refs, symbol_catalog, etc.)

        Returns:
            HallucinationMetrics with all measurements
        """
        context = context or {}
        metrics = HallucinationMetrics()

        # Extract all claims
        claims = self._extract_claims(content)
        metrics.total_claims = len(claims)

        # Verify claims against context
        verified, unverified = self._verify_claims(claims, context)
        metrics.verified_claims = len(verified)
        metrics.unverified_claims = len(unverified)
        metrics.hall_m = len(unverified) / len(claims) if claims else 0.0

        # Check API accuracy
        api_calls = self._extract_api_calls(content)
        valid_apis = self._verify_apis(api_calls, context)
        metrics.api_accuracy = len(valid_apis) / len(api_calls) if api_calls else 1.0

        # Check package validity
        packages = self._extract_packages(content)
        valid_packages = [p for p in packages if self._is_valid_package(p)]
        metrics.package_validity = len(valid_packages) / len(packages) if packages else 1.0
        metrics.package_hallucinations = len(packages) - len(valid_packages)

        # Check type correctness (simplified)
        type_issues = self._check_type_issues(content)
        metrics.type_correctness = 1.0 - (len(type_issues) / 20)  # Normalize
        metrics.type_correctness = max(0, metrics.type_correctness)

        # Analyze by category
        metrics.intent_conflicts = self._count_intent_conflicts(content, context)
        metrics.context_inconsistencies = self._count_context_inconsistencies(content, context)
        metrics.dead_code_instances = self._count_dead_code(content)
        metrics.knowledge_conflicts = len(unverified)  # Approximation

        return metrics

    def _extract_claims(self, content: str) -> list[dict]:
        """Extract verifiable claims from content."""
        claims = []

        # Symbol references
        symbols = re.findall(r'`([A-Z][a-zA-Z0-9_]+)`', content)
        for sym in symbols:
            claims.append({'type': 'symbol', 'text': sym})

        # Function references
        functions = re.findall(r'`([a-z_][a-zA-Z0-9_]*)\(\)`', content)
        for func in functions:
            claims.append({'type': 'function', 'text': func})

        # File citations
        citations = re.findall(r'`?([a-zA-Z0-9_/]+\.py):(\d+)`?', content)
        for file, line in citations:
            claims.append({'type': 'citation', 'file': file, 'line': int(line)})

        return claims

    def _verify_claims(self, claims: list, context: dict) -> tuple[list, list]:
        """Verify claims against context."""
        source_refs = context.get('source_refs', [])
        symbol_catalog = context.get('symbol_catalog', {})

        verified = []
        unverified = []

        for claim in claims:
            is_verified = False

            # Check symbol catalog
            if claim['type'] in ['symbol', 'function']:
                if claim['text'] in symbol_catalog:
                    is_verified = True
                # Check source refs
                for ref in source_refs:
                    if hasattr(ref, 'symbol_name') and claim['text'].lower() in ref.symbol_name.lower():
                        is_verified = True
                        break

            if is_verified:
                verified.append(claim)
            else:
                unverified.append(claim)

        return verified, unverified

    def _extract_api_calls(self, content: str) -> list[str]:
        """Extract API calls from content."""
        # Pattern: object.method() or module.function()
        calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)
        return [f"{obj}.{method}" for obj, method in calls]

    def _verify_apis(self, api_calls: list, context: dict) -> list[str]:
        """Verify API calls are valid."""
        # This would ideally check against documentation
        # For now, return all as valid (would need DDR integration)
        return api_calls

    def _extract_packages(self, content: str) -> list[str]:
        """Extract imported package names."""
        packages = set()

        # import X
        for match in re.finditer(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.M):
            packages.add(match.group(1))

        # from X import Y
        for match in re.finditer(r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import', content, re.M):
            root = match.group(1).split('.')[0]
            packages.add(root)

        return list(packages)

    def _is_valid_package(self, package: str) -> bool:
        """Check if package is known to be valid."""
        return package in self.known_packages

    def _check_type_issues(self, content: str) -> list[str]:
        """Check for type-related issues (simplified)."""
        issues = []

        # Pattern: obvious type mismatches in assignments
        # This is simplified; real implementation would use type inference

        return issues

    def _count_intent_conflicts(self, content: str, context: dict) -> int:
        """Count intent conflicts (code doesn't match request)."""
        # Would need the original request to compare
        # For now, return 0
        return 0

    def _count_context_inconsistencies(self, content: str, context: dict) -> int:
        """Count context inconsistencies."""
        count = 0

        # Check for contradictory statements (simplified)
        # "X is always Y" followed by "X can be Z"
        # Would need NLP for proper detection

        return count

    def _count_dead_code(self, content: str) -> int:
        """Count dead code instances in code blocks."""
        count = 0

        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        for block in code_blocks:
            # Check for return statements followed by more code
            lines = block.split('\n')
            in_function = False
            returned = False
            indent_at_return = 0

            for line in lines:
                stripped = line.lstrip()
                current_indent = len(line) - len(stripped)

                if stripped.startswith('def '):
                    in_function = True
                    returned = False

                if in_function and returned:
                    # Code after return at same or deeper indent = dead
                    if current_indent >= indent_at_return and stripped:
                        count += 1

                if stripped.startswith('return '):
                    returned = True
                    indent_at_return = current_indent

        return count

    def get_summary(self, metrics: HallucinationMetrics) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "HALLUCINATION METRICS SUMMARY",
            "=" * 60,
            "",
            f"Hall_m Rate: {metrics.hall_m:.4f} (target < 0.02)",
            f"Target Met: {'YES' if metrics.meets_target else 'NO'}",
            "",
            "Composite Scores:",
            f"  Overall Score: {metrics.composite_score:.2f}",
            f"  API Accuracy: {metrics.api_accuracy:.2%}",
            f"  Package Validity: {metrics.package_validity:.2%}",
            f"  Type Correctness: {metrics.type_correctness:.2%}",
            f"  Semantic Fidelity: {metrics.semantic_fidelity:.2%}",
            "",
            "Claims:",
            f"  Total: {metrics.total_claims}",
            f"  Verified: {metrics.verified_claims}",
            f"  Unverified: {metrics.unverified_claims}",
            "",
            "Category Issues:",
            f"  Intent Conflicts: {metrics.intent_conflicts}",
            f"  Context Inconsistencies: {metrics.context_inconsistencies}",
            f"  Dead Code: {metrics.dead_code_instances}",
            f"  Knowledge Conflicts: {metrics.knowledge_conflicts}",
            f"  Package Hallucinations: {metrics.package_hallucinations}",
            "",
            "=" * 60,
        ]
        return '\n'.join(lines)
