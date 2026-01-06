#!/usr/bin/env python3
"""Test DDR on Docling CodeWiki (smaller library for validation)."""
import sys
from pathlib import Path

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
retrieve_validated = ddr_module.retrieve_validated
SourceRef = ddr_module.SourceRef


def main():
    print("=" * 60)
    print("DOCLING DDR TEST")
    print("=" * 60)

    codewiki_path = Path("/home/user/skills_fabric/crawl_output/docling")
    catalog_path = codewiki_path / "symbol_catalog.md"

    if not catalog_path.exists():
        print(f"ERROR: {catalog_path} not found")
        return False

    # Load DDR
    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(catalog_path)

    metrics = ddr.get_hallucination_metrics()
    print(f"Symbols indexed: {metrics['symbols_indexed']}")
    print(f"Unique symbols: {metrics['unique_symbols']}")

    # Test queries
    test_queries = [
        "DocumentConverter",
        "PdfDocumentBackend",
        "AbstractDocumentBackend",
        "DoclingDocument",
        "TableFormerMode",
        "FakeSymbol",  # Should NOT be found
    ]

    print("\n--- Symbol Retrieval ---")
    verified = 0
    for query in test_queries:
        result = ddr.retrieve(query, max_results=3)
        status = "VERIFIED" if result.validated_count > 0 else "NOT FOUND"
        print(f"  {query}: {status} ({result.validated_count} matches)")

        if result.validated_count > 0:
            verified += 1
            for elem in result.elements[:2]:
                ref = elem.source_ref
                print(f"    -> {ref.symbol_name} at {ref.file_path}:{ref.line_number}")

    print(f"\n--- Summary ---")
    print(f"Verified: {verified}/{len(test_queries)}")
    print(f"FakeSymbol correctly rejected: {'YES' if verified == len(test_queries) - 1 else 'NO'}")

    return metrics['unique_symbols'] > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
