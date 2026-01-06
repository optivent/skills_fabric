"""Verification module - Zero-hallucination verification pipeline.

Components:
- DDR: Direct Dependency Retriever for validated code retrieval
- CrossLayer: Multi-layer verification across iceberg layers
- Sandbox: Isolated code execution
- Tracer: Execution tracing
"""
from .ddr import (
    DirectDependencyRetriever,
    SourceRef,
    CodeElement,
    DDRResult,
    retrieve_validated,
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
    "retrieve_validated",
    # Cross-layer
    "CrossLayerVerifier",
    "CrossLayerResult",
    "LayerVerification",
]
