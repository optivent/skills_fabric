# Proof-Based Code Understanding Architecture

## The Vision

Like Lean4 transforms mathematics from "opinions" to "machine-verified truth",
this architecture transforms code understanding from "I think I understand" to
"I have proven N theorems about this code".

## Achieved So Far

```
┌────────────────────────────────────────────────────────────────┐
│                    PROOF-BASED UNDERSTANDING                   │
│                         (Implemented)                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ✓ Theorem System         ✓ AST Proof Checker                 │
│  ✓ Proof Objects          ✓ Execution Proof Checker           │
│  ✓ Counterexample         ✓ Invariant Verification            │
│    Detection                                                   │
│                                                                │
│  Test Results: 25/25 theorems proven (100% certainty)         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Scaling to LangGraph: The Complete Stack

```
┌────────────────────────────────────────────────────────────────┐
│                      LAYER 5: KNOWLEDGE                        │
│              (Proven facts about the codebase)                 │
├────────────────────────────────────────────────────────────────┤
│  • "StateGraph.compile() returns CompiledStateGraph"           │
│  • "CompiledStateGraph.invoke() accepts dict input"            │
│  • "Graph cycles are detected at compile time"                 │
│                                                                │
│  STATUS: Each fact is a THEOREM with PROOF                     │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Proofs
                              │
┌────────────────────────────────────────────────────────────────┐
│                   LAYER 4: PROOF CHECKERS                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │     AST      │  │     LSP      │  │  Execution   │        │
│  │   Checker    │  │   Checker    │  │   Checker    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│        │                  │                  │                 │
│        │ Structural       │ Semantic         │ Behavioral      │
│        │ facts            │ facts            │ facts           │
│        ▼                  ▼                  ▼                 │
│  "Class X exists"  "X has type Y"   "X.f() returns Z"         │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Slicing    │  │   Property   │  │ Consistency  │        │
│  │   Checker    │  │   Checker    │  │   Checker    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│        │                  │                  │                 │
│        │ Dependency       │ Invariant        │ Cross-fact      │
│        │ facts            │ facts            │ coherence       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Raw Data
                              │
┌────────────────────────────────────────────────────────────────┐
│                    LAYER 3: DATA SOURCES                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    AST (Python ast module)                │ │
│  │  • Class definitions, method signatures                   │ │
│  │  • Control flow structure                                 │ │
│  │  • Static dependencies                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    LSP (via mcpls)                        │ │
│  │  • Type inference (beyond annotations)                    │ │
│  │  • Cross-file references                                  │ │
│  │  • Semantic symbol navigation                             │ │
│  │  • Call hierarchy                                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                Execution Traces                           │ │
│  │  • Actual runtime behavior                                │ │
│  │  • Exception paths                                        │ │
│  │  • Input/output relationships                             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Source
                              │
┌────────────────────────────────────────────────────────────────┐
│                     LAYER 2: SOURCE CODE                       │
├────────────────────────────────────────────────────────────────┤
│  Git Repository: langgraph                                     │
│  Files: ~100 Python files                                      │
│  Entry Points: StateGraph, CompiledStateGraph                  │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Links
                              │
┌────────────────────────────────────────────────────────────────┐
│                     LAYER 1: CODEWIKI                          │
├────────────────────────────────────────────────────────────────┤
│  High-level concept documentation                              │
│  Links to source files                                         │
│  Starting point for exploration                                │
└────────────────────────────────────────────────────────────────┘
```

## LSP Integration Strategy

### Why LSP?

AST gives us **syntax**. LSP gives us **semantics**.

| Information | AST | LSP |
|-------------|-----|-----|
| "Class X exists" | ✓ | ✓ |
| "X has method m" | ✓ | ✓ |
| "m returns type T" | Annotations only | Inferred types |
| "m is called from Y.f" | Must search | Direct lookup |
| "X.z references A.b" | Must trace | Direct |

### Integration via mcpls

```python
# Theorem requiring LSP for proof
theorem = Theorem(
    statement="StateGraph.compile returns CompiledStateGraph",
    category="type",
    subject="StateGraph.compile"
)

# AST proof: Check annotation
ast_proof = ast_checker.prove_return_type("StateGraph", "compile")
# Result: "CompiledStateGraph" (from annotation)

# LSP proof: Check inferred type at call sites
lsp_proof = lsp_checker.prove_inferred_return_type("StateGraph.compile")
# Result: Consistent with CompiledStateGraph at all call sites
```

### mcpls Commands for Proof Generation

```
textDocument/definition    → Prove "X is defined at location Y"
textDocument/references    → Prove "X is used by {list}"
textDocument/typeDefinition → Prove "X has type Y"
textDocument/hover         → Extract type information
textDocument/callHierarchy → Prove "X calls Y calls Z"
```

## Theorem Categories for LangGraph

### 1. Existence Theorems (AST-provable)
```
∀ class C mentioned in docs: C exists in source
∀ method M mentioned in docs: M exists in class
```

### 2. Type Theorems (LSP-provable)
```
StateGraph : Graph[State]
CompiledStateGraph : Runnable
compile() : StateGraph → CompiledStateGraph
```

### 3. Relationship Theorems (Cross-reference)
```
CompiledStateGraph depends on StateGraph
MessageGraph is a specialization of StateGraph
All graphs inherit from Graph base
```

### 4. Behavioral Theorems (Execution-provable)
```
graph.compile() does not raise on valid graph
graph.compile() raises on cyclic graph
compiled.invoke({}) returns dict
```

### 5. Invariant Theorems (Property-based)
```
∀ valid_graph: compile(graph).invoke(input) terminates
∀ node: after execution, state is updated
∀ edge: condition determines next node
```

## Implementation Roadmap

### Phase 1: LSP Checker (Current Priority)
```python
class LSPProofChecker:
    def __init__(self, workspace_path: str):
        self.client = mcpls.connect(workspace_path)

    def prove_type(self, symbol: str, expected_type: str) -> Optional[Proof]:
        hover = self.client.hover(symbol)
        if expected_type in hover.type_info:
            return Proof(method=ProofMethod.TYPE_CHECK, ...)
        return None

    def prove_references(self, symbol: str) -> List[Proof]:
        refs = self.client.references(symbol)
        return [Proof(..., witness=ref) for ref in refs]
```

### Phase 2: Cross-File Theorem Prover
```python
class CrossFileProver:
    def prove_dependency(self, from_file: str, to_file: str) -> Proof:
        # Use LSP to trace imports and references
        pass

    def prove_inheritance(self, child: str, parent: str) -> Proof:
        # Trace MRO through AST + LSP
        pass
```

### Phase 3: Full LangGraph Understanding
```python
def prove_langgraph_understanding() -> ProofBasedUnderstanding:
    # Start from codewiki links
    concepts = codewiki.get_concepts()

    theorems = []
    for concept in concepts:
        # Generate theorems from documentation claims
        theorems += theorem_generator.from_docs(concept)

        # Generate theorems from code structure
        theorems += theorem_generator.from_code(concept.source_file)

    # Prove all theorems
    for theorem in theorems:
        prover.prove(theorem)

    return ProofBasedUnderstanding(theorems=theorems)
```

## Success Criteria

### For Test Repo (Achieved)
- 100% certainty (all theorems proven or refuted)
- 100% truth ratio (all proven theorems are true)
- Counterexamples detected for false claims

### For LangGraph (Target)
- Generate >200 theorems about core concepts
- Prove >180 theorems (90% certainty)
- All proven theorems verified by execution
- No hallucinated claims accepted

## The Fundamental Guarantee

```
IF a claim appears in our understanding
THEN it has a machine-verified proof

IF a claim has no proof
THEN it is NOT part of our understanding

This is NOT "I think I understand"
This IS "I have proven that X is true"
```

## Next Steps

1. **Implement LSP Checker** using mcpls
2. **Add type inference proofs** beyond annotations
3. **Add cross-file reference proofs**
4. **Scale to LangGraph StateGraph**
5. **Achieve 90%+ certainty on real codebase**
