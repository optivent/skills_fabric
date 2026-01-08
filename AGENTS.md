# Skills Fabric - AI Agent Instructions

> Instructions for AI coding assistants (Claude Code, Cursor, Copilot, etc.)

## OpenSpec Integration

This project uses **OpenSpec** for spec-driven development. Before implementing features, ensure specifications are agreed upon.

### OpenSpec Commands

```bash
# View active changes
openspec list

# Show a specific change
openspec show <change-name>

# Validate change format
openspec validate <change-name>

# Archive completed change
openspec archive <change-name>
```

### Slash Commands (Claude Code, Cursor)

- `/openspec:proposal` - Create new change proposal
- `/openspec:apply` - Implement from specification
- `/openspec:archive` - Archive completed change

## Project Structure

```
openspec/
├── specs/           # Living specifications (source of truth)
│   └── core/        # Core system specs
└── changes/         # Active change proposals
    ├── cli-tests/   # TASK-001: Add CLI tests
    ├── remove-dead-code/  # TASK-002: Clean up
    └── thread-safety/     # TASK-003: Fix concurrency

docs/
├── bmad/            # BMAD v6 analysis (strategy)
│   ├── agent-analysis.md
│   ├── improvement-roadmap.md
│   └── tasks.md
└── speckit/         # SpecKit artifacts (principles)
    ├── constitution.md
    └── specification.md
```

## Development Workflow

### For New Features

1. Check `openspec/changes/` for existing proposals
2. If none exists, create proposal with `/openspec:proposal`
3. Implement according to specification
4. Archive with `/openspec:archive`

### For Bug Fixes

1. Quick fixes: Implement directly
2. Complex fixes: Create OpenSpec proposal first

## Code Quality Requirements

### From Constitution (docs/speckit/constitution.md)

- **Hall_m < 0.02**: Every claim needs `file:line` citation
- **Multi-source validation**: >= 2 sources for high confidence
- **Graceful degradation**: LSP → AST → Tree-sitter fallback
- **Type hints required**: All public functions
- **Tests required**: 80% coverage target

### Linting

```bash
ruff check src/
mypy src/skills_fabric
```

### Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src/skills_fabric
```

## Priority Tasks (P0)

See `openspec/changes/` for current priorities:

1. **cli-tests**: Add test suite for `__main__.py`
2. **remove-dead-code**: Clean up `older_project/`, `analyze_/`
3. **thread-safety**: Fix global `hall_metric` concurrency issue

## BMAD Tracks

When selecting work approach:

- **Quick Flow** (< 5 min): Bug fixes, small patches
- **BMad Method** (< 15 min): New features
- **Enterprise** (< 30 min): Large refactors

## Do Not

- Commit without running tests
- Skip Hall_m verification for generated content
- Use global state for concurrent operations
- Add features without specifications

## References

- [OpenSpec Docs](https://github.com/Fission-AI/OpenSpec)
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)
- [SpecKit](https://github.com/github/spec-kit)
