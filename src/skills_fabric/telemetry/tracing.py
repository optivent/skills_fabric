"""OpenTelemetry Tracing for Skills Fabric.

Provides distributed tracing for the LangGraph agent pipeline.
Traces can be exported to Jaeger, Zipkin, or any OTLP-compatible backend.

Usage:
    from skills_fabric.telemetry import init_tracing, trace_agent

    # Initialize once at startup
    init_tracing(service_name="skills-fabric", endpoint="http://localhost:4317")

    # Use decorator on agent methods
    @trace_agent("researcher")
    def research(self, query):
        ...

    # Or use context manager
    with tracer.start_as_current_span("generate_skill") as span:
        span.set_attribute("skill.library", "docling")
        ...
"""
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Optional, Callable, Any
import time
import json

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


@dataclass
class TracingConfig:
    """Configuration for tracing."""
    service_name: str = "skills-fabric"
    endpoint: Optional[str] = None  # OTLP endpoint
    console_export: bool = False  # Also export to console
    sample_rate: float = 1.0  # 1.0 = trace everything
    enabled: bool = True


# Global tracer instance
_tracer: Optional[Any] = None
_config: Optional[TracingConfig] = None


def init_tracing(
    service_name: str = "skills-fabric",
    endpoint: Optional[str] = None,
    console_export: bool = False,
    sample_rate: float = 1.0,
) -> bool:
    """Initialize OpenTelemetry tracing.

    Args:
        service_name: Name for this service in traces
        endpoint: OTLP endpoint (e.g., "http://localhost:4317")
        console_export: Also print spans to console
        sample_rate: Sampling rate (0.0 to 1.0)

    Returns:
        True if tracing initialized successfully
    """
    global _tracer, _config

    if not OTEL_AVAILABLE:
        print("Warning: OpenTelemetry not available, tracing disabled")
        return False

    _config = TracingConfig(
        service_name=service_name,
        endpoint=endpoint,
        console_export=console_export,
        sample_rate=sample_rate,
    )

    # Create resource with service info
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": "development",
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint provided
    if endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Add console exporter if requested
    if console_export:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    # Get tracer
    _tracer = trace.get_tracer(__name__)

    return True


def get_tracer():
    """Get the global tracer instance."""
    global _tracer
    if _tracer is None and OTEL_AVAILABLE:
        # Initialize with defaults if not already done
        init_tracing()
    return _tracer


def trace_agent(agent_name: str):
    """Decorator to trace agent execution.

    Args:
        agent_name: Name of the agent (researcher, generator, etc.)

    Example:
        @trace_agent("researcher")
        def execute(self, task):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()

            if tracer is None:
                return func(*args, **kwargs)

            with tracer.start_as_current_span(
                f"agent.{agent_name}.{func.__name__}"
            ) as span:
                # Set agent attributes
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.function", func.__name__)

                # Extract task info if available
                if args and hasattr(args[0], '__class__'):
                    span.set_attribute("agent.class", args[0].__class__.__name__)

                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    # Record success
                    span.set_status(Status(StatusCode.OK))

                    # Add result attributes if available
                    if hasattr(result, 'success'):
                        span.set_attribute("result.success", result.success)
                    if hasattr(result, 'output'):
                        span.set_attribute("result.has_output", result.output is not None)

                    return result

                except Exception as e:
                    # Record error
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("duration_ms", duration_ms)

        return wrapper
    return decorator


def trace_langgraph_node(node_name: str):
    """Decorator for LangGraph node functions.

    Args:
        node_name: Name of the graph node

    Example:
        @trace_langgraph_node("research")
        def research_node(state: GraphState) -> GraphState:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state, *args, **kwargs):
            tracer = get_tracer()

            if tracer is None:
                return func(state, *args, **kwargs)

            with tracer.start_as_current_span(f"node.{node_name}") as span:
                span.set_attribute("langgraph.node", node_name)

                # Capture input state keys
                if isinstance(state, dict):
                    span.set_attribute("state.keys", list(state.keys()))

                start_time = time.time()

                try:
                    result = func(state, *args, **kwargs)

                    span.set_status(Status(StatusCode.OK))

                    # Capture output state changes
                    if isinstance(result, dict):
                        span.set_attribute("result.keys", list(result.keys()))

                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("duration_ms", duration_ms)

        return wrapper
    return decorator


@contextmanager
def trace_span(
    name: str,
    attributes: Optional[dict] = None,
):
    """Context manager for creating a traced span.

    Args:
        name: Span name
        attributes: Optional attributes to set

    Example:
        with trace_span("verify_citations", {"skill_id": "docling:pdf"}) as span:
            result = verify(...)
            span.set_attribute("citations.count", len(result))
    """
    tracer = get_tracer()

    if tracer is None:
        # No-op context manager when tracing disabled
        yield None
        return

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        yield span


class AgentTracer:
    """Helper class for tracing agent pipelines.

    Provides structured tracing for the skills generation pipeline.
    """

    def __init__(self, pipeline_name: str = "skills_generation"):
        self.pipeline_name = pipeline_name
        self.tracer = get_tracer()

    @contextmanager
    def trace_pipeline(self, library: str, **attributes):
        """Trace an entire pipeline execution.

        Args:
            library: Target library name
            **attributes: Additional span attributes
        """
        if self.tracer is None:
            yield None
            return

        with self.tracer.start_as_current_span(
            f"pipeline.{self.pipeline_name}"
        ) as span:
            span.set_attribute("pipeline.name", self.pipeline_name)
            span.set_attribute("pipeline.library", library)

            for key, value in attributes.items():
                span.set_attribute(f"pipeline.{key}", value)

            yield span

    @contextmanager
    def trace_stage(self, stage_name: str, **attributes):
        """Trace a pipeline stage.

        Args:
            stage_name: Name of the stage (research, generate, verify, etc.)
            **attributes: Additional span attributes
        """
        if self.tracer is None:
            yield None
            return

        with self.tracer.start_as_current_span(
            f"stage.{stage_name}"
        ) as span:
            span.set_attribute("stage.name", stage_name)

            for key, value in attributes.items():
                span.set_attribute(f"stage.{key}", value)

            yield span

    def record_verification(
        self,
        span,
        total_claims: int,
        verified_claims: int,
        hall_m: float,
    ):
        """Record verification metrics on a span.

        Args:
            span: Current span
            total_claims: Total number of claims
            verified_claims: Number of verified claims
            hall_m: Hallucination rate
        """
        if span is None:
            return

        span.set_attribute("verification.total_claims", total_claims)
        span.set_attribute("verification.verified_claims", verified_claims)
        span.set_attribute("verification.hall_m", hall_m)
        span.set_attribute("verification.passed", hall_m < 0.02)

    def record_skill_generated(
        self,
        span,
        skill_id: str,
        citations: int,
        level: int,
    ):
        """Record skill generation on a span.

        Args:
            span: Current span
            skill_id: Generated skill ID
            citations: Number of citations
            level: Progressive disclosure level
        """
        if span is None:
            return

        span.set_attribute("skill.id", skill_id)
        span.set_attribute("skill.citations", citations)
        span.set_attribute("skill.level", level)


class LangGraphTracer:
    """Integrates tracing with LangGraph execution.

    Can be used as a callback or wrapper for graph execution.
    """

    def __init__(self, graph_name: str = "skills_graph"):
        self.graph_name = graph_name
        self.tracer = get_tracer()
        self._current_span = None

    def on_graph_start(self, inputs: dict):
        """Called when graph execution starts."""
        if self.tracer is None:
            return

        self._current_span = self.tracer.start_span(
            f"graph.{self.graph_name}"
        )
        self._current_span.set_attribute("graph.name", self.graph_name)
        self._current_span.set_attribute("graph.input_keys", list(inputs.keys()))

    def on_graph_end(self, outputs: dict, error: Optional[Exception] = None):
        """Called when graph execution ends."""
        if self._current_span is None:
            return

        if error:
            self._current_span.set_status(Status(StatusCode.ERROR, str(error)))
            self._current_span.record_exception(error)
        else:
            self._current_span.set_status(Status(StatusCode.OK))
            self._current_span.set_attribute("graph.output_keys", list(outputs.keys()))

        self._current_span.end()
        self._current_span = None

    def on_node_start(self, node_name: str, inputs: dict):
        """Called when a node starts executing."""
        if self.tracer is None:
            return None

        span = self.tracer.start_span(
            f"node.{node_name}",
            context=trace.set_span_in_context(self._current_span) if self._current_span else None,
        )
        span.set_attribute("node.name", node_name)
        return span

    def on_node_end(self, span, outputs: dict, error: Optional[Exception] = None):
        """Called when a node finishes executing."""
        if span is None:
            return

        if error:
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.record_exception(error)
        else:
            span.set_status(Status(StatusCode.OK))

        span.end()


def shutdown_tracing():
    """Shutdown tracing and flush pending spans."""
    if OTEL_AVAILABLE:
        provider = trace.get_tracer_provider()
        if hasattr(provider, 'shutdown'):
            provider.shutdown()


# Export utilities
def get_trace_context() -> dict:
    """Get current trace context for propagation."""
    if not OTEL_AVAILABLE:
        return {}

    propagator = TraceContextTextMapPropagator()
    carrier = {}
    propagator.inject(carrier)
    return carrier


def set_trace_context(carrier: dict):
    """Set trace context from propagated headers."""
    if not OTEL_AVAILABLE:
        return None

    propagator = TraceContextTextMapPropagator()
    return propagator.extract(carrier)
