# Skills Fabric - BMAD Actionable Tasks

> Generated from BMAD v6 and SpecKit Analysis
> Created: 2026-01-07

---

## Task Board Format

Each task follows BMAD structure:
- **ID**: Unique identifier
- **Track**: Quick Flow / BMad Method / Enterprise
- **Agent**: BMAD agent responsible
- **Priority**: P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)
- **Estimate**: Story points or time
- **Dependencies**: Blocking tasks

---

## Sprint 1: Critical Stabilization

### TASK-001: Add CLI Test Suite
```yaml
ID: TASK-001
Track: BMad Method
Agent: QA
Priority: P0
Estimate: 5 points
Dependencies: None
Status: TODO

Description: |
  Create comprehensive test suite for __main__.py CLI.
  Currently 1125 lines with 0 tests.

Acceptance Criteria:
  - [ ] Test all 6 commands (generate, verify, analyze, research, search, version)
  - [ ] Test error cases (missing args, invalid input)
  - [ ] Test JSON output mode
  - [ ] Test verbose/quiet flags
  - [ ] Coverage > 80% for __main__.py

Files to Create:
  - tests/test_cli.py
  - tests/test_cli_integration.py

Test Count Target: 30+ tests
```

### TASK-002: Remove Dead Code
```yaml
ID: TASK-002
Track: Quick Flow
Agent: Architect
Priority: P0
Estimate: 2 points
Dependencies: None
Status: TODO

Description: |
  Remove unused directories and files identified in analysis.

Actions:
  - [ ] Delete older_project/ directory
  - [ ] Delete or merge analyze_/ directory
  - [ ] Review integrations/*.py for dead code
  - [ ] Update __init__.py exports if needed

Verification:
  - All tests pass after removal
  - No import errors
  - No broken references
```

### TASK-003: Fix HallMetric Thread Safety
```yaml
ID: TASK-003
Track: Quick Flow
Agent: Developer
Priority: P0
Estimate: 3 points
Dependencies: None
Status: TODO

Description: |
  Make HallMetric thread-safe using contextvars.

Changes:
  - [ ] Add contextvars for hall_metric state
  - [ ] Update DDR to use context-local metrics
  - [ ] Add thread safety tests
  - [ ] Document thread safety guarantees

Files to Modify:
  - src/skills_fabric/verify/ddr/__init__.py
  - tests/test_ddr.py (add concurrency tests)
```

---

## Sprint 2: Feature Completion

### TASK-004: Implement Context7 Client
```yaml
ID: TASK-004
Track: BMad Method
Agent: Developer
Priority: P1
Estimate: 5 points
Dependencies: None
Status: TODO

Description: |
  Implement missing Context7 API client.

Deliverables:
  - [ ] Context7Config dataclass
  - [ ] Context7Client with resolve_library_id()
  - [ ] Context7Client with get_library_docs()
  - [ ] Context7Client with search_docs()
  - [ ] Unit tests for all methods
  - [ ] Integration test with real API (marked requires_api)

Files to Create:
  - src/skills_fabric/retrievals/context7_client.py
  - tests/test_context7_client.py

API Reference: https://mcp.context7.com/mcp
```

### TASK-005: Consolidate Memory Systems
```yaml
ID: TASK-005
Track: Enterprise
Agent: Architect
Priority: P1
Estimate: 8 points
Dependencies: TASK-002
Status: TODO

Description: |
  Consolidate duplicate memory systems into single interface.

Decision: Keep Legacy (Supermemory-style), deprecate Modern (Beads/MIRIX)

Actions:
  - [ ] Add deprecation warnings to AgentMemorySystem
  - [ ] Migrate any Modern-only features to Legacy
  - [ ] Update all imports to use Legacy
  - [ ] Document migration path
  - [ ] Schedule removal in next major version

Files to Modify:
  - src/skills_fabric/memory/__init__.py
  - src/skills_fabric/memory/agent_memory.py (add deprecation)
  - All files importing AgentMemorySystem
```

### TASK-006: Add Progress Indicators
```yaml
ID: TASK-006
Track: Quick Flow
Agent: Developer
Priority: P1
Estimate: 2 points
Dependencies: None
Status: TODO

Description: |
  Add progress bars/spinners for long operations.

Changes:
  - [ ] Add rich library to dependencies
  - [ ] Add spinner to generate command
  - [ ] Add progress bar to batch verify
  - [ ] Add progress to analyze directory

Files to Modify:
  - pyproject.toml (add rich dependency)
  - src/skills_fabric/__main__.py
```

---

## Sprint 3: Quality Hardening

### TASK-007: Abstract External Services
```yaml
ID: TASK-007
Track: BMad Method
Agent: Architect
Priority: P2
Estimate: 5 points
Dependencies: TASK-004
Status: TODO

Description: |
  Create protocol interfaces for external service providers.

Deliverables:
  - [ ] SearchProvider protocol
  - [ ] ResearchProvider protocol
  - [ ] Update PerplexityClient to implement ResearchProvider
  - [ ] Update BraveSearchClient to implement SearchProvider
  - [ ] Update Context7Client to implement appropriate protocol
  - [ ] Factory function for provider creation

Files to Create:
  - src/skills_fabric/retrievals/protocol.py

Files to Modify:
  - src/skills_fabric/retrievals/perplexity_client.py
  - src/skills_fabric/retrievals/brave_search_client.py
  - src/skills_fabric/retrievals/context7_client.py
```

### TASK-008: Add Network Resilience Tests
```yaml
ID: TASK-008
Track: BMad Method
Agent: QA
Priority: P2
Estimate: 5 points
Dependencies: TASK-007
Status: TODO

Description: |
  Add comprehensive tests for network failure scenarios.

Test Cases:
  - [ ] Timeout triggers retry
  - [ ] Rate limit (429) triggers backoff
  - [ ] Server error (5xx) triggers retry
  - [ ] Partial response handling
  - [ ] Max retries exceeded
  - [ ] Network unreachable

Files to Create:
  - tests/test_network_resilience.py
```

### TASK-009: Add Performance Tests
```yaml
ID: TASK-009
Track: BMad Method
Agent: QA
Priority: P2
Estimate: 5 points
Dependencies: None
Status: TODO

Description: |
  Add performance regression tests.

Test Cases:
  - [ ] Large file parsing (10K lines < 5s)
  - [ ] Directory parsing (100 files < 10s)
  - [ ] Batch verification (1000 symbols < 30s)
  - [ ] Memory usage under limits

Files to Create:
  - tests/test_performance.py
  - tests/benchmarks/

Configuration:
  - Add @pytest.mark.slow marker
  - Add benchmark tracking (pytest-benchmark)
```

### TASK-010: Add User Documentation
```yaml
ID: TASK-010
Track: Enterprise
Agent: Tech Writer
Priority: P2
Estimate: 8 points
Dependencies: TASK-001, TASK-004
Status: TODO

Description: |
  Create comprehensive user documentation.

Deliverables:
  - [ ] Getting Started guide
  - [ ] CLI Reference
  - [ ] Configuration Guide
  - [ ] API Documentation
  - [ ] Architecture Overview
  - [ ] Example Projects

Files to Create:
  - docs/getting-started.md
  - docs/cli-reference.md
  - docs/configuration.md
  - docs/api/README.md
  - docs/architecture.md
  - examples/basic-usage/
  - examples/advanced-workflow/
```

---

## Sprint 4: Infrastructure

### TASK-011: Add CI/CD Pipeline
```yaml
ID: TASK-011
Track: BMad Method
Agent: Developer
Priority: P2
Estimate: 3 points
Dependencies: TASK-001
Status: TODO

Description: |
  Set up GitHub Actions CI/CD pipeline.

Deliverables:
  - [ ] Test job (pytest with coverage)
  - [ ] Lint job (ruff, mypy)
  - [ ] Security scan (bandit)
  - [ ] Build job (wheel creation)
  - [ ] Release job (PyPI publish)

Files to Create:
  - .github/workflows/ci.yml
  - .github/workflows/release.yml
```

### TASK-012: Add Pre-commit Hooks
```yaml
ID: TASK-012
Track: Quick Flow
Agent: Developer
Priority: P2
Estimate: 1 point
Dependencies: None
Status: TODO

Description: |
  Configure pre-commit hooks for code quality.

Hooks:
  - [ ] ruff (lint + format)
  - [ ] mypy (type check)
  - [ ] pytest (quick tests)
  - [ ] trailing-whitespace
  - [ ] end-of-file-fixer

Files to Create:
  - .pre-commit-config.yaml
```

### TASK-013: Add Docker Development Environment
```yaml
ID: TASK-013
Track: BMad Method
Agent: Developer
Priority: P3
Estimate: 3 points
Dependencies: None
Status: TODO

Description: |
  Create Docker-based development environment.

Deliverables:
  - [ ] Dockerfile for development
  - [ ] docker-compose.yml with dependencies
  - [ ] Dev container configuration
  - [ ] Documentation

Files to Create:
  - Dockerfile
  - docker-compose.yml
  - .devcontainer/devcontainer.json
```

---

## Backlog (Future Sprints)

### TASK-014: Complete SCIP Integration
```yaml
Priority: P3
Estimate: 8 points
Description: Fully integrate SCIP for cross-file symbol resolution
```

### TASK-015: Add Plugin System
```yaml
Priority: P3
Estimate: 13 points
Description: Allow custom analyzers and providers via plugins
```

### TASK-016: Create MCP Server
```yaml
Priority: P3
Estimate: 8 points
Description: Expose Skills Fabric as MCP server for Claude
```

### TASK-017: Add Web UI
```yaml
Priority: P3
Estimate: 21 points
Description: Create web interface for browsing generated skills
```

### TASK-018: Add Checkpointing
```yaml
Priority: P2
Estimate: 5 points
Description: Allow resuming interrupted operations
```

---

## Task Summary

| Sprint | Tasks | Total Points |
|--------|-------|--------------|
| Sprint 1 | 3 | 10 |
| Sprint 2 | 3 | 15 |
| Sprint 3 | 4 | 23 |
| Sprint 4 | 3 | 7 |
| Backlog | 5 | 55 |
| **Total** | **18** | **110** |

---

## Definition of Done

For each task:
- [ ] Code complete and reviewed
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No new linting errors
- [ ] Hall_m compliance verified
- [ ] PR approved and merged

---

## BMAD Workflow Commands

```bash
# Initialize BMAD for this project
npx bmad-method@alpha install

# Start a task
*workflow-init  # Analyze and recommend track

# Quick Flow (bug fixes, small changes)
*quick-flow

# BMad Method (new features)
*bmad-method

# Enterprise (large refactors)
*enterprise
```

---

## Sources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [BMAD v6 Installation](https://bmadcodes.com/)
- [SpecKit Tasks Command](https://github.com/github/spec-kit)
