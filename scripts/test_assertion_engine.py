#!/usr/bin/env python3
"""Test the Assertion-Based Understanding Engine.

This script validates that our engine:
1. Extracts meaningful claims from code
2. Verifies claims against source
3. Builds understanding from verified assertions
"""
import sys
import importlib.util
from pathlib import Path

# Direct import to bypass package system (avoids kuzu dependency)
script_dir = Path(__file__).parent.parent / "src" / "skills_fabric" / "understanding"

spec = importlib.util.spec_from_file_location(
    "assertions",
    script_dir / "assertions.py"
)
assertions_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assertions_module)

UnderstandingEngine = assertions_module.UnderstandingEngine
ClaimExtractor = assertions_module.ClaimExtractor
AssertionVerifier = assertions_module.AssertionVerifier
Assertion = assertions_module.Assertion
VerificationType = assertions_module.VerificationType
VerificationResult = assertions_module.VerificationResult


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_claim_extraction():
    """Test that we can extract claims from source code."""
    print_section("TEST 1: CLAIM EXTRACTION")

    # Sample source code to analyze
    sample_source = '''
class StateGraph(Generic[StateT]):
    """A graph for managing state transitions.

    StateGraph provides a way to define nodes and edges
    that transform state in a controlled manner.

    Args:
        state_schema: The TypedDict defining state structure
        config_schema: Optional configuration schema

    Returns:
        A new StateGraph instance

    Raises:
        TypeError: If state_schema is not a TypedDict
    """

    def __init__(self, state_schema: type, config_schema: type = None):
        self.schema = state_schema

    def add_node(self, name: str, action: Callable) -> "StateGraph":
        """Add a node to the graph."""
        pass

    async def astream(self, input: dict) -> AsyncIterator:
        """Async stream results."""
        pass
'''

    extractor = ClaimExtractor(sample_source, "test_file.py")
    assertions = extractor.extract_from_class("StateGraph", 2)

    print(f"Extracted {len(assertions)} claims:\n")
    for i, assertion in enumerate(assertions, 1):
        print(f"  {i}. [{assertion.category}] {assertion.claim}")
        print(f"     Verification: {assertion.verification_type.name}")
        print()

    # Validate we got the right claims
    categories = {a.category for a in assertions}
    expected_categories = {"existence", "relationship", "signature", "behavior"}

    found = categories & expected_categories
    print(f"Found categories: {found}")
    print(f"Expected: {expected_categories}")

    if found:
        print("\n✓ Claim extraction working")
        return True
    else:
        print("\n✗ Missing expected categories")
        return False


def test_verification():
    """Test that we can verify claims."""
    print_section("TEST 2: CLAIM VERIFICATION")

    repo_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo"

    if not repo_path.exists():
        print(f"Repository not found at {repo_path}")
        return False

    verifier = AssertionVerifier(repo_path)

    # Test 1: Existence claim (should pass)
    existence_claim = Assertion(
        claim="StateGraph is a class defined at line 112",
        category="existence",
        source_concept="StateGraph",
        source_file="libs/langgraph/langgraph/graph/state.py",
        source_line=112,
        verification_type=VerificationType.EXISTENCE
    )

    result = verifier.verify(existence_claim)
    print(f"Test 1 - Existence claim:")
    print(f"  Claim: {result.claim}")
    print(f"  Result: {result.result.name}")
    print(f"  Evidence: {result.evidence[0] if result.evidence else 'none'}")
    print()

    # Test 2: Method exists (should pass with AST)
    method_claim = Assertion(
        claim="StateGraph.__init__ is a method",
        category="existence",
        source_concept="StateGraph.__init__",
        source_file="libs/langgraph/langgraph/graph/state.py",
        source_line=197,
        verification_type=VerificationType.EXISTENCE
    )

    result2 = verifier.verify(method_claim)
    print(f"Test 2 - Method existence claim:")
    print(f"  Claim: {result2.claim}")
    print(f"  Result: {result2.result.name}")
    print(f"  Evidence: {result2.evidence[0] if result2.evidence else 'none'}")
    print()

    # Test 3: Non-existent file (should fail)
    missing_claim = Assertion(
        claim="StateGraph exists in fake_file.py",
        category="existence",
        source_concept="StateGraph",
        source_file="fake_file.py",
        source_line=1,
        verification_type=VerificationType.EXISTENCE
    )

    result3 = verifier.verify(missing_claim)
    print(f"Test 3 - Non-existent file:")
    print(f"  Result: {result3.result.name}")
    print()

    # Check results
    passed = (
        result.result == VerificationResult.VERIFIED and
        result2.result == VerificationResult.VERIFIED and  # Method should be found
        result3.result == VerificationResult.REFUTED
    )

    if passed:
        print("✓ Verification working correctly")
    else:
        print("✗ Verification has issues")

    return passed


def test_full_understanding():
    """Test the complete understanding engine."""
    print_section("TEST 3: FULL UNDERSTANDING ENGINE")

    repo_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo"

    if not repo_path.exists():
        print(f"Repository not found at {repo_path}")
        return False

    engine = UnderstandingEngine(repo_path)

    # Understand StateGraph
    state = engine.understand(
        file_path="libs/langgraph/langgraph/graph/state.py",
        concept="StateGraph",
        line=112
    )

    print(f"Concept: {state.concept}")
    print(f"Source: {state.source_file}:{state.source_line}")
    print(f"\nAssertions: {state.verified_count()}/{state.total_count()} verified")
    print(f"Understanding Ratio: {state.understanding_ratio():.1%}")

    print("\n--- Assertions ---")
    for assertion in state.assertions[:10]:  # Show first 10
        status = "✓" if assertion.is_verified() else "✗"
        print(f"  {status} [{assertion.category}] {assertion.claim[:60]}...")
        if assertion.evidence:
            print(f"     Evidence: {assertion.evidence[0].content[:50]}...")

    print("\n--- Program Model (Structure) ---")
    if state.program_model.get("structure"):
        struct = state.program_model["structure"]
        print(f"  Type: {struct.get('type')}")
        print(f"  Lines: {struct.get('line')}-{struct.get('end_line')}")
        print(f"  Bases: {struct.get('bases')}")
        print(f"  Methods: {len(struct.get('methods', []))}")
        if struct.get('methods'):
            for m in struct['methods'][:5]:
                async_marker = "async " if m['is_async'] else ""
                print(f"    - {async_marker}{m['name']}()")

    print("\n--- Domain Model (Meaning) ---")
    if state.domain_model:
        print(f"  Confidence: {state.domain_model.get('confidence', 0):.1%}")
        print(f"  Verified behaviors: {len(state.domain_model.get('verified_behaviors', []))}")
        print(f"  Verified relationships: {len(state.domain_model.get('verified_relationships', []))}")
        print(f"  Verified constraints: {len(state.domain_model.get('verified_constraints', []))}")

    # Check results
    passed = (
        state.total_count() > 0 and
        state.verified_count() > 0 and
        state.program_model.get("structure")
    )

    if passed:
        print("\n✓ Full understanding engine working")
    else:
        print("\n✗ Understanding engine has issues")

    return passed


def test_comparison_with_old_approach():
    """Compare assertion-based understanding with the old coverage-based approach."""
    print_section("TEST 4: OLD vs NEW APPROACH COMPARISON")

    repo_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo"

    if not repo_path.exists():
        print(f"Repository not found at {repo_path}")
        return False

    engine = UnderstandingEngine(repo_path)

    # Understand StateGraph with new approach
    state = engine.understand(
        file_path="libs/langgraph/langgraph/graph/state.py",
        concept="StateGraph",
        line=112
    )

    print("OLD APPROACH (Coverage-Based):")
    print("  'We found 16 methods' → Score: 45%")
    print("  'We found 89 dependencies' → Score: 65%")
    print("  'Docstring exists' → Score: 70%")
    print("  Problem: These numbers don't prove understanding")
    print()

    print("NEW APPROACH (Assertion-Based):")
    print(f"  Total claims made: {state.total_count()}")
    print(f"  Claims verified: {state.verified_count()}")
    print(f"  Claims refuted: {sum(1 for a in state.assertions if a.result == VerificationResult.REFUTED)}")
    print(f"  Claims inconclusive: {sum(1 for a in state.assertions if a.result == VerificationResult.INCONCLUSIVE)}")
    print()

    print("What we ACTUALLY know (verified):")
    for assertion in state.assertions:
        if assertion.is_verified():
            print(f"  ✓ {assertion.claim[:70]}...")
    print()

    print("What we DON'T know (unverified):")
    for assertion in state.unverified_assertions()[:5]:
        print(f"  ? {assertion.claim[:70]}...")

    print("\n" + "="*70)
    print("KEY INSIGHT:")
    print("  Old: 'We explored the code' (exploration != understanding)")
    print("  New: 'We verified these specific claims' (verified claims = understanding)")
    print("="*70)

    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  ASSERTION ENGINE TESTS")
    print("="*70)

    results = []

    results.append(("Claim Extraction", test_claim_extraction()))
    results.append(("Verification", test_verification()))
    results.append(("Full Understanding", test_full_understanding()))
    results.append(("Comparison", test_comparison_with_old_approach()))

    print_section("SUMMARY")
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed - Assertion Engine is working!")
    else:
        print("\n✗ Some tests failed")


if __name__ == "__main__":
    main()
