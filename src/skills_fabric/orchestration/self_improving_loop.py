"""Self-Improving Skill Generation Loop.

Implements the Ralph Wiggum autonomous iteration pattern with:
1. Generation - Create skill from verified source
2. Verification - Test in sandbox
3. Critique - Identify weaknesses
4. Exploration - Find better evidence
5. Reflection - Update strategy
6. Re-implementation - Improve the skill

The key insight: failures are data, not errors.
Each iteration learns from the previous, progressively improving.

Usage:
    from skills_fabric.orchestration.self_improving_loop import (
        SelfImprovingFactory,
        ImprovementCycle,
    )

    factory = SelfImprovingFactory(
        repo_path="/path/to/langgraph",
        library="langgraph"
    )

    # Generate with self-improvement
    result = await factory.generate_with_improvement(
        concept="StateGraph",
        file_path="libs/langgraph/langgraph/graph/state.py",
        line=112,
        max_cycles=5
    )

    print(f"Cycles: {result.cycles_completed}")
    print(f"Final quality: {result.final_quality}")
    print(f"Learnings: {result.learnings}")
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum
from pathlib import Path

from ..intelligence.depth_controller import (
    DepthController,
    DepthLevel,
    CodeWikiRef,
    DepthResult,
    determine_depth,
)


class CyclePhase(Enum):
    """Phases of the improvement cycle."""
    GENERATE = "generate"
    VERIFY = "verify"
    CRITIQUE = "critique"
    EXPLORE = "explore"
    REFLECT = "reflect"
    REIMPLEMENT = "reimplement"


@dataclass
class CritiqueFinding:
    """A finding from self-critique."""
    category: str  # grounding, execution, coverage, clarity
    severity: str  # critical, major, minor
    description: str
    suggestion: str
    evidence: str = ""


@dataclass
class ExplorationResult:
    """Result from exploration phase."""
    new_refs: list[CodeWikiRef] = field(default_factory=list)
    additional_context: str = ""
    alternative_approaches: list[str] = field(default_factory=list)
    confidence_delta: float = 0.0


@dataclass
class Reflection:
    """Reflection from a cycle."""
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    strategy_adjustments: list[str] = field(default_factory=list)
    depth_recommendation: Optional[DepthLevel] = None


@dataclass
class SkillDraft:
    """A draft skill being improved."""
    question: str
    code: str
    concepts_taught: list[str]
    symbols_used: list[str]
    source_refs: list[CodeWikiRef]
    depth_level: DepthLevel
    grounding_score: float = 0.0
    execution_verified: bool = False
    iteration: int = 0


@dataclass
class ImprovementCycle:
    """Record of one improvement cycle."""
    iteration: int
    phase: CyclePhase
    draft_before: Optional[SkillDraft]
    draft_after: Optional[SkillDraft]
    critique: list[CritiqueFinding] = field(default_factory=list)
    exploration: Optional[ExplorationResult] = None
    reflection: Optional[Reflection] = None
    quality_before: float = 0.0
    quality_after: float = 0.0
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ImprovementResult:
    """Final result of self-improving generation."""
    success: bool
    final_skill: Optional[SkillDraft]
    cycles: list[ImprovementCycle]
    cycles_completed: int
    final_quality: float
    initial_quality: float
    learnings: list[str]
    total_duration_ms: float


class SelfImprovingFactory:
    """Factory for generating skills with self-improvement loop.

    Core Philosophy:
    - Every failure teaches us something
    - Quality improves through iteration
    - Verification is non-negotiable
    - Grounding in source is the foundation
    """

    def __init__(
        self,
        repo_path: Path | str,
        library: str,
        min_quality: float = 0.8,
        max_depth: DepthLevel = DepthLevel.CALL_GRAPH
    ):
        """Initialize the self-improving factory.

        Args:
            repo_path: Path to cloned repository
            library: Library name (e.g., "langgraph")
            min_quality: Minimum quality score to accept (0-1)
            max_depth: Maximum depth level to analyze
        """
        self.repo_path = Path(repo_path)
        self.library = library
        self.min_quality = min_quality
        self.max_depth = max_depth
        self.depth_controller = DepthController(repo_path)
        self._learnings: list[str] = []

    async def generate_with_improvement(
        self,
        concept: str,
        file_path: str,
        line: int,
        max_cycles: int = 5,
        skill_type: str = "how_to_use"
    ) -> ImprovementResult:
        """Generate a skill with self-improvement loop.

        Args:
            concept: The concept to teach (e.g., "StateGraph")
            file_path: Path to source file in repo
            line: Line number of the symbol
            max_cycles: Maximum improvement cycles
            skill_type: Type of skill (how_to_use, what_does, how_works, debug)

        Returns:
            ImprovementResult with final skill and cycle history
        """
        start_time = datetime.now()
        cycles: list[ImprovementCycle] = []

        # Create initial reference
        ref = CodeWikiRef(
            concept=concept,
            file_path=file_path,
            line=line,
            repo=self.library
        )

        # Determine initial depth
        depth = determine_depth(skill_type)
        depth = min(depth, self.max_depth)

        # Phase 1: Initial generation
        current_draft = await self._generate(ref, depth)
        initial_quality = self._assess_quality(current_draft)

        for i in range(max_cycles):
            cycle_start = datetime.now()
            quality_before = self._assess_quality(current_draft)

            # Phase 2: Verify
            verification = await self._verify(current_draft)
            if not verification["passed"]:
                current_draft.execution_verified = False

            # Phase 3: Critique
            critique = self._critique(current_draft, verification)

            # Check if quality is good enough
            if quality_before >= self.min_quality and not critique:
                cycles.append(ImprovementCycle(
                    iteration=i,
                    phase=CyclePhase.VERIFY,
                    draft_before=current_draft,
                    draft_after=current_draft,
                    quality_before=quality_before,
                    quality_after=quality_before,
                    duration_ms=(datetime.now() - cycle_start).total_seconds() * 1000
                ))
                break

            # Phase 4: Explore for better evidence
            exploration = await self._explore(current_draft, critique)

            # Phase 5: Reflect on what to change
            reflection = self._reflect(current_draft, critique, exploration)

            # Phase 6: Re-implement with improvements
            draft_before = current_draft
            current_draft = await self._reimplement(
                current_draft, critique, exploration, reflection
            )

            quality_after = self._assess_quality(current_draft)

            # Record the cycle
            cycles.append(ImprovementCycle(
                iteration=i,
                phase=CyclePhase.REIMPLEMENT,
                draft_before=draft_before,
                draft_after=current_draft,
                critique=critique,
                exploration=exploration,
                reflection=reflection,
                quality_before=quality_before,
                quality_after=quality_after,
                duration_ms=(datetime.now() - cycle_start).total_seconds() * 1000
            ))

            # Add learnings
            self._learnings.extend(reflection.what_worked)
            self._learnings.extend(
                [f"Avoid: {f}" for f in reflection.what_failed]
            )

        total_duration = (datetime.now() - start_time).total_seconds() * 1000

        return ImprovementResult(
            success=self._assess_quality(current_draft) >= self.min_quality,
            final_skill=current_draft,
            cycles=cycles,
            cycles_completed=len(cycles),
            final_quality=self._assess_quality(current_draft),
            initial_quality=initial_quality,
            learnings=list(set(self._learnings)),  # Deduplicate
            total_duration_ms=total_duration
        )

    async def _generate(self, ref: CodeWikiRef, depth: DepthLevel) -> SkillDraft:
        """Phase 1: Generate initial skill draft."""
        # Use depth controller to get symbol info
        result = self.depth_controller.expand(ref, depth)

        # Build question from concept
        question = self._generate_question(ref, result)

        # Build code example from source
        code = self._generate_code(ref, result)

        return SkillDraft(
            question=question,
            code=code,
            concepts_taught=[ref.concept],
            symbols_used=[result.symbol.name] if result.symbol else [],
            source_refs=[ref],
            depth_level=depth,
            grounding_score=1.0 if result.validated else 0.0,
            execution_verified=False,
            iteration=0
        )

    async def _verify(self, draft: SkillDraft) -> dict:
        """Phase 2: Verify the skill works."""
        # Check grounding
        grounding_ok = draft.grounding_score >= 0.8

        # Check code syntax
        syntax_ok = self._check_syntax(draft.code)

        # TODO: Sandbox execution
        execution_ok = syntax_ok  # Placeholder

        return {
            "passed": grounding_ok and syntax_ok,
            "grounding": grounding_ok,
            "syntax": syntax_ok,
            "execution": execution_ok,
            "errors": []
        }

    def _critique(
        self,
        draft: SkillDraft,
        verification: dict
    ) -> list[CritiqueFinding]:
        """Phase 3: Critique the skill and find weaknesses."""
        findings = []

        # Grounding critique
        if draft.grounding_score < 0.8:
            findings.append(CritiqueFinding(
                category="grounding",
                severity="critical",
                description="Skill not fully grounded in source code",
                suggestion="Add more source references and validate all claims",
                evidence=f"Grounding score: {draft.grounding_score}"
            ))

        # Execution critique
        if not verification.get("execution", False):
            findings.append(CritiqueFinding(
                category="execution",
                severity="critical",
                description="Code does not execute successfully",
                suggestion="Fix syntax errors and ensure all imports are present",
                evidence=str(verification.get("errors", []))
            ))

        # Coverage critique
        if len(draft.symbols_used) < 1:
            findings.append(CritiqueFinding(
                category="coverage",
                severity="major",
                description="Skill does not reference any symbols",
                suggestion="Include at least one symbol from source",
                evidence=""
            ))

        # Clarity critique
        if len(draft.question) < 20:
            findings.append(CritiqueFinding(
                category="clarity",
                severity="minor",
                description="Question is too short",
                suggestion="Expand question to be more descriptive",
                evidence=f"Question length: {len(draft.question)}"
            ))

        return findings

    async def _explore(
        self,
        draft: SkillDraft,
        critique: list[CritiqueFinding]
    ) -> ExplorationResult:
        """Phase 4: Explore for better evidence."""
        result = ExplorationResult()

        # If grounding is weak, explore for more references
        grounding_issues = [c for c in critique if c.category == "grounding"]
        if grounding_issues:
            # Use depth controller to find related symbols
            for ref in draft.source_refs:
                expanded = self.depth_controller.expand(ref, DepthLevel.DEPENDENCIES)
                for dep in expanded.dependencies:
                    if dep.is_from_import and self.library in dep.module:
                        # This is a related symbol
                        result.additional_context += f"\nRelated: {dep.module}.{dep.name}"
                        result.confidence_delta += 0.1

        # If execution failed, explore examples
        execution_issues = [c for c in critique if c.category == "execution"]
        if execution_issues:
            result.alternative_approaches.append(
                "Try simpler example with minimal dependencies"
            )
            result.alternative_approaches.append(
                "Check for missing imports in source"
            )

        return result

    def _reflect(
        self,
        draft: SkillDraft,
        critique: list[CritiqueFinding],
        exploration: ExplorationResult
    ) -> Reflection:
        """Phase 5: Reflect on what to change."""
        reflection = Reflection()

        # What worked
        if draft.grounding_score > 0.5:
            reflection.what_worked.append("Source reference found")
        if draft.symbols_used:
            reflection.what_worked.append("Symbols extracted from source")

        # What failed
        for finding in critique:
            if finding.severity == "critical":
                reflection.what_failed.append(finding.description)

        # Strategy adjustments
        if exploration.alternative_approaches:
            reflection.strategy_adjustments.extend(exploration.alternative_approaches)

        # Depth recommendation
        if any(c.category == "coverage" for c in critique):
            reflection.depth_recommendation = DepthLevel(
                min(draft.depth_level + 1, DepthLevel.CALL_GRAPH)
            )

        return reflection

    async def _reimplement(
        self,
        draft: SkillDraft,
        critique: list[CritiqueFinding],
        exploration: ExplorationResult,
        reflection: Reflection
    ) -> SkillDraft:
        """Phase 6: Re-implement with improvements."""
        new_draft = SkillDraft(
            question=draft.question,
            code=draft.code,
            concepts_taught=draft.concepts_taught.copy(),
            symbols_used=draft.symbols_used.copy(),
            source_refs=draft.source_refs.copy(),
            depth_level=reflection.depth_recommendation or draft.depth_level,
            grounding_score=draft.grounding_score,
            execution_verified=draft.execution_verified,
            iteration=draft.iteration + 1
        )

        # Apply improvements based on critique
        for finding in critique:
            if finding.category == "clarity" and finding.severity == "minor":
                # Expand question
                new_draft.question = f"How do I use {draft.concepts_taught[0]} in {self.library}? {draft.question}"

            if finding.category == "grounding":
                # Re-expand with deeper analysis
                if draft.source_refs:
                    result = self.depth_controller.expand(
                        draft.source_refs[0],
                        new_draft.depth_level
                    )
                    if result.validated:
                        new_draft.grounding_score = min(1.0, new_draft.grounding_score + 0.2)

        # Add exploration context
        if exploration.additional_context:
            new_draft.code = f"# Context: {exploration.additional_context}\n{new_draft.code}"

        return new_draft

    def _assess_quality(self, draft: SkillDraft) -> float:
        """Assess the quality of a skill draft (0-1)."""
        score = 0.0

        # Grounding (40%)
        score += draft.grounding_score * 0.4

        # Execution (30%)
        if draft.execution_verified:
            score += 0.3

        # Coverage (20%)
        if draft.symbols_used:
            score += min(len(draft.symbols_used) / 3, 1.0) * 0.2

        # Clarity (10%)
        if len(draft.question) >= 20:
            score += 0.1

        return score

    def _generate_question(self, ref: CodeWikiRef, result: DepthResult) -> str:
        """Generate a question from the reference."""
        if result.symbol:
            if result.symbol.kind == "class":
                return f"How do I create and use a {ref.concept} in {self.library}?"
            elif result.symbol.kind == "function":
                return f"How do I call {ref.concept} in {self.library}?"
        return f"How do I use {ref.concept}?"

    def _generate_code(self, ref: CodeWikiRef, result: DepthResult) -> str:
        """Generate code example from the source."""
        code_lines = [f"# Example: Using {ref.concept}"]
        code_lines.append(f"# Source: {ref.file_path}:{ref.line}")
        code_lines.append("")

        # Add relevant imports
        for imp in result.imports[:5]:
            if ref.concept.lower() in imp.lower():
                code_lines.append(imp)

        code_lines.append("")

        # Add usage based on symbol type
        if result.symbol:
            if result.symbol.kind == "class":
                code_lines.append(f"# Create instance of {ref.concept}")
                code_lines.append(f"instance = {ref.concept}()")
            elif result.symbol.kind == "function":
                code_lines.append(f"# Call {ref.concept}")
                code_lines.append(f"result = {ref.concept}()")

        return "\n".join(code_lines)

    def _check_syntax(self, code: str) -> bool:
        """Check if code has valid Python syntax."""
        try:
            compile(code, "<string>", "exec")
            return True
        except SyntaxError:
            return False
