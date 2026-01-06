#!/usr/bin/env python3
"""Test KuzuDB code knowledge graph."""

import sys
import shutil
import importlib.util

# Load the module directly to avoid __init__.py chain
spec = importlib.util.spec_from_file_location(
    "schema",
    "/home/user/skills_fabric/src/skills_fabric/graph/schema.py"
)
schema_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema_module)

CodeGraph = schema_module.CodeGraph
create_test_graph = schema_module.create_test_graph


def cleanup_db(path):
    """Clean up a KuzuDB database path."""
    import os
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def test_schema_creation():
    """Test creating the schema."""
    print("=" * 60)
    print("TEST 1: Schema Creation")
    print("=" * 60)

    # Clean up any existing test db
    test_db = "./test_kuzu_schema"
    cleanup_db(test_db)

    graph = CodeGraph(test_db)
    graph.initialize_schema()

    print("✓ Schema created successfully")

    # Check we can get stats (empty)
    stats = graph.get_stats()
    print(f"  Initial stats: {stats}")

    assert stats.get("Symbol", 0) == 0, "Should start empty"

    # Clean up
    graph.close()
    cleanup_db(test_db)
    return True


def test_add_nodes():
    """Test adding nodes to the graph."""
    print("\n" + "=" * 60)
    print("TEST 2: Add Nodes")
    print("=" * 60)

    import time
    test_db = "./test_kuzu_nodes"
    cleanup_db(test_db)

    graph = CodeGraph(test_db)
    graph.initialize_schema()

    # Add file
    graph.add_file(
        path="src/example.py",
        language="python",
        size=1000,
        last_modified=int(time.time())
    )
    print("✓ Added file node")

    # Add symbols
    graph.add_symbol(
        id="example:MyClass",
        name="MyClass",
        kind="class",
        file_path="src/example.py",
        line_start=10,
        documentation="A sample class for testing."
    )
    print("✓ Added symbol node (class)")

    graph.add_symbol(
        id="example:my_function",
        name="my_function",
        kind="function",
        file_path="src/example.py",
        line_start=50,
        documentation="A sample function."
    )
    print("✓ Added symbol node (function)")

    # Add concept
    graph.add_concept(
        id="concept:example_overview",
        name="Example Overview",
        description="Level 0 overview of the example module",
        level=0
    )
    print("✓ Added concept node")

    # Add skill
    graph.add_skill(
        id="skill:example_usage",
        name="Example Usage",
        library="example",
        content="# Using Example\n\nThis skill shows...",
        created_at=int(time.time())
    )
    print("✓ Added skill node")

    # Verify
    stats = graph.get_stats()
    print(f"\n  Stats: {stats}")

    assert stats["File"] == 1, f"Expected 1 file, got {stats['File']}"
    assert stats["Symbol"] == 2, f"Expected 2 symbols, got {stats['Symbol']}"
    assert stats["Concept"] == 1, f"Expected 1 concept, got {stats['Concept']}"
    assert stats["Skill"] == 1, f"Expected 1 skill, got {stats['Skill']}"

    # Clean up
    graph.close()
    cleanup_db(test_db)
    return True


def test_relationships():
    """Test creating relationships."""
    print("\n" + "=" * 60)
    print("TEST 3: Relationships")
    print("=" * 60)

    test_db = "./test_kuzu_rels"
    cleanup_db(test_db)

    graph = create_test_graph(test_db)

    # Query skill uses
    result = graph.query_symbols_for_skill("skill:docling_pdf")
    print(f"✓ Queried skill symbols: {len(result)} found")

    if result:
        for r in result:
            print(f"  - {r}")

    assert len(result) > 0, "Expected skill to reference symbols"

    # Check stats
    stats = graph.get_stats()
    print(f"\n  Stats: {stats}")

    # Clean up
    graph.close()
    cleanup_db(test_db)
    return True


def test_complex_queries():
    """Test complex graph queries."""
    print("\n" + "=" * 60)
    print("TEST 4: Complex Queries")
    print("=" * 60)

    import time
    test_db = "./test_kuzu_complex"
    cleanup_db(test_db)

    graph = CodeGraph(test_db)
    graph.initialize_schema()

    # Create a call chain: main -> process -> helper
    graph.add_file("src/main.py", "python", 100, int(time.time()))

    graph.add_symbol("main:main", "main", "function", "src/main.py", 1)
    graph.add_symbol("main:process", "process", "function", "src/main.py", 10)
    graph.add_symbol("main:helper", "helper", "function", "src/main.py", 20)

    graph.link_file_contains_symbol("src/main.py", "main:main")
    graph.link_file_contains_symbol("src/main.py", "main:process")
    graph.link_file_contains_symbol("src/main.py", "main:helper")

    graph.link_symbol_calls("main:main", "main:process", call_site=5)
    graph.link_symbol_calls("main:process", "main:helper", call_site=15)

    print("✓ Created call chain: main -> process -> helper")

    # Query call graph
    result = graph.query_call_graph("main", depth=2)
    print(f"✓ Call graph query returned {len(result)} paths")

    # Clean up
    graph.close()
    cleanup_db(test_db)
    return True


def test_persistence():
    """Test that data persists across connections."""
    print("\n" + "=" * 60)
    print("TEST 5: Persistence")
    print("=" * 60)

    import time
    test_db = "./test_kuzu_persist"
    cleanup_db(test_db)

    # Create and populate
    graph1 = CodeGraph(test_db)
    graph1.initialize_schema()
    graph1.add_symbol("persist:TestClass", "TestClass", "class", "test.py", 1, documentation="Test")
    stats1 = graph1.get_stats()
    print(f"✓ Created graph with {stats1['Symbol']} symbols")
    graph1.close()

    # Reopen and verify
    graph2 = CodeGraph(test_db)
    graph2.initialize_schema()
    stats2 = graph2.get_stats()
    print(f"✓ Reopened graph, found {stats2['Symbol']} symbols")

    assert stats2["Symbol"] == stats1["Symbol"], "Data should persist"
    print("✓ Data persisted correctly")

    # Clean up
    graph2.close()
    cleanup_db(test_db)
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("KUZUDB CODE GRAPH TEST SUITE")
    print("=" * 60)

    tests = [
        test_schema_creation,
        test_add_nodes,
        test_relationships,
        test_complex_queries,
        test_persistence,
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
