# BMAD Deep Investigation: Honest Gap Analysis

## C.O.R.E. Principle: "Discover through guided reflection, not assumptions"

**Date**: 2026-01-05  
**Investigator**: Following user's challenge to prove integration claims

---

## Executive Summary

| Claim | Reality | Status |
|-------|---------|--------|
| CodeWiki ↔ GitClone connected | 10/10 PROVEN links verified on disk | ✅ TRUE |
| All 20 Context7 files used | Only 3 files used, 17 ignored | ❌ FALSE |
| LSP integration | Not implemented | ❌ FALSE |
| AST analysis | Only syntax check, not real parsing | ⚠️ PARTIAL |
| Tree-sitter | Not used | ❌ FALSE |
| All concepts processed | Only 1 concept per run (LIMIT 1) | ❌ FALSE |
| Bubblewrap testing | Works, verified | ✅ TRUE |

---

## What's ACTUALLY Working

### ✅ Verified True

1. **CodeWiki → KuzuDB → GitClone**
   - 21 CodeWiki docs ingested → 824 Concepts
   - 10 PROVEN links created
   - **All 10 point to real files on disk** (100% verified)

2. **SCIP Index**
   - 7MB binary parsed
   - 3 Symbols extracted with file paths
   - Files exist in git clone

3. **Bubblewrap Sandbox**
   - v0.9.0 installed and working
   - Execution tested successfully

4. **GLM-4.7 Coding Plan**
   - Connected via v4 endpoint
   - Generates grounded questions

---

## What's NOT Working (Gaps)

### ❌ Context7: 17 of 20 Files Ignored

```python
# Current code in skill_factory_v2.py:
cache_files[:3]  # ← Only uses FIRST 3 files!
```

**Libraries NOT being used**:

- HuggingFace Transformers (2 files)
- OpenAI (2 files)
- Crawl4AI (1 file)
- LangChain (3 files)
- Pandas (1 file)
- Scikit-learn (1 file)
- 7 more Pydantic files

### ❌ Only 1 Concept Per Run

```python
# Current code in skill_factory_v2.py:
MATCH ... LIMIT 1  # ← Only one concept!
```

**Impact**: Each run creates 1 skill. With 10 PROVEN links, we'd need 10 separate runs.

### ❌ No LSP Integration

- Claimed but never implemented
- Would provide: type info, hover docs, goto definition
- Current state: Just reading raw files

### ⚠️ AST Only for Syntax Check

```python
# Current usage:
f.write(f'import ast\nast.parse("""{code}""")\nprint("SYNTAX_OK")')
```

**Reality**: Only checks if code parses, doesn't extract structure.  
**Should be**: Walking AST to find functions, classes, imports.

### ❌ No Tree-sitter

- Not imported, not used
- Would allow language-agnostic deep parsing
- Currently: Regex only

---

## The Real Picture

```
What We Claimed                  What We Have
─────────────────                ────────────────
20 Context7 files        →       3 files used
824 Concepts processed   →       1 per run
LSP + AST + Tree-sitter  →       Regex + SCIP
Full graph utilization   →       10 PROVEN links only
```

---

## Required Fixes

### Priority 1: Use ALL Context7 Files

```python
# Change:
for cache_file in cache_files[:3]:  # ← OLD
# To:
for cache_file in cache_files:  # ← NEW: All 20
```

### Priority 2: Process ALL PROVEN Concepts

```python
# Change:
MATCH ... LIMIT 1  # ← OLD
# To:
MATCH ... (no limit, iterate all)  # ← NEW
```

### Priority 3: Add Real AST Parsing

```python
import ast
tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Extract function info
```

### Priority 4: Add LSP (Optional Enhancement)

- Install pylsp
- Query for type info on symbols
- Enrich skill metadata

---

## Honest Status

| Component | Status | Gap |
|-----------|--------|-----|
| Data sources | ✅ All present | None |
| Ingestion | ✅ Working | None |
| KuzuDB | ✅ 824 concepts | Only 10 linked |
| Skill Factory | ⚠️ Works | Single-skill, 3-file limit |
| LLM | ✅ GLM-4.7 connected | None |
| Sandbox | ✅ Bubblewrap | None |
| AST/LSP | ❌ Not real | Major gap |

---

## Next Steps to Fix

1. [ ] Modify `enrich_with_context7` to use ALL 20 files
2. [ ] Add batch processing mode to generate skills for ALL PROVEN links
3. [ ] Implement real AST walking (not just syntax check)
4. [ ] (Optional) Add LSP for type enrichment
