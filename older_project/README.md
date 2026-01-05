# Skills Fabric - Older Project Archive

## Purpose

This folder contains the **complete intellectual history** of the Skills Fabric project, including research prototypes, crawled documentation, strategy documents, and implementation artifacts from the development journey.

---

## Goal: Progressive Iceberg Zero-Hallucination Claude Skill Compiler

Build a **production-ready system** that generates **verified Claude Skills** from any open-source library by:
1. Extracting documentation with embedded GitHub links (CodeWiki)
2. Validating links against actual source code (Git Clone)
3. Parsing symbols at configurable depth (AST/LSP)
4. Verifying execution in sandbox (Bubblewrap)
5. Storing in knowledge graph (KuzuDB)

---

## Key Documents

### Architecture & Strategy

| File | Description |
|------|-------------|
| `PROGRESSIVE_ICEBERG_ARCHITECTURE.md` | **Core Architecture** - The 5-layer Progressive Iceberg model with Progressive Deepening (Levels 0-5) |
| `ZAI_GLM_INTEGRATION.md` | Z.AI GLM-4.7 Coding Plan API integration guide |
| `audit_reports/BMAD_AUDIT_PLAN.md` | BMAD methodology audit plan |
| `audit_reports/BMAD_HONEST_GAP_ANALYSIS.md` | Honest gap analysis of current vs ideal state |
| `audit_reports/QA_AUDIT_REPORT.md` | Quality assurance audit findings |
| `audit_reports/SOVEREIGN_PLATFORM_ARCHITECTURE.md` | Original platform architecture |
| `audit_reports/ULTRATHINK_ROBUSTNESS_STRATEGY.md` | Robustness and error handling strategy |

---

## Prototype Implementations

### `play_prototypes/`

| Folder | Purpose |
|--------|---------|
| `code_wiki_mcp/` | Selenium-based MCP server for CodeWiki scraping |
| `forensic_mcp/` | AST forensic analysis MCP server |
| `loguru_poc/` | **Complete end-to-end POC** - Loguru library skill generation |
| `orchestrator/` | Multi-agent MCP orchestration (`triple_sensor_agent.py`) |

### `research_artifacts/`

| File | Purpose |
|------|---------|
| `skill_factory.py` | V1 skill generation (basic) |
| `skill_factory_v2.py` | V2 with AST validation |
| `skill_factory_v3.py` | V3 with LangGraph orchestration |
| `sovereign_bridge.py` | Cross-process bridge pattern |
| `kuzu_skill_store.py` | KuzuDB storage implementation |
| `codewiki_ingest.py` | CodeWiki ingestion with Crawl4AI |

---

## Crawled Documentation

### `crawl_data/crawl_opencode/`

**Complete OpenCode framework documentation:**
- `docs_full/` - 25 official documentation pages
- `ecosystem_detail/` - 30+ ecosystem plugin analyses

### `crawl_data/langgraph_repo/`

**LangGraph source repository:**
- `AGENTS.md`, `CLAUDE.md` - AI agent instructions
- Full examples and documentation

---

## Agent Definitions

### `opencode_skills/`

| Agent | Role |
|-------|------|
| `oracle_fabric.md` | Deep audit specialist (Daniel Miessler perspective) |
| `sisyphus_fabric.md` | Lead orchestrator (disciplined SF Bay Area engineer) |
| `librarian_fabric.md` | Context and documentation specialist |
| `explore_fabric.md` | Codebase discovery and pattern matching |

---

## Knowledge Base

### `opencode_knowledge/`

20 ingested architecture documents covering:
- Agent definitions and architecture
- Lifecycle hooks and behavior modification
- MCP (Micro Component Providers) implementation
- LSP (Language Server Protocol) integrations
- Context window limit recovery

---

## Z.AI GLM Integration

### `zai_glm_integration/`

| File | Purpose |
|------|---------|
| `glm_api_client.py` | Full Z.AI Coding Plan API client (38KB) |
| `glm_research.py` | Research-oriented wrapper |
| `model_router.py` | Intelligent model selection |

**Pricing:** GLM-4.7 is 6x cheaper than Claude for extraction tasks.

---

## Protocols

### `protocols/scip.proto`

SCIP (Source Code Intelligence Protocol) schema for compiler-grade symbol indexing - enables deep code understanding.

---

## Progressive Deepening Model

From a CodeWiki connection point (e.g., line 112), we expand progressively:

| Level | Action | Stop If... |
|-------|--------|------------|
| 0 | Validate link exists | Just syntax example |
| 1 | Parse the symbol | Just API reference |
| 2 | Parse immediate dependencies | Understanding behavior |
| 3 | Follow 1 level of call graph | Understanding mechanics |
| 4 | Full recursive expansion | Master class skill |
| 5 | Execution trace in sandbox | Debugging skill |

---

## File Counts

| Category | Files |
|----------|-------|
| Architecture docs | 2 |
| Audit reports | 10 |
| Research artifacts | 14 |
| Play prototypes | 800+ |
| Crawl data | 700+ |
| OpenCode knowledge | 20 |
| Agent skills | 4 |
| Z.AI integration | 3 |
| Protocols | 1 |
| **Total** | **~1,555** |

---

## How to Use This Archive

1. **Understand the vision:** Read `PROGRESSIVE_ICEBERG_ARCHITECTURE.md`
2. **See working examples:** Explore `play_prototypes/loguru_poc/`
3. **Learn the framework:** Study `opencode_knowledge/*.md`
4. **Integrate Z.AI:** Follow `ZAI_GLM_INTEGRATION.md`
5. **Review audit findings:** Check `audit_reports/`

---

## Related: Main `src/` Implementation

The production code in `../src/skills_fabric/` implements:
- `ingest/` - Context7, Exa Search, Fusion
- `analyze/` - AST, Tree-sitter, LSP, Symbol Graph
- `verify/` - Bubblewrap sandbox, Tracer, Cross-layer
- `link/` - PROVEN linker, Embedding linker
- `generate/` - LLM client, Skill factory
- `store/` - KuzuDB storage
