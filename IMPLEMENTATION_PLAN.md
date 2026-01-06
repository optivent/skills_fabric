# Implementation Plan

> **Project**: Skills Fabric - Zero-Hallucination Progressive Disclosure Skill Generator
> **Created**: January 2026
> **Status**: Ready for Implementation

---

## Executive Summary

Skills Fabric is **70% implemented**. The core architecture exists:
- Progressive disclosure (6 levels) ✓
- Ralph Wiggum iteration loop ✓
- Multi-agent supervisor ✓
- Trust hierarchy ✓
- PROVEN linking ✓

**Remaining work**: Connect research insights to existing code, enhance verification for zero-hallucination.

---

## Current State

### Implemented ✓

| Module | File | Status |
|--------|------|--------|
| Progressive Disclosure | `understanding/progressive_disclosure.py` | Complete |
| Ralph Wiggum Loop | `orchestration/ralph_wiggum.py` | Complete |
| Completion Promises | `orchestration/completion_promise.py` | Complete |
| Supervisor Agent | `agents/supervisor.py` | Complete |
| Miner Agent | `agents/miner.py` | Complete |
| Linker Agent | `agents/linker.py` | Complete |
| Verifier Agent | `agents/verifier.py` | Complete |
| Writer Agent | `agents/writer.py` | Complete |
| Trust Hierarchy | `trust/hierarchy.py` | Complete |
| Knowledge Graph | `memory/knowledge_graph.py` | Complete |
| Beads/MIRIX Memory | `memory/agent_memory.py` | Complete |
| Observability | `observability/*.py` | Complete |

### Needs Enhancement

| Module | Gap | Research Solution |
|--------|-----|-------------------|
| Verification | Basic trust check | DDR (Hall_m < 0.02) |
| Memory | No decay | AgeMem + Cognitive Decay |
| Context | Basic | CaveAgent dual-stream |
| Testing | Manual | MAESTRO framework |

---

## Implementation Phases

### Phase 1: Zero-Hallucination Pipeline (Priority: HIGH)

**Goal**: Achieve Hall_m < 0.02 hallucination rate

**Tasks**:

1. **DDR Integration** (`verify/ddr.py`)
   ```python
   class DirectDependencyRetriever:
       """Only retrieve elements that actually exist in source."""

       async def retrieve(self, query: str) -> List[CodeElement]:
           # 1. Search AST for matching symbols
           symbols = await self.ast_search(query)

           # 2. Validate each symbol exists
           validated = [s for s in symbols if await self.validate(s)]

           # 3. Return with file:line citations
           return validated
   ```

2. **Multi-Agent Verification** (`agents/auditor.py`)
   ```python
   class AuditorAgent(BaseAgent):
       """Verifies generated content against source."""

       async def audit(self, content: str, sources: List[SourceRef]) -> AuditResult:
           for claim in self.extract_claims(content):
               if not self.verify_against_source(claim, sources):
                   return AuditResult(passed=False, unverified=claim)
           return AuditResult(passed=True)
   ```

3. **Citation System** (`generate/citations.py`)
   ```python
   def add_citations(content: str, refs: List[SourceRef]) -> str:
       """Add file:line citations to all code references."""
       for ref in refs:
           content = content.replace(
               f"`{ref.symbol_name}`",
               f"[`{ref.symbol_name}`]({ref.github_url})"
           )
       return content
   ```

**Completion Criteria**:
- [ ] DDR retrieves only validated symbols
- [ ] Auditor rejects unverified claims
- [ ] All code refs have file:line citations
- [ ] Hall_m metric tracking implemented

---

### Phase 2: Enhanced Memory & Context (Priority: MEDIUM)

**Goal**: Implement AgeMem + CaveAgent patterns

**Tasks**:

1. **AgeMem Tools** (`memory/agmem_tools.py`)
   ```python
   class AgeMemTools:
       """Memory tools exposed to agent (AgeMem pattern)."""

       def get_tools(self) -> List[Tool]:
           return [
               Tool("store_ltm", self.store_long_term),
               Tool("retrieve_stm", self.retrieve_short_term),
               Tool("summarize_context", self.summarize),
               Tool("discard_stale", self.garbage_collect),
           ]
   ```

2. **CaveAgent Context** (`orchestration/context_manager.py`)
   ```python
   class DualStreamContext:
       """CaveAgent dual-stream context management."""

       def __init__(self):
           self.semantic_stream = []   # Lightweight summaries
           self.runtime_stream = {}    # Actual objects/state

       async def sync(self):
           """Synchronize runtime state to semantic stream."""
           summary = await self.summarize_runtime()
           self.semantic_stream.append(f"[STATE] {summary}")
   ```

**Completion Criteria**:
- [ ] Memory tools callable by agents
- [ ] Dual-stream context prevents token explosion
- [ ] Cognitive decay removes stale info

---

### Phase 3: Testing & Observability (Priority: MEDIUM)

**Goal**: Implement MAESTRO-style testing

**Tasks**:

1. **MAESTRO Adapter** (`testing/maestro.py`)
   ```python
   class MAESTROAdapter:
       """Framework-agnostic agent testing."""

       async def test_skill(self, skill, test_cases) -> TestReport:
           results = []
           for case in test_cases:
               trace = await self.execute_with_trace(skill, case)
               results.append(self.evaluate(trace, case.expected))
           return TestReport(results)
   ```

2. **Observability Enhancement** (`observability/langfuse.py`)
   ```python
   class LangfuseTracer:
       """Cost tracking and performance monitoring."""

       def trace_skill_generation(self, library: str):
           with self.observation(name=f"skill_{library}") as obs:
               result = yield
               obs.log_cost(result.tokens, result.model)
   ```

**Completion Criteria**:
- [ ] Test suite for all depth levels
- [ ] Cost tracking per skill
- [ ] Trace visualization in Langfuse/LangSmith

---

### Phase 4: Production Optimization (Priority: LOW)

**Goal**: Parallel execution and cost optimization

**Tasks**:

1. **Git Worktrees** (`orchestration/parallel.py`)
   ```python
   class ParallelExecutor:
       """Execute agents in isolated worktrees."""

       async def execute_parallel(self, tasks: List[Task]):
           async with asyncio.TaskGroup() as tg:
               for task in tasks:
                   worktree = await self.create_worktree(task.id)
                   tg.create_task(task.execute(cwd=worktree))
   ```

2. **Cost Optimization** (existing `integrations/unified_api.py`)
   - Zerank 2 reranking ($0.025/M vs GPT-4o)
   - Qwen3-Embedding (open-source, Apache 2.0)
   - Batch processing for large repos

**Completion Criteria**:
- [ ] Worktree isolation for parallel agents
- [ ] Target: ~$0.06 per skill
- [ ] Batch mode for bulk processing

---

## Quick Start Commands

```bash
# Run skill generation for a library
python -m skills_fabric generate langgraph --depth 3

# Test with Ralph Wiggum loop
python -m skills_fabric.orchestration.ralph_wiggum --library langgraph --max-iterations 10

# Build progressive understanding
python -m skills_fabric.understanding.progressive_disclosure

# Verify trust hierarchy
python -m skills_fabric.trust.hierarchy --check
```

---

## File Structure (Final)

```
/home/user/skills_fabric/
├── IMPLEMENTATION_PLAN.md          # This file
├── MASTER_RESEARCH_GUIDE.md        # Quick reference
├── specs/
│   └── SKILL.spec.md               # Main specification
├── docs/
│   ├── research/
│   │   ├── rounds/                 # Raw research (6 rounds)
│   │   └── summaries/              # Processed insights
│   └── reference/                  # Framework references
├── src/skills_fabric/
│   ├── agents/                     # Multi-agent system ✓
│   ├── memory/                     # Knowledge + AgeMem ✓
│   ├── orchestration/              # Ralph Wiggum + Supervisor ✓
│   ├── trust/                      # Verification ✓
│   ├── understanding/              # Progressive disclosure ✓
│   ├── verify/                     # DDR (to implement)
│   ├── integrations/               # APIs ✓
│   └── ...
├── retrievals/                     # Perplexity, Brave, arXiv ✓
└── scripts/                        # Research scripts ✓
```

---

## Next Actions

1. **Immediate**: Run existing pipeline on a test library
   ```bash
   python -m skills_fabric generate requests --depth 2
   ```

2. **This Week**: Implement DDR verification
   - Create `verify/ddr.py`
   - Add `agents/auditor.py`
   - Update `agents/supervisor.py` to include audit step

3. **Next Week**: Add AgeMem tools + testing
   - Create `memory/agmem_tools.py`
   - Create `testing/maestro.py`
   - Add test suite

---

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Hallucination Rate | Unknown | < 0.02 |
| Coverage | ~60% | > 80% |
| Source Validity | ~90% | 100% |
| Cost per Skill | ~$0.15 | < $0.10 |

---

## References

- **Spec**: `specs/SKILL.spec.md`
- **Research**: `docs/research/summaries/`
- **Frameworks**: `docs/reference/DETAILED_FRAMEWORKS_REFERENCE.md`
- **Master Guide**: `MASTER_RESEARCH_GUIDE.md`
