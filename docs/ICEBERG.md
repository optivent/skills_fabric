# Progressive Iceberg Architecture

## The Vision

> **AI agents that can "see through" all transparent layers: from syntax to ultra-deep code investigations.**

```
                    ☀️ SURFACE (User-Facing)
    ════════════════════════════════════════════════════
    │                                                  │
    │   HOW-TO SYNTAX LAYER                           │
    │   ─────────────────                             │
    │   • Context7 multiple retrievals                │
    │   • Exa Search (semantic web search)            │
    │   • Grep App (pattern matching)                 │
    │   • Grounded syntax examples                    │
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
    │   • AI observes runtime behavior                │
    │   • Actual outputs captured                     │
    │   • Memory structures analyzed                  │
    │                                                  │
    ════════════════════════════════════════════════════
    │                                                  │
    │   CODEWIKI MAP LAYER (Navigation)               │
    │   ───────────────────────────────               │
    │   • Documentation → Source links               │
    │   • 433+ PROVEN verified connections            │
    │   • KuzuDB graph navigation                     │
    │   • Concept → Symbol → File paths              │
    │                                                  │
    ════════════════════════════════════════════════════
    │                                                  │
    │   GIT CLONE REALITY LAYER (Foundation)          │
    │   ────────────────────────────────              │
    │   • Actual source code files                    │
    │   • Version controlled truth                    │
    │   • Complete repository state                   │
    │   • The ground truth everything links to        │
    │                                                  │
    ════════════════════════════════════════════════════
                    🌊 BEDROCK (Immutable Truth)
```

---

## Layer Details

### Layer 1: HOW-TO SYNTAX (Surface)

**Purpose:** User-facing examples and syntax patterns

**Data Sources:**
| Source | Purpose | Integration |
|--------|---------|-------------|
| Context7 | Fresh library docs with code examples | Direct HTTP MCP API |
| Exa Search | Semantic web search for tutorials | API integration |
| Grep App | Pattern matching across codebase | CLI tool |

**Output:** Grounded syntax examples that directly answer "how do I..."

---

### Layer 2: AST + LSP DEEP ANALYSIS

**Purpose:** Compiler-grade code understanding

**Tools:**
```python
# AST - Every node, every symbol
import ast
tree = ast.parse(source_code)
for node in ast.walk(tree):
    # Extract classes, functions, imports, calls...

# Tree-sitter - Multi-language
from tree_sitter import Parser
tree = parser.parse(source_bytes)
# Extract from Python, TypeScript, Rust, Go...

# LSP - Type information
hover_info = lsp_client.get_hover(file, line, col)
# Get: type signatures, docstrings, definitions

# SCIP - Compiler symbols
symbols = scip_index.get_symbols(file)
# Get: cross-references, implementations
```

**Output:** Complete structural understanding of code

---

### Layer 3: BUBBLEWRAP AI UNDERSTANDING

**Purpose:** Runtime behavior comprehension

**Process:**
```bash
# Execute in isolated sandbox
bwrap --ro-bind / / --unshare-net -- python3 code.py

# AI observes:
# - What functions are called
# - What data structures are used
# - What outputs are produced
# - What patterns emerge
```

**Output:** AI-verified behavioral understanding

---

### Layer 4: CODEWIKI MAP (Navigation)

**Purpose:** Link documentation to reality

**Structure:**
```cypher
(Concept)-[:PROVEN]->(Symbol)
(Concept)-[:MENTIONS]->(FilePath)
(Symbol)-[:DEFINED_IN]->(File)
(Symbol)-[:CALLS]->(Symbol)
```

**Output:** 433+ verified navigation links

---

### Layer 5: GIT CLONE REALITY (Foundation)

**Purpose:** Immutable source of truth

**Content:**
- Complete repository clone
- All source files
- All history (optional depth)
- The bedrock everything references

---

## Transparency: AI Sees Through All Layers

### The Key Innovation

```
User Query: "How does StateGraph handle checkpoints?"
              │
              ▼
    ┌─────────────────────────────────────────────────┐
    │ LAYER 1: Context7 finds tutorial examples       │
    │          "Use MemorySaver for checkpoints"      │
    └────────────────────┬────────────────────────────┘
                         │ (BUT WHERE IS THE CODE?)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │ LAYER 2: AST finds checkpoint implementation    │
    │          graph/state.py → StateGraph class      │
    │          LSP: checkpoint method at line 847     │
    └────────────────────┬────────────────────────────┘
                         │ (BUT DOES IT WORK?)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │ LAYER 3: Bubblewrap executes checkpoint code    │
    │          AI sees: saves state, retrieves state  │
    │          Verified: works as documented          │
    └────────────────────┬────────────────────────────┘
                         │ (HOW IS IT CONNECTED?)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │ LAYER 4: CodeWiki shows the map                 │
    │          "checkpoint" → PROVEN → StateGraph     │
    │          → USES → MemorySaver                   │
    └────────────────────┬────────────────────────────┘
                         │ (WHAT IS THE TRUTH?)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │ LAYER 5: Git clone has the actual file          │
    │          libs/langgraph/langgraph/graph/state.py│
    │          Line 847: def checkpoint(self)...      │
    └─────────────────────────────────────────────────┘
```

### Result: Zero Hallucination

The AI never guesses because:
1. **Surface layer** gives the syntax (from real docs)
2. **AST layer** gives the structure (from real code)
3. **Bubblewrap layer** gives verification (from real execution)
4. **Map layer** connects everything (verified links)
5. **Git layer** is the source of truth (immutable)

---

## Memory Structures for Agent Navigation

### KuzuDB Graph Schema

```cypher
// Nodes
Concept(name, content, source_doc)
Symbol(name, file_path, line, type_info)
Skill(id, question, code, verified)
File(path, language, size)

// Relationships
(Concept)-[:PROVEN]->(Symbol)
(Concept)-[:MENTIONS]->(File)
(Symbol)-[:DEFINED_IN]->(File)
(Symbol)-[:CALLS]->(Symbol)
(Symbol)-[:USES]->(Symbol)
(Skill)-[:TEACHES]->(Concept)
(Skill)-[:USES]->(Symbol)
```

### Agent Navigation Pattern

```python
def investigate(query: str):
    """AI agent transparent investigation."""
    
    # Layer 1: Surface examples
    examples = context7.query(query)
    exa_results = exa_search(query)
    
    # Layer 2: Deep structure
    symbols = ast_parser.find_related(query)
    types = lsp_client.get_types(symbols)
    
    # Layer 3: Runtime understanding
    for symbol in symbols:
        sandbox_result = bubblewrap.execute(symbol.code)
        understanding = ai.observe(sandbox_result)
    
    # Layer 4: Map navigation
    graph_path = kuzu.traverse(
        start=concept,
        through=[PROVEN, CALLS, USES],
        to=target_symbol
    )
    
    # Layer 5: Ground truth
    source = git_clone.read(symbol.file_path)
    
    return {
        "examples": examples,      # What users see
        "structure": symbols,      # How its built
        "behavior": understanding, # How it works
        "map": graph_path,         # How its connected
        "truth": source            # What it actually is
    }
```

---

## The Complete Tool Stack

| Layer | Tools | Purpose |
|-------|-------|---------|
| Surface | Context7, Exa, Grep | Find examples |
| Structure | AST, Tree-sitter, LSP, SCIP | Parse code |
| Runtime | Bubblewrap, AI observation | Understand behavior |
| Map | KuzuDB, PROVEN links | Navigate connections |
| Truth | Git clone | Ground everything |

---

## One-Line Summary

> **"A progressive iceberg where AI agents see through every layer - from user-facing syntax down to immutable source truth - with full transparency and zero hallucination."**
