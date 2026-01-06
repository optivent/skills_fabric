"""Pattern Executor - Execute Fabric-style patterns.

Runs patterns with variable substitution and optional
LLM enhancement for complex reasoning steps.

Execution Modes:
- Template: Simple variable substitution
- Enhanced: LLM processes each step
- Hybrid: Template + LLM for specific steps
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum

from .registry import Pattern, PatternRegistry


class ExecutionMode(Enum):
    """Pattern execution modes."""
    TEMPLATE = "template"    # Pure template substitution
    ENHANCED = "enhanced"    # LLM processes steps
    HYBRID = "hybrid"        # Mix of both


@dataclass
class StepResult:
    """Result of executing a pattern step."""
    step_number: int
    step_text: str
    output: Any
    success: bool
    duration_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of pattern execution."""
    pattern_name: str
    mode: ExecutionMode
    success: bool
    output: Any
    step_results: list[StepResult]
    total_duration_ms: float
    variables_used: dict
    error: Optional[str] = None


class PatternExecutor:
    """Execute patterns with configurable modes.

    Usage:
        executor = PatternExecutor()

        # Simple template execution
        result = executor.execute(
            pattern=registry.get("create_skill"),
            variables={"topic": "state management", "library": "langgraph"},
            mode=ExecutionMode.TEMPLATE
        )

        # Enhanced with LLM
        result = executor.execute(
            pattern=registry.get("extract_wisdom"),
            variables={"documentation": doc_text},
            mode=ExecutionMode.ENHANCED,
            llm_callback=my_llm_function
        )
    """

    def __init__(self, registry: PatternRegistry = None):
        self.registry = registry or PatternRegistry()
        self._default_mode = ExecutionMode.TEMPLATE

    def execute(
        self,
        pattern: Pattern | str,
        variables: dict = None,
        mode: ExecutionMode = None,
        llm_callback: Callable[[str], str] = None
    ) -> ExecutionResult:
        """Execute a pattern.

        Args:
            pattern: Pattern object or name string
            variables: Variables to substitute
            mode: Execution mode
            llm_callback: Function(prompt) -> response for enhanced mode

        Returns:
            ExecutionResult with output and step results
        """
        start = datetime.now()
        variables = variables or {}
        mode = mode or self._default_mode

        # Resolve pattern name to Pattern object
        if isinstance(pattern, str):
            pattern = self.registry.get(pattern)
            if not pattern:
                return ExecutionResult(
                    pattern_name=pattern if isinstance(pattern, str) else "unknown",
                    mode=mode,
                    success=False,
                    output=None,
                    step_results=[],
                    total_duration_ms=0,
                    variables_used=variables,
                    error=f"Pattern not found: {pattern}"
                )

        try:
            if mode == ExecutionMode.TEMPLATE:
                return self._execute_template(pattern, variables, start)
            elif mode == ExecutionMode.ENHANCED:
                return self._execute_enhanced(pattern, variables, llm_callback, start)
            else:  # HYBRID
                return self._execute_hybrid(pattern, variables, llm_callback, start)

        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            return ExecutionResult(
                pattern_name=pattern.name,
                mode=mode,
                success=False,
                output=None,
                step_results=[],
                total_duration_ms=duration,
                variables_used=variables,
                error=str(e)
            )

    def _execute_template(
        self,
        pattern: Pattern,
        variables: dict,
        start: datetime
    ) -> ExecutionResult:
        """Execute pattern with pure template substitution."""
        step_results = []

        for i, step in enumerate(pattern.steps):
            step_start = datetime.now()

            # Substitute variables in step
            rendered_step = step
            for key, value in variables.items():
                rendered_step = rendered_step.replace(f"${{{key}}}", str(value))
                rendered_step = rendered_step.replace(f"${key}", str(value))

            step_duration = (datetime.now() - step_start).total_seconds() * 1000
            step_results.append(StepResult(
                step_number=i + 1,
                step_text=rendered_step,
                output=rendered_step,
                success=True,
                duration_ms=step_duration
            ))

        # Generate final output
        output = pattern.render(variables)

        duration = (datetime.now() - start).total_seconds() * 1000
        return ExecutionResult(
            pattern_name=pattern.name,
            mode=ExecutionMode.TEMPLATE,
            success=True,
            output=output,
            step_results=step_results,
            total_duration_ms=duration,
            variables_used=variables
        )

    def _execute_enhanced(
        self,
        pattern: Pattern,
        variables: dict,
        llm_callback: Callable,
        start: datetime
    ) -> ExecutionResult:
        """Execute pattern with LLM processing each step."""
        if not llm_callback:
            return ExecutionResult(
                pattern_name=pattern.name,
                mode=ExecutionMode.ENHANCED,
                success=False,
                output=None,
                step_results=[],
                total_duration_ms=0,
                variables_used=variables,
                error="LLM callback required for enhanced mode"
            )

        step_results = []
        context = {"variables": variables, "outputs": []}

        for i, step in enumerate(pattern.steps):
            step_start = datetime.now()

            # Build prompt for this step
            prompt = self._build_step_prompt(pattern, step, i, context)

            try:
                # Call LLM
                response = llm_callback(prompt)
                context["outputs"].append(response)

                step_duration = (datetime.now() - step_start).total_seconds() * 1000
                step_results.append(StepResult(
                    step_number=i + 1,
                    step_text=step,
                    output=response,
                    success=True,
                    duration_ms=step_duration
                ))

            except Exception as e:
                step_duration = (datetime.now() - step_start).total_seconds() * 1000
                step_results.append(StepResult(
                    step_number=i + 1,
                    step_text=step,
                    output=None,
                    success=False,
                    duration_ms=step_duration,
                    error=str(e)
                ))

        # Check if all steps succeeded
        all_success = all(sr.success for sr in step_results)

        # Combine outputs
        output = "\n\n".join(
            f"Step {sr.step_number}: {sr.output}"
            for sr in step_results if sr.output
        )

        duration = (datetime.now() - start).total_seconds() * 1000
        return ExecutionResult(
            pattern_name=pattern.name,
            mode=ExecutionMode.ENHANCED,
            success=all_success,
            output=output,
            step_results=step_results,
            total_duration_ms=duration,
            variables_used=variables
        )

    def _execute_hybrid(
        self,
        pattern: Pattern,
        variables: dict,
        llm_callback: Callable,
        start: datetime
    ) -> ExecutionResult:
        """Execute with template for simple steps, LLM for complex."""
        step_results = []
        context = {"variables": variables, "outputs": []}

        # Keywords indicating complex reasoning
        complex_keywords = [
            "analyze", "identify", "evaluate", "reason",
            "determine", "assess", "synthesize", "compare"
        ]

        for i, step in enumerate(pattern.steps):
            step_start = datetime.now()
            step_lower = step.lower()

            # Decide if step needs LLM
            needs_llm = llm_callback and any(kw in step_lower for kw in complex_keywords)

            if needs_llm:
                prompt = self._build_step_prompt(pattern, step, i, context)
                try:
                    response = llm_callback(prompt)
                    output = response
                    success = True
                except Exception as e:
                    output = None
                    success = False
            else:
                # Template substitution
                output = step
                for key, value in variables.items():
                    output = output.replace(f"${{{key}}}", str(value))
                success = True

            context["outputs"].append(output)
            step_duration = (datetime.now() - step_start).total_seconds() * 1000

            step_results.append(StepResult(
                step_number=i + 1,
                step_text=step,
                output=output,
                success=success,
                duration_ms=step_duration
            ))

        all_success = all(sr.success for sr in step_results)
        output = pattern.render(variables) if all_success else None

        duration = (datetime.now() - start).total_seconds() * 1000
        return ExecutionResult(
            pattern_name=pattern.name,
            mode=ExecutionMode.HYBRID,
            success=all_success,
            output=output,
            step_results=step_results,
            total_duration_ms=duration,
            variables_used=variables
        )

    def _build_step_prompt(
        self,
        pattern: Pattern,
        step: str,
        step_index: int,
        context: dict
    ) -> str:
        """Build prompt for LLM to process a step."""
        previous_outputs = context.get("outputs", [])
        variables = context.get("variables", {})

        prompt = f"""## PATTERN: {pattern.name}

## IDENTITY
{pattern.identity}

## YOUR TASK
Execute step {step_index + 1}: {step}

## CONTEXT
Variables: {variables}

Previous step outputs:
{chr(10).join(f'Step {i+1}: {out}' for i, out in enumerate(previous_outputs))}

## CONSTRAINTS
{chr(10).join(f'- {c}' for c in pattern.constraints)}

## EXPECTED OUTPUT
Provide the result of executing this step."""

        return prompt


def execute_pattern(
    pattern_name: str,
    variables: dict = None,
    mode: ExecutionMode = ExecutionMode.TEMPLATE
) -> ExecutionResult:
    """Convenience function to execute a pattern by name.

    Usage:
        result = execute_pattern(
            "create_skill",
            variables={"topic": "state management"},
            mode=ExecutionMode.TEMPLATE
        )
    """
    registry = PatternRegistry()
    registry.load_builtin()

    executor = PatternExecutor(registry)
    return executor.execute(pattern_name, variables, mode)
