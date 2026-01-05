"""Core module for Skills Fabric.

Provides database access, configuration, and exception hierarchy.
"""
from .database import db, KuzuDatabase
from .exceptions import (
    # Base
    SkillsFabricError,
    # Database
    DatabaseError,
    ConnectionError,
    QueryError,
    SchemaError,
    # Trust hierarchy
    TrustError,
    ValidationError,
    VerificationError,
    HallucinationError,
    # Pipeline
    PipelineError,
    IngestError,
    AnalysisError,
    LinkingError,
    GenerationError,
    SandboxError,
    # External services
    ExternalServiceError,
    Context7Error,
    LSPError,
    LLMError,
    ExaSearchError,
    # Configuration
    ConfigurationError,
    MissingConfigError,
    # Iteration
    IterationError,
    MaxIterationsExceeded,
    CompletionPromiseNotMet,
)

__all__ = [
    # Database
    "db",
    "KuzuDatabase",
    # Exceptions
    "SkillsFabricError",
    "DatabaseError",
    "ConnectionError",
    "QueryError",
    "SchemaError",
    "TrustError",
    "ValidationError",
    "VerificationError",
    "HallucinationError",
    "PipelineError",
    "IngestError",
    "AnalysisError",
    "LinkingError",
    "GenerationError",
    "SandboxError",
    "ExternalServiceError",
    "Context7Error",
    "LSPError",
    "LLMError",
    "ExaSearchError",
    "ConfigurationError",
    "MissingConfigError",
    "IterationError",
    "MaxIterationsExceeded",
    "CompletionPromiseNotMet",
]
