#!/usr/bin/env python3
"""Test OpenTelemetry Tracing Integration."""

import sys
import importlib.util
import time

# Load tracing module
spec = importlib.util.spec_from_file_location(
    "tracing",
    "/home/user/skills_fabric/src/skills_fabric/telemetry/tracing.py"
)
tracing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracing)

init_tracing = tracing.init_tracing
get_tracer = tracing.get_tracer
trace_agent = tracing.trace_agent
trace_langgraph_node = tracing.trace_langgraph_node
trace_span = tracing.trace_span
AgentTracer = tracing.AgentTracer
LangGraphTracer = tracing.LangGraphTracer
OTEL_AVAILABLE = tracing.OTEL_AVAILABLE


def test_otel_availability():
    """Test OpenTelemetry is available."""
    print("=" * 60)
    print("TEST 1: OpenTelemetry Availability")
    print("=" * 60)

    print(f"✓ OpenTelemetry available: {OTEL_AVAILABLE}")
    assert OTEL_AVAILABLE, "OpenTelemetry should be available"

    return True


def test_init_tracing():
    """Test initializing tracing."""
    print("\n" + "=" * 60)
    print("TEST 2: Initialize Tracing")
    print("=" * 60)

    # Initialize with console export for testing
    result = init_tracing(
        service_name="test-service",
        console_export=False,  # Set True to see spans
    )

    print(f"✓ Tracing initialized: {result}")
    assert result, "Tracing should initialize"

    tracer = get_tracer()
    print(f"✓ Got tracer: {tracer is not None}")
    assert tracer is not None

    return True


def test_trace_agent_decorator():
    """Test the trace_agent decorator."""
    print("\n" + "=" * 60)
    print("TEST 3: trace_agent Decorator")
    print("=" * 60)

    class MockAgent:
        @trace_agent("researcher")
        def execute(self, query: str) -> dict:
            time.sleep(0.01)  # Simulate work
            return {"success": True, "output": f"Result for: {query}"}

    agent = MockAgent()
    result = agent.execute("test query")

    print(f"✓ Decorated method executed")
    print(f"  Result: {result}")
    assert result["success"]

    return True


def test_trace_langgraph_node():
    """Test the trace_langgraph_node decorator."""
    print("\n" + "=" * 60)
    print("TEST 4: trace_langgraph_node Decorator")
    print("=" * 60)

    @trace_langgraph_node("research")
    def research_node(state: dict) -> dict:
        time.sleep(0.01)
        return {**state, "researched": True}

    input_state = {"query": "test", "library": "docling"}
    output_state = research_node(input_state)

    print(f"✓ Node function executed")
    print(f"  Input keys: {list(input_state.keys())}")
    print(f"  Output keys: {list(output_state.keys())}")
    assert output_state["researched"]

    return True


def test_trace_span_context():
    """Test the trace_span context manager."""
    print("\n" + "=" * 60)
    print("TEST 5: trace_span Context Manager")
    print("=" * 60)

    with trace_span("verify_skill", {"skill_id": "docling:pdf"}) as span:
        time.sleep(0.01)
        if span:
            span.set_attribute("citations.count", 5)
            span.set_attribute("hall_m", 0.0)

    print("✓ Context manager executed")
    print("  Attributes set on span")

    return True


def test_agent_tracer():
    """Test AgentTracer helper class."""
    print("\n" + "=" * 60)
    print("TEST 6: AgentTracer Helper")
    print("=" * 60)

    tracer = AgentTracer("test_pipeline")

    with tracer.trace_pipeline("docling", version="1.0") as span:
        print("✓ Pipeline span created")

        with tracer.trace_stage("research", query="pdf conversion") as stage_span:
            print("  ✓ Research stage span created")
            time.sleep(0.01)

        with tracer.trace_stage("verify") as verify_span:
            print("  ✓ Verify stage span created")
            tracer.record_verification(verify_span, 10, 10, 0.0)

        with tracer.trace_stage("generate") as gen_span:
            print("  ✓ Generate stage span created")
            tracer.record_skill_generated(gen_span, "docling:pdf", 5, 3)

    return True


def test_langgraph_tracer():
    """Test LangGraphTracer for graph execution."""
    print("\n" + "=" * 60)
    print("TEST 7: LangGraphTracer")
    print("=" * 60)

    tracer = LangGraphTracer("test_graph")

    # Simulate graph execution
    inputs = {"query": "test", "library": "docling"}
    tracer.on_graph_start(inputs)
    print("✓ Graph started")

    # Simulate node execution
    node_span = tracer.on_node_start("research", {"query": "test"})
    time.sleep(0.01)
    tracer.on_node_end(node_span, {"results": []})
    print("  ✓ Research node completed")

    node_span = tracer.on_node_start("generate", {"results": []})
    time.sleep(0.01)
    tracer.on_node_end(node_span, {"skill": "content"})
    print("  ✓ Generate node completed")

    outputs = {"skill": "content", "hall_m": 0.0}
    tracer.on_graph_end(outputs)
    print("✓ Graph ended")

    return True


def test_error_tracing():
    """Test error recording in traces."""
    print("\n" + "=" * 60)
    print("TEST 8: Error Tracing")
    print("=" * 60)

    @trace_agent("faulty")
    def failing_function():
        raise ValueError("Test error")

    try:
        failing_function()
        assert False, "Should have raised"
    except ValueError as e:
        print(f"✓ Error caught: {e}")
        print("  Error recorded in span")

    return True


def test_nested_spans():
    """Test nested span creation."""
    print("\n" + "=" * 60)
    print("TEST 9: Nested Spans")
    print("=" * 60)

    with trace_span("outer", {"level": "1"}) as outer:
        print("✓ Outer span created")

        with trace_span("middle", {"level": "2"}) as middle:
            print("  ✓ Middle span created")

            with trace_span("inner", {"level": "3"}) as inner:
                print("    ✓ Inner span created")
                time.sleep(0.01)

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OPENTELEMETRY TRACING TEST SUITE")
    print("=" * 60)
    print(f"OpenTelemetry available: {OTEL_AVAILABLE}")

    tests = [
        test_otel_availability,
        test_init_tracing,
        test_trace_agent_decorator,
        test_trace_langgraph_node,
        test_trace_span_context,
        test_agent_tracer,
        test_langgraph_tracer,
        test_error_tracing,
        test_nested_spans,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    # Cleanup
    tracing.shutdown_tracing()

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
