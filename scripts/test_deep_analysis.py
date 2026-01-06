#!/usr/bin/env python3
"""Test deep analysis (Levels 3-5) of progressive disclosure."""

import sys
from pathlib import Path

# Add the understanding module directory to path
sys.path.insert(0, '/home/user/skills_fabric/src/skills_fabric/understanding')

# Now import directly
from progressive_disclosure import DepthLevel, ProgressiveUnderstandingBuilder
from deep_analysis import create_deep_understanding, DeepAnalyzer

# Test
repo_path = Path("/home/user/skills_fabric/langgraph_repo")
codewiki_path = Path("/home/user/skills_fabric/crawl_output/langgraph")

print(f"Repo exists: {repo_path.exists()}")
print(f"CodeWiki exists: {codewiki_path.exists()}")

if repo_path.exists() and codewiki_path.exists():
    print("\n" + "="*60)
    print("Creating deep progressive understanding...")
    print("="*60)

    deep_pu = create_deep_understanding("langgraph", repo_path, codewiki_path)

    print(f"\nBuilt: {deep_pu.name}")
    print(f"Total nodes: {len(deep_pu.nodes)}")

    # Count by level
    for level in DepthLevel:
        count = len(deep_pu.get_at_level(level))
        if count > 0:
            print(f"  Level {level.value} ({level.name}): {count} nodes")

    # Test Level 3-5 on nodes with source refs
    print("\n" + "="*60)
    print("Testing Deep Analysis (Levels 3-5)")
    print("="*60)

    sections = deep_pu.get_at_level(DepthLevel.DETAILED_SECTIONS)
    tested = 0

    for section in sections:
        if section.source_refs and tested < 3:
            print(f"\n--- {section.title} ---")
            print(f"Source refs: {len(section.source_refs)}")

            for ref in section.source_refs[:2]:
                print(f"  -> {ref.symbol_name} @ {ref.file_path}:{ref.line}")

            # Level 3: Validate
            deep_pu.expand(section.id, DepthLevel.SOURCE_REFERENCES)
            validated = sum(1 for r in section.source_refs if r.verified)
            print(f"Level 3 - Validated: {validated}/{len(section.source_refs)}")

            # Level 4: Semantics
            deep_pu.expand(section.id, DepthLevel.SEMANTIC_ANALYSIS)
            if section.semantic_info:
                sig = section.semantic_info.type_signature
                print(f"Level 4 - Signature: {sig[:60] if sig else 'N/A'}...")
                if section.semantic_info.calls:
                    print(f"Level 4 - Calls: {section.semantic_info.calls[:5]}")
                if section.semantic_info.imports:
                    print(f"Level 4 - Imports: {len(section.semantic_info.imports)} total")

            # Level 5: Proofs
            deep_pu.expand(section.id, DepthLevel.EXECUTION_PROOFS)
            print(f"Level 5 - Proofs generated: {len(section.execution_proofs)}")
            for proof in section.execution_proofs[:2]:
                print(f"  -> {proof.assertion[:60]}...")

            tested += 1

    print("\n" + "="*60)
    print("Deep Analysis Complete!")
    print("="*60)
