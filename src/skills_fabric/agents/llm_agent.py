"""LLM-backed Agent - Uses GLM-4.7 for generation tasks.

Integrates GLM-4.7's preserved thinking with the agent framework
for multi-turn coding tasks with zero-hallucination verification.

Key Features:
- Preserved thinking across turns
- Automatic citation extraction
- Integration with DDR verification
- Token usage tracking
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
import re

# Handle both package and standalone imports
try:
    from .base import BaseAgent, AgentRole, AgentResult, AgentStatus
except ImportError:
    # Standalone execution - create minimal stubs
    from enum import Enum

    class AgentRole(Enum):
        WRITER = "writer"

    class AgentStatus(Enum):
        IDLE = "idle"
        RUNNING = "running"
        SUCCESS = "success"
        FAILED = "failed"

    @dataclass
    class AgentResult:
        agent: AgentRole
        status: AgentStatus
        output: Any = None
        error: Optional[str] = None
        duration_ms: float = 0.0
        messages: list = field(default_factory=list)

        @property
        def success(self) -> bool:
            return self.status == AgentStatus.SUCCESS

    class BaseAgent:
        def __init__(self, role: AgentRole):
            self.role = role
            self.status = AgentStatus.IDLE

        def _start_execution(self):
            self.status = AgentStatus.RUNNING
            return datetime.now()

        def _end_execution(self, start_time, output=None, error=None):
            duration = (datetime.now() - start_time).total_seconds() * 1000
            if error:
                self.status = AgentStatus.FAILED
                return AgentResult(self.role, AgentStatus.FAILED, error=error, duration_ms=duration)
            self.status = AgentStatus.SUCCESS
            return AgentResult(self.role, AgentStatus.SUCCESS, output=output, duration_ms=duration)

# Import GLM client
try:
    from ..llm.glm_client import GLMClient, GLMCodingAgent, GLMResponse
    GLM_AVAILABLE = True
except ImportError:
    try:
        # Try absolute import for standalone
        from skills_fabric.llm.glm_client import GLMClient, GLMCodingAgent, GLMResponse
        GLM_AVAILABLE = True
    except ImportError:
        GLM_AVAILABLE = False
        GLMClient = None
        GLMCodingAgent = None
        GLMResponse = None


@dataclass
class GenerationTask:
    """Task for LLM generation."""
    prompt: str
    library: str
    context: Optional[str] = None
    level: int = 1  # Progressive disclosure level
    require_citations: bool = True


@dataclass
class GenerationOutput:
    """Output from LLM generation."""
    content: str
    thinking: Optional[str] = None
    citations: list[str] = field(default_factory=list)
    tokens_used: int = 0
    cost_usd: float = 0.0
    has_code_blocks: bool = False


class LLMGeneratorAgent(BaseAgent):
    """Agent that uses GLM-4.7 for skill generation.

    Uses preserved thinking mode to maintain reasoning
    across multiple generation attempts.
    """

    SYSTEM_PROMPT = """You are an expert technical writer creating Claude Code skills.

When generating skills:
1. Include precise citations in format: `path/file.py:123`
2. Use progressive disclosure (L1: basic → L5: advanced)
3. Verify all code examples are syntactically correct
4. Include type hints and docstrings
5. Reference actual symbols from the library

For each code example:
- Show the import statement
- Demonstrate basic usage first
- Add error handling for production use
- Include expected output in comments

CRITICAL: Every claim must have a citation. No hallucinated APIs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        preserve_thinking: bool = True,
    ):
        """Initialize LLM generator agent.

        Args:
            api_key: GLM API key (or use env var)
            preserve_thinking: Keep thinking across turns
        """
        super().__init__(AgentRole.WRITER)

        self.preserve_thinking = preserve_thinking
        self._client: Optional[GLMClient] = None
        self._agent: Optional[GLMCodingAgent] = None

        if GLM_AVAILABLE and api_key:
            self._client = GLMClient(api_key=api_key)
            self._agent = GLMCodingAgent(
                client=self._client,
                system_prompt=self.SYSTEM_PROMPT,
            )
        elif GLM_AVAILABLE:
            try:
                self._client = GLMClient()
                self._agent = GLMCodingAgent(
                    client=self._client,
                    system_prompt=self.SYSTEM_PROMPT,
                )
            except ValueError:
                pass  # No API key available

    @property
    def available(self) -> bool:
        """Check if GLM is available."""
        return self._agent is not None

    def execute(self, task: Any, context: dict = None) -> AgentResult:
        """Execute generation task.

        Args:
            task: GenerationTask or string prompt
            context: Additional context (symbols, docs, etc.)

        Returns:
            AgentResult with GenerationOutput
        """
        start_time = self._start_execution()

        if not self.available:
            return self._end_execution(
                start_time,
                error="GLM-4.7 not available (no API key)"
            )

        # Normalize task
        if isinstance(task, str):
            task = GenerationTask(prompt=task, library="unknown")

        try:
            output = self._generate(task, context or {})
            return self._end_execution(start_time, output=output)
        except Exception as e:
            return self._end_execution(start_time, error=str(e))

    def _generate(
        self,
        task: GenerationTask,
        context: dict,
    ) -> GenerationOutput:
        """Generate content using GLM-4.7.

        Args:
            task: Generation task
            context: Additional context

        Returns:
            GenerationOutput
        """
        # Build prompt with context
        prompt = self._build_prompt(task, context)

        # Generate with preserved thinking
        response = self._agent.send(
            message=prompt,
            preserve_thinking=self.preserve_thinking,
        )

        # Extract citations from response
        citations = self._extract_citations(response.content)

        # Check for code blocks
        has_code = bool(re.search(r'```\w*\n', response.content))

        return GenerationOutput(
            content=response.content,
            thinking=response.thinking,
            citations=citations,
            tokens_used=response.usage.total_tokens,
            cost_usd=response.usage.cost_usd,
            has_code_blocks=has_code,
        )

    def _build_prompt(
        self,
        task: GenerationTask,
        context: dict,
    ) -> str:
        """Build generation prompt.

        Args:
            task: Generation task
            context: Additional context

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add library context
        parts.append(f"Library: {task.library}")
        parts.append(f"Progressive Disclosure Level: L{task.level}")
        parts.append("")

        # Add symbols if available
        if "symbols" in context:
            parts.append("Available Symbols:")
            for sym in context["symbols"][:20]:  # Limit to top 20
                if isinstance(sym, dict):
                    parts.append(f"  - {sym.get('name')}: {sym.get('citation', '')}")
                else:
                    parts.append(f"  - {sym}")
            parts.append("")

        # Add documentation excerpts if available
        if "docs" in context:
            parts.append("Documentation:")
            parts.append(context["docs"][:2000])  # Limit length
            parts.append("")

        # Add the main prompt
        parts.append("Task:")
        parts.append(task.prompt)

        # Add context code if provided
        if task.context:
            parts.append("")
            parts.append("Context Code:")
            parts.append(f"```python\n{task.context}\n```")

        # Add citation requirement
        if task.require_citations:
            parts.append("")
            parts.append("IMPORTANT: Include citations for all code references in format: `file.py:123`")

        return "\n".join(parts)

    def _extract_citations(self, content: str) -> list[str]:
        """Extract citations from generated content.

        Args:
            content: Generated content

        Returns:
            List of citation strings
        """
        # Pattern: path/file.py:123 or file.py:123
        pattern = r'`?([a-zA-Z0-9_/.-]+\.(?:py|js|ts|rs|go|r|rb|java)):(\d+)`?'
        matches = re.findall(pattern, content)
        return [f"{path}:{line}" for path, line in matches]

    def generate_skill(
        self,
        library: str,
        topic: str,
        level: int = 3,
        symbols: list[dict] = None,
    ) -> GenerationOutput:
        """Convenience method to generate a skill.

        Args:
            library: Target library
            topic: Skill topic
            level: Progressive disclosure level (1-5)
            symbols: Available symbols from SCIP

        Returns:
            GenerationOutput
        """
        task = GenerationTask(
            prompt=f"Generate a skill for {topic} using the {library} library.",
            library=library,
            level=level,
            require_citations=True,
        )

        context = {}
        if symbols:
            context["symbols"] = symbols

        result = self.execute(task, context)

        if result.success:
            return result.output
        else:
            raise RuntimeError(result.error)

    def refine(
        self,
        feedback: str,
        preserve_context: bool = True,
    ) -> GenerationOutput:
        """Refine the previous generation based on feedback.

        Args:
            feedback: Feedback or correction
            preserve_context: Keep conversation history

        Returns:
            Updated GenerationOutput
        """
        if not preserve_context:
            self._agent.reset()

        prompt = f"""Based on the following feedback, improve the previous generation:

Feedback: {feedback}

Please address the issues and provide an updated version."""

        response = self._agent.send(
            message=prompt,
            preserve_thinking=True,  # Always preserve for refinement
        )

        citations = self._extract_citations(response.content)
        has_code = bool(re.search(r'```\w*\n', response.content))

        return GenerationOutput(
            content=response.content,
            thinking=response.thinking,
            citations=citations,
            tokens_used=response.usage.total_tokens,
            cost_usd=response.usage.cost_usd,
            has_code_blocks=has_code,
        )

    def reset_conversation(self):
        """Reset the conversation history."""
        if self._agent:
            self._agent.reset()

    def get_thinking_history(self) -> list[str]:
        """Get all thinking blocks from the conversation."""
        if self._agent:
            return self._agent.thinking_history
        return []

    def get_token_usage(self) -> dict:
        """Get total token usage."""
        if self._client:
            usage = self._client.get_total_usage()
            return {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "thinking_tokens": usage.thinking_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": usage.cost_usd,
            }
        return {}
