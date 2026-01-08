# Skills Fabric: BMAD v6 Comprehensive Development Plan

> **Document Type**: Living Specification
> **Created**: 2026-01-08
> **Methodology**: BMAD v6 (Breakthrough Multi-Agent Development)
> **Track**: Enterprise (Full Governance Suite)

---

## Executive Summary

This document presents a comprehensive BMAD v6 development and testing plan for the Skills Fabric project—a zero-hallucination Claude skill generation pipeline. The plan synthesizes deep analysis of the existing codebase (70% complete), BMAD v6 methodology principles, and industry best practices including MAESTRO threat modeling, AgentBench evaluation frameworks, and progressive disclosure architecture.

### Core Guarantee

```
Hall_m = rejected / (validated + rejected) < 0.02 (2%)
```

Every generated skill must be grounded in actual source code with `file:line` citations.

### Plan Structure

The plan follows BMAD v6's four-phase lifecycle:
1. **Analysis Phase** - Gap identification and research validation
2. **Planning Phase** - Scale-adaptive roadmap with PRD specifications
3. **Solutioning Phase** - Architecture design and agent orchestration
4. **Implementation Phase** - Story-driven development with continuous verification

---

# Phase 1: Analysis (Gap Identification & Research Validation)

## 1.1 Current State Assessment

### Codebase Architecture

```
skills_fabric/
├── src/skills_fabric/
│   ├── agents/          # Multi-agent orchestration (base.py, supervisor)
│   ├── analyze/         # AST parsing, Tree-sitter, LSP integration
│   ├── understanding/   # Progressive disclosure (Levels 0-5)
│   ├── verification/    # DDR pipeline, Hall_m tracking
│   ├── research/        # Perplexity/Brave integration
│   ├── storage/         # KuzuDB graph database
│   └── observability/   # Logging and metrics
├── tests/
│   ├── unit/           # AST, DDR tests
│   └── integration/    # Skill generation flows
├── openspec/           # Living specifications
│   ├── specs/core/     # Core system spec
│   └── changes/        # Change proposals
└── docs/
    ├── research/       # Round 5-6 findings
    └── bmad/           # BMAD methodology docs
```

### Implementation Maturity Matrix

| Component | Status | Maturity | Priority |
|-----------|--------|----------|----------|
| CLI Commands | ✅ Implemented | 80% | Medium |
| ASTParser | ✅ Implemented | 95% | Low |
| TreeSitterParser | ✅ Implemented | 85% | Low |
| DDR Pipeline | ⚠️ Partial | 60% | **Critical** |
| Progressive Disclosure | ✅ Implemented | 75% | High |
| Multi-Agent Supervisor | ⚠️ Partial | 50% | **Critical** |
| Research Loop (Perplexity) | ⚠️ Partial | 40% | High |
| KuzuDB Storage | ✅ Implemented | 70% | Medium |
| Hall_m Tracking | ⚠️ Partial | 45% | **Critical** |
| RalphWiggumLoop | ⚠️ Partial | 30% | High |

### Trust Hierarchy Verification

| Level | Name | Current Coverage | Target |
|-------|------|-----------------|--------|
| 1 | HardContent (100% trust) | 60% verified | 100% |
| 2 | VerifiedSoft (95% trust) | 40% verified | 95% |
| 3 | Unverified (0% trust) | N/A | Auto-reject |

## 1.2 Gap Analysis by Domain

### Critical Gaps (P0)

1. **Hall_m Enforcement Pipeline**
   - Missing: Threshold rejection system
   - Missing: Real-time hallucination rate tracking
   - Missing: Multi-agent audit cross-validation
   - Location: `src/skills_fabric/verification/`

2. **SupervisorAgent Orchestration**
   - Missing: DAG-based workflow execution
   - Missing: Stage transition logic (INIT → MINING → LINKING → WRITING → AUDITING → VERIFYING → STORING)
   - Missing: Error recovery and retry logic
   - Location: `src/skills_fabric/agents/supervisor.py`

3. **End-to-End Verification Flow**
   - Missing: Complete Miner → Linker → Writer → Auditor → Verifier pipeline
   - Missing: Confidence scoring for proven links
   - Missing: Source reference validation
   - Location: `src/skills_fabric/agents/`

### High Priority Gaps (P1)

4. **Research Loop Integration**
   - Missing: Convergence detection algorithm
   - Missing: Citation trust scoring (domain-based)
   - Missing: Max-depth and budget enforcement
   - Location: `src/skills_fabric/research/`

5. **Progressive Understanding Builder**
   - Missing: Level 4-5 expansion (deep dive, expert reference)
   - Missing: Semantic analysis enrichment
   - Missing: Execution proofs
   - Location: `src/skills_fabric/understanding/progressive_disclosure.py`

6. **RalphWiggumLoop Implementation**
   - Missing: Completion promise detection
   - Missing: Checkpoint creation and restoration
   - Missing: Max-iteration enforcement
   - Location: `src/skills_fabric/orchestration/`

### Medium Priority Gaps (P2)

7. **Test Coverage Expansion**
   - Missing: MAESTRO-style threat modeling tests
   - Missing: AgentBench multi-turn evaluation
   - Missing: Fuzz testing for AST edge cases

8. **Multi-Model Routing**
   - Missing: Contextual-bandit router
   - Missing: Planner-Worker delegation
   - Missing: Cost-aware model selection

9. **Parallel Agent Execution**
   - Missing: Git worktree isolation
   - Missing: Concurrent agent coordination
   - Missing: Result aggregation

## 1.3 Research Validation

### Industry Best Practices Applied

| Framework | Application to Skills Fabric |
|-----------|------------------------------|
| **MAESTRO** | Seven-layer threat modeling for agent security |
| **AgentBench** | Multi-turn evaluation across 8 environments |
| **DDR (Direct Dependency Retrieval)** | Hall_m < 0.02 through source grounding |
| **Fabric (Miessler PAI)** | Pattern-based prompt engineering |
| **BMAD v6** | Four-phase development with specialized agents |
| **Spec-Kit** | Structured specification for agent behaviors |

### Validated Architectural Decisions

1. **Hybrid AST + LLM** for code understanding (proven best-in-class)
2. **3-Tier Progressive Disclosure** for UX (industry standard)
3. **Multi-Agent Verification** for zero hallucination
4. **KuzuDB Graph Storage** for skill relationships
5. **OpenSpec Living Documentation** for spec-driven development

---

# Phase 2: Planning (Scale-Adaptive Roadmap)

## 2.1 Project Track Selection

Based on BMAD v6 complexity analysis:

| Factor | Assessment | Weight |
|--------|------------|--------|
| Lines of Code | ~15,000 | 3 |
| Agent Count | 5+ specialized agents | 4 |
| Integration Points | 4+ external APIs | 3 |
| Compliance Needs | Hall_m < 0.02 guarantee | 5 |
| **Total Score** | **Enterprise Track** | 15/20 |

**Selected Track**: Enterprise (Full Governance Suite)
- PRD + Architecture + UX + Test Strategy + Security Analysis
- Timeline: Phased implementation over 4 sprints

## 2.2 Sprint Planning

### Sprint 1: Core Pipeline Completion (P0 Gaps)

**Theme**: Zero-Hallucination Foundation

| Story | Agent | Complexity | Acceptance Criteria |
|-------|-------|------------|---------------------|
| S1.1: Hall_m Threshold System | Architect, Developer | L | Hall_m calculated per skill; > 0.02 rejected |
| S1.2: Supervisor Workflow Engine | Architect, Developer | XL | 7-stage DAG execution with state machine |
| S1.3: Auditor Agent Implementation | Developer, QA | L | Cross-validation with source refs |
| S1.4: Verifier Agent Implementation | Developer, QA | M | Final approval gate before storage |
| S1.5: Integration Test Suite | Test Architect | M | >80% pipeline coverage |

**Exit Criteria**:
- Hall_m tracking operational
- Complete Miner → Storage pipeline
- All P0 gaps addressed

### Sprint 2: Progressive Understanding Enhancement (P1 Gaps)

**Theme**: Deep Understanding Expansion

| Story | Agent | Complexity | Acceptance Criteria |
|-------|-------|------------|---------------------|
| S2.1: Research Loop Convergence | Developer | L | Citation overlap detection; auto-stop |
| S2.2: Level 4-5 Progressive Disclosure | Developer, UX | L | Deep dive and expert ref generation |
| S2.3: RalphWiggumLoop Integration | Developer | M | Completion promise; checkpointing |
| S2.4: Citation Trust Scoring | Developer | S | Domain-based scoring; >0.8 trusted |
| S2.5: Semantic Analysis Enrichment | Developer | M | Type signatures; behavior extraction |

**Exit Criteria**:
- Research loop fully functional
- All 6 progressive disclosure levels
- RalphWiggumLoop operational

### Sprint 3: Testing & Security Hardening (P2 Gaps)

**Theme**: Production Readiness

| Story | Agent | Complexity | Acceptance Criteria |
|-------|-------|------------|---------------------|
| S3.1: MAESTRO Threat Model | Security, Architect | L | 7-layer analysis documented |
| S3.2: AgentBench Evaluation Suite | Test Architect | L | Multi-turn test scenarios |
| S3.3: Fuzz Testing for Parsers | Developer, QA | M | Edge cases for AST/TreeSitter |
| S3.4: Contextual-Bandit Router | Developer | L | Model tier selection |
| S3.5: Parallel Agent Execution | Developer | L | Worktree isolation |

**Exit Criteria**:
- MAESTRO threat model complete
- >90% test coverage
- Multi-model routing operational

### Sprint 4: Optimization & Polish

**Theme**: Performance & Developer Experience

| Story | Agent | Complexity | Acceptance Criteria |
|-------|-------|------------|---------------------|
| S4.1: Cost-Aware Model Selection | Developer | M | Token budget enforcement |
| S4.2: CLI Experience Enhancement | UX, Developer | M | Improved error messages; progress bars |
| S4.3: Documentation Generation | Tech Writer | M | Auto-generated API docs |
| S4.4: Performance Profiling | Developer | S | Identify and fix bottlenecks |
| S4.5: Production Deployment Guide | DevOps | M | Docker/Kubernetes configs |

**Exit Criteria**:
- All features production-ready
- Documentation complete
- Performance optimized

## 2.3 Product Requirements Document (PRD)

### Vision Statement

Skills Fabric transforms any Python library into Claude-optimized skills with mathematically guaranteed zero hallucination (Hall_m < 0.02), using a multi-agent verification pipeline grounded in actual source code.

### Target Users

1. **Library Authors**: Generate accurate documentation skills from source
2. **AI Engineers**: Build reliable Claude skills for production
3. **Enterprise Teams**: Ensure compliance through verifiable citations

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hallucination Rate | < 2% | Hall_m = rejected / (validated + rejected) |
| Skill Generation Success | > 95% | Completed / Attempted |
| Average Generation Time | < 5 min | Per skill end-to-end |
| Test Coverage | > 90% | Lines covered / Total lines |
| User Satisfaction | > 4.5/5 | Post-generation survey |

### Non-Functional Requirements

1. **Reliability**: 99.9% uptime for CLI operations
2. **Scalability**: Handle repositories up to 100K LOC
3. **Security**: No credential leakage; sandboxed execution
4. **Observability**: Full tracing with OpenTelemetry

---

# Phase 3: Solutioning (Architecture Design)

## 3.1 Multi-Agent Architecture

### Agent Roster

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUPERVISOR AGENT                                    │
│  Responsibilities: Orchestration, State Management, Stage Transitions        │
│  Model: Claude Opus (complex reasoning)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ MINER AGENT   │          │ LINKER AGENT  │          │ WRITER AGENT  │
│ - Symbol      │          │ - Concept to  │          │ - Skill       │
│   extraction  │───────▶  │   symbol      │───────▶  │   generation  │
│ - Code mining │          │   matching    │          │ - Citation    │
│               │          │ - Confidence  │          │   injection   │
└───────────────┘          └───────────────┘          └───────────────┘
Model: Haiku               Model: Sonnet               Model: Sonnet
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    ▼
        ┌───────────────────────────┴───────────────────────────┐
        ▼                                                       ▼
┌───────────────┐                                      ┌───────────────┐
│ AUDITOR AGENT │                                      │VERIFIER AGENT │
│ - Hall_m calc │                                      │ - Final check │
│ - Source      │◀─────────────────────────────────────│ - Approval    │
│   validation  │                                      │   gate        │
│ - Cross-check │                                      │               │
└───────────────┘                                      └───────────────┘
Model: Opus                                            Model: Sonnet
```

### Workflow State Machine

```
              ┌──────────────────────────────────────────────────────────────┐
              │                                                              │
              ▼                                                              │
          ┌──────┐     ┌────────┐     ┌─────────┐     ┌─────────┐     ┌────────┐
START ──▶ │ INIT │ ──▶ │ MINING │ ──▶ │ LINKING │ ──▶ │ WRITING │ ──▶ │AUDITING│
          └──────┘     └────────┘     └─────────┘     └─────────┘     └────────┘
              │             │              │               │               │
              │             │              │               │               │
              ▼             ▼              ▼               ▼               ▼
          ┌──────┐     ┌────────┐     ┌─────────┐     ┌─────────┐     ┌────────┐
          │FAILED│◀────│ FAILED │◀────│ FAILED  │◀────│ FAILED  │◀────│ FAILED │
          └──────┘     └────────┘     └─────────┘     └─────────┘     └────────┘
                                                                           │
                                                                           ▼
                                                      ┌──────────┐     ┌────────┐
                                                      │VERIFYING │ ──▶ │STORING │
                                                      └──────────┘     └────────┘
                                                           │               │
                                                           ▼               ▼
                                                      ┌──────────┐     ┌────────┐
                                                      │  FAILED  │     │COMPLETE│
                                                      └──────────┘     └────────┘
```

## 3.2 DDR (Direct Dependency Retrieval) Pipeline

### Verification Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DDR VERIFICATION PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Source Code ──▶ ASTParser ──▶ Symbol Extraction ──▶ EnhancedSymbol        │
│       │                              │                       │              │
│       │                              ▼                       ▼              │
│       │         ┌─────────────────────────────────────────────────┐        │
│       │         │                  DDR Engine                      │        │
│       │         │  ┌────────────────────────────────────────────┐ │        │
│       │         │  │ Multi-Source Validation                    │ │        │
│       │         │  │  - AST Parse Match (100% trust)            │ │        │
│       │         │  │  - Tree-sitter Parse (95% trust)           │ │        │
│       │         │  │  - LSP Resolution (90% trust)              │ │        │
│       │         │  │  - File Content Grep (85% trust)           │ │        │
│       │         │  └────────────────────────────────────────────┘ │        │
│       │         └─────────────────────────────────────────────────┘        │
│       │                              │                                      │
│       │                              ▼                                      │
│       │                    ┌─────────────────┐                             │
│       │                    │  SourceRef      │                             │
│       │                    │  file:line:col  │                             │
│       │                    │  commit:sha     │                             │
│       │                    │  trust_level    │                             │
│       │                    └─────────────────┘                             │
│       │                              │                                      │
│       ▼                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    HALLUCINATION GATE                                │   │
│  │                                                                      │   │
│  │    validated_claims ──────────────────────────▶ skill_claims         │   │
│  │                                                       │              │   │
│  │    unvalidated_claims ──▶ REJECTION_QUEUE             │              │   │
│  │                                   │                   │              │   │
│  │    Hall_m = rejected / (validated + rejected)         │              │   │
│  │                                   │                   │              │   │
│  │         IF Hall_m > 0.02 ─────────┼──────▶ REJECT_SKILL              │   │
│  │         IF Hall_m ≤ 0.02 ─────────┼──────▶ APPROVE_SKILL ────────────┘   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.3 Progressive Disclosure Architecture

### Level Structure

```
Level 0: Executive Summary (1 sentence)
├── "LangGraph is a framework for building stateful agents with cycles"
│
Level 1: Quick Start (30 seconds)
├── Purpose + Install + Hello World
├── pip install langgraph
└── 5-line example
│
Level 2: Core Concepts (5 minutes)
├── StateGraph, Nodes, Edges
├── Key patterns with examples
├── SourceRefs for each concept
└── Common use cases
│
Level 3: Detailed Guide (30 minutes)
├── Full API coverage
├── All parameters explained
├── Error handling patterns
└── SourceRefs with file:line citations
│
Level 4: Deep Implementation (2+ hours)
├── Source code walkthrough
├── Internal architecture diagrams
├── Extension mechanisms
├── SemanticInfo: type signatures, behaviors
└── ExecutionProofs: verified examples
│
Level 5: Expert Reference
├── Edge cases and gotchas
├── Performance optimization
├── Contribution guide
├── Complete call graphs
└── Full audit trail
```

### UnderstandingNode Schema

```python
@dataclass
class UnderstandingNode:
    """A node in the progressive understanding tree."""

    id: str                          # Unique identifier
    title: str                       # Display title
    level: DepthLevel               # 0-5 depth
    content: str                     # Markdown content
    parent_id: Optional[str]         # Parent node ID
    children_ids: List[str]          # Child node IDs
    source_refs: List[SourceRef]     # Grounding citations
    semantic_info: Optional[SemanticInfo]  # Level 4+ metadata
    execution_proofs: List[ExecutionProof] # Level 5 verification
    keywords: Set[str]               # Search indexing

    @property
    def is_expanded(self) -> bool:
        """Check if node is fully expanded for its level."""
        if self.level >= DepthLevel.SOURCE_REFERENCES:
            return len(self.source_refs) > 0
        if self.level >= DepthLevel.SEMANTIC_ANALYSIS:
            return self.semantic_info is not None
        return True
```

## 3.4 Research Loop Architecture

### Convergence Detection

```python
class ResearchLoop:
    """Autonomous research with convergence detection."""

    def __init__(
        self,
        perplexity_client: PerplexityClient,
        max_depth: int = 5,
        convergence_threshold: float = 0.8,
        token_budget: int = 100000
    ):
        self.client = perplexity_client
        self.max_depth = max_depth
        self.convergence_threshold = convergence_threshold
        self.token_budget = token_budget

    async def research(self, initial_query: str) -> ResearchFindings:
        """Execute research loop until convergence or budget."""

        findings = []
        queries = [initial_query]
        seen_citations = set()
        tokens_used = 0

        for depth in range(self.max_depth):
            if not queries:
                break  # NO_NEW_QUERIES

            if tokens_used >= self.token_budget:
                break  # BUDGET_EXHAUSTED

            # Execute query batch
            responses = await self._batch_query(queries)
            tokens_used += sum(r.token_count for r in responses)

            # Extract findings and citations
            new_findings, new_citations = self._extract(responses)
            findings.extend(new_findings)

            # Calculate convergence
            overlap = self._calculate_overlap(seen_citations, new_citations)
            if overlap >= self.convergence_threshold:
                break  # CONVERGED

            # Update state
            seen_citations.update(new_citations)
            queries = self._generate_followups(responses)

        return ResearchFindings(
            findings=findings,
            citations=list(seen_citations),
            depth_reached=depth,
            convergence_score=overlap,
            tokens_used=tokens_used
        )
```

## 3.5 MAESTRO Security Model

### Seven-Layer Threat Analysis

| Layer | Skills Fabric Component | Threats | Mitigations |
|-------|------------------------|---------|-------------|
| 1. Model | Claude API | Prompt injection | Input sanitization; system prompt hardening |
| 2. Perception | ASTParser, TreeSitter | Malicious code parsing | Sandboxed parsing; timeout limits |
| 3. Reasoning | Agent decision logic | Goal misalignment | Explicit constraints; human oversight |
| 4. Tool Use | CLI commands, file ops | Command injection | Allowlist commands; path validation |
| 5. Memory | KuzuDB, conversation | Data poisoning | Schema validation; access control |
| 6. Communication | Inter-agent messaging | Message tampering | Signed messages; audit logs |
| 7. Orchestration | Supervisor workflow | Control hijacking | State machine enforcement |

### Security Controls

```python
class SecurityLayer:
    """MAESTRO-aligned security controls."""

    # Layer 1: Model Protection
    ALLOWED_MODELS = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]

    # Layer 2: Perception Limits
    MAX_FILE_SIZE = 10_000_000  # 10MB
    PARSE_TIMEOUT = 30  # seconds

    # Layer 4: Tool Allowlist
    ALLOWED_COMMANDS = ["git", "python", "pytest", "pip"]
    BLOCKED_PATHS = ["/etc", "/root", ".ssh", ".aws"]

    # Layer 5: Memory Validation
    MAX_CONTEXT_SIZE = 100_000  # tokens

    # Layer 7: Workflow Constraints
    MAX_AGENT_TURNS = 50
    MAX_RETRY_COUNT = 3
```

---

# Phase 4: Implementation (Story-Driven Development)

## 4.1 Sprint 1 Stories

### S1.1: Hall_m Threshold System

**As a** Skills Fabric user
**I want** automatic rejection of skills with hallucination rate > 2%
**So that** I can trust all generated skills are grounded in source code

**Acceptance Criteria**:
- [ ] HallMetric class calculates Hall_m = rejected / (validated + rejected)
- [ ] Threshold of 0.02 enforced in Auditor agent
- [ ] Rejected skills logged with detailed reason
- [ ] Hall_m displayed in CLI output
- [ ] Unit tests for edge cases (0/0, 100% valid, 100% rejected)

**Technical Notes**:
```python
# Location: src/skills_fabric/verification/hallucination.py

@dataclass
class HallMetric:
    """Hallucination rate metric."""

    validated: int = 0
    rejected: int = 0

    @property
    def hall_m(self) -> float:
        total = self.validated + self.rejected
        if total == 0:
            return 0.0
        return self.rejected / total

    def is_acceptable(self, threshold: float = 0.02) -> bool:
        return self.hall_m <= threshold
```

### S1.2: Supervisor Workflow Engine

**As a** Skills Fabric system
**I want** a robust state machine for the 7-stage pipeline
**So that** skill generation proceeds reliably from start to finish

**Acceptance Criteria**:
- [ ] WorkflowState enum with all 9 stages
- [ ] DAG-based execution with dependency resolution
- [ ] Error handling with FAILED state transitions
- [ ] Retry logic (max 3 attempts per stage)
- [ ] Progress tracking exposed to CLI
- [ ] Integration tests for full pipeline

**Technical Notes**:
```python
# Location: src/skills_fabric/agents/supervisor.py

class WorkflowStage(Enum):
    INIT = "init"
    MINING = "mining"
    LINKING = "linking"
    WRITING = "writing"
    AUDITING = "auditing"
    VERIFYING = "verifying"
    STORING = "storing"
    COMPLETE = "complete"
    FAILED = "failed"

class SupervisorAgent:
    """Orchestrates multi-agent skill generation workflow."""

    TRANSITIONS = {
        WorkflowStage.INIT: [WorkflowStage.MINING, WorkflowStage.FAILED],
        WorkflowStage.MINING: [WorkflowStage.LINKING, WorkflowStage.FAILED],
        WorkflowStage.LINKING: [WorkflowStage.WRITING, WorkflowStage.FAILED],
        WorkflowStage.WRITING: [WorkflowStage.AUDITING, WorkflowStage.FAILED],
        WorkflowStage.AUDITING: [WorkflowStage.VERIFYING, WorkflowStage.FAILED],
        WorkflowStage.VERIFYING: [WorkflowStage.STORING, WorkflowStage.FAILED],
        WorkflowStage.STORING: [WorkflowStage.COMPLETE, WorkflowStage.FAILED],
    }
```

### S1.3: Auditor Agent Implementation

**As a** skill generation pipeline
**I want** an Auditor agent that validates claims against source
**So that** ungrounded claims are identified and rejected

**Acceptance Criteria**:
- [ ] Auditor receives skill content and source refs
- [ ] Each claim extracted and validated against refs
- [ ] Hall_m calculated for skill
- [ ] Detailed audit report generated
- [ ] Skills with Hall_m > 0.02 marked as FAILED
- [ ] Audit logs persisted for traceability

### S1.4: Verifier Agent Implementation

**As a** skill generation pipeline
**I want** a final Verifier gate before storage
**So that** only fully approved skills enter the database

**Acceptance Criteria**:
- [ ] Verifier receives audited skill
- [ ] Final consistency check performed
- [ ] Approval/rejection decision logged
- [ ] Passed skills forwarded to storage
- [ ] Failed skills added to rejection queue

### S1.5: Integration Test Suite

**As a** development team
**I want** comprehensive integration tests for the pipeline
**So that** regressions are caught before release

**Acceptance Criteria**:
- [ ] End-to-end test from CLI to storage
- [ ] Mock agents for isolated testing
- [ ] Hall_m threshold test scenarios
- [ ] Error handling path coverage
- [ ] >80% pipeline code coverage

## 4.2 Testing Strategy

### Test Pyramid

```
                    ┌─────────────────┐
                    │   E2E Tests     │  5%
                    │  (Full Pipeline)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Integration     │  15%
                    │ (Multi-Agent)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Component      │  30%
                    │ (Single Agent)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Unit Tests    │  50%
                    │ (Functions)     │
                    └─────────────────┘
```

### AgentBench-Style Evaluation

```python
class AgentBenchEvaluation:
    """Multi-turn agent evaluation framework."""

    EVALUATION_SCENARIOS = [
        # Scenario: Simple library documentation
        {
            "name": "simple_lib",
            "repo": "fixtures/simple_lib",
            "expected_skills": 3,
            "max_turns": 10,
            "hall_m_threshold": 0.02,
        },
        # Scenario: Complex library with edge cases
        {
            "name": "complex_lib",
            "repo": "fixtures/complex_lib",
            "expected_skills": 15,
            "max_turns": 50,
            "hall_m_threshold": 0.02,
        },
        # Scenario: Error recovery
        {
            "name": "error_recovery",
            "repo": "fixtures/malformed_lib",
            "expected_skills": 0,  # Should gracefully fail
            "max_turns": 5,
            "expected_state": "FAILED",
        },
    ]

    async def run_evaluation(self) -> EvaluationReport:
        """Execute all evaluation scenarios."""
        results = []
        for scenario in self.EVALUATION_SCENARIOS:
            result = await self._run_scenario(scenario)
            results.append(result)
        return EvaluationReport(results=results)
```

## 4.3 Continuous Validation

### Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: hall-m-check
        name: Hall_m Threshold Check
        entry: pytest tests/unit/test_hallucination.py -v
        language: system
        pass_filenames: false

      - id: type-check
        name: Type Check
        entry: mypy src/skills_fabric
        language: system

      - id: lint
        name: Lint
        entry: ruff check src/skills_fabric
        language: system
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: Skills Fabric CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run unit tests
        run: pytest tests/unit -v --cov=src/skills_fabric

      - name: Run integration tests
        run: pytest tests/integration -v -m "not requires_api"

      - name: Check Hall_m compliance
        run: pytest tests/ -k "hall" -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

# Appendices

## A. BMAD Agent Mapping

| BMAD Agent | Skills Fabric Role | Responsibilities |
|------------|-------------------|------------------|
| Product Manager | Requirements Lead | PRD maintenance; success metrics |
| Architect | System Designer | Multi-agent architecture; DDR pipeline |
| Developer | Implementation Lead | Core pipeline; agents |
| UX Designer | CLI Experience | Progressive disclosure UX |
| Test Architect | Quality Lead | Test strategy; AgentBench evaluation |
| Scrum Master | Sprint Lead | Story management; blockers |
| Tech Writer | Documentation | API docs; user guides |
| QA Agent | Verification | Auditor/Verifier implementation |

## B. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Language | Python 3.11+ | Core implementation |
| Framework | LangGraph | Agent orchestration |
| Database | KuzuDB | Graph storage for skills |
| Parsing | Tree-sitter, AST | Multi-language code analysis |
| API Client | Anthropic SDK | Claude integration |
| Research | Perplexity API | External knowledge |
| Search | Brave API | Documentation discovery |
| Testing | pytest | Test framework |
| CI/CD | GitHub Actions | Automation |

## C. References

### Industry Frameworks
- [MAESTRO Threat Modeling](https://medium.com/@oracle_43885/maestro-orchestrating-next-generation-security-for-the-agentic-ai-revolution)
- [AgentBench Evaluation](https://o-mega.ai/articles/the-best-ai-agent-evals-and-benchmarks-full-2025-guide)
- [BMAD Method v6](https://github.com/bmad-code-org/BMAD-METHOD)

### Research Papers
- DDR: Hall_m < 0.02 (arxiv.org/html/2511.11990v4)
- Hybrid AST+LLM (arxiv.org/html/2601.01233v1)
- Contextual-Bandit Routing (arxiv.org/html/2512.24008v1)
- InlineCoder (arxiv.org/html/2601.00376v1)

### Existing Documentation
- `docs/ARCHITECTURE.md` - System architecture
- `docs/PROOF_BASED_ARCHITECTURE.md` - Verification approach
- `docs/research/summaries/SKILL_IMPLEMENTATION_PATTERNS.md` - Implementation patterns
- `openspec/specs/core/spec.md` - Core specification

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-08 | Claude Opus 4.5 | Initial BMAD v6 plan creation |

---

*This is a living document maintained according to BMAD v6 methodology.*
