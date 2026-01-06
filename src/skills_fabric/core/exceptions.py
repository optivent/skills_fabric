"""Custom exception hierarchy for Skills Fabric.

Provides structured error handling with proper categorization,
enabling better debugging and error recovery.

Trust Hierarchy Integration:
- ValidationError: Trust Level 1 (HardContent) failures
- VerificationError: Trust Level 2 (VerifiedSoft) failures
- HallucinationError: Trust Level 3 content detected (REJECTED)
"""


class SkillsFabricError(Exception):
    """Base exception for all Skills Fabric errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# =============================================================================
# Database Errors
# =============================================================================

class DatabaseError(SkillsFabricError):
    """Base class for database-related errors."""
    pass


class ConnectionError(DatabaseError):
    """Failed to connect to database."""
    pass


class QueryError(DatabaseError):
    """Query execution failed."""
    pass


class SchemaError(DatabaseError):
    """Schema validation or creation failed."""
    pass


# =============================================================================
# Trust Hierarchy Errors
# =============================================================================

class TrustError(SkillsFabricError):
    """Base class for trust hierarchy violations."""
    pass


class ValidationError(TrustError):
    """Trust Level 1 (HardContent) validation failed.

    Indicates that source code or AST verification failed.
    """

    def __init__(self, message: str, source_file: str = None, **kwargs):
        super().__init__(message, {"source_file": source_file, **kwargs})
        self.source_file = source_file


class VerificationError(TrustError):
    """Trust Level 2 (VerifiedSoft) verification failed.

    Indicates that sandbox execution or grounding check failed.
    """

    def __init__(self, message: str, skill_id: str = None, **kwargs):
        super().__init__(message, {"skill_id": skill_id, **kwargs})
        self.skill_id = skill_id


class HallucinationError(TrustError):
    """Trust Level 3 (Unverified) content detected - REJECTED.

    Indicates content that cannot be grounded in source code.
    This is a critical error - the content MUST be rejected.
    """

    def __init__(self, message: str, ungrounded_content: str = None, **kwargs):
        super().__init__(message, {"ungrounded_content": ungrounded_content, **kwargs})
        self.ungrounded_content = ungrounded_content


# =============================================================================
# Pipeline Errors
# =============================================================================

class PipelineError(SkillsFabricError):
    """Base class for pipeline execution errors."""
    pass


class IngestError(PipelineError):
    """Error during ingestion phase."""
    pass


class AnalysisError(PipelineError):
    """Error during analysis phase."""
    pass


class LinkingError(PipelineError):
    """Error during PROVEN linking phase."""
    pass


class GenerationError(PipelineError):
    """Error during skill generation phase."""
    pass


class SandboxError(PipelineError):
    """Error during sandbox execution."""

    def __init__(self, message: str, exit_code: int = None, stderr: str = None, **kwargs):
        super().__init__(message, {"exit_code": exit_code, "stderr": stderr, **kwargs})
        self.exit_code = exit_code
        self.stderr = stderr


# =============================================================================
# External Service Errors
# =============================================================================

class ExternalServiceError(SkillsFabricError):
    """Base class for external service failures."""
    pass


class Context7Error(ExternalServiceError):
    """Context7 API call failed."""
    pass


class LSPError(ExternalServiceError):
    """Language Server Protocol error."""

    def __init__(self, message: str, method: str = None, **kwargs):
        super().__init__(message, {"method": method, **kwargs})
        self.method = method


class LLMError(ExternalServiceError):
    """LLM API call failed."""

    def __init__(self, message: str, model: str = None, **kwargs):
        super().__init__(message, {"model": model, **kwargs})
        self.model = model


class ExaSearchError(ExternalServiceError):
    """Exa Search API call failed."""
    pass


# =============================================================================
# Configuration Errors
# =============================================================================

class ConfigurationError(SkillsFabricError):
    """Configuration-related error."""
    pass


class MissingConfigError(ConfigurationError):
    """Required configuration value is missing."""

    def __init__(self, key: str, **kwargs):
        super().__init__(f"Missing required configuration: {key}", {"key": key, **kwargs})
        self.key = key


# =============================================================================
# Ralph Wiggum (Autonomous Loop) Errors
# =============================================================================

class IterationError(SkillsFabricError):
    """Error during autonomous iteration."""
    pass


class MaxIterationsExceeded(IterationError):
    """Maximum iterations reached without meeting completion promise."""

    def __init__(self, max_iterations: int, failures: list = None, **kwargs):
        super().__init__(
            f"Max iterations ({max_iterations}) exceeded",
            {"max_iterations": max_iterations, "failure_count": len(failures or []), **kwargs}
        )
        self.max_iterations = max_iterations
        self.failures = failures or []


class CompletionPromiseNotMet(IterationError):
    """Completion promise criteria not satisfied."""

    def __init__(self, promise_description: str, actual_result: dict = None, **kwargs):
        super().__init__(
            f"Completion promise not met: {promise_description}",
            {"promise": promise_description, "result": actual_result, **kwargs}
        )
        self.promise_description = promise_description
        self.actual_result = actual_result
