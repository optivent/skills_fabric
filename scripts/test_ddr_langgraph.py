#!/usr/bin/env python3
"""Test DDR (Direct Dependency Retriever) on LangGraph CodeWiki.

This script validates that the zero-hallucination pipeline works
by testing DDR retrieval against the LangGraph symbol catalog.

Usage:
    python scripts/test_ddr_langgraph.py
"""
import sys
from pathlib import Path

# Add src to path - import modules directly to avoid kuzu dependency
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import directly from module files to avoid __init__.py dependency issues
import importlib.util

def load_module(name, path):
    """Load a module directly from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load DDR module directly
ddr_module = load_module(
    "ddr",
    src_path / "skills_fabric" / "verify" / "ddr.py"
)
DirectDependencyRetriever = ddr_module.DirectDependencyRetriever
retrieve_validated = ddr_module.retrieve_validated
SourceRef = ddr_module.SourceRef


def test_ddr_loading():
    """Test loading the symbol catalog."""
    print("=" * 60)
    print("TEST 1: Loading LangGraph Symbol Catalog")
    print("=" * 60)

    codewiki_path = Path("/home/user/skills_fabric/crawl_output/langgraph")
    catalog_path = codewiki_path / "symbol_catalog.md"

    if not catalog_path.exists():
        print(f"ERROR: Symbol catalog not found at {catalog_path}")
        return False

    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(catalog_path)

    metrics = ddr.get_hallucination_metrics()
    print(f"Symbols indexed: {metrics['symbols_indexed']}")
    print(f"Unique symbols: {metrics['unique_symbols']}")
    print(f"Target Hall_m: {metrics['target_hall_m']}")

    return metrics['unique_symbols'] > 0


def test_ddr_retrieval():
    """Test retrieving symbols."""
    print("\n" + "=" * 60)
    print("TEST 2: Retrieving LangGraph Symbols")
    print("=" * 60)

    codewiki_path = Path("/home/user/skills_fabric/crawl_output/langgraph")

    test_queries = [
        "StateGraph",
        "add_node",
        "add_edge",
        "Checkpoint",
        "compile",
        "MessageGraph",
    ]

    results = []
    for query in test_queries:
        result = retrieve_validated(query, codewiki_path, max_results=5)
        print(f"\nQuery: '{query}'")
        print(f"  Validated: {result.validated_count}")
        print(f"  Rejected: {result.rejected_count}")
        print(f"  Hall_m: {result.hallucination_rate:.4f}")

        for element in result.elements[:3]:
            ref = element.source_ref
            print(f"    - {ref.symbol_name} ({ref.symbol_type}) at {ref.citation}")

        results.append(result)

    # Check overall success
    total_validated = sum(r.validated_count for r in results)
    total_rejected = sum(r.rejected_count for r in results)

    print(f"\n--- Summary ---")
    print(f"Total validated: {total_validated}")
    print(f"Total rejected: {total_rejected}")

    return total_validated > 0


def test_auditor():
    """Test the auditor claim extraction (without full agent)."""
    print("\n" + "=" * 60)
    print("TEST 3: Claim Extraction (Auditor Logic)")
    print("=" * 60)

    import re

    codewiki_path = Path("/home/user/skills_fabric/crawl_output/langgraph")

    # Sample content with LangGraph references
    test_content = """
    The `StateGraph` class is the main entry point for building graphs.
    You can use `add_node()` to add nodes and `add_edge()` to connect them.
    The `Checkpoint` interface enables persistence.
    Call `compile()` to create the runnable graph.

    There is also a `FakeSymbol` that doesn't exist.
    """

    # Extract claims (simplified from auditor)
    claims = []

    # Pattern 1: Inline code references like `SymbolName`
    code_refs = re.findall(r'`([A-Z][a-zA-Z0-9_]+)`', test_content)
    claims.extend(code_refs)

    # Pattern 2: Function calls like `func_name()`
    func_refs = re.findall(r'`([a-z_][a-zA-Z0-9_]*)\(\)`', test_content)
    claims.extend(func_refs)

    print(f"Extracted claims: {claims}")

    # Verify against DDR
    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(codewiki_path / "symbol_catalog.md")

    verified = 0
    unverified = 0

    for claim in claims:
        result = ddr.retrieve(claim, max_results=1)
        if result.validated_count > 0:
            print(f"  {claim}: VERIFIED")
            verified += 1
        else:
            print(f"  {claim}: UNVERIFIED")
            unverified += 1

    total = verified + unverified
    hall_rate = unverified / total if total > 0 else 0.0

    print(f"\nVerified: {verified}/{total}")
    print(f"Hall_m rate: {hall_rate:.4f}")
    print(f"Meets target (<0.02): {'YES' if hall_rate < 0.02 else 'NO'}")

    return verified > 0


def test_citations():
    """Test the citation system (inline implementation)."""
    print("\n" + "=" * 60)
    print("TEST 4: Citation System")
    print("=" * 60)

    import re
    from dataclasses import dataclass

    # Simple inline citation system for testing
    @dataclass
    class CitationResult:
        original_content: str
        cited_content: str
        citations_added: int
        uncited_symbols: list

    def add_citations(content, refs):
        """Simple citation adder."""
        cited_content = content
        citations_added = 0
        uncited = []

        # Build index of refs
        ref_index = {r.symbol_name.lower(): r for r in refs}

        # Find code references
        pattern = r'`([A-Za-z_][A-Za-z0-9_]*)`'
        matches = list(re.finditer(pattern, content))

        for match in reversed(matches):
            symbol = match.group(1)
            ref = ref_index.get(symbol.lower())

            if ref:
                citation = f"[`{symbol}`]({ref.file_path}#L{ref.line_number})"
                start, end = match.span()
                cited_content = cited_content[:start] + citation + cited_content[end:]
                citations_added += 1
            else:
                if symbol not in uncited:
                    uncited.append(symbol)

        return CitationResult(content, cited_content, citations_added, uncited)

    # Register some refs
    refs = [
        SourceRef(
            symbol_name="StateGraph",
            file_path="langgraph/graph/state.py",
            line_number=50,
        ),
        SourceRef(
            symbol_name="add_node",
            file_path="langgraph/graph/graph.py",
            line_number=100,
        ),
    ]

    content = """
    Use `StateGraph` to create your graph.
    Then call `add_node` to add processing nodes.
    """

    result = add_citations(content, refs)

    print(f"Original content:")
    print(content)
    print(f"\nCited content:")
    print(result.cited_content)
    print(f"\nCitations added: {result.citations_added}")
    print(f"Uncited symbols: {result.uncited_symbols}")

    return result.citations_added > 0


def main():
    """Run all tests."""
    print("=" * 60)
    print("SKILLS FABRIC - ZERO-HALLUCINATION PIPELINE TESTS")
    print("Target Library: LangGraph")
    print("=" * 60)

    tests = [
        ("DDR Loading", test_ddr_loading),
        ("DDR Retrieval", test_ddr_retrieval),
        ("Auditor Agent", test_auditor),
        ("Citation System", test_citations),
    ]

    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed))
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
