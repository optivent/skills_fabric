# Skills Fabric - BMAD v6 Improvement Roadmap

> Following BMAD Methodology for Structured Improvements
> Created: 2026-01-07

---

## Quick Reference: BMAD Tracks

| Track | Duration | Use Case |
|-------|----------|----------|
| **Quick Flow** | < 5 min | Bug fixes, small patches |
| **BMad Method** | < 15 min | New features, enhancements |
| **Enterprise** | < 30 min | Large refactors, governance |

---

## Phase 1: Stabilization (Quick Flow Track)

**Duration:** 1-2 Sprints | **Priority:** Critical

### 1.1 Add CLI Tests (CRITICAL)

**Problem:** `__main__.py` has 1125 lines with 0 tests
**Impact:** Cannot safely refactor or modify CLI
**BMAD Agent:** QA

```python
# tests/test_cli.py - Create this file
import pytest
from click.testing import CliRunner
from skills_fabric.__main__ import main

class TestGenerateCommand:
    def test_generate_with_library(self):
        runner = CliRunner()
        result = runner.invoke(main, ['generate', 'langgraph', '--depth', '1'])
        assert result.exit_code == 0

    def test_generate_missing_library(self):
        runner = CliRunner()
        result = runner.invoke(main, ['generate'])
        assert result.exit_code != 0
        assert 'required' in result.output.lower()

class TestVerifyCommand:
    def test_verify_with_query(self):
        runner = CliRunner()
        result = runner.invoke(main, ['verify', 'StateGraph', '--json'])
        # Should work even without codewiki

class TestAnalyzeCommand:
    def test_analyze_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")
        runner = CliRunner()
        result = runner.invoke(main, ['analyze', str(test_file)])
        assert result.exit_code == 0

class TestVersionCommand:
    def test_version_output(self):
        runner = CliRunner()
        result = runner.invoke(main, ['version'])
        assert result.exit_code == 0
        assert 'skills-fabric' in result.output.lower()
```

### 1.2 Remove Dead Code

**Problem:** Multiple unused/duplicate directories
**Impact:** Confuses developers, increases maintenance burden
**BMAD Agent:** Architect

**Actions:**
```bash
# Remove older_project (legacy code)
rm -rf /home/user/skills_fabric/older_project/

# Consolidate analyze_ into analyze (if different)
# Or remove if duplicate
rm -rf /home/user/skills_fabric/src/skills_fabric/analyze_/

# Clean up aspirational integration files
# Review and remove if not functional:
# - integrations/ultimate_stack.py
# - integrations/unified_api.py
# - integrations/complete_architecture.py
```

### 1.3 Fix Thread Safety

**Problem:** Global `hall_metric` state not thread-safe
**Impact:** Incorrect metrics in concurrent scenarios
**BMAD Agent:** Developer

```python
# Option 1: Use contextvars (recommended)
import contextvars
_hall_metric_context: contextvars.ContextVar[HallMetric] = contextvars.ContextVar('hall_metric')

def get_hall_metric() -> HallMetric:
    try:
        return _hall_metric_context.get()
    except LookupError:
        metric = HallMetric()
        _hall_metric_context.set(metric)
        return metric

# Option 2: Instance-scoped in DDR
class DirectDependencyRetriever:
    def __init__(self, ...):
        self.hall_metric = HallMetric()  # Instance, not global
```

---

## Phase 2: Completion (BMad Method Track)

**Duration:** 2-3 Sprints | **Priority:** High

### 2.1 Implement Context7 Client

**Problem:** Referenced in docs but not implemented
**Impact:** Missing promised functionality
**BMAD Agent:** Developer

```python
# src/skills_fabric/retrievals/context7_client.py
from dataclasses import dataclass
from typing import Optional
import httpx

@dataclass
class Context7Config:
    api_url: str = "https://mcp.context7.com/mcp"
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "Context7Config":
        return cls(
            api_url=os.environ.get("CONTEXT7_URL", cls.api_url)
        )

@dataclass
class Context7Doc:
    library_id: str
    title: str
    content: str
    url: str

class Context7Client:
    def __init__(self, config: Optional[Context7Config] = None):
        self.config = config or Context7Config.from_env()

    async def resolve_library_id(self, library_name: str) -> Optional[str]:
        """Resolve library name to Context7 library ID."""
        ...

    async def get_library_docs(self, library_id: str) -> list[Context7Doc]:
        """Fetch all documentation for a library."""
        ...

    async def search_docs(self, library_id: str, query: str) -> list[Context7Doc]:
        """Search documentation for specific topics."""
        ...
```

### 2.2 Consolidate Memory Systems

**Problem:** Two parallel memory implementations
**Impact:** Confusion, maintenance burden
**BMAD Agent:** Architect

**Decision Needed:** Keep Legacy OR Modern?

```python
# Option A: Keep Legacy (Supermemory-style)
# Deprecate: memory/agent_memory.py (Beads/MIRIX/ADK)

# Option B: Keep Modern (Agent-focused)
# Deprecate: memory/knowledge_graph.py, memory/session.py

# Recommendation: Option A (Legacy is more complete)
# Add deprecation warnings to Modern:
import warnings

class AgentMemorySystem:
    def __init__(self, ...):
        warnings.warn(
            "AgentMemorySystem is deprecated. Use KnowledgeGraph instead.",
            DeprecationWarning,
            stacklevel=2
        )
```

### 2.3 Add Progress Indicators

**Problem:** Long operations have no feedback
**Impact:** Users think system is stuck
**BMAD Agent:** UX Designer (via Developer)

```python
# Use rich library for progress bars
from rich.progress import Progress, SpinnerColumn, TextColumn

def cmd_generate(args):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Cloning repository...", total=None)
        # ... clone
        progress.update(task, description="Analyzing symbols...")
        # ... analyze
        progress.update(task, description="Generating skills...")
        # ... generate
```

### 2.4 Abstract External Services

**Problem:** APIs lack common interface
**Impact:** Hard to add new providers, test difficult
**BMAD Agent:** Architect

```python
# src/skills_fabric/retrievals/protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class SearchProvider(Protocol):
    async def search(
        self,
        query: str,
        count: int = 10,
        **kwargs
    ) -> "SearchResult":
        ...

@runtime_checkable
class ResearchProvider(Protocol):
    async def research(
        self,
        query: str,
        depth: int = 1,
        **kwargs
    ) -> "ResearchResult":
        ...

# Update existing clients to implement protocols
class PerplexityClient(ResearchProvider):
    async def research(self, query: str, depth: int = 1, **kwargs):
        return await self.iterative_research(query, max_depth=depth)

class BraveSearchClient(SearchProvider):
    async def search(self, query: str, count: int = 10, **kwargs):
        return await self._search(query, count=count, **kwargs)
```

---

## Phase 3: Hardening (Enterprise Track)

**Duration:** 3-4 Sprints | **Priority:** Medium

### 3.1 Add Network Resilience Tests

```python
# tests/test_network_resilience.py
import pytest
from unittest.mock import AsyncMock, patch

class TestPerplexityResilience:
    @pytest.mark.asyncio
    async def test_timeout_triggers_retry(self):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = [
                httpx.TimeoutException("timeout"),
                httpx.TimeoutException("timeout"),
                AsyncMock(json=lambda: {"choices": [...]})
            ]
            client = PerplexityClient()
            result = await client.search("test")
            assert mock_post.call_count == 3  # 2 retries + success

    @pytest.mark.asyncio
    async def test_rate_limit_backoff(self):
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = [
                httpx.HTTPStatusError("429", request=..., response=...),
                AsyncMock(json=lambda: {"choices": [...]})
            ]
            client = PerplexityClient()
            result = await client.search("test")
            # Verify backoff delay was applied
```

### 3.2 Add Performance Tests

```python
# tests/test_performance.py
import pytest
import time

@pytest.mark.slow
class TestPerformance:
    def test_large_file_parsing(self, tmp_path):
        """Parse 10,000 line Python file under 5 seconds."""
        large_file = tmp_path / "large.py"
        content = "\n".join([f"def func_{i}(): pass" for i in range(10000)])
        large_file.write_text(content)

        parser = ASTParser()
        start = time.perf_counter()
        symbols = parser.parse_file_enhanced(large_file)
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0
        assert len(symbols) == 10000

    def test_batch_verification(self):
        """Verify 1000 symbols under 30 seconds."""
        queries = [f"symbol_{i}" for i in range(1000)]

        ddr = DirectDependencyRetriever(...)
        start = time.perf_counter()
        results = ddr.retrieve_batch(queries)
        elapsed = time.perf_counter() - start

        assert elapsed < 30.0
```

### 3.3 Add User Documentation

```markdown
# docs/getting-started.md
# Getting Started with Skills Fabric

## Installation
pip install skills-fabric

## Quick Start
# Generate skills for a library
python -m skills_fabric generate langgraph --depth 2

## Configuration
export ANTHROPIC_API_KEY="your-key"

## Example: Full Workflow
...
```

### 3.4 Add CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e .[dev]
      - run: pytest --cov=src/skills_fabric --cov-report=xml
      - uses: codecov/codecov-action@v4

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install ruff mypy
      - run: ruff check src/
      - run: mypy src/skills_fabric
```

---

## Phase 4: Polish (Ongoing)

### 4.1 Documentation Improvements
- API reference generation (sphinx/mkdocs)
- Architecture diagrams (mermaid)
- Example projects

### 4.2 Developer Experience
- Pre-commit hooks
- VS Code extension
- Debug configurations

### 4.3 Ecosystem
- Plugin system for custom analyzers
- MCP server for Claude integration
- Web UI for skill browsing

---

## Implementation Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| CLI Tests | High | Medium | P0 |
| Remove Dead Code | Medium | Low | P0 |
| Thread Safety Fix | High | Low | P0 |
| Context7 Client | Medium | Medium | P1 |
| Memory Consolidation | Medium | Medium | P1 |
| Progress Indicators | Low | Low | P1 |
| Service Abstraction | Medium | High | P2 |
| Network Tests | Medium | Medium | P2 |
| Performance Tests | Medium | Medium | P2 |
| User Docs | High | High | P2 |
| CI/CD | High | Medium | P2 |

---

## BMAD Compliance Checklist

Before each change:
- [ ] Identified which BMAD agent perspective applies
- [ ] Selected appropriate track (Quick/BMad/Enterprise)
- [ ] Created or updated tests
- [ ] Updated documentation
- [ ] Verified Hall_m compliance maintained
- [ ] No new technical debt introduced

---

## Sources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [BMAD v6 Overview](https://nayakpplaban.medium.com/bmad-ai-powered-agile-framework-overview-238d4af39aa4)
- [SpecKit GitHub](https://github.com/github/spec-kit)
- [Spec-Driven Development Guide](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
