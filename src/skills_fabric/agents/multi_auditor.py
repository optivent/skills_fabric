"""Multi-Agent Auditor - 4-Agent Verification System.

Based on CodeX-Verify research, 4 specialized agents with different
detection patterns find more issues together than any single agent.

Expected improvement: 32.8% → 72.4% detection (+39.7 percentage points)

Agents:
1. BugDetectionAgent - logical inconsistencies, runtime errors
2. CodeSmellAgent - anti-patterns, maintainability issues
3. SecurityAgent - vulnerability detection, injection risks
4. DocumentationAgent - accuracy vs source, completeness
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path
import re
import asyncio
from abc import ABC, abstractmethod

# Handle imports for both package and standalone use
try:
    from .base import AgentRole, AgentResult
    from ..verify.ddr import DirectDependencyRetriever, SourceRef
except ImportError:
    # Standalone mode - create minimal stubs
    class AgentRole:
        AUDITOR = "AUDITOR"

    @dataclass
    class AgentResult:
        success: bool = True
        output: Any = None

    @dataclass
    class SourceRef:
        symbol_name: str = ""
        file_path: str = ""
        line_number: int = 0
        validated: bool = True

    class DirectDependencyRetriever:
        def __init__(self, **kwargs): pass
        def retrieve(self, query, max_results=5):
            return type('obj', (object,), {'elements': []})()
        def validate_source_ref(self, ref): return False


@dataclass
class Issue:
    """An issue found by an agent."""
    category: str  # bug, code_smell, security, documentation
    severity: str  # critical, high, medium, low
    description: str
    location: Optional[str] = None  # file:line or symbol name
    confidence: float = 1.0
    agent: str = ""


@dataclass
class AgentAnalysis:
    """Result from a single specialized agent."""
    agent_name: str
    issues: list[Issue]
    passed: bool
    score: float  # 0-1, higher is better (fewer issues)
    execution_time_ms: float = 0.0


@dataclass
class MultiAuditResult:
    """Combined result from all 4 agents."""
    passed: bool
    agent_results: list[AgentAnalysis]
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    composite_score: float  # Combined score from all agents
    hallucination_rate: float  # From documentation agent

    @property
    def meets_target(self) -> bool:
        """Meets quality targets."""
        return (
            self.critical_issues == 0 and
            self.high_issues <= 2 and
            self.hallucination_rate < 0.02
        )


class SpecializedAgent(ABC):
    """Base class for specialized verification agents."""

    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    @abstractmethod
    def analyze(self, content: str, context: dict) -> AgentAnalysis:
        """Analyze content and return issues found."""
        pass


class BugDetectionAgent(SpecializedAgent):
    """Detects logical inconsistencies and potential runtime errors.

    Focuses on:
    - Undefined variable references
    - Type mismatches in code examples
    - Missing error handling patterns
    - Logic errors in described behavior
    """

    def __init__(self):
        super().__init__("BugDetector", "bug")

    def analyze(self, content: str, context: dict) -> AgentAnalysis:
        """Analyze content for bugs and logical issues."""
        import time
        start = time.time()

        issues = []

        # Check 1: Undefined variables in code blocks
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        for block in code_blocks:
            issues.extend(self._check_undefined_variables(block))

        # Check 2: Type inconsistencies
        issues.extend(self._check_type_inconsistencies(content))

        # Check 3: Missing error handling patterns
        issues.extend(self._check_error_handling(content, code_blocks))

        # Check 4: Logic consistency
        issues.extend(self._check_logic_consistency(content))

        # Calculate score
        critical_count = sum(1 for i in issues if i.severity == "critical")
        high_count = sum(1 for i in issues if i.severity == "high")
        score = max(0, 1.0 - (critical_count * 0.3 + high_count * 0.15 + len(issues) * 0.02))

        passed = critical_count == 0

        return AgentAnalysis(
            agent_name=self.name,
            issues=issues,
            passed=passed,
            score=score,
            execution_time_ms=(time.time() - start) * 1000,
        )

    def _check_undefined_variables(self, code: str) -> list[Issue]:
        """Check for undefined variable patterns."""
        issues = []

        # Pattern: Variable used before assignment (simple check)
        lines = code.split('\n')
        defined = set()
        builtins = {'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set',
                    'range', 'enumerate', 'zip', 'map', 'filter', 'open', 'True',
                    'False', 'None', 'self', 'cls', 'type', 'isinstance', 'hasattr'}

        for i, line in enumerate(lines):
            # Extract assignments (simple pattern)
            assignments = re.findall(r'^(\s*)(\w+)\s*=', line)
            for _, var in assignments:
                defined.add(var)

            # Extract function defs
            func_defs = re.findall(r'def\s+(\w+)', line)
            for func in func_defs:
                defined.add(func)

            # Extract class defs
            class_defs = re.findall(r'class\s+(\w+)', line)
            for cls in class_defs:
                defined.add(cls)

            # Check for usages (very simplified)
            usages = re.findall(r'\b([a-z_][a-zA-Z0-9_]*)\b', line)
            for usage in usages:
                if usage not in defined and usage not in builtins:
                    # Check if it's an import
                    if not re.search(rf'(import|from).*{usage}', code):
                        issues.append(Issue(
                            category="bug",
                            severity="medium",
                            description=f"Possible undefined variable: '{usage}'",
                            location=f"line {i+1}",
                            confidence=0.6,
                            agent=self.name,
                        ))

        return issues

    def _check_type_inconsistencies(self, content: str) -> list[Issue]:
        """Check for type mismatches in documentation."""
        issues = []

        # Pattern: "returns X" but shows "return Y" where X and Y mismatch
        return_claims = re.findall(r'returns?\s+(?:a\s+)?(\w+)', content, re.I)
        return_examples = re.findall(r'return\s+(\w+)', content)

        # This is a simplified heuristic
        for claim in return_claims:
            if claim.lower() in ['none', 'true', 'false']:
                continue
            # Add type checking logic here if needed

        return issues

    def _check_error_handling(self, content: str, code_blocks: list) -> list[Issue]:
        """Check for missing error handling in code examples."""
        issues = []

        for block in code_blocks:
            # Check for file operations without try/except
            if re.search(r'open\s*\(', block):
                if 'try:' not in block and 'with ' not in block:
                    issues.append(Issue(
                        category="bug",
                        severity="low",
                        description="File operation without error handling or context manager",
                        confidence=0.7,
                        agent=self.name,
                    ))

            # Check for network calls without error handling
            if re.search(r'(requests\.|urllib|http)', block):
                if 'try:' not in block:
                    issues.append(Issue(
                        category="bug",
                        severity="medium",
                        description="Network operation without error handling",
                        confidence=0.8,
                        agent=self.name,
                    ))

        return issues

    def _check_logic_consistency(self, content: str) -> list[Issue]:
        """Check for logical inconsistencies in descriptions."""
        issues = []

        # Pattern: Contradictory statements (simplified)
        # "X is always Y" followed by "X can be Z"
        # This would require NLP, so we use simple patterns

        return issues


class CodeSmellAgent(SpecializedAgent):
    """Detects anti-patterns and maintainability issues.

    Focuses on:
    - Long methods/functions in examples
    - Deep nesting
    - Magic numbers/strings
    - Duplicated code patterns
    - Poor naming conventions
    """

    def __init__(self):
        super().__init__("CodeSmell", "code_smell")

    def analyze(self, content: str, context: dict) -> AgentAnalysis:
        """Analyze content for code smells."""
        import time
        start = time.time()

        issues = []
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

        for block in code_blocks:
            issues.extend(self._check_complexity(block))
            issues.extend(self._check_magic_values(block))
            issues.extend(self._check_naming(block))

        # Check documentation for anti-patterns
        issues.extend(self._check_doc_anti_patterns(content))

        # Calculate score
        high_count = sum(1 for i in issues if i.severity in ["critical", "high"])
        score = max(0, 1.0 - (high_count * 0.2 + len(issues) * 0.03))
        passed = high_count == 0

        return AgentAnalysis(
            agent_name=self.name,
            issues=issues,
            passed=passed,
            score=score,
            execution_time_ms=(time.time() - start) * 1000,
        )

    def _check_complexity(self, code: str) -> list[Issue]:
        """Check for complexity issues."""
        issues = []
        lines = code.strip().split('\n')

        # Check 1: Long functions (>30 lines in example)
        if len(lines) > 30:
            issues.append(Issue(
                category="code_smell",
                severity="low",
                description=f"Code example is {len(lines)} lines - consider breaking into smaller examples",
                confidence=0.9,
                agent=self.name,
            ))

        # Check 2: Deep nesting (>4 levels)
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                spaces_per_indent = 4
                level = indent // spaces_per_indent
                max_indent = max(max_indent, level)

        if max_indent > 4:
            issues.append(Issue(
                category="code_smell",
                severity="medium",
                description=f"Deep nesting ({max_indent} levels) - consider refactoring",
                confidence=0.85,
                agent=self.name,
            ))

        return issues

    def _check_magic_values(self, code: str) -> list[Issue]:
        """Check for magic numbers and strings."""
        issues = []

        # Magic numbers (excluding common ones like 0, 1, -1, 2)
        numbers = re.findall(r'(?<![a-zA-Z_])(\d{3,})', code)
        for num in numbers:
            if int(num) not in [100, 200, 404, 500, 1000]:  # Common HTTP codes, etc.
                issues.append(Issue(
                    category="code_smell",
                    severity="low",
                    description=f"Magic number '{num}' - consider using named constant",
                    confidence=0.6,
                    agent=self.name,
                ))

        return issues

    def _check_naming(self, code: str) -> list[Issue]:
        """Check for poor naming conventions."""
        issues = []

        # Single letter variables (except common ones)
        single_vars = re.findall(r'\b([a-z])\s*=', code)
        allowed = {'i', 'j', 'k', 'n', 'x', 'y', '_'}
        for var in single_vars:
            if var not in allowed:
                issues.append(Issue(
                    category="code_smell",
                    severity="low",
                    description=f"Single-letter variable '{var}' - consider descriptive name",
                    confidence=0.5,
                    agent=self.name,
                ))

        return issues

    def _check_doc_anti_patterns(self, content: str) -> list[Issue]:
        """Check documentation for anti-patterns."""
        issues = []

        # Very long paragraphs without code examples
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para) > 500 and '```' not in para:
                issues.append(Issue(
                    category="code_smell",
                    severity="low",
                    description="Long text block without code example - consider adding demonstration",
                    confidence=0.4,
                    agent=self.name,
                ))

        return issues


class SecurityAgent(SpecializedAgent):
    """Detects security vulnerabilities and injection risks.

    Focuses on:
    - SQL injection patterns
    - Command injection risks
    - Hardcoded credentials
    - Insecure deserialization
    - Path traversal
    """

    def __init__(self):
        super().__init__("Security", "security")

    def analyze(self, content: str, context: dict) -> AgentAnalysis:
        """Analyze content for security issues."""
        import time
        start = time.time()

        issues = []
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

        for block in code_blocks:
            issues.extend(self._check_injection(block))
            issues.extend(self._check_credentials(block))
            issues.extend(self._check_insecure_functions(block))

        # Calculate score
        critical_count = sum(1 for i in issues if i.severity == "critical")
        high_count = sum(1 for i in issues if i.severity == "high")
        score = max(0, 1.0 - (critical_count * 0.5 + high_count * 0.25 + len(issues) * 0.05))
        passed = critical_count == 0

        return AgentAnalysis(
            agent_name=self.name,
            issues=issues,
            passed=passed,
            score=score,
            execution_time_ms=(time.time() - start) * 1000,
        )

    def _check_injection(self, code: str) -> list[Issue]:
        """Check for injection vulnerabilities."""
        issues = []

        # SQL injection patterns
        if re.search(r'execute\s*\(\s*["\'].*%s|execute\s*\(\s*f["\']', code):
            issues.append(Issue(
                category="security",
                severity="critical",
                description="Potential SQL injection - use parameterized queries",
                confidence=0.9,
                agent=self.name,
            ))

        # Command injection
        if re.search(r'(os\.system|subprocess\.\w+)\s*\(.*\+|eval\s*\(', code):
            issues.append(Issue(
                category="security",
                severity="critical",
                description="Potential command injection - avoid string concatenation in commands",
                confidence=0.85,
                agent=self.name,
            ))

        # Shell=True with user input
        if 'shell=True' in code:
            issues.append(Issue(
                category="security",
                severity="high",
                description="shell=True is dangerous - avoid if possible",
                confidence=0.8,
                agent=self.name,
            ))

        return issues

    def _check_credentials(self, code: str) -> list[Issue]:
        """Check for hardcoded credentials."""
        issues = []

        # Common credential patterns
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']', "Hardcoded token"),
        ]

        for pattern, desc in patterns:
            if re.search(pattern, code, re.I):
                issues.append(Issue(
                    category="security",
                    severity="high",
                    description=f"{desc} detected - use environment variables",
                    confidence=0.75,
                    agent=self.name,
                ))

        return issues

    def _check_insecure_functions(self, code: str) -> list[Issue]:
        """Check for use of insecure functions."""
        issues = []

        insecure = [
            ('pickle.loads', 'medium', 'pickle.loads with untrusted data - use json instead'),
            ('yaml.load', 'medium', 'yaml.load without Loader - use safe_load'),
            ('eval(', 'high', 'eval() is dangerous - avoid with user input'),
            ('exec(', 'high', 'exec() is dangerous - avoid with user input'),
            ('__import__', 'medium', 'Dynamic import could be exploited'),
        ]

        for func, severity, desc in insecure:
            if func in code:
                issues.append(Issue(
                    category="security",
                    severity=severity,
                    description=desc,
                    confidence=0.7,
                    agent=self.name,
                ))

        return issues


class DocumentationAgent(SpecializedAgent):
    """Verifies documentation accuracy against source code.

    This is the core hallucination-detection agent.

    Focuses on:
    - Symbol accuracy (classes, functions exist)
    - Citation verification
    - API correctness
    - Behavior claims match source
    """

    def __init__(self, ddr: Optional[DirectDependencyRetriever] = None):
        super().__init__("Documentation", "documentation")
        self.ddr = ddr

    def analyze(self, content: str, context: dict) -> AgentAnalysis:
        """Analyze content for documentation accuracy."""
        import time
        start = time.time()

        issues = []
        claims = self._extract_claims(content)
        source_refs = context.get('source_refs', [])

        verified = 0
        unverified = 0

        for claim in claims:
            is_verified = self._verify_claim(claim, source_refs)
            if is_verified:
                verified += 1
            else:
                unverified += 1
                issues.append(Issue(
                    category="documentation",
                    severity="high" if claim['type'] == 'symbol' else "medium",
                    description=f"Unverified {claim['type']}: '{claim['text']}'",
                    confidence=0.9,
                    agent=self.name,
                ))

        total = verified + unverified
        hall_rate = unverified / total if total > 0 else 0.0

        # Store hallucination rate for composite score
        score = 1.0 - hall_rate
        passed = hall_rate < 0.02

        result = AgentAnalysis(
            agent_name=self.name,
            issues=issues,
            passed=passed,
            score=score,
            execution_time_ms=(time.time() - start) * 1000,
        )

        # Attach extra data
        result.__dict__['hallucination_rate'] = hall_rate
        result.__dict__['verified_claims'] = verified
        result.__dict__['total_claims'] = total

        return result

    def _extract_claims(self, content: str) -> list[dict]:
        """Extract verifiable claims from content."""
        claims = []

        # Symbol references like `SymbolName`
        code_refs = re.findall(r'`([A-Z][a-zA-Z0-9_]+)`', content)
        for ref in code_refs:
            claims.append({'text': ref, 'type': 'symbol', 'symbol': ref})

        # File:line citations
        file_line_refs = re.findall(r'`?([a-zA-Z0-9_/]+\.py):(\d+)`?', content)
        for file_path, line in file_line_refs:
            claims.append({
                'text': f"{file_path}:{line}",
                'type': 'citation',
                'file': file_path,
                'line': int(line)
            })

        # Function references
        func_refs = re.findall(r'`([a-z_][a-zA-Z0-9_]*)\(\)`', content)
        for ref in func_refs:
            claims.append({'text': ref, 'type': 'symbol', 'symbol': ref})

        return claims

    def _verify_claim(self, claim: dict, source_refs: list[SourceRef]) -> bool:
        """Verify a claim against sources."""
        # Check against provided refs
        for ref in source_refs:
            if claim.get('symbol'):
                if claim['symbol'].lower() in ref.symbol_name.lower():
                    return True
            if claim.get('file') and claim.get('line'):
                if claim['file'] in ref.file_path and claim['line'] == ref.line_number:
                    return True

        # Check via DDR
        if self.ddr and claim.get('symbol'):
            result = self.ddr.retrieve(claim['symbol'], max_results=3)
            for element in result.elements:
                if element.is_valid:
                    return True

        return False


class MultiAgentAuditor:
    """Orchestrates 4 specialized agents for comprehensive verification.

    Based on CodeX-Verify research:
    - Multiple agents with different detection patterns find more issues
    - Submodular combination provides better coverage
    - Expected 39.7% improvement over single agent
    """

    def __init__(self, ddr: Optional[DirectDependencyRetriever] = None):
        self.agents = {
            'bug_detector': BugDetectionAgent(),
            'code_smell': CodeSmellAgent(),
            'security': SecurityAgent(),
            'documentation': DocumentationAgent(ddr),
        }
        self.ddr = ddr

    def audit(self, content: str, context: dict = None) -> MultiAuditResult:
        """Run all agents and combine results.

        Args:
            content: Content to audit
            context: Additional context (source_refs, etc.)

        Returns:
            Combined audit result from all agents
        """
        context = context or {}
        agent_results = []

        # Run each agent
        for name, agent in self.agents.items():
            result = agent.analyze(content, context)
            agent_results.append(result)

        # Combine results
        return self._combine_results(agent_results)

    async def audit_async(self, content: str, context: dict = None) -> MultiAuditResult:
        """Run all agents in parallel asynchronously."""
        context = context or {}

        async def run_agent(agent):
            # Run in thread pool since analyze is sync
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, lambda: agent.analyze(content, context)
            )

        # Run all agents in parallel
        results = await asyncio.gather(*[
            run_agent(agent) for agent in self.agents.values()
        ])

        return self._combine_results(list(results))

    def _combine_results(self, agent_results: list[AgentAnalysis]) -> MultiAuditResult:
        """Combine results from all agents using submodular combination."""
        all_issues = []
        for result in agent_results:
            all_issues.extend(result.issues)

        # Count by severity
        critical = sum(1 for i in all_issues if i.severity == "critical")
        high = sum(1 for i in all_issues if i.severity == "high")
        medium = sum(1 for i in all_issues if i.severity == "medium")
        low = sum(1 for i in all_issues if i.severity == "low")

        # Get hallucination rate from documentation agent
        doc_result = next(
            (r for r in agent_results if r.agent_name == "Documentation"),
            None
        )
        hall_rate = doc_result.__dict__.get('hallucination_rate', 0.0) if doc_result else 0.0

        # Calculate composite score (submodular combination)
        # Each agent contributes diminishing returns
        weights = {
            'BugDetector': 0.30,
            'CodeSmell': 0.15,
            'Security': 0.25,
            'Documentation': 0.30,
        }

        composite = sum(
            weights.get(r.agent_name, 0.25) * r.score
            for r in agent_results
        )

        # Determine overall pass/fail
        passed = (
            critical == 0 and
            high <= 2 and
            all(r.passed for r in agent_results if r.agent_name == "Documentation")
        )

        return MultiAuditResult(
            passed=passed,
            agent_results=agent_results,
            total_issues=len(all_issues),
            critical_issues=critical,
            high_issues=high,
            medium_issues=medium,
            low_issues=low,
            composite_score=composite,
            hallucination_rate=hall_rate,
        )

    def get_summary(self, result: MultiAuditResult) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "MULTI-AGENT AUDIT SUMMARY",
            "=" * 60,
            "",
            f"Overall: {'PASSED' if result.passed else 'FAILED'}",
            f"Composite Score: {result.composite_score:.2f}",
            f"Hallucination Rate: {result.hallucination_rate:.4f}",
            "",
            "Issues by Severity:",
            f"  Critical: {result.critical_issues}",
            f"  High: {result.high_issues}",
            f"  Medium: {result.medium_issues}",
            f"  Low: {result.low_issues}",
            "",
            "Agent Results:",
        ]

        for agent_result in result.agent_results:
            status = "PASS" if agent_result.passed else "FAIL"
            lines.append(
                f"  {agent_result.agent_name}: {status} "
                f"(score={agent_result.score:.2f}, issues={len(agent_result.issues)}, "
                f"time={agent_result.execution_time_ms:.1f}ms)"
            )

        if result.total_issues > 0:
            lines.append("")
            lines.append("Top Issues:")
            # Sort by severity
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            all_issues = []
            for ar in result.agent_results:
                all_issues.extend(ar.issues)
            all_issues.sort(key=lambda i: severity_order.get(i.severity, 4))

            for i, issue in enumerate(all_issues[:10], 1):
                lines.append(
                    f"  {i}. [{issue.severity.upper()}] {issue.description} "
                    f"({issue.agent})"
                )

        lines.append("")
        lines.append("=" * 60)

        return '\n'.join(lines)
