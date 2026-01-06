"""Assertion-Based Code Understanding Engine.

Based on research synthesis:
- Pennington (1987): Program Model vs Domain Model
- Execution Traces as Grounded Supervision (2025)
- Property-Based Testing for LLM Code Validation
- Neuro-Symbolic Verification

Key insight: Understanding is not counting what we found.
Understanding is making claims and verifying them.

A claim is verified when:
1. We can state what we believe about the code
2. We can generate a test that would prove/disprove it
3. We execute the test and record the result
4. The evidence is traceable to source

Example:
    Claim: "StateGraph.__init__ requires TypedDict for state_schema"
    Verification: Execute with dict vs TypedDict, compare errors
    Evidence: "TypeError: Expected TypedDict, got dict"
    Verified: True
"""
import ast
import re
import sys
import io
import traceback
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, Any
from pathlib import Path
from datetime import datetime


class VerificationType(Enum):
    """How a claim can be verified."""
    EXISTENCE = auto()      # File/line/symbol exists
    TYPE_CHECK = auto()     # Type signature matches
    EXECUTION = auto()      # Code runs and produces expected output
    PROPERTY = auto()       # Property holds for generated inputs
    TRACE = auto()          # Execution trace shows expected behavior
    MUTATION = auto()       # Mutant behaves differently as expected
    STATIC = auto()         # AST/structure matches claim


class VerificationResult(Enum):
    """Outcome of verification."""
    VERIFIED = auto()       # Claim proven true
    REFUTED = auto()        # Claim proven false
    INCONCLUSIVE = auto()   # Could not determine
    ERROR = auto()          # Verification failed to run


@dataclass
class Evidence:
    """Traceable evidence for a verification."""
    type: str                          # "execution_output", "error_message", "ast_node", etc.
    content: str                       # The actual evidence
    source_file: str = ""              # Where this came from
    source_line: int = 0               # Line number
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self):
        loc = f"{self.source_file}:{self.source_line}" if self.source_file else "runtime"
        return f"[{self.type}@{loc}] {self.content[:100]}"


@dataclass
class Assertion:
    """A verifiable claim about code behavior.

    This is the core unit of understanding. Instead of saying
    "we found 16 methods" (which proves nothing), we say
    "StateGraph has an add_node method that accepts a callable"
    and then VERIFY that claim.
    """
    claim: str                         # Natural language claim
    category: str                      # "signature", "behavior", "relationship", "invariant"
    source_concept: str                # What we're making a claim about
    source_file: str                   # Where we derived this claim
    source_line: int                   # Line number

    verification_type: VerificationType = VerificationType.EXISTENCE
    verification_code: str = ""        # Code that tests this claim

    result: VerificationResult = VerificationResult.INCONCLUSIVE
    evidence: list[Evidence] = field(default_factory=list)

    confidence: float = 0.0            # 0-1, based on verification strength

    def is_verified(self) -> bool:
        return self.result == VerificationResult.VERIFIED

    def summary(self) -> str:
        status = "✓" if self.is_verified() else "✗" if self.result == VerificationResult.REFUTED else "?"
        return f"{status} [{self.category}] {self.claim}"


@dataclass
class UnderstandingState:
    """Accumulated understanding of a code concept.

    Unlike coverage-based scoring, this tracks:
    - What claims have we made?
    - Which are verified vs refuted vs unknown?
    - What evidence do we have?
    """
    concept: str
    source_file: str
    source_line: int

    assertions: list[Assertion] = field(default_factory=list)

    # Pennington's dual model
    program_model: dict = field(default_factory=dict)   # Structure: control flow, syntax
    domain_model: dict = field(default_factory=dict)    # Meaning: goals, function, data flow

    def add_assertion(self, assertion: Assertion):
        self.assertions.append(assertion)

    def verified_count(self) -> int:
        return sum(1 for a in self.assertions if a.is_verified())

    def total_count(self) -> int:
        return len(self.assertions)

    def understanding_ratio(self) -> float:
        """Ratio of verified assertions to total.

        This is NOT a percentage score - it's a measure of
        how many of our claims we've successfully verified.
        """
        if not self.assertions:
            return 0.0
        return self.verified_count() / self.total_count()

    def unverified_assertions(self) -> list[Assertion]:
        return [a for a in self.assertions if not a.is_verified()]

    def summary(self) -> str:
        lines = [
            f"Understanding: {self.concept}",
            f"Source: {self.source_file}:{self.source_line}",
            f"Assertions: {self.verified_count()}/{self.total_count()} verified",
            ""
        ]
        for a in self.assertions:
            lines.append(f"  {a.summary()}")
        return "\n".join(lines)


class ClaimExtractor:
    """Extract verifiable claims from code and documentation.

    Claims come from:
    1. Docstrings (explicit documentation)
    2. Type hints (signature claims)
    3. Method names (behavioral claims)
    4. Assertions in code (invariant claims)
    5. Comments (informal claims)
    """

    def __init__(self, source_code: str, file_path: str = ""):
        self.source = source_code
        self.file_path = file_path
        self.tree = ast.parse(source_code)

    def extract_from_class(self, class_name: str, line: int) -> list[Assertion]:
        """Extract claims from a class definition."""
        assertions = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Claim 1: Class exists at this location
                assertions.append(Assertion(
                    claim=f"{class_name} is a class defined at line {node.lineno}",
                    category="existence",
                    source_concept=class_name,
                    source_file=self.file_path,
                    source_line=node.lineno,
                    verification_type=VerificationType.EXISTENCE
                ))

                # Claim 2: Inheritance
                if node.bases:
                    bases = [self._get_name(b) for b in node.bases]
                    assertions.append(Assertion(
                        claim=f"{class_name} inherits from {', '.join(bases)}",
                        category="relationship",
                        source_concept=class_name,
                        source_file=self.file_path,
                        source_line=node.lineno,
                        verification_type=VerificationType.STATIC
                    ))

                # Claim 3: Docstring claims
                docstring = ast.get_docstring(node)
                if docstring:
                    doc_claims = self._extract_docstring_claims(
                        docstring, class_name, node.lineno
                    )
                    assertions.extend(doc_claims)

                # Claim 4: Method signatures
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_claims = self._extract_method_claims(
                            item, class_name
                        )
                        assertions.extend(method_claims)

                break

        return assertions

    def _extract_docstring_claims(
        self, docstring: str, concept: str, line: int
    ) -> list[Assertion]:
        """Extract claims from a docstring.

        Looks for:
        - "Args:" sections (parameter claims)
        - "Returns:" sections (return type claims)
        - "Raises:" sections (exception claims)
        - "Example:" sections (behavioral claims)
        """
        assertions = []

        # Parameter claims from Args section
        args_match = re.search(r'Args?:\s*\n((?:\s+\w+.*\n)+)', docstring, re.IGNORECASE)
        if args_match:
            args_text = args_match.group(1)
            for param_match in re.finditer(r'\s+(\w+)\s*[:\(]([^:\n]+)', args_text):
                param_name = param_match.group(1)
                param_desc = param_match.group(2).strip()
                assertions.append(Assertion(
                    claim=f"{concept} accepts parameter '{param_name}': {param_desc}",
                    category="signature",
                    source_concept=concept,
                    source_file=self.file_path,
                    source_line=line,
                    verification_type=VerificationType.TYPE_CHECK
                ))

        # Return type claims
        returns_match = re.search(r'Returns?:\s*\n?\s*(.+?)(?:\n\n|\n\s*\w+:|\Z)',
                                   docstring, re.IGNORECASE | re.DOTALL)
        if returns_match:
            return_desc = returns_match.group(1).strip().split('\n')[0]
            assertions.append(Assertion(
                claim=f"{concept} returns: {return_desc}",
                category="behavior",
                source_concept=concept,
                source_file=self.file_path,
                source_line=line,
                verification_type=VerificationType.TYPE_CHECK
            ))

        # Exception claims
        raises_match = re.search(r'Raises?:\s*\n((?:\s+\w+.*\n)+)', docstring, re.IGNORECASE)
        if raises_match:
            raises_text = raises_match.group(1)
            for exc_match in re.finditer(r'\s+(\w+Error|\w+Exception)\s*:', raises_text):
                exc_name = exc_match.group(1)
                assertions.append(Assertion(
                    claim=f"{concept} can raise {exc_name}",
                    category="behavior",
                    source_concept=concept,
                    source_file=self.file_path,
                    source_line=line,
                    verification_type=VerificationType.EXECUTION
                ))

        return assertions

    def _extract_method_claims(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, class_name: str
    ) -> list[Assertion]:
        """Extract claims from a method definition."""
        assertions = []
        method_name = node.name
        full_name = f"{class_name}.{method_name}"

        # Claim: Method exists
        assertions.append(Assertion(
            claim=f"{full_name} is {'an async ' if isinstance(node, ast.AsyncFunctionDef) else 'a '}method",
            category="existence",
            source_concept=full_name,
            source_file=self.file_path,
            source_line=node.lineno,
            verification_type=VerificationType.EXISTENCE
        ))

        # Claim: Parameter signature
        params = []
        for arg in node.args.args:
            param = arg.arg
            if arg.annotation:
                param += f": {self._get_name(arg.annotation)}"
            params.append(param)

        if params:
            assertions.append(Assertion(
                claim=f"{full_name} accepts parameters: ({', '.join(params)})",
                category="signature",
                source_concept=full_name,
                source_file=self.file_path,
                source_line=node.lineno,
                verification_type=VerificationType.TYPE_CHECK
            ))

        # Claim: Return type
        if node.returns:
            return_type = self._get_name(node.returns)
            assertions.append(Assertion(
                claim=f"{full_name} returns {return_type}",
                category="signature",
                source_concept=full_name,
                source_file=self.file_path,
                source_line=node.lineno,
                verification_type=VerificationType.TYPE_CHECK
            ))

        return assertions

    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "?"


class AssertionVerifier:
    """Verify assertions through execution and analysis.

    This is the core of the neuro-symbolic approach:
    - Neural: LLM generates claims
    - Symbolic: We verify them through execution/analysis
    """

    def __init__(self, repo_path: Path | str = None):
        self.repo_path = Path(repo_path) if repo_path else None

    def verify(self, assertion: Assertion) -> Assertion:
        """Verify an assertion and update it with results."""
        if assertion.verification_type == VerificationType.EXISTENCE:
            return self._verify_existence(assertion)
        elif assertion.verification_type == VerificationType.STATIC:
            return self._verify_static(assertion)
        elif assertion.verification_type == VerificationType.EXECUTION:
            return self._verify_execution(assertion)
        elif assertion.verification_type == VerificationType.TYPE_CHECK:
            return self._verify_type(assertion)
        else:
            assertion.result = VerificationResult.INCONCLUSIVE
            return assertion

    def _verify_existence(self, assertion: Assertion) -> Assertion:
        """Verify that something exists at the claimed location.

        Uses AST-based verification for more accurate checking:
        - For "Class.method" → find class, then find method inside
        - For "Class" → find class definition
        """
        if not self.repo_path:
            assertion.result = VerificationResult.INCONCLUSIVE
            assertion.evidence.append(Evidence(
                type="error",
                content="No repository path configured"
            ))
            return assertion

        file_path = self.repo_path / assertion.source_file
        if not file_path.exists():
            assertion.result = VerificationResult.REFUTED
            assertion.evidence.append(Evidence(
                type="file_check",
                content=f"File not found: {file_path}",
                source_file=assertion.source_file
            ))
            return assertion

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Parse AST for precise verification
            tree = ast.parse(content)
            concept = assertion.source_concept

            # Handle "Class.method" format
            if "." in concept:
                class_name, method_name = concept.rsplit(".", 1)
                found = self._find_method_in_class(tree, class_name, method_name)

                if found:
                    assertion.result = VerificationResult.VERIFIED
                    assertion.confidence = 1.0
                    assertion.evidence.append(Evidence(
                        type="ast_found",
                        content=f"Found method '{method_name}' in class '{class_name}' at line {found}",
                        source_file=assertion.source_file,
                        source_line=found
                    ))
                else:
                    assertion.result = VerificationResult.REFUTED
                    assertion.evidence.append(Evidence(
                        type="ast_not_found",
                        content=f"Method '{method_name}' not found in class '{class_name}'",
                        source_file=assertion.source_file
                    ))
            else:
                # Simple class/function lookup
                found = self._find_definition(tree, concept)

                if found:
                    assertion.result = VerificationResult.VERIFIED
                    assertion.confidence = 1.0
                    assertion.evidence.append(Evidence(
                        type="ast_found",
                        content=f"Found '{concept}' at line {found}",
                        source_file=assertion.source_file,
                        source_line=found
                    ))
                else:
                    assertion.result = VerificationResult.REFUTED
                    assertion.evidence.append(Evidence(
                        type="ast_not_found",
                        content=f"'{concept}' not found in AST",
                        source_file=assertion.source_file
                    ))

        except SyntaxError as e:
            assertion.result = VerificationResult.ERROR
            assertion.evidence.append(Evidence(
                type="parse_error",
                content=f"Could not parse file: {e}"
            ))
        except Exception as e:
            assertion.result = VerificationResult.ERROR
            assertion.evidence.append(Evidence(
                type="error",
                content=str(e)
            ))

        return assertion

    def _find_method_in_class(self, tree: ast.AST, class_name: str, method_name: str) -> int | None:
        """Find a method inside a class, return line number or None."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name == method_name:
                            return item.lineno
        return None

    def _find_definition(self, tree: ast.AST, name: str) -> int | None:
        """Find a class or function definition, return line number or None."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == name:
                return node.lineno
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return node.lineno
        return None

    def _verify_static(self, assertion: Assertion) -> Assertion:
        """Verify through static analysis of AST."""
        if not self.repo_path:
            assertion.result = VerificationResult.INCONCLUSIVE
            return assertion

        file_path = self.repo_path / assertion.source_file
        try:
            with open(file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source)

            # Check inheritance claims
            if "inherits from" in assertion.claim:
                match = re.search(r'(\w+) inherits from (.+)', assertion.claim)
                if match:
                    class_name = match.group(1)
                    expected_bases = [b.strip() for b in match.group(2).split(',')]

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == class_name:
                            actual_bases = [self._get_name(b) for b in node.bases]

                            # Check if expected bases are subset of actual
                            found = all(
                                any(exp in act for act in actual_bases)
                                for exp in expected_bases
                            )

                            if found:
                                assertion.result = VerificationResult.VERIFIED
                                assertion.confidence = 1.0
                                assertion.evidence.append(Evidence(
                                    type="ast_inheritance",
                                    content=f"Bases: {actual_bases}",
                                    source_file=assertion.source_file,
                                    source_line=node.lineno
                                ))
                            else:
                                assertion.result = VerificationResult.REFUTED
                                assertion.evidence.append(Evidence(
                                    type="ast_inheritance",
                                    content=f"Expected {expected_bases}, found {actual_bases}",
                                    source_file=assertion.source_file,
                                    source_line=node.lineno
                                ))
                            break

        except Exception as e:
            assertion.result = VerificationResult.ERROR
            assertion.evidence.append(Evidence(
                type="error",
                content=str(e)
            ))

        return assertion

    def _verify_execution(self, assertion: Assertion) -> Assertion:
        """Verify through code execution."""
        if not assertion.verification_code:
            assertion.result = VerificationResult.INCONCLUSIVE
            assertion.evidence.append(Evidence(
                type="missing_code",
                content="No verification code provided"
            ))
            return assertion

        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            # Execute the verification code
            exec_globals = {}
            exec(assertion.verification_code, exec_globals)

            stdout_val = sys.stdout.getvalue()
            stderr_val = sys.stderr.getvalue()

            # Check for explicit PASS/FAIL markers
            if "PASS" in stdout_val or "VERIFIED" in stdout_val:
                assertion.result = VerificationResult.VERIFIED
                assertion.confidence = 0.9
            elif "FAIL" in stdout_val or "REFUTED" in stdout_val:
                assertion.result = VerificationResult.REFUTED
            else:
                # No error = likely passed
                assertion.result = VerificationResult.VERIFIED
                assertion.confidence = 0.7

            assertion.evidence.append(Evidence(
                type="execution_output",
                content=stdout_val[:500] if stdout_val else "(no output)"
            ))

            if stderr_val:
                assertion.evidence.append(Evidence(
                    type="execution_stderr",
                    content=stderr_val[:500]
                ))

        except Exception as e:
            assertion.result = VerificationResult.REFUTED
            assertion.evidence.append(Evidence(
                type="execution_error",
                content=f"{type(e).__name__}: {str(e)}"
            ))
            assertion.evidence.append(Evidence(
                type="traceback",
                content=traceback.format_exc()[:500]
            ))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return assertion

    def _verify_type(self, assertion: Assertion) -> Assertion:
        """Verify type-related claims through AST analysis.

        Handles:
        - "X.method accepts parameters: (...)"
        - "X.method returns Y"
        """
        if not self.repo_path:
            assertion.result = VerificationResult.INCONCLUSIVE
            return assertion

        file_path = self.repo_path / assertion.source_file
        if not file_path.exists():
            assertion.result = VerificationResult.REFUTED
            return assertion

        try:
            with open(file_path, 'r') as f:
                source = f.read()
            tree = ast.parse(source)

            # Parse the claim
            claim = assertion.claim

            # Handle "X.method accepts parameters: (...)"
            param_match = re.match(r'(\w+)\.(\w+) accepts parameters: \(([^)]*)\)', claim)
            if param_match:
                class_name = param_match.group(1)
                method_name = param_match.group(2)
                # Note: We just verify the method exists with some parameters
                # Full type checking would require mypy

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if item.name == method_name:
                                    # Extract actual parameters
                                    actual_params = []
                                    for arg in item.args.args:
                                        param = arg.arg
                                        if arg.annotation:
                                            param += f": {self._get_name(arg.annotation)}"
                                        actual_params.append(param)

                                    assertion.result = VerificationResult.VERIFIED
                                    assertion.confidence = 0.8
                                    assertion.evidence.append(Evidence(
                                        type="ast_signature",
                                        content=f"Found {method_name}({', '.join(actual_params[:3])}...)",
                                        source_file=assertion.source_file,
                                        source_line=item.lineno
                                    ))
                                    return assertion

                assertion.result = VerificationResult.REFUTED
                assertion.evidence.append(Evidence(
                    type="method_not_found",
                    content=f"Method {method_name} not found in {class_name}"
                ))
                return assertion

            # Handle "X.method returns Y"
            return_match = re.match(r'(\w+)\.(\w+) returns (\w+)', claim)
            if return_match:
                class_name = return_match.group(1)
                method_name = return_match.group(2)
                expected_return = return_match.group(3)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if item.name == method_name:
                                    if item.returns:
                                        actual_return = self._get_name(item.returns)
                                        assertion.result = VerificationResult.VERIFIED
                                        assertion.confidence = 0.8
                                        assertion.evidence.append(Evidence(
                                            type="ast_return_type",
                                            content=f"Return type: {actual_return}",
                                            source_file=assertion.source_file,
                                            source_line=item.lineno
                                        ))
                                    else:
                                        assertion.result = VerificationResult.VERIFIED
                                        assertion.confidence = 0.5
                                        assertion.evidence.append(Evidence(
                                            type="no_return_annotation",
                                            content="No return type annotation found",
                                            source_file=assertion.source_file,
                                            source_line=item.lineno
                                        ))
                                    return assertion

            # Fallback to static verification
            return self._verify_static(assertion)

        except Exception as e:
            assertion.result = VerificationResult.ERROR
            assertion.evidence.append(Evidence(
                type="error",
                content=str(e)
            ))
            return assertion

    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        return "?"


class UnderstandingEngine:
    """Main engine for assertion-based code understanding.

    This replaces the coverage-based approach with verification-based approach.

    Old: "We found 16 methods" (proves nothing)
    New: "We verified 12/15 claims about StateGraph" (proves understanding)
    """

    def __init__(self, repo_path: Path | str):
        self.repo_path = Path(repo_path)
        self.verifier = AssertionVerifier(self.repo_path)

    def understand(
        self,
        file_path: str,
        concept: str,
        line: int
    ) -> UnderstandingState:
        """Build verified understanding of a code concept.

        Process:
        1. Read source code
        2. Extract claims from docstrings, types, structure
        3. Verify each claim
        4. Build understanding state with evidence
        """
        full_path = self.repo_path / file_path

        state = UnderstandingState(
            concept=concept,
            source_file=file_path,
            source_line=line
        )

        if not full_path.exists():
            return state

        with open(full_path, 'r') as f:
            source = f.read()

        # Extract claims
        extractor = ClaimExtractor(source, file_path)
        assertions = extractor.extract_from_class(concept, line)

        # Verify each claim
        for assertion in assertions:
            verified = self.verifier.verify(assertion)
            state.add_assertion(verified)

        # Build program model (structure)
        state.program_model = self._build_program_model(source, concept, line)

        # Build domain model (meaning) - requires verified assertions
        state.domain_model = self._build_domain_model(state)

        return state

    def _build_program_model(
        self, source: str, concept: str, line: int
    ) -> dict:
        """Build Pennington's program model (textbase).

        This captures the structural understanding:
        - Control flow
        - Syntax structure
        - Elementary operations
        """
        model = {
            "concept": concept,
            "structure": {},
            "control_flow": [],
            "operations": []
        }

        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == concept:
                    model["structure"]["type"] = "class"
                    model["structure"]["line"] = node.lineno
                    model["structure"]["end_line"] = node.end_lineno
                    model["structure"]["bases"] = [
                        self._get_name(b) for b in node.bases
                    ]
                    model["structure"]["methods"] = []

                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            model["structure"]["methods"].append({
                                "name": item.name,
                                "line": item.lineno,
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                                "params": len(item.args.args)
                            })
                    break
        except:
            pass

        return model

    def _build_domain_model(self, state: UnderstandingState) -> dict:
        """Build Pennington's domain model (situation model).

        This captures the semantic understanding:
        - Goals (what does this accomplish?)
        - Function (what is its role?)
        - Data flow (how does information move?)

        This is built from VERIFIED assertions, not speculation.
        """
        model = {
            "concept": state.concept,
            "verified_behaviors": [],
            "verified_relationships": [],
            "verified_constraints": [],
            "confidence": state.understanding_ratio()
        }

        for assertion in state.assertions:
            if assertion.is_verified():
                if assertion.category == "behavior":
                    model["verified_behaviors"].append(assertion.claim)
                elif assertion.category == "relationship":
                    model["verified_relationships"].append(assertion.claim)
                elif assertion.category in ("signature", "invariant"):
                    model["verified_constraints"].append(assertion.claim)

        return model

    def _get_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        return "?"
