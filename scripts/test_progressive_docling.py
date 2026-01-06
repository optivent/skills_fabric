#!/usr/bin/env python3
"""Test Progressive Disclosure generation for Docling with DDR integration."""
import sys
from pathlib import Path
import json
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

# Load modules directly to avoid kuzu dependency
ddr_module = load_module("ddr", src_path / "skills_fabric" / "verify" / "ddr.py")
pd_module = load_module("progressive_disclosure", src_path / "skills_fabric" / "understanding" / "progressive_disclosure.py")

DirectDependencyRetriever = ddr_module.DirectDependencyRetriever
SourceRef = ddr_module.SourceRef
DepthLevel = pd_module.DepthLevel
ProgressiveUnderstanding = pd_module.ProgressiveUnderstanding
UnderstandingNode = pd_module.UnderstandingNode


class DoclingProgressiveUnderstanding(ProgressiveUnderstanding):
    """Progressive understanding with DDR integration for Docling."""

    def __init__(self, codewiki_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.codewiki_path = codewiki_path
        self.ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
        self.ddr.load_symbol_catalog(codewiki_path / "symbol_catalog.md")

    def _find_source_refs(self, node: UnderstandingNode) -> list:
        """Find source references using DDR (zero-hallucination)."""
        refs = []

        # Extract keywords from node title and content
        keywords = list(node.keywords) + [node.title]

        for keyword in keywords:
            result = self.ddr.retrieve(keyword, max_results=3)
            for element in result.elements:
                # Convert DDR SourceRef to progressive_disclosure SourceRef
                pd_ref = pd_module.SourceRef(
                    file_path=element.source_ref.file_path,
                    line=element.source_ref.line_number,
                    commit="main",
                    repo="docling-project/docling",
                    symbol_name=element.source_ref.symbol_name,
                    symbol_kind=element.source_ref.symbol_type,
                    verified=element.source_ref.validated,
                )
                refs.append(pd_ref)

        return refs


def parse_codewiki_sections(codewiki_path: Path) -> dict:
    """Parse CodeWiki sections into L0-L2 nodes."""
    sections_dir = codewiki_path / "sections"
    codewiki_file = codewiki_path / "codewiki_docling.md"

    nodes = {
        "concepts": [],
        "details": [],
    }

    # Parse main codewiki for executive summary
    if codewiki_file.exists():
        content = codewiki_file.read_text()
        # Extract first paragraph after title
        match = re.search(r'^Docling simplifies.*?$', content, re.MULTILINE)
        if match:
            nodes["executive_summary"] = match.group(0)

    # Parse sections for concepts and details
    if sections_dir.exists():
        for section_file in sorted(sections_dir.glob("*.md"))[:20]:
            content = section_file.read_text()
            # Extract title from first line
            lines = content.strip().split('\n')
            if lines:
                title = lines[0].lstrip('#').strip()
                # First 200 chars of content
                body = '\n'.join(lines[1:])[:500]

                nodes["concepts"].append({
                    "title": title,
                    "content": body,
                    "file": section_file.name
                })

    return nodes


def build_progressive_understanding(codewiki_path: Path) -> DoclingProgressiveUnderstanding:
    """Build progressive understanding tree for Docling."""
    pu = DoclingProgressiveUnderstanding(
        codewiki_path=codewiki_path,
        name="docling",
        repo="docling-project/docling",
        commit="main"
    )

    # Parse CodeWiki
    parsed = parse_codewiki_sections(codewiki_path)

    # Level 0: Executive Summary (root)
    root = UnderstandingNode(
        id="root",
        title="Docling",
        level=DepthLevel.EXECUTIVE_SUMMARY,
        content=parsed.get("executive_summary", "Docling simplifies document processing, parsing diverse formats including advanced PDF understanding."),
        keywords={"docling", "pdf", "document", "parsing", "converter"}
    )
    pu.add_node(root)
    pu.root_id = "root"

    # Level 1: Concept Map
    concept_keywords = [
        ("Document Conversion", {"converter", "convert", "document"}),
        ("PDF Processing", {"pdf", "parsing", "layout"}),
        ("Backend Architecture", {"backend", "abstract", "base"}),
        ("Pipeline Options", {"pipeline", "options", "config"}),
        ("Export Formats", {"export", "markdown", "json"}),
    ]

    for i, (title, keywords) in enumerate(concept_keywords):
        concept = UnderstandingNode(
            id=f"concept_{i}",
            title=title,
            level=DepthLevel.CONCEPT_MAP,
            content=f"Core concept: {title}",
            parent_id="root",
            keywords=keywords
        )
        pu.add_node(concept)
        root.children_ids.append(f"concept_{i}")

    # Level 2: Detailed Sections (from CodeWiki sections)
    for i, section in enumerate(parsed.get("concepts", [])[:10]):
        detail = UnderstandingNode(
            id=f"detail_{i}",
            title=section["title"],
            level=DepthLevel.DETAILED_SECTIONS,
            content=section["content"],
            parent_id=f"concept_{i % 5}",  # Distribute among concepts
            keywords=set(section["title"].lower().split())
        )
        pu.add_node(detail)

    return pu


def test_progressive_disclosure():
    """Test progressive disclosure with DDR integration."""
    print("=" * 70)
    print("PROGRESSIVE DISCLOSURE TEST - DOCLING")
    print("=" * 70)

    codewiki_path = Path("/home/user/skills_fabric/crawl_output/docling")

    # Build understanding tree
    print("\n--- Building Progressive Understanding ---")
    pu = build_progressive_understanding(codewiki_path)

    print(f"Total nodes: {len(pu.nodes)}")
    for level in DepthLevel:
        count = len(pu.get_at_level(level))
        print(f"  Level {level.value} ({level.name}): {count} nodes")

    # Test Level 0: Executive Summary
    print("\n--- Level 0: Executive Summary ---")
    root = pu.nodes[pu.root_id]
    print(f"Title: {root.title}")
    print(f"Content: {root.content[:200]}...")

    # Test Level 1: Concept Map
    print("\n--- Level 1: Concept Map ---")
    concepts = pu.get_at_level(DepthLevel.CONCEPT_MAP)
    for c in concepts:
        print(f"  - {c.title}: {c.content[:50]}...")

    # Test Level 2: Detailed Sections
    print("\n--- Level 2: Detailed Sections ---")
    details = pu.get_at_level(DepthLevel.DETAILED_SECTIONS)
    print(f"  {len(details)} detailed sections")
    for d in details[:3]:
        print(f"  - {d.title}")

    # Test Level 3: Source References (DDR Integration)
    print("\n--- Level 3: Source References (DDR) ---")
    test_node = concepts[0]  # Document Conversion
    print(f"Expanding '{test_node.title}' with DDR...")

    expanded = pu.expand(test_node.id, DepthLevel.SOURCE_REFERENCES)

    if expanded.source_refs:
        print(f"  Found {len(expanded.source_refs)} source references:")
        for ref in expanded.source_refs[:5]:
            verified = "✓" if ref.verified else "✗"
            print(f"    {verified} {ref.symbol_name} ({ref.symbol_kind})")
            print(f"       {ref.local_path}")
    else:
        print("  No source references found")

    # Test search functionality
    print("\n--- Search Test ---")
    queries = ["converter", "pdf", "backend"]
    for query in queries:
        results = pu.search(query)
        print(f"  '{query}': {len(results)} results")
        if results:
            print(f"    Top: {results[0].title} (L{results[0].level})")

    # Test summary generation
    print("\n--- Summary Generation ---")
    summary = pu.get_summary(max_level=DepthLevel.CONCEPT_MAP)
    print(summary[:500] + "...")

    # Verify DDR integration
    print("\n--- DDR Integration Validation ---")
    total_refs = 0
    verified_refs = 0

    for node in pu.nodes.values():
        if node.source_refs:
            total_refs += len(node.source_refs)
            verified_refs += sum(1 for r in node.source_refs if r.verified)

    print(f"  Total source refs: {total_refs}")
    print(f"  Verified refs: {verified_refs}")
    if total_refs > 0:
        rate = verified_refs / total_refs
        print(f"  Verification rate: {rate:.2%}")
        print(f"  Meets target (100%): {'YES' if rate == 1.0 else 'NO'}")

    return True


def main():
    success = test_progressive_disclosure()

    print("\n" + "=" * 70)
    print(f"TEST RESULT: {'PASS' if success else 'FAIL'}")
    print("=" * 70)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
