# Skills Fabric - Core System Specification

> OpenSpec Living Specification
> Last Updated: 2026-01-07

## System Overview

Skills Fabric is a **zero-hallucination Claude skill generation pipeline** that creates AI skills from real source code with verifiable citations.

## Core Guarantee

```
Hall_m = rejected / (validated + rejected) < 0.02 (2%)
```

Every generated skill must be grounded in actual source code with `file:line` citations.

## Trust Hierarchy

| Level | Name | Trust | Verification |
|-------|------|-------|--------------|
| 1 | HardContent | 100% | AST/SCIP verified |
| 2 | VerifiedSoft | 95% | Sandbox + grounding |
| 3 | Unverified | 0% | REJECTED |

## CLI Commands

| Command | Purpose |
|---------|---------|
| `generate <library>` | Generate skills with progressive understanding |
| `verify <query>` | Verify symbols via DDR |
| `analyze <path>` | Extract symbols from source |
| `research <topic>` | Research via Perplexity |
| `search <query>` | Search via Brave |
| `version` | Show version |

## Key Components

### Verification Pipeline (DDR)
- Multi-source validation (AST, Tree-sitter, LSP, File Content)
- HallMetric tracking with threshold enforcement
- SourceRef citations for all validated symbols

### Analysis Layer
- ASTParser: Python with rich metadata
- TreeSitterParser: Multi-language (Python, TypeScript, JavaScript)
- LSPClient: Language server integration
- CodeAnalyzer: Unified interface with graceful degradation

### Orchestration
- SupervisorAgent: Multi-agent coordination
- RalphWiggumLoop: Autonomous iteration until completion
- CompletionPromise: Exit conditions

### Storage
- KuzuDB: Graph database for skills and relationships
- Thread-safe singleton with thread-local connections

## Dependencies

- Python 3.11+
- kuzu, langgraph, langchain-openai
- tree-sitter with language packs
- pydantic, requests

## Configuration

Required environment variables:
- `ANTHROPIC_API_KEY`: Claude API access
- `ZAI_API_KEY`: GLM API access

Optional:
- `PERPLEXITY_API_KEY`: Research queries
- `BRAVE_API_KEY`: Documentation search

---

*This is a living specification maintained by OpenSpec.*
