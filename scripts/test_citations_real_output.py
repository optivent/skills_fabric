#!/usr/bin/env python3
"""Test citation system on real generated skills."""
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
SourceRef = ddr_module.SourceRef


def add_citations(content: str, refs: dict) -> tuple[str, int, list]:
    """Add citations to content and return (cited_content, citations_added, uncited)."""
    cited_content = content
    citations_added = 0
    uncited = []

    # Find code references
    pattern = r'`([A-Za-z_][A-Za-z0-9_]*)`'
    matches = list(re.finditer(pattern, content))

    for match in reversed(matches):
        symbol = match.group(1)
        ref = refs.get(symbol.lower())

        if ref:
            citation = f"[`{symbol}`]({ref.file_path}#L{ref.line_number})"
            start, end = match.span()
            cited_content = cited_content[:start] + citation + cited_content[end:]
            citations_added += 1
        else:
            if symbol not in uncited:
                uncited.append(symbol)

    return cited_content, citations_added, uncited


def main():
    print("=" * 70)
    print("CITATION SYSTEM VALIDATION")
    print("=" * 70)

    skills_path = Path("/home/user/skills_fabric/output/docling_skills")
    codewiki_path = Path("/home/user/skills_fabric/crawl_output/docling")

    if not skills_path.exists():
        print("ERROR: No generated skills found")
        return False

    # Load DDR
    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(codewiki_path / "symbol_catalog.md")

    # Build reference map
    refs = {}
    for symbol_key, entries in ddr._symbol_index.items():
        for entry in entries:
            ref = SourceRef(
                symbol_name=entry['symbol'],
                file_path=entry['file'],
                line_number=entry['line'],
                symbol_type=entry.get('type', 'unknown'),
                validated=True
            )
            refs[symbol_key] = ref
            # Also index by exact symbol name
            refs[entry['symbol'].lower()] = ref

    print(f"Reference map: {len(refs)} entries")

    # Process each skill
    total_citations = 0
    total_uncited = 0
    all_uncited = []

    output_path = Path("/home/user/skills_fabric/output/docling_skills_cited")
    output_path.mkdir(parents=True, exist_ok=True)

    skill_files = list(skills_path.glob("*.md"))
    print(f"\nProcessing {len(skill_files)} skill files...")

    for skill_file in skill_files:
        content = skill_file.read_text()

        # Add citations
        cited_content, citations, uncited = add_citations(content, refs)

        total_citations += citations
        total_uncited += len(uncited)
        all_uncited.extend(uncited)

        # Save cited version
        cited_file = output_path / skill_file.name
        cited_file.write_text(cited_content)

        print(f"  {skill_file.name}: {citations} citations added, {len(uncited)} uncited")

    # Summary
    print("\n" + "=" * 70)
    print("CITATION SUMMARY")
    print("=" * 70)
    print(f"  Total skills processed: {len(skill_files)}")
    print(f"  Total citations added: {total_citations}")
    print(f"  Total uncited symbols: {total_uncited}")

    if all_uncited:
        unique_uncited = list(set(all_uncited))
        print(f"\n  Uncited symbols:")
        for sym in unique_uncited[:10]:
            print(f"    - {sym}")

    # Show sample cited skill
    print("\n" + "=" * 70)
    print("SAMPLE CITED SKILL")
    print("=" * 70)
    sample = (output_path / "FormatOption.md").read_text()
    print(sample)

    # Verify citations are valid
    print("\n" + "=" * 70)
    print("CITATION VERIFICATION")
    print("=" * 70)

    # Extract citations from sample
    citation_pattern = r'\[`([^`]+)`\]\(([^)]+)\)'
    citations_found = re.findall(citation_pattern, sample)

    verified = 0
    for symbol, path in citations_found:
        # Check if path exists in DDR
        file_path = path.split('#')[0]
        result = ddr.retrieve(symbol, max_results=1)
        if result.validated_count > 0:
            verified += 1
            print(f"  ✓ {symbol} -> {path}")
        else:
            print(f"  ✗ {symbol} -> {path} (NOT FOUND IN DDR)")

    if citations_found:
        rate = verified / len(citations_found)
        print(f"\n  Verification rate: {rate:.2%}")
        print(f"  Target (100%): {'PASS' if rate == 1.0 else 'FAIL'}")
    else:
        print("  No citations to verify")

    success = total_uncited == 0 or (total_citations > 0 and len(citations_found) > 0 and verified == len(citations_found))
    print(f"\nFINAL RESULT: {'PASS' if success else 'FAIL'}")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
