"""Verification module - Zero-hallucination verification pipeline.

Components:
- DDR: Direct Dependency Retriever for validated code retrieval
- CrossLayer: Multi-layer verification across iceberg layers
- Sandbox: Isolated code execution
- Tracer: Execution tracing

Batch Processing:
- BatchProgress: Progress tracking for large batches
- BatchResult: Result aggregation for batch operations
- retrieve_all_proven: Retrieve ALL PROVEN links without LIMIT constraints
"""
from .ddr import (
    DirectDependencyRetriever,
    SourceRef,
    CodeElement,
    DDRResult,
    BatchProgress,
    BatchResult,
    retrieve_validated,
    retrieve_batch_validated,
    retrieve_all_proven_links,
)
from .cross_layer import (
    CrossLayerVerifier,
    CrossLayerResult,
    LayerVerification,
)

__all__ = [
    # DDR
    "DirectDependencyRetriever",
    "SourceRef",
    "CodeElement",
    "DDRResult",
    "BatchProgress",
    "BatchResult",
    "retrieve_validated",
    "retrieve_batch_validated",
    "retrieve_all_proven_links",
    # Cross-layer
    "CrossLayerVerifier",
    "CrossLayerResult",
    "LayerVerification",
]
