# Progressive Iceberg Architecture

## The Vision

> **Zero-hallucination Claude Skills through transparent, verifiable layers from syntax to source truth.**

This document describes the **perfect integration** of the Progressive Iceberg model for generating verified AI skills.

---

## Core Insight: CodeWiki Pre-Verified Links

Google's CodeWiki returns documentation with **embedded GitHub links** that include:
- Repository path
- File path  
- Commit hash
- **Line numbers**

Example:
```markdown
The [`StateGraph`](https://github.com/langchain-ai/langgraph/blob/abc123/libs/langgraph/graph/state.py#L112) 
class is the core abstraction...
```

**This is a PRE-VERIFIED connection from documentation to source code.**

---

## The Five Layers

```
              ☀️ SURFACE (User-Facing)
    ════════════════════════════════════════════════════
    │                                                  │
    │   HOW-TO SYNTAX LAYER                           │
    │   ─────────────────                             │
    │   • Context7 multiple retrievals                │
    │   • Exa Search (semantic web search)            │
    │   • Grep App (pattern matching)                 │
    │   • FUSION: Merge + consensus score             │
    │   • LINK EXTRACTION: Parse GitHub refs          │
    │                                                  │
    ════════════════════════════════════════════════════
                         WATERLINE
    ════════════════════════════════════════════════════
    │                                                  │
    │   AST + LSP DEEP ANALYSIS LAYER                 │
    │   ─────────────────────────────                 │
    │   • Full AST walking (every node)               │
    │   • LSP type information                        │
    │   • Tree-sitter multi-language parsing          │
    │   • SCIP compiler-grade symbols                 │
    │   • GLiNER NER extraction                       │
    │                                                  │
    ════════════════════════════════════════════════════
    │                                                  │
    │   BUBBLEWRAP AI UNDERSTANDING LAYER             │
    │   ─────────────────────────────────             │
    │   • Code executed in sandbox                    │
    │   • Execution tracing (sys.settrace)            │
    │   • State snapshots before/after                │
    │   • AI observes and models behavior             │
    │                                                  │
    ════════════════════════════════════════════════════
    │                                                  │
    │   KNOWLEDGE GRAPH NAVIGATION LAYER              │
    │   ───────────────────────────────               │
    │   • KuzuDB graph storage                        │
    │   • PROVEN links (doc ↔ code)                   │
    │   • Concept → Symbol → File paths               │
    │   • Weighted confidence traversal               │
    │                                                  │
    ════════════════════════════════════════════════════
    │                                                  │
    │   GIT CLONE REALITY LAYER (Foundation)          │
    │   ────────────────────────────────              │
    │   • Actual source code files                    │
    │   • Version controlled truth                    │
    │   • Commit-pinned references                    │
    │   • The ground truth everything links to        │
    │                                                  │
    ════════════════════════════════════════════════════
                    🌊 BEDROCK (Immutable Truth)
```

---

## Progressive Deepening Model

From a CodeWiki connection point (e.g., "StateGraph at line 112"), we can go deeper progressively:

### Level 0: Validate Link
```
CodeWiki: "StateGraph at github.com/.../state.py#L112"
    │
    ▼
Git Clone: Does line 112 contain "StateGraph"?
    │
    ▼
✅ YES → Link is valid
```

**Use Case:** Simple syntax examples

### Level 1: Parse Symbol
```
Git Clone: Read lines 112-200 (class body)
    │
    ▼
AST Parse: Extract methods, parameters, docstrings
    │
    ▼
Output: {
  "__init__": ["state_schema: Type[Any]"],
  "add_node": ["name: str", "action: Callable"],
  "compile": ["**kwargs"] -> "CompiledGraph"
}
```

**Use Case:** API reference skills

### Level 2: Immediate Dependencies
```
AST: StateGraph uses → Graph, CompiledGraph, Channel
    │
    ▼
For each dependency:
  - Where is it defined?
  - What does it provide?
```

**Use Case:** Behavioral understanding

### Level 3: Call Graph Expansion
```
StateGraph.compile()
    │
    ├── calls → CompiledGraph.__init__()
    │              └── calls → _build_channel_maps()
    │
    └── uses → Checkpointer (optional)
               └── calls → MemorySaver or SqliteSaver
```

**Use Case:** Deep dive / internals skills

### Level 4: Full Recursive Expansion
```
Complete call graph with all transitive dependencies
```

**Use Case:** Master class skills

### Level 5: Execution Trace
```
Bubblewrap Sandbox:
  - Execute the code
  - Capture function call sequence
  - Record state mutations
  - AI observes runtime behavior
```

**Use Case:** Debugging / verification skills

---

## Depth Decision Matrix

| Skill Type | Depth | Tools Used |
|------------|-------|------------|
| "How to use X" | 0-1 | Link validation, symbol parse |
| "What does X do" | 1-2 | AST + immediate deps |
| "How does X work" | 2-3 | Call graph expansion |
| "Debug why X fails" | 4-5 | Full trace + sandbox |
| "Master class on X" | 5 | Everything |

---

## Implementation: Depth Controller

```python
from dataclasses import dataclass
from enum import IntEnum

class DepthLevel(IntEnum):
    VALIDATE = 0      # Just check link exists
    PARSE_SYMBOL = 1  # Extract symbol structure
    DEPENDENCIES = 2  # Immediate deps
    CALL_GRAPH = 3    # One-level call expansion
    FULL_GRAPH = 4    # Recursive expansion
    EXEC_TRACE = 5    # Runtime execution

@dataclass
class CodeWikiRef:
    concept: str
    repo: str
    file_path: str
    line: int
    commit: str

class DepthController:
    def expand(self, ref: CodeWikiRef, depth: DepthLevel):
        result = {}
        
        if depth >= DepthLevel.VALIDATE:
            result["validated"] = self._validate(ref)
        
        if depth >= DepthLevel.PARSE_SYMBOL:
            result["symbol"] = self._parse_symbol(ref)
        
        if depth >= DepthLevel.DEPENDENCIES:
            result["deps"] = self._find_deps(result["symbol"])
        
        if depth >= DepthLevel.CALL_GRAPH:
            result["calls"] = self._build_call_graph(result["symbol"])
        
        if depth >= DepthLevel.FULL_GRAPH:
            result["full_graph"] = self._expand_recursively(result["calls"])
        
        if depth >= DepthLevel.EXEC_TRACE:
            result["trace"] = self._execute_and_trace(ref)
        
        return result
```

---

## Link Extraction from CodeWiki

```python
import re

def extract_codewiki_refs(markdown: str) -> list[CodeWikiRef]:
    """Extract GitHub links from CodeWiki markdown."""
    
    pattern = r"\[`?([^`\]]+)`?\]\(https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#)]+)(?:#L(\d+))?\)"
    
    refs = []
    for match in re.finditer(pattern, markdown):
        refs.append(CodeWikiRef(
            concept=match.group(1),
            repo=match.group(2),
            file_path=match.group(4),
            line=int(match.group(5)) if match.group(5) else 0,
            commit=match.group(3)
        ))
    return refs
```

---

## Perfect Skill Output

```yaml
skill:
  id: "langgraph_stategraph_001"
  question: "How do I create a StateGraph with checkpoints?"
  
  # Layer 1: Syntax (from CodeWiki)
  codewiki_source: "https://codewiki.google/github.com/langchain-ai/langgraph"
  example_code: |
    from langgraph.graph import StateGraph
    graph = StateGraph(AgentState)
    compiled = graph.compile(checkpointer=MemorySaver())
  
  # Layer 2: Structure (from AST)
  depth_level: 2
  symbols_used:
    - name: "StateGraph"
      file: "libs/langgraph/langgraph/graph/state.py"
      line: 112
      methods: ["__init__", "add_node", "compile"]
  
  # Layer 3: Behavior (from sandbox, if depth >= 5)
  runtime_verified: true
  
  # Layer 4: Navigation (from KuzuDB)
  proven_links:
    - concept: "State Management"
      symbol: "StateGraph"
      confidence: 0.95
      source: "codewiki_embedded"  # Pre-verified!
  
  # Layer 5: Foundation
  source_commit: "abc123"
  verified: true
```

---

## Key Principles

1. **CodeWiki links are pre-verified** - Parse, dont infer
2. **Progressive deepening** - Go only as deep as needed
3. **Every layer validates the one above** - Bidirectional verification
4. **Git clone is ground truth** - Final arbiter of reality
5. **Sandbox execution for behavior** - Dont guess, run it

---

## Integration with Tools

| Tool | Layer | Purpose |
|------|-------|---------|
| Context7 | 1 | Multi-query documentation |
| Exa Search | 1 | Semantic web search |
| Grep | 1 | Pattern matching |
| AST Parser | 2 | Symbol extraction |
| Tree-sitter | 2 | Multi-language parsing |
| LSP Client | 2 | Type information |
| SCIP | 2 | Compiler-grade indexing |
| Bubblewrap | 3 | Safe execution sandbox |
| Tracer | 3 | Execution trace capture |
| KuzuDB | 4 | Knowledge graph storage |
| Git Clone | 5 | Source truth |

---

## Summary

The Progressive Iceberg is not just layers of tools - it is a **unified cognitive system** where:

> **Every layer verifies the layer above it, and every layer is grounded in the layer below it.**

The key insight is that **CodeWiki provides pre-verified links** from documentation to source code, making the connection between Layer 1 (Syntax) and Layer 5 (Foundation) direct and reliable.

From that connection point, we **progressively deepen** based on the skill type required, going from simple validation to full execution traces.

**Result: Zero-hallucination Claude Skills grounded in immutable source truth.**
