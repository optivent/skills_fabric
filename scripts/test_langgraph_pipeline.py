#!/usr/bin/env python3
"""Test LangGraph Pipeline with GLM-4.7 SDK."""

import sys
import os
import importlib.util

# Load modules using importlib
spec_glm = importlib.util.spec_from_file_location(
    "glm_client",
    "/home/user/skills_fabric/src/skills_fabric/llm/glm_client.py"
)
glm_client = importlib.util.module_from_spec(spec_glm)
sys.modules['glm_client'] = glm_client
spec_glm.loader.exec_module(glm_client)

spec_tracing = importlib.util.spec_from_file_location(
    "tracing",
    "/home/user/skills_fabric/src/skills_fabric/telemetry/tracing.py"
)
tracing = importlib.util.module_from_spec(spec_tracing)
spec_tracing.loader.exec_module(tracing)

spec_pipeline = importlib.util.spec_from_file_location(
    "langgraph_pipeline",
    "/home/user/skills_fabric/src/skills_fabric/pipeline/langgraph_pipeline.py"
)
pipeline_module = importlib.util.module_from_spec(spec_pipeline)
spec_pipeline.loader.exec_module(pipeline_module)

# Extract classes
SkillState = pipeline_module.SkillState
SkillGenerationPipeline = pipeline_module.SkillGenerationPipeline
create_skill_graph = pipeline_module.create_skill_graph
research_node = pipeline_module.research_node
verify_node = pipeline_module.verify_node

# Check for API key
API_KEY = os.getenv("ZAI_API_KEY", os.getenv("GLM_API_KEY", ""))
LIVE_TEST = bool(API_KEY)


def test_skill_state():
    """Test SkillState TypedDict."""
    print("=" * 60)
    print("TEST 1: SkillState TypedDict")
    print("=" * 60)

    state: SkillState = {
        "library": "test_lib",
        "topic": "testing",
        "level": 3,
        "symbols": [],
        "documentation": "",
        "content": "",
        "thinking": "",
        "citations": [],
        "hall_m": 0.0,
        "verified_citations": 0,
        "total_citations": 0,
        "passed": False,
        "retry_count": 0,
        "max_retries": 2,
        "error": None,
        "final_skill": None,
        "token_usage": {},
    }

    print(f"✓ Created SkillState")
    print(f"  Library: {state['library']}")
    print(f"  Level: {state['level']}")
    print(f"  Max retries: {state['max_retries']}")

    assert state["library"] == "test_lib"
    assert state["level"] == 3

    return True


def test_research_node():
    """Test research node in isolation."""
    print("\n" + "=" * 60)
    print("TEST 2: Research Node")
    print("=" * 60)

    state: SkillState = {
        "library": "pandas",
        "topic": "DataFrame creation",
        "level": 2,
        "symbols": [],
        "documentation": "",
        "content": "",
        "thinking": "",
        "citations": [],
        "hall_m": 0.0,
        "verified_citations": 0,
        "total_citations": 0,
        "passed": False,
        "retry_count": 0,
        "max_retries": 2,
        "error": None,
        "final_skill": None,
        "token_usage": {},
    }

    result = research_node(state)

    print(f"✓ Research node executed")
    print(f"  Symbols found: {len(result['symbols'])}")
    print(f"  Documentation length: {len(result['documentation'])}")

    assert "symbols" in result
    assert "documentation" in result
    assert len(result["symbols"]) > 0

    return True


def test_verify_node():
    """Test verify node with citations."""
    print("\n" + "=" * 60)
    print("TEST 3: Verify Node")
    print("=" * 60)

    # Create state with citations that should pass
    state: SkillState = {
        "library": "test_lib",
        "topic": "testing",
        "level": 3,
        "symbols": [
            {"name": "test_lib.main_class", "citation": "test_lib/core.py:42"},
            {"name": "test_lib.helper_func", "citation": "test_lib/utils.py:15"},
        ],
        "documentation": "",
        "content": "Use the main_class from test_lib/core.py:42",
        "thinking": "",
        "citations": ["test_lib/core.py:42", "test_lib/utils.py:15"],
        "hall_m": 0.0,
        "verified_citations": 0,
        "total_citations": 0,
        "passed": False,
        "retry_count": 0,
        "max_retries": 2,
        "error": None,
        "final_skill": None,
        "token_usage": {},
    }

    result = verify_node(state)

    print(f"✓ Verify node executed")
    print(f"  Hall_m: {result['hall_m']:.2%}")
    print(f"  Verified: {result['verified_citations']}/{result['total_citations']}")
    print(f"  Passed: {result['passed']}")

    # Should pass with these valid citations
    assert result["hall_m"] < 0.5
    assert result["verified_citations"] > 0

    return True


def test_verify_hallucination_detection():
    """Test that verify node detects hallucinations."""
    print("\n" + "=" * 60)
    print("TEST 4: Hallucination Detection")
    print("=" * 60)

    # Create state with hallucination patterns
    state: SkillState = {
        "library": "test_lib",
        "topic": "testing",
        "level": 3,
        "symbols": [
            {"name": "test_lib.main_class", "citation": "test_lib/core.py:42"},
        ],
        "documentation": "",
        "content": "This might work: import fake_library",
        "thinking": "",
        "citations": ["nonexistent/file.py:99"],
        "hall_m": 0.0,
        "verified_citations": 0,
        "total_citations": 0,
        "passed": False,
        "retry_count": 0,
        "max_retries": 2,
        "error": None,
        "final_skill": None,
        "token_usage": {},
    }

    result = verify_node(state)

    print(f"✓ Hallucination detection executed")
    print(f"  Hall_m: {result['hall_m']:.2%}")
    print(f"  Passed: {result['passed']}")

    # Should fail due to hallucinations
    assert result["hall_m"] > 0.02
    assert not result["passed"]

    return True


def test_graph_creation():
    """Test graph creation."""
    print("\n" + "=" * 60)
    print("TEST 5: Graph Creation")
    print("=" * 60)

    graph = create_skill_graph()

    print(f"✓ Created StateGraph")
    print(f"  Nodes: {list(graph.nodes.keys())}")

    assert "research" in graph.nodes
    assert "generate" in graph.nodes
    assert "verify" in graph.nodes
    assert "store" in graph.nodes

    return True


def test_pipeline_creation():
    """Test pipeline creation."""
    print("\n" + "=" * 60)
    print("TEST 6: Pipeline Creation")
    print("=" * 60)

    pipeline = SkillGenerationPipeline(checkpointing=False)

    print(f"✓ Created SkillGenerationPipeline")
    print(f"  App compiled: {pipeline.app is not None}")
    print(f"  Tracer initialized: {pipeline.tracer is not None}")

    return True


def test_visualization():
    """Test graph visualization."""
    print("\n" + "=" * 60)
    print("TEST 7: Graph Visualization")
    print("=" * 60)

    pipeline = SkillGenerationPipeline(checkpointing=False)
    mermaid = pipeline.get_visualization()

    print(f"✓ Generated visualization")
    if mermaid and mermaid != "Visualization not available":
        print(f"  Mermaid diagram length: {len(mermaid)}")
        # Print first few lines
        lines = mermaid.split("\n")[:5]
        for line in lines:
            print(f"    {line}")
    else:
        print(f"  Visualization: {mermaid}")

    return True


def test_live_pipeline():
    """Test live pipeline execution."""
    print("\n" + "=" * 60)
    print("TEST 8: Live Pipeline Execution")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    pipeline = SkillGenerationPipeline(checkpointing=False)

    result = pipeline.generate(
        library="requests",
        topic="HTTP GET request",
        level=2,
        max_retries=1,
    )

    print(f"✓ Pipeline execution completed")
    print(f"  Library: {result['library']}")
    print(f"  Topic: {result['topic']}")
    print(f"  Passed: {result['passed']}")
    print(f"  Hall_m: {result['hall_m']:.2%}")
    print(f"  Citations: {result['verified_citations']}/{result['total_citations']}")
    print(f"  Retries: {result['retry_count']}")
    print(f"  Tokens: {result['token_usage'].get('total_tokens', 'N/A')}")

    # Verify result structure
    assert "final_skill" in result
    assert result["final_skill"] is not None
    assert result["hall_m"] >= 0

    return True


def test_retry_logic():
    """Test pipeline retry logic."""
    print("\n" + "=" * 60)
    print("TEST 9: Retry Logic")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    pipeline = SkillGenerationPipeline(checkpointing=False)

    # Generate with low retry count
    result = pipeline.generate(
        library="json",
        topic="JSON parsing",
        level=1,
        max_retries=0,  # No retries
    )

    print(f"✓ Pipeline with retry limit completed")
    print(f"  Passed: {result['passed']}")
    print(f"  Retries: {result['retry_count']}")

    # Even with no retries, should produce some result
    assert result["final_skill"] is not None

    return True


def test_progressive_levels():
    """Test different progressive disclosure levels."""
    print("\n" + "=" * 60)
    print("TEST 10: Progressive Disclosure Levels")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    pipeline = SkillGenerationPipeline(checkpointing=False)

    # Test Level 1 (basic)
    result_l1 = pipeline.generate(
        library="os",
        topic="file existence check",
        level=1,
        max_retries=0,
    )

    # Test Level 5 (advanced)
    result_l5 = pipeline.generate(
        library="os",
        topic="file existence check",
        level=5,
        max_retries=0,
    )

    print(f"✓ Multi-level generation completed")
    print(f"  L1 tokens: {result_l1['token_usage'].get('total_tokens', 'N/A')}")
    print(f"  L5 tokens: {result_l5['token_usage'].get('total_tokens', 'N/A')}")

    # Both should produce valid skills
    assert result_l1["final_skill"] is not None
    assert result_l5["final_skill"] is not None

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LANGGRAPH PIPELINE TEST SUITE")
    print("=" * 60)
    print(f"Live tests enabled: {LIVE_TEST}")

    tests = [
        test_skill_state,
        test_research_node,
        test_verify_node,
        test_verify_hallucination_detection,
        test_graph_creation,
        test_pipeline_creation,
        test_visualization,
        test_live_pipeline,
        test_retry_logic,
        test_progressive_levels,
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

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
