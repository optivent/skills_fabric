#!/usr/bin/env python3
"""Comprehensive DDR validation - verify ALL symbols are parsed correctly."""
import sys
from pathlib import Path
import re

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

ddr_module = load_module("ddr", src_path / "skills_fabric" / "verify" / "ddr.py")
DirectDependencyRetriever = ddr_module.DirectDependencyRetriever


def count_symbols_in_catalog(catalog_path: Path) -> dict:
    """Count symbols directly from catalog file."""
    content = catalog_path.read_text()

    counts = {
        "classes": 0,
        "functions": 0,
        "methods": 0,
        "total": 0,
        "files": set(),
        "all_symbols": []
    }

    current_file = None
    simple_file_pattern = r'^###\s+`([^`]+)`'
    simple_symbol_pattern = r'^-\s+Line\s+(\d+):\s+`([^`]+)`\s+\((\w+)\)'

    for line in content.split('\n'):
        file_match = re.match(simple_file_pattern, line)
        if file_match:
            current_file = file_match.group(1)
            counts["files"].add(current_file)
            continue

        if current_file:
            symbol_match = re.match(simple_symbol_pattern, line)
            if symbol_match:
                line_num = int(symbol_match.group(1))
                symbol = symbol_match.group(2)
                sym_type = symbol_match.group(3)

                counts["all_symbols"].append({
                    "symbol": symbol,
                    "type": sym_type,
                    "line": line_num,
                    "file": current_file
                })
                counts["total"] += 1

                if sym_type == "class":
                    counts["classes"] += 1
                elif sym_type == "function":
                    counts["functions"] += 1
                elif sym_type == "method":
                    counts["methods"] += 1

    counts["files"] = len(counts["files"])
    return counts


def verify_ddr_parsing(catalog_path: Path, codewiki_path: Path) -> dict:
    """Verify DDR parses all symbols from catalog."""
    # Load DDR
    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(catalog_path)

    metrics = ddr.get_hallucination_metrics()

    return {
        "symbols_indexed": metrics["symbols_indexed"],
        "unique_symbols": metrics["unique_symbols"],
        "index": ddr._symbol_index
    }


def compare_and_report(catalog_counts: dict, ddr_results: dict) -> bool:
    """Compare catalog counts with DDR parsing and report discrepancies."""
    print("=" * 70)
    print("COMPREHENSIVE DDR VALIDATION")
    print("=" * 70)

    print("\n--- Catalog Analysis (Ground Truth) ---")
    print(f"  Total symbols in catalog: {catalog_counts['total']}")
    print(f"  Classes: {catalog_counts['classes']}")
    print(f"  Functions: {catalog_counts['functions']}")
    print(f"  Methods: {catalog_counts['methods']}")
    print(f"  Source files: {catalog_counts['files']}")

    print("\n--- DDR Parsing Results ---")
    print(f"  Symbols indexed: {ddr_results['symbols_indexed']}")
    print(f"  Unique symbols: {ddr_results['unique_symbols']}")

    # Check if counts match
    match = catalog_counts['total'] == ddr_results['symbols_indexed']

    print("\n--- Validation ---")
    if match:
        print(f"  ✓ PASS: All {catalog_counts['total']} symbols parsed correctly")
    else:
        print(f"  ✗ FAIL: Expected {catalog_counts['total']}, got {ddr_results['symbols_indexed']}")
        diff = catalog_counts['total'] - ddr_results['symbols_indexed']
        print(f"  Missing: {diff} symbols")

    # Sample verification - check specific symbols can be retrieved
    print("\n--- Sample Retrieval Test ---")
    sample_symbols = [
        catalog_counts['all_symbols'][0],  # First
        catalog_counts['all_symbols'][len(catalog_counts['all_symbols'])//2],  # Middle
        catalog_counts['all_symbols'][-1],  # Last
    ]

    ddr = DirectDependencyRetriever(codewiki_path=Path("/home/user/skills_fabric/crawl_output/docling"))
    ddr._symbol_index = ddr_results['index']
    ddr._loaded = True

    for sym in sample_symbols:
        result = ddr.retrieve(sym['symbol'], max_results=1)
        status = "✓" if result.validated_count > 0 else "✗"
        print(f"  {status} {sym['symbol']} ({sym['type']}) at {sym['file']}:{sym['line']}")
        if result.validated_count > 0:
            found = result.elements[0].source_ref
            print(f"      Found: {found.file_path}:{found.line_number}")

    # Check for any symbols that weren't indexed
    print("\n--- Missing Symbol Analysis ---")
    indexed_symbols = set()
    for key, entries in ddr_results['index'].items():
        for entry in entries:
            indexed_symbols.add(entry['symbol'].lower())

    missing = []
    for sym in catalog_counts['all_symbols']:
        if sym['symbol'].lower() not in indexed_symbols:
            missing.append(sym)

    if missing:
        print(f"  {len(missing)} symbols NOT indexed:")
        for m in missing[:10]:
            print(f"    - {m['symbol']} ({m['type']}) at {m['file']}:{m['line']}")
        if len(missing) > 10:
            print(f"    ... and {len(missing) - 10} more")
    else:
        print("  ✓ All symbols indexed successfully")

    return match and len(missing) == 0


def main():
    catalog_path = Path("/home/user/skills_fabric/crawl_output/docling/symbol_catalog.md")
    codewiki_path = Path("/home/user/skills_fabric/crawl_output/docling")

    if not catalog_path.exists():
        print(f"ERROR: {catalog_path} not found")
        return False

    # Count symbols in catalog
    catalog_counts = count_symbols_in_catalog(catalog_path)

    # Verify DDR parsing
    ddr_results = verify_ddr_parsing(catalog_path, codewiki_path)

    # Compare and report
    success = compare_and_report(catalog_counts, ddr_results)

    print("\n" + "=" * 70)
    print(f"FINAL RESULT: {'PASS' if success else 'FAIL'}")
    print("=" * 70)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
