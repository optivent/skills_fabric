#!/usr/bin/env python3
"""Test Hallucination Metrics module."""

import sys
import importlib.util

# Load module directly
spec = importlib.util.spec_from_file_location(
    "metrics",
    "/home/user/skills_fabric/src/skills_fabric/verify/metrics.py"
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

HallucinationMetrics = metrics_module.HallucinationMetrics
HallucinationAnalyzer = metrics_module.HallucinationAnalyzer


# Test content
CONTENT_WITH_HALLUCINATIONS = '''
# Example with issues

The `NonExistentClass` provides functionality.
Use `fake_function()` to do things.

```python
import fake_package
from nonexistent import Something

def example():
    result = Something.process()
    return result
```
'''

CLEAN_CONTENT = '''
# Using Standard Libraries

The `Path` class from pathlib handles paths.
Use `json.loads()` to parse JSON.

```python
import json
from pathlib import Path

def read_config():
    path = Path("config.json")
    data = json.loads(path.read_text())
    return data
```
'''


def test_metrics_dataclass():
    """Test HallucinationMetrics dataclass."""
    print("=" * 60)
    print("TEST 1: Metrics Dataclass")
    print("=" * 60)

    metrics = HallucinationMetrics(
        hall_m=0.1,
        api_accuracy=0.9,
        package_validity=0.8,
        type_correctness=0.95,
        semantic_fidelity=0.85,
        total_claims=10,
        verified_claims=9,
        unverified_claims=1,
    )

    print(f"✓ Created HallucinationMetrics")
    print(f"  Hall_m: {metrics.hall_m}")
    print(f"  Composite Score: {metrics.composite_score:.2f}")
    print(f"  Meets Target: {metrics.meets_target}")

    # Test to_dict
    d = metrics.to_dict()
    assert 'hall_m' in d
    assert 'composite_score' in d

    print(f"✓ to_dict() works")

    return True


def test_analyzer_clean_content():
    """Test analyzer on clean content."""
    print("\n" + "=" * 60)
    print("TEST 2: Analyze Clean Content")
    print("=" * 60)

    analyzer = HallucinationAnalyzer()
    metrics = analyzer.analyze(CLEAN_CONTENT)

    print(f"✓ Analyzed clean content")
    print(f"  Hall_m: {metrics.hall_m:.4f}")
    print(f"  Package Validity: {metrics.package_validity:.2%}")
    print(f"  Total Claims: {metrics.total_claims}")

    # Clean content should have high validity
    assert metrics.package_validity >= 0.5, "Clean content should have valid packages"

    return True


def test_analyzer_hallucinating_content():
    """Test analyzer on hallucinating content."""
    print("\n" + "=" * 60)
    print("TEST 3: Analyze Hallucinating Content")
    print("=" * 60)

    analyzer = HallucinationAnalyzer()
    metrics = analyzer.analyze(CONTENT_WITH_HALLUCINATIONS)

    print(f"✓ Analyzed hallucinating content")
    print(f"  Hall_m: {metrics.hall_m:.4f}")
    print(f"  Package Validity: {metrics.package_validity:.2%}")
    print(f"  Package Hallucinations: {metrics.package_hallucinations}")
    print(f"  Total Claims: {metrics.total_claims}")

    # Should detect invalid packages
    assert metrics.package_hallucinations > 0, "Should detect fake packages"

    return True


def test_summary_generation():
    """Test summary generation."""
    print("\n" + "=" * 60)
    print("TEST 4: Summary Generation")
    print("=" * 60)

    analyzer = HallucinationAnalyzer()
    metrics = analyzer.analyze(CONTENT_WITH_HALLUCINATIONS)
    summary = analyzer.get_summary(metrics)

    print(summary)

    assert "HALLUCINATION METRICS SUMMARY" in summary
    assert "Hall_m Rate" in summary
    assert "Composite Score" in summary

    return True


def test_composite_score_calculation():
    """Test composite score weights."""
    print("\n" + "=" * 60)
    print("TEST 5: Composite Score Calculation")
    print("=" * 60)

    # Perfect metrics
    perfect = HallucinationMetrics(
        hall_m=0.0,
        api_accuracy=1.0,
        package_validity=1.0,
        type_correctness=1.0,
        semantic_fidelity=1.0,
    )

    # Terrible metrics
    terrible = HallucinationMetrics(
        hall_m=1.0,
        api_accuracy=0.0,
        package_validity=0.0,
        type_correctness=0.0,
        semantic_fidelity=0.0,
    )

    print(f"✓ Perfect metrics composite: {perfect.composite_score:.2f}")
    print(f"✓ Terrible metrics composite: {terrible.composite_score:.2f}")

    assert perfect.composite_score == 1.0, "Perfect should be 1.0"
    assert terrible.composite_score == 0.0, "Terrible should be 0.0"

    # Mixed metrics
    mixed = HallucinationMetrics(
        hall_m=0.05,  # Slightly above target
        api_accuracy=0.8,
        package_validity=0.9,
        type_correctness=0.85,
        semantic_fidelity=0.7,
    )

    print(f"✓ Mixed metrics composite: {mixed.composite_score:.2f}")
    assert 0.5 < mixed.composite_score < 1.0, "Mixed should be moderate"

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("HALLUCINATION METRICS TEST SUITE")
    print("=" * 60)

    tests = [
        test_metrics_dataclass,
        test_analyzer_clean_content,
        test_analyzer_hallucinating_content,
        test_summary_generation,
        test_composite_score_calculation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
