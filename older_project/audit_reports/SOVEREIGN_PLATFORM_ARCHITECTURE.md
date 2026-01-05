# Sovereign Platform: Complete Architecture Diagram

## Full System Overview

```mermaid
flowchart TB
    subgraph SOURCES["📥 DATA SOURCES"]
        CW["📄 CodeWiki<br/>21 markdown docs"]
        GIT["💾 Git Clone<br/>oh-my-opencode repo"]
        C7["🌐 Context7<br/>20 JSON cache files"]
        SCIP["🔍 SCIP Index<br/>7MB symbol index"]
    end

    subgraph INGESTION["⚙️ INGESTION LAYER"]
        SB["sovereign_bridge.py<br/>GLiNER + SCIP parser"]
        SV["structural_verifier.py<br/>Path extraction + verification"]
    end

    subgraph GRAPH["🗄️ KNOWLEDGE GRAPH (KuzuDB)"]
        subgraph NODES["Nodes"]
            CONCEPT["Concept<br/>824 nodes"]
            SYMBOL["Symbol<br/>3 nodes"]
            SKILL["Skill<br/>3 nodes"]
            TEST["TestResult<br/>2 nodes"]
        end
        subgraph RELS["Relationships"]
            IMPL["IMPLEMENTS<br/>2 links"]
            PROV["PROVEN<br/>10 links"]
            TEACH["TEACHES<br/>6 links"]
            USES["USES<br/>1 link"]
            VERBY["VERIFIED_BY<br/>1 link"]
        end
    end

    subgraph FACTORY["🏭 SKILL FACTORY V2 (LangGraph)"]
        N1["1. QueryKuzuConcepts"]
        N2["2. ReadSourceCode"]
        N3["3. EnrichWithContext7"]
        N4["4. ExtractHardContent"]
        N5["5. GenerateQuestion<br/>(GLM-4.7 Coding Plan)"]
        N6["6. VerifyGrounding"]
        N7["7. ExecuteSandbox<br/>(Bubblewrap)"]
        N8["8. StoreSkill"]
    end

    subgraph OUTPUT["📤 OUTPUT"]
        SKILLS["Claude Skills<br/>Grounded, Verified"]
        QUERY["Query Engine<br/>Natural Language → Code"]
    end

    %% Data flow
    CW --> SB
    GIT --> SB
    SCIP --> SB
    CW --> SV
    GIT --> SV
    C7 --> N3

    SB --> CONCEPT
    SB --> SYMBOL
    SV --> PROV

    CONCEPT --> N1
    SYMBOL --> N2
    
    N1 --> N2 --> N3 --> N4 --> N5 --> N6 --> N7 --> N8
    
    N8 --> SKILL
    N8 --> TEACH
    N8 --> USES
    N8 --> VERBY

    SKILL --> SKILLS
    CONCEPT --> QUERY
    SYMBOL --> QUERY

    %% Styling
    classDef source fill:#e1f5fe,stroke:#01579b
    classDef ingest fill:#fff3e0,stroke:#e65100
    classDef graph fill:#f3e5f5,stroke:#7b1fa2
    classDef factory fill:#e8f5e9,stroke:#2e7d32
    classDef output fill:#fce4ec,stroke:#c2185b

    class CW,GIT,C7,SCIP source
    class SB,SV ingest
    class CONCEPT,SYMBOL,SKILL,TEST,IMPL,PROV,TEACH,USES,VERBY graph
    class N1,N2,N3,N4,N5,N6,N7,N8 factory
    class SKILLS,QUERY output
```

---

## Layer-by-Layer Breakdown

### Layer 1: Data Sources

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                  │
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│   CodeWiki   │   Git Clone  │   Context7   │      SCIP Index        │
│   21 docs    │ oh-my-opencode│  20 JSON     │      7MB binary        │
│   (Markdown) │   (TypeScript)│  (API cache) │   (Compiler symbols)   │
└──────────────┴──────────────┴──────────────┴────────────────────────┘
```

### Layer 2: Ingestion

```
┌──────────────────────────────────────────────────────────────────────┐
│                       INGESTION PIPELINE                              │
├─────────────────────────────┬────────────────────────────────────────┤
│    sovereign_bridge.py      │      structural_verifier.py            │
│    ─────────────────────    │      ────────────────────────          │
│    • GLiNER NER extraction  │      • GitHub path extraction          │
│    • SCIP symbol parsing    │      • File existence verification     │
│    • Concept creation       │      • PROVEN link creation            │
│    • Symbol creation        │      • 264 files verified              │
└─────────────────────────────┴────────────────────────────────────────┘
```

### Layer 3: Knowledge Graph (KuzuDB)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         KUZU GRAPH DB                                 │
│                                                                       │
│   ┌─────────┐                                      ┌─────────┐       │
│   │ Concept │──────IMPLEMENTS (2)─────────────────▶│ Symbol  │       │
│   │   824   │                                      │    3    │       │
│   └────┬────┘                                      └────┬────┘       │
│        │                                                │            │
│        │ PROVEN (10)                                    │            │
│        └────────────────────────────────────────────────┘            │
│                                                                       │
│   ┌─────────┐     TEACHES (6)      ┌─────────────┐                   │
│   │  Skill  │◀─────────────────────│   Concept   │                   │
│   │    3    │                      └─────────────┘                   │
│   └────┬────┘                                                        │
│        │ USES (1)           VERIFIED_BY (1)                          │
│        ▼                           ▼                                 │
│   ┌─────────┐              ┌─────────────┐                           │
│   │ Symbol  │              │ TestResult  │                           │
│   └─────────┘              │     2       │                           │
│                            └─────────────┘                           │
└──────────────────────────────────────────────────────────────────────┘
```

### Layer 4: Skill Factory V2 (LangGraph Pipeline)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    SKILL FACTORY V2 PIPELINE                          │
│                                                                       │
│   START                                                               │
│     │                                                                 │
│     ▼                                                                 │
│   ┌─────────────────────┐                                            │
│   │ 1. QueryKuzuConcepts│ ← Query Concepts with PROVEN links         │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 2. ReadSourceCode   │ ← Read actual file from Git clone         │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 3. EnrichWithContext7│ ← Add examples from API cache            │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 4. ExtractHardContent│ ← AST/Regex (0% LLM, 100% trust)         │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 5. GenerateQuestion │ ← GLM-4.7 Coding Plan (v4 endpoint)       │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 6. VerifyGrounding  │ ← Check question references real concepts │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 7. ExecuteSandbox   │ ← Bubblewrap v0.9.0 isolation             │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│   ┌─────────────────────┐                                            │
│   │ 8. StoreSkill       │ ← KuzuDB + TEACHES + USES links           │
│   └──────────┬──────────┘                                            │
│              ▼                                                        │
│     END                                                               │
└──────────────────────────────────────────────────────────────────────┘
```

### Layer 5: Trust Hierarchy (Miessler-Aligned)

```
┌──────────────────────────────────────────────────────────────────────┐
│                       TRUST HIERARCHY                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Level 1: HardContent (100% Trust)                                  │
│   ─────────────────────────────────                                  │
│   • AST-extracted imports                                            │
│   • Regex-extracted API calls                                        │
│   • File paths from SCIP index                                       │
│   • ZERO LLM = ZERO hallucination                                    │
│                                                                       │
│   Level 2: Verified Soft (95% Trust)                                 │
│   ────────────────────────────────                                   │
│   • LLM-generated questions                                          │
│   • Grounded in Level 1 concepts                                     │
│   • Verified via sandbox execution                                   │
│                                                                       │
│   Level 3: Unverified Soft (0% Trust) ← REJECTED                     │
│   ─────────────────────────────────────                              │
│   • Pure LLM output                                                  │
│   • Not used in skills                                               │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## File Locations on `core` VM

| Component | Path |
|-----------|------|
| **Skill Factory V2** | `~/sovereign_platform/src/factory/skill_factory_v2.py` |
| **KuzuDB Store** | `~/sovereign_platform/src/unified/kuzu_skill_store.py` |
| **Sovereign Bridge** | `~/sovereign_platform/src/bridge/sovereign_bridge.py` |
| **Structural Verifier** | `~/sovereign_platform/scripts/structural_verifier.py` |
| **E2E Test** | `~/sovereign_platform/scripts/e2e_test.py` |
| **KuzuDB Data** | `~/sovereign_platform/data/kuzu_db/` |
| **CodeWiki** | `~/sovereign_platform/data/codewiki/` |
| **Git Clone** | `~/sovereign_platform/data/oh-my-opencode/` |
| **Context7 Cache** | `~/sovereign_platform/data/context7_cache/` |
