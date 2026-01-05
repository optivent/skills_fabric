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
