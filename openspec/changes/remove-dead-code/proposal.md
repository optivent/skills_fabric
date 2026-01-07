# Proposal: Remove Dead Code

> OpenSpec Change Proposal
> ID: TASK-002 | Priority: P0 (Critical) | BMAD Track: Quick Flow

## Problem Statement

The codebase contains unused directories and duplicate code that confuses developers and increases maintenance burden.

## Current State

### Dead Directories Identified

```
older_project/           # ~30+ files, legacy code
src/skills_fabric/analyze_/  # Duplicate of analyze/
```

### Aspirational Integration Files

```
src/skills_fabric/integrations/ultimate_stack.py      # Blueprint, not functional
src/skills_fabric/integrations/unified_api.py         # Blueprint, not functional
src/skills_fabric/integrations/complete_architecture.py  # Blueprint, not functional
```

## Proposed Solution

1. Delete `older_project/` directory entirely
2. Review `analyze_/` vs `analyze/` - delete if duplicate
3. Review integration files - mark as aspirational or delete

## Acceptance Criteria

- [ ] `older_project/` deleted
- [ ] `analyze_/` consolidated or deleted
- [ ] Integration files reviewed and cleaned
- [ ] All imports still work after removal
- [ ] All tests pass
- [ ] No broken references

## Verification Steps

```bash
# After removal, verify:
python -c "import skills_fabric"  # Should work
pytest tests/ -x                   # All tests pass
ruff check src/                   # No import errors
```

## Risk Assessment

**Low Risk** - These directories are not imported by active code.

## Estimated Effort

2 story points (~2-4 hours)

## BMAD Agent

Architect Agent perspective - codebase hygiene.

---

*Proposal created from BMAD analysis. See `docs/bmad/agent-analysis.md` for details.*
