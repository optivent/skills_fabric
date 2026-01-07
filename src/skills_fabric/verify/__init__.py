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

Multi-Source Validation (Phase 5.2):
- MultiSourceValidator: Cross-check symbols with AST, tree-sitter, LSP
- ValidationSource: Enum of validation sources
- ValidationResult: Result with confidence scoring

Hall_m Metric Tracking (Phase 5.3):
- HallMetric: Comprehensive hallucination rate tracking
- HallMetricSnapshot: Point-in-time metric snapshot
- HallMetricExceededException: Exception when Hall_m >= 0.02
- get_hall_metric, reset_hall_metric: Global tracker functions
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
    # Multi-source validation (Phase 5.2)
    MultiSourceValidator,
    ValidationSource,
    ValidationResult,
    validate_symbol,
    # Hall_m metric tracking (Phase 5.3)
    HallMetric,
    HallMetricSnapshot,
    HallMetricExceededException,
    get_hall_metric,
    reset_hall_metric,
    set_hall_metric_threshold,
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
    # Multi-source validation (Phase 5.2)
    "MultiSourceValidator",
    "ValidationSource",
    "ValidationResult",
    "validate_symbol",
    # Hall_m metric tracking (Phase 5.3)
    "HallMetric",
    "HallMetricSnapshot",
    "HallMetricExceededException",
    "get_hall_metric",
    "reset_hall_metric",
    "set_hall_metric_threshold",
    # Cross-layer
    "CrossLayerVerifier",
    "CrossLayerResult",
    "LayerVerification",
]
