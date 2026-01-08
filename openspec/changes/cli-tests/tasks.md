# Tasks: Add CLI Test Suite

> OpenSpec Task Breakdown
> Proposal: cli-tests | Status: Ready

## Task List

### Setup

- [ ] Create `tests/test_cli.py` file
- [ ] Add Click testing utilities (CliRunner)
- [ ] Create test fixtures for mock data

### Generate Command Tests

- [ ] Test `generate <library>` with valid library
- [ ] Test `generate` without library (error case)
- [ ] Test `generate --depth` with valid depths (0-5)
- [ ] Test `generate --depth` with invalid depth
- [ ] Test `generate --json` output format
- [ ] Test `generate --quiet` flag
- [ ] Test `generate --factory` mode

### Verify Command Tests

- [ ] Test `verify <query>` with valid query
- [ ] Test `verify` without query (error case)
- [ ] Test `verify --codewiki` with path
- [ ] Test `verify --json` output format
- [ ] Test `verify --strict` mode
- [ ] Test `verify --show-metrics` flag

### Analyze Command Tests

- [ ] Test `analyze <file>` with Python file
- [ ] Test `analyze <file>` with TypeScript file
- [ ] Test `analyze <dir> --directory` mode
- [ ] Test `analyze` with nonexistent path (error case)
- [ ] Test `analyze --json` output format
- [ ] Test `analyze --analyzer ast` mode
- [ ] Test `analyze --analyzer tree-sitter` mode

### Research Command Tests

- [ ] Test `research <query>` basic usage
- [ ] Test `research --iterative` mode
- [ ] Test `research --json` output format

### Search Command Tests

- [ ] Test `search <query>` basic usage
- [ ] Test `search --technical` filter
- [ ] Test `search --academic` filter
- [ ] Test `search --freshness` options
- [ ] Test `search --json` output format

### Version Command Tests

- [ ] Test `version` output
- [ ] Test `version --json` output format

### Error Handling Tests

- [ ] Test unknown command
- [ ] Test help output (`--help`)
- [ ] Test global `--quiet` and `--verbose` flags

## Verification

```bash
# Run tests
pytest tests/test_cli.py -v

# Check coverage
pytest tests/test_cli.py --cov=src/skills_fabric/__main__ --cov-report=term-missing
```

## Definition of Done

- All tests pass
- Coverage > 80%
- No new linting errors
- PR approved
