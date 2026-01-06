# Skill Implementation Patterns

> **Generated**: January 2026
> **Source**: Round 5 Research (12 queries, 120 citations)
> **Purpose**: Zero-hallucination progressive disclosure code skill implementation

---

## Executive Summary

Round 5 research filled critical gaps for our specific skill implementation. Key findings:

1. **Git worktrees** provide isolation for parallel multi-agent work
2. **3-tier progressive disclosure** is the proven UX pattern
3. **Hybrid AST+LLM** is best for code understanding
4. **Direct Dependency Retrieval** achieves near-zero hallucination (Hall_m < 0.02)
5. **Planner-Worker architecture** with contextual routing optimizes model usage

---

## 1. Parallel Execution with Git Worktrees

### Why Worktrees for AI Agents
- **Isolation**: Agents don't perform well when files change beneath them
- **Parallel work**: Multiple agents can work on logically separate features
- **Safety boundary**: Contains experimental/problematic actions

### Tools
| Tool | Purpose |
|------|---------|
| **Worktrunk** | CLI for git worktree management with AI agents |
| **Workmux** | Combines git worktrees with tmux windows |

### Implementation Pattern
```python
class ParallelAgentExecutor:
    """Execute multiple agents in isolated worktrees."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.worktrees = {}

    async def create_worktree(self, agent_id: str, branch: str) -> Path:
        """Create isolated worktree for agent."""
        worktree_path = self.repo_path.parent / f".worktrees/{agent_id}"

        # Create worktree on dedicated branch
        await run(f"git worktree add {worktree_path} -b {branch}")

        self.worktrees[agent_id] = worktree_path
        return worktree_path

    async def execute_parallel(self, tasks: List[AgentTask]):
        """Run agents in parallel worktrees."""
        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                worktree = await self.create_worktree(task.agent_id, task.branch)
                tg.create_task(task.agent.execute(cwd=worktree))

    async def cleanup(self, agent_id: str):
        """Remove worktree after agent completes."""
        worktree_path = self.worktrees.pop(agent_id)
        await run(f"git worktree remove {worktree_path}")
```

### Key Insight
> "AI agents don't perform well when files change beneath them as they execute their plans, so worktrees solve this by giving each agent a separate working directory."

---

## 2. Progressive Disclosure Architecture

### 3-Tier Model

| Tier | Content | Visibility | Example |
|------|---------|------------|---------|
| **Tier 1: Overview** | Brief summaries, purpose | Always visible | Library name, quick install |
| **Tier 2: Intermediate** | Key examples, patterns | On-demand | Common code snippets |
| **Tier 3: Deep** | Full specs, edge cases | Expanded | Signal definitions, raw code |

### Implementation Structure
```
Level 0: One-Liner
├── "LangGraph is a framework for building stateful agents with cycles"

Level 1: Quick Start (30 seconds)
├── Purpose + Install + Hello World
├── pip install langgraph
└── 5-line example

Level 2: Core Concepts (5 minutes)
├── StateGraph, Nodes, Edges
├── Key patterns with examples
└── Common use cases

Level 3: Detailed Guide (30 minutes)
├── Full API coverage
├── All parameters explained
├── Error handling patterns

Level 4: Deep Implementation (2+ hours)
├── Source code walkthrough
├── Internal architecture
├── Extension mechanisms

Level 5: Expert Reference
├── Edge cases, gotchas
├── Performance optimization
└── Contribution guide
```

### UX Patterns
```python
class ProgressiveDisclosureSkill:
    """Generate documentation at multiple depth levels."""

    LEVELS = {
        0: "one_liner",      # 1 sentence
        1: "quick_start",    # 30 seconds
        2: "core_concepts",  # 5 minutes
        3: "detailed_guide", # 30 minutes
        4: "deep_dive",      # 2+ hours
        5: "expert_ref",     # Complete reference
    }

    async def generate(self, library: str, level: int) -> Documentation:
        """Generate docs at specified depth level."""

        if level == 0:
            return await self._generate_one_liner(library)
        elif level == 1:
            return await self._generate_quick_start(library)
        # ... progressive expansion

    async def expand(self, section: str, current_level: int) -> Documentation:
        """User-driven expansion of specific section."""
        return await self.generate(section, current_level + 1)
```

### Key Insight
> "Progressive disclosure structures content in tiers to match user needs, loading only essential details initially."

---

## 3. Zero-Hallucination Code Documentation

### Core Technique: Direct Dependency Retrieval (DDR)

**Hallucination Rate**: Hall_m < 0.02 (near-zero)

```python
class GroundedDocGenerator:
    """Generate documentation grounded in actual source code."""

    def __init__(self):
        self.retriever = DependencyRetriever()
        self.verifier = NeuroSymbolicVerifier()

    async def generate(self, library: str) -> Documentation:
        # 1. Retrieve actual code elements
        code_elements = await self.retriever.retrieve(library)

        # 2. Generate documentation constrained to retrieved elements
        docs = await self._generate_constrained(code_elements)

        # 3. Verify every claim against source
        verified_docs = await self.verifier.verify(docs, code_elements)

        return verified_docs

    async def _generate_constrained(self, elements: List[CodeElement]):
        """Generate only from verified elements."""
        for element in elements:
            # Cite exact locations
            doc = f"**{element.name}** (Line {element.line} in `{element.file}`)"
            doc += await self._describe_from_source(element)
            yield doc
```

### Multi-Agent Verification Pattern
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Generator     │───▶│    Auditor      │───▶│   Publisher     │
│   (creates)     │    │   (verifies)    │    │   (outputs)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                     │                       │
         ▼                     ▼                       ▼
   Generate docs         Cross-check vs         Only publish
   from source           knowledge base         verified claims
```

### Verification Techniques

| Technique | Hallucination Reduction | Use Case |
|-----------|------------------------|----------|
| **DDR (Direct Dependency Retrieval)** | Hall_m < 0.02 | API documentation |
| **RAG Grounding** | Binds to evidence | General docs |
| **Multi-Agent Auditor** | 0% in knowledge base | Production systems |
| **Streaming Detection** | 78% mid-process | Real-time verification |

### Key Insight
> "Hybrid neuro-symbolic architectures achieve 0% hallucination rates for covered codebases by cross-checking generated documentation against a knowledge base of code snippets."

---

## 4. Code Understanding Pipeline

### Hybrid AST + LLM Approach (Best in Class)

```
Source Code
     │
     ▼
┌─────────────┐
│  AST Parse  │──── Precise structure, dependencies
└─────────────┘
     │
     ▼
┌─────────────┐
│ LLM Enrich  │──── Semantic purpose, behavior
└─────────────┘
     │
     ▼
┌─────────────┐
│   Merge     │──── Factually grounded + semantically rich
└─────────────┘
```

### Implementation by Granularity

```python
class HybridCodeUnderstanding:
    """Combine AST precision with LLM semantics."""

    def __init__(self):
        self.ast_parser = ASTParser()
        self.llm = LLMClient()

    async def understand_function(self, func: str) -> FunctionDoc:
        """Function-level: AST slicing + LLM purpose."""
        # AST: Extract precise dependencies
        ast_info = self.ast_parser.backward_slice(func)

        # LLM: Infer purpose with Chain-of-Thought
        purpose = await self.llm.infer_purpose(func, ast_info)

        return FunctionDoc(
            name=ast_info.name,
            dependencies=ast_info.dependencies,  # Factual from AST
            purpose=purpose,  # Semantic from LLM
            line_numbers=ast_info.line_numbers,  # Citation
        )

    async def understand_repo(self, repo_path: Path) -> RepoDoc:
        """Repo-level: InlineCoder + call graph."""
        # Build call graph
        call_graph = self.ast_parser.build_call_graph(repo_path)

        # Inline context for multi-perspective understanding
        context = await self._inline_context(call_graph)

        # LLM: Generate holistic understanding
        return await self.llm.summarize_repo(context)
```

### Key Tools

| Level | AST Technique | LLM Enhancement |
|-------|--------------|-----------------|
| **Function** | Backward slicing | CoT purpose inference |
| **Class** | Subgraph extraction | Method/attribute summary |
| **Module** | Import/export analysis | RAG + rescoring |
| **Repo** | Call graph construction | InlineCoder context |

### Key Insight
> "Hybrid approaches combining LLMs with AST-based techniques dominate, excelling in extracting purpose, behavior, and dependencies while ensuring factual grounding."

---

## 5. Multi-Model Delegation

### Planner-Worker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PLANNER (Large Model)                     │
│  - Decomposes goals into sub-tasks                          │
│  - High-level reasoning and planning                        │
│  - Context handoff via structured memory                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────┐                         ┌───────────────┐
│ WORKER (Small)│                         │ WORKER (Small)│
│ - Execute task│                         │ - Execute task│
│ - Fast/cheap  │                         │ - Fast/cheap  │
└───────────────┘                         └───────────────┘
```

### Contextual-Bandit Routing

```python
class AdaptiveRouter:
    """Route tasks to appropriate model tier."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.router_weights = self._load_weights()

    async def route(self, query: str, context: Context) -> ModelTier:
        """Select model based on task complexity."""
        # Extract features
        features = self.feature_extractor.extract(query, context)

        # Softmax-based routing
        scores = softmax(self.router_weights @ features)

        # Select tier
        if scores['simple'] > 0.7:
            return ModelTier.FAST  # Haiku-equivalent
        elif scores['complex'] > 0.5:
            return ModelTier.BALANCED  # Sonnet-equivalent
        else:
            return ModelTier.POWERFUL  # Opus-equivalent

    async def execute_with_routing(self, task: Task) -> Result:
        tier = await self.route(task.query, task.context)

        # Fast path for routine, verified for high-risk
        if tier == ModelTier.FAST and not task.is_high_risk:
            return await self.fast_model.execute(task)
        else:
            result = await self.powerful_model.execute(task)
            if task.is_high_risk:
                result = await self.verify(result)
            return result
```

### Warp-Cortex Pattern (River & Stream)

```
Main Agent (High Priority)
     │
     ├──▶ Side Agent 1 (Medium) ──▶ Fact-checking
     │
     ├──▶ Side Agent 2 (Medium) ──▶ Logic verification
     │
     └──▶ Side Agent 3 (Medium) ──▶ Code validation

Agents spawned just-in-time, conserving resources
```

### Key Insight
> "The most impactful improvements often come from changing the decision loop rather than changing the base model."

---

## 6. Repository-Level Understanding

### InlineCoder Pattern

```python
class RepoUnderstanding:
    """Repository-level code understanding."""

    async def inline_context(self, target_function: str) -> Context:
        """Inline unfinished functions into call graph."""

        # 1. Build call graph
        call_graph = await self.build_call_graph()

        # 2. Identify target in graph
        node = call_graph.find(target_function)

        # 3. Inline upstream/downstream context
        context = Context()
        context.add_imports(node.imports)
        context.add_callers(node.callers)
        context.add_callees(node.callees)
        context.add_prior_drafts(node.drafts)

        return context
```

### RepoNavigator (RL-based Symbol Jumping)

```python
class RepoNavigator:
    """RL agent for repository navigation."""

    async def navigate(self, query: str) -> List[CodeLocation]:
        """Navigate repo using symbol jumping."""

        locations = []
        current = self.entry_point

        while not self.done:
            # Reasoning step
            reasoning = await self.reason(query, current)

            # Action: jump to symbol definition
            target = await self.jump_to_definition(reasoning.target_symbol)

            if target:
                locations.append(target)
                current = target

            # Optimized via GRPO for long-horizon trajectories

        return locations
```

### Key Insight
> "Context inlining and call graph integration represent a primary advancement, reframing repository-level understanding as function-level coding tasks."

---

## 7. Complete Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROGRESSIVE DISCLOSURE SKILL                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  INPUT: Library name + depth level (0-5)                            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   PLANNER (Opus-equivalent)                   │    │
│  │  - Analyze library structure                                  │    │
│  │  - Decompose into documentation tasks                         │    │
│  │  - Route to appropriate workers                               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│      ┌───────────────────────┼───────────────────────┐              │
│      ▼                       ▼                       ▼              │
│  ┌────────┐            ┌────────┐            ┌────────┐            │
│  │ Worker │            │ Worker │            │ Worker │            │
│  │ (AST)  │            │ (LLM)  │            │(Verify)│            │
│  └────────┘            └────────┘            └────────┘            │
│      │                       │                       │              │
│      └───────────────────────┼───────────────────────┘              │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   GROUNDED DOCUMENTATION                      │    │
│  │  - Every claim cited to source (file:line)                   │    │
│  │  - DDR: Hall_m < 0.02                                        │    │
│  │  - 3-tier progressive disclosure                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  OUTPUT: Level-appropriate documentation                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Key Research Sources

| Topic | Key Source | Finding |
|-------|-----------|---------|
| **Worktrees** | github.com/banteg/agents | Isolation prevents conflicts |
| **Progressive Disclosure** | github.com/muratcankoylan/Agent-Skills | 3-tier model |
| **Zero-Hallucination** | arxiv.org/html/2511.11990v4 | DDR Hall_m < 0.02 |
| **Hybrid Understanding** | arxiv.org/html/2601.01233v1 | AST+LLM best |
| **Model Routing** | arxiv.org/html/2512.24008v1 | Contextual-bandit |
| **Hierarchical LLM** | arxiv.org/html/2506.13324v2 | Planner-Worker |
| **Repo Understanding** | arxiv.org/html/2601.00376v1 | InlineCoder |
| **Grounded Docs** | arxiv.org/html/2512.18748v2 | Code2Doc pipeline |

---

## 9. Implementation Priorities

### Phase 1: Foundation
- [ ] Set up git worktree infrastructure for parallel agents
- [ ] Implement 3-tier progressive disclosure structure
- [ ] Build AST parser for Python libraries

### Phase 2: Code Understanding
- [ ] Hybrid AST+LLM understanding pipeline
- [ ] InlineCoder-style context inlining
- [ ] Call graph construction

### Phase 3: Zero-Hallucination
- [ ] Direct Dependency Retrieval (DDR)
- [ ] Multi-agent verification (Generator → Auditor)
- [ ] Line-level citation system

### Phase 4: Multi-Model Optimization
- [ ] Contextual-bandit router
- [ ] Planner-Worker architecture
- [ ] Cost-aware model selection
