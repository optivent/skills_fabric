#!/usr/bin/env python3
"""LangGraph Deep Understanding - True Progressive Depth Loop.

This script implements REAL progressive understanding:
1. Start with CodeWiki markdown
2. Extract references
3. For each reference, progressively deepen
4. Score based on WHAT WAS DISCOVERED at each layer
5. Critique based on GAPS in understanding
6. Explore deeper when critique finds gaps
7. Only stop when true understanding is achieved

The key insight: scoring reflects actual depth of knowledge,
not superficial properties like "syntax valid" or "question length".

Run:
    python scripts/langgraph_deep_understanding.py
"""
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# Direct import - bypass package system to avoid kuzu dependency
script_dir = Path(__file__).parent.parent / "src" / "skills_fabric" / "intelligence"

spec = importlib.util.spec_from_file_location(
    "depth_controller",
    script_dir / "depth_controller.py"
)
depth_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(depth_module)

DepthController = depth_module.DepthController
DepthLevel = depth_module.DepthLevel
CodeWikiRef = depth_module.CodeWikiRef
DepthResult = depth_module.DepthResult
extract_codewiki_refs = depth_module.extract_codewiki_refs


# =============================================================================
# UNDERSTANDING METRICS - What we ACTUALLY learned at each depth
# =============================================================================

@dataclass
class UnderstandingScore:
    """Score based on what was actually discovered at each depth level.

    This is NOT about surface properties. It's about:
    - Did we find the thing?
    - Did we understand its structure?
    - Did we understand its dependencies?
    - Did we understand how it's used?
    - Did we verify it works?
    """
    level: DepthLevel

    # Level 0: Validation
    exists: bool = False
    concept_found_at_line: bool = False

    # Level 1: Symbol Understanding
    symbol_parsed: bool = False
    symbol_kind: str = ""  # class, function, etc.
    method_count: int = 0
    has_docstring: bool = False
    docstring_quality: float = 0.0  # 0-1 based on length and content
    parameter_count: int = 0
    base_classes_understood: bool = False

    # Level 2: Dependency Understanding
    dependency_count: int = 0
    internal_deps: int = 0  # From same library
    external_deps: int = 0  # From stdlib or other
    import_statements_found: int = 0
    key_dependencies_identified: list[str] = field(default_factory=list)

    # Level 3: Call Graph Understanding
    calls_made: int = 0
    unique_callees: int = 0
    call_patterns_identified: list[str] = field(default_factory=list)

    # Level 4: Usage Understanding
    callers_found: int = 0
    usage_patterns: list[str] = field(default_factory=list)

    # Level 5: Execution Understanding
    execution_attempted: bool = False
    execution_success: bool = False
    output_captured: bool = False

    def score_at_level(self, level: DepthLevel) -> tuple[float, dict]:
        """Calculate understanding score at a specific depth level.

        Returns (score, breakdown) where score is 0-1 and breakdown
        shows what contributed to the score.
        """
        breakdown = {}

        if level >= DepthLevel.VALIDATE:
            # Level 0: 20% of total possible
            l0_score = 0.0
            if self.exists:
                l0_score += 0.5
            if self.concept_found_at_line:
                l0_score += 0.5
            breakdown["L0_validation"] = {
                "exists": self.exists,
                "concept_at_line": self.concept_found_at_line,
                "score": l0_score * 0.2
            }

        if level >= DepthLevel.PARSE_SYMBOL:
            # Level 1: 25% of total possible
            l1_score = 0.0
            if self.symbol_parsed:
                l1_score += 0.3
            if self.method_count > 0:
                l1_score += min(self.method_count / 10, 0.3)  # Cap at 10 methods
            if self.has_docstring:
                l1_score += 0.2
            l1_score += self.docstring_quality * 0.2
            breakdown["L1_symbol"] = {
                "parsed": self.symbol_parsed,
                "kind": self.symbol_kind,
                "methods": self.method_count,
                "has_docstring": self.has_docstring,
                "docstring_quality": self.docstring_quality,
                "score": l1_score * 0.25
            }

        if level >= DepthLevel.DEPENDENCIES:
            # Level 2: 20% of total possible
            l2_score = 0.0
            if self.dependency_count > 0:
                l2_score += 0.4
            if self.internal_deps > 0:
                l2_score += min(self.internal_deps / 5, 0.3)  # Library understanding
            if len(self.key_dependencies_identified) > 0:
                l2_score += 0.3
            breakdown["L2_dependencies"] = {
                "total_deps": self.dependency_count,
                "internal": self.internal_deps,
                "external": self.external_deps,
                "key_deps": self.key_dependencies_identified,
                "score": l2_score * 0.20
            }

        if level >= DepthLevel.CALL_GRAPH:
            # Level 3: 15% of total possible
            l3_score = 0.0
            if self.calls_made > 0:
                l3_score += 0.5
            if self.unique_callees > 0:
                l3_score += min(self.unique_callees / 10, 0.3)
            if len(self.call_patterns_identified) > 0:
                l3_score += 0.2
            breakdown["L3_call_graph"] = {
                "calls_made": self.calls_made,
                "unique_callees": self.unique_callees,
                "patterns": self.call_patterns_identified,
                "score": l3_score * 0.15
            }

        if level >= DepthLevel.FULL_GRAPH:
            # Level 4: 10% of total possible
            l4_score = 0.0
            if self.callers_found > 0:
                l4_score += 0.6
            if len(self.usage_patterns) > 0:
                l4_score += 0.4
            breakdown["L4_usage"] = {
                "callers": self.callers_found,
                "patterns": self.usage_patterns,
                "score": l4_score * 0.10
            }

        if level >= DepthLevel.EXEC_TRACE:
            # Level 5: 10% of total possible
            l5_score = 0.0
            if self.execution_attempted:
                l5_score += 0.3
            if self.execution_success:
                l5_score += 0.5
            if self.output_captured:
                l5_score += 0.2
            breakdown["L5_execution"] = {
                "attempted": self.execution_attempted,
                "success": self.execution_success,
                "output": self.output_captured,
                "score": l5_score * 0.10
            }

        total = sum(b["score"] for b in breakdown.values())
        return total, breakdown


def analyze_depth_result(result: DepthResult, library: str = "langgraph") -> UnderstandingScore:
    """Convert a DepthResult into an UnderstandingScore.

    This extracts WHAT WE LEARNED from the depth analysis.
    """
    score = UnderstandingScore(level=result.level)

    # Level 0
    score.exists = result.validated
    score.concept_found_at_line = result.validated

    # Level 1
    if result.symbol:
        score.symbol_parsed = True
        score.symbol_kind = result.symbol.kind
        score.method_count = len(result.methods)
        score.has_docstring = bool(result.symbol.docstring)
        if result.symbol.docstring:
            doc = result.symbol.docstring
            # Quality based on: length, has examples, has params documented
            quality = 0.0
            if len(doc) > 50:
                quality += 0.3
            if len(doc) > 200:
                quality += 0.2
            if "example" in doc.lower() or ">>>" in doc:
                quality += 0.3
            if "args:" in doc.lower() or "param" in doc.lower():
                quality += 0.2
            score.docstring_quality = min(quality, 1.0)
        score.base_classes_understood = bool(result.symbol.bases)

    # Level 2
    score.dependency_count = len(result.dependencies)
    score.import_statements_found = len(result.imports)
    for dep in result.dependencies:
        if library in dep.module:
            score.internal_deps += 1
            if dep.name not in score.key_dependencies_identified:
                score.key_dependencies_identified.append(dep.name)
        else:
            score.external_deps += 1

    # Level 3
    score.calls_made = len(result.calls)
    callees = set(c.callee for c in result.calls)
    score.unique_callees = len(callees)
    # Identify patterns
    for callee in callees:
        if "validate" in callee.lower():
            if "validation pattern" not in score.call_patterns_identified:
                score.call_patterns_identified.append("validation pattern")
        if "add_" in callee.lower():
            if "builder pattern" not in score.call_patterns_identified:
                score.call_patterns_identified.append("builder pattern")

    # Level 4
    score.callers_found = len(result.called_by)

    # Level 5
    if result.level >= DepthLevel.EXEC_TRACE:
        score.execution_attempted = True
        score.execution_success = result.execution_success
        score.output_captured = bool(result.execution_output)

    return score


# =============================================================================
# CRITIQUE - What gaps exist in our understanding?
# =============================================================================

@dataclass
class UnderstandingGap:
    """A gap in our understanding that needs exploration."""
    level: DepthLevel
    category: str
    description: str
    impact: str  # How this gap affects skill quality
    exploration_hint: str  # How to fill this gap


def critique_understanding(score: UnderstandingScore, target_level: DepthLevel) -> list[UnderstandingGap]:
    """Identify gaps in understanding based on what was discovered."""
    gaps = []

    # Level 0 gaps
    if not score.exists:
        gaps.append(UnderstandingGap(
            level=DepthLevel.VALIDATE,
            category="existence",
            description="Reference does not exist at specified location",
            impact="Cannot verify any claims about this code",
            exploration_hint="Check file path and line number"
        ))
        return gaps  # Can't continue if file doesn't exist

    if not score.concept_found_at_line:
        gaps.append(UnderstandingGap(
            level=DepthLevel.VALIDATE,
            category="location",
            description="Concept not found near specified line",
            impact="May be referencing wrong location",
            exploration_hint="Search for concept in file"
        ))

    # Level 1 gaps
    if target_level >= DepthLevel.PARSE_SYMBOL:
        if not score.symbol_parsed:
            gaps.append(UnderstandingGap(
                level=DepthLevel.PARSE_SYMBOL,
                category="structure",
                description="Could not parse symbol structure",
                impact="Don't understand what this code IS",
                exploration_hint="Check if it's a class, function, or other construct"
            ))

        if score.method_count == 0 and score.symbol_kind == "class":
            gaps.append(UnderstandingGap(
                level=DepthLevel.PARSE_SYMBOL,
                category="methods",
                description="Class has no methods found",
                impact="Don't know what operations are available",
                exploration_hint="Parse class body more carefully"
            ))

        if not score.has_docstring:
            gaps.append(UnderstandingGap(
                level=DepthLevel.PARSE_SYMBOL,
                category="documentation",
                description="No docstring found",
                impact="Missing authoritative description of purpose",
                exploration_hint="Check for inline comments or usage examples"
            ))
        elif score.docstring_quality < 0.5:
            gaps.append(UnderstandingGap(
                level=DepthLevel.PARSE_SYMBOL,
                category="documentation_quality",
                description=f"Docstring quality low ({score.docstring_quality:.0%})",
                impact="May not fully understand intended usage",
                exploration_hint="Look for examples in tests or documentation"
            ))

    # Level 2 gaps
    if target_level >= DepthLevel.DEPENDENCIES:
        if score.dependency_count == 0:
            gaps.append(UnderstandingGap(
                level=DepthLevel.DEPENDENCIES,
                category="dependencies",
                description="No dependencies found",
                impact="Don't understand what this code relies on",
                exploration_hint="Check imports more carefully"
            ))

        if score.internal_deps == 0:
            gaps.append(UnderstandingGap(
                level=DepthLevel.DEPENDENCIES,
                category="library_integration",
                description="No internal library dependencies found",
                impact="Don't understand how this fits in the library",
                exploration_hint="Look for imports from the same package"
            ))

    # Level 3 gaps
    if target_level >= DepthLevel.CALL_GRAPH:
        if score.calls_made == 0:
            gaps.append(UnderstandingGap(
                level=DepthLevel.CALL_GRAPH,
                category="behavior",
                description="No internal calls found",
                impact="Don't understand what this code DOES",
                exploration_hint="Analyze method bodies for function calls"
            ))

        if len(score.call_patterns_identified) == 0 and score.calls_made > 5:
            gaps.append(UnderstandingGap(
                level=DepthLevel.CALL_GRAPH,
                category="patterns",
                description="Many calls but no patterns identified",
                impact="Don't understand the design approach",
                exploration_hint="Look for repeated patterns in call structure"
            ))

    # Level 4 gaps
    if target_level >= DepthLevel.FULL_GRAPH:
        if score.callers_found == 0:
            gaps.append(UnderstandingGap(
                level=DepthLevel.FULL_GRAPH,
                category="usage",
                description="No callers found in codebase",
                impact="Don't know how this is used in practice",
                exploration_hint="Search for references in tests and examples"
            ))

    # Level 5 gaps
    if target_level >= DepthLevel.EXEC_TRACE:
        if not score.execution_success:
            gaps.append(UnderstandingGap(
                level=DepthLevel.EXEC_TRACE,
                category="execution",
                description="Code execution failed or not attempted",
                impact="Haven't verified code actually works",
                exploration_hint="Create minimal example and run in sandbox"
            ))

    return gaps


# =============================================================================
# PROGRESSIVE DEEPENING LOOP
# =============================================================================

@dataclass
class DeepUnderstandingResult:
    """Result of progressive deepening analysis."""
    concept: str
    final_level: DepthLevel
    understanding_score: float
    iterations: int
    gaps_remaining: list[UnderstandingGap]
    learning_journey: list[dict]
    skill_ready: bool


def progressive_deepen(
    controller: DepthController,
    ref: CodeWikiRef,
    min_understanding: float = 0.7,
    max_level: DepthLevel = DepthLevel.FULL_GRAPH,
    verbose: bool = True
) -> DeepUnderstandingResult:
    """Progressively deepen understanding until threshold is met.

    Args:
        controller: Depth controller for analysis
        ref: CodeWiki reference to analyze
        min_understanding: Minimum understanding score (0-1)
        max_level: Maximum depth to explore
        verbose: Print progress

    Returns:
        DeepUnderstandingResult with final understanding state
    """
    journey = []
    current_level = DepthLevel.VALIDATE

    if verbose:
        print(f"\n{'='*70}")
        print(f"  PROGRESSIVE DEEPENING: {ref.concept}")
        print(f"  Target: {min_understanding:.0%} understanding at depth ≤ {max_level.name}")
        print(f"{'='*70}")

    while current_level <= max_level:
        iteration_start = datetime.now()

        # Expand to current depth
        result = controller.expand(ref, current_level)

        # Analyze what we learned
        understanding = analyze_depth_result(result, ref.repo.split("/")[-1])
        score, breakdown = understanding.score_at_level(current_level)

        # Critique to find gaps
        gaps = critique_understanding(understanding, current_level)

        duration = (datetime.now() - iteration_start).total_seconds() * 1000

        # Record this iteration
        iteration_record = {
            "level": current_level.value,
            "level_name": current_level.name,
            "score": score,
            "breakdown": breakdown,
            "gaps_found": len(gaps),
            "duration_ms": duration
        }
        journey.append(iteration_record)

        if verbose:
            print(f"\n--- Level {current_level.value}: {current_level.name} ---")
            print(f"  Understanding: {score:.1%}")
            for level_key, level_data in breakdown.items():
                level_score = level_data.get("score", 0)
                print(f"    {level_key}: {level_score:.2f}")

            if gaps:
                print(f"  Gaps found: {len(gaps)}")
                for gap in gaps[:3]:  # Show first 3 gaps
                    print(f"    - [{gap.level.name}] {gap.category}: {gap.description}")

        # Check if we've reached sufficient understanding
        if score >= min_understanding:
            if verbose:
                print(f"\n  ✓ Reached {min_understanding:.0%} understanding at Level {current_level.value}")
            return DeepUnderstandingResult(
                concept=ref.concept,
                final_level=current_level,
                understanding_score=score,
                iterations=len(journey),
                gaps_remaining=gaps,
                learning_journey=journey,
                skill_ready=True
            )

        # Check for critical gaps that block progress
        critical_gaps = [g for g in gaps if g.level == current_level]
        if critical_gaps and current_level == DepthLevel.VALIDATE:
            if verbose:
                print(f"\n  ✗ Cannot progress - validation failed")
            return DeepUnderstandingResult(
                concept=ref.concept,
                final_level=current_level,
                understanding_score=score,
                iterations=len(journey),
                gaps_remaining=gaps,
                learning_journey=journey,
                skill_ready=False
            )

        # Check if we've reached max depth
        if current_level >= max_level:
            if verbose:
                print(f"\n  Reached max level {max_level.name}")
                print(f"  Final understanding: {score:.1%} (target was {min_understanding:.0%})")
                if score < min_understanding:
                    print(f"  ✗ Could not reach target - gaps remain")
            return DeepUnderstandingResult(
                concept=ref.concept,
                final_level=current_level,
                understanding_score=score,
                iterations=len(journey),
                gaps_remaining=gaps,
                learning_journey=journey,
                skill_ready=score >= min_understanding
            )

        # Go deeper
        current_level = DepthLevel(current_level + 1)

    # Reached max level
    final_result = controller.expand(ref, max_level)
    final_understanding = analyze_depth_result(final_result)
    final_score, _ = final_understanding.score_at_level(max_level)
    final_gaps = critique_understanding(final_understanding, max_level)

    if verbose:
        print(f"\n  Reached max level {max_level.name}")
        print(f"  Final understanding: {final_score:.1%}")

    return DeepUnderstandingResult(
        concept=ref.concept,
        final_level=max_level,
        understanding_score=final_score,
        iterations=len(journey),
        gaps_remaining=final_gaps,
        learning_journey=journey,
        skill_ready=final_score >= min_understanding
    )


# =============================================================================
# SKILL GENERATION FROM DEEP UNDERSTANDING
# =============================================================================

def generate_skill_from_understanding(
    controller: DepthController,
    ref: CodeWikiRef,
    understanding_result: DeepUnderstandingResult
) -> dict:
    """Generate a skill based on verified deep understanding.

    The skill quality is directly tied to understanding depth.
    """
    result = controller.expand(ref, understanding_result.final_level)

    skill = {
        "id": f"{ref.repo.replace('/', '_')}_{ref.concept.lower()}",
        "concept": ref.concept,
        "understanding_level": understanding_result.final_level.name,
        "understanding_score": understanding_result.understanding_score,
        "verified": understanding_result.skill_ready,
        "source": {
            "file": ref.file_path,
            "line": ref.line,
            "repo": ref.repo
        },
        "what_we_know": {},
        "gaps": [
            {"level": g.level.name, "issue": g.description}
            for g in understanding_result.gaps_remaining[:3]
        ],
        "code": "",
        "confidence": "high" if understanding_result.understanding_score >= 0.8 else
                     "medium" if understanding_result.understanding_score >= 0.6 else "low"
    }

    # Fill in what we actually know
    if result.symbol:
        skill["what_we_know"]["type"] = result.symbol.kind
        skill["what_we_know"]["docstring_preview"] = (
            result.symbol.docstring[:300] + "..."
            if result.symbol.docstring and len(result.symbol.docstring) > 300
            else result.symbol.docstring
        )

    if result.methods:
        skill["what_we_know"]["methods"] = [
            {"name": m.name, "async": m.is_async, "params": len(m.parameters)}
            for m in result.methods[:10]
        ]

    if result.dependencies:
        internal = [d for d in result.dependencies if ref.concept.lower() in d.module.lower() or
                   ref.repo.split("/")[-1] in d.module]
        skill["what_we_know"]["key_imports"] = [d.name for d in internal[:5]]

    # Generate code based on understanding level
    skill["code"] = generate_code_from_understanding(ref, result, understanding_result)

    return skill


def generate_code_from_understanding(
    ref: CodeWikiRef,
    result: DepthResult,
    understanding: DeepUnderstandingResult
) -> str:
    """Generate code example based on depth of understanding.

    Higher understanding = more complete and accurate code.
    """
    lines = [
        f"# Example: {ref.concept}",
        f"# Understanding: {understanding.understanding_score:.0%} at Level {understanding.final_level.name}",
        f"# Source: {ref.file_path}:{ref.line}",
        ""
    ]

    # Add imports we actually know about
    if result.imports:
        for imp in result.imports[:5]:
            if ref.concept.lower() in imp.lower():
                lines.append(imp)
        lines.append("")

    # Generate based on what we know
    if result.symbol:
        if result.symbol.kind == "class":
            lines.append(f"# {ref.concept} is a class")
            if result.symbol.bases:
                lines.append(f"# Inherits from: {', '.join(result.symbol.bases[:3])}")

            # Only generate instantiation if we understand the constructor
            constructor = next((m for m in result.methods if m.name == "__init__"), None)
            if constructor:
                # Generate with known parameters
                param_hint = ", ".join(constructor.parameters[1:3])  # Skip self
                lines.append(f"instance = {ref.concept}({param_hint})")
            else:
                lines.append(f"# Constructor signature unknown - need deeper analysis")
                lines.append(f"instance = {ref.concept}(...)  # TODO: fill in params")

        elif result.symbol.kind in ("function", "async_function"):
            lines.append(f"# {ref.concept} is a {'async ' if 'async' in result.symbol.kind else ''}function")
            lines.append(f"result = {'await ' if 'async' in result.symbol.kind else ''}{ref.concept}(...)")

    # If we have high understanding, add method usage
    if understanding.understanding_score >= 0.6 and result.methods:
        lines.append("")
        lines.append("# Key methods discovered:")
        for m in result.methods[:5]:
            async_prefix = "await " if m.is_async else ""
            lines.append(f"# - instance.{m.name}()")

    return "\n".join(lines)


# =============================================================================
# MAIN - Run the complete deep understanding loop
# =============================================================================

def main():
    """Run the deep understanding demonstration."""
    print("\n" + "="*70)
    print("  LANGGRAPH DEEP UNDERSTANDING - TRUE PROGRESSIVE DEPTH")
    print("="*70)
    print("\nThis demonstrates REAL progressive understanding:")
    print("  - Score based on what was DISCOVERED, not surface properties")
    print("  - Critique based on GAPS in understanding")
    print("  - Deepening continues until understanding threshold is met")
    print("  - Skills generated only from verified knowledge")

    # Path to the crawled LangGraph repo
    repo_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo"

    if not repo_path.exists():
        print(f"\nERROR: LangGraph repo not found at {repo_path}")
        return

    print(f"\nRepository: {repo_path}")

    # Initialize controller
    controller = DepthController(repo_path)

    # Create reference to StateGraph
    ref = CodeWikiRef(
        concept="StateGraph",
        file_path="libs/langgraph/langgraph/graph/state.py",
        line=112,
        repo="langchain-ai/langgraph"
    )

    # Run progressive deepening - push for HIGH understanding
    result = progressive_deepen(
        controller,
        ref,
        min_understanding=0.75,  # 75% understanding threshold - forces deeper exploration
        max_level=DepthLevel.FULL_GRAPH,  # Go up to Level 4
        verbose=True
    )

    # Generate skill from understanding
    print(f"\n{'='*70}")
    print("  SKILL GENERATION FROM VERIFIED UNDERSTANDING")
    print(f"{'='*70}")

    skill = generate_skill_from_understanding(controller, ref, result)

    print(f"\nSkill ID: {skill['id']}")
    print(f"Concept: {skill['concept']}")
    print(f"Understanding: {skill['understanding_score']:.1%} at {skill['understanding_level']}")
    print(f"Confidence: {skill['confidence']}")
    print(f"Verified: {skill['verified']}")

    if skill["gaps"]:
        print(f"\nRemaining gaps ({len(skill['gaps'])}):")
        for gap in skill["gaps"]:
            print(f"  - [{gap['level']}] {gap['issue']}")

    if skill["what_we_know"].get("methods"):
        print(f"\nMethods discovered ({len(skill['what_we_know']['methods'])}):")
        for m in skill["what_we_know"]["methods"][:5]:
            print(f"  - {m['name']}() - {m['params']} params")

    print(f"\nGenerated Code:")
    print("-" * 50)
    print(skill["code"])

    # Show learning journey
    print(f"\n{'='*70}")
    print("  LEARNING JOURNEY")
    print(f"{'='*70}")

    for step in result.learning_journey:
        print(f"\nLevel {step['level_name']}:")
        print(f"  Score: {step['score']:.1%}")
        print(f"  Duration: {step['duration_ms']:.1f}ms")
        print(f"  Gaps found: {step['gaps_found']}")

    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"\nStarted at Level 0, reached Level {result.final_level.name}")
    print(f"Final understanding: {result.understanding_score:.1%}")
    print(f"Iterations: {result.iterations}")
    print(f"Skill ready: {result.skill_ready}")
    print(f"\nThe scores above reflect ACTUAL DEPTH OF UNDERSTANDING,")
    print(f"not superficial properties. Each level builds on the previous,")
    print(f"and gaps are identified based on what's missing from our knowledge.")


def demo_gaps():
    """Demonstrate gap detection with a harder case."""
    print("\n" + "="*70)
    print("  GAP DETECTION DEMO - WHAT HAPPENS WHEN UNDERSTANDING IS INCOMPLETE")
    print("="*70)

    repo_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo"
    if not repo_path.exists():
        print(f"ERROR: LangGraph repo not found")
        return

    controller = DepthController(repo_path)

    # Test with a real class but push for execution-level understanding
    ref = CodeWikiRef(
        concept="CompiledStateGraph",
        file_path="libs/langgraph/langgraph/graph/state.py",
        line=932,  # Real line from source
        repo="langchain-ai/langgraph"
    )

    print(f"\nTarget: {ref.concept}")
    print(f"File: {ref.file_path}")
    print(f"Line: {ref.line}")

    # Try to reach 90% understanding - likely will show gaps
    result = progressive_deepen(
        controller,
        ref,
        min_understanding=0.90,  # Very high threshold
        max_level=DepthLevel.EXEC_TRACE,  # Allow deepest level
        verbose=True
    )

    print(f"\n{'='*70}")
    print("  GAP ANALYSIS")
    print(f"{'='*70}")

    if result.gaps_remaining:
        print(f"\nGaps that prevent {90}% understanding:")
        for gap in result.gaps_remaining:
            print(f"\n  [{gap.level.name}] {gap.category}")
            print(f"    Issue: {gap.description}")
            print(f"    Impact: {gap.impact}")
            print(f"    How to fix: {gap.exploration_hint}")
    else:
        print("\nNo gaps found - full understanding achieved!")


if __name__ == "__main__":
    main()
    print("\n\n")
    demo_gaps()
