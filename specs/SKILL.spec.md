# Skills Fabric - Main Specification

> **Version**: 1.0.0
> **Status**: Active Development
> **Last Updated**: January 2026

---

## 1. Vision

**One-liner**: Zero-hallucination Claude skill generator with progressive disclosure at progressive depth of understanding.

**Mission**: Generate Claude skills for any code library that are:
1. **Grounded**: Every claim backed by actual source code (file:line citations)
2. **Progressive**: 6 levels of depth (L0-L5) expandable on-demand
3. **Verified**: Trust hierarchy ensures no hallucinated content

---

## 2. User Stories

### Primary User: Claude Code Developer

**US-1**: As a developer, I want to generate a skill for a library so that Claude understands the library's API and patterns.

**US-2**: As a developer, I want progressive disclosure so I can get quick answers (L0) or deep analysis (L5) based on my needs.

**US-3**: As a developer, I want zero hallucinations so I can trust the skill's code examples and API references.

**US-4**: As a developer, I want source citations so I can verify any claim against actual code.

---

## 3. Acceptance Criteria

### AC-1: Zero Hallucination
- [ ] Every code reference must link to actual source (file:line)
- [ ] Hallucination rate: Hall_m < 0.02 (DDR standard)
- [ ] Multi-agent verification: Generator → Auditor pipeline
- [ ] Trust hierarchy enforced: HardContent (100%) > VerifiedSoft (95%) > REJECTED

### AC-2: Progressive Disclosure
- [ ] Level 0: One-liner (1 sentence)
- [ ] Level 1: Quick Start (30 seconds to understand)
- [ ] Level 2: Core Concepts (5 minutes)
- [ ] Level 3: Detailed Guide with source refs (30 minutes)
- [ ] Level 4: Semantic Analysis (LSP + AST)
- [ ] Level 5: Execution Proofs (verified behavior)
- [ ] On-demand expansion: User can drill down any section

### AC-3: Quality Metrics
- [ ] Coverage: >80% of public API documented
- [ ] Accuracy: 100% source references valid
- [ ] Completeness: All depth levels populated
- [ ] Cost: ~$0.06 per skill execution

---

## 4. Architecture

### 4.1 Existing Components (Implemented)

```
src/skills_fabric/
├── understanding/
│   └── progressive_disclosure.py    # 6-level DepthLevel system ✓
├── orchestration/
│   ├── ralph_wiggum.py              # Iteration loop with promises ✓
│   └── completion_promise.py        # Exit conditions ✓
├── agents/
│   ├── supervisor.py                # Multi-agent coordinator ✓
│   ├── miner.py                     # Source code search ✓
│   ├── linker.py                    # PROVEN linking ✓
│   ├── verifier.py                  # Trust verification ✓
│   └── writer.py                    # Content generation ✓
├── trust/
│   ├── hierarchy.py                 # TrustLevel enum ✓
│   └── cross_layer.py               # Verification ✓
├── memory/
│   ├── knowledge_graph.py           # KuzuDB graph ✓
│   └── agent_memory.py              # Beads + MIRIX ✓
└── integrations/
    ├── ultimate_stack.py            # Tool specifications ✓
    └── unified_api.py               # API manager ✓
```

### 4.2 Research-Informed Enhancements

| Component | Current | Enhancement (from Research) |
|-----------|---------|----------------------------|
| **Memory** | Beads + MIRIX | + AgeMem (GRPO tools) |
| **Context** | Basic | + CaveAgent dual-stream |
| **Verification** | Trust hierarchy | + DDR (Hall_m < 0.02) |
| **Orchestration** | Supervisor | + BMAD phases |
| **Testing** | Basic | + MAESTRO framework |

### 4.3 Data Flow

```
INPUT: library_name + depth_level
           │
           ▼
    ┌──────────────────┐
    │   INGEST         │ GitClone + CodeWiki
    │   (existing)     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   ANALYZE        │ AST + Tree-sitter + LSP
    │   (existing)     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   UNDERSTAND     │ Progressive Disclosure Builder
    │   (existing)     │ 6 DepthLevels
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   VERIFY         │ Trust Hierarchy + DDR
    │   (enhance)      │ Hall_m < 0.02
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   GENERATE       │ Writer Agent + Citations
    │   (existing)     │
    └────────┬─────────┘
             │
             ▼
OUTPUT: ProgressiveUnderstanding with verified content
```

---

## 5. Technical Specifications

### 5.1 Progressive Disclosure Levels

```python
class DepthLevel(IntEnum):
    EXECUTIVE_SUMMARY = 0  # What is this? (1 paragraph)
    CONCEPT_MAP = 1        # Major components (H2 sections)
    DETAILED_SECTIONS = 2  # How things work (H3 sections)
    SOURCE_REFERENCES = 3  # Actual code (GitHub links)
    SEMANTIC_ANALYSIS = 4  # LSP + AST (type info, call graph)
    EXECUTION_PROOFS = 5   # Tests + assertions (verified behavior)
```

### 5.2 Trust Hierarchy

```python
class TrustLevel(Enum):
    HARD_CONTENT = 1      # 100% - Direct from source code
    VERIFIED_SOFT = 2     # 95%  - LLM output verified against source
    UNVERIFIED = 3        # 0%   - ALWAYS REJECTED
```

### 5.3 Zero-Hallucination Pipeline

```python
# DDR: Direct Dependency Retrieval
async def generate_grounded(library: str, level: int):
    # 1. Retrieve actual code elements
    elements = await ddr.retrieve(library)

    # 2. Generate constrained to retrieved elements
    content = await generator.generate_from_elements(elements)

    # 3. Verify every claim
    verified = await auditor.verify(content, elements)

    # 4. Cite sources
    return add_citations(verified, elements)
```

### 5.4 Ralph Wiggum Loop Configuration

```python
loop_config = {
    "max_iterations": 50,      # From research: Ralph default 100
    "max_cost": 10.0,          # Budget per skill
    "checkpoint_interval": 5,  # Git checkpoints
    "completion_promises": [
        "all_levels_populated",
        "zero_unverified_content",
        "source_refs_valid",
    ]
}
```

---

## 6. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hallucination Rate | < 0.02 | DDR Hall_m metric |
| Coverage | > 80% | Public API symbols documented |
| Source Validity | 100% | All file:line refs resolve |
| Cost per Skill | < $0.10 | Token usage tracking |
| Time per Library | < 10 min | End-to-end processing |

---

## 7. Implementation Phases

### Phase 1: Foundation (Current)
- [x] Progressive disclosure (6 levels)
- [x] Ralph Wiggum loop
- [x] Multi-agent supervisor
- [x] Trust hierarchy
- [x] PROVEN linking

### Phase 2: Zero-Hallucination Enhancement
- [ ] DDR integration
- [ ] Multi-agent verification (Generator → Auditor)
- [ ] Line-level citation system
- [ ] Hallucination rate tracking

### Phase 3: Memory & Context
- [ ] AgeMem tool-based interface
- [ ] CaveAgent dual-stream context
- [ ] Cognitive decay for relevance

### Phase 4: Production
- [ ] MAESTRO testing integration
- [ ] LangSmith/Langfuse observability
- [ ] Cost optimization
- [ ] Parallel worktree execution

---

## 8. Edge Cases

1. **Empty repository**: Return minimal L0-L1 from README
2. **No docstrings**: Fall back to AST + type hints
3. **Large codebase**: Chunk processing with memory
4. **Rate limits**: Exponential backoff + checkpointing
5. **Verification failure**: Reject content, retry with constraints

---

## 9. Dependencies

### Required APIs
- Anthropic Claude API (ANTHROPIC_API_KEY)
- Perplexity Sonar (PERPLEXITY_API_KEY) - for research
- Optional: Zerank 2 (ZERANK_API_KEY) - for reranking

### Infrastructure
- KuzuDB (graph storage)
- Git (worktrees for parallel execution)
- Python 3.11+

---

## 10. References

- `docs/research/summaries/OPTIMAL_INFRASTRUCTURE_MAP.md`
- `docs/research/summaries/SKILL_IMPLEMENTATION_PATTERNS.md`
- `docs/reference/DETAILED_FRAMEWORKS_REFERENCE.md`
- `src/skills_fabric/understanding/progressive_disclosure.py`
- `src/skills_fabric/orchestration/ralph_wiggum.py`
