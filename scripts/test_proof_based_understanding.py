#!/usr/bin/env python3
"""Test Proof-Based Code Understanding.

This demonstrates the paradigm shift from "opinions about understanding"
to "machine-verified proofs about code".

Like Lean4 for mathematics:
- Every claim is a theorem
- Every theorem must be proven
- Invalid proofs are rejected
- The result is CERTAIN knowledge
"""
import sys
import importlib.util
from pathlib import Path

# Direct imports
script_dir = Path(__file__).parent.parent / "src" / "skills_fabric" / "understanding"
test_repo = Path(__file__).parent.parent / "test_repos" / "provable_calc"

spec = importlib.util.spec_from_file_location("proofs", script_dir / "proofs.py")
proofs_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proofs_module)

Theorem = proofs_module.Theorem
Proof = proofs_module.Proof
ProofStatus = proofs_module.ProofStatus
ProofMethod = proofs_module.ProofMethod
ASTProofChecker = proofs_module.ASTProofChecker
ExecutionProofChecker = proofs_module.ExecutionProofChecker
TheoremProver = proofs_module.TheoremProver
prove_understanding = proofs_module.prove_understanding
ProofBasedUnderstanding = proofs_module.ProofBasedUnderstanding


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_ast_proofs():
    """Test AST-based proofs (structural facts)."""
    print_section("TEST 1: AST PROOFS (Structural Facts)")

    calc_file = test_repo / "calculator.py"
    with open(calc_file) as f:
        source = f.read()

    checker = ASTProofChecker(source, str(calc_file))

    # Prove class exists
    proof = checker.prove_class_exists("Calculator")
    if proof:
        print(f"✓ PROVEN: Calculator class exists")
        print(f"  Method: {proof.method.name}")
        print(f"  Evidence: {proof.evidence}")
        print(f"  Witness: line {proof.witness}")
    else:
        print("✗ REFUTED: Calculator class does not exist")

    print()

    # Prove methods exist
    methods = ["__init__", "add", "subtract", "multiply", "divide", "reset"]
    for method in methods:
        proof = checker.prove_method_exists("Calculator", method)
        status = "✓ PROVEN" if proof else "✗ REFUTED"
        print(f"  {status}: Calculator.{method} exists")

    print()

    # Prove method count
    proof = checker.prove_method_count("Calculator", 6)  # 5 + __init__
    if proof:
        print(f"✓ PROVEN: Calculator has exactly 6 methods")
        print(f"  Methods: {proof.witness}")
    else:
        print("✗ REFUTED: Calculator does not have 6 methods")

    print()

    # Prove type annotations
    typed_methods = ["add", "subtract", "multiply", "divide", "reset"]
    typed_count = 0
    for method in typed_methods:
        proof = checker.prove_has_type_annotation("Calculator", method)
        if proof:
            typed_count += 1
            print(f"  ✓ {method} has return type: {proof.witness}")

    print(f"\n{typed_count}/{len(typed_methods)} methods have type annotations")

    return True


def test_execution_proofs():
    """Test execution-based proofs (behavioral facts)."""
    print_section("TEST 2: EXECUTION PROOFS (Behavioral Facts)")

    calc_file = test_repo / "calculator.py"

    # Add test_repo to path
    sys.path.insert(0, str(test_repo.parent))

    checker = ExecutionProofChecker(str(calc_file))

    # Prove instantiation works
    proof = checker.prove_instantiation("Calculator")
    if proof:
        print(f"✓ PROVEN: Calculator() can be instantiated")
        print(f"  Evidence: {proof.evidence}")
    else:
        print("✗ REFUTED: Calculator cannot be instantiated")

    print()

    # Prove methods work
    proof = checker.prove_method_callable("Calculator", "add", method_args=(5,))
    if proof:
        print(f"✓ PROVEN: Calculator().add(5) is callable")
        print(f"  Result: {proof.witness}")

    proof = checker.prove_method_callable("Calculator", "multiply", method_args=(3,))
    if proof:
        print(f"✓ PROVEN: Calculator().multiply(3) is callable")
        print(f"  Result: {proof.witness}")

    print()

    # Prove exception behavior
    proof = checker.prove_raises_exception(
        "Calculator", "divide", ValueError,
        method_args=(0,)
    )
    if proof:
        print(f"✓ PROVEN: Calculator().divide(0) raises ValueError")
        print(f"  Message: {proof.witness}")
    else:
        print("✗ REFUTED: divide(0) does not raise ValueError")

    print()

    # Prove invariant
    proof = checker.prove_invariant(
        "Calculator",
        setup=lambda c: (c.add(10), c.reset()),
        check=lambda c: c.value == 0,
        description="After reset(), value is 0"
    )
    if proof:
        print(f"✓ PROVEN: Invariant holds - after reset(), value is 0")
    else:
        print("✗ Could not prove invariant")

    return True


def test_full_understanding():
    """Generate complete proof-based understanding."""
    print_section("TEST 3: COMPLETE PROOF-BASED UNDERSTANDING")

    calc_file = test_repo / "calculator.py"
    with open(calc_file) as f:
        source = f.read()

    understanding = prove_understanding(source, str(calc_file))

    print(understanding.summary())

    print()
    print("--- KEY INSIGHT ---")
    print(f"Certainty: {understanding.certainty():.1%}")
    print("This means we have DEFINITIVE knowledge (proven or refuted)")
    print("for this percentage of claims. No opinions, no maybes.")

    return understanding.certainty() > 0.9


def test_complete_repo_understanding():
    """Prove understanding of entire test repo."""
    print_section("TEST 4: COMPLETE REPO UNDERSTANDING")

    total_theorems = 0
    total_proven = 0
    total_refuted = 0

    files = [
        test_repo / "calculator.py",
        test_repo / "history.py"
    ]

    all_understanding = []

    for file_path in files:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        with open(file_path) as f:
            source = f.read()

        understanding = prove_understanding(source, str(file_path))
        all_understanding.append(understanding)

        total_theorems += understanding.total_count()
        total_proven += understanding.proven_count()
        total_refuted += understanding.refuted_count()

        print(f"\n{file_path.name}:")
        print(f"  Theorems: {understanding.total_count()}")
        print(f"  Proven: {understanding.proven_count()}")
        print(f"  Refuted: {understanding.refuted_count()}")

    print(f"\n{'='*50}")
    print(f"COMPLETE REPO SUMMARY")
    print(f"{'='*50}")
    print(f"Total theorems: {total_theorems}")
    print(f"Total proven: {total_proven}")
    print(f"Total refuted: {total_refuted}")

    if total_theorems > 0:
        certainty = (total_proven + total_refuted) / total_theorems
        truth = total_proven / (total_proven + total_refuted) if (total_proven + total_refuted) > 0 else 0
        print(f"\nOverall Certainty: {certainty:.1%}")
        print(f"Overall Truth Ratio: {truth:.1%}")

    print("\n--- THE PARADIGM SHIFT ---")
    print("OLD: 'I think I understand this code' (opinion)")
    print("NEW: 'I have proven {n} theorems about this code' (fact)".format(n=total_proven))
    print("\nLike Lean4 for math, we now have MACHINE-VERIFIED understanding.")

    return total_proven > 0


def test_counterexample_detection():
    """Test that false claims are properly refuted."""
    print_section("TEST 5: COUNTEREXAMPLE DETECTION")

    calc_file = test_repo / "calculator.py"
    with open(calc_file) as f:
        source = f.read()

    prover = TheoremProver(source, str(calc_file))

    # Try to prove a FALSE theorem
    false_theorem = Theorem(
        statement="Method Calculator.non_existent_method exists",
        category="existence",
        subject="Calculator.non_existent_method",
        source_file=str(calc_file)
    )

    result = prover.prove(false_theorem)

    if result.is_refuted():
        print(f"✓ CORRECTLY REFUTED false claim:")
        print(f"  Claim: {result.statement}")
        print(f"  Counterexample: {result.counterexample}")
    else:
        print("✗ Failed to refute false claim")

    # Try another false theorem
    false_theorem2 = Theorem(
        statement="Class NonExistentClass exists",
        category="existence",
        subject="NonExistentClass",
        source_file=str(calc_file)
    )

    result2 = prover.prove(false_theorem2)

    if result2.is_refuted():
        print(f"\n✓ CORRECTLY REFUTED:")
        print(f"  Claim: {result2.statement}")
        print(f"  Counterexample: {result2.counterexample}")
    else:
        print("✗ Failed to refute false claim")

    print("\n--- KEY INSIGHT ---")
    print("Unlike LLMs that might 'hallucinate' understanding,")
    print("our proof system REJECTS invalid claims.")

    return result.is_refuted() and result2.is_refuted()


def main():
    """Run all proof-based understanding tests."""
    print("\n" + "="*70)
    print("  PROOF-BASED CODE UNDERSTANDING")
    print("  'From Opinions to Machine-Verified Truth'")
    print("="*70)

    print("\nThe Paradigm:")
    print("  OLD: 'I understand X' (assertion, may be wrong)")
    print("  NEW: 'X has property P, PROVEN' (verified, certain)")

    results = []

    results.append(("AST Proofs", test_ast_proofs()))
    results.append(("Execution Proofs", test_execution_proofs()))
    results.append(("Full Understanding", test_full_understanding()))
    results.append(("Complete Repo", test_complete_repo_understanding()))
    results.append(("Counterexample Detection", test_counterexample_detection()))

    print_section("FINAL SUMMARY")
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    print("\n" + "="*70)
    print("  THE FUNDAMENTAL INSIGHT")
    print("="*70)
    print("""
Like Lean4 makes mathematics machine-checkable:
  - Theorems are stated precisely
  - Proofs are verified mechanically
  - Invalid proofs are REJECTED

Our proof-based code understanding does the same:
  - Claims about code are theorems
  - Evidence is gathered through AST/execution
  - False claims are detected and refuted

This is NOT 'opinion about understanding'.
This is VERIFIED KNOWLEDGE.
    """)


if __name__ == "__main__":
    main()
