# Proposal: Add CLI Test Suite

> OpenSpec Change Proposal
> ID: TASK-001 | Priority: P0 (Critical) | BMAD Track: BMad Method

## Problem Statement

The CLI entry point (`src/skills_fabric/__main__.py`) has **1,125 lines of code with 0 tests**. This is a critical gap that prevents safe refactoring and modification of the CLI.

## Current State

```
File: src/skills_fabric/__main__.py
Lines: 1,125
Tests: 0
Coverage: 0%
```

The CLI provides 6 commands:
- `generate` - Skill generation
- `verify` - Symbol verification
- `analyze` - Source analysis
- `research` - Perplexity research
- `search` - Brave search
- `version` - Version info

## Proposed Solution

Create a comprehensive test suite covering all CLI commands with:
- Happy path tests for each command
- Error handling tests (missing args, invalid input)
- Output format tests (JSON mode, quiet mode, verbose mode)
- Integration tests with mock data

## Acceptance Criteria

- [ ] All 6 commands have unit tests
- [ ] Error cases tested (missing required args, invalid paths)
- [ ] JSON output mode tested for applicable commands
- [ ] Verbose/quiet flags tested
- [ ] Coverage > 80% for `__main__.py`
- [ ] Tests pass in CI

## Files to Create

```
tests/
├── test_cli.py              # Unit tests for each command
└── test_cli_integration.py  # End-to-end CLI tests
```

## Test Count Target

**30+ tests** covering:
- 6 commands × 3 scenarios (success, error, edge case) = 18 base tests
- Output format variations = 6 tests
- Flag combinations = 6+ tests

## Dependencies

None - can be implemented immediately.

## Estimated Effort

5 story points (~1-2 days)

## BMAD Agent

QA Agent perspective - test coverage is critical quality gate.

---

*Proposal created from BMAD analysis. See `docs/bmad/tasks.md` for full context.*
