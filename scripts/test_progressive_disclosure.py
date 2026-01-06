#!/usr/bin/env python3
"""Test progressive disclosure with docling (smaller dataset)."""

import sys
from pathlib import Path

# Direct import to avoid kuzu dependency in __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "progressive_disclosure",
    "/home/user/skills_fabric/src/skills_fabric/understanding/progressive_disclosure.py"
)
pd_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pd_module)

build_progressive_understanding = pd_module.build_progressive_understanding
DepthLevel = pd_module.DepthLevel
ProgressiveUnderstandingBuilder = pd_module.ProgressiveUnderstandingBuilder

# Test with langgraph
repo_path = Path('/home/user/skills_fabric/langgraph_repo')
codewiki_path = Path('/home/user/skills_fabric/crawl_output/langgraph')

print(f"Repo exists: {repo_path.exists()}")
print(f"CodeWiki exists: {codewiki_path.exists()}")

if repo_path.exists() and codewiki_path.exists():
    print("Building progressive understanding...")
    builder = ProgressiveUnderstandingBuilder('langgraph', repo_path, codewiki_path)
    print(f"Loaded {len(builder.symbols)} symbols")

    pu = builder.build()

    print(f"\n{'='*60}")
    print(f"Built progressive understanding for: {pu.name}")
    print(f"Commit: {pu.commit}")
    print(f"Total nodes: {len(pu.nodes)}")

    # Count by level
    for level in DepthLevel:
        count = len(pu.get_at_level(level))
        if count > 0:
            print(f"  Level {level.value} ({level.name}): {count} nodes")

    print(f"\n{'='*60}")
    print("LEVEL 0: EXECUTIVE SUMMARY")
    print('='*60)
    if pu.root_id:
        root = pu.nodes[pu.root_id]
        print(root.content[:500] if root.content else "(no content)")

    print(f"\n{'='*60}")
    print("LEVEL 1: CONCEPT MAP (Major Components)")
    print('='*60)
    for node in pu.get_at_level(DepthLevel.CONCEPT_MAP)[:10]:
        print(f"  - {node.title}")

    print(f"\n{'='*60}")
    print("LEVEL 2: DETAILED SECTIONS (with source refs)")
    print('='*60)
    for node in pu.get_at_level(DepthLevel.DETAILED_SECTIONS)[:8]:
        refs = [r.symbol_name for r in node.source_refs[:3]]
        refs_str = f" -> [{', '.join(refs)}]" if refs else ""
        print(f"  - {node.title}{refs_str}")

    # Save output
    output_path = codewiki_path / "progressive_understanding.json"
    pu.save(output_path)
    print(f"\nSaved to: {output_path}")
else:
    print("Paths not found!")
