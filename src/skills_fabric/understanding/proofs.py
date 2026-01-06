"""Proof-Based Code Understanding.

Inspired by Lean4/Coq: Every claim about code must be PROVEN, not asserted.

The key insight (from Martin Kleppmann):
"Writing proof scripts is one of the best applications for LLMs.
It doesn't matter if they hallucinate nonsense, because the
proof checker will reject any invalid proof."

This module provides:
1. Theorem - A claim about code that can be proven or refuted
2. Proof - Evidence that proves a theorem
3. ProofChecker - Verifies proofs mechanically
4. TheoremProver - Attempts to prove theorems

Unlike assertions (which may be unverified), EVERY theorem
here has a definitive status: PROVEN, REFUTED, or UNPROVABLE.
"""
import ast
import sys
import importlib
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, List, Dict, Set, Tuple
from enum import Enum, auto
from pathlib import Path
from datetime import datetime


class ProofStatus(Enum):
    """Status of a theorem."""
    PROVEN = auto()      # Mechanically verified to be true
    REFUTED = auto()     # Mechanically verified to be false
    UNPROVABLE = auto()  # Cannot be decided with current methods


class ProofMethod(Enum):
    """Method used to prove a theorem."""
    AST_ANALYSIS = auto()      # Structural analysis of source
    TYPE_CHECK = auto()        # Type system verification
    EXECUTION = auto()         # Dynamic execution
    EXCEPTION_CHECK = auto()   # Exception behavior verification
    INVARIANT_CHECK = auto()   # Pre/post condition verification
    REFERENCE_CHECK = auto()   # Cross-reference verification


@dataclass
class Proof:
    """A machine-verifiable proof of a theorem.

    A proof consists of:
    - method: How the proof was constructed
    - evidence: The concrete evidence (code, output, etc.)
    - witness: Specific value/state that demonstrates truth
    """
    method: ProofMethod
    evidence: str
    witness: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"Proof({self.method.name}): {self.evidence[:100]}"


@dataclass
class Theorem:
    """A provable claim about code.

    Unlike assertions which may be "believed", theorems are
    definitively proven or refuted by mechanical checking.
    """
    # The claim
    statement: str
    category: str  # "existence", "type", "behavior", "invariant"

    # What the theorem is about
    subject: str        # e.g., "Calculator.add"
    source_file: str

    # Proof status
    status: ProofStatus = ProofStatus.UNPROVABLE
    proofs: List[Proof] = field(default_factory=list)

    # For refuted theorems
    counterexample: str = ""

    def is_proven(self) -> bool:
        return self.status == ProofStatus.PROVEN

    def is_refuted(self) -> bool:
        return self.status == ProofStatus.REFUTED

    def add_proof(self, proof: Proof) -> None:
        self.proofs.append(proof)
        self.status = ProofStatus.PROVEN

    def refute(self, counterexample: str) -> None:
        self.counterexample = counterexample
        self.status = ProofStatus.REFUTED


class ASTProofChecker:
    """Prove theorems using AST analysis.

    This is the most reliable checker - it examines source
    structure directly without execution.
    """

    def __init__(self, source_code: str, file_path: str = ""):
        self.source = source_code
        self.file_path = file_path
        try:
            self.tree = ast.parse(source_code)
        except SyntaxError:
            self.tree = None

    def prove_class_exists(self, class_name: str) -> Optional[Proof]:
        """Prove that a class exists in the source."""
        if not self.tree:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return Proof(
                    method=ProofMethod.AST_ANALYSIS,
                    evidence=f"ClassDef node found at line {node.lineno}",
                    witness=node.lineno
                )
        return None

    def prove_method_exists(self, class_name: str, method_name: str) -> Optional[Proof]:
        """Prove that a method exists in a class."""
        if not self.tree:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name == method_name:
                            return Proof(
                                method=ProofMethod.AST_ANALYSIS,
                                evidence=f"FunctionDef '{method_name}' in class '{class_name}' at line {item.lineno}",
                                witness=item.lineno
                            )
        return None

    def prove_method_count(self, class_name: str, expected_count: int) -> Optional[Proof]:
        """Prove a class has exactly N methods."""
        if not self.tree:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                methods = [
                    item for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                actual_count = len(methods)
                if actual_count == expected_count:
                    method_names = [m.name for m in methods]
                    return Proof(
                        method=ProofMethod.AST_ANALYSIS,
                        evidence=f"Class has exactly {expected_count} methods: {method_names}",
                        witness=method_names
                    )
        return None

    def prove_has_type_annotation(self, class_name: str, method_name: str) -> Optional[Proof]:
        """Prove a method has return type annotation."""
        if not self.tree:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == method_name:
                        if item.returns is not None:
                            return Proof(
                                method=ProofMethod.TYPE_CHECK,
                                evidence=f"Method has return annotation: {ast.unparse(item.returns)}",
                                witness=ast.unparse(item.returns)
                            )
        return None

    def prove_inherits_from(self, class_name: str, base_name: str) -> Optional[Proof]:
        """Prove a class inherits from another."""
        if not self.tree:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == base_name:
                        return Proof(
                            method=ProofMethod.AST_ANALYSIS,
                            evidence=f"Class {class_name} has base class {base_name}",
                            witness=base_name
                        )
        return None

    def count_classes(self) -> Tuple[int, List[str]]:
        """Count all classes in source."""
        if not self.tree:
            return 0, []

        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return len(classes), classes


class ExecutionProofChecker:
    """Prove theorems by actual execution.

    This is the most powerful checker - it runs code and
    observes actual behavior.
    """

    def __init__(self, module_path: str):
        """Load module for execution-based proofs."""
        self.module_path = module_path
        self.module = None
        self._load_module()

    def _load_module(self):
        """Dynamically load the module."""
        try:
            # Add parent directory to path if needed
            path = Path(self.module_path)
            if path.parent.parent not in [Path(p) for p in sys.path]:
                sys.path.insert(0, str(path.parent.parent))

            # Import the module
            module_name = path.stem
            spec = importlib.util.spec_from_file_location(module_name, self.module_path)
            if spec and spec.loader:
                self.module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.module)
        except Exception as e:
            self.module = None

    def prove_instantiation(self, class_name: str, *args, **kwargs) -> Optional[Proof]:
        """Prove a class can be instantiated."""
        if not self.module:
            return None

        try:
            cls = getattr(self.module, class_name, None)
            if cls is None:
                return None

            instance = cls(*args, **kwargs)
            return Proof(
                method=ProofMethod.EXECUTION,
                evidence=f"Successfully instantiated {class_name}({args}, {kwargs})",
                witness=type(instance).__name__
            )
        except Exception:
            return None

    def prove_method_callable(self, class_name: str, method_name: str,
                              init_args: tuple = (),
                              method_args: tuple = ()) -> Optional[Proof]:
        """Prove a method can be called."""
        if not self.module:
            return None

        try:
            cls = getattr(self.module, class_name, None)
            if cls is None:
                return None

            instance = cls(*init_args)
            method = getattr(instance, method_name, None)
            if method is None:
                return None

            result = method(*method_args)
            return Proof(
                method=ProofMethod.EXECUTION,
                evidence=f"{class_name}().{method_name}{method_args} returned {result}",
                witness=result
            )
        except Exception:
            return None

    def prove_raises_exception(self, class_name: str, method_name: str,
                               exception_type: type,
                               init_args: tuple = (),
                               method_args: tuple = ()) -> Optional[Proof]:
        """Prove a method raises specific exception."""
        if not self.module:
            return None

        try:
            cls = getattr(self.module, class_name, None)
            if cls is None:
                return None

            instance = cls(*init_args)
            method = getattr(instance, method_name, None)
            if method is None:
                return None

            try:
                method(*method_args)
                return None  # Should have raised
            except exception_type as e:
                return Proof(
                    method=ProofMethod.EXCEPTION_CHECK,
                    evidence=f"{class_name}().{method_name}{method_args} raised {exception_type.__name__}: {e}",
                    witness=str(e)
                )
            except Exception:
                return None  # Wrong exception type
        except Exception:
            return None

    def prove_invariant(self, class_name: str,
                        setup: Callable[[Any], None],
                        check: Callable[[Any], bool],
                        description: str,
                        init_args: tuple = ()) -> Optional[Proof]:
        """Prove an invariant holds after operations."""
        if not self.module:
            return None

        try:
            cls = getattr(self.module, class_name, None)
            if cls is None:
                return None

            instance = cls(*init_args)
            setup(instance)

            if check(instance):
                return Proof(
                    method=ProofMethod.INVARIANT_CHECK,
                    evidence=f"Invariant holds: {description}",
                    witness=True
                )
            return None
        except Exception:
            return None


class TheoremProver:
    """Attempts to prove theorems about code.

    Combines multiple proof checkers to attempt proofs.
    """

    def __init__(self, source_code: str, file_path: str):
        self.source = source_code
        self.file_path = file_path
        self.ast_checker = ASTProofChecker(source_code, file_path)
        self.exec_checker = ExecutionProofChecker(file_path) if Path(file_path).exists() else None

    def prove(self, theorem: Theorem) -> Theorem:
        """Attempt to prove a theorem."""
        category = theorem.category.lower()

        if category == "existence":
            return self._prove_existence(theorem)
        elif category == "type":
            return self._prove_type(theorem)
        elif category == "behavior":
            return self._prove_behavior(theorem)
        elif category == "invariant":
            return self._prove_invariant(theorem)

        return theorem

    def _prove_existence(self, theorem: Theorem) -> Theorem:
        """Prove existence claims."""
        subject = theorem.subject

        if "." in subject:
            class_name, method_name = subject.rsplit(".", 1)
            proof = self.ast_checker.prove_method_exists(class_name, method_name)
        else:
            proof = self.ast_checker.prove_class_exists(subject)

        if proof:
            theorem.add_proof(proof)
        else:
            theorem.refute(f"Not found in AST: {subject}")

        return theorem

    def _prove_type(self, theorem: Theorem) -> Theorem:
        """Prove type claims."""
        subject = theorem.subject

        if "." in subject:
            class_name, method_name = subject.rsplit(".", 1)
            proof = self.ast_checker.prove_has_type_annotation(class_name, method_name)
            if proof:
                theorem.add_proof(proof)
            else:
                theorem.refute(f"No type annotation found: {subject}")

        return theorem

    def _prove_behavior(self, theorem: Theorem) -> Theorem:
        """Prove behavioral claims through execution."""
        if not self.exec_checker:
            return theorem

        # Parse the statement to understand what to prove
        statement = theorem.statement.lower()
        subject = theorem.subject

        if "raises" in statement and "." in subject:
            class_name, method_name = subject.rsplit(".", 1)

            # Check for ValueError on divide by zero
            if "valueerror" in statement and "zero" in statement:
                proof = self.exec_checker.prove_raises_exception(
                    class_name, method_name, ValueError,
                    method_args=(0,)
                )
                if proof:
                    theorem.add_proof(proof)
                else:
                    theorem.refute("Exception not raised")

        return theorem

    def _prove_invariant(self, theorem: Theorem) -> Theorem:
        """Prove invariant claims."""
        if not self.exec_checker:
            return theorem

        # For now, mark as unprovable without specific invariant handlers
        return theorem


@dataclass
class ProofBasedUnderstanding:
    """Complete understanding of a codebase through proven theorems.

    This represents VERIFIED knowledge, not opinions.
    """
    source_file: str
    theorems: List[Theorem] = field(default_factory=list)

    def proven_count(self) -> int:
        return sum(1 for t in self.theorems if t.is_proven())

    def refuted_count(self) -> int:
        return sum(1 for t in self.theorems if t.is_refuted())

    def unprovable_count(self) -> int:
        return sum(1 for t in self.theorems if t.status == ProofStatus.UNPROVABLE)

    def total_count(self) -> int:
        return len(self.theorems)

    def certainty(self) -> float:
        """Fraction of theorems with definitive status."""
        if not self.theorems:
            return 0.0
        decided = self.proven_count() + self.refuted_count()
        return decided / len(self.theorems)

    def truth_ratio(self) -> float:
        """Fraction of proven theorems among decided ones."""
        decided = self.proven_count() + self.refuted_count()
        if decided == 0:
            return 0.0
        return self.proven_count() / decided

    def summary(self) -> str:
        lines = [
            f"Proof-Based Understanding: {self.source_file}",
            f"=" * 60,
            f"Total theorems: {self.total_count()}",
            f"  PROVEN:     {self.proven_count()}",
            f"  REFUTED:    {self.refuted_count()}",
            f"  UNPROVABLE: {self.unprovable_count()}",
            f"",
            f"Certainty: {self.certainty():.1%} (theorems with definitive status)",
            f"Truth Ratio: {self.truth_ratio():.1%} (proven among decided)",
            f"",
            f"Proven Theorems:"
        ]

        for t in self.theorems:
            if t.is_proven():
                lines.append(f"  ✓ {t.statement}")
                if t.proofs:
                    lines.append(f"      Proof: {t.proofs[0].method.name}")

        refuted = [t for t in self.theorems if t.is_refuted()]
        if refuted:
            lines.append(f"")
            lines.append(f"Refuted Theorems:")
            for t in refuted:
                lines.append(f"  ✗ {t.statement}")
                lines.append(f"      Counterexample: {t.counterexample}")

        return "\n".join(lines)


def prove_understanding(source_code: str, file_path: str) -> ProofBasedUnderstanding:
    """Generate and prove theorems about code.

    This is the main entry point for proof-based understanding.
    Returns only verified knowledge, not opinions.
    """
    prover = TheoremProver(source_code, file_path)
    ast_checker = prover.ast_checker

    theorems = []

    # Auto-generate theorems from AST
    count, class_names = ast_checker.count_classes()

    for class_name in class_names:
        # Theorem: Class exists
        t = Theorem(
            statement=f"Class {class_name} exists",
            category="existence",
            subject=class_name,
            source_file=file_path
        )
        theorems.append(prover.prove(t))

        # Find methods and generate theorems for each
        if ast_checker.tree:
            for node in ast.walk(ast_checker.tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_name = item.name

                            # Theorem: Method exists
                            t = Theorem(
                                statement=f"Method {class_name}.{method_name} exists",
                                category="existence",
                                subject=f"{class_name}.{method_name}",
                                source_file=file_path
                            )
                            theorems.append(prover.prove(t))

                            # Theorem: Method has type annotation
                            if item.returns:
                                t = Theorem(
                                    statement=f"Method {class_name}.{method_name} has return type annotation",
                                    category="type",
                                    subject=f"{class_name}.{method_name}",
                                    source_file=file_path
                                )
                                theorems.append(prover.prove(t))

    return ProofBasedUnderstanding(
        source_file=file_path,
        theorems=theorems
    )
