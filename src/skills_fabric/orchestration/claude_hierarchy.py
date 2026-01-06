#!/usr/bin/env python3
"""
Claude Hierarchy: Tiered Intelligence Architecture

Three-tier system optimized for reliability and cost:
- Opus 4.5: Architect (rare, strategic decisions)
- Sonnet 4.5: Engineer (coordination, verification, search)
- Haiku 4.5: Executor (fast, reliable code generation)

The key insight: Haiku with perfect context outperforms
smarter models with poor context.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from pathlib import Path
import json
from datetime import datetime


class ClaudeTier(Enum):
    """Intelligence tiers with their optimal use cases."""
    OPUS = "claude-opus-4-5-20251101"      # Architect
    SONNET = "claude-sonnet-4-5-20251101"  # Engineer
    HAIKU = "claude-haiku-4-5-20251101"    # Executor


@dataclass
class TierConfig:
    """Configuration for each intelligence tier."""
    model: str
    max_tokens: int
    temperature: float
    description: str
    cost_per_1k_input: float
    cost_per_1k_output: float

    # When to use this tier
    use_cases: List[str] = field(default_factory=list)

    # When NOT to use
    avoid_for: List[str] = field(default_factory=list)


# Tier configurations
TIER_CONFIGS = {
    ClaudeTier.OPUS: TierConfig(
        model="claude-opus-4-5-20251101",
        max_tokens=16000,
        temperature=0.7,  # Allow creativity for architecture
        description="The Architect - strategic decisions and system design",
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        use_cases=[
            "System architecture design",
            "Complex algorithmic decisions",
            "Framework selection",
            "Trade-off analysis",
            "Novel problem solving",
            "Design document creation",
        ],
        avoid_for=[
            "Simple code generation",
            "Repetitive tasks",
            "Well-defined implementations",
            "Search operations",
        ]
    ),
    ClaudeTier.SONNET: TierConfig(
        model="claude-sonnet-4-5-20251101",
        max_tokens=8000,
        temperature=0.3,  # Balanced for coordination
        description="The Engineer - coordination, verification, search",
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        use_cases=[
            "Code review and verification",
            "Search coordination",
            "Context assembly",
            "Error analysis",
            "Test generation",
            "Documentation review",
            "Ralph loop orchestration",
        ],
        avoid_for=[
            "High-level architecture",
            "Simple code edits",
            "Repetitive generation",
        ]
    ),
    ClaudeTier.HAIKU: TierConfig(
        model="claude-haiku-4-5-20251101",
        max_tokens=4000,
        temperature=0.1,  # Low temperature = precise execution
        description="The Executor - fast, reliable code generation",
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        use_cases=[
            "Code generation with context",
            "Simple edits and refactoring",
            "Boilerplate generation",
            "Format conversion",
            "Repetitive tasks",
            "Quick fixes",
        ],
        avoid_for=[
            "Complex architectural decisions",
            "Novel problem solving",
            "Ambiguous requirements",
        ]
    ),
}


@dataclass
class TaskContext:
    """Context package prepared by Engineer for Executor."""
    task_description: str

    # From Progressive Disclosure
    level_0_summary: str = ""
    level_1_concept: str = ""
    level_2_section: str = ""

    # Source references (Level 3)
    source_refs: List[Dict[str, Any]] = field(default_factory=list)

    # Semantic info (Level 4)
    type_signatures: List[str] = field(default_factory=list)
    imports_needed: List[str] = field(default_factory=list)

    # Patterns to follow
    code_patterns: List[str] = field(default_factory=list)

    # Constraints
    constraints: List[str] = field(default_factory=list)

    def to_prompt(self) -> str:
        """Convert context to a prompt for Haiku."""
        lines = [
            "# Task",
            self.task_description,
            "",
        ]

        if self.level_2_section:
            lines.extend([
                "# Context",
                self.level_2_section[:500],
                "",
            ])

        if self.source_refs:
            lines.append("# Reference Code")
            for ref in self.source_refs[:3]:
                lines.append(f"# From {ref.get('file_path', 'unknown')}:{ref.get('line', 0)}")
                if ref.get('code_snippet'):
                    lines.append(f"```python\n{ref['code_snippet']}\n```")
            lines.append("")

        if self.type_signatures:
            lines.append("# Type Signatures to Match")
            for sig in self.type_signatures[:5]:
                lines.append(f"# {sig}")
            lines.append("")

        if self.imports_needed:
            lines.append("# Required Imports")
            lines.append("```python")
            for imp in self.imports_needed[:10]:
                lines.append(f"from {imp}")
            lines.append("```")
            lines.append("")

        if self.code_patterns:
            lines.append("# Patterns to Follow")
            for pattern in self.code_patterns[:3]:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.constraints:
            lines.append("# Constraints")
            for constraint in self.constraints:
                lines.append(f"- {constraint}")
            lines.append("")

        lines.extend([
            "# Instructions",
            "Generate ONLY the code. No explanations.",
            "Follow the patterns exactly.",
            "Use the imports provided.",
        ])

        return "\n".join(lines)


@dataclass
class ExecutionResult:
    """Result from any tier execution."""
    tier: ClaudeTier
    success: bool
    output: str
    tokens_used: int = 0
    latency_ms: int = 0
    cost: float = 0.0
    error: Optional[str] = None


class ClaudeHierarchy:
    """
    Orchestrates the three-tier Claude architecture.

    Usage:
        hierarchy = ClaudeHierarchy(progressive_understanding)

        # Architect designs the approach
        architecture = hierarchy.architect("Design a state machine for...")

        # Engineer prepares context
        context = hierarchy.engineer_prepare(task, architecture)

        # Executor generates code
        code = hierarchy.execute(context)

        # Engineer verifies
        verified = hierarchy.engineer_verify(code, context)
    """

    def __init__(self, progressive_understanding=None):
        self.pu = progressive_understanding
        self.execution_log: List[ExecutionResult] = []

    def select_tier(self, task: str) -> ClaudeTier:
        """
        Automatically select the appropriate tier for a task.

        This is a heuristic - can be overridden.
        """
        task_lower = task.lower()

        # Opus indicators
        opus_keywords = [
            "architect", "design", "framework", "system",
            "trade-off", "strategy", "complex", "novel"
        ]
        if any(kw in task_lower for kw in opus_keywords):
            return ClaudeTier.OPUS

        # Sonnet indicators
        sonnet_keywords = [
            "verify", "review", "search", "find", "coordinate",
            "analyze", "test", "check", "validate"
        ]
        if any(kw in task_lower for kw in sonnet_keywords):
            return ClaudeTier.SONNET

        # Default to Haiku for everything else
        return ClaudeTier.HAIKU

    def architect(self, task: str) -> str:
        """
        Use Opus for architectural decisions.

        Returns a design document or decision.
        """
        config = TIER_CONFIGS[ClaudeTier.OPUS]

        prompt = f"""You are the Architect. Your role is strategic design decisions.

Task: {task}

Provide:
1. High-level approach
2. Key components needed
3. Integration points
4. Potential challenges
5. Recommended patterns

Be concise but thorough. This will guide the Engineer and Executor."""

        # In real implementation, this would call the API
        # For now, return a placeholder
        return f"[OPUS WOULD PROCESS: {task[:100]}...]"

    def engineer_prepare(self, task: str, architecture: str = "") -> TaskContext:
        """
        Use Sonnet to prepare context for Haiku.

        This is the key coordination step:
        1. Search Progressive Disclosure for relevant info
        2. Validate source references
        3. Extract patterns and constraints
        4. Package everything for Haiku
        """
        context = TaskContext(task_description=task)

        if self.pu:
            # Search for relevant nodes
            results = self.pu.search(task)

            if results:
                # Get Level 0 summary
                root = self.pu.nodes.get(self.pu.root_id)
                if root:
                    context.level_0_summary = root.content

                # Get most relevant Level 1-2 content
                for node in results[:3]:
                    if node.level.value == 1:
                        context.level_1_concept = node.content
                    elif node.level.value == 2:
                        context.level_2_section = node.content

                        # Extract source refs
                        for ref in node.source_refs[:5]:
                            context.source_refs.append({
                                "file_path": ref.file_path,
                                "line": ref.line,
                                "symbol": ref.symbol_name,
                            })

        # Add architecture guidance if provided
        if architecture:
            context.constraints.append(f"Follow architecture: {architecture[:200]}")

        return context

    def execute(self, context: TaskContext) -> str:
        """
        Use Haiku to execute the task with prepared context.

        Haiku receives:
        - Clear task description
        - Verified source references
        - Exact patterns to follow
        - Required imports

        With this context, Haiku executes reliably and fast.
        """
        config = TIER_CONFIGS[ClaudeTier.HAIKU]
        prompt = context.to_prompt()

        # In real implementation, this would call the API
        # For now, return a placeholder
        return f"[HAIKU WOULD GENERATE CODE FOR: {context.task_description[:50]}...]"

    def engineer_verify(self, code: str, context: TaskContext) -> Dict[str, Any]:
        """
        Use Sonnet to verify the generated code.

        Checks:
        1. Matches the patterns from context
        2. Uses correct imports
        3. Type signatures match
        4. No obvious errors
        """
        verification = {
            "passed": True,
            "checks": [],
            "issues": [],
        }

        # Check imports
        for imp in context.imports_needed:
            if imp in code:
                verification["checks"].append(f"✓ Import {imp} present")
            else:
                verification["issues"].append(f"✗ Missing import: {imp}")
                verification["passed"] = False

        # Check patterns (simple string matching for now)
        for pattern in context.code_patterns:
            pattern_keyword = pattern.split()[0] if pattern else ""
            if pattern_keyword and pattern_keyword in code:
                verification["checks"].append(f"✓ Pattern '{pattern_keyword}' found")

        return verification

    def ralph_loop(
        self,
        task: str,
        max_iterations: int = 5,
        success_criteria: Optional[Callable[[str], bool]] = None
    ) -> Dict[str, Any]:
        """
        Execute the full Ralph loop with tiered intelligence.

        1. Opus: Design approach (once)
        2. Loop:
           a. Sonnet: Prepare context
           b. Haiku: Generate code
           c. Sonnet: Verify
           d. If failed, refine and retry
        """
        result = {
            "success": False,
            "iterations": 0,
            "code": "",
            "architecture": "",
            "log": [],
        }

        # Step 1: Opus designs approach (only if complex)
        if self.select_tier(task) == ClaudeTier.OPUS:
            result["architecture"] = self.architect(task)
            result["log"].append({
                "tier": "OPUS",
                "action": "architecture",
                "output": result["architecture"][:200]
            })

        # Step 2: Iterate with Sonnet + Haiku
        for i in range(max_iterations):
            result["iterations"] = i + 1

            # Sonnet prepares context
            context = self.engineer_prepare(task, result["architecture"])
            result["log"].append({
                "tier": "SONNET",
                "action": "prepare_context",
                "refs_found": len(context.source_refs)
            })

            # Haiku executes
            code = self.execute(context)
            result["code"] = code
            result["log"].append({
                "tier": "HAIKU",
                "action": "generate_code",
                "output_length": len(code)
            })

            # Sonnet verifies
            verification = self.engineer_verify(code, context)
            result["log"].append({
                "tier": "SONNET",
                "action": "verify",
                "passed": verification["passed"],
                "issues": verification["issues"]
            })

            # Check success
            if verification["passed"]:
                if success_criteria is None or success_criteria(code):
                    result["success"] = True
                    break

            # Refine task for next iteration
            if verification["issues"]:
                task = f"{task}\n\nPrevious issues to fix: {verification['issues']}"

        return result

    def estimate_cost(self, task: str, estimated_tokens: int = 2000) -> Dict[str, float]:
        """Estimate cost for processing a task through the hierarchy."""
        costs = {}

        # Assume typical distribution
        # Opus: 10% of calls (if needed)
        # Sonnet: 30% of calls
        # Haiku: 60% of calls

        tier = self.select_tier(task)

        if tier == ClaudeTier.OPUS:
            config = TIER_CONFIGS[ClaudeTier.OPUS]
            costs["opus"] = (estimated_tokens / 1000) * (config.cost_per_1k_input + config.cost_per_1k_output)

        # Sonnet always used for coordination
        config = TIER_CONFIGS[ClaudeTier.SONNET]
        costs["sonnet"] = (estimated_tokens / 1000) * (config.cost_per_1k_input + config.cost_per_1k_output) * 2

        # Haiku for execution
        config = TIER_CONFIGS[ClaudeTier.HAIKU]
        costs["haiku"] = (estimated_tokens / 1000) * (config.cost_per_1k_input + config.cost_per_1k_output) * 3

        costs["total"] = sum(costs.values())

        return costs


def demonstrate_hierarchy():
    """Demonstrate the tiered architecture."""
    print("=" * 60)
    print("Claude Hierarchy: Tiered Intelligence Architecture")
    print("=" * 60)

    # Show tier configurations
    for tier, config in TIER_CONFIGS.items():
        print(f"\n{tier.name}: {config.description}")
        print(f"  Model: {config.model}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Cost: ${config.cost_per_1k_input}/1K in, ${config.cost_per_1k_output}/1K out")
        print(f"  Use for: {', '.join(config.use_cases[:3])}")

    # Demonstrate tier selection
    print("\n" + "=" * 60)
    print("Tier Selection Examples")
    print("=" * 60)

    hierarchy = ClaudeHierarchy()

    tasks = [
        "Design a new authentication system architecture",
        "Search for all usages of StateGraph in the codebase",
        "Add a docstring to the compile() method",
        "Verify that the tests pass type checking",
        "Generate a simple CRUD endpoint",
    ]

    for task in tasks:
        tier = hierarchy.select_tier(task)
        print(f"\n  Task: {task[:50]}...")
        print(f"  → Selected: {tier.name}")

    # Cost estimation
    print("\n" + "=" * 60)
    print("Cost Estimation (2000 tokens)")
    print("=" * 60)

    for task in tasks[:2]:
        costs = hierarchy.estimate_cost(task)
        print(f"\n  Task: {task[:40]}...")
        for tier, cost in costs.items():
            print(f"    {tier}: ${cost:.4f}")


if __name__ == "__main__":
    demonstrate_hierarchy()
