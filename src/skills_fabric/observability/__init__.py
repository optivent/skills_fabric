"""Observability module for Skills Fabric.

Production-grade monitoring and debugging:
- Metrics: Counters, gauges, histograms, timers
- Logging: Structured JSON logging with context
- Tracing: Distributed tracing with span management

Key Features:
- Thread-safe metric collection
- Contextual logging with correlation IDs
- OpenTelemetry-compatible tracing
- Multiple backend support (in-memory, Prometheus, Jaeger)

Usage:
    from skills_fabric.observability import (
        # Metrics
        MetricsRegistry, SkillsMetrics, get_metrics,
        # Logging
        SkillsLogger, configure_logging, log_context,
        # Tracing
        SkillsTracer, get_tracer, get_skills_tracer,
    )

    # Metrics
    metrics = SkillsMetrics()
    metrics.skill_generated(library="langgraph")
    with metrics.generation_duration("langgraph"):
        generate_skill()

    # Logging
    configure_logging(level="INFO", format="json")
    logger = SkillsLogger("trust")
    with log_context(session_id="abc123"):
        logger.verification_passed(trust_level=1)

    # Tracing
    tracer = get_skills_tracer()
    with tracer.skill_generation("langgraph") as span:
        span.add_event("mining_completed")
"""
from .metrics import (
    MetricType,
    MetricValue,
    MetricsRegistry,
    TimerContext,
    SkillsMetrics,
    get_metrics,
)
from .logging import (
    LogContext,
    JSONFormatter,
    ConsoleFormatter,
    SkillsLogger,
    configure_logging,
    get_logger,
    get_context,
    set_context,
    clear_context,
    log_context,
)
from .tracing import (
    SpanStatus,
    SpanEvent,
    Span,
    TracerProvider,
    Tracer,
    SkillsTracer,
    get_tracer,
    get_provider,
    get_skills_tracer,
    console_exporter,
    json_exporter,
)

__all__ = [
    # Metrics
    "MetricType",
    "MetricValue",
    "MetricsRegistry",
    "TimerContext",
    "SkillsMetrics",
    "get_metrics",
    # Logging
    "LogContext",
    "JSONFormatter",
    "ConsoleFormatter",
    "SkillsLogger",
    "configure_logging",
    "get_logger",
    "get_context",
    "set_context",
    "clear_context",
    "log_context",
    # Tracing
    "SpanStatus",
    "SpanEvent",
    "Span",
    "TracerProvider",
    "Tracer",
    "SkillsTracer",
    "get_tracer",
    "get_provider",
    "get_skills_tracer",
    "console_exporter",
    "json_exporter",
]
