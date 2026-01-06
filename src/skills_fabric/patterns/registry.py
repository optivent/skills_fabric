"""Pattern Registry - Discover and load Fabric-style patterns.

Inspired by Daniel Miessler's Fabric framework:
- 234+ reusable patterns
- IDENTITY → STEPS → OUTPUT → CONSTRAINTS format
- Structured prompts for consistent results

Pattern Structure:
```markdown
# pattern_name.md

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
"""
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import re


@dataclass
class Pattern:
    """A Fabric-style pattern."""
    name: str
    identity: str
    steps: list[str]
    output_format: str
    constraints: list[str]
    description: str = ""
    tags: list[str] = field(default_factory=list)
    source_file: Optional[Path] = None

    def render(self, variables: dict = None) -> str:
        """Render the pattern with variables substituted."""
        variables = variables or {}

        template = f"""## IDENTITY
{self.identity}

## STEPS
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(self.steps))}

## OUTPUT
{self.output_format}

## CONSTRAINTS
{chr(10).join(f'- {c}' for c in self.constraints)}"""

        # Substitute variables
        for key, value in variables.items():
            template = template.replace(f"${{{key}}}", str(value))
            template = template.replace(f"${key}", str(value))

        return template


class PatternRegistry:
    """Registry for discovering and loading patterns.

    Usage:
        registry = PatternRegistry()

        # Load built-in patterns
        registry.load_builtin()

        # Load custom patterns from directory
        registry.load_from_directory("./my_patterns")

        # Get a pattern
        pattern = registry.get("create_skill")

        # List all patterns
        all_patterns = registry.list_patterns()
    """

    def __init__(self):
        self._patterns: dict[str, Pattern] = {}

    def register(self, pattern: Pattern) -> None:
        """Register a pattern."""
        self._patterns[pattern.name] = pattern

    def get(self, name: str) -> Optional[Pattern]:
        """Get a pattern by name."""
        return self._patterns.get(name)

    def list_patterns(self, tag: str = None) -> list[Pattern]:
        """List all patterns, optionally filtered by tag."""
        patterns = list(self._patterns.values())
        if tag:
            patterns = [p for p in patterns if tag in p.tags]
        return sorted(patterns, key=lambda p: p.name)

    def load_from_file(self, file_path: Path) -> Optional[Pattern]:
        """Load a pattern from a markdown file."""
        try:
            content = file_path.read_text()
            pattern = self._parse_pattern(content, file_path.stem)
            if pattern:
                pattern.source_file = file_path
                self.register(pattern)
            return pattern
        except Exception:
            return None

    def load_from_directory(self, directory: Path) -> int:
        """Load all patterns from a directory."""
        directory = Path(directory)
        if not directory.exists():
            return 0

        loaded = 0
        for md_file in directory.glob("*.md"):
            if self.load_from_file(md_file):
                loaded += 1

        return loaded

    def load_builtin(self) -> int:
        """Load built-in patterns."""
        for pattern in BUILTIN_PATTERNS:
            self.register(pattern)
        return len(BUILTIN_PATTERNS)

    def _parse_pattern(self, content: str, name: str) -> Optional[Pattern]:
        """Parse a pattern from markdown content."""
        # Extract sections
        identity = self._extract_section(content, "IDENTITY")
        steps_text = self._extract_section(content, "STEPS")
        output = self._extract_section(content, "OUTPUT")
        constraints_text = self._extract_section(content, "CONSTRAINTS")

        if not identity:
            return None

        # Parse steps (numbered list)
        steps = []
        for line in steps_text.split('\n'):
            match = re.match(r'^\d+\.\s*(.+)$', line.strip())
            if match:
                steps.append(match.group(1))

        # Parse constraints (bullet list)
        constraints = []
        for line in constraints_text.split('\n'):
            match = re.match(r'^[-*]\s*(.+)$', line.strip())
            if match:
                constraints.append(match.group(1))

        return Pattern(
            name=name,
            identity=identity.strip(),
            steps=steps,
            output_format=output.strip(),
            constraints=constraints
        )

    def _extract_section(self, content: str, section: str) -> str:
        """Extract a section from markdown content."""
        pattern = rf'##\s*{section}\s*\n(.*?)(?=##|$)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""


# =============================================================================
# Built-in Patterns
# =============================================================================

BUILTIN_PATTERNS = [
    Pattern(
        name="create_skill",
        identity="You are a skill generator that creates zero-hallucination Claude skills grounded in source code.",
        steps=[
            "Receive the topic and source code context",
            "Extract the key concept being taught",
            "Generate a clear, actionable question",
            "Write executable code that demonstrates the answer",
            "Verify the source_url points to a real file",
            "Ensure code can execute in a sandbox"
        ],
        output_format="""```json
{
  "question": "How do you...",
  "code": "# Executable example...",
  "source_url": "file:///path/to/real/file.py",
  "verified": true
}
```""",
        constraints=[
            "source_url MUST point to an existing file",
            "code MUST be executable Python",
            "NO hallucinated imports or modules",
            "Trust Level 3 content = REJECTED"
        ],
        description="Generate a Claude skill from source code",
        tags=["skill", "generation", "core"]
    ),

    Pattern(
        name="verify_grounding",
        identity="You are a trust verifier that ensures content is grounded in real source code.",
        steps=[
            "Receive the content to verify",
            "Check if source_url points to existing file",
            "Parse source code with AST",
            "Verify claimed symbols exist",
            "Execute code in sandbox if possible",
            "Assign trust level"
        ],
        output_format="""```json
{
  "trust_level": 1,  // 1=HardContent, 2=VerifiedSoft, 3=Unverified
  "grounding_evidence": ["file_exists", "ast_parsed", "sandbox_passed"],
  "passed": true,
  "rejection_reason": null
}
```""",
        constraints=[
            "Level 1 requires NO LLM involvement",
            "Level 2 requires grounding + sandbox",
            "Level 3 is ALWAYS rejected",
            "Report honestly - gaps are findings"
        ],
        description="Verify content is grounded in source code",
        tags=["verification", "trust", "core"]
    ),

    Pattern(
        name="extract_wisdom",
        identity="You are a wisdom extractor that identifies key insights from documentation.",
        steps=[
            "Read the documentation thoroughly",
            "Identify core concepts being explained",
            "Extract practical insights and patterns",
            "Note any warnings or best practices",
            "Summarize actionable takeaways"
        ],
        output_format="""## KEY INSIGHTS
- Insight 1
- Insight 2

## PATTERNS
- Pattern 1: Description
- Pattern 2: Description

## BEST PRACTICES
- Practice 1
- Practice 2

## WARNINGS
- Warning 1
- Warning 2""",
        constraints=[
            "Focus on actionable insights",
            "Ground all claims in source material",
            "Cite specific sections when possible",
            "Distinguish facts from opinions"
        ],
        description="Extract key insights from documentation",
        tags=["analysis", "documentation"]
    ),

    Pattern(
        name="analyze_code",
        identity="You are a code analyzer that explains how code works.",
        steps=[
            "Parse the code structure (functions, classes)",
            "Identify the main entry points",
            "Trace the execution flow",
            "Note any patterns or idioms used",
            "Identify dependencies and imports"
        ],
        output_format="""## STRUCTURE
- Main components: ...
- Entry points: ...

## FLOW
1. First, ...
2. Then, ...

## PATTERNS
- Pattern: Description

## DEPENDENCIES
- Dependency 1: Purpose
- Dependency 2: Purpose""",
        constraints=[
            "Analyze actual code, not assumptions",
            "Use AST for structure analysis",
            "Note uncertainty explicitly",
            "Don't guess missing context"
        ],
        description="Analyze code structure and flow",
        tags=["analysis", "code"]
    ),

    Pattern(
        name="link_concept",
        identity="You are a concept linker that connects documentation to source code.",
        steps=[
            "Receive the concept from documentation",
            "Search for matching symbols in codebase",
            "Apply matching strategies (exact, filename, content)",
            "Score confidence for each match",
            "Create PROVEN relationship for high-confidence matches"
        ],
        output_format="""```json
{
  "concept": "StateGraph",
  "matches": [
    {"symbol": "StateGraph", "file": "graph.py", "confidence": 0.9, "match_type": "exact"}
  ],
  "proven_link": {"created": true, "confidence": 0.9}
}
```""",
        constraints=[
            "Confidence >= 0.5 required for links",
            "Exact matches get 0.9 confidence",
            "Filename matches get 0.7 confidence",
            "Content matches get 0.5 confidence"
        ],
        description="Link documentation concepts to source code",
        tags=["linking", "proven", "core"]
    ),

    Pattern(
        name="generate_question",
        identity="You are a question generator that creates teaching questions from code.",
        steps=[
            "Analyze the code snippet",
            "Identify what it teaches",
            "Formulate a clear question",
            "Ensure question is actionable",
            "Include code reference in question"
        ],
        output_format="""How do you use the `{symbol}` {type} to {action}?

Example patterns:
- "How do you create a StateGraph with typed state?"
- "What does the `add_node` method do and how do you use it?"
- "Show how to implement checkpointing in LangGraph."
""",
        constraints=[
            "Questions must be answerable from code",
            "Include backtick code references",
            "Start with action word (How, What, Show)",
            "Keep under 100 characters"
        ],
        description="Generate teaching questions from code",
        tags=["generation", "question"]
    ),
]
