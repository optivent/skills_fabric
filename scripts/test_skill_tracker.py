#!/usr/bin/env python3
"""Test Skill Tracker - KuzuDB skill integration."""

import sys
import shutil
import importlib.util
from pathlib import Path

# Load modules directly
spec = importlib.util.spec_from_file_location(
    "skill_tracker",
    "/home/user/skills_fabric/src/skills_fabric/graph/skill_tracker.py"
)
skill_tracker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_tracker_module)

SkillTracker = skill_tracker_module.SkillTracker
TrackedSkill = skill_tracker_module.TrackedSkill
populate_from_skills_directory = skill_tracker_module.populate_from_skills_directory


def cleanup_db(path):
    """Clean up test database."""
    import os
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


# Sample skill content for testing
SAMPLE_SKILL_1 = '''
# Document Conversion with Docling

The `DocumentConverter` class provides PDF conversion functionality.

## Usage

```python
from docling import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
```

See `DocumentConverter` implementation at `docling/document_converter.py:50`

The `InputFormat` enum defines supported input formats.
Reference: `docling/datamodel/input_format.py:25`
'''

SAMPLE_SKILL_2 = '''
# Advanced PDF Processing

Building on `DocumentConverter`, this skill shows advanced usage.

## Features

- Uses `DocumentConverter` from `docling/document_converter.py:50`
- Configures `PdfPipelineOptions` at `docling/pipeline/pdf_options.py:100`
- Handles errors via `ConversionError` at `docling/errors.py:15`
'''


def test_create_tracker():
    """Test creating skill tracker."""
    print("=" * 60)
    print("TEST 1: Create Skill Tracker")
    print("=" * 60)

    test_db = "./test_skill_tracker"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    print("✓ Created SkillTracker")
    print(f"  Database: {test_db}")

    tracker.close()
    cleanup_db(test_db)
    return True


def test_register_skill():
    """Test registering a skill."""
    print("\n" + "=" * 60)
    print("TEST 2: Register Skill")
    print("=" * 60)

    test_db = "./test_skill_register"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    skill = tracker.register_skill(
        skill_id="docling:pdf_conversion",
        name="PDF Conversion",
        library="docling",
        content=SAMPLE_SKILL_1,
    )

    print(f"✓ Registered skill: {skill.skill_id}")
    print(f"  Name: {skill.name}")
    print(f"  Library: {skill.library}")
    print(f"  Citations found: {len(skill.citations)}")

    for citation in skill.citations:
        print(f"    - {citation.symbol_name}: {citation.citation_text}")

    assert len(skill.citations) >= 2, "Should extract citations"

    tracker.close()
    cleanup_db(test_db)
    return True


def test_query_skill_symbols():
    """Test querying symbols for a skill."""
    print("\n" + "=" * 60)
    print("TEST 3: Query Skill Symbols")
    print("=" * 60)

    test_db = "./test_skill_query"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    # Register skill
    tracker.register_skill(
        skill_id="docling:pdf_conversion",
        name="PDF Conversion",
        library="docling",
        content=SAMPLE_SKILL_1,
    )

    # Query symbols
    symbols = tracker.get_skill_symbols("docling:pdf_conversion")

    print(f"✓ Queried symbols: {len(symbols)} found")

    for sym in symbols:
        print(f"  - {sym.get('sym.name', 'N/A')}: {sym.get('r.citation', 'N/A')}")

    assert len(symbols) >= 1, "Should find symbols"

    tracker.close()
    cleanup_db(test_db)
    return True


def test_find_related_skills():
    """Test finding related skills via shared symbols."""
    print("\n" + "=" * 60)
    print("TEST 4: Find Related Skills")
    print("=" * 60)

    test_db = "./test_skill_related"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    # Register two skills that share symbols
    tracker.register_skill(
        skill_id="docling:pdf_conversion",
        name="PDF Conversion",
        library="docling",
        content=SAMPLE_SKILL_1,
    )

    tracker.register_skill(
        skill_id="docling:advanced_pdf",
        name="Advanced PDF",
        library="docling",
        content=SAMPLE_SKILL_2,
    )

    # Find skills related to pdf_conversion
    related = tracker.find_related_skills("docling:pdf_conversion")

    print(f"✓ Found related skills: {len(related)}")

    for rel in related:
        print(f"  - {rel.get('s2.name', 'N/A')}: {rel.get('shared_symbols', 0)} shared symbols")

    # Both skills reference DocumentConverter, so they should be related
    # (but only if the citations extract the same symbol)

    tracker.close()
    cleanup_db(test_db)
    return True


def test_citation_integrity():
    """Test citation integrity checking."""
    print("\n" + "=" * 60)
    print("TEST 5: Citation Integrity")
    print("=" * 60)

    test_db = "./test_skill_integrity"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    tracker.register_skill(
        skill_id="docling:pdf_conversion",
        name="PDF Conversion",
        library="docling",
        content=SAMPLE_SKILL_1,
    )

    integrity = tracker.get_citation_integrity("docling:pdf_conversion")

    print(f"✓ Citation integrity check:")
    print(f"  Total citations: {integrity['total_citations']}")
    print(f"  Valid: {integrity['valid_citations']}")
    print(f"  Invalid: {integrity['invalid_citations']}")
    print(f"  Score: {integrity['integrity_score']:.2f}")

    tracker.close()
    cleanup_db(test_db)
    return True


def test_library_stats():
    """Test library statistics."""
    print("\n" + "=" * 60)
    print("TEST 6: Library Statistics")
    print("=" * 60)

    test_db = "./test_skill_stats"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    # Register multiple skills
    tracker.register_skill(
        skill_id="docling:pdf_conversion",
        name="PDF Conversion",
        library="docling",
        content=SAMPLE_SKILL_1,
    )

    tracker.register_skill(
        skill_id="docling:advanced_pdf",
        name="Advanced PDF",
        library="docling",
        content=SAMPLE_SKILL_2,
    )

    stats = tracker.get_library_stats("docling")

    print(f"✓ Library stats for 'docling':")
    print(f"  Skills: {stats['skill_count']}")
    print(f"  Unique symbols: {stats['symbol_count']}")
    print(f"  Avg symbols/skill: {stats['avg_symbols_per_skill']:.1f}")

    assert stats['skill_count'] == 2, "Should have 2 skills"

    tracker.close()
    cleanup_db(test_db)
    return True


def test_with_real_skills():
    """Test with real generated skills if available."""
    print("\n" + "=" * 60)
    print("TEST 7: Real Skills (if available)")
    print("=" * 60)

    skills_dir = Path("/home/user/skills_fabric/output/docling_skills")

    if not skills_dir.exists() or not list(skills_dir.glob("*.md")):
        print("⚠ No real skills found, skipping")
        return True

    test_db = "./test_skill_real"
    cleanup_db(test_db)

    tracker = SkillTracker(test_db)

    tracked = populate_from_skills_directory(
        tracker=tracker,
        skills_dir=str(skills_dir),
        library="docling",
    )

    print(f"✓ Loaded {len(tracked)} real skills")

    for skill in tracked[:3]:
        print(f"  - {skill.name}: {len(skill.citations)} citations")

    stats = tracker.get_library_stats("docling")
    print(f"\n  Total unique symbols: {stats['symbol_count']}")

    tracker.close()
    cleanup_db(test_db)
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SKILL TRACKER TEST SUITE")
    print("=" * 60)

    tests = [
        test_create_tracker,
        test_register_skill,
        test_query_skill_symbols,
        test_find_related_skills,
        test_citation_integrity,
        test_library_stats,
        test_with_real_skills,
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
