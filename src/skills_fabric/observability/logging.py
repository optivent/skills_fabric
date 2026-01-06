"""Structured Logging - Production logging for Skills Fabric.

Provides consistent, structured logging across the system:
- JSON format for log aggregation (ELK, Datadog, etc.)
- Contextual fields (session_id, library, trust_level)
- Log levels aligned with production practices
- Correlation IDs for request tracing

BMAD C.O.R.E. Integration:
- Collaboration: Clear log messages for debugging
- Optimized: Minimal overhead, lazy evaluation
- Reflection: Honest reporting of errors and warnings
- Engine: Consistent format across all components
"""
import logging
import json
import sys
from typing import Any, Optional
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass, field
import threading


# Thread-local storage for context
_context = threading.local()


@dataclass
class LogContext:
    """Contextual information for structured logging."""
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    library: Optional[str] = None
    trust_level: Optional[int] = None
    user_id: Optional[str] = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {}
        if self.session_id:
            result["session_id"] = self.session_id
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.library:
            result["library"] = self.library
        if self.trust_level is not None:
            result["trust_level"] = self.trust_level
        if self.user_id:
            result["user_id"] = self.user_id
        result.update(self.extra)
        return result


def get_context() -> LogContext:
    """Get the current thread's log context."""
    if not hasattr(_context, "log_context"):
        _context.log_context = LogContext()
    return _context.log_context


def set_context(**kwargs) -> None:
    """Set context fields for the current thread."""
    ctx = get_context()
    for key, value in kwargs.items():
        if hasattr(ctx, key):
            setattr(ctx, key, value)
        else:
            ctx.extra[key] = value


def clear_context() -> None:
    """Clear the current thread's context."""
    _context.log_context = LogContext()


@contextmanager
def log_context(**kwargs):
    """Context manager for temporary log context.

    Usage:
        with log_context(session_id="abc123", library="langgraph"):
            logger.info("Generating skill")
    """
    ctx = get_context()
    old_values = {}

    # Save old values and set new ones
    for key, value in kwargs.items():
        if hasattr(ctx, key):
            old_values[key] = getattr(ctx, key)
            setattr(ctx, key, value)
        else:
            old_values[key] = ctx.extra.get(key)
            ctx.extra[key] = value

    try:
        yield ctx
    finally:
        # Restore old values
        for key, value in old_values.items():
            if hasattr(ctx, key):
                setattr(ctx, key, value)
            elif value is None:
                ctx.extra.pop(key, None)
            else:
                ctx.extra[key] = value


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Output format:
    {
        "timestamp": "2024-01-15T10:30:00.000Z",
        "level": "INFO",
        "logger": "skills_fabric.trust",
        "message": "Skill verified successfully",
        "session_id": "abc123",
        "library": "langgraph",
        "trust_level": 1,
        "duration_ms": 150
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context fields
        ctx = get_context()
        log_entry.update(ctx.to_dict())

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the log record
        for key in ["duration_ms", "skill_id", "error_type", "iteration"]:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        return json.dumps(log_entry, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter.

    Output format:
    2024-01-15 10:30:00 [INFO] skills_fabric.trust: Skill verified successfully
    """

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record for console output."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.use_colors:
            color = self.COLORS.get(record.levelname, "")
            level = f"{color}[{record.levelname}]{self.RESET}"
        else:
            level = f"[{record.levelname}]"

        message = record.getMessage()

        # Add context summary
        ctx = get_context()
        ctx_parts = []
        if ctx.session_id:
            ctx_parts.append(f"session={ctx.session_id[:8]}")
        if ctx.library:
            ctx_parts.append(f"lib={ctx.library}")

        ctx_str = f" ({', '.join(ctx_parts)})" if ctx_parts else ""

        formatted = f"{timestamp} {level} {record.name}: {message}{ctx_str}"

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


def configure_logging(
    level: str = "INFO",
    format: str = "console",
    output: str = "stderr"
) -> None:
    """Configure logging for Skills Fabric.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Output format ("console" or "json")
        output: Output destination ("stderr", "stdout", or file path)
    """
    root_logger = logging.getLogger("skills_fabric")
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handler
    if output == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(output)

    # Set formatter
    if format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        use_colors = output in ("stderr", "stdout") and sys.stderr.isatty()
        handler.setFormatter(ConsoleFormatter(use_colors=use_colors))

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given name.

    Args:
        name: Logger name (will be prefixed with 'skills_fabric.')

    Returns:
        Configured logger instance
    """
    if not name.startswith("skills_fabric"):
        name = f"skills_fabric.{name}"
    return logging.getLogger(name)


# =============================================================================
# Convenience Logging Functions
# =============================================================================

class SkillsLogger:
    """High-level logger for common Skills Fabric operations.

    Usage:
        logger = SkillsLogger("trust")
        logger.skill_generated("langgraph", skill_id="s1")
        logger.verification_passed(trust_level=1, duration_ms=150)
        logger.verification_failed("No grounding evidence")
    """

    def __init__(self, component: str):
        self.logger = get_logger(component)

    def skill_generated(self, library: str, skill_id: str = "", **kwargs):
        """Log skill generation."""
        self.logger.info(
            f"Skill generated: {skill_id or 'unknown'}",
            extra={"library": library, "skill_id": skill_id, **kwargs}
        )

    def verification_passed(self, trust_level: int, duration_ms: float = 0, **kwargs):
        """Log successful verification."""
        self.logger.info(
            f"Verification passed at trust level {trust_level}",
            extra={"trust_level": trust_level, "duration_ms": duration_ms, **kwargs}
        )

    def verification_failed(self, reason: str, **kwargs):
        """Log failed verification."""
        self.logger.warning(
            f"Verification failed: {reason}",
            extra={"error_type": "verification_failed", **kwargs}
        )

    def iteration_started(self, iteration: int, max_iterations: int, **kwargs):
        """Log iteration start."""
        self.logger.debug(
            f"Starting iteration {iteration}/{max_iterations}",
            extra={"iteration": iteration, **kwargs}
        )

    def iteration_completed(self, iteration: int, success: bool, **kwargs):
        """Log iteration completion."""
        status = "succeeded" if success else "failed"
        self.logger.info(
            f"Iteration {iteration} {status}",
            extra={"iteration": iteration, "success": success, **kwargs}
        )

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log an error."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning."""
        self.logger.warning(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)


# Default configuration on import
configure_logging()
