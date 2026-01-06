#!/usr/bin/env python3
"""Test Execution Proof System."""

import sys
import importlib.util

# Load execution_proof module
spec = importlib.util.spec_from_file_location(
    "execution_proof",
    "/home/user/skills_fabric/src/skills_fabric/verify/execution_proof.py"
)
execution_proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(execution_proof)

CodeBlockExtractor = execution_proof.CodeBlockExtractor
ExecutionProver = execution_proof.ExecutionProver
ExecutionResult = execution_proof.ExecutionResult
SANDBOX_AVAILABLE = execution_proof.SANDBOX_AVAILABLE
get_verification_summary = execution_proof.get_verification_summary


SAMPLE_SKILL = '''
# Document Conversion Skill

## Basic Usage

Convert a PDF document:

```python
result = 1 + 2 + 3
print(f"Sum: {result}")
```

## List Processing

```python
numbers = [1, 2, 3, 4, 5]
doubled = [x * 2 for x in numbers]
print(doubled)
```

## Dictionary Example

```python
data = {"name": "test", "value": 42}
print(data["name"])
```

## JavaScript Example

```javascript
const x = 10 + 20;
console.log("Result:", x);
```

## Non-executable

```yaml
name: config
value: 100
```
'''

FAILING_SKILL = '''
# Skill with Errors

```python
# This will fail
undefined_variable + 10
```

```python
# This would succeed
print("Hello")
```
'''


def test_code_block_extraction():
    """Test extracting code blocks from markdown."""
    print("=" * 60)
    print("TEST 1: Code Block Extraction")
    print("=" * 60)

    blocks = CodeBlockExtractor.extract(SAMPLE_SKILL)

    print(f"✓ Extracted {len(blocks)} code blocks")

    for lang, code in blocks:
        preview = code[:40].replace('\n', ' ')
        print(f"  - {lang}: {preview}...")

    assert len(blocks) >= 4, "Should extract at least 4 code blocks"

    # Check languages detected
    languages = set(lang for lang, _ in blocks)
    assert 'python' in languages, "Should detect Python"
    assert 'yaml' not in languages or 'javascript' in languages

    return True


def test_language_detection():
    """Test language alias normalization."""
    print("\n" + "=" * 60)
    print("TEST 2: Language Detection")
    print("=" * 60)

    test_content = '''
```py
x = 1
```

```python3
y = 2
```

```js
let z = 3;
```

```ts
const a: number = 4;
```
'''

    blocks = CodeBlockExtractor.extract(test_content)

    print(f"✓ Extracted {len(blocks)} blocks")

    for lang, _ in blocks:
        print(f"  - Normalized: {lang}")

    # Check normalization
    languages = [lang for lang, _ in blocks]
    assert 'python' in languages, "py should normalize to python"
    assert 'javascript' in languages, "js should normalize to javascript"

    return True


def test_executable_check():
    """Test checking if language is executable."""
    print("\n" + "=" * 60)
    print("TEST 3: Executable Check")
    print("=" * 60)

    executable = ['python', 'javascript', 'go', 'r', 'ruby']
    non_executable = ['yaml', 'text', 'markdown', 'json']

    print("✓ Checking executable languages:")
    for lang in executable:
        is_exec = CodeBlockExtractor.is_executable(lang)
        status = "✓" if is_exec else "✗"
        print(f"  {status} {lang}: {is_exec}")
        assert is_exec, f"{lang} should be executable"

    print("\n  Non-executable:")
    for lang in non_executable:
        is_exec = CodeBlockExtractor.is_executable(lang)
        status = "✓" if not is_exec else "✗"
        print(f"  {status} {lang}: {is_exec}")

    return True


def test_execution_result():
    """Test ExecutionResult dataclass."""
    print("\n" + "=" * 60)
    print("TEST 4: ExecutionResult")
    print("=" * 60)

    result = ExecutionResult(
        success=True,
        output="Hello World",
        error=None,
        exit_code=0,
        execution_time_ms=50.5,
        language="python",
        code_hash="abc123",
    )

    print("✓ Created ExecutionResult")
    print(f"  Success: {result.success}")
    print(f"  Output: {result.output}")
    print(f"  Time: {result.execution_time_ms}ms")

    # Test to_dict
    d = result.to_dict()
    assert d['success'] == True
    assert d['output'] == "Hello World"
    print(f"  to_dict: {len(d)} fields")

    return True


def test_prover_creation():
    """Test creating ExecutionProver."""
    print("\n" + "=" * 60)
    print("TEST 5: ExecutionProver Creation")
    print("=" * 60)

    prover = ExecutionProver(
        timeout_seconds=30,
        memory_limit_mb=256,
        use_pool=True,
    )

    print("✓ Created ExecutionProver")
    print(f"  Timeout: {prover.timeout}s")
    print(f"  Memory limit: {prover.memory_limit}MB")
    print(f"  Use pool: {prover.use_pool}")
    print(f"  Sandbox available: {SANDBOX_AVAILABLE}")

    return True


def test_placeholder_detection():
    """Test detecting placeholder code."""
    print("\n" + "=" * 60)
    print("TEST 6: Placeholder Detection")
    print("=" * 60)

    prover = ExecutionProver()

    placeholders = [
        "# TODO: implement this",
        "pass  # implement later",
        "...",
        "YOUR_API_KEY = 'xxx'",
        "<your_token_here>",
    ]

    real_code = [
        "x = 1 + 2\nprint(x)",
        "def foo(): return 42",
        "import os\nos.getcwd()",
    ]

    print("✓ Checking placeholder detection:")

    for code in placeholders:
        is_placeholder = prover._is_example_placeholder(code)
        status = "✓" if is_placeholder else "✗"
        preview = code[:30].replace('\n', ' ')
        print(f"  {status} Placeholder: '{preview}...'")
        assert is_placeholder, f"Should detect placeholder: {code[:30]}"

    for code in real_code:
        is_placeholder = prover._is_example_placeholder(code)
        status = "✓" if not is_placeholder else "✗"
        preview = code[:30].replace('\n', ' ')
        print(f"  {status} Real code: '{preview}...'")
        assert not is_placeholder, f"Should not be placeholder: {code[:30]}"

    return True


def test_skill_verification_without_sandbox():
    """Test skill verification structure (no sandbox)."""
    print("\n" + "=" * 60)
    print("TEST 7: Skill Verification Structure")
    print("=" * 60)

    prover = ExecutionProver()
    report = prover.verify_skill("test_skill", SAMPLE_SKILL)

    print(f"✓ Generated verification report")
    print(f"  Skill ID: {report.skill_id}")
    print(f"  Total blocks: {report.total_code_blocks}")
    print(f"  Executed: {report.executed_blocks}")
    print(f"  Successful: {report.successful_blocks}")
    print(f"  Failed: {report.failed_blocks}")
    print(f"  Skipped: {report.skipped_blocks}")
    print(f"  Score: {report.verification_score:.2%}")

    assert report.skill_id == "test_skill"
    assert report.total_code_blocks > 0

    return True


def test_summary_generation():
    """Test summary generation."""
    print("\n" + "=" * 60)
    print("TEST 8: Summary Generation")
    print("=" * 60)

    prover = ExecutionProver()
    report = prover.verify_skill("summary_test", SAMPLE_SKILL)

    summary = get_verification_summary(report)

    print("✓ Generated summary:")
    lines = summary.split('\n')
    for line in lines[:15]:
        print(f"  {line}")
    print("  ...")

    assert "EXECUTION PROOF REPORT" in summary
    assert "summary_test" in summary

    return True


def test_actual_execution():
    """Test actual code execution (if sandbox available)."""
    print("\n" + "=" * 60)
    print("TEST 9: Actual Execution")
    print("=" * 60)

    if not SANDBOX_AVAILABLE:
        print("⚠ Sandbox not available, skipping")
        return True

    prover = ExecutionProver(timeout_seconds=10)

    # Simple Python code
    result = prover.execute_code("print('Hello from sandbox!')", "python")

    print(f"✓ Executed code in sandbox")
    print(f"  Success: {result.success}")
    print(f"  Output: {result.output}")
    print(f"  Error: {result.error}")
    print(f"  Time: {result.execution_time_ms:.1f}ms")

    if result.success:
        assert "Hello from sandbox" in result.output

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("EXECUTION PROOF TEST SUITE")
    print("=" * 60)
    print(f"Sandbox available: {SANDBOX_AVAILABLE}")

    tests = [
        test_code_block_extraction,
        test_language_detection,
        test_executable_check,
        test_execution_result,
        test_prover_creation,
        test_placeholder_detection,
        test_skill_verification_without_sandbox,
        test_summary_generation,
        test_actual_execution,
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
