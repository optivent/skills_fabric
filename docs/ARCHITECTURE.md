# Skills Fabric Architecture

## Vision & Philosophy

### Zero-Hallucination Skill Generation

> "Compile the skill sheets directly from the source, not from summaries or
> interpretations. This is the only way to achieve zero-hallucination skills."

The core principle: **Never trust LLM output unless grounded in verified source code**.

---

## Trust Hierarchy (Miessler-Aligned PAI)

| Level | Content Type | Trust | Source |
|-------|-------------|-------|--------|
| **1** | HardContent | 100% | AST, SCIP, regex extraction - ZERO LLM |
| **2** | Verified Soft | 95% | LLM output grounded in Level 1, sandbox-tested |
| **3** | Unverified | 0% | Pure LLM - REJECTED, never used |

---

## BMAD C.O.R.E. Principles

| Principle | Meaning | Implementation |
|-----------|---------|----------------|
| **C**ollaboration | Human-AI partnership | Always ask, never assume |
| **O**ptimized | No arbitrary limits | ALL files, ALL concepts, ALL iterations |
| **R**eflection | Verify before proceed | Query/test every claim |
| **E**ngine | Systematic workflow | LangGraph orchestration |

### BMAD Checklist

**Before Starting:**
- [ ] Read requirement completely
- [ ] Verify what exists (dont assume)
- [ ] Stop if verification fails

**During Execution:**
- [ ] No hardcoded limits ([:3], LIMIT 1)
- [ ] Test each component independently
- [ ] Log actual counts, not assumptions

**After Completion:**
- [ ] Run verification queries
- [ ] Report honestly (gaps are findings)
- [ ] Update documentation

---

## Data Sources Integration

### 1. CodeWiki (Documentation)
- Markdown documentation scraped from official sources
- Split into concepts with content extraction
- Source of truth for WHAT things do

### 2. Git Clone (Reality)
- Actual source code repository
- SCIP index for compiler-grade symbols
- Source of truth for HOW things work

### 3. Context7 (Fresh Docs)
- Direct HTTP MCP API calls
- resolve-library-id + query-docs
- Up-to-date documentation with code examples

### 4. PROVEN Links (Bridge)
- 433+ verified links between docs and code
- 3-strategy matching: exact, filename, content
- Confidence scoring for quality control

---

## 7-Node LangGraph Pipeline

```
START
  │
  ▼
┌─────────────┐
│   INGEST    │ Clone repo, list source files
└──────┬──────┘
       ▼
┌─────────────┐
│   ANALYZE   │ AST + Tree-sitter symbol extraction
└──────┬──────┘
       ▼
┌─────────────┐
│    LINK     │ Create PROVEN relationships
└──────┬──────┘
       ▼
┌─────────────┐
│   ENRICH    │ Fetch Context7 documentation
└──────┬──────┘
       ▼
┌─────────────┐
│  GENERATE   │ GLM-4.7 question generation
└──────┬──────┘
       ▼
┌─────────────┐
│   VERIFY    │ Bubblewrap sandbox execution
└──────┬──────┘
       ▼
┌─────────────┐
│    STORE    │ KuzuDB with TEACHES/USES links
└──────┬──────┘
       ▼
     END
```

---

## Key Technical Decisions

### Multi-Language Support
- **Python**: Native AST module
- **TypeScript**: Tree-sitter parser
- **Any language**: Tree-sitter extensible

### Context7 Direct API
```python
# Bypass interactive session requirement
POST https://mcp.context7.com/mcp
{
  "method": "tools/call",
  "params": {"name": "query-docs", "arguments": {...}}
}
```

### Bubblewrap Sandbox
```bash
bwrap --ro-bind / / --unshare-net -- python3 code.py
```
Isolates code execution: read-only filesystem, no network.

### KuzuDB Graph Schema
```cypher
Concept -[:PROVEN]-> Symbol
Skill -[:TEACHES]-> Concept
Skill -[:USES]-> Symbol
Skill -[:VERIFIED_BY]-> TestResult
```

---

## User Wishes Implemented

1. ✅ **Full resource utilization** - No arbitrary limits on files/concepts
2. ✅ **Context7 integration** - Direct HTTP API, not MCP session
3. ✅ **PROVEN linking** - 433+ verified doc-to-code connections
4. ✅ **Tree-sitter AST** - Real parsing, not regex
5. ✅ **GLiNER NER** - Named entity extraction for concepts
6. ✅ **Bubblewrap sandbox** - Safe code execution
7. ✅ **LangGraph orchestration** - 7-node stateful pipeline
8. ✅ **KuzuDB storage** - Graph relationships (TEACHES, USES)
9. ✅ **BMAD C.O.R.E.** - Systematic verification workflow
10. ✅ **Trust hierarchy** - Miessler-aligned PAI principles
11. ✅ **Zero hallucination** - Grounded in source, not summaries

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/optivent/skills_fabric
cd skills_fabric
pip install -e .

# Initialize database
python scripts/setup_db.py

# Clone a target repo
python -c "from skills_fabric.ingest.gitclone import GitCloner; GitCloner().clone(\"https://github.com/langchain-ai/langgraph\")"

# Generate skills
python scripts/generate_skills.py --repo langgraph
```

---

## Kit-Spec Methodology

### Source: BMAD-SPEC-KIT

The kit-spec methodology is a **spec-driven development** approach from the BMAD framework. Instead of jumping to implementation, you first define clear specifications.

### Core Principle

> "Specifications are the contract between what you want and what you build.
> Without specs, you are building based on assumptions."

### The Flow

```
┌─────────────┐
│    SPEC     │ Define what success looks like
└──────┬──────┘
       ▼
┌─────────────┐
│   STORIES   │ Break into user-facing stories
└──────┬──────┘
       ▼
┌─────────────┐
│    BUILD    │ Implement story by story
└──────┬──────┘
       ▼
┌─────────────┐
│   VERIFY    │ Check against original spec
└─────────────┘
```

### Applied to Skills Fabric

**SPEC (What we need):**
- Generate Claude skills from source code
- Zero hallucination: grounded in verified source
- Multi-language: Python, TypeScript, any Tree-sitter lang
- Graph storage: relationships between concepts/symbols/skills

**STORIES (User-facing units):**
1. As a developer, I can ingest a GitHub repository
2. As a developer, I can link documentation to source code
3. As a developer, I can generate skills with grounded questions
4. As a developer, I can verify skills execute correctly
5. As a developer, I can query my skill library

**BUILD (Implementation):**
- `ingest/gitclone.py` → Story 1
- `link/proven_linker.py` → Story 2
- `generate/skill_factory.py` → Story 3
- `verify/sandbox.py` → Story 4
- `store/kuzu_store.py` → Story 5

**VERIFY (Check against spec):**
- 48/48 tests pass
- 433 PROVEN links verified
- Real API calls (Context7, GLM-4.7)
- Bubblewrap sandbox works

### Kit-Spec in Practice

**When adding a new feature:**

1. **Write the spec first:**
   ```markdown
   ## Feature: Add LSP Integration
   
   ### Goal
   Get type information for symbols via Language Server Protocol.
   
   ### Success Criteria
   - [ ] LSP server starts for Python/TypeScript
   - [ ] Can query hover info for symbols
   - [ ] Type information stored in Symbol nodes
   ```

2. **Define the stories:**
   ```markdown
   - As a developer, I can start an LSP server for a project
   - As a developer, I can get type info for a function
   ```

3. **Then implement:**
   ```python
   # analyze/lsp_client.py
   class LSPClient:
       def start_server(self, project_path): ...
       def get_hover(self, file, line, col): ...
   ```

4. **Verify against spec:**
   ```python
   def test_lsp_integration():
       client = LSPClient()
       client.start_server(project)
       info = client.get_hover("main.py", 10, 5)
       assert info.type is not None
   ```

### The Key Insight

> "Never write code until you can describe, in plain language,
> what success looks like and how you will verify it."

---

## Hybrid Kit-Spec + BMAD Methodology

### The Synthesis

Kit-Spec and BMAD are complementary:
- **Kit-Spec** = WHAT to build (spec-driven planning)
- **BMAD C.O.R.E.** = HOW to build (execution principles)

### Unified Flow

```
┌────────────────────────────────────────────────────────────┐
│                    HYBRID METHODOLOGY                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 1: SPEC (Kit-Spec + BMAD Reflection)          │   │
│  │                                                      │   │
│  │ 1. Define success criteria                           │   │
│  │ 2. BMAD: What do we CLAIM to need?                  │   │
│  │ 3. BMAD: What do we ACTUALLY need? (verify scope)   │   │
│  │ 4. Identify gaps between claim and reality          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 2: STORIES (Kit-Spec + BMAD Collaboration)    │   │
│  │                                                      │   │
│  │ 1. Break spec into user-facing stories               │   │
│  │ 2. BMAD: Ask user to prioritize/clarify             │   │
│  │ 3. BMAD: Never assume, always confirm                │   │
│  │ 4. Size each story (Quick/Method/Enterprise)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 3: BUILD (Kit-Spec + BMAD Optimized Engine)   │   │
│  │                                                      │   │
│  │ 1. Implement story by story                          │   │
│  │ 2. BMAD: No arbitrary limits (all files, concepts)  │   │
│  │ 3. BMAD: Test each component independently          │   │
│  │ 4. BMAD: Log actual results, not assumptions        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PHASE 4: VERIFY (Kit-Spec + BMAD Reflection)        │   │
│  │                                                      │   │
│  │ 1. Check implementation against spec                 │   │
│  │ 2. BMAD: Run verification queries                   │   │
│  │ 3. BMAD: Report honestly (gaps are findings)        │   │
│  │ 4. BMAD: Document what works AND what doesnt        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### The Integration Matrix

| Phase | Kit-Spec Focus | BMAD Principle |
|-------|---------------|----------------|
| SPEC | Define success | **Reflection**: Verify claims vs reality |
| STORIES | User-facing units | **Collaboration**: Ask, dont assume |
| BUILD | Implementation | **Optimized**: No limits, battle-tested |
| VERIFY | Check against spec | **Engine**: Systematic verification |

### Practical Example: Adding a New Data Source

**SPEC Phase:**
```markdown
Goal: Add Reddit API as data source for Skills Fabric

Success Criteria:
- [ ] Can fetch top posts from subreddits
- [ ] Can extract code snippets from posts
- [ ] Code integrated into existing pipeline

BMAD Reflection:
- Claim: "We need Reddit for more examples"
- Verify: Do we have enough examples already? (Check Context7 count)
- Gap: Context7 has 2379 snippets, Reddit might add noise
- Decision: Continue only if curated subreddits (r/Python, r/typescript)
```

**STORIES Phase:**
```markdown
Stories (with BMAD sizing):
1. As a dev, I can authenticate with Reddit API (Quick Flow)
2. As a dev, I can fetch posts from a subreddit (Quick Flow)
3. As a dev, I can extract code blocks from posts (Method)
4. As a dev, I can store Reddit content as Concepts (Method)

BMAD Collaboration:
→ Ask user: "Which subreddits should we prioritize?"
→ Never assume which communities have valuable content
```

**BUILD Phase:**
```python
# ingest/reddit.py (BMAD: No limits)

class RedditClient:
    def fetch_posts(self, subreddit: str, limit: int = 100):
        # BMAD: Use ALL posts up to limit, not [:3]
        posts = self._api.get(f"/r/{subreddit}/top", limit=limit)
        return posts  # All of them
    
    def extract_code(self, posts: list) -> list:
        # BMAD: Process ALL posts, log actual count
        code_blocks = []
        for post in posts:
            blocks = self._find_code_blocks(post.text)
            code_blocks.extend(blocks)
        
        print(f"[Reddit] Extracted {len(code_blocks)} code blocks")
        return code_blocks
```

**VERIFY Phase:**
```python
# BMAD: Run actual verification queries
def test_reddit_integration():
    client = RedditClient()
    posts = client.fetch_posts("Python", limit=10)
    
    # BMAD: Report honestly
    assert len(posts) == 10, f"Expected 10, got {len(posts)}"
    
    code = client.extract_code(posts)
    print(f"Result: {len(code)} code blocks from {len(posts)} posts")
    
    # BMAD: Document gaps
    if len(code) < 5:
        print("WARNING: Low code extraction rate")
```

### The Hybrid Commitment

1. **Start with spec** (Kit-Spec) + **verify scope** (BMAD Reflection)
2. **Define stories** (Kit-Spec) + **confirm with user** (BMAD Collaboration)
3. **Build without limits** (Kit-Spec stories) + **test each part** (BMAD Optimized)
4. **Verify against spec** (Kit-Spec) + **report honestly** (BMAD Engine)

> "The hybrid approach ensures you build the RIGHT thing (Kit-Spec)
> in the RIGHT way (BMAD) with HONEST reporting (both)."
