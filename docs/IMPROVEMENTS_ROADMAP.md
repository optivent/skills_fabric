# Skills Fabric Improvements Roadmap

## Research Synthesis (January 2026)

This document captures deep research findings on improvements for our zero-hallucination Claude skill generator with progressive disclosure.

---

## 1. Zero-Hallucination Enhancement Techniques

### 1.1 Current State
- **DDR (Direct Dependency Retriever)**: Achieves Hall_m < 0.02 (2% hallucination rate)
- **Pipeline**: Mining → Linking → Writing → Auditing → Verifying → Storing
- **Validation**: 100% verified on Docling with 495 symbols

### 1.2 Advanced Techniques to Implement

#### A. Formal Verification Integration
**Source**: [Towards Formal Verification of LLM-Generated Code](https://arxiv.org/html/2507.13290v1)

| System | Approach | Verification Rate |
|--------|----------|-------------------|
| Astrogator | Symbolic interpreter + knowledge base | 83% correct, 92% error detection |
| PREFACE | RL agent + Dafny formal verification | Model-agnostic, no fine-tuning needed |
| PSV-Verus | Self-play with Rust formal proofs | 9.6× improvement over baselines |

**Implementation Priority**: HIGH
```
Action: Integrate Verus/Dafny verification for generated skill proofs
Benefit: Move from statistical validation to mathematical guarantees
```

#### B. Multi-Agent Verification (CodeX-Verify)
**Source**: [Multi-Agent Code Verification via Information Theory](https://arxiv.org/html/2511.16708)

- 4 specialized agents detect different bug types
- 76.1% bug detection rate
- 39.7 percentage point improvement over single agents (32.8% → 72.4%)

**Implementation Priority**: HIGH
```
Action: Extend our Auditor agent to use 4 specialized sub-agents:
  1. Bug Detection Agent - logical inconsistencies, runtime errors
  2. Code Smell Agent - anti-patterns, maintainability issues
  3. Security Agent - vulnerability detection
  4. Documentation Agent - accuracy verification
```

#### C. Retrieval-Augmented Generation Improvements
**Source**: [The 2025 Guide to RAG](https://www.edenai.co/post/the-2025-guide-to-retrieval-augmented-generation-rag)

- RAG reduces hallucination by 60-80%
- **Max-Min Semantic Chunking** outperforms LlamaIndex Semantic Splitter
- **Search/Retrieve decoupling**: Use small chunks for search, aggregate for retrieval

**Implementation Priority**: MEDIUM
```
Action: Implement semantic chunking for CodeWiki sections
Current: Fixed-size file parsing
Target: Max-Min semantic similarity grouping
```

#### D. Documentation Augmented Generation (DAG)
**Source**: [On Mitigating Code LLM Hallucinations with API Documentation](https://arxiv.org/html/2407.09726v1)

- Significantly improves low-frequency API handling
- "De-Hallucinator" method: find similar existing APIs when hallucination detected

**Implementation Priority**: MEDIUM
```
Action: Build API documentation index alongside symbol catalog
Trigger: Confidence score threshold or API index miss
```

---

## 2. Multi-Language Support

### 2.1 Language Status Matrix

| Language | LSP | AST Parser | MCP Server | Static Analysis | Our Support |
|----------|-----|------------|------------|-----------------|-------------|
| Python | ✓ | tree-sitter | ✓ | mypy, pyright | ✓ Full |
| TypeScript | ✓ | tree-sitter | ✓ | tsc | ✓ Full |
| Rust | ✓ | tree-sitter | ✓ | Verus, Clippy | ◐ Partial |
| Julia | ✓ | JuliaSyntax | ✓ | JET.jl, StaticLint.jl | ✗ None |
| R | ✓ | tree-sitter | ✗ **GAP** | lintr | ✗ None |
| Go | ✓ | tree-sitter | ✓ | go vet | ◐ Partial |

### 2.2 R Language Support (GAP IDENTIFIED)

**Current State**: No MCP implementation exists for R
**Opportunity**: First-mover advantage in scientific computing community

**Available R Tools**:
- **languageserver**: LSP implementation with lintr integration
- **tree-sitter-r**: R grammar for tree-sitter parsing
- **lintr**: Static analysis and linting

**Implementation Plan**:
```
Phase 1: Create R symbol extractor using languageserver
Phase 2: Build R MCP server (first in ecosystem!)
Phase 3: Integrate with DDR for R package verification
```

**Priority**: HIGH (unique opportunity, large scientific community)

### 2.3 Julia Language Support

**Available Tools**:
- **JET.jl**: Type inference and error detection
- **StaticLint.jl**: Static analysis
- **JuliaSyntax.jl**: Official parser (moving to core)
- **ModelContextProtocol.jl**: MCP implementation exists!

**Implementation Plan**:
```
Phase 1: Integrate ModelContextProtocol.jl
Phase 2: Add JET.jl validation to DDR
Phase 3: Support Julia package documentation
```

**Priority**: MEDIUM (MCP already exists, just needs integration)

### 2.4 SCIP Integration (Multi-Language Solution)
**Source**: [Sourcegraph SCIP](https://github.com/sourcegraph/scip)

Semantic Code Intelligence Protocol provides:
- Unified index format across all languages
- Pre-built indexers for 15+ languages
- Symbol definitions, references, and documentation

**Implementation Plan**:
```
Action: Use SCIP as universal symbol extraction layer
Benefit: Single integration covers Python, TypeScript, Go, Java, Rust, etc.
```

**Priority**: HIGH (maximum ROI for multi-language support)

---

## 3. Code Understanding & Embedding

### 3.1 Embedding Model Comparison

**Source**: [Code Embedding Models Deep Dive](https://medium.com/@abhilasha4042/code-isnt-just-text-a-deep-dive-into-code-embedding-models-418cf27ea576)

| Model | MRR | Recall@1 | Notes |
|-------|-----|----------|-------|
| Voyage Code-3 | 97.3% | 95% | Best specialized model |
| OpenAI text-embedding-3-small | Excellent | Excellent | Surprisingly strong |
| GraphCodeBERT | Poor | Poor | Outdated architecture |
| CodeBERT | Poor | Poor | Training limitations |

**Recommendation**: Use Voyage Code-3 or OpenAI embeddings, NOT CodeBERT

### 3.2 GraphCodeBERT Limitations
- Older transformer architecture
- Training data limitations
- Not optimized for retrieval tasks
- MiniLM-L6 (384 dim) outperforms both CodeBERT models

**Action**: Replace any CodeBERT usage with modern embeddings

---

## 4. Graph Database Architecture

### 4.1 Neo4j vs KuzuDB Comparison

**Source**: [KuzuDB Study](https://github.com/prrao87/kuzudb-study)

| Metric | Neo4j | KuzuDB |
|--------|-------|--------|
| Ingestion Speed | Baseline | **18× faster** |
| N-hop Path Queries | Baseline | **Significant speedup** |
| Schema | Optional | Required |
| Deployment | Server | **Embedded** |
| Query Language | Cypher | Cypher (openCypher) |

**Recommendation**: Use KuzuDB for embedded code knowledge graphs

### 4.2 Code Knowledge Graph Architecture

**Source**: [Codebase Knowledge Graph](https://neo4j.com/blog/developer/codebase-knowledge-graph/)

Structure:
```
Nodes: Files, Classes, Functions, Variables, Concepts
Edges: CONTAINS, CALLS, INHERITS, IMPORTS, REFERENCES, DOCUMENTS
```

**Implementation Plan**:
```
Phase 1: Build KuzuDB schema for code elements
Phase 2: Index symbol relationships from DDR
Phase 3: Enable graph queries for skill generation
```

---

## 5. Verification & Quality Gates

### 5.1 Continuous Verification Pipeline

**Source**: [Autonomous Quality Gates](https://www.augmentcode.com/guides/autonomous-quality-gates-ai-powered-code-review)

Three-tier architecture:
1. **Pre-commit**: Local AI checks before submission
2. **Pull Request**: Automated analysis + feedback
3. **Continuous**: Real-time quality metrics

**Implementation for Skills Fabric**:
```
Pre-generation: Validate symbol catalog completeness
Post-generation: Multi-agent audit (4 specialized agents)
Pre-storage: Citation verification (100% validated refs)
Post-storage: Continuous quality monitoring
```

### 5.2 AI Code Assurance

**Key Principle**: Every generated skill must pass structured review before storage

**Quality Gates**:
1. Zero uncited claims (Hall_m = 0)
2. All source refs validated
3. No deprecated/removed APIs
4. Progressive disclosure levels complete

---

## 6. Execution & Proof Generation

### 6.1 LLM Sandbox Options

**Source**: [LLM Sandbox](https://github.com/vndee/llm-sandbox)

| Tool | Features | MCP Support |
|------|----------|-------------|
| llm-sandbox | Lightweight, Docker-based | ✓ Yes |
| E2B | Enterprise, 200ms startup | Any language |
| Modal | 50K+ concurrent sessions | Python focus |

**Implementation Plan**:
```
Phase 1: Integrate llm-sandbox for Level 5 (Execution Proofs)
Phase 2: Run skill code examples in sandboxed environment
Phase 3: Capture and validate execution outputs
```

### 6.2 AutoVerus for Rust

**Source**: [Automated Proof Generation for Rust](https://www.cs.umd.edu/event/2025/02/automated-proof-generation-rust-code-using-llm)

AutoVerus uses LLM agents for three-phase proof construction:
1. Preliminary proof generation
2. Proof refinement with generic tips
3. Proof debugging with verification errors

**Application**: Use for Rust library skill generation with formal proofs

---

## 7. Tree-sitter Integration

### 7.1 MCP Server

**Source**: [mcp-server-tree-sitter](https://skywork.ai/skypage/en/mcp-server-tree-sitter-The-Ultimate-Guide-for-AI-Engineers/1972133047164960768)

Benefits:
- Incremental parsing (updates on edit)
- 100+ language grammars
- Error-tolerant parsing
- Unified AST representation

**Implementation**:
```
Action: Replace custom AST parsing with tree-sitter MCP
Benefit: Instant multi-language support, better performance
```

### 7.2 Language-Specific Queries

Tree-sitter queries enable:
- Symbol extraction
- Scope detection
- Reference resolution
- Code folding points

---

## 8. Priority Implementation Matrix

| Improvement | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| Multi-Agent Verification (4 agents) | Very High | Medium | 🔴 P0 |
| SCIP Integration | Very High | Medium | 🔴 P0 |
| R MCP Server (first-mover) | High | High | 🟠 P1 |
| KuzuDB Code Graph | High | Medium | 🟠 P1 |
| Tree-sitter MCP | High | Low | 🟠 P1 |
| llm-sandbox for L5 Proofs | Medium | Low | 🟡 P2 |
| Max-Min Semantic Chunking | Medium | Medium | 🟡 P2 |
| Voyage Code-3 Embeddings | Medium | Low | 🟡 P2 |
| Julia MCP Integration | Medium | Low | 🟢 P3 |
| Formal Verification (Verus) | High | Very High | 🟢 P3 |

---

## 9. Next Steps

### Immediate (Week 1)
1. Implement 4-agent verification system
2. Integrate tree-sitter MCP server
3. Set up SCIP for multi-language indexing

### Short-term (Month 1)
4. Build R MCP server (first in ecosystem)
5. Migrate to KuzuDB for code graph
6. Add llm-sandbox for execution proofs

### Medium-term (Quarter 1)
7. Implement Max-Min semantic chunking
8. Add Julia support via ModelContextProtocol.jl
9. Integrate Voyage Code-3 embeddings

### Long-term (Year 1)
10. Formal verification integration (Verus/Dafny)
11. Continuous verification pipeline
12. Full multi-language coverage

---

## References

### Zero-Hallucination
- [Formal Verification of LLM Code](https://arxiv.org/html/2507.13290v1)
- [Multi-Agent Code Verification](https://arxiv.org/html/2511.16708)
- [LLM Hallucinations in Code Generation](https://dl.acm.org/doi/10.1145/3728894)
- [API Documentation for Hallucination Mitigation](https://arxiv.org/html/2407.09726v1)

### Multi-Language
- [Julia MCP](https://github.com/JuliaComputing/ModelContextProtocol.jl)
- [R languageserver](https://github.com/REditorSupport/languageserver)
- [SCIP Protocol](https://github.com/sourcegraph/scip)
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter)

### Code Intelligence
- [Microsoft CodeBERT](https://github.com/microsoft/CodeBERT)
- [Code Knowledge Graphs](https://neo4j.com/blog/developer/codebase-knowledge-graph/)
- [KuzuDB Study](https://github.com/prrao87/kuzudb-study)

### Verification
- [Autonomous Quality Gates](https://www.augmentcode.com/guides/autonomous-quality-gates-ai-powered-code-review)
- [LLM Sandbox](https://github.com/vndee/llm-sandbox)
- [AutoVerus](https://www.cs.umd.edu/event/2025/02/automated-proof-generation-rust-code-using-llm)

### RAG
- [RAG Chunking Strategies](https://weaviate.io/blog/chunking-strategies-for-rag)
- [Max-Min Semantic Chunking](https://link.springer.com/article/10.1007/s10791-025-09638-7)
- [2025 RAG Guide](https://www.edenai.co/post/the-2025-guide-to-retrieval-augmented-generation-rag)

---

## 10. Implementation Specifications (Deep Research)

This section provides concrete implementation details gathered from additional research.

### 10.1 SCIP Integration Architecture

**Source**: [SCIP Protocol](https://github.com/sourcegraph/scip), [SCIP Python](https://github.com/sourcegraph/scip-python)

#### Protobuf Schema Structure
```protobuf
message Index {
  Metadata metadata = 1;
  repeated Document documents = 2;
  repeated SymbolInformation external_symbols = 3;
}

message Document {
  string relative_path = 1;
  repeated Occurrence occurrences = 2;
  repeated SymbolInformation symbols = 3;
}
```

#### Python Integration
```bash
# Install scip-python (built on Pyright)
npm install -g @sourcegraph/scip-python

# Index a project
scip-python index . --project-name=my_project

# Output: index.scip (protobuf format)
```

#### Consuming SCIP in Skills Fabric
```python
# Use provided language bindings (no protoc needed)
from scip import Index, Document, SymbolInformation

def load_scip_index(path: str) -> dict:
    """Load SCIP index and convert to DDR format."""
    with open(path, 'rb') as f:
        index = Index.FromString(f.read())

    symbols = {}
    for doc in index.documents:
        for sym in doc.symbols:
            symbols[sym.symbol] = {
                'file': doc.relative_path,
                'documentation': sym.documentation,
                'kind': sym.kind,
            }
    return symbols
```

#### Performance Benefits
- 8× smaller than LSIF (Meta/Glean benchmark)
- 3× faster processing
- Streaming consumption supported for large codebases

---

### 10.2 Building R MCP Server with FastMCP

**Source**: [FastMCP](https://github.com/jlowin/fastmcp), [Reticulate](https://rstudio.github.io/reticulate/)

#### Architecture: Python MCP Server + R Bridge
```
┌─────────────────────────────────────────────┐
│  Claude / MCP Client                        │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────────┐
│  FastMCP Python Server                      │
│  - @mcp.tool decorators                     │
│  - @mcp.resource decorators                 │
└─────────────────┬───────────────────────────┘
                  │ reticulate bridge
┌─────────────────▼───────────────────────────┐
│  R Runtime                                  │
│  - languageserver (LSP)                     │
│  - lintr (static analysis)                  │
│  - roxygen2 (documentation)                 │
└─────────────────────────────────────────────┘
```

#### FastMCP Server Skeleton for R
```python
from fastmcp import FastMCP
import subprocess
import json

mcp = FastMCP("R Language Server 🔬")

@mcp.tool
def r_get_symbols(file_path: str) -> dict:
    """Extract R symbols (functions, classes, S4 methods) from a file."""
    r_script = f'''
    library(languageserver)
    symbols <- languageserver:::document_symbols("{file_path}")
    cat(jsonlite::toJSON(symbols, auto_unbox=TRUE))
    '''
    result = subprocess.run(['Rscript', '-e', r_script], capture_output=True)
    return json.loads(result.stdout)

@mcp.tool
def r_lint_file(file_path: str) -> list:
    """Run lintr static analysis on R file."""
    r_script = f'''
    library(lintr)
    lints <- lint("{file_path}")
    cat(jsonlite::toJSON(as.data.frame(lints), auto_unbox=TRUE))
    '''
    result = subprocess.run(['Rscript', '-e', r_script], capture_output=True)
    return json.loads(result.stdout)

@mcp.resource("r://package/{package_name}/functions")
def r_package_functions(package_name: str) -> str:
    """List all exported functions from an R package."""
    r_script = f'''
    funcs <- ls("package:{package_name}")
    cat(jsonlite::toJSON(funcs))
    '''
    result = subprocess.run(['Rscript', '-e', r_script], capture_output=True)
    return result.stdout.decode()

if __name__ == "__main__":
    mcp.run()
```

#### Key R Packages to Integrate
| Package | Purpose | Integration |
|---------|---------|-------------|
| languageserver | LSP symbols, completion | Core symbol extraction |
| lintr | Static analysis | Code quality validation |
| roxygen2 | Documentation parsing | Docstring extraction |
| pkgdown | Package documentation | Full docs generation |
| covr | Test coverage | Quality metrics |

---

### 10.3 Tree-sitter MCP Server Capabilities

**Source**: [mcp-server-tree-sitter](https://github.com/wrale/mcp-server-tree-sitter)

#### Available Tools (we can use directly)
| Tool | Purpose | Our Use Case |
|------|---------|--------------|
| `get_symbols` | Extract functions, classes, imports | Symbol catalog building |
| `search_pattern` | Regex + tree-sitter queries | Find code patterns |
| `get_ast` | Get AST with configurable depth | Structure analysis |
| `find_similar` | Find similar code snippets | Deduplication |
| `analyze_complexity` | Code metrics | Quality scoring |
| `get_dependencies` | Import/dependency tracking | Relationship mapping |

#### Supported Languages (built-in)
Python, JavaScript, TypeScript, Go, Rust, C, C++, Swift, Java, Kotlin, Julia, APL

#### Additional Languages (via tree-sitter-language-pack)
Bash, C#, Clojure, Elixir, Elm, Haskell, Lua, Objective-C, OCaml, PHP, Ruby, Scala, SQL, XML

#### Limitation to Note
> "Tree-sitter provides structure; semantic understanding belongs to other tool classes such as LSP servers or code indexers"

**Implication**: Use tree-sitter for AST/structure, but combine with SCIP or LSP for type information and cross-file references.

#### Integration with Skills Fabric
```python
# Install
pip install mcp-server-tree-sitter

# In our pipeline, use tree-sitter for fast AST extraction
# Then enrich with SCIP for semantic information
```

---

### 10.4 KuzuDB Schema for Code Knowledge Graph

**Source**: [KuzuDB Docs](https://docs.kuzudb.com/get-started/)

#### Node Tables
```cypher
CREATE NODE TABLE File (
    path STRING PRIMARY KEY,
    language STRING,
    size INT64,
    last_modified TIMESTAMP
);

CREATE NODE TABLE Symbol (
    id STRING PRIMARY KEY,
    name STRING,
    kind STRING,  -- function, class, method, variable
    file_path STRING,
    line_start INT32,
    line_end INT32,
    documentation STRING
);

CREATE NODE TABLE Concept (
    id STRING PRIMARY KEY,
    name STRING,
    description STRING,
    level INT32  -- progressive disclosure level 0-5
);
```

#### Relationship Tables
```cypher
CREATE REL TABLE CONTAINS (
    FROM File TO Symbol
);

CREATE REL TABLE CALLS (
    FROM Symbol TO Symbol,
    call_site INT32
);

CREATE REL TABLE INHERITS (
    FROM Symbol TO Symbol
);

CREATE REL TABLE IMPORTS (
    FROM File TO File
);

CREATE REL TABLE REFERENCES (
    FROM Symbol TO Symbol,
    ref_type STRING  -- read, write, call
);

CREATE REL TABLE DOCUMENTS (
    FROM Symbol TO Concept
);

CREATE REL TABLE SKILL_USES (
    FROM Skill TO Symbol,
    citation STRING
);
```

#### Query Examples for Skill Generation
```cypher
-- Find all symbols a skill references
MATCH (s:Skill)-[r:SKILL_USES]->(sym:Symbol)
WHERE s.id = 'docling_pdf_conversion'
RETURN sym.name, sym.kind, r.citation;

-- Find related concepts for progressive disclosure
MATCH (sym:Symbol)-[:DOCUMENTS]->(c:Concept)
WHERE sym.name = 'DocumentConverter'
RETURN c.name, c.level ORDER BY c.level;

-- Trace call graph for a function
MATCH path = (f:Symbol)-[:CALLS*1..3]->(target:Symbol)
WHERE f.name = 'convert_pdf'
RETURN path;
```

---

### 10.5 Hallucination Measurement Metrics

**Source**: [HalluCode Benchmark](https://arxiv.org/abs/2404.00971), [Hallucinations Leaderboard](https://huggingface.co/blog/leaderboard-hallucinations)

#### Our Current Metric: Hall_m
```
Hall_m = (uncited_claims + invalid_citations) / total_claims
Target: Hall_m < 0.02 (2%)
Achieved: Hall_m = 0.0000 on Docling (100% validated)
```

#### Research-Backed Hallucination Categories
| Category | Description | Detection Method |
|----------|-------------|------------------|
| Intent Conflicting | Code doesn't match request | Requirement tracing |
| Context Inconsistency | Contradicts provided context | DDR validation |
| Dead Code | Unreachable/unused code | Static analysis |
| Knowledge Conflicting | Wrong API/syntax | Symbol catalog lookup |
| Package Hallucination | Non-existent packages | Package index check |

#### Enhanced Metrics to Add
```python
@dataclass
class HallucinationMetrics:
    hall_m: float           # Current: uncited/total claims
    api_accuracy: float     # % correct API calls
    package_validity: float # % real packages
    type_correctness: float # % type-valid code
    semantic_fidelity: float # BLEU/ROUGE vs source docs

    @property
    def composite_score(self) -> float:
        """Weighted composite hallucination score."""
        return (
            0.3 * (1 - self.hall_m) +
            0.25 * self.api_accuracy +
            0.2 * self.package_validity +
            0.15 * self.type_correctness +
            0.1 * self.semantic_fidelity
        )
```

#### Detection Approach (from research)
- Individual metrics: ~56-62% ROC-AUC (barely better than random)
- Combined metrics: 69-75% ROC-AUC (substantial improvement)

**Implication**: Use multiple detection methods, not just citation checking.

---

### 10.6 Multi-Agent Architecture Detail

**Source**: [CodeX-Verify](https://arxiv.org/html/2511.16708), [Multi-Agent Code Review](https://medium.com/google-cloud/agents-that-prove-not-guess-a-multi-agent-code-review-system-e2c0a735e994)

#### Agent Specialization (4-Agent System)
```python
class MultiAgentAuditor:
    """Four specialized agents for comprehensive verification."""

    def __init__(self):
        self.agents = {
            'bug_detector': BugDetectionAgent(),
            'code_smell': CodeSmellAgent(),
            'security': SecurityAgent(),
            'documentation': DocumentationAgent(),
        }

    async def audit(self, skill_content: str, context: dict) -> AuditResult:
        """Run all agents in parallel, combine results."""
        results = await asyncio.gather(*[
            agent.analyze(skill_content, context)
            for agent in self.agents.values()
        ])
        return self._combine_with_submodularity(results)

    def _combine_with_submodularity(self, results: list) -> AuditResult:
        """
        Use submodular combination (from CodeX-Verify paper).
        Agents with different detection patterns find more issues together
        than any single agent alone.
        """
        # Mutual information based combination
        ...
```

#### Agent Responsibilities
| Agent | Focus | Tools |
|-------|-------|-------|
| Bug Detector | Logical inconsistencies, runtime errors | AST analysis, type checking |
| Code Smell | Anti-patterns, maintainability | Complexity metrics, pattern matching |
| Security | Vulnerabilities, injection risks | Security rules, taint analysis |
| Documentation | Accuracy vs source, completeness | DDR lookup, citation verification |

#### Expected Improvement
- Single agent: 32.8% bug detection
- 4-agent system: 72.4% bug detection (+39.7 percentage points)

---

### 10.7 FastMCP Production Patterns

**Source**: [FastMCP Docs](https://gofastmcp.com/tutorials/create-mcp-server)

#### Three Core Primitives
```python
from fastmcp import FastMCP

mcp = FastMCP("Skills Fabric")

# 1. TOOLS - Actions the LLM can take
@mcp.tool
def generate_skill(library: str, topic: str) -> dict:
    """Generate a Claude skill for the given library and topic."""
    ...

# 2. RESOURCES - Data the LLM can read (like GET endpoints)
@mcp.resource("skills://{library}/{skill_name}")
def get_skill(library: str, skill_name: str) -> str:
    """Retrieve a generated skill."""
    ...

# 3. PROMPTS - Reusable templates
@mcp.prompt
def skill_template(library: str) -> str:
    """Template for skill generation."""
    return f"Generate a comprehensive skill for {library}..."
```

#### Production Features (FastMCP 2.0)
- **Enterprise Auth**: Google, GitHub, Azure, Auth0
- **Server Composition**: Combine multiple MCP servers
- **OpenAPI Generation**: Auto-generate REST API from MCP
- **Testing Utilities**: Built-in test framework

---

## 11. Immediate Action Items

Based on deep research, here are the concrete next steps:

### Week 1: Foundation
1. **Install mcp-server-tree-sitter** → Instant 100+ language AST support
2. **Install scip-python** → Precise Python indexing
3. **Create KuzuDB schema** → Code knowledge graph foundation

### Week 2: Multi-Agent
4. **Split Auditor into 4 agents** → 39.7% improvement in detection
5. **Add combined hallucination metrics** → Beyond just citation checking

### Week 3: R Language
6. **Build FastMCP R server skeleton** → First R MCP in ecosystem
7. **Integrate languageserver + lintr** → Symbol extraction + linting

### Week 4: Integration
8. **Connect SCIP → DDR** → Multi-language symbol catalogs
9. **Connect KuzuDB → Skills** → Graph-based skill generation
10. **Add llm-sandbox** → Level 5 execution proofs
