"""Execution Proof System - Level 5 Verification.

Uses llm-sandbox for secure, sandboxed execution of code examples.
This provides the highest level of verification: actual execution proof.

Verification Levels:
1. Static Citation - file:line reference exists
2. Symbol Verification - symbol exists in codebase
3. Type Checking - code is type-correct
4. Import Verification - all imports resolve
5. Execution Proof - code actually runs (this module)

Based on research:
- llm-sandbox: Lightweight Docker-based code execution
- Supports Python, JavaScript, Go, R, and more
- Container pooling for 10x faster execution
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path
import re
import json
import hashlib

# Try to import llm-sandbox
try:
    from llm_sandbox import SandboxSession
    from llm_sandbox.docker import DockerSandbox
    SANDBOX_AVAILABLE = True
except ImportError:
    SANDBOX_AVAILABLE = False
    SandboxSession = None
    DockerSandbox = None


@dataclass
class ExecutionResult:
    """Result of code execution in sandbox."""
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    execution_time_ms: float = 0.0
    language: str = "python"
    code_hash: str = ""

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'exit_code': self.exit_code,
            'execution_time_ms': self.execution_time_ms,
            'language': self.language,
            'code_hash': self.code_hash,
        }


@dataclass
class ExecutionProof:
    """Proof that a code example executes correctly."""
    code_block: str
    language: str
    verified: bool
    result: Optional[ExecutionResult] = None
    verification_level: int = 5  # Level 5 = execution proof
    proof_hash: str = ""

    def __post_init__(self):
        if not self.proof_hash:
            content = f"{self.code_block}:{self.verified}:{self.language}"
            self.proof_hash = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class SkillExecutionReport:
    """Execution verification report for a skill."""
    skill_id: str
    total_code_blocks: int
    executed_blocks: int
    successful_blocks: int
    failed_blocks: int
    skipped_blocks: int
    execution_proofs: list[ExecutionProof] = field(default_factory=list)
    overall_success: bool = False
    verification_score: float = 0.0

    def __post_init__(self):
        if self.total_code_blocks > 0:
            self.verification_score = self.successful_blocks / self.total_code_blocks
            self.overall_success = self.failed_blocks == 0


class CodeBlockExtractor:
    """Extract code blocks from markdown content."""

    LANGUAGE_ALIASES = {
        'python': 'python',
        'py': 'python',
        'python3': 'python',
        'javascript': 'javascript',
        'js': 'javascript',
        'typescript': 'typescript',
        'ts': 'typescript',
        'r': 'r',
        'go': 'go',
        'golang': 'go',
        'rust': 'rust',
        'rs': 'rust',
        'ruby': 'ruby',
        'rb': 'ruby',
        'java': 'java',
        'cpp': 'cpp',
        'c++': 'cpp',
    }

    @classmethod
    def extract(cls, content: str) -> list[tuple[str, str]]:
        """Extract code blocks with language tags.

        Args:
            content: Markdown content with code blocks

        Returns:
            List of (language, code) tuples
        """
        blocks = []

        # Pattern: ```language\ncode\n```
        pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)

        for match in pattern.finditer(content):
            lang_tag = match.group(1).lower() or 'text'
            code = match.group(2).strip()

            # Normalize language
            lang = cls.LANGUAGE_ALIASES.get(lang_tag, lang_tag)

            if code and lang != 'text':
                blocks.append((lang, code))

        return blocks

    @classmethod
    def is_executable(cls, language: str) -> bool:
        """Check if language is supported for execution."""
        return language in ['python', 'javascript', 'go', 'r', 'ruby', 'java']


class ExecutionProver:
    """Verify code examples through sandboxed execution."""

    SUPPORTED_LANGUAGES = {
        'python': 'python:3.11-slim',
        'javascript': 'node:18-slim',
        'go': 'golang:1.21-alpine',
        'r': 'r-base:4.3.0',
        'ruby': 'ruby:3.2-slim',
        'java': 'openjdk:17-slim',
    }

    def __init__(
        self,
        timeout_seconds: int = 30,
        memory_limit_mb: int = 256,
        use_pool: bool = True,
    ):
        """Initialize execution prover.

        Args:
            timeout_seconds: Max execution time per block
            memory_limit_mb: Memory limit for sandbox
            use_pool: Use container pooling for speed
        """
        self.timeout = timeout_seconds
        self.memory_limit = memory_limit_mb
        self.use_pool = use_pool
        self._sandbox = None

    def _get_sandbox(self, language: str) -> Optional[Any]:
        """Get or create sandbox for language."""
        if not SANDBOX_AVAILABLE:
            return None

        image = self.SUPPORTED_LANGUAGES.get(language)
        if not image:
            return None

        try:
            sandbox = DockerSandbox(
                image=image,
                keep_template=self.use_pool,
                verbose=False,
            )
            return sandbox
        except Exception:
            return None

    def execute_code(
        self,
        code: str,
        language: str = "python",
        setup_code: str = "",
    ) -> ExecutionResult:
        """Execute code in sandbox.

        Args:
            code: Code to execute
            language: Programming language
            setup_code: Optional setup code (imports, etc.)

        Returns:
            ExecutionResult with output or error
        """
        import time

        # Generate code hash for caching
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]

        if not SANDBOX_AVAILABLE:
            return ExecutionResult(
                success=False,
                output="",
                error="llm-sandbox not available",
                code_hash=code_hash,
                language=language,
            )

        if language not in self.SUPPORTED_LANGUAGES:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Language {language} not supported",
                code_hash=code_hash,
                language=language,
            )

        # Combine setup and main code
        full_code = f"{setup_code}\n{code}" if setup_code else code

        try:
            start_time = time.time()

            with SandboxSession(
                lang=language,
                verbose=False,
                keep_template=self.use_pool,
            ) as session:
                result = session.run(full_code)

            elapsed_ms = (time.time() - start_time) * 1000

            # Handle result based on llm-sandbox output format
            if hasattr(result, 'stdout'):
                output = result.stdout or ""
                error = result.stderr if hasattr(result, 'stderr') else None
                exit_code = result.exit_code if hasattr(result, 'exit_code') else 0
            else:
                # String result
                output = str(result) if result else ""
                error = None
                exit_code = 0

            success = exit_code == 0 and not error

            return ExecutionResult(
                success=success,
                output=output,
                error=error,
                exit_code=exit_code,
                execution_time_ms=elapsed_ms,
                language=language,
                code_hash=code_hash,
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1,
                language=language,
                code_hash=code_hash,
            )

    def verify_skill(
        self,
        skill_id: str,
        content: str,
        execute_all: bool = False,
    ) -> SkillExecutionReport:
        """Verify all code blocks in a skill.

        Args:
            skill_id: Skill identifier
            content: Skill markdown content
            execute_all: Execute all blocks even after failure

        Returns:
            SkillExecutionReport with all proofs
        """
        blocks = CodeBlockExtractor.extract(content)
        proofs = []

        executed = 0
        successful = 0
        failed = 0
        skipped = 0

        for language, code in blocks:
            if not CodeBlockExtractor.is_executable(language):
                skipped += 1
                proofs.append(ExecutionProof(
                    code_block=code,
                    language=language,
                    verified=False,
                ))
                continue

            # Skip obviously incomplete examples
            if self._is_example_placeholder(code):
                skipped += 1
                proofs.append(ExecutionProof(
                    code_block=code,
                    language=language,
                    verified=False,
                ))
                continue

            # Execute the code
            result = self.execute_code(code, language)
            executed += 1

            if result.success:
                successful += 1
                proofs.append(ExecutionProof(
                    code_block=code,
                    language=language,
                    verified=True,
                    result=result,
                ))
            else:
                failed += 1
                proofs.append(ExecutionProof(
                    code_block=code,
                    language=language,
                    verified=False,
                    result=result,
                ))

                if not execute_all:
                    # Stop on first failure
                    break

        return SkillExecutionReport(
            skill_id=skill_id,
            total_code_blocks=len(blocks),
            executed_blocks=executed,
            successful_blocks=successful,
            failed_blocks=failed,
            skipped_blocks=skipped,
            execution_proofs=proofs,
        )

    def _is_example_placeholder(self, code: str) -> bool:
        """Check if code is a placeholder/incomplete example."""
        placeholders = [
            '...',
            '# TODO',
            '# your code here',
            'pass  # implement',
            '<your_',
            'YOUR_',
            'INSERT_',
        ]
        code_lower = code.lower()
        return any(p.lower() in code_lower for p in placeholders)


class ExecutionProofCache:
    """Cache execution proofs to avoid re-running."""

    def __init__(self, cache_path: Optional[Path] = None):
        self.cache_path = cache_path or Path("./execution_cache.json")
        self._cache: dict[str, ExecutionResult] = {}
        self._load()

    def _load(self):
        """Load cache from disk."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path) as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._cache[k] = ExecutionResult(**v)
            except Exception:
                pass

    def _save(self):
        """Save cache to disk."""
        try:
            data = {k: v.to_dict() for k, v in self._cache.items()}
            with open(self.cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get(self, code_hash: str) -> Optional[ExecutionResult]:
        """Get cached result."""
        return self._cache.get(code_hash)

    def put(self, code_hash: str, result: ExecutionResult):
        """Cache a result."""
        self._cache[code_hash] = result
        self._save()


def verify_skill_execution(
    skill_id: str,
    content: str,
    timeout: int = 30,
) -> SkillExecutionReport:
    """Convenience function to verify skill execution.

    Args:
        skill_id: Skill identifier
        content: Skill markdown content
        timeout: Execution timeout in seconds

    Returns:
        SkillExecutionReport
    """
    prover = ExecutionProver(timeout_seconds=timeout)
    return prover.verify_skill(skill_id, content)


def get_verification_summary(report: SkillExecutionReport) -> str:
    """Generate human-readable summary."""
    lines = [
        "=" * 60,
        "EXECUTION PROOF REPORT",
        "=" * 60,
        "",
        f"Skill: {report.skill_id}",
        f"Overall Success: {'YES' if report.overall_success else 'NO'}",
        f"Verification Score: {report.verification_score:.2%}",
        "",
        "Code Blocks:",
        f"  Total: {report.total_code_blocks}",
        f"  Executed: {report.executed_blocks}",
        f"  Successful: {report.successful_blocks}",
        f"  Failed: {report.failed_blocks}",
        f"  Skipped: {report.skipped_blocks}",
    ]

    if report.execution_proofs:
        lines.append("")
        lines.append("Execution Results:")
        for i, proof in enumerate(report.execution_proofs, 1):
            status = "✓" if proof.verified else "✗"
            lines.append(f"  {status} Block {i} ({proof.language})")
            if proof.result:
                if proof.result.error:
                    error_preview = proof.result.error[:50]
                    lines.append(f"      Error: {error_preview}...")
                else:
                    lines.append(f"      Time: {proof.result.execution_time_ms:.1f}ms")

    lines.append("")
    lines.append("=" * 60)

    return '\n'.join(lines)


if __name__ == "__main__":
    # Demo
    print("Execution Proof System Demo")
    print("=" * 50)
    print(f"Sandbox available: {SANDBOX_AVAILABLE}")
    print()

    # Test code extraction
    sample_skill = '''
# Sample Skill

## Basic Usage

```python
x = 1 + 2
print(f"Result: {x}")
```

## Advanced Example

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

## Non-executable

```text
This is just text
```
'''

    print("Extracting code blocks...")
    blocks = CodeBlockExtractor.extract(sample_skill)
    print(f"Found {len(blocks)} code blocks")

    for lang, code in blocks:
        print(f"\n  Language: {lang}")
        print(f"  Code: {code[:50]}...")

    if SANDBOX_AVAILABLE:
        print("\n\nRunning execution proofs...")
        prover = ExecutionProver(timeout_seconds=10)
        report = prover.verify_skill("demo_skill", sample_skill)
        print(get_verification_summary(report))
    else:
        print("\n\nSkipping execution (sandbox not available)")
