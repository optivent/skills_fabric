#!/usr/bin/env python3
"""
Round 5: Skill-Specific Patterns Research

Focused research on implementation-specific patterns for the
zero-hallucination progressive disclosure code skill.

Topics:
1. Parallel worktrees for AI coding agents
2. Progressive disclosure in technical documentation
3. Code library documentation best practices
4. Multi-model delegation (large/medium/small model cascades)
5. Zero-hallucination techniques for code generation
6. Library understanding and extraction patterns
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


ROUND_5_QUERIES = [
    # Parallel Worktrees
    ResearchQuery(
        topic="Git Worktrees for AI Agent Workflows",
        query="""What are best practices for using git worktrees in AI coding agent workflows?
        Include: parallel execution, branch isolation, multi-agent coordination.
        Focus on: how AI agents can leverage worktrees for concurrent tasks,
        avoiding conflicts, state management across worktrees.
        What patterns exist for multi-agent development in isolated branches?""",
        domains=["arxiv.org", "github.com", "git-scm.com"],
    ),
    ResearchQuery(
        topic="Parallel Code Analysis Architectures",
        query="""What are the best architectures for parallel code analysis in 2026?
        Include: concurrent file processing, dependency-aware parallelization.
        Focus on: how to analyze large codebases efficiently with multiple agents,
        avoiding race conditions, merging analysis results.
        What frameworks support parallel static analysis?""",
        domains=["arxiv.org", "github.com"],
    ),

    # Progressive Disclosure
    ResearchQuery(
        topic="Progressive Disclosure in Technical Documentation",
        query="""What are best practices for progressive disclosure in technical documentation?
        Include: information layering, depth levels, user-driven exploration.
        Focus on: code documentation, API references, library guides.
        How to structure content from overview to deep implementation details?
        What UX patterns work best for developer documentation?""",
        domains=["arxiv.org", "github.com", "nngroup.com"],
    ),
    ResearchQuery(
        topic="Layered Documentation Systems",
        query="""What are the best layered documentation systems for code libraries in 2026?
        Include: auto-generated docs, multi-level abstractions, drill-down patterns.
        Compare: Sphinx, MkDocs, Docusaurus, custom solutions.
        Focus on: how to generate documentation at multiple depth levels,
        from quick start to implementation internals.""",
        domains=["arxiv.org", "github.com"],
    ),

    # Code Documentation Best Practices
    ResearchQuery(
        topic="AI-Generated Code Documentation 2026",
        query="""What are the best practices for AI-generated code documentation in 2026?
        Include: accuracy verification, hallucination prevention, source grounding.
        Focus on: generating accurate library documentation from source code,
        ensuring factual correctness, citation of actual code locations.
        How do modern systems prevent documentation hallucinations?""",
        domains=["arxiv.org", "github.com", "anthropic.com"],
    ),
    ResearchQuery(
        topic="Code Understanding and Summarization",
        query="""What are the best code understanding and summarization techniques in 2026?
        Include: function-level, class-level, module-level, repo-level summarization.
        Focus on: extracting purpose, behavior, dependencies accurately.
        Compare: LLM-based vs AST-based vs hybrid approaches.
        How to ensure summaries are factually grounded in actual code?""",
        domains=["arxiv.org", "github.com"],
    ),

    # Multi-Model Delegation
    ResearchQuery(
        topic="Model Cascading and Routing 2026",
        query="""What are the best model cascading and routing patterns for AI agents in 2026?
        Include: large-to-small model delegation, task-based routing, cost optimization.
        Focus on: when to use powerful vs efficient models, routing algorithms,
        quality-cost tradeoffs in multi-model architectures.
        How do production systems implement model selection?""",
        domains=["arxiv.org", "github.com", "anthropic.com", "openai.com"],
    ),
    ResearchQuery(
        topic="Hierarchical LLM Orchestration",
        query="""What are the best hierarchical LLM orchestration patterns in 2026?
        Include: planner-worker architectures, supervisor-subordinate patterns.
        Focus on: using large models for planning, smaller for execution,
        context handoff between model tiers, verification chains.
        Examples from production multi-model systems?""",
        domains=["arxiv.org", "github.com"],
    ),

    # Zero-Hallucination Techniques
    ResearchQuery(
        topic="Hallucination Prevention in Code Generation",
        query="""What are the best hallucination prevention techniques for code generation in 2026?
        Include: retrieval grounding, verification loops, citation requirements.
        Focus on: ensuring generated code references exist, API correctness,
        preventing fabricated functions or parameters.
        What evaluation metrics detect code hallucinations?""",
        domains=["arxiv.org", "github.com"],
    ),
    ResearchQuery(
        topic="Grounded Code Documentation",
        query="""How to generate grounded, verifiable code documentation?
        Include: source-linked explanations, traceable claims, fact verification.
        Focus on: every statement backed by actual code, line number citations,
        preventing invented behavior descriptions.
        What systems ensure documentation accuracy against source?""",
        domains=["arxiv.org", "github.com"],
    ),

    # Library Understanding
    ResearchQuery(
        topic="Automated Library Analysis Patterns",
        query="""What are the best patterns for automated library analysis in 2026?
        Include: API extraction, dependency mapping, usage pattern detection.
        Focus on: understanding library architecture from source code,
        identifying key abstractions, entry points, extension mechanisms.
        How do AI systems learn library mental models?""",
        domains=["arxiv.org", "github.com"],
    ),
    ResearchQuery(
        topic="Repository-Level Code Understanding",
        query="""What are the best approaches for repository-level code understanding in 2026?
        Include: cross-file analysis, architectural inference, design pattern detection.
        Focus on: building comprehensive repo understanding for AI agents,
        handling large codebases, incremental analysis.
        What benchmarks evaluate repo-level comprehension?""",
        domains=["arxiv.org", "github.com"],
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
    print("ROUND 5: SKILL-SPECIFIC PATTERNS RESEARCH")
    print("Progressive disclosure, worktrees, multi-model, zero-hallucination")
    print("=" * 70)

    output_dir = Path("research_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    client = PerplexityClient()
    results = []

    try:
        for i, query in enumerate(ROUND_5_QUERIES, 1):
            print(f"\n[{i}/{len(ROUND_5_QUERIES)}]")
            result = await research_query(client, query)
            results.append(result)

            if i < len(ROUND_5_QUERIES):
                print("  Waiting 2s...")
                await asyncio.sleep(2)

        # Save results
        data = {
            "timestamp": datetime.now().isoformat(),
            "round": "5_skill_patterns",
            "total_queries": len(results),
            "results": [asdict(r) for r in results],
        }

        output_path = output_dir / "round5_skill_patterns.json"
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved results to: {output_path}")

        # Generate markdown report
        lines = [
            "# Round 5: Skill-Specific Patterns Research",
            f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Queries**: {len(results)}",
            "\n## Research Categories",
            "1. Parallel Worktrees (2 queries)",
            "2. Progressive Disclosure (2 queries)",
            "3. Code Documentation (2 queries)",
            "4. Multi-Model Delegation (2 queries)",
            "5. Zero-Hallucination (2 queries)",
            "6. Library Understanding (2 queries)",
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

        report_path = output_dir / "ROUND5_SKILL_PATTERNS_REPORT.md"
        with open(report_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Generated report: {report_path}")

    finally:
        await client.close()

    print("\n" + "=" * 70)
    print("ROUND 5 RESEARCH COMPLETE")
    print(f"Total queries: {len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
