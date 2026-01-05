# ULTRATHINK: Sovereign Bridge + Skill Factory Integration Strategy

**Date**: 2026-01-05
**Purpose**: Synthesize two powerful systems into one unified "Sovereign Intelligence Platform"

---

## Executive Summary

We have two complementary systems on `core`:

| System | Location | Purpose | Strength |
|--------|----------|---------|----------|
| **Sovereign Bridge** | `~/kuzu_db`, `~/sovereign_bridge.py` | Link Docs → Code | Graph DB, GLiNER NER, SCIP parsing |
| **ULTRATHINK Skill Factory** | `~/lab/new_crawl4AI/` | Generate verified code skills | Context7, LangGraph, Sandbox verification |

**The Vision**: Combine them into a **Sovereign Intelligence Platform** that:

1. **Grounds** documentation in real source code (Bridge)
2. **Generates** verified, executable code skills (Factory)
3. **Stores** everything in a unified graph (KuzuDB)
4. **Queries** via natural language (GLiNER + Cypher)

---

## Architecture Analysis

### What Sovereign Bridge Does Well

```
┌─────────────────────────────────────────────────────┐
│               SOVEREIGN BRIDGE                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  INPUT:  CodeWiki Docs + Git Repository             │
│                                                      │
│  PROCESS:                                            │
│    1. GLiNER extracts concepts from docs            │
│    2. SCIP parses code symbols from repo            │
│    3. Fuzzy matching links Concept → Symbol         │
│                                                      │
│  OUTPUT: KuzuDB Graph                                │
│    (Concept) --[IMPLEMENTS]--> (Symbol)             │
│                                                      │
│  STRENGTH: Code-level grounding, embedded DB        │
│  WEAKNESS: No code execution, no verification       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### What ULTRATHINK Skill Factory Does Well

```
┌─────────────────────────────────────────────────────┐
│            ULTRATHINK SKILL FACTORY                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  INPUT: Context7 API (15,000+ verified snippets)    │
│         + CodeWiki prose (for context)              │
│                                                      │
│  PROCESS:                                            │
│    1. Fetch real code from Context7                 │
│    2. Generate question grounded in AST symbols     │
│    3. Verify code runs in bubblewrap sandbox        │
│    4. Check semantic correctness (LLM eval)         │
│    5. Deduplicate and quality gate                  │
│                                                      │
│  OUTPUT: Verified Skills (JSON)                      │
│    {question, code, verified: true, source_url}     │
│                                                      │
│  STRENGTH: Execution proof, hallucination-free      │
│  WEAKNESS: No graph structure, file-based storage   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Integration Strategy: "The Unified Graph"

### Phase 1: Consolidate File Structure (Light Refactor)

```
/home/aig/sovereign_platform/
├── venv/                        # Unified Python 3.12 (from sovereign_venv)
├── data/
│   ├── kuzu_db                  # THE GRAPH
│   ├── context7_cache/          # Moved from new_crawl4AI
│   ├── codewiki/                # Ingested docs
│   └── scip_indexes/            # Code indexes
├── src/
│   ├── bridge/                  # Sovereign Bridge modules
│   │   ├── ingestors/           # GLiNER, SCIP parsers
│   │   ├── linkers/             # Fuzzy match logic
│   │   └── graph.py             # KuzuDB operations
│   ├── factory/                 # ULTRATHINK modules (from skills_factory)
│   │   ├── skill_generator.py
│   │   ├── verification_first.py
│   │   ├── glm_verifier.py
│   │   └── ...
│   └── unified/                 # NEW: Integration layer
│       ├── skill_to_graph.py    # Ingest verified skills into KuzuDB
│       └── query_engine.py      # Natural language → Graph query
├── scripts/
│   ├── run_bridge.py
│   ├── run_factory.py
│   └── run_unified.py
└── README.md
```

### Phase 2: Extend KuzuDB Schema

Current schema:

```cypher
(Concept) --[IMPLEMENTS]--> (Symbol)
```

Extended schema for skills:

```cypher
(Concept) --[IMPLEMENTS]--> (Symbol)
(Skill)   --[TEACHES]--> (Concept)
(Skill)   --[USES]--> (Symbol)
(Skill)   --[VERIFIED_BY]--> (TestResult)
```

New node types:

- **Skill**: A verified Q&A pair with executable code
- **TestResult**: Sandbox execution proof (stdout, exit_code, timestamp)

### Phase 3: Integration Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED SOVEREIGN PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────────────┐  │
│  │  CodeWiki   │      │  Context7   │      │      Git Repo           │  │
│  │   (Docs)    │      │   (Code)    │      │     (oh-my-opencode)    │  │
│  └──────┬──────┘      └──────┬──────┘      └───────────┬─────────────┘  │
│         │                    │                         │                 │
│         ▼                    ▼                         ▼                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     INGESTION LAYER                              │    │
│  │   GLiNER     +     Context7 Client     +     SCIP Parser        │    │
│  └─────────────────────────────┬───────────────────────────────────┘    │
│                                │                                         │
│                                ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     KuzuDB GRAPH                                 │    │
│  │                                                                  │    │
│  │   (Concept)──IMPLEMENTS──▶(Symbol)◀──USES──(Skill)              │    │
│  │       ▲                                        │                 │    │
│  │       └─────────TEACHES────────────────────────┘                 │    │
│  │                                                                  │    │
│  └─────────────────────────────┬───────────────────────────────────┘    │
│                                │                                         │
│                                ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     QUERY LAYER                                  │    │
│  │   "How do I use Context Window Limit Recovery?"                  │    │
│  │      ↓                                                           │    │
│  │   ContextWindowLimitRecovery (Symbol)                            │    │
│  │      ↓                                                           │    │
│  │   Verified Skill with working code example                       │    │
│  │      ↓                                                           │    │
│  │   + Exact file path: src/hooks/.../index.ts                      │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Integration Points

### 1. Skill → Graph Ingestion

The Skill Factory outputs JSON files. We need a translator:

```python
# skill_to_graph.py
def ingest_skill_to_kuzu(skill: dict, conn: kuzu.Connection):
    # Create Skill node
    conn.execute('''
        MERGE (s:Skill {
            id: $id,
            question: $question,
            code: $code,
            source_url: $source
        })
    ''', skill)
    
    # Link to concepts it teaches
    for concept in skill['concepts']:
        conn.execute('''
            MATCH (c:Concept {name: $concept})
            MERGE (s:Skill {id: $skill_id})-[:TEACHES]->(c)
        ''', {'skill_id': skill['id'], 'concept': concept})
```

### 2. Unified Query Engine

```python
# query_engine.py
def answer_question(question: str, conn: kuzu.Connection):
    # Step 1: Extract concepts from question (GLiNER)
    concepts = gliner.extract(question)
    
    # Step 2: Find related symbols and skills
    result = conn.execute('''
        MATCH (c:Concept)-[:IMPLEMENTS]->(sym:Symbol)
        WHERE c.name IN $concepts
        OPTIONAL MATCH (skill:Skill)-[:TEACHES]->(c)
        RETURN c.name, sym.file_path, skill.code
    ''', {'concepts': concepts})
    
    # Step 3: Return grounded answer
    return format_response(result)
```

---

## Implementation Effort

| Phase | Task | Effort |
|-------|------|--------|
| **Phase 1** | Consolidate directories | 30 min |
| **Phase 1** | Merge venvs | 15 min |
| **Phase 2** | Extend KuzuDB schema | 15 min |
| **Phase 2** | Write skill_to_graph.py | 30 min |
| **Phase 3** | Write unified query engine | 1 hour |
| **Phase 3** | Integration testing | 30 min |
| **Total** | | **~3 hours** |

---

## Recommendation

**Do the integration incrementally:**

1. **Today**: Light refactor - move files into unified structure
2. **Tomorrow**: Extend schema, ingest existing skills
3. **Day 3**: Build query engine, test end-to-end

The ULTRATHINK Skill Factory is powerful but scattered. The Sovereign Bridge is focused but limited. Together, they become a **Sovereign Intelligence Platform** that can:

- Answer: "What is Context Window Limit Recovery?" (from docs)
- Show: Exactly which file implements it (from graph)
- Provide: Verified, runnable code example (from skills)

---

## Open Questions for User

1. Should we prioritize depth (one library fully integrated) or breadth (all 13 libraries partially)?
2. Keep LangGraph orchestration or simplify to pure Python?
3. Use existing Context7 cache or refresh data?
