#!/usr/bin/env python3
"""
Round 6: Framework & Best Practices Research

Deep dive into specific frameworks and methodologies:
1. BMAD Framework
2. Spec-Kit
3. AgentOS
4. Daniel Miessler's Fabric patterns
5. Ralph's Loop
6. AwesomeClaude resources
7. Claude Anthropic best features for agents
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


ROUND_6_QUERIES = [
    # BMAD Framework
    ResearchQuery(
        topic="BMAD Framework for AI Agents",
        query="""What is the BMAD framework for AI agent development?
        Include: core principles, workflow stages, implementation patterns.
        Focus on: how BMAD structures agent development, best practices.
        What are the key components and how do they work together?""",
        domains=["github.com", "arxiv.org"],
    ),

    # Spec-Kit
    ResearchQuery(
        topic="Spec-Kit for Agent Specifications",
        query="""What is Spec-Kit for AI agent specifications?
        Include: specification templates, validation patterns, documentation structure.
        Focus on: how to define agent behavior, capabilities, constraints.
        What are best practices for agent specification?""",
        domains=["github.com", "arxiv.org"],
    ),

    # AgentOS
    ResearchQuery(
        topic="AgentOS Operating System for AI Agents",
        query="""What is AgentOS for AI agent orchestration?
        Include: architecture, features, agent lifecycle management.
        Focus on: how AgentOS manages multiple agents, resource allocation.
        What are the key patterns and integrations?""",
        domains=["github.com", "arxiv.org"],
    ),

    # Daniel Miessler's Fabric
    ResearchQuery(
        topic="Daniel Miessler Fabric AI Patterns",
        query="""What is Daniel Miessler's Fabric framework for AI?
        Include: pattern library, prompt engineering, augmentation approach.
        Focus on: how Fabric organizes AI patterns, best prompts and templates.
        What are the key patterns for code analysis and documentation?""",
        domains=["github.com", "danielmiessler.com"],
    ),

    # Fabric Patterns Deep Dive
    ResearchQuery(
        topic="Fabric Patterns for Code and Analysis",
        query="""What are the best Fabric patterns by Daniel Miessler for code analysis?
        Include: extract_wisdom, analyze_code, create_summary patterns.
        Focus on: patterns useful for code documentation, understanding, extraction.
        List the most useful patterns with their purposes.""",
        domains=["github.com", "danielmiessler.com"],
    ),

    # Ralph's Loop
    ResearchQuery(
        topic="Ralph's Loop Agent Execution Pattern",
        query="""What is Ralph's Loop pattern for AI agent execution?
        Include: loop structure, iteration patterns, feedback mechanisms.
        Focus on: how Ralph's Loop improves agent reasoning and execution.
        What are the key implementation patterns?""",
        domains=["github.com", "arxiv.org"],
    ),

    # AwesomeClaude
    ResearchQuery(
        topic="AwesomeClaude Resources and Tools",
        query="""What resources are available at awesomeclaude.ai?
        Include: tools, integrations, best practices for Claude.
        Focus on: Claude Code features, MCP servers, agent patterns.
        What are the most useful resources for Claude development?""",
        domains=["github.com", "awesomeclaude.ai", "anthropic.com"],
    ),

    # Claude Code Best Features
    ResearchQuery(
        topic="Claude Code Best Features 2026",
        query="""What are the best features of Claude Code for AI development in 2026?
        Include: hooks, slash commands, MCP servers, parallel agents.
        Focus on: features for building skills and automating workflows.
        What are the most powerful capabilities for developers?""",
        domains=["github.com", "anthropic.com", "docs.anthropic.com"],
    ),

    # Claude Agent SDK
    ResearchQuery(
        topic="Claude Agent SDK Patterns",
        query="""What are the best patterns for Claude Agent SDK development?
        Include: agent architecture, tool use, memory management.
        Focus on: building production-ready Claude agents.
        What are the recommended patterns and anti-patterns?""",
        domains=["github.com", "anthropic.com"],
    ),

    # Claude MCP Servers
    ResearchQuery(
        topic="Claude MCP Server Best Practices",
        query="""What are the best MCP (Model Context Protocol) servers for Claude?
        Include: popular servers, integration patterns, custom server development.
        Focus on: MCP servers for code analysis, file management, search.
        What are the most useful MCP servers for development workflows?""",
        domains=["github.com", "anthropic.com", "modelcontextprotocol.io"],
    ),

    # Claude Hooks and Automation
    ResearchQuery(
        topic="Claude Code Hooks and Automation",
        query="""What are Claude Code hooks and how to use them for automation?
        Include: pre/post hooks, event triggers, workflow automation.
        Focus on: automating development workflows with Claude hooks.
        What are the best practices for hook implementation?""",
        domains=["github.com", "anthropic.com"],
    ),

    # Anthropic Best Practices
    ResearchQuery(
        topic="Anthropic Agent Best Practices 2026",
        query="""What are Anthropic's recommended best practices for building AI agents in 2026?
        Include: official guidelines, safety patterns, reliability techniques.
        Focus on: production-ready agent development with Claude.
        What does Anthropic recommend for agent architecture?""",
        domains=["anthropic.com", "docs.anthropic.com", "github.com/anthropics"],
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
    print("ROUND 6: FRAMEWORKS & BEST PRACTICES RESEARCH")
    print("BMAD, Spec-Kit, AgentOS, Fabric, Ralph's Loop, Claude Features")
    print("=" * 70)

    output_dir = Path("research_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    client = PerplexityClient()
    results = []

    try:
        for i, query in enumerate(ROUND_6_QUERIES, 1):
            print(f"\n[{i}/{len(ROUND_6_QUERIES)}]")
            result = await research_query(client, query)
            results.append(result)

            if i < len(ROUND_6_QUERIES):
                print("  Waiting 2s...")
                await asyncio.sleep(2)

        # Save results
        data = {
            "timestamp": datetime.now().isoformat(),
            "round": "6_frameworks_best_practices",
            "total_queries": len(results),
            "results": [asdict(r) for r in results],
        }

        output_path = output_dir / "round6_frameworks.json"
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved results to: {output_path}")

        # Generate markdown report
        lines = [
            "# Round 6: Frameworks & Best Practices Research",
            f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Queries**: {len(results)}",
            "\n## Research Categories",
            "1. BMAD Framework (1 query)",
            "2. Spec-Kit (1 query)",
            "3. AgentOS (1 query)",
            "4. Daniel Miessler's Fabric (2 queries)",
            "5. Ralph's Loop (1 query)",
            "6. Claude/Anthropic Features (6 queries)",
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

        report_path = output_dir / "ROUND6_FRAMEWORKS_REPORT.md"
        with open(report_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Generated report: {report_path}")

    finally:
        await client.close()

    print("\n" + "=" * 70)
    print("ROUND 6 RESEARCH COMPLETE")
    print(f"Total queries: {len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
