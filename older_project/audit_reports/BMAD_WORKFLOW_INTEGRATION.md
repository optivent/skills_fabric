# BMAD C.O.R.E. Workflow Integration

## Permanent Adoption for Sovereign Platform Development

**Source**: <https://github.com/oimiragieo/BMAD-SPEC-KIT>  
**Integrated**: 2026-01-05

---

## C.O.R.E. Principles (Always Apply)

| Principle | Meaning | My Commitment |
|-----------|---------|---------------|
| **C**ollaboration | Human-AI partnership | Always ask, never assume |
| **O**ptimized | Battle-tested processes | Use proven patterns, measure outcomes |
| **R**eflection | Strategic questioning | Challenge every claim, verify before proceeding |
| **E**ngine | Framework orchestration | Systematic execution, not ad-hoc |

---

## Four-Phase Methodology

### Phase 1: Analysis (Reflection First)

Before ANY implementation:

- [ ] What do we CLAIM to have?
- [ ] What do we ACTUALLY have? (Verify with queries/tests)
- [ ] What are the GAPS between claim and reality?
- [ ] Is the scope appropriate? (Quick Flow / BMad / Enterprise)

### Phase 2: Planning (Scale-Adaptive)

**Quick Flow Track** (< 1 hour work):

- Single file changes
- Bug fixes
- Direct implementation

**BMad Method Track** (1-8 hours work):

- Multiple files
- Architecture decisions needed
- Create implementation plan artifact

**Enterprise Track** (> 8 hours work):

- Full PRD/specification
- Security/compliance considerations
- Formal review gates

### Phase 3: Solutioning (Before Code)

- [ ] Architecture designed
- [ ] Edge cases considered
- [ ] Test cases defined
- [ ] Dependencies identified

### Phase 4: Implementation (Iterative)

- [ ] Story-centric development
- [ ] Just-in-time context loading
- [ ] Verify each step before proceeding
- [ ] No "LIMIT 1" shortcuts without explicit approval

---

## BMAD Checklist for Every Task

### Before Starting

```
□ Read the requirement completely
□ Identify what track this is (Quick/Method/Enterprise)
□ State what I believe exists vs verify it exists
□ If verification fails, STOP and report
```

### During Execution

```
□ No hardcoded limits ([:3], LIMIT 1) unless explicitly requested
□ All files, all concepts, all iterations
□ Test each component independently
□ Log actual counts/results, not assumptions
```

### After Completion

```
□ Run verification queries to confirm claims
□ Report honestly: what works, what doesn't
□ Document gaps for future work
□ Update task.md with accurate status
```

---

## Integration with Sovereign Platform

### Current Gaps to Fix (Phase 4: Implementation)

| Gap | BMAD Action | Priority |
|-----|-------------|----------|
| Only 3 Context7 files used | Remove [:3] limit, use all 20 | HIGH |
| Only 1 concept per run | Remove LIMIT 1, batch process | HIGH |
| AST is syntax-only | Implement real AST walking | MEDIUM |
| LSP not used | Add pylsp integration | LOW |

### Verification Protocol (C.O.R.E. Reflection)

After EVERY change, run:

```bash
# Count all entities
MATCH (n:Concept) RETURN count(n) AS concepts
MATCH (s:Symbol) RETURN count(s) AS symbols
MATCH (sk:Skill) RETURN count(sk) AS skills

# Verify relationships
MATCH ()-[r:PROVEN]->() RETURN count(r) AS proven
MATCH ()-[r:TEACHES]->() RETURN count(r) AS teaches
MATCH ()-[r:USES]->() RETURN count(r) AS uses

# Check file existence for ALL symbols
MATCH (s:Symbol) RETURN s.file_path
# Then: os.path.exists() for EACH one
```

---

## BMAD Applied to True Implementation

### Step 1: Fix Context7 (All 20 Files)

**Track**: Quick Flow  
**Verification**: Count code blocks extracted from EACH file

### Step 2: Fix Batch Processing (All PROVEN Links)

**Track**: BMad Method  
**Verification**: Skills created == PROVEN links count

### Step 3: Real AST Parsing

**Track**: BMad Method  
**Verification**: AST nodes extracted > regex extraction

### Step 4: LSP Integration (If Requested)

**Track**: Enterprise (optional)  
**Verification**: Type info available for symbols

---

## Commitment

From this point forward, I will:

1. **Never assume** - Always verify with queries/tests
2. **Never shortcut** - No arbitrary limits unless requested
3. **Always check** - Run verification after every change
4. **Report honestly** - Gaps are findings, not failures
