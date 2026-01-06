#!/usr/bin/env python3
"""Test SCIP index reading and symbol extraction."""

import sys
sys.path.insert(0, '/home/user/skills_fabric')

import scip_pb2


def test_read_scip_index():
    """Test reading the SCIP index we generated."""
    print("=" * 60)
    print("TEST: Reading SCIP Index")
    print("=" * 60)

    # Read the index
    with open('/home/user/skills_fabric/test_index.scip', 'rb') as f:
        index = scip_pb2.Index()
        index.ParseFromString(f.read())

    print(f"✓ Successfully loaded SCIP index")

    # Check metadata
    print(f"\nMetadata:")
    print(f"  Project root: {index.metadata.project_root}")
    print(f"  Tool: {index.metadata.tool_info.name} v{index.metadata.tool_info.version}")

    # Count documents and symbols
    total_docs = len(index.documents)
    total_symbols = 0
    classes = []
    functions = []
    methods = []

    # Find our DDR file
    ddr_doc = None

    for doc in index.documents:
        for sym in doc.symbols:
            total_symbols += 1

            # Categorize symbols
            symbol_name = sym.symbol
            if '.class.' in symbol_name.lower() or '#class' in symbol_name:
                classes.append(symbol_name)
            elif '.method.' in symbol_name.lower() or '#method' in symbol_name:
                methods.append(symbol_name)
            elif '.function.' in symbol_name.lower() or '#function' in symbol_name:
                functions.append(symbol_name)

        if 'verify/ddr.py' in doc.relative_path:
            ddr_doc = doc

    print(f"\nIndex Statistics:")
    print(f"  Total documents: {total_docs}")
    print(f"  Total symbols: {total_symbols}")
    print(f"  Classes found: {len(classes)}")
    print(f"  Methods found: {len(methods)}")
    print(f"  Functions found: {len(functions)}")

    # Check DDR file specifically
    if ddr_doc:
        print(f"\n✓ Found DDR document: {ddr_doc.relative_path}")
        print(f"  Symbols in DDR: {len(ddr_doc.symbols)}")
        print(f"  Occurrences in DDR: {len(ddr_doc.occurrences)}")

        # Print first few symbols
        print(f"\n  First 5 symbols in DDR:")
        for sym in ddr_doc.symbols[:5]:
            print(f"    - {sym.symbol}")
            if sym.documentation:
                # Clean up documentation
                doc_preview = sym.documentation[0][:80] if sym.documentation else ""
                print(f"      Doc: {doc_preview}...")
    else:
        print(f"\n⚠ DDR document not found in index")

    return True


def test_symbol_search():
    """Test searching for specific symbols."""
    print("\n" + "=" * 60)
    print("TEST: Symbol Search")
    print("=" * 60)

    with open('/home/user/skills_fabric/test_index.scip', 'rb') as f:
        index = scip_pb2.Index()
        index.ParseFromString(f.read())

    # Search for DirectDependencyRetriever
    target = 'DirectDependencyRetriever'
    found = []

    for doc in index.documents:
        for sym in doc.symbols:
            if target.lower() in sym.symbol.lower():
                found.append({
                    'symbol': sym.symbol,
                    'file': doc.relative_path,
                    'kind': sym.kind,
                    'documentation': sym.documentation[0][:100] if sym.documentation else None
                })

    print(f"✓ Search for '{target}':")
    print(f"  Found {len(found)} matches")

    for match in found[:3]:
        print(f"\n  Symbol: {match['symbol']}")
        print(f"  File: {match['file']}")
        if match['documentation']:
            print(f"  Doc: {match['documentation']}...")

    # Search for SourceRef
    target2 = 'SourceRef'
    found2 = []

    for doc in index.documents:
        for sym in doc.symbols:
            if target2 in sym.symbol:
                found2.append(sym.symbol)

    print(f"\n✓ Search for '{target2}': {len(found2)} matches")

    return len(found) > 0


def test_extract_for_ddr():
    """Test extracting symbols in DDR-compatible format."""
    print("\n" + "=" * 60)
    print("TEST: Extract DDR-Compatible Format")
    print("=" * 60)

    with open('/home/user/skills_fabric/test_index.scip', 'rb') as f:
        index = scip_pb2.Index()
        index.ParseFromString(f.read())

    # Convert to DDR format
    ddr_symbols = {}

    for doc in index.documents:
        file_path = doc.relative_path

        for sym in doc.symbols:
            # Parse the symbol name to extract the actual name
            # SCIP symbols look like: scip-python python skills_fabric_verify 1.0.0 `src/skills_fabric/verify/ddr.py`/DirectDependencyRetriever#
            parts = sym.symbol.split('/')
            if parts:
                # Get the last part (class/function name)
                name = parts[-1].rstrip('#').rstrip('.')

                # Extract line number from first occurrence if available
                line_num = None
                for occ in doc.occurrences:
                    if occ.symbol == sym.symbol:
                        # Range is [start_line, start_char, end_line, end_char]
                        if occ.range:
                            line_num = occ.range[0] + 1  # 0-indexed to 1-indexed
                        break

                ddr_symbols[name] = {
                    'file_path': file_path,
                    'line_num': line_num,
                    'documentation': sym.documentation[0] if sym.documentation else None,
                    'kind': sym.kind,
                    'full_symbol': sym.symbol,
                }

    print(f"✓ Extracted {len(ddr_symbols)} symbols in DDR format")

    # Show sample
    print(f"\nSample symbols:")
    for name, info in list(ddr_symbols.items())[:5]:
        print(f"\n  {name}:")
        print(f"    File: {info['file_path']}")
        print(f"    Line: {info['line_num']}")
        if info['documentation']:
            print(f"    Doc: {info['documentation'][:60]}...")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SCIP INDEX TEST SUITE")
    print("=" * 60)

    tests = [
        test_read_scip_index,
        test_symbol_search,
        test_extract_for_ddr,
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
