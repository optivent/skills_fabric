# BMAD-Grade Integration Audit Plan

## Sovereign Platform: Full Pipeline Verification

**Framework**: BMAD C.O.R.E. (Collaboration, Optimized, Reflection, Engine)  
**Date**: 2026-01-05  
**Principle**: "Discover through guided reflection, not assumptions"

---

## C.O.R.E. Application to This Audit

| Principle | Application |
|-----------|-------------|
| **Collaboration** | Human verification of each finding |
| **Optimized** | Test each layer independently, then together |
| **Reflection** | Question every assumption, verify every claim |
| **Engine** | Systematic validation framework |

---

## Audit Scope: What Claims Must Be Verified

### Layer 1: Data Sources (Do They Exist?)

| Source | Claimed Path | Test |
|--------|--------------|------|
| CodeWiki | `~/sovereign_platform/data/codewiki/` | File count, sample content |
| Git Clone | `~/sovereign_platform/data/oh-my-opencode/` | Is it a git repo? File count? |
| Context7 | `~/sovereign_platform/data/context7_cache/` | JSON validity, code blocks |
| SCIP Index | `~/sovereign_platform/data/oh-my-opencode/index.scip` | Exists? Parseable? |

### Layer 2: Ingestion (Is Data In KuzuDB?)

| Data Type | Claimed Count | Test Query |
|-----------|---------------|------------|
| Concepts | 824 | `MATCH (c:Concept) RETURN count(c)` |
| Symbols | 3 | `MATCH (s:Symbol) RETURN count(s)` |
| Skills | 1 | `MATCH (sk:Skill) RETURN count(sk)` |
| PROVEN Links | 10 | `MATCH ()-[r:PROVEN]->() RETURN count(r)` |

### Layer 3: Links (Are They Real?)

| Link Type | Test | Expected |
|-----------|------|----------|
| PROVEN | Does Symbol file exist on disk? | 100% should exist |
| IMPLEMENTS | Does Concept text mention Symbol name? | Check manually |

### Layer 4: Pipeline (Does Code Actually Run?)

| Component | Test | Expected |
|-----------|------|----------|
| `sovereign_bridge.py` | Execute, check output | Should complete |
| `structural_verifier.py` | Execute, check PROVEN count | Should be >= 10 |
| `skill_factory.py` | Build graph, print nodes | Should have 6 nodes |
| `kuzu_skill_store.py` | Run QA tests | 9/9 pass |
| `e2e_test.py` | Full run | Complete successfully |

### Layer 5: Integration (Are Components Connected?)

| From | To | Link Method | Test |
|------|----|-----------|----|
| CodeWiki docs | KuzuDB Concepts | `sovereign_bridge.py` | Query concepts by doc name |
| Git clone files | KuzuDB Symbols | `sovereign_bridge.py` | Query symbols by file path |
| Concepts | Symbols | PROVEN relationship | Count, sample |
| Skill Factory | KuzuDB | `kuzu_skill_store.py` | Create skill, verify exists |
| Skill Factory | CodeWiki | ❓ MISSING | This is the gap |
| Skill Factory | Git Clone | ❓ MISSING | This is the gap |

---

## Audit Execution Plan

### Phase A: Filesystem Verification (No Code)

```bash
# A1: CodeWiki exists and has content
ls -la ~/sovereign_platform/data/codewiki/
head -20 ~/sovereign_platform/data/codewiki/00_introduction.md

# A2: Git clone is a valid repo
cd ~/sovereign_platform/data/oh-my-opencode && git log --oneline -5

# A3: Context7 cache has valid JSON
cat ~/sovereign_platform/data/context7_cache/*.json | jq '.' | head -50

# A4: SCIP index exists
ls -la ~/sovereign_platform/data/oh-my-opencode/index.scip
```

### Phase B: KuzuDB Verification (Query-Only)

```python
# B1: Count all node types
# B2: Sample 5 concepts and verify they reference CodeWiki
# B3: Sample 5 symbols and verify file paths exist
# B4: Sample 5 PROVEN links and verify both ends
```

### Phase C: Component Execution (Run Each Script)

```bash
# C1: sovereign_bridge.py
# C2: structural_verifier.py  
# C3: skill_factory.py
# C4: kuzu_skill_store.py tests
# C5: e2e_test.py
```

### Phase D: Integration Verification (End-to-End)

```python
# D1: Can we query a Concept and find its source CodeWiki doc?
# D2: Can we query a Symbol and read its actual source code?
# D3: Can we traverse Concept -> PROVEN -> Symbol -> Source Code?
# D4: Does Skill Factory use any of the above? (THE GAP)
```

---

## Expected Findings

Based on prior investigation:

1. **Layers 1-3**: Likely working (data exists, ingested, linked)
2. **Layer 4**: Components run independently
3. **Layer 5**: **THE GAP** - Skill Factory does NOT integrate with:
   - CodeWiki concepts
   - Git clone source code
   - PROVEN links

---

## Success Criteria

| Criterion | Threshold | Current State |
|-----------|-----------|---------------|
| All data sources accessible | 4/4 | ❓ Untested |
| All node types populated | 4/4 | ❓ Untested |
| PROVEN links point to real files | 100% | ❓ Untested |
| All scripts execute without error | 5/5 | ❓ Untested |
| Skill Factory uses CodeWiki | Yes | ❌ Known gap |
| Skill Factory uses Git Clone | Yes | ❌ Known gap |
| E2E: Skill references PROVEN Symbol | Yes | ❌ Not implemented |

---

## Post-Audit Action

If gaps confirmed:

1. Redesign Skill Factory to query KuzuDB for Concepts
2. Add node to read source code from Git clone
3. Verify skill questions reference real Concepts
4. Store skills with TEACHES relationships to Concepts
