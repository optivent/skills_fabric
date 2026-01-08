# Tasks: Remove Dead Code

> OpenSpec Task Breakdown
> Proposal: remove-dead-code | Status: Ready

## Task List

### Analysis Phase

- [ ] Verify `older_project/` has no active imports
- [ ] Compare `analyze_/` vs `analyze/` for differences
- [ ] Check if integration files are imported anywhere

### Removal Phase

- [ ] Delete `older_project/` directory
- [ ] Delete or merge `analyze_/` directory
- [ ] Review each integration file:
  - [ ] `ultimate_stack.py` - delete or mark TODO
  - [ ] `unified_api.py` - delete or mark TODO
  - [ ] `complete_architecture.py` - delete or mark TODO

### Verification Phase

- [ ] Run `python -c "import skills_fabric"`
- [ ] Run `pytest tests/ -x`
- [ ] Run `ruff check src/`
- [ ] Verify no broken imports in any file

### Cleanup Phase

- [ ] Update `__init__.py` exports if needed
- [ ] Update any documentation references
- [ ] Commit with descriptive message

## Commands

```bash
# Check for imports before deletion
grep -r "older_project" src/
grep -r "analyze_" src/ --include="*.py"

# Delete directories
rm -rf older_project/
rm -rf src/skills_fabric/analyze_/

# Verify
python -c "import skills_fabric; print('OK')"
pytest tests/ -x
```

## Definition of Done

- Dead code removed
- All tests pass
- No import errors
- Commit pushed
