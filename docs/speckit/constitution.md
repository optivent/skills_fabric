# Skills Fabric - Project Constitution

> SpecKit Constitution Document - Non-Negotiable Principles
> Version: 1.0.0 | Created: 2026-01-07

## Mission Statement

Skills Fabric generates **zero-hallucination Claude skills** from real source code with verifiable citations. Every claim must be traceable to a `file:line` reference in actual source code.

---

## Non-Negotiable Principles

### 1. Zero Hallucination Guarantee (Hall_m < 0.02)

```
PRINCIPLE: Never trust LLM output unless grounded in verified source code.
METRIC: Hall_m = rejected / (validated + rejected) MUST BE < 0.02 (2%)
ENFORCEMENT: HallMetricExceededException raised when threshold exceeded
```

**Requirements:**
- Every code reference MUST have a `file:line` citation
- Every symbol MUST be validated against actual source via multi-source verification
- Unverified content is REJECTED, not downgraded

### 2. Trust Hierarchy (Miessler-Aligned PAI Framework)

```
Level 1: HardContent (100% trust)
  - AST parsing verification
  - SCIP symbol indexing
  - Regex extraction from source

Level 2: VerifiedSoft (95% trust)
  - LLM output + sandbox execution passes
  - Grounding checks against documentation

Level 3: Unverified (0% trust - REJECTED)
  - Pure LLM hallucinations
  - Content without source references
```

**Requirements:**
- All generated skills MUST achieve Level 1 or Level 2 trust
- Level 3 content MUST trigger HallucinationError
- Trust level MUST be explicitly recorded on every skill

### 3. Multi-Source Validation

```
PRINCIPLE: Single-source validation is insufficient.
REQUIREMENT: >= 2 independent sources must confirm a symbol.
SOURCES: AST, Tree-sitter, LSP, File Content, Symbol Catalog
```

**Requirements:**
- ValidationResult.confidence requires multiple sources
- High-confidence threshold: >= 2 sources agreeing
- Single-source results flagged with lower confidence score

### 4. Graceful Degradation

```
PRINCIPLE: The system MUST always work, even in constrained environments.
PATTERN: LSP → AST → Tree-sitter → File Content (fallback chain)
```

**Requirements:**
- Missing LSP server: degrade to AST-only mode
- Missing Tree-sitter language: skip gracefully with warning
- Never crash on optional dependency failure
- Always log degradation with clear warning messages

### 5. Test Coverage Requirements

```
MINIMUM: 80% code coverage for core modules
REQUIRED: All public APIs must have unit tests
REQUIRED: Integration tests for end-to-end workflows
REQUIRED: Error path testing for all exception types
```

**Requirements:**
- No PR merged without passing tests
- New features require corresponding test coverage
- CLI entry points must have explicit tests

### 6. Citation Format Standard

```
FORMAT: {file_path}:{line_number}
EXAMPLE: src/skills_fabric/verify/ddr/__init__.py:142
REQUIREMENT: 1-indexed line numbers (human-readable)
```

**Requirements:**
- All SourceRef objects MUST have valid citations
- Citations MUST be verifiable against actual file content
- Broken citations trigger ValidationError

---

## Code Quality Standards

### Typing Requirements
- All public functions MUST have type hints
- Return types MUST be explicit (no implicit None)
- Use `Optional[T]` for nullable types
- Complex types should use TypeAlias or dataclass

### Documentation Requirements
- All public classes MUST have docstrings
- All public functions MUST have docstrings with Args/Returns
- Complex algorithms MUST have inline comments explaining logic
- Module-level docstrings MUST explain purpose and usage

### Error Handling Requirements
- Use domain-specific exceptions from `core.exceptions`
- Never catch bare `Exception` in production code
- Always include context in error messages
- Log errors with appropriate level (warning/error/critical)

### Performance Requirements
- Batch operations for > 10 items
- Lazy loading for optional dependencies
- Thread-safe database access (use thread-local connections)
- Timeout on all external API calls

---

## Architectural Constraints

### Single Responsibility
- Each module has ONE clear purpose
- Agents handle ONE stage of the pipeline
- Utilities do not contain business logic

### Dependency Direction
```
CLI (__main__.py)
    ↓
Orchestration (agents, orchestration)
    ↓
Domain Logic (verify, analyze, generate, link)
    ↓
Infrastructure (core, store, observability)
    ↓
External (retrievals, integrations)
```

### No Circular Imports
- Modules at lower levels MUST NOT import from higher levels
- Use dependency injection for cross-cutting concerns
- Abstract interfaces at domain boundaries

### Database Isolation
- All DB access through KuzuDatabase singleton
- Thread-local connections for concurrency
- Migrations handled explicitly, not auto-generated

---

## Security Constraints

### Input Validation
- All file paths MUST be validated against path traversal
- All user input MUST be sanitized before use in queries
- Symbol names from external sources MUST be validated

### Sandbox Execution
- All code execution MUST use Bubblewrap sandbox
- No shell=True in subprocess calls with user input
- Execution timeout MUST be enforced

### API Key Handling
- API keys loaded from environment variables only
- Never log API keys or tokens
- Use redaction in error messages

---

## Compatibility Requirements

### Python Version
- Minimum: Python 3.11
- Maximum: Python 3.13 (test before adopting newer)

### Supported Languages (Analysis)
- Python: Full support (AST + Tree-sitter + LSP)
- TypeScript: Full support (Tree-sitter + LSP)
- JavaScript: Full support (Tree-sitter + LSP)
- Others: Tree-sitter only (best effort)

### IDE Integration
- Claude Code: Primary target
- Cursor: Supported
- VS Code: Supported via CLI

---

## Versioning & Releases

### Semantic Versioning
```
MAJOR.MINOR.PATCH
- MAJOR: Breaking API changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes only
```

### Changelog Requirements
- Every PR MUST update CHANGELOG.md
- Breaking changes MUST be highlighted
- Migration guides for major versions

---

## Review Checklist

Before any code is merged:
- [ ] Hall_m compliance verified
- [ ] Tests pass (unit + integration)
- [ ] Type hints complete
- [ ] Docstrings present
- [ ] No new security vulnerabilities
- [ ] Performance impact assessed
- [ ] Graceful degradation maintained
