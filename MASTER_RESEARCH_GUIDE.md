# Master Research Guide: Skills Fabric

> **Generated**: January 2026
> **Research Rounds**: 6 (42 queries, 420+ citations)
> **Purpose**: Zero-hallucination progressive disclosure code skill

---

## Table of Contents

1. [Infrastructure Stack](#1-infrastructure-stack)
2. [Agent Architecture Patterns](#2-agent-architecture-patterns)
3. [Memory Systems](#3-memory-systems)
4. [Code Understanding](#4-code-understanding)
5. [Progressive Disclosure](#5-progressive-disclosure)
6. [Zero-Hallucination](#6-zero-hallucination)
7. [Development Frameworks](#7-development-frameworks)
8. [Claude Code Features](#8-claude-code-features)
9. [Implementation Priorities](#9-implementation-priorities)

---

## 1. Infrastructure Stack

### Complete Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                     SKILLS FABRIC STACK                          │
├─────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION                                                   │
│  ├── LangGraph (state machines, handoffs)                       │
│  ├── Plan-and-Execute + Reflection (architecture)               │
│  ├── Hierarchical Supervisor (multi-agent)                      │
│  └── BMAD Method (agile personas)                               │
├─────────────────────────────────────────────────────────────────┤
│  MEMORY                                                          │
│  ├── AgeMem (unified LTM/STM with GRPO)                         │
│  ├── Cognitive Decay (Ebbinghaus/ACT-R)                         │
│  ├── Beads (work orchestration)                                 │
│  └── MIRIX (6-type memory)                                      │
├─────────────────────────────────────────────────────────────────┤
│  RETRIEVAL                                                       │
│  ├── Qwen3-Embedding (primary, MTEB leader)                     │
│  ├── Voyage-code-3 (code-specific)                              │
│  ├── Milvus/Qdrant (vector storage + hybrid search)             │
│  ├── Zerank 2 (reranking, ELO 1644)                             │
│  └── Cognee (knowledge graphs)                                  │
├─────────────────────────────────────────────────────────────────┤
│  CODE UNDERSTANDING                                              │
│  ├── Hybrid AST + LLM (best accuracy)                           │
│  ├── InlineCoder (call graph context)                           │
│  ├── RepoNavigator (RL symbol jumping)                          │
│  └── DDR (zero-hallucination retrieval)                         │
├─────────────────────────────────────────────────────────────────┤
│  CONTEXT MANAGEMENT                                              │
│  ├── CaveAgent Dual-Stream (semantic + runtime)                 │
│  ├── Jenius-Agent (3 optimization patterns)                     │
│  └── Git Worktrees (parallel agent isolation)                   │
├─────────────────────────────────────────────────────────────────┤
│  TESTING                                                         │
│  ├── MAESTRO (multi-agent evaluation)                           │
│  ├── 3-Layer Framework (static, dynamic, judge)                 │
│  └── Trace-First Flywheel (continuous learning)                 │
├─────────────────────────────────────────────────────────────────┤
│  OBSERVABILITY                                                   │
│  ├── LangSmith (LangGraph integration)                          │
│  ├── Langfuse (cost + OpenTelemetry)                           │
│  └── Helicone (production monitoring)                           │
├─────────────────────────────────────────────────────────────────┤
│  RESEARCH                                                        │
│  ├── Perplexity Sonar (deep research)                           │
│  ├── Brave Search (web search)                                  │
│  ├── arXiv + Docling (papers)                                   │
│  └── Brightdata (JS rendering)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Metrics

| Component | Solution | Cost/Performance |
|-----------|----------|------------------|
| Execution | ~$0.06/skill run | 19K input, 1.3K output tokens |
| Reranking | Zerank 2 | $0.025/M tokens, ELO 1644 |
| LLM-as-Judge | Low-cost monitoring | $0.06, 14.7s |
| Agent-as-Judge | High-stakes audits | $0.96, 913s |

---

## 2. Agent Architecture Patterns

### Primary: Plan-and-Execute + Reflection

```python
class SkillAgent:
    """Hybrid architecture with best production reliability."""

    def __init__(self):
        self.planner = HierarchicalPlanner()  # Decomposes into sub-tasks
        self.verifier = SelfReflectionModule()  # Validates outputs
        self.memory = AgeMem()  # Unified LTM/STM

    async def execute(self, task: str) -> Result:
        # 1. Plan
        plan = await self.planner.decompose(task)

        # 2. Execute with verification
        for step in plan:
            result = await self._execute_step(step)
            if not await self.verifier.validate(result):
                result = await self._retry_with_reflection(step)

        return result
```

### Multi-Agent Orchestration

**Hierarchical Supervisor** (best for complex tasks):

```python
class SupervisorOrchestrator:
    """Centralized coordination with specialized agents."""

    async def orchestrate(self, goal: str):
        # Supervisor decomposes and delegates
        subtasks = await self.supervisor.decompose(goal)

        # Spawn specialized agents
        results = []
        async with asyncio.TaskGroup() as tg:
            for task in subtasks:
                agent = self._select_agent(task)
                tg.create_task(agent.execute(task))

        # Aggregate and verify
        return await self._aggregate_results(results)
```

### Key Patterns from Research

| Pattern | Use Case | Source |
|---------|----------|--------|
| **BMAD Method** | Agile personas (QA, SM, Dev) | github.com/bmad-code-org/BMAD-METHOD |
| **Supervisor** | Complex task delegation | Shannon, arxiv 2601.01831 |
| **Planner-Worker** | Large model plans, small executes | arxiv 2506.13324 |
| **Warp-Cortex** | River & Stream topology | arxiv 2601.01298 |
| **Ralph's Loop** | Iterative completion | github.com/mikeyobrien/ralph-orchestrator |

---

## 3. Memory Systems

### AgeMem: Unified LTM/STM

**Key Innovation**: Memory tools as agent actions with GRPO optimization.

```python
class AgeMemSystem:
    """Agent autonomously manages memory via tools."""

    def get_memory_tools(self):
        return [
            Tool("store_ltm", self._store_long_term),
            Tool("retrieve_stm", self._retrieve_short_term),
            Tool("summarize_context", self._summarize),
            Tool("discard_stale", self._garbage_collect),
        ]

    async def recall(self, query: str):
        # Activation-based with decay: A_i = ln(t_i) - decay * d
        return await self.decay_engine.retrieve(query, decay=True)
```

### 4-Layer Architecture

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| **Beads** | Work orchestration | Git-backed task queue |
| **MIRIX** | 6 memory types | Episodic, semantic, procedural |
| **ADK** | Multi-agent handoff | Context compilation |
| **Decay** | Relevance optimization | Ebbinghaus/ACT-R |

---

## 4. Code Understanding

### Hybrid AST + LLM (Best in Class)

```python
class HybridCodeUnderstanding:
    """Combine AST precision with LLM semantics."""

    async def understand(self, code: str, level: str) -> Documentation:
        # 1. AST: Extract precise structure
        ast_info = self.ast_parser.parse(code)

        # 2. LLM: Infer semantic purpose
        purpose = await self.llm.infer_purpose(code, ast_info)

        # 3. Merge: Factually grounded + semantically rich
        return Documentation(
            structure=ast_info,  # From AST (factual)
            purpose=purpose,     # From LLM (semantic)
            citations=ast_info.line_numbers,  # Grounding
        )
```

### Repository-Level: InlineCoder + RepoNavigator

```python
class RepoUnderstanding:
    """Context inlining + RL symbol jumping."""

    async def understand_repo(self, path: Path):
        # Build call graph
        call_graph = await self.build_call_graph(path)

        # Inline context for multi-perspective
        context = await self._inline_context(call_graph)

        # Navigate with RL-based symbol jumping
        locations = await self.navigator.navigate(context)

        return await self._synthesize(locations)
```

---

## 5. Progressive Disclosure

### 3-Tier Model

| Tier | Content | Visibility |
|------|---------|------------|
| **Overview** | Purpose, install, hello world | Always visible |
| **Intermediate** | Key patterns, examples | On-demand |
| **Deep** | Full specs, edge cases | Expanded |

### 6 Depth Levels

```
Level 0: One-Liner (1 sentence)
Level 1: Quick Start (30 seconds)
Level 2: Core Concepts (5 minutes)
Level 3: Detailed Guide (30 minutes)
Level 4: Deep Dive (2+ hours)
Level 5: Expert Reference (complete)
```

### Implementation

```python
class ProgressiveSkill:
    """Generate docs at specified depth."""

    LEVELS = {
        0: "one_liner",
        1: "quick_start",
        2: "core_concepts",
        3: "detailed_guide",
        4: "deep_dive",
        5: "expert_reference",
    }

    async def generate(self, library: str, level: int):
        # Get appropriate depth
        method = getattr(self, f"_gen_{self.LEVELS[level]}")
        return await method(library)

    async def expand(self, section: str, current_level: int):
        """User-driven expansion."""
        return await self.generate(section, current_level + 1)
```

---

## 6. Zero-Hallucination

### Direct Dependency Retrieval (DDR)

**Hallucination Rate**: Hall_m < 0.02 (near-zero)

```python
class ZeroHallucinationGenerator:
    """Every claim grounded in source code."""

    async def generate(self, library: str):
        # 1. Retrieve actual code elements
        elements = await self.ddr.retrieve(library)

        # 2. Generate constrained to retrieved elements
        docs = []
        for element in elements:
            doc = await self._generate_from_element(element)
            doc.citation = f"{element.file}:{element.line}"
            docs.append(doc)

        # 3. Multi-agent verification
        return await self.auditor.verify(docs, elements)
```

### Verification Pipeline

```
Generator → Auditor → Publisher
    │           │          │
    ▼           ▼          ▼
 Create    Cross-check   Output
 from       against     verified
 source   knowledge     claims
           base
```

### Key Techniques

| Technique | Reduction | Source |
|-----------|-----------|--------|
| **DDR** | Hall_m < 0.02 | arxiv 2511.11990 |
| **Multi-Agent Audit** | 0% in knowledge base | arxiv 2512.23743 |
| **Streaming Detection** | 78% mid-process | arxiv 2601.02170 |
| **RAG Grounding** | Binds to evidence | arxiv 2601.01743 |

---

## 7. Development Frameworks

### BMAD Method

**Multi-agent agile framework with personas:**

| Agent | Role |
|-------|------|
| **QA** | Senior code review |
| **SM** | Story drafting |
| **Dev** | Implementation |

**Workflow**: Pre-Dev Ideation → Story Drafting → Development → QA Review

### Spec-Kit

**Spec-Driven Development toolkit:**

```bash
/specify <feature> <description>
# Creates: specs/active/<feature>/spec.md
```

**Template structure**:
- User stories
- Acceptance criteria
- Success metrics
- Edge cases
- QA checklist

### Daniel Miessler's Fabric

**219+ crowdsourced AI patterns:**

| Pattern | Purpose |
|---------|---------|
| `extract_wisdom` | Extract key insights |
| `analyze_code` | Code review/analysis |
| `create_summary` | Generate summaries |
| `suggest_pattern` | Recommend patterns |

**Usage**: `fabric <pattern_name> <input>`

### Ralph's Loop

**Iterative completion pattern:**

```bash
while [ ! completion_marker ]; do
    result=$(claude "$prompt")
    if contains_marker "$result"; then
        break
    fi
    prompt="$prompt\n$result"
    checkpoint
done
```

**Key features**:
- Fixed-prompt repetition
- Checkpointed progression
- TDD variant (until tests pass)
- Max-iteration cap

---

## 8. Claude Code Features

### Hooks

**Event-driven automation scripts:**

| Hook Type | Trigger |
|-----------|---------|
| **PreToolUse** | Before tool execution |
| **PostToolUse** | After tool execution |
| **UserPromptSubmit** | On user message |
| **SessionStart** | Session initialization |
| **PermissionRequest** | Permission checks |

**Configuration** (`settings.json`):
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "echo Validating..."
      }]
    }]
  }
}
```

### MCP Servers

**Model Context Protocol for external integrations:**

| Server | Purpose |
|--------|---------|
| **bruno-mcp** | API automation |
| **computer-use-mcp** | Computer control |
| **codex-mcp** | Blockchain data |
| **otlp-mcp** | OpenTelemetry |

### Slash Commands

**Reusable prompts via CLI:**
- `/review` - Code review
- `/specify` - Create specification
- `/ralph-loop` - Iterative execution

### Parallel Agents (Sub-agents)

**Concurrent specialized tasks:**

```python
# Complete isolation pattern
class ParallelSkillExecution:
    async def execute(self, tasks: List[Task]):
        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                # Each in independent sub-agent
                tg.create_task(self._spawn_subagent(task))
```

### Git Worktrees

**Isolation for parallel agent work:**

```bash
# Create isolated worktree for agent
git worktree add .worktrees/agent-1 -b feature-1

# Agent works in isolation
cd .worktrees/agent-1
# ... agent executes ...

# Cleanup
git worktree remove .worktrees/agent-1
```

---

## 9. Implementation Priorities

### Phase 1: Foundation (Core Infrastructure)

- [ ] Set up Perplexity/Brave/arXiv retrieval module ✅
- [ ] Implement Beads work orchestration
- [ ] Set up git worktree infrastructure
- [ ] Create 3-tier progressive disclosure structure

### Phase 2: Code Understanding

- [ ] Build hybrid AST + LLM parser
- [ ] Implement InlineCoder context inlining
- [ ] Create Cognee knowledge graph integration
- [ ] Set up Qwen3-Embedding + Zerank 2

### Phase 3: Zero-Hallucination

- [ ] Implement DDR (Direct Dependency Retrieval)
- [ ] Build multi-agent verification (Generator → Auditor)
- [ ] Create line-level citation system
- [ ] Set up grounding pipeline

### Phase 4: Production

- [ ] Implement Planner-Worker architecture
- [ ] Set up contextual-bandit routing
- [ ] Configure MAESTRO testing
- [ ] Add LangSmith/Langfuse observability

### Phase 5: Claude Integration

- [ ] Create hooks for workflow automation
- [ ] Build slash commands for skills
- [ ] Configure MCP servers
- [ ] Implement Ralph's Loop for iteration

---

## Key Research Sources

### Infrastructure (Rounds 1-4)
- arxiv.org/html/2601.01857v1 (Jenius-Agent)
- arxiv.org/html/2601.00481v1 (MAESTRO)
- arxiv.org/html/2601.01569v1 (CaveAgent)
- arxiv.org/html/2601.01885v1 (AgeMem)

### Skill Patterns (Round 5)
- arxiv.org/html/2511.11990v4 (DDR)
- arxiv.org/html/2601.01233v1 (Hybrid understanding)
- arxiv.org/html/2601.00376v1 (InlineCoder)

### Frameworks (Round 6)
- github.com/bmad-code-org/BMAD-METHOD
- github.com/danielmiessler/fabric
- github.com/mikeyobrien/ralph-orchestrator
- awesomeclaude.ai

---

## Quick Reference

### Target Metrics
- **Hallucination rate**: < 0.02
- **Execution cost**: ~$0.06/run
- **Accuracy gain**: 20% (Jenius patterns)

### Essential Patterns
1. **Plan-and-Execute + Reflection** (architecture)
2. **Hierarchical Supervisor** (orchestration)
3. **Hybrid AST + LLM** (code understanding)
4. **DDR** (zero-hallucination)
5. **3-Tier Progressive Disclosure** (UX)
6. **Git Worktrees** (parallel execution)
7. **Ralph's Loop** (iterative completion)

### Key Innovations
- **AgeMem**: RL-trained memory management
- **CaveAgent**: Dual-stream context
- **InlineCoder**: Call graph inlining
- **MAESTRO**: Framework-agnostic testing
