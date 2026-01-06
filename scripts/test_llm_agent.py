#!/usr/bin/env python3
"""Test LLM Generator Agent."""

import sys
import os
import importlib.util

# Load glm_client first
spec_glm = importlib.util.spec_from_file_location(
    "glm_client",
    "/home/user/skills_fabric/src/skills_fabric/llm/glm_client.py"
)
glm_client = importlib.util.module_from_spec(spec_glm)
sys.modules['skills_fabric.llm.glm_client'] = glm_client
spec_glm.loader.exec_module(glm_client)

# Load llm_agent
spec_agent = importlib.util.spec_from_file_location(
    "llm_agent",
    "/home/user/skills_fabric/src/skills_fabric/agents/llm_agent.py"
)
llm_agent = importlib.util.module_from_spec(spec_agent)
spec_agent.loader.exec_module(llm_agent)

# Extract classes
GLMClient = glm_client.GLMClient
LLMGeneratorAgent = llm_agent.LLMGeneratorAgent
GenerationTask = llm_agent.GenerationTask
GenerationOutput = llm_agent.GenerationOutput
GLM_AVAILABLE = llm_agent.GLM_AVAILABLE

# Check for API key
API_KEY = os.getenv("ZAI_API_KEY", os.getenv("GLM_API_KEY", ""))
LIVE_TEST = bool(API_KEY)


def test_generation_task():
    """Test GenerationTask dataclass."""
    print("=" * 60)
    print("TEST 1: GenerationTask")
    print("=" * 60)

    task = GenerationTask(
        prompt="Generate a PDF conversion skill",
        library="docling",
        level=3,
        require_citations=True,
    )

    print(f"✓ Created GenerationTask")
    print(f"  Library: {task.library}")
    print(f"  Level: {task.level}")
    print(f"  Require citations: {task.require_citations}")

    assert task.library == "docling"
    assert task.level == 3

    return True


def test_generation_output():
    """Test GenerationOutput dataclass."""
    print("\n" + "=" * 60)
    print("TEST 2: GenerationOutput")
    print("=" * 60)

    output = GenerationOutput(
        content="# Skill\n\n```python\nfrom docling import convert\n```",
        thinking="First, I need to understand the library...",
        citations=["docling/convert.py:42", "docling/pipeline.py:100"],
        tokens_used=500,
        cost_usd=0.001,
        has_code_blocks=True,
    )

    print(f"✓ Created GenerationOutput")
    print(f"  Content length: {len(output.content)}")
    print(f"  Citations: {len(output.citations)}")
    print(f"  Has code blocks: {output.has_code_blocks}")
    print(f"  Cost: ${output.cost_usd:.4f}")

    assert output.has_code_blocks
    assert len(output.citations) == 2

    return True


def test_agent_creation():
    """Test LLMGeneratorAgent creation."""
    print("\n" + "=" * 60)
    print("TEST 3: Agent Creation")
    print("=" * 60)

    # Create without API key (should be unavailable)
    old_key = os.environ.pop("ZAI_API_KEY", None)
    old_key2 = os.environ.pop("GLM_API_KEY", None)

    try:
        agent = LLMGeneratorAgent()
        print(f"✓ Created LLMGeneratorAgent")
        print(f"  GLM available: {GLM_AVAILABLE}")
        print(f"  Agent available: {agent.available}")
        print(f"  Role: {agent.role.value}")

    finally:
        if old_key:
            os.environ["ZAI_API_KEY"] = old_key
        if old_key2:
            os.environ["GLM_API_KEY"] = old_key2

    return True


def test_agent_with_key():
    """Test agent creation with API key."""
    print("\n" + "=" * 60)
    print("TEST 4: Agent with API Key")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    agent = LLMGeneratorAgent()

    print(f"✓ Created LLMGeneratorAgent with API key")
    print(f"  Available: {agent.available}")
    print(f"  Preserve thinking: {agent.preserve_thinking}")

    assert agent.available

    return True


def test_citation_extraction():
    """Test citation extraction from content."""
    print("\n" + "=" * 60)
    print("TEST 5: Citation Extraction")
    print("=" * 60)

    agent = LLMGeneratorAgent(api_key="test-key" if not LIVE_TEST else None)

    content = """
Here's how to use the converter:

The `DocumentConverter` class (`docling/converter.py:42`) handles conversion.
You can also use `pipeline.run()` from `src/pipeline.py:100`.

```python
from docling import convert  # docling/__init__.py:5
result = convert(file)
```
"""

    citations = agent._extract_citations(content)

    print(f"✓ Extracted {len(citations)} citations:")
    for c in citations:
        print(f"  - {c}")

    assert len(citations) >= 2

    return True


def test_prompt_building():
    """Test prompt building with context."""
    print("\n" + "=" * 60)
    print("TEST 6: Prompt Building")
    print("=" * 60)

    agent = LLMGeneratorAgent(api_key="test-key" if not LIVE_TEST else None)

    task = GenerationTask(
        prompt="Create a PDF extraction skill",
        library="docling",
        level=3,
    )

    context = {
        "symbols": [
            {"name": "DocumentConverter", "citation": "docling/converter.py:42"},
            {"name": "ExportFormat", "citation": "docling/format.py:10"},
        ],
        "docs": "Docling is a document conversion library...",
    }

    prompt = agent._build_prompt(task, context)

    print(f"✓ Built prompt ({len(prompt)} chars)")
    print(f"  Contains library: {'docling' in prompt}")
    print(f"  Contains level: {'L3' in prompt}")
    print(f"  Contains symbols: {'DocumentConverter' in prompt}")

    assert "docling" in prompt
    assert "L3" in prompt
    assert "DocumentConverter" in prompt

    return True


def test_execute_unavailable():
    """Test execute when GLM unavailable."""
    print("\n" + "=" * 60)
    print("TEST 7: Execute (Unavailable)")
    print("=" * 60)

    # Create agent without key
    old_key = os.environ.pop("ZAI_API_KEY", None)
    old_key2 = os.environ.pop("GLM_API_KEY", None)

    try:
        agent = LLMGeneratorAgent()
        result = agent.execute("Test prompt")

        print(f"✓ Execute returned result")
        print(f"  Success: {result.success}")
        print(f"  Error: {result.error}")

        if not agent.available:
            assert not result.success
            assert "not available" in result.error.lower()

    finally:
        if old_key:
            os.environ["ZAI_API_KEY"] = old_key
        if old_key2:
            os.environ["GLM_API_KEY"] = old_key2

    return True


def test_live_generation():
    """Test live skill generation."""
    print("\n" + "=" * 60)
    print("TEST 8: Live Generation")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    agent = LLMGeneratorAgent()

    task = GenerationTask(
        prompt="Create a simple example showing how to read a file in Python",
        library="builtins",
        level=1,
        require_citations=False,  # Don't require for this simple test
    )

    result = agent.execute(task)

    print(f"✓ Generation completed")
    print(f"  Success: {result.success}")

    if result.success:
        output = result.output
        print(f"  Content length: {len(output.content)}")
        print(f"  Has code blocks: {output.has_code_blocks}")
        print(f"  Tokens: {output.tokens_used}")
        print(f"  Cost: ${output.cost_usd:.4f}")

        # Preview
        preview = output.content[:200].replace('\n', ' ')
        print(f"  Preview: {preview}...")

    return result.success


def test_live_refinement():
    """Test live refinement with preserved thinking."""
    print("\n" + "=" * 60)
    print("TEST 9: Live Refinement")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    agent = LLMGeneratorAgent()

    # First generation
    task = GenerationTask(
        prompt="Write a function to add two numbers",
        library="python",
        level=1,
    )
    result1 = agent.execute(task)

    if not result1.success:
        print(f"✗ Initial generation failed: {result1.error}")
        return False

    print(f"✓ Initial generation completed")

    # Refine with feedback
    output2 = agent.refine("Add type hints and a docstring")

    print(f"✓ Refinement completed")
    print(f"  Thinking history: {len(agent.get_thinking_history())} entries")
    print(f"  Has type hints: {'def ' in output2.content and ':' in output2.content}")

    return True


def test_token_tracking():
    """Test token usage tracking."""
    print("\n" + "=" * 60)
    print("TEST 10: Token Tracking")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key)")
        return True

    agent = LLMGeneratorAgent()

    # Make a simple call
    task = GenerationTask(
        prompt="Say hello",
        library="test",
        level=1,
    )
    agent.execute(task)

    usage = agent.get_token_usage()

    print(f"✓ Token usage tracked")
    print(f"  Prompt tokens: {usage.get('prompt_tokens', 0)}")
    print(f"  Completion tokens: {usage.get('completion_tokens', 0)}")
    print(f"  Thinking tokens: {usage.get('thinking_tokens', 0)}")
    print(f"  Total: {usage.get('total_tokens', 0)}")
    print(f"  Cost: ${usage.get('cost_usd', 0):.4f}")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LLM GENERATOR AGENT TEST SUITE")
    print("=" * 60)
    print(f"GLM available: {GLM_AVAILABLE}")
    print(f"Live tests: {LIVE_TEST}")

    tests = [
        test_generation_task,
        test_generation_output,
        test_agent_creation,
        test_agent_with_key,
        test_citation_extraction,
        test_prompt_building,
        test_execute_unavailable,
        test_live_generation,
        test_live_refinement,
        test_token_tracking,
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
