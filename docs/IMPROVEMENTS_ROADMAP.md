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
