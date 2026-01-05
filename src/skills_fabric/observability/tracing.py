"""Distributed Tracing - Request tracing for Skills Fabric.

Implements OpenTelemetry-compatible tracing:
- Span creation and management
- Context propagation across components
- Integration with external systems (Jaeger, Zipkin)
- Skill generation pipeline tracing

Supports multiple backends:
- In-memory (default, for development)
- OpenTelemetry (production)
- Console (debugging)
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum
from contextlib import contextmanager
import threading
import uuid


class SpanStatus(Enum):
    """Status of a tracing span."""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanEvent:
    """An event within a span."""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: dict = field(default_factory=dict)


@dataclass
class Span:
    """A tracing span representing a unit of work.

    Spans form a tree structure:
    - Root span: The outermost operation
    - Child spans: Nested operations within a parent
    """
    trace_id: str
    span_id: str
    name: str
    parent_span_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: dict = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict = None) -> None:
        """Add an event to the span."""
        self.events.append(SpanEvent(
            name=name,
            attributes=attributes or {}
        ))

    def set_status(self, status: SpanStatus, description: str = "") -> None:
        """Set the span status."""
        self.status = status
        if description:
            self.attributes["status.description"] = description

    def end(self) -> None:
        """End the span."""
        self.end_time = datetime.now()

    @property
    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds."""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000

    def to_dict(self) -> dict:
        """Convert span to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "attributes": self.attributes,
            "events": [
                {"name": e.name, "timestamp": e.timestamp.isoformat(), "attributes": e.attributes}
                for e in self.events
            ]
        }


# Thread-local storage for current span context
_trace_context = threading.local()


def _get_current_span() -> Optional[Span]:
    """Get the current span for this thread."""
    return getattr(_trace_context, "current_span", None)


def _set_current_span(span: Optional[Span]) -> None:
    """Set the current span for this thread."""
    _trace_context.current_span = span


def _generate_id() -> str:
    """Generate a unique ID for traces/spans."""
    return uuid.uuid4().hex[:16]


class TracerProvider:
    """Tracer provider managing all tracers and spans.

    Usage:
        provider = TracerProvider()
        tracer = provider.get_tracer("skills_fabric.trust")

        with tracer.start_span("verify_skill") as span:
            span.set_attribute("skill_id", "s1")
            # ... do work ...
    """

    def __init__(self):
        self._tracers: dict[str, "Tracer"] = {}
        self._spans: list[Span] = []
        self._lock = threading.Lock()
        self._exporters: list[Callable[[Span], None]] = []

    def get_tracer(self, name: str) -> "Tracer":
        """Get or create a tracer for the given name."""
        if name not in self._tracers:
            self._tracers[name] = Tracer(name, self)
        return self._tracers[name]

    def record_span(self, span: Span) -> None:
        """Record a completed span."""
        with self._lock:
            self._spans.append(span)
            # Export to all registered exporters
            for exporter in self._exporters:
                try:
                    exporter(span)
                except Exception:
                    pass  # Don't let exporter errors affect tracing

    def add_exporter(self, exporter: Callable[[Span], None]) -> None:
        """Add a span exporter."""
        self._exporters.append(exporter)

    def get_all_spans(self) -> list[Span]:
        """Get all recorded spans."""
        with self._lock:
            return list(self._spans)

    def get_trace(self, trace_id: str) -> list[Span]:
        """Get all spans for a trace."""
        with self._lock:
            return [s for s in self._spans if s.trace_id == trace_id]

    def clear(self) -> None:
        """Clear all recorded spans."""
        with self._lock:
            self._spans.clear()


class Tracer:
    """Creates and manages spans for a specific component.

    Usage:
        tracer = get_tracer("skills_fabric.orchestration")

        with tracer.start_span("generate_skill") as span:
            span.set_attribute("library", "langgraph")

            with tracer.start_span("verify") as child:
                child.set_attribute("trust_level", 1)
    """

    def __init__(self, name: str, provider: TracerProvider):
        self.name = name
        self._provider = provider

    @contextmanager
    def start_span(
        self,
        name: str,
        attributes: dict = None,
        kind: str = "internal"
    ):
        """Start a new span as a context manager.

        Args:
            name: Span name
            attributes: Initial span attributes
            kind: Span kind (internal, server, client, producer, consumer)

        Yields:
            The created span
        """
        parent = _get_current_span()

        span = Span(
            trace_id=parent.trace_id if parent else _generate_id(),
            span_id=_generate_id(),
            name=f"{self.name}.{name}",
            parent_span_id=parent.span_id if parent else None,
            attributes={"span.kind": kind, **(attributes or {})}
        )

        _set_current_span(span)

        try:
            yield span
            if span.status == SpanStatus.UNSET:
                span.set_status(SpanStatus.OK)
        except Exception as e:
            span.set_status(SpanStatus.ERROR, str(e))
            span.set_attribute("exception.type", type(e).__name__)
            span.set_attribute("exception.message", str(e))
            raise
        finally:
            span.end()
            _set_current_span(parent)
            self._provider.record_span(span)

    def start_as_current_span(
        self,
        name: str,
        attributes: dict = None
    ):
        """Decorator to wrap a function in a span.

        Usage:
            @tracer.start_as_current_span("process_data")
            def process_data(x):
                return x * 2
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.start_span(name, attributes):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


# Global tracer provider
_provider = TracerProvider()


def get_tracer(name: str) -> Tracer:
    """Get a tracer from the global provider.

    Args:
        name: Tracer name (e.g., "skills_fabric.trust")

    Returns:
        Tracer instance
    """
    return _provider.get_tracer(name)


def get_provider() -> TracerProvider:
    """Get the global tracer provider."""
    return _provider


# =============================================================================
# Exporters
# =============================================================================

def console_exporter(span: Span) -> None:
    """Export spans to console for debugging."""
    indent = "  " if span.parent_span_id else ""
    status_icon = "✓" if span.status == SpanStatus.OK else "✗"
    print(f"{indent}{status_icon} {span.name} ({span.duration_ms:.1f}ms)")
    for key, value in span.attributes.items():
        if not key.startswith("span."):
            print(f"{indent}    {key}={value}")


def json_exporter(output_file: str) -> Callable[[Span], None]:
    """Create a JSON file exporter.

    Args:
        output_file: Path to output file

    Returns:
        Exporter function
    """
    import json

    def exporter(span: Span) -> None:
        with open(output_file, "a") as f:
            f.write(json.dumps(span.to_dict()) + "\n")

    return exporter


# =============================================================================
# Skills Fabric Tracing Utilities
# =============================================================================

class SkillsTracer:
    """High-level tracing for Skills Fabric operations.

    Usage:
        tracer = SkillsTracer()

        with tracer.skill_generation("langgraph") as span:
            span.add_event("mining_started")
            # ... mining ...
            span.add_event("mining_completed", {"symbols_found": 42})

            with tracer.verification() as verify_span:
                # ... verification ...
                pass
    """

    def __init__(self):
        self.tracer = get_tracer("skills_fabric")

    @contextmanager
    def skill_generation(self, library: str, question: str = ""):
        """Trace skill generation."""
        with self.tracer.start_span(
            "skill_generation",
            attributes={"library": library, "question": question[:100]}
        ) as span:
            yield span

    @contextmanager
    def verification(self, trust_level: int = 0):
        """Trace verification."""
        with self.tracer.start_span(
            "verification",
            attributes={"trust_level": trust_level}
        ) as span:
            yield span

    @contextmanager
    def ralph_wiggum_iteration(self, iteration: int, max_iterations: int):
        """Trace a Ralph Wiggum iteration."""
        with self.tracer.start_span(
            "ralph_wiggum_iteration",
            attributes={"iteration": iteration, "max_iterations": max_iterations}
        ) as span:
            yield span

    @contextmanager
    def agent_execution(self, agent_name: str, role: str = ""):
        """Trace agent execution."""
        with self.tracer.start_span(
            f"agent.{agent_name}",
            attributes={"role": role}
        ) as span:
            yield span

    @contextmanager
    def sandbox_execution(self, code_hash: str = ""):
        """Trace sandbox code execution."""
        with self.tracer.start_span(
            "sandbox_execution",
            attributes={"code_hash": code_hash}
        ) as span:
            yield span


def get_skills_tracer() -> SkillsTracer:
    """Get a SkillsTracer instance."""
    return SkillsTracer()
