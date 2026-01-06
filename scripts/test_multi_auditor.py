#!/usr/bin/env python3
"""Test Multi-Agent Auditor (4-agent verification system)."""

import sys
import importlib.util

# Load multi_auditor module directly (it handles missing imports with stubs)
spec = importlib.util.spec_from_file_location(
    "multi_auditor",
    "/home/user/skills_fabric/src/skills_fabric/agents/multi_auditor.py"
)
multi_auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(multi_auditor)

# Get classes
MultiAgentAuditor = multi_auditor.MultiAgentAuditor
BugDetectionAgent = multi_auditor.BugDetectionAgent
CodeSmellAgent = multi_auditor.CodeSmellAgent
SecurityAgent = multi_auditor.SecurityAgent
DocumentationAgent = multi_auditor.DocumentationAgent


# Test content samples
CLEAN_CONTENT = '''
# Using DocumentConverter

The `DocumentConverter` class provides document conversion functionality.

```python
from docling import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
print(result.text)
```

See `docling/document_converter.py:50` for the implementation.
'''

BUGGY_CONTENT = '''
# Example with issues

```python
def process_data():
    result = undefined_var + 10  # Bug: undefined variable
    with open("file.txt") as f:  # Good: context manager
        data = f.read()
    return data
```
'''

SMELLY_CONTENT = '''
# Deep nesting example

```python
def complex_function(data):
    if data:
        for item in data:
            if item.valid:
                for sub in item.children:
                    if sub.active:
                        for child in sub.parts:
                            if child.ready:
                                process(child)
```

This example has 12345 magic numbers.
'''

INSECURE_CONTENT = '''
# Security issues

```python
password = "super_secret_123"  # Hardcoded password
api_key = "sk-1234567890abcdef"  # Hardcoded API key

import os
os.system(f"rm -rf {user_input}")  # Command injection

cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL injection
```
'''

HALLUCINATING_CONTENT = '''
# Made up symbols

The `NonExistentClass` provides amazing functionality.
Use the `fake_function()` method to do things.

See `imaginary_file.py:999` for details.
'''


def test_bug_detection_agent():
    """Test BugDetectionAgent."""
    print("=" * 60)
    print("TEST 1: Bug Detection Agent")
    print("=" * 60)

    agent = BugDetectionAgent()

    # Test on buggy content
    result = agent.analyze(BUGGY_CONTENT, {})

    print(f"✓ Bug Detection Agent ran")
    print(f"  Issues found: {len(result.issues)}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")

    for issue in result.issues:
        print(f"  - [{issue.severity}] {issue.description}")

    # Test on clean content
    clean_result = agent.analyze(CLEAN_CONTENT, {})
    print(f"\n✓ Clean content: {len(clean_result.issues)} issues, score={clean_result.score:.2f}")

    return True


def test_code_smell_agent():
    """Test CodeSmellAgent."""
    print("\n" + "=" * 60)
    print("TEST 2: Code Smell Agent")
    print("=" * 60)

    agent = CodeSmellAgent()

    result = agent.analyze(SMELLY_CONTENT, {})

    print(f"✓ Code Smell Agent ran")
    print(f"  Issues found: {len(result.issues)}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")

    for issue in result.issues:
        print(f"  - [{issue.severity}] {issue.description}")

    return True


def test_security_agent():
    """Test SecurityAgent."""
    print("\n" + "=" * 60)
    print("TEST 3: Security Agent")
    print("=" * 60)

    agent = SecurityAgent()

    result = agent.analyze(INSECURE_CONTENT, {})

    print(f"✓ Security Agent ran")
    print(f"  Issues found: {len(result.issues)}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")

    for issue in result.issues:
        print(f"  - [{issue.severity}] {issue.description}")

    # Should find critical issues
    critical = sum(1 for i in result.issues if i.severity == "critical")
    assert critical > 0, "Should find critical security issues"

    return True


def test_documentation_agent():
    """Test DocumentationAgent."""
    print("\n" + "=" * 60)
    print("TEST 4: Documentation Agent")
    print("=" * 60)

    agent = DocumentationAgent()

    # Test on hallucinating content (no source refs)
    result = agent.analyze(HALLUCINATING_CONTENT, {'source_refs': []})

    print(f"✓ Documentation Agent ran")
    print(f"  Issues found: {len(result.issues)}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")
    print(f"  Hallucination rate: {result.__dict__.get('hallucination_rate', 'N/A')}")

    for issue in result.issues:
        print(f"  - [{issue.severity}] {issue.description}")

    # Should fail due to unverified claims
    assert not result.passed, "Should fail with hallucinating content"

    return True


def test_multi_agent_auditor():
    """Test full MultiAgentAuditor."""
    print("\n" + "=" * 60)
    print("TEST 5: Multi-Agent Auditor (Combined)")
    print("=" * 60)

    auditor = MultiAgentAuditor()

    # Test on clean content
    result = auditor.audit(CLEAN_CONTENT, {'source_refs': []})

    print(f"✓ Multi-Agent Auditor ran")
    print(f"  Overall passed: {result.passed}")
    print(f"  Composite score: {result.composite_score:.2f}")
    print(f"  Total issues: {result.total_issues}")
    print(f"  Critical: {result.critical_issues}")
    print(f"  High: {result.high_issues}")
    print(f"  Medium: {result.medium_issues}")
    print(f"  Low: {result.low_issues}")

    print(f"\n  Agent results:")
    for ar in result.agent_results:
        print(f"    - {ar.agent_name}: score={ar.score:.2f}, issues={len(ar.issues)}")

    return True


def test_multi_agent_on_insecure():
    """Test MultiAgentAuditor on insecure content."""
    print("\n" + "=" * 60)
    print("TEST 6: Multi-Agent on Insecure Content")
    print("=" * 60)

    auditor = MultiAgentAuditor()
    result = auditor.audit(INSECURE_CONTENT, {'source_refs': []})

    print(f"✓ Multi-Agent Auditor on insecure content")
    print(f"  Overall passed: {result.passed}")
    print(f"  Critical issues: {result.critical_issues}")

    # Should fail due to security issues
    assert not result.passed, "Should fail on insecure content"
    assert result.critical_issues > 0, "Should find critical issues"

    return True


def test_summary_generation():
    """Test summary generation."""
    print("\n" + "=" * 60)
    print("TEST 7: Summary Generation")
    print("=" * 60)

    auditor = MultiAgentAuditor()
    result = auditor.audit(SMELLY_CONTENT, {'source_refs': []})

    summary = auditor.get_summary(result)
    print(summary)

    assert "MULTI-AGENT AUDIT SUMMARY" in summary
    assert "Agent Results:" in summary

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MULTI-AGENT AUDITOR TEST SUITE")
    print("=" * 60)

    tests = [
        test_bug_detection_agent,
        test_code_smell_agent,
        test_security_agent,
        test_documentation_agent,
        test_multi_agent_auditor,
        test_multi_agent_on_insecure,
        test_summary_generation,
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
