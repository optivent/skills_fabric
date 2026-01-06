#!/usr/bin/env python3
"""
Test Unified API Integration

Demonstrates and validates:
- Service initialization
- Memory-aware conversations
- Code embedding and search
- Safe code execution
- Deep research

Usage:
    python scripts/test_unified_api.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skills_fabric.integrations import (
    UnifiedAPI,
    APIConfig,
    OPTIMAL_STACK,
    CONFIGURATIONS,
    get_install_commands,
)


async def test_initialization():
    """Test API initialization and status."""
    print("=" * 70)
    print("TEST: Service Initialization")
    print("=" * 70)

    api = UnifiedAPI()
    status = await api.initialize()

    api.print_status()

    connected = sum(1 for v in status.values() if v)
    print(f"\n✓ Initialization complete: {connected}/{len(status)} services")

    return api, status


async def test_chat(api: UnifiedAPI):
    """Test tiered chat capability."""
    print("\n" + "=" * 70)
    print("TEST: Tiered Chat (Claude Hierarchy)")
    print("=" * 70)

    if not api.status.get("anthropic"):
        print("⚠ Anthropic not configured - skipping chat test")
        return

    # Test auto tier selection
    tasks = [
        ("Design a state machine for order processing", "should route to opus"),
        ("Search for all usages of compile()", "should route to sonnet"),
        ("Add a type hint to this function", "should route to haiku"),
    ]

    for task, expected in tasks:
        tier = api._select_tier(task)
        print(f"\n  Task: {task[:50]}...")
        print(f"  → Selected: {tier.upper()} ({expected})")

    # Actual chat test
    print("\n  Testing actual chat with Haiku...")
    response = await api.chat(
        "What is one key benefit of using state machines in applications?",
        tier="haiku"
    )
    print(f"  Response: {response[:200]}...")


async def test_memory(api: UnifiedAPI):
    """Test memory operations."""
    print("\n" + "=" * 70)
    print("TEST: Memory Layer (Mem0)")
    print("=" * 70)

    if not api.status.get("mem0"):
        print("⚠ Mem0 not configured - skipping memory test")
        return

    user_id = "test_user_001"

    # Add memory
    mem_id = await api.add_memory(
        content="User prefers Python over JavaScript for backend development",
        user_id=user_id
    )
    print(f"  Added memory: {mem_id}")

    # Recall
    memories = await api.recall_memories("backend development preferences", user_id)
    print(f"  Recalled {len(memories)} memories")

    for mem in memories[:3]:
        print(f"    - {mem.content[:50]}...")


async def test_embeddings(api: UnifiedAPI):
    """Test code embedding."""
    print("\n" + "=" * 70)
    print("TEST: Code Embeddings (Voyage AI)")
    print("=" * 70)

    if not api.status.get("voyage"):
        print("⚠ Voyage not configured - skipping embedding test")
        return

    code_samples = [
        "def create_graph():\n    return StateGraph(State)",
        "class MyAgent(Agent):\n    def run(self): pass",
        "from langgraph.graph import StateGraph",
    ]

    embeddings = await api.embed_code(code_samples)

    print(f"  Embedded {len(code_samples)} code samples")
    for i, emb in enumerate(embeddings):
        print(f"    Sample {i+1}: vector dim={len(emb)}, first 3 values={emb[:3]}")


async def test_code_execution(api: UnifiedAPI):
    """Test safe code execution."""
    print("\n" + "=" * 70)
    print("TEST: Code Execution (E2B)")
    print("=" * 70)

    if not api.status.get("e2b"):
        print("⚠ E2B not configured - skipping execution test")
        return

    # Simple test
    result = await api.execute_code("""
import sys
print(f"Python version: {sys.version}")
result = sum(range(100))
print(f"Sum of 0-99: {result}")
result
""")

    print(f"  Success: {result.success}")
    print(f"  Stdout: {result.stdout}")
    print(f"  Time: {result.execution_time_ms}ms")

    if result.stderr:
        print(f"  Stderr: {result.stderr}")


async def test_research(api: UnifiedAPI):
    """Test research capability."""
    print("\n" + "=" * 70)
    print("TEST: Research (Perplexity)")
    print("=" * 70)

    if not api.status.get("perplexity"):
        print("⚠ Perplexity not configured - skipping research test")
        return

    answer = await api.research(
        "What is LangGraph and how does it differ from LangChain?",
        mode="fast"
    )

    print(f"  Research answer: {answer[:300]}...")


def show_configuration_options():
    """Show available configurations."""
    print("\n" + "=" * 70)
    print("AVAILABLE CONFIGURATIONS")
    print("=" * 70)

    for name, config in CONFIGURATIONS.items():
        print(f"\n  {name.upper()}:")
        print(f"    Description: {config['description']}")
        print(f"    Tools: {', '.join(config['tools'])}")
        print(f"    Cost estimate: {config['cost_estimate']}")

    print("\n" + "-" * 70)
    print("RECOMMENDED INSTALL COMMANDS")
    print("-" * 70)

    for cmd in get_install_commands("recommended"):
        print(f"  {cmd}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("UNIFIED API TEST SUITE")
    print("Skills Fabric Integration Layer")
    print("=" * 70)

    # Show configurations
    show_configuration_options()

    # Initialize and test
    api, status = await test_initialization()

    # Run tests based on available services
    await test_chat(api)
    await test_memory(api)
    await test_embeddings(api)
    await test_code_execution(api)
    await test_research(api)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    connected = sum(1 for v in status.values() if v)
    print(f"\nServices connected: {connected}/{len(status)}")

    if connected < len(status):
        print("\nTo enable more services, set these environment variables:")
        missing = [
            ("ANTHROPIC_API_KEY", "anthropic"),
            ("MEM0_API_KEY", "mem0"),
            ("VOYAGE_API_KEY", "voyage"),
            ("QDRANT_API_KEY", "qdrant (optional - can use local)"),
            ("JINA_API_KEY", "jina"),
            ("PERPLEXITY_API_KEY", "perplexity"),
            ("E2B_API_KEY", "e2b"),
            ("LANGCHAIN_API_KEY", "langsmith"),
        ]

        for env_var, service in missing:
            if not status.get(service.split()[0], False):
                print(f"  export {env_var}=your-key-here")

    print("\n✓ Tests complete")


if __name__ == "__main__":
    asyncio.run(main())
