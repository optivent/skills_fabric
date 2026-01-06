"""Pattern Library for Skills Fabric.

Inspired by Daniel Miessler's Fabric framework:
- Structured prompts with IDENTITY → STEPS → OUTPUT → CONSTRAINTS
- 234+ reusable patterns
- Consistent, reproducible results

Key Components:
- Pattern: A structured prompt template
- PatternRegistry: Discover and load patterns
- PatternExecutor: Execute patterns with variable substitution

Pattern Format:
```markdown
## IDENTITY
Who/what the pattern is

## STEPS
1. First step
2. Second step

## OUTPUT
Expected output format

## CONSTRAINTS
- Constraint 1
- Constraint 2
```

Usage:
    from skills_fabric.patterns import (
        PatternRegistry, PatternExecutor, ExecutionMode
    )

    # Load patterns
    registry = PatternRegistry()
    registry.load_builtin()

    # Execute a pattern
    executor = PatternExecutor(registry)
    result = executor.execute(
        pattern="create_skill",
        variables={"topic": "state management", "library": "langgraph"}
    )

    print(result.output)
"""
from .registry import (
    Pattern,
    PatternRegistry,
    BUILTIN_PATTERNS,
)
from .executor import (
    PatternExecutor,
    ExecutionMode,
    ExecutionResult,
    StepResult,
    execute_pattern,
)

__all__ = [
    # Registry
    "Pattern",
    "PatternRegistry",
    "BUILTIN_PATTERNS",
    # Executor
    "PatternExecutor",
    "ExecutionMode",
    "ExecutionResult",
    "StepResult",
    "execute_pattern",
]
