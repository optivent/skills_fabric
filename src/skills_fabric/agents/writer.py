"""Writer Agent - Skill output generation.

Specializes in:
- Generating skill questions
- Formatting code examples
- Creating structured skill output
- Ensuring schema compliance

Model: Sonnet (structured output generation)
"""
from dataclasses import dataclass, field
from typing import Any, Optional

from .base import BaseAgent, AgentRole, AgentResult
from ..store.kuzu_store import SkillRecord


@dataclass
class WritingTask:
    """Task for the writer agent."""
    concept_name: str
    symbol_name: str
    source_code: str
    file_path: str
    context_docs: str = ""
    library: str = ""


@dataclass
class WritingResult:
    """Result from writing operation."""
    skill: SkillRecord
    question_quality: float  # 0.0 to 1.0
    code_quality: float


class WriterAgent(BaseAgent[WritingResult]):
    """Agent that generates skill output.

    Responsibilities:
    - Generate teaching questions
    - Format code examples
    - Create SkillRecord with all fields
    - Ensure schema compliance

    Output Schema:
    - question: str (teaching question)
    - code: str (executable code example)
    - source_url: str (must point to real file)
    - library: str (library name)
    - verified: bool (set by verifier)
    """

    def __init__(self):
        super().__init__(AgentRole.WRITER)

    def execute(self, task: WritingTask, context: dict = None) -> AgentResult:
        """Execute writing task.

        Args:
            task: WritingTask with content to transform
            context: Shared context

        Returns:
            AgentResult with WritingResult
        """
        start = self._start_execution()

        try:
            # Generate question
            question = self._generate_question(
                task.concept_name,
                task.symbol_name,
                task.source_code,
                task.context_docs
            )

            # Format code
            code = self._format_code(task.source_code, task.symbol_name)

            # Create skill record
            skill = SkillRecord(
                question=question,
                code=code,
                source_url=f"file://{task.file_path}",
                library=task.library,
                verified=False  # Will be set by verifier
            )

            # Assess quality
            question_quality = self._assess_question_quality(question)
            code_quality = self._assess_code_quality(code)

            result = WritingResult(
                skill=skill,
                question_quality=question_quality,
                code_quality=code_quality
            )

            self.send_message(
                AgentRole.SUPERVISOR,
                f"Created skill: {question[:50]}...",
                quality=f"Q:{question_quality:.0%} C:{code_quality:.0%}"
            )

            return self._end_execution(start, output=result)

        except Exception as e:
            return self._end_execution(start, error=str(e))

    def _generate_question(
        self,
        concept: str,
        symbol: str,
        code: str,
        docs: str
    ) -> str:
        """Generate a teaching question.

        Uses template-based generation (HardContent approach)
        rather than pure LLM generation.
        """
        # Template patterns for different symbol types
        templates = {
            'function': [
                f"How do you use the `{symbol}` function in {concept}?",
                f"What does the `{symbol}` function do and how do you call it?",
                f"Show how to implement {concept} using the `{symbol}` function.",
            ],
            'class': [
                f"How do you create and use a `{symbol}` instance?",
                f"What is the purpose of the `{symbol}` class?",
                f"Demonstrate the `{symbol}` class for {concept}.",
            ],
            'method': [
                f"How do you use the `{symbol}` method?",
                f"What parameters does `{symbol}` accept?",
                f"Show an example of calling `{symbol}`.",
            ],
            'default': [
                f"How do you use `{symbol}` for {concept}?",
                f"What is `{symbol}` and how does it work?",
                f"Demonstrate `{symbol}` in practice.",
            ]
        }

        # Detect symbol type from code
        symbol_type = 'default'
        if f'def {symbol}' in code:
            symbol_type = 'function'
        elif f'class {symbol}' in code:
            symbol_type = 'class'
        elif f'.{symbol}(' in code or f'self.{symbol}' in code:
            symbol_type = 'method'

        # Select best template
        import random
        return random.choice(templates[symbol_type])

    def _format_code(self, source_code: str, symbol: str) -> str:
        """Format code for the skill.

        Extracts relevant portion around the symbol.
        """
        lines = source_code.split('\n')
        relevant_lines = []
        in_symbol = False
        indent_level = 0

        for i, line in enumerate(lines):
            # Start of symbol definition
            if f'def {symbol}' in line or f'class {symbol}' in line:
                in_symbol = True
                indent_level = len(line) - len(line.lstrip())
                relevant_lines.append(line)
                continue

            if in_symbol:
                # Check if we've exited the symbol
                if line.strip() and not line.startswith(' ' * (indent_level + 1)):
                    if not line.strip().startswith('#'):
                        # New top-level definition
                        if line.strip().startswith('def ') or line.strip().startswith('class '):
                            break

                relevant_lines.append(line)

                # Limit to reasonable size
                if len(relevant_lines) > 50:
                    relevant_lines.append('    # ... (truncated)')
                    break

        if relevant_lines:
            return '\n'.join(relevant_lines)

        # Fallback: return first 30 lines
        return '\n'.join(lines[:30])

    def _assess_question_quality(self, question: str) -> float:
        """Assess quality of generated question."""
        score = 0.5  # Base score

        # Length check
        if 20 < len(question) < 200:
            score += 0.2

        # Contains code reference
        if '`' in question:
            score += 0.1

        # Is a question
        if question.strip().endswith('?'):
            score += 0.1

        # Contains action word
        action_words = ['how', 'what', 'show', 'demonstrate', 'explain', 'use']
        if any(w in question.lower() for w in action_words):
            score += 0.1

        return min(1.0, score)

    def _assess_code_quality(self, code: str) -> float:
        """Assess quality of code example."""
        score = 0.5  # Base score

        # Not empty
        if len(code.strip()) > 10:
            score += 0.1

        # Has function or class
        if 'def ' in code or 'class ' in code:
            score += 0.2

        # Is parseable Python
        try:
            import ast
            ast.parse(code)
            score += 0.2
        except SyntaxError:
            pass  # Might be TypeScript

        return min(1.0, score)

    def write_skill(
        self,
        concept: str,
        symbol: str,
        code: str,
        file_path: str,
        library: str = ""
    ) -> Optional[SkillRecord]:
        """Convenience method to write a single skill."""
        task = WritingTask(
            concept_name=concept,
            symbol_name=symbol,
            source_code=code,
            file_path=file_path,
            library=library
        )
        result = self.execute(task)
        return result.output.skill if result.success else None
