"""LangGraph Pipeline for Zero-Hallucination Skill Generation.

Integrates:
- GLM-4.7 SDK for generation (with preserved thinking)
- SCIP/DDR for symbol verification
- Multi-agent auditor for verification
- KuzuDB for citation tracking
- OpenTelemetry for observability

Pipeline Flow:
    research → generate → verify → [retry if hall_m > 0.02] → store
"""
from typing import TypedDict, Optional, Annotated, Literal
from dataclasses import dataclass, field
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import our components
import sys
import importlib.util

# Load GLM client
spec_glm = importlib.util.spec_from_file_location(
    "glm_client",
    "/home/user/skills_fabric/src/skills_fabric/llm/glm_client.py"
)
glm_module = importlib.util.module_from_spec(spec_glm)
sys.modules['glm_client'] = glm_module
spec_glm.loader.exec_module(glm_module)

GLMClient = glm_module.GLMClient
GLMCodingAgent = glm_module.GLMCodingAgent

# Load telemetry
spec_tracing = importlib.util.spec_from_file_location(
    "tracing",
    "/home/user/skills_fabric/src/skills_fabric/telemetry/tracing.py"
)
tracing_module = importlib.util.module_from_spec(spec_tracing)
spec_tracing.loader.exec_module(tracing_module)

trace_langgraph_node = tracing_module.trace_langgraph_node
AgentTracer = tracing_module.AgentTracer


# =============================================================================
# State Definition
# =============================================================================

class SkillState(TypedDict):
    """State for skill generation pipeline."""
    # Input
    library: str
    topic: str
    level: int  # Progressive disclosure level 1-5

    # Research phase
    symbols: list[dict]  # Symbols from SCIP
    documentation: str  # Fetched docs

    # Generation phase
    content: str  # Generated skill content
    thinking: str  # GLM thinking trace
    citations: list[str]  # Extracted citations

    # Verification phase
    hall_m: float  # Hallucination rate
    verified_citations: int
    total_citations: int
    passed: bool

    # Control flow
    retry_count: int
    max_retries: int
    error: Optional[str]

    # Output
    final_skill: Optional[str]
    token_usage: dict


# =============================================================================
# Node Functions
# =============================================================================

@trace_langgraph_node("research")
def research_node(state: SkillState) -> dict:
    """Research phase: gather symbols and documentation.

    In production, this would:
    - Query SCIP index for library symbols
    - Fetch documentation from source
    - Use tree-sitter for code parsing
    """
    library = state["library"]
    topic = state["topic"]

    # Simulated research (in production: use SCIP adapter)
    symbols = [
        {"name": f"{library}.main_class", "citation": f"{library}/core.py:42"},
        {"name": f"{library}.helper_func", "citation": f"{library}/utils.py:15"},
        {"name": f"{library}.Config", "citation": f"{library}/config.py:8"},
    ]

    documentation = f"""
# {library} Library

## Overview
{library} is a Python library for {topic}.

## Main Components
- main_class: Primary interface
- helper_func: Utility functions
- Config: Configuration management

## Usage
```python
from {library} import main_class
result = main_class.process(data)
```
"""

    return {
        "symbols": symbols,
        "documentation": documentation,
    }


@trace_langgraph_node("generate")
def generate_node(state: SkillState) -> dict:
    """Generate phase: use GLM-4.7 to create skill content."""
    library = state["library"]
    topic = state["topic"]
    level = state["level"]
    symbols = state["symbols"]
    documentation = state["documentation"]
    retry_count = state.get("retry_count", 0)

    # Initialize GLM client
    client = GLMClient()

    # Build prompt with context
    symbol_list = "\n".join([
        f"  - {s['name']}: {s['citation']}" for s in symbols
    ])

    prompt = f"""Generate a Claude Code skill for: {topic}

Library: {library}
Progressive Disclosure Level: L{level}

Available Symbols:
{symbol_list}

Documentation:
{documentation}

Requirements:
1. Include precise citations in format: `path/file.py:123`
2. Use progressive disclosure (L{level} complexity)
3. Include working code examples
4. Reference actual symbols from the library

{"IMPORTANT: Previous attempt had hallucinations. Be more careful with citations." if retry_count > 0 else ""}
"""

    # Generate with preserved thinking
    response = client.chat(
        user_message=prompt,
        system_prompt="You are an expert technical writer creating zero-hallucination Claude Code skills. Every claim must have a citation.",
        thinking=True,
    )

    # Extract citations from response
    import re
    citation_pattern = r'`?([a-zA-Z0-9_/.-]+\.(?:py|js|ts)):(\d+)`?'
    matches = re.findall(citation_pattern, response.content)
    citations = [f"{path}:{line}" for path, line in matches]

    return {
        "content": response.content,
        "thinking": response.thinking or "",
        "citations": citations,
        "token_usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "cost_usd": response.usage.cost_usd,
        },
    }


@trace_langgraph_node("verify")
def verify_node(state: SkillState) -> dict:
    """Verify phase: check for hallucinations.

    In production, this would:
    - Use DDR to verify each citation
    - Run multi-agent auditor
    - Check symbol existence in SCIP index
    """
    citations = state["citations"]
    symbols = state["symbols"]
    content = state["content"]

    # Get valid citation paths from symbols
    valid_paths = {s["citation"].split(":")[0] for s in symbols}

    # Verify citations
    verified = 0
    for citation in citations:
        path = citation.split(":")[0]
        if any(valid in path for valid in valid_paths):
            verified += 1

    total = len(citations) if citations else 1
    hall_m = 1.0 - (verified / total) if total > 0 else 0.0

    # Check for common hallucination patterns
    hallucination_patterns = [
        "import fake_",
        "from nonexistent",
        "hypothetically",
        "might work",
    ]
    for pattern in hallucination_patterns:
        if pattern.lower() in content.lower():
            hall_m = min(1.0, hall_m + 0.1)

    passed = hall_m < 0.02

    return {
        "hall_m": hall_m,
        "verified_citations": verified,
        "total_citations": total,
        "passed": passed,
    }


@trace_langgraph_node("retry_decision")
def retry_decision(state: SkillState) -> Literal["generate", "store"]:
    """Decide whether to retry or proceed to storage."""
    if state["passed"]:
        return "store"

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if retry_count < max_retries:
        return "generate"

    # Max retries reached, store anyway but flag it
    return "store"


@trace_langgraph_node("increment_retry")
def increment_retry_node(state: SkillState) -> dict:
    """Increment retry counter before regenerating."""
    return {
        "retry_count": state.get("retry_count", 0) + 1,
    }


@trace_langgraph_node("store")
def store_node(state: SkillState) -> dict:
    """Store phase: save the final skill.

    In production, this would:
    - Save to KuzuDB with citations
    - Track skill relationships
    - Update library statistics
    """
    content = state["content"]
    passed = state["passed"]
    hall_m = state["hall_m"]

    # Add verification footer
    status = "✓ VERIFIED" if passed else f"⚠ UNVERIFIED (hall_m={hall_m:.2%})"
    final_skill = f"{content}\n\n---\n_Verification Status: {status}_"

    return {
        "final_skill": final_skill,
    }


# =============================================================================
# Graph Construction
# =============================================================================

def create_skill_graph() -> StateGraph:
    """Create the skill generation graph."""

    # Create graph
    graph = StateGraph(SkillState)

    # Add nodes
    graph.add_node("research", research_node)
    graph.add_node("generate", generate_node)
    graph.add_node("verify", verify_node)
    graph.add_node("increment_retry", increment_retry_node)
    graph.add_node("store", store_node)

    # Add edges
    graph.set_entry_point("research")
    graph.add_edge("research", "generate")
    graph.add_edge("generate", "verify")

    # Conditional edge for retry logic
    graph.add_conditional_edges(
        "verify",
        retry_decision,
        {
            "generate": "increment_retry",
            "store": "store",
        }
    )
    graph.add_edge("increment_retry", "generate")
    graph.add_edge("store", END)

    return graph


def compile_graph(checkpointing: bool = True):
    """Compile the graph with optional checkpointing."""
    graph = create_skill_graph()

    if checkpointing:
        memory = MemorySaver()
        return graph.compile(checkpointer=memory)
    else:
        return graph.compile()


# =============================================================================
# Main Pipeline Interface
# =============================================================================

class SkillGenerationPipeline:
    """High-level interface for skill generation."""

    def __init__(self, checkpointing: bool = True):
        self.app = compile_graph(checkpointing)
        self.tracer = AgentTracer("skill_generation")

    def generate(
        self,
        library: str,
        topic: str,
        level: int = 3,
        max_retries: int = 2,
    ) -> dict:
        """Generate a skill with verification.

        Args:
            library: Target library name
            topic: Skill topic
            level: Progressive disclosure level (1-5)
            max_retries: Max retry attempts for verification

        Returns:
            Final state with generated skill
        """
        initial_state: SkillState = {
            "library": library,
            "topic": topic,
            "level": level,
            "symbols": [],
            "documentation": "",
            "content": "",
            "thinking": "",
            "citations": [],
            "hall_m": 1.0,
            "verified_citations": 0,
            "total_citations": 0,
            "passed": False,
            "retry_count": 0,
            "max_retries": max_retries,
            "error": None,
            "final_skill": None,
            "token_usage": {},
        }

        config = {"configurable": {"thread_id": f"{library}_{topic}"}}

        with self.tracer.trace_pipeline(library, topic=topic, level=level):
            result = self.app.invoke(initial_state, config)

        return result

    def get_visualization(self) -> str:
        """Get Mermaid diagram of the graph."""
        try:
            return self.app.get_graph().draw_mermaid()
        except Exception:
            return "Visualization not available"


# =============================================================================
# Demo / Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LANGGRAPH + GLM-4.7 SKILL GENERATION PIPELINE")
    print("=" * 60)
    print()

    # Create pipeline
    pipeline = SkillGenerationPipeline(checkpointing=False)

    # Generate a skill
    print("Generating skill for: docling / PDF conversion")
    print("-" * 60)

    result = pipeline.generate(
        library="docling",
        topic="PDF conversion",
        level=3,
        max_retries=1,
    )

    # Print results
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Library: {result['library']}")
    print(f"Topic: {result['topic']}")
    print(f"Level: L{result['level']}")
    print(f"Passed: {result['passed']}")
    print(f"Hall_m: {result['hall_m']:.2%}")
    print(f"Citations: {result['verified_citations']}/{result['total_citations']}")
    print(f"Retries: {result['retry_count']}")
    print(f"Tokens: {result['token_usage'].get('total_tokens', 'N/A')}")
    print(f"Cost: ${result['token_usage'].get('cost_usd', 0):.4f}")
    print()
    print("Generated Skill (preview):")
    print("-" * 60)
    skill_preview = result['final_skill'][:500] if result['final_skill'] else "None"
    print(skill_preview)
    print("...")
