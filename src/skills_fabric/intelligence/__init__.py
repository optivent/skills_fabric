"""Code Intelligence module for Skills Fabric.

Advanced code understanding capabilities:
- Code Embeddings: Semantic similarity using GraphCodeBERT/CodeBERT
- Call Graph: Function call relationship analysis
- (Future) Symbolic Execution: Path exploration
- (Future) Data Flow Analysis: Taint tracking

Key Components:
- CodeSimilaritySearch: Find semantically similar code
- CallGraph: Build and query function relationships

Usage:
    from skills_fabric.intelligence import (
        CodeSimilaritySearch,
        CallGraph
    )

    # Semantic code search
    search = CodeSimilaritySearch()
    search.index("func1", "def add(a, b): return a + b")
    similar = search.find_similar("def sum(x, y): return x + y")

    # Call graph analysis
    graph = CallGraph()
    graph.build_from_directory("/path/to/repo")
    callers = graph.get_callers("process_data")
    dead_code = graph.find_dead_code(entry_points=["main"])
"""
from .code_embeddings import (
    CodeEmbedding,
    CodeEmbeddingProvider,
    GraphCodeBERTProvider,
    LocalCodeEmbeddingProvider,
    CodeSimilaritySearch,
)
from .call_graph import (
    CallGraph,
    CallNode,
    CallGraphBuilder,
)

__all__ = [
    # Code Embeddings
    "CodeEmbedding",
    "CodeEmbeddingProvider",
    "GraphCodeBERTProvider",
    "LocalCodeEmbeddingProvider",
    "CodeSimilaritySearch",
    # Call Graph
    "CallGraph",
    "CallNode",
    "CallGraphBuilder",
]
