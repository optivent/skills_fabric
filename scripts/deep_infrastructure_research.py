#!/usr/bin/env python3
"""
Deep Infrastructure Research Script

Systematic multi-round research using Perplexity API to map
the optimal infrastructure for AI skill development.

Research Areas:
1. AI Agent Infrastructure Patterns
2. Memory and RAG Architectures
3. Code Understanding Systems
4. Execution and Verification
5. Observability and Production Patterns
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent / "retrievals"))
from perplexity_client import PerplexityClient, SonarModel, SearchRecency, SearchContextSize


@dataclass
class ResearchQuery:
    """A research query with metadata."""
    topic: str
    query: str
    domains: List[str] = None
    recency: str = "month"
    follow_up: bool = True


@dataclass
class ResearchResult:
    """Result from a research query."""
    topic: str
    query: str
    response: str
    citations: List[str]
    related_questions: List[str]
    timestamp: str
    model: str


# =============================================================================
# RESEARCH QUERIES - Round 1: Foundation
# =============================================================================

ROUND_1_QUERIES = [
    ResearchQuery(
        topic="AI Agent Architectures 2026",
        query="""What are the most effective AI agent architectures in 2026?
        Compare: ReAct, Plan-and-Execute, LATS, Reflection patterns.
        Include: multi-agent systems, tool use patterns, memory integration.
        Focus on: production-ready, scalable, reliable approaches.""",
        domains=["arxiv.org", "github.com", "langchain.com", "anthropic.com"],
    ),
    ResearchQuery(
        topic="Multi-Agent Orchestration Patterns",
        query="""What are the best multi-agent orchestration patterns in 2026?
        Compare: hierarchical vs flat, supervisor patterns, swarm intelligence.
        Include: Google ADK patterns, LangGraph, AutoGen, CrewAI architectures.
        Focus on: context management, handoff protocols, state synchronization.""",
        domains=["arxiv.org", "github.com", "langchain.com"],
    ),
    ResearchQuery(
        topic="Memory Systems for AI Agents",
        query="""What are the best memory architectures for AI coding agents in 2026?
        Compare: Mem0, Zep, MemGPT, Letta, custom implementations.
        Include: episodic, semantic, procedural memory types.
        Focus on: work tracking, learning from experience, session continuity.""",
        domains=["arxiv.org", "github.com", "mem0.ai"],
    ),
    ResearchQuery(
        topic="RAG Infrastructure 2026",
        query="""What is the optimal RAG infrastructure for code understanding in 2026?
        Compare: embedding models (Qwen3, Voyage, BGE), vector DBs (Qdrant, Pinecone, Milvus).
        Include: hybrid search, reranking strategies, chunking approaches.
        Focus on: code-specific retrieval, semantic code search.""",
        domains=["arxiv.org", "qdrant.tech", "milvus.io"],
    ),
]


# =============================================================================
# RESEARCH QUERIES - Round 2: Deep Dive
# =============================================================================

ROUND_2_QUERIES = [
    ResearchQuery(
        topic="Code Knowledge Graphs",
        query="""What are the best approaches for building code knowledge graphs in 2026?
        Compare: Cognee, CodeQL, Sourcegraph, custom AST-based solutions.
        Include: dependency analysis, call graphs, semantic relationships.
        Focus on: Python codebases, incremental updates, query patterns.""",
        domains=["arxiv.org", "github.com", "sourcegraph.com"],
    ),
    ResearchQuery(
        topic="Code Execution Sandboxes",
        query="""What are the best code execution sandboxes for AI agents in 2026?
        Compare: E2B, Modal, Firecracker, Docker, gVisor.
        Include: security models, performance, language support, pricing.
        Focus on: AI-generated code execution, isolation, reproducibility.""",
        domains=["e2b.dev", "modal.com", "arxiv.org"],
    ),
    ResearchQuery(
        topic="LLM Observability and Tracing",
        query="""What are the best observability tools for LLM applications in 2026?
        Compare: LangSmith, Langfuse, Helicone, Weights & Biases, Phoenix.
        Include: tracing, cost tracking, evaluation, debugging.
        Focus on: multi-agent systems, production monitoring.""",
        domains=["langchain.com", "github.com", "arxiv.org"],
    ),
    ResearchQuery(
        topic="Embedding Models for Code",
        query="""What are the best embedding models for code search and retrieval in 2026?
        Compare: Voyage-code-3, CodeBERT, GraphCodeBERT, Qwen3-Embedding.
        Include: benchmarks, dimensions, multilingual support.
        Focus on: function-level retrieval, semantic similarity.""",
        domains=["arxiv.org", "huggingface.co", "voyageai.com"],
    ),
]


# =============================================================================
# RESEARCH QUERIES - Round 3: Integration Patterns
# =============================================================================

ROUND_3_QUERIES = [
    ResearchQuery(
        topic="Production AI Agent Patterns",
        query="""What are proven production patterns for AI agents in 2026?
        Include: error handling, fallbacks, rate limiting, caching.
        Focus on: reliability, cost optimization, scalability.
        Examples from: enterprise deployments, open-source projects.""",
        domains=["arxiv.org", "github.com", "anthropic.com"],
    ),
    ResearchQuery(
        topic="AI Agent Testing and Verification",
        query="""What are the best testing approaches for AI agents in 2026?
        Include: unit testing, integration testing, evaluation frameworks.
        Compare: deterministic vs stochastic testing, benchmark suites.
        Focus on: code generation quality, hallucination detection.""",
        domains=["arxiv.org", "github.com", "langchain.com"],
    ),
    ResearchQuery(
        topic="Context Window Management",
        query="""What are the best context window management strategies for AI agents in 2026?
        Include: summarization, compression, selective retrieval.
        Compare: sliding window, hierarchical context, dynamic loading.
        Focus on: long conversations, multi-file code context.""",
        domains=["arxiv.org", "anthropic.com", "openai.com"],
    ),
    ResearchQuery(
        topic="Tool Use and Function Calling",
        query="""What are the best practices for AI agent tool use in 2026?
        Include: tool definition, parameter validation, error recovery.
        Compare: OpenAI function calling, Anthropic tool use, custom approaches.
        Focus on: complex tool chains, parallel execution.""",
        domains=["arxiv.org", "anthropic.com", "openai.com"],
    ),
]


class InfrastructureResearcher:
    """Systematic infrastructure research using Perplexity."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = PerplexityClient()
        self.results: List[ResearchResult] = []

    async def research_query(self, query: ResearchQuery, max_retries: int = 3) -> ResearchResult:
        """Execute a single research query with retry logic."""
        print(f"\n  Researching: {query.topic}")
        print(f"  Query: {query.query[:80]}...")

        # Map recency string to enum
        recency_map = {
            "hour": SearchRecency.HOUR,
            "day": SearchRecency.DAY,
            "week": SearchRecency.WEEK,
            "month": SearchRecency.MONTH,
        }

        # Try with exponential backoff
        for attempt in range(max_retries):
            try:
                # Use sonar (more stable) with fallback to sonar-pro
                model = SonarModel.SONAR if attempt < 2 else SonarModel.SONAR_PRO

                response = await self.client.search(
                    query=query.query,
                    model=model,
                    domains=query.domains,
                    recency=recency_map.get(query.recency),
                    context_size=SearchContextSize.HIGH,
                    return_citations=True,
                    return_related_questions=True,
                    max_tokens=4096,
                )

                result = ResearchResult(
                    topic=query.topic,
                    query=query.query,
                    response=response.content,
                    citations=[c.url for c in response.citations],
                    related_questions=response.related_questions,
                    timestamp=datetime.now().isoformat(),
                    model=response.model,
                )

                print(f"  ✓ Got {len(response.content)} chars, {len(response.citations)} citations")
                return result

            except Exception as e:
                wait_time = 2 ** (attempt + 1)  # 2, 4, 8 seconds
                print(f"  ✗ Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"  Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)

        # All retries failed
        print(f"  ✗ All {max_retries} attempts failed")
        return ResearchResult(
            topic=query.topic,
            query=query.query,
            response=f"Error: All {max_retries} retry attempts failed",
            citations=[],
            related_questions=[],
            timestamp=datetime.now().isoformat(),
            model="error",
        )

    async def run_round(self, round_name: str, queries: List[ResearchQuery]) -> List[ResearchResult]:
        """Run a round of research queries."""
        print(f"\n{'='*70}")
        print(f"RESEARCH ROUND: {round_name}")
        print(f"{'='*70}")
        print(f"Queries: {len(queries)}")

        results = []
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}]")
            result = await self.research_query(query)
            results.append(result)
            self.results.append(result)

            # Rate limiting - be nice to the API
            if i < len(queries):
                print("  Waiting 2s...")
                await asyncio.sleep(2)

        return results

    def save_results(self, filename: str):
        """Save results to JSON file."""
        output_path = self.output_dir / filename

        data = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(self.results),
            "results": [asdict(r) for r in self.results],
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nSaved results to: {output_path}")

    def generate_markdown_report(self) -> str:
        """Generate markdown report from results."""
        lines = [
            "# Infrastructure Research Report",
            f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Queries**: {len(self.results)}",
            "\n---\n",
        ]

        # Group by topic
        for result in self.results:
            lines.append(f"## {result.topic}")
            lines.append(f"\n**Query**: {result.query[:200]}...")
            lines.append(f"\n**Model**: {result.model}")
            lines.append(f"\n### Findings\n")
            lines.append(result.response)

            if result.citations:
                lines.append(f"\n### Sources ({len(result.citations)})")
                for i, url in enumerate(result.citations[:10], 1):
                    lines.append(f"{i}. {url}")

            if result.related_questions:
                lines.append(f"\n### Related Questions")
                for q in result.related_questions[:5]:
                    lines.append(f"- {q}")

            lines.append("\n---\n")

        return "\n".join(lines)

    async def close(self):
        """Close the client."""
        await self.client.close()


async def main():
    """Run the full research pipeline."""
    print("="*70)
    print("DEEP INFRASTRUCTURE RESEARCH")
    print("Building comprehensive map of optimal AI skill development infrastructure")
    print("="*70)

    output_dir = Path("research_output")
    researcher = InfrastructureResearcher(output_dir)

    try:
        # Round 1: Foundation
        await researcher.run_round("Round 1: Foundation", ROUND_1_QUERIES)
        researcher.save_results("round1_foundation.json")

        # Round 2: Deep Dive
        await researcher.run_round("Round 2: Deep Dive", ROUND_2_QUERIES)
        researcher.save_results("round2_deep_dive.json")

        # Round 3: Integration Patterns
        await researcher.run_round("Round 3: Integration Patterns", ROUND_3_QUERIES)
        researcher.save_results("round3_integration.json")

        # Generate final report
        report = researcher.generate_markdown_report()
        report_path = output_dir / "INFRASTRUCTURE_RESEARCH_REPORT.md"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\nGenerated report: {report_path}")

        # Save all results
        researcher.save_results("all_results.json")

    finally:
        await researcher.close()

    print("\n" + "="*70)
    print("RESEARCH COMPLETE")
    print(f"Total queries: {len(researcher.results)}")
    print(f"Output directory: {output_dir}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
