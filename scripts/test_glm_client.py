#!/usr/bin/env python3
"""Test GLM-4.7 Client."""

import sys
import os
import importlib.util

# Load GLM client module
spec = importlib.util.spec_from_file_location(
    "glm_client",
    "/home/user/skills_fabric/src/skills_fabric/llm/glm_client.py"
)
glm_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(glm_client)

GLMClient = glm_client.GLMClient
GLMConfig = glm_client.GLMConfig
GLMResponse = glm_client.GLMResponse
GLMCodingAgent = glm_client.GLMCodingAgent
GLMOpenAIWrapper = glm_client.GLMOpenAIWrapper
ThinkingMode = glm_client.ThinkingMode
TokenUsage = glm_client.TokenUsage

# Check if API key is available for live tests
API_KEY = os.getenv("ZAI_API_KEY", os.getenv("GLM_API_KEY", ""))
LIVE_TEST = bool(API_KEY)


def test_token_usage():
    """Test TokenUsage dataclass."""
    print("=" * 60)
    print("TEST 1: TokenUsage")
    print("=" * 60)

    usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=500,
        thinking_tokens=200,
        total_tokens=1700,
    )

    print(f"✓ Created TokenUsage")
    print(f"  Prompt: {usage.prompt_tokens}")
    print(f"  Completion: {usage.completion_tokens}")
    print(f"  Thinking: {usage.thinking_tokens}")
    print(f"  Cost: ${usage.cost_usd:.4f}")

    # Verify cost calculation
    expected_cost = (1000 / 1_000_000) * 0.60 + (700 / 1_000_000) * 2.20
    assert abs(usage.cost_usd - expected_cost) < 0.0001

    return True


def test_glm_config():
    """Test GLMConfig dataclass."""
    print("\n" + "=" * 60)
    print("TEST 2: GLMConfig")
    print("=" * 60)

    config = GLMConfig(
        api_key="test-key",
        model="glm-4.7",
        max_tokens=4096,
        thinking_mode=ThinkingMode.PRESERVED,
    )

    print(f"✓ Created GLMConfig")
    print(f"  Model: {config.model}")
    print(f"  Max tokens: {config.max_tokens}")
    print(f"  Thinking: {config.thinking_mode.value}")
    print(f"  Base URL: {config.base_url}")

    assert config.model == "glm-4.7"
    assert config.thinking_mode == ThinkingMode.PRESERVED

    return True


def test_glm_response():
    """Test GLMResponse dataclass."""
    print("\n" + "=" * 60)
    print("TEST 3: GLMResponse")
    print("=" * 60)

    response = GLMResponse(
        content="def hello(): return 'world'",
        thinking="First, I need to create a simple function...",
        usage=TokenUsage(prompt_tokens=50, completion_tokens=20),
        latency_ms=150.5,
    )

    print(f"✓ Created GLMResponse")
    print(f"  Has thinking: {response.has_thinking}")
    print(f"  Content length: {len(response.content)}")
    print(f"  Latency: {response.latency_ms:.1f}ms")

    assert response.has_thinking
    assert response.content == "def hello(): return 'world'"

    return True


def test_client_creation_no_key():
    """Test client creation without API key."""
    print("\n" + "=" * 60)
    print("TEST 4: Client Creation (no key)")
    print("=" * 60)

    # Clear env vars temporarily
    old_key = os.environ.pop("ZAI_API_KEY", None)
    old_key2 = os.environ.pop("GLM_API_KEY", None)

    try:
        try:
            client = GLMClient()
            print("✗ Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")

    finally:
        if old_key:
            os.environ["ZAI_API_KEY"] = old_key
        if old_key2:
            os.environ["GLM_API_KEY"] = old_key2

    return True


def test_client_creation_with_key():
    """Test client creation with API key."""
    print("\n" + "=" * 60)
    print("TEST 5: Client Creation (with key)")
    print("=" * 60)

    client = GLMClient(api_key="test-key-12345")

    print(f"✓ Created GLMClient")
    print(f"  Endpoint: {client.endpoint}")
    print(f"  Headers: Authorization present: {'Authorization' in client.headers}")

    assert "Bearer" in client.headers["Authorization"]

    return True


def test_coding_agent_creation():
    """Test GLMCodingAgent creation."""
    print("\n" + "=" * 60)
    print("TEST 6: GLMCodingAgent Creation")
    print("=" * 60)

    client = GLMClient(api_key="test-key")
    agent = GLMCodingAgent(client=client)

    print(f"✓ Created GLMCodingAgent")
    print(f"  Messages: {len(agent.messages)}")
    print(f"  System prompt length: {len(agent.system_prompt)}")

    # Check system message is present
    assert len(agent.messages) == 1
    assert agent.messages[0]["role"] == "system"

    return True


def test_openai_wrapper():
    """Test OpenAI-compatible wrapper."""
    print("\n" + "=" * 60)
    print("TEST 7: OpenAI Wrapper")
    print("=" * 60)

    wrapper = GLMOpenAIWrapper(api_key="test-key")

    print(f"✓ Created GLMOpenAIWrapper")
    print(f"  Has chat attribute: {hasattr(wrapper, 'chat')}")
    print(f"  Has create method: {hasattr(wrapper.chat, 'create')}")

    assert hasattr(wrapper, 'chat')
    assert hasattr(wrapper.chat, 'create')

    return True


def test_thinking_modes():
    """Test thinking mode enum."""
    print("\n" + "=" * 60)
    print("TEST 8: Thinking Modes")
    print("=" * 60)

    modes = list(ThinkingMode)

    print(f"✓ ThinkingMode enum has {len(modes)} modes:")
    for mode in modes:
        print(f"  - {mode.name}: {mode.value}")

    assert ThinkingMode.DISABLED.value == "disabled"
    assert ThinkingMode.ENABLED.value == "enabled"
    assert ThinkingMode.PRESERVED.value == "preserved"

    return True


def test_live_api_call():
    """Test live API call (only if API key available)."""
    print("\n" + "=" * 60)
    print("TEST 9: Live API Call")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key set)")
        print("  Set ZAI_API_KEY or GLM_API_KEY to enable")
        return True

    client = GLMClient()

    response = client.chat(
        user_message="What is 2 + 2? Reply with just the number.",
        thinking=True,
    )

    print(f"✓ API call successful")
    print(f"  Content: {response.content[:100]}")
    print(f"  Has thinking: {response.has_thinking}")
    print(f"  Latency: {response.latency_ms:.1f}ms")
    print(f"  Tokens: {response.usage.total_tokens}")
    print(f"  Cost: ${response.usage.cost_usd:.6f}")

    return True


def test_live_code_generation():
    """Test live code generation (only if API key available)."""
    print("\n" + "=" * 60)
    print("TEST 10: Live Code Generation")
    print("=" * 60)

    if not LIVE_TEST:
        print("⚠ Skipping (no API key set)")
        return True

    client = GLMClient()

    response = client.code_generation(
        prompt="Write a Python function to check if a number is prime",
        language="python",
    )

    print(f"✓ Code generation successful")
    print(f"  Content preview: {response.content[:200]}...")
    print(f"  Has thinking: {response.has_thinking}")
    if response.thinking:
        print(f"  Thinking preview: {response.thinking[:100]}...")

    assert "def" in response.content or "prime" in response.content.lower()

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GLM-4.7 CLIENT TEST SUITE")
    print("=" * 60)
    print(f"Live tests enabled: {LIVE_TEST}")

    tests = [
        test_token_usage,
        test_glm_config,
        test_glm_response,
        test_client_creation_no_key,
        test_client_creation_with_key,
        test_coding_agent_creation,
        test_openai_wrapper,
        test_thinking_modes,
        test_live_api_call,
        test_live_code_generation,
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
