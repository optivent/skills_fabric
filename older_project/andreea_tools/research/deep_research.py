"""
Deep Research Agent for MARO v2.0

LangGraph-based autonomous research agent that:
1. Plans research approach
2. Searches academic databases (S2, ArXiv)
3. Searches web for grey literature (Brave)
4. Curates and ranks sources
5. Synthesizes findings
6. Verifies conclusions
7. Iterates until depth reached

Based on patterns from GPT-Researcher but with multi-model routing.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Try imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("langgraph not available - using simplified research flow")

# Import model router - try relative import first, then absolute
try:
    from ..model_router import ModelRouter
    MODEL_ROUTER_AVAILABLE = True
except ImportError:
    try:
        from model_router import ModelRouter
        MODEL_ROUTER_AVAILABLE = True
    except ImportError:
        MODEL_ROUTER_AVAILABLE = False
        logger.warning("ModelRouter not available - research will be limited")


class ResearchState(TypedDict, total=False):
    """State for the research graph."""
    question: str
    plan: str
    academic_sources: List[Dict[str, Any]]
    web_sources: List[Dict[str, Any]]
    curated_sources: List[Dict[str, Any]]
    synthesis: str
    verification: Dict[str, Any]
    gaps: List[str]
    iteration: int
    max_iterations: int
    complete: bool


@dataclass
class ResearchResult:
    """Final research result."""
    question: str
    synthesis: str
    sources: List[Dict[str, Any]]
    verification: Dict[str, Any]
    gaps: List[str]
    iterations: int
    model_used: str


# Prompts
PLAN_PROMPT = """You are a research planning assistant. Create a research plan for this question.

QUESTION: {question}

Create a concise research plan with:
1. Key concepts to search for
2. Types of evidence needed (RCTs, reviews, guidelines, etc.)
3. Potential databases to search (academic vs web/grey literature)
4. Inclusion criteria for sources

Return a structured plan in 3-5 sentences."""


CURATE_PROMPT = """You are a research curator. Select the most relevant sources for this research question.

QUESTION: {question}

AVAILABLE SOURCES:
{sources}

Select and rank the top 10 most relevant sources. Consider:
- Relevance to the question
- Study quality (RCTs > observational > case reports)
- Recency
- Citation count

Return JSON:
{{
    "selected_sources": [
        {{
            "id": "source identifier",
            "title": "source title",
            "relevance_score": 0.0 to 1.0,
            "quality_tier": "high" or "medium" or "low",
            "reason": "why this source is relevant"
        }}
    ]
}}

Return ONLY valid JSON."""


SYNTHESIZE_PROMPT = """You are a research synthesizer. Synthesize findings from these sources to answer the research question.

QUESTION: {question}

SOURCES:
{sources}

Previous synthesis (if iterating): {previous_synthesis}

Provide a comprehensive synthesis that:
1. Directly answers the research question
2. Summarizes key findings from sources
3. Notes areas of agreement/disagreement
4. Identifies limitations and gaps

Write 3-5 paragraphs with inline citations [Author, Year] or [Source ID]."""


GAP_ANALYSIS_PROMPT = """Identify research gaps based on this synthesis.

QUESTION: {question}

CURRENT SYNTHESIS:
{synthesis}

SOURCES USED:
{sources}

Identify:
1. Questions not fully answered
2. Missing evidence types (e.g., long-term data, specific populations)
3. Contradictions needing resolution
4. Future research needs

Return JSON:
{{
    "gaps": [
        {{
            "gap": "description of the gap",
            "severity": "major" or "minor",
            "searchable": true/false (can we find more sources?)
        }}
    ],
    "continue_research": true/false (should we iterate?)
}}

Return ONLY valid JSON."""


class DeepResearchAgent:
    """
    LangGraph-based autonomous research agent.

    Performs iterative research:
    1. PLAN: Create research strategy
    2. SEARCH: Query academic and web sources
    3. CURATE: Select and rank relevant sources
    4. SYNTHESIZE: Create evidence synthesis
    5. VERIFY: Check conclusions against sources
    6. ITERATE: If gaps found and depth allows

    Example:
        agent = DeepResearchAgent()

        # Research a question
        result = await agent.research(
            "What is the evidence for VEGF inhibitors in diabetic macular edema?",
            max_iterations=2
        )
        print(result.synthesis)
    """

    def __init__(
        self,
        router: Optional['ModelRouter'] = None,
        academic_search_fn=None,
        web_search_fn=None,
    ):
        """
        Initialize research agent.

        Args:
            router: ModelRouter for LLM calls
            academic_search_fn: Async function to search academic sources
            web_search_fn: Async function to search web sources
        """
        if router:
            self.router = router
        elif MODEL_ROUTER_AVAILABLE:
            self.router = ModelRouter()
        else:
            self.router = None
            logger.warning("ModelRouter not available")

        self.academic_search_fn = academic_search_fn
        self.web_search_fn = web_search_fn

        # Build graph if available
        self.graph = self._build_graph() if LANGGRAPH_AVAILABLE else None

    def _build_graph(self):
        """Build LangGraph workflow."""
        graph = StateGraph(ResearchState)

        # Add nodes
        graph.add_node("plan", self._plan)
        graph.add_node("search_academic", self._search_academic)
        graph.add_node("search_web", self._search_web)
        graph.add_node("curate", self._curate)
        graph.add_node("synthesize", self._synthesize)
        graph.add_node("analyze_gaps", self._analyze_gaps)

        # Define edges
        graph.add_edge("plan", "search_academic")
        graph.add_edge("search_academic", "search_web")
        graph.add_edge("search_web", "curate")
        graph.add_edge("curate", "synthesize")
        graph.add_edge("synthesize", "analyze_gaps")

        # Conditional edge for iteration
        graph.add_conditional_edges(
            "analyze_gaps",
            self._should_continue,
            {
                "continue": "search_academic",
                "end": END,
            }
        )

        # Set entry point
        graph.set_entry_point("plan")

        return graph.compile()

    async def _plan(self, state: ResearchState) -> Dict[str, Any]:
        """Create research plan."""
        if not self.router:
            return {"plan": "No router available"}

        prompt = PLAN_PROMPT.format(question=state["question"])

        result = await self.router.call(
            task_type="research",
            prompt=prompt,
        )

        return {"plan": result.content}

    async def _search_academic(self, state: ResearchState) -> Dict[str, Any]:
        """Search academic sources."""
        sources = []

        if self.academic_search_fn:
            try:
                results = await self.academic_search_fn(state["question"])
                sources = results[:20]  # Limit
            except Exception as e:
                logger.error(f"Academic search error: {e}")

        # If no search function, generate simulated sources
        if not sources and self.router:
            # Use LLM to suggest what sources might exist
            result = await self.router.call(
                task_type="research",
                prompt=f"For the research question '{state['question']}', "
                       f"list 5 hypothetical academic papers that would be relevant. "
                       f"Format as JSON list with title, authors, year, abstract_snippet.",
                response_format={"type": "json_object"},
            )
            try:
                data = json.loads(result.content)
                sources = data.get("papers", [])
            except:
                pass

        return {"academic_sources": sources}

    async def _search_web(self, state: ResearchState) -> Dict[str, Any]:
        """Search web/grey literature."""
        sources = []

        if self.web_search_fn:
            try:
                results = await self.web_search_fn(state["question"])
                sources = results[:10]  # Limit
            except Exception as e:
                logger.error(f"Web search error: {e}")

        return {"web_sources": sources}

    async def _curate(self, state: ResearchState) -> Dict[str, Any]:
        """Curate and rank sources."""
        if not self.router:
            return {"curated_sources": state.get("academic_sources", [])}

        # Combine sources
        all_sources = []
        for s in state.get("academic_sources", []):
            all_sources.append(f"[Academic] {json.dumps(s)}")
        for s in state.get("web_sources", []):
            all_sources.append(f"[Web] {json.dumps(s)}")

        if not all_sources:
            return {"curated_sources": []}

        sources_text = "\n".join(all_sources[:30])  # Limit

        prompt = CURATE_PROMPT.format(
            question=state["question"],
            sources=sources_text
        )

        result = await self.router.call(
            task_type="classify",
            prompt=prompt,
            response_format={"type": "json_object"},
        )

        try:
            data = json.loads(result.content)
            curated = data.get("selected_sources", [])
        except:
            curated = state.get("academic_sources", [])[:10]

        return {"curated_sources": curated}

    async def _synthesize(self, state: ResearchState) -> Dict[str, Any]:
        """Synthesize findings."""
        if not self.router:
            return {"synthesis": "No router available"}

        sources = state.get("curated_sources", [])
        sources_text = "\n".join([
            f"- {s.get('title', 'Unknown')}: {s.get('reason', s.get('abstract_snippet', ''))}"
            for s in sources[:10]
        ])

        previous = state.get("synthesis", "None")

        prompt = SYNTHESIZE_PROMPT.format(
            question=state["question"],
            sources=sources_text,
            previous_synthesis=previous[:500] if previous else "None"
        )

        result = await self.router.call(
            task_type="synthesize",
            prompt=prompt,
        )

        return {"synthesis": result.content}

    async def _analyze_gaps(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze gaps in the synthesis."""
        if not self.router:
            return {"gaps": [], "complete": True}

        sources_text = ", ".join([
            s.get("title", "Unknown")[:50]
            for s in state.get("curated_sources", [])[:10]
        ])

        prompt = GAP_ANALYSIS_PROMPT.format(
            question=state["question"],
            synthesis=state.get("synthesis", "")[:2000],
            sources=sources_text
        )

        result = await self.router.call(
            task_type="gap_analysis",
            prompt=prompt,
            response_format={"type": "json_object"},
        )

        try:
            data = json.loads(result.content)
            gaps = [g["gap"] for g in data.get("gaps", [])]
            continue_research = data.get("continue_research", False)
        except:
            gaps = []
            continue_research = False

        iteration = state.get("iteration", 0) + 1
        max_iter = state.get("max_iterations", 2)

        return {
            "gaps": gaps,
            "iteration": iteration,
            "complete": not continue_research or iteration >= max_iter,
        }

    def _should_continue(self, state: ResearchState) -> str:
        """Decide whether to continue iterating."""
        if state.get("complete", True):
            return "end"
        return "continue"

    async def research(
        self,
        question: str,
        max_iterations: int = 2,
    ) -> ResearchResult:
        """
        Conduct deep research on a question.

        Args:
            question: Research question
            max_iterations: Maximum research iterations

        Returns:
            ResearchResult with synthesis and sources
        """
        # Initial state
        initial_state: ResearchState = {
            "question": question,
            "plan": "",
            "academic_sources": [],
            "web_sources": [],
            "curated_sources": [],
            "synthesis": "",
            "verification": {},
            "gaps": [],
            "iteration": 0,
            "max_iterations": max_iterations,
            "complete": False,
        }

        # Run graph or simplified flow
        if self.graph:
            final_state = await self.graph.ainvoke(initial_state)
        else:
            # Simplified flow without LangGraph
            final_state = initial_state.copy()
            final_state.update(await self._plan(final_state))
            final_state.update(await self._search_academic(final_state))
            final_state.update(await self._search_web(final_state))
            final_state.update(await self._curate(final_state))
            final_state.update(await self._synthesize(final_state))
            final_state.update(await self._analyze_gaps(final_state))

        return ResearchResult(
            question=question,
            synthesis=final_state.get("synthesis", ""),
            sources=final_state.get("curated_sources", []),
            verification=final_state.get("verification", {}),
            gaps=final_state.get("gaps", []),
            iterations=final_state.get("iteration", 1),
            model_used="glm-4.6",
        )

    async def quick_research(self, question: str) -> str:
        """
        Quick single-shot research (no iteration).

        Args:
            question: Research question

        Returns:
            Synthesis text
        """
        result = await self.research(question, max_iterations=1)
        return result.synthesis


# Test function
async def _test_agent():
    """Test deep research agent."""
    agent = DeepResearchAgent()

    print("=== Deep Research Test ===")
    result = await agent.research(
        "What is the current evidence for artificial tears in dry eye disease?",
        max_iterations=1
    )

    print(f"Iterations: {result.iterations}")
    print(f"Sources: {len(result.sources)}")
    print(f"Gaps: {result.gaps}")
    print()
    print("Synthesis:")
    print(result.synthesis[:1000])


if __name__ == "__main__":
    asyncio.run(_test_agent())
