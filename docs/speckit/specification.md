# Skills Fabric - Technical Specification

> SpecKit Specification Document
> Version: 1.0.0 | Created: 2026-01-07

---

## 1. System Overview

### 1.1 Purpose

Skills Fabric is a **zero-hallucination skill generation pipeline** that creates Claude-compatible skills from real source code. Every generated skill is grounded in verifiable source references.

### 1.2 Core Value Proposition

```
INPUT:  Library name (e.g., "langgraph")
OUTPUT: Verified skills with file:line citations
GUARANTEE: Hall_m < 0.02 (less than 2% hallucination rate)
```

### 1.3 System Boundaries

**In Scope:**
- Source code ingestion (Git clone)
- Documentation crawling (CodeWiki)
- Symbol extraction (AST, Tree-sitter, LSP)
- Multi-source validation
- Skill generation with citations
- Hallucination tracking and enforcement

**Out of Scope:**
- Runtime skill execution
- User authentication/authorization
- Cloud deployment orchestration
- Real-time collaboration

---

## 2. Functional Requirements

### 2.1 CLI Commands

| Command | Input | Output | Validation |
|---------|-------|--------|------------|
| `generate <library>` | Library name, depth 0-5 | Progressive understanding JSON | Hall_m < 0.02 |
| `verify <query>` | Symbol name | DDRResult with citations | Multi-source check |
| `analyze <path>` | File or directory | EnhancedSymbol list | Syntax validity |
| `research <topic>` | Search query | Perplexity response | Citation present |
| `search <query>` | Search query | Brave search results | Results returned |
| `version` | None | Version string | Format valid |

### 2.2 Core Workflows

#### 2.2.1 Skill Generation Workflow

```
1. INGEST
   - Clone repository (if not local)
   - Crawl documentation via CodeWiki
   - Fetch Context7 docs (if available)

2. ANALYZE
   - Extract symbols using AST/Tree-sitter
   - Build symbol graph with relationships
   - Generate embeddings for similarity search

3. LINK
   - Match documentation concepts to code symbols
   - Create PROVEN links with confidence scores
   - Filter links below confidence threshold

4. GENERATE
   - Create skill content using LLM
   - Add file:line citations for every claim
   - Track source references

5. VERIFY
   - Validate citations against actual source
   - Multi-source symbol verification
   - Calculate Hall_m metric

6. STORE
   - Persist skills to KuzuDB
   - Create TEACHES and USES relationships
   - Record verification results
```

#### 2.2.2 Verification Workflow

```
1. SEARCH
   - Query symbol catalog
   - Identify potential matches

2. VALIDATE (Multi-Source)
   - AST Parser: Extract from Python AST
   - Tree-sitter: Multi-language support
   - LSP: Type info and cross-refs
   - File Content: Direct grep

3. SCORE
   - Count sources confirming symbol
   - Calculate confidence: confirmed/checked
   - High confidence: >= 2 sources

4. TRACK
   - Record validated/rejected counts
   - Calculate Hall_m
   - Fail if threshold exceeded
```

### 2.3 Data Structures

#### 2.3.1 EnhancedSymbol
```python
@dataclass
class EnhancedSymbol:
    name: str              # Symbol name
    kind: str              # class, function, method
    file_path: str         # Absolute file path
    line: int              # Start line (1-indexed)
    end_line: int          # End line
    signature: str         # Function signature
    docstring: str         # Documentation
    parameters: list       # Function parameters
    return_type: str       # Return type annotation
    decorators: list       # Decorator names
    calls: list            # Called functions
    is_async: bool         # Async function
```

#### 2.3.2 SourceRef
```python
@dataclass
class SourceRef:
    symbol_name: str       # What was found
    file_path: str         # Where found
    line_number: int       # Line (1-indexed)
    end_line: int          # End line
    symbol_type: str       # class, function, etc.
    signature: str         # Rich metadata
    docstring: str         # Documentation
    validated: bool        # Verified against source

    @property
    def citation(self) -> str:
        return f"{self.file_path}:{self.line_number}"
```

#### 2.3.3 DDRResult
```python
@dataclass
class DDRResult:
    query: str                    # Original query
    elements: list[CodeElement]   # Validated elements
    validated_count: int          # Symbols confirmed
    rejected_count: int           # Symbols rejected
    hallucination_rate: float     # Hall_m value
    success: bool                 # Hall_m < threshold
```

### 2.4 Trust Levels

| Level | Name | Trust | Requirements |
|-------|------|-------|--------------|
| 1 | HardContent | 100% | AST/SCIP verified, file:line citation |
| 2 | VerifiedSoft | 95% | LLM + sandbox passes, grounding check |
| 3 | Unverified | 0% | REJECTED - no source reference |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Metric | Target | Current |
|--------|--------|---------|
| Single file analysis | < 100ms | ~50ms |
| Directory analysis (100 files) | < 10s | ~5s |
| Symbol verification | < 50ms | ~30ms |
| Batch verification (100 symbols) | < 5s | ~3s |
| Full skill generation | < 60s | ~45s |

### 3.2 Scalability

- Support repositories up to 1M LOC
- Process up to 10,000 symbols per batch
- Handle 100+ concurrent verification requests

### 3.3 Reliability

- Graceful degradation when LSP unavailable
- Retry with exponential backoff on API failures
- No data loss on unexpected termination (checkpointing)

### 3.4 Security

- Sandbox all code execution (Bubblewrap)
- Validate all file paths against traversal
- Redact API keys in logs
- No shell=True with user input

---

## 4. Integration Points

### 4.1 External APIs

| API | Purpose | Status |
|-----|---------|--------|
| Perplexity | Research queries | Implemented |
| Brave Search | Documentation search | Implemented |
| Context7 | API documentation | Missing |
| GLM/Claude | LLM generation | Implemented |
| Exa Search | Semantic search | Partial |

### 4.2 Storage

| System | Purpose | Status |
|--------|---------|--------|
| KuzuDB | Graph storage | Implemented |
| File System | Cache, temp files | Implemented |
| In-Memory | Session state | Implemented |

### 4.3 Analysis Tools

| Tool | Purpose | Status |
|------|---------|--------|
| Python AST | Python analysis | Implemented |
| Tree-sitter | Multi-language | Implemented |
| LSP (pylsp) | Python server | Implemented |
| LSP (tsserver) | TypeScript server | Implemented |
| SCIP | Cross-file refs | Partial |

---

## 5. Error Handling

### 5.1 Exception Hierarchy

```
SkillsFabricError (base)
├── DatabaseError
│   ├── ConnectionError
│   ├── QueryError
│   └── SchemaError
├── TrustError
│   ├── ValidationError (Level 1 failure)
│   ├── VerificationError (Level 2 failure)
│   └── HallucinationError (Level 3 detected)
├── PipelineError
│   ├── IngestError
│   ├── AnalysisError
│   ├── LinkingError
│   ├── GenerationError
│   └── SandboxError
├── ExternalServiceError
│   ├── Context7Error
│   ├── LSPError
│   ├── LLMError
│   └── ExaSearchError
├── ConfigurationError
│   └── MissingConfigError
└── IterationError
    ├── MaxIterationsExceeded
    └── CompletionPromiseNotMet
```

### 5.2 Recovery Strategies

| Error Type | Strategy |
|------------|----------|
| API timeout | Retry with exponential backoff (max 3) |
| LSP unavailable | Degrade to AST-only mode |
| Parse error | Log warning, skip file |
| Hall_m exceeded | Raise exception, fail fast |
| Database error | Retry once, then fail |

---

## 6. Observability

### 6.1 Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| `skills_generated_total` | Counter | Track generation volume |
| `hall_m_current` | Gauge | Current hallucination rate |
| `validation_duration_seconds` | Histogram | Performance tracking |
| `api_requests_total` | Counter | External API usage |
| `errors_total` | Counter | Error tracking by type |

### 6.2 Logging

| Level | Usage |
|-------|-------|
| DEBUG | Detailed execution trace |
| INFO | Normal operations |
| WARNING | Degradation, recoverable issues |
| ERROR | Operation failures |
| CRITICAL | System-wide failures |

### 6.3 Tracing

- OpenTelemetry-compatible spans
- Correlation IDs across requests
- Parent-child span relationships

---

## 7. Testing Requirements

### 7.1 Coverage Targets

| Area | Target | Current |
|------|--------|---------|
| Core modules | 90% | ~70% |
| CLI commands | 80% | 0% |
| Agents | 80% | ~20% |
| Integration | 70% | ~60% |
| Overall | 80% | ~60% |

### 7.2 Test Types

- **Unit Tests**: All public APIs
- **Integration Tests**: End-to-end workflows
- **Performance Tests**: Large-scale operations
- **Error Tests**: All exception paths
- **Security Tests**: Input validation

---

## 8. Deployment

### 8.1 Requirements

- Python 3.11+
- 4GB RAM minimum
- 10GB disk for large repos

### 8.2 Installation

```bash
pip install skills-fabric
# or
pip install -e .  # development
```

### 8.3 Configuration

```bash
# Required
export ZAI_API_KEY="..."        # GLM API
export ANTHROPIC_API_KEY="..."  # Claude API

# Optional
export PERPLEXITY_API_KEY="..." # Research
export BRAVE_API_KEY="..."      # Search
export CONTEXT7_URL="..."       # Context7 endpoint
```

---

## 9. Clarifications Needed

1. **Context7 Integration**: Should we implement or remove references?
2. **Memory System**: Consolidate to one system or maintain both?
3. **SCIP Usage**: Is SCIP adapter actively used or aspirational?
4. **Performance Targets**: Are current targets acceptable?
5. **Multi-tenant**: Any future requirement for isolation?
