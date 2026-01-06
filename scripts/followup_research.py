#!/usr/bin/env python3
"""
Follow-up Deep Research - Round 4

Investigating specific systems discovered in initial research:
1. Memory Bear architecture details
2. CaveAgent dual-stream implementation
3. Jenius-Agent production patterns
4. AgeMem LTM/STM integration
5. Cognee code graph implementation
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent / "retrievals"))
from perplexity_client import PerplexityClient, SonarModel, SearchRecency, SearchContextSize


@dataclass
class ResearchQuery:
    topic: str
    query: str
    domains: List[str] = None
    recency: str = "month"


@dataclass
class ResearchResult:
    topic: str
    query: str
    response: str
    citations: List[str]
    related_questions: List[str]
    timestamp: str
    model: str


# Follow-up queries based on Round 1-3 discoveries
FOLLOWUP_QUERIES = [
    ResearchQuery(
        topic="Memory Bear Architecture Deep Dive",
        query="""What is Memory Bear architecture for AI agents?
        Include: forgetting engine (Ebbinghaus/ACT-R), activation decay mechanisms.
        Focus on: implementation details, API design, integration patterns.
        How does it compare to Mem0/MemGPT in production deployments?""",
        domains=["arxiv.org", "github.com"],
    ),
    ResearchQuery(
        topic="CaveAgent Dual-Stream Implementation",
        query="""How does CaveAgent implement dual-stream context management?
        Include: semantic stream vs runtime stream, dynamic synchronization.
        Focus on: code architecture, persistent object storage, variable references.
        What are the integration patterns for coding agents?""",
        domains=["arxiv.org", "github.com"],
    ),
    ResearchQuery(
        topic="Jenius-Agent Production Patterns",
        query="""What are the key implementation patterns in Jenius-Agent framework?
        Include: adaptive prompting, hierarchical memory, context-aware orchestration.
        Focus on: production optimizations, token efficiency, reliability patterns.
        How does it achieve 20% accuracy gains over baselines?""",
        domains=["arxiv.org", "github.com"],
    ),
    ResearchQuery(
        topic="AgeMem Agentic Memory System",
        query="""How does AgeMem implement agentic memory with LTM/STM tools?
        Include: autonomous memory invocation, unified LTM/STM architecture.
        Focus on: reinforcement learning for memory management, tool-based recall.
        What benchmarks show its performance gains?""",
        domains=["arxiv.org", "github.com"],
    ),
    ResearchQuery(
        topic="Cognee Code Graph Implementation",
        query="""How to implement Cognee for code knowledge graphs?
        Include: graph indexing, DFG edges, AST integration, schema-bounded updates.
        Focus on: Python codebase integration, query patterns, incremental updates.
        How does it integrate with LLMs like CGM for code understanding?""",
        domains=["arxiv.org", "github.com", "cognee.ai"],
    ),
    ResearchQuery(
        topic="MAESTRO Multi-Agent Evaluation",
        query="""What is the MAESTRO framework for multi-agent evaluation?
        Include: evaluation dimensions, test case design, benchmark methodology.
        Focus on: agent testing patterns, success metrics, failure analysis.
        How does it compare to AgentBench and other evaluation suites?""",
        domains=["arxiv.org", "github.com", "langchain.com"],
    ),
]


async def research_query(client: PerplexityClient, query: ResearchQuery, max_retries: int = 3) -> ResearchResult:
    """Execute a single research query with retry logic."""
    print(f"\n  Researching: {query.topic}")
    print(f"  Query: {query.query[:80]}...")

    recency_map = {
        "hour": SearchRecency.HOUR,
        "day": SearchRecency.DAY,
        "week": SearchRecency.WEEK,
        "month": SearchRecency.MONTH,
    }

    for attempt in range(max_retries):
        try:
            model = SonarModel.SONAR if attempt < 2 else SonarModel.SONAR_PRO

            response = await client.search(
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
            wait_time = 2 ** (attempt + 1)
            print(f"  ✗ Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

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


async def main():
    print("=" * 70)
    print("FOLLOW-UP DEEP RESEARCH - Round 4")
    print("Investigating discovered systems from initial research")
    print("=" * 70)

    output_dir = Path("research_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    client = PerplexityClient()
    results = []

    try:
        for i, query in enumerate(FOLLOWUP_QUERIES, 1):
            print(f"\n[{i}/{len(FOLLOWUP_QUERIES)}]")
            result = await research_query(client, query)
            results.append(result)

            if i < len(FOLLOWUP_QUERIES):
                print("  Waiting 2s...")
                await asyncio.sleep(2)

        # Save results
        data = {
            "timestamp": datetime.now().isoformat(),
            "round": "4_followup",
            "total_queries": len(results),
            "results": [asdict(r) for r in results],
        }

        output_path = output_dir / "round4_followup.json"
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved results to: {output_path}")

        # Generate markdown report
        lines = [
            "# Follow-up Research Report - Round 4",
            f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Queries**: {len(results)}",
            "\n---\n",
        ]

        for result in results:
            lines.append(f"## {result.topic}")
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

        report_path = output_dir / "FOLLOWUP_RESEARCH_REPORT.md"
        with open(report_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Generated report: {report_path}")

    finally:
        await client.close()

    print("\n" + "=" * 70)
    print("FOLLOW-UP RESEARCH COMPLETE")
    print(f"Total queries: {len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
