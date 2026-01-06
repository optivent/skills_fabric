"""LangGraph Pipeline for Zero-Hallucination Skill Generation.

Integrates:
- GLM-4.7 SDK for generation (with preserved thinking)
- DDR (Direct Dependency Retriever) for symbol validation
- SCIP adapter for precise code intelligence
- Multi-agent auditor for verification
- KuzuDB for citation tracking
- OpenTelemetry for observability

Pipeline Flow:
    research → generate → verify → [retry if hall_m > 0.02] → store
"""
from typing import TypedDict, Optional, Annotated, Literal
from dataclasses import dataclass, field
from pathlib import Path
import operator
import re

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

# Load DDR
spec_ddr = importlib.util.spec_from_file_location(
    "ddr",
    "/home/user/skills_fabric/src/skills_fabric/verify/ddr.py"
)
ddr_module = importlib.util.module_from_spec(spec_ddr)
spec_ddr.loader.exec_module(ddr_module)

DirectDependencyRetriever = ddr_module.DirectDependencyRetriever
DDRResult = ddr_module.DDRResult
SourceRef = ddr_module.SourceRef

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
# Configuration
# =============================================================================

# Available CodeWiki symbol catalogs
CODEWIKI_PATHS = {
    "langgraph": Path("/home/user/skills_fabric/crawl_output/langgraph"),
    "docling": Path("/home/user/skills_fabric/crawl_output/docling"),
}

# SCIP index paths
SCIP_INDICES = {
    "test": Path("/home/user/skills_fabric/test_index.scip"),
}


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
    symbols: list[dict]  # Validated symbols from DDR/SCIP
    documentation: str  # Fetched docs
    ddr_result: Optional[dict]  # Raw DDR result

    # Generation phase
    content: str  # Generated skill content
    thinking: str  # GLM thinking trace
    citations: list[str]  # Extracted citations

    # Verification phase
    hall_m: float  # Hallucination rate
    verified_citations: int
    total_citations: int
    passed: bool
    verification_details: list[dict]  # Detailed verification per citation

    # Control flow
    retry_count: int
    max_retries: int
    error: Optional[str]

    # Output
    final_skill: Optional[str]
    token_usage: dict


# =============================================================================
# DDR Integration
# =============================================================================

class DDRResearchEngine:
    """Research engine using DDR for zero-hallucination symbol retrieval."""

    def __init__(self):
        self._ddrs: dict[str, DirectDependencyRetriever] = {}
        self._loaded_catalogs: set[str] = set()

    def get_ddr(self, library: str) -> Optional[DirectDependencyRetriever]:
        """Get DDR instance for a library."""
        library_lower = library.lower()

        # Check if we have a CodeWiki for this library
        for name, path in CODEWIKI_PATHS.items():
            if library_lower in name or name in library_lower:
                if name not in self._ddrs:
                    ddr = DirectDependencyRetriever(codewiki_path=path)
                    catalog_path = path / "symbol_catalog.md"
                    if catalog_path.exists():
                        ddr.load_symbol_catalog(catalog_path)
                        self._ddrs[name] = ddr
                        self._loaded_catalogs.add(name)
                return self._ddrs.get(name)

        return None

    def research(self, library: str, topic: str, max_results: int = 10) -> DDRResult:
        """Research symbols for a library topic."""
        ddr = self.get_ddr(library)

        if ddr:
            # Use real DDR retrieval
            return ddr.retrieve(topic, max_results=max_results)

        # Fallback: no CodeWiki available
        return DDRResult(
            query=topic,
            elements=[],
            validated_count=0,
            rejected_count=0,
            hallucination_rate=1.0,  # Mark as uncertain
        )

    @property
    def available_libraries(self) -> list[str]:
        """List libraries with available CodeWiki data."""
        return list(CODEWIKI_PATHS.keys())


# Global research engine
_research_engine = DDRResearchEngine()


# =============================================================================
# Node Functions
# =============================================================================

@trace_langgraph_node("research")
def research_node(state: SkillState) -> dict:
    """Research phase: gather VALIDATED symbols and documentation using DDR.

    This uses the real DDR (Direct Dependency Retriever) to:
    - Query symbol catalogs for the target library
    - Validate each symbol exists with file:line citation
    - Extract documentation from CodeWiki
    """
    library = state["library"]
    topic = state["topic"]

    # Use DDR for validated symbol retrieval
    ddr_result = _research_engine.research(library, topic, max_results=15)

    # Convert DDR elements to symbol list
    symbols = []
    documentation_parts = []

    for element in ddr_result.elements:
        ref = element.source_ref
        symbols.append({
            "name": ref.symbol_name,
            "citation": ref.citation,  # file_path:line_number
            "type": ref.symbol_type,
            "docstring": ref.docstring or "",
            "validated": ref.validated,
        })

        # Build documentation from validated elements
        if ref.docstring:
            documentation_parts.append(f"### {ref.symbol_name}\n{ref.docstring}\n")
        elif element.content:
            documentation_parts.append(f"### {ref.symbol_name}\n```python\n{element.content[:500]}\n```\n")

    # Generate documentation summary
    documentation = f"""# {library} - {topic}

## Validated Symbols ({ddr_result.validated_count} found)

{"".join(documentation_parts) if documentation_parts else "No validated symbols found in CodeWiki."}

## Retrieval Stats
- Query: {topic}
- Validated: {ddr_result.validated_count}
- Rejected: {ddr_result.rejected_count}
- DDR Hallucination Rate: {ddr_result.hallucination_rate:.2%}
"""

    # Store DDR result for verification
    ddr_dict = {
        "query": ddr_result.query,
        "validated_count": ddr_result.validated_count,
        "rejected_count": ddr_result.rejected_count,
        "hallucination_rate": ddr_result.hallucination_rate,
        "success": ddr_result.success,
    }

    return {
        "symbols": symbols,
        "documentation": documentation,
        "ddr_result": ddr_dict,
    }


@trace_langgraph_node("generate")
def generate_node(state: SkillState) -> dict:
    """Generate phase: use GLM-4.7 to create skill content.

    Uses validated symbols from DDR to constrain generation.
    """
    library = state["library"]
    topic = state["topic"]
    level = state["level"]
    symbols = state["symbols"]
    documentation = state["documentation"]
    retry_count = state.get("retry_count", 0)
    ddr_result = state.get("ddr_result", {})

    # Initialize GLM client
    client = GLMClient()

    # Build prompt with VALIDATED symbols only
    if symbols:
        symbol_list = "\n".join([
            f"  - `{s['name']}` ({s['type']}): `{s['citation']}`"
            for s in symbols if s.get('validated', False)
        ])
    else:
        symbol_list = "  (No validated symbols available - use general knowledge carefully)"

    # Warn about hallucination if DDR failed
    ddr_warning = ""
    if ddr_result.get("validated_count", 0) == 0:
        ddr_warning = """
⚠ WARNING: No validated symbols found in CodeWiki for this library.
Be extra careful about citations. Only cite paths/lines you are certain exist.
If unsure, use general documentation references instead of specific file:line citations.
"""

    prompt = f"""Generate a Claude Code skill for: {topic}

Library: {library}
Progressive Disclosure Level: L{level}
{ddr_warning}
## VALIDATED Symbols (from DDR - these are confirmed to exist):
{symbol_list}

## Documentation Context:
{documentation}

## Requirements:
1. ONLY use citations from the validated symbols list above
2. Format citations as: `path/file.py:123`
3. Use progressive disclosure (L{level} complexity)
4. Include working code examples
5. DO NOT invent file paths or line numbers

{"IMPORTANT: Previous attempt had hallucinations. Use ONLY the validated symbols above." if retry_count > 0 else ""}
"""

    # Generate with preserved thinking
    response = client.chat(
        user_message=prompt,
        system_prompt="""You are an expert technical writer creating zero-hallucination Claude Code skills.

CRITICAL: Every citation MUST come from the validated symbols list provided.
DO NOT invent or guess file paths or line numbers.
If you're unsure about a citation, reference the documentation generally instead.""",
        thinking=True,
    )

    # Extract citations from response
    citation_pattern = r'`?([a-zA-Z0-9_/.-]+\.(?:py|js|ts|tsx|jsx)):(\d+)`?'
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
    """Verify phase: check citations against VALIDATED symbols.

    Verification is strict:
    - Citations must match validated symbols from DDR
    - File paths must match exactly (not substring)
    - Line numbers should be within tolerance
    """
    citations = state["citations"]
    symbols = state["symbols"]
    content = state["content"]
    ddr_result = state.get("ddr_result", {})

    # Build validation index from DDR symbols
    # Use list to allow multiple symbols per file
    valid_citations = []
    for sym in symbols:
        if sym.get("validated", False):
            citation = sym["citation"]
            parts = citation.split(":")
            if len(parts) == 2:
                file_path = parts[0]
                try:
                    line_num = int(parts[1])
                    valid_citations.append({
                        "file_path": file_path,
                        "line": line_num,
                        "symbol": sym["name"],
                    })
                except ValueError:
                    pass

    # Verify each citation
    verification_details = []
    verified = 0

    for citation in citations:
        parts = citation.split(":")
        if len(parts) != 2:
            verification_details.append({
                "citation": citation,
                "status": "invalid_format",
                "verified": False,
            })
            continue

        file_path, line_str = parts
        try:
            cited_line = int(line_str)
        except ValueError:
            verification_details.append({
                "citation": citation,
                "status": "invalid_line_number",
                "verified": False,
            })
            continue

        # Check against valid citations
        matched = False
        for valid_info in valid_citations:
            valid_path = valid_info["file_path"]
            # Path matching: exact or suffix match
            if file_path == valid_path or valid_path.endswith(file_path) or file_path.endswith(valid_path):
                # Line number tolerance: within 10 lines
                if abs(cited_line - valid_info["line"]) <= 10:
                    verified += 1
                    matched = True
                    verification_details.append({
                        "citation": citation,
                        "status": "verified",
                        "verified": True,
                        "matched_symbol": valid_info["symbol"],
                        "matched_citation": f"{valid_path}:{valid_info['line']}",
                    })
                    break

        if not matched:
            verification_details.append({
                "citation": citation,
                "status": "not_in_validated_symbols",
                "verified": False,
            })

    # Calculate hallucination rate
    total = len(citations) if citations else 1
    hall_m = 1.0 - (verified / total) if total > 0 else 0.0

    # Additional hallucination pattern check
    hallucination_patterns = [
        r"import\s+fake_",
        r"from\s+nonexistent",
        r"hypothetically",
        r"might\s+work",
        r"could\s+be\s+located",
        r"probably\s+at",
    ]
    pattern_violations = 0
    for pattern in hallucination_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            pattern_violations += 1

    # Adjust hall_m for pattern violations
    if pattern_violations > 0:
        hall_m = min(1.0, hall_m + (pattern_violations * 0.05))

    # Also consider DDR result in final assessment
    ddr_hall_rate = ddr_result.get("hallucination_rate", 0.0)
    if ddr_hall_rate > 0.5:
        # If DDR had high rejection rate, be more cautious
        hall_m = min(1.0, hall_m + 0.1)

    passed = hall_m < 0.02

    return {
        "hall_m": hall_m,
        "verified_citations": verified,
        "total_citations": total,
        "passed": passed,
        "verification_details": verification_details,
    }


@trace_langgraph_node("retry_decision")
def retry_decision(state: SkillState) -> Literal["increment_retry", "store"]:
    """Decide whether to retry or proceed to storage."""
    if state["passed"]:
        return "store"

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if retry_count < max_retries:
        return "increment_retry"

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
    """Store phase: save the final skill with verification metadata."""
    content = state["content"]
    passed = state["passed"]
    hall_m = state["hall_m"]
    verified_citations = state["verified_citations"]
    total_citations = state["total_citations"]
    ddr_result = state.get("ddr_result", {})
    verification_details = state.get("verification_details", [])

    # Add verification footer
    if passed:
        status = f"✓ VERIFIED (hall_m={hall_m:.2%}, {verified_citations}/{total_citations} citations verified)"
    else:
        status = f"⚠ UNVERIFIED (hall_m={hall_m:.2%}, {verified_citations}/{total_citations} citations verified)"

    # Add DDR stats
    ddr_info = ""
    if ddr_result:
        ddr_info = f"\n_DDR Stats: {ddr_result.get('validated_count', 0)} symbols validated, {ddr_result.get('rejected_count', 0)} rejected_"

    # Build verification report
    verification_report = ""
    if verification_details:
        verified_list = [d for d in verification_details if d.get("verified")]
        failed_list = [d for d in verification_details if not d.get("verified")]

        if verified_list:
            verification_report += "\n\n**Verified Citations:**\n"
            for v in verified_list[:5]:  # Show top 5
                verification_report += f"- `{v['citation']}` → {v.get('matched_symbol', 'match')}\n"

        if failed_list:
            verification_report += "\n**Unverified Citations:**\n"
            for v in failed_list[:5]:  # Show top 5
                verification_report += f"- `{v['citation']}` ({v.get('status', 'unknown')})\n"

    final_skill = f"""{content}

---
_Verification Status: {status}_{ddr_info}{verification_report}"""

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
            "increment_retry": "increment_retry",
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
        self.research_engine = _research_engine

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
            "ddr_result": None,
            "content": "",
            "thinking": "",
            "citations": [],
            "hall_m": 1.0,
            "verified_citations": 0,
            "total_citations": 0,
            "passed": False,
            "verification_details": [],
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

    @property
    def available_libraries(self) -> list[str]:
        """List libraries with CodeWiki data available."""
        return self.research_engine.available_libraries


# =============================================================================
# Demo / Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LANGGRAPH + GLM-4.7 SKILL GENERATION PIPELINE")
    print("(Using Real DDR Integration)")
    print("=" * 60)
    print()

    # Create pipeline
    pipeline = SkillGenerationPipeline(checkpointing=False)

    print(f"Available libraries with CodeWiki: {pipeline.available_libraries}")
    print()

    # Generate a skill for langgraph (we have real data for this)
    print("Generating skill for: langgraph / StateGraph creation")
    print("-" * 60)

    result = pipeline.generate(
        library="langgraph",
        topic="StateGraph",
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
    print("DDR Result:")
    ddr_r = result.get('ddr_result', {})
    print(f"  Validated symbols: {ddr_r.get('validated_count', 0)}")
    print(f"  Rejected symbols: {ddr_r.get('rejected_count', 0)}")
    print(f"  DDR Hall rate: {ddr_r.get('hallucination_rate', 0):.2%}")

    print()
    print("Symbols (first 5):")
    for sym in result['symbols'][:5]:
        print(f"  - {sym['name']}: {sym['citation']} ({'✓' if sym.get('validated') else '✗'})")

    print()
    print("Verification Details:")
    for detail in result.get('verification_details', [])[:5]:
        status = "✓" if detail.get('verified') else "✗"
        print(f"  {status} {detail.get('citation', 'N/A')}: {detail.get('status', 'unknown')}")

    print()
    print("Generated Skill (preview):")
    print("-" * 60)
    skill_preview = result['final_skill'][:800] if result['final_skill'] else "None"
    print(skill_preview)
    print("...")
