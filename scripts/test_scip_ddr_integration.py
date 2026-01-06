#!/usr/bin/env python3
"""Test SCIP-DDR Integration."""

import sys
import importlib.util

# Load the SCIP adapter module
spec = importlib.util.spec_from_file_location(
    "scip_adapter",
    "/home/user/skills_fabric/src/skills_fabric/verify/scip_adapter.py"
)
scip_adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scip_adapter)

SCIPIndex = scip_adapter.SCIPIndex
SCIPDDRAdapter = scip_adapter.SCIPDDRAdapter
SCIP_AVAILABLE = scip_adapter.SCIP_AVAILABLE

SCIP_INDEX_PATH = "/home/user/skills_fabric/test_index.scip"


def test_scip_availability():
    """Test SCIP is available."""
    print("=" * 60)
    print("TEST 1: SCIP Availability")
    print("=" * 60)

    print(f"✓ SCIP available: {SCIP_AVAILABLE}")
    assert SCIP_AVAILABLE, "SCIP protobuf not available"

    return True


def test_load_scip_index():
    """Test loading SCIP index."""
    print("\n" + "=" * 60)
    print("TEST 2: Load SCIP Index")
    print("=" * 60)

    import os
    if not os.path.exists(SCIP_INDEX_PATH):
        print(f"⚠ SCIP index not found at {SCIP_INDEX_PATH}")
        print("  Skipping test (run scip-python index first)")
        return True

    index = SCIPIndex(SCIP_INDEX_PATH)
    index.load()

    meta = index.metadata
    print(f"✓ Loaded SCIP index")
    print(f"  Project root: {meta['project_root']}")
    print(f"  Tool: {meta['tool_name']} v{meta['tool_version']}")
    print(f"  Documents: {meta['total_documents']}")
    print(f"  Symbols: {meta['total_symbols']}")

    assert meta['total_symbols'] > 0, "Should have symbols"

    return True


def test_search_symbols():
    """Test symbol search."""
    print("\n" + "=" * 60)
    print("TEST 3: Search Symbols")
    print("=" * 60)

    import os
    if not os.path.exists(SCIP_INDEX_PATH):
        print("⚠ Skipping (no index)")
        return True

    index = SCIPIndex(SCIP_INDEX_PATH)

    # Search for our DDR class
    results = index.search("DirectDependencyRetriever", max_results=5)

    print(f"✓ Search for 'DirectDependencyRetriever': {len(results)} results")

    for sym in results[:3]:
        print(f"\n  Symbol: {sym.name}")
        print(f"  Kind: {sym.kind_name}")
        print(f"  File: {sym.file_path}")
        print(f"  Line: {sym.line_number}")
        if sym.documentation:
            doc_preview = sym.documentation[:80].replace('\n', ' ')
            print(f"  Doc: {doc_preview}...")

    assert len(results) > 0, "Should find DDR"

    return True


def test_scip_ddr_adapter():
    """Test SCIPDDRAdapter."""
    print("\n" + "=" * 60)
    print("TEST 4: SCIP-DDR Adapter")
    print("=" * 60)

    import os
    if not os.path.exists(SCIP_INDEX_PATH):
        print("⚠ Skipping (no index)")
        return True

    index = SCIPIndex(SCIP_INDEX_PATH)
    adapter = SCIPDDRAdapter(index)

    # Test verify_symbol
    exists, sym = adapter.verify_symbol("DirectDependencyRetriever")
    print(f"✓ verify_symbol('DirectDependencyRetriever'): {exists}")
    if sym:
        print(f"  Found: {sym.name} at {sym.file_path}:{sym.line_number}")

    # Test get_citation
    citation = adapter.get_citation("DirectDependencyRetriever")
    print(f"\n✓ get_citation: {citation}")

    # Test get_documentation
    doc = adapter.get_documentation("DirectDependencyRetriever")
    if doc:
        doc_preview = doc[:100].replace('\n', ' ')
        print(f"\n✓ get_documentation: {doc_preview}...")

    # Test verify non-existent symbol
    exists_fake, _ = adapter.verify_symbol("NonExistentFakeClass")
    print(f"\n✓ verify_symbol('NonExistentFakeClass'): {exists_fake}")
    assert not exists_fake, "Fake class should not exist"

    return True


def test_to_ddr_format():
    """Test converting to DDR format."""
    print("\n" + "=" * 60)
    print("TEST 5: Convert to DDR Format")
    print("=" * 60)

    import os
    if not os.path.exists(SCIP_INDEX_PATH):
        print("⚠ Skipping (no index)")
        return True

    index = SCIPIndex(SCIP_INDEX_PATH)
    ddr_format = index.to_ddr_format()

    print(f"✓ Converted to DDR format: {len(ddr_format)} symbols")

    # Show sample entries
    sample_keys = list(ddr_format.keys())[:5]
    print(f"\n  Sample symbols:")
    for key in sample_keys:
        info = ddr_format[key]
        print(f"    - {key}: {info['file_path']}:{info['line_num']}")

    return True


def test_integrated_verification():
    """Test integrated verification workflow."""
    print("\n" + "=" * 60)
    print("TEST 6: Integrated Verification Workflow")
    print("=" * 60)

    import os
    if not os.path.exists(SCIP_INDEX_PATH):
        print("⚠ Skipping (no index)")
        return True

    index = SCIPIndex(SCIP_INDEX_PATH)
    adapter = SCIPDDRAdapter(index)

    # Simulate verifying claims from generated content
    claims = [
        "DirectDependencyRetriever",
        "SourceRef",
        "DDRResult",
        "FakeHallucinatedClass",
        "retrieve",
    ]

    verified = 0
    unverified = 0

    print("Verifying claims:")
    for claim in claims:
        exists, sym = adapter.verify_symbol(claim)
        status = "✓" if exists else "✗"
        print(f"  {status} {claim}: {'VERIFIED' if exists else 'NOT FOUND'}")

        if exists:
            verified += 1
        else:
            unverified += 1

    hall_m = unverified / len(claims) if claims else 0

    print(f"\n  Results:")
    print(f"    Verified: {verified}/{len(claims)}")
    print(f"    Hall_m: {hall_m:.2f}")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SCIP-DDR INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_scip_availability,
        test_load_scip_index,
        test_search_symbols,
        test_scip_ddr_adapter,
        test_to_ddr_format,
        test_integrated_verification,
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
