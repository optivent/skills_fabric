#!/usr/bin/env python3
"""Test the CodeWiki-First approach.

This demonstrates the CORRECT order of operations:
1. Read CodeWiki output (pre-verified documentation)
2. Extract all GitHub links
3. Validate each against git clone
4. Parse symbols at verified locations
5. Expand dependencies

The key insight: We don't SEARCH for code, we FOLLOW verified links.
"""
import sys
import importlib.util
from pathlib import Path

# Load the module
script_dir = Path(__file__).parent.parent / "src" / "skills_fabric" / "understanding"
spec = importlib.util.spec_from_file_location("codewiki_first", script_dir / "codewiki_first.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

extract_codewiki_refs = module.extract_codewiki_refs
deduplicate_refs = module.deduplicate_refs
CodeWikiVerifier = module.CodeWikiVerifier
process_codewiki = module.process_codewiki
summarize_understanding = module.summarize_understanding
DepthLevel = module.DepthLevel


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_extract_refs():
    """Test extraction of references from CodeWiki."""
    print_section("STEP 1 & 2: EXTRACT CODEWIKI REFERENCES")

    codewiki_path = Path(__file__).parent.parent / "older_project" / "play_prototypes" / "loguru_poc" / "loguru_docs_output" / "Delgan_loguru" / "Loguru_Core_Library" / "codewiki_Loguru_Core_Library.md"

    if not codewiki_path.exists():
        print(f"CodeWiki file not found: {codewiki_path}")
        return []

    content = codewiki_path.read_text()
    refs = extract_codewiki_refs(content)
    refs = deduplicate_refs(refs)

    print(f"Found {len(refs)} unique references in CodeWiki\n")

    # Show first 10
    print("First 10 references:")
    for ref in refs[:10]:
        print(f"  • {ref.concept}")
        print(f"    └─ {ref.file_path}:{ref.line}")

    print(f"\n... and {len(refs) - 10} more")

    return refs, content


def test_validate_refs():
    """Test validation of references against actual code.

    Note: This would require the loguru repo to be cloned.
    For demonstration, we'll show what WOULD happen.
    """
    print_section("STEP 3: VALIDATE AGAINST GIT CLONE")

    print("For each CodeWiki reference:")
    print("")
    print("  CodeWikiRef(concept='logger', file='_logger.py', line=231)")
    print("      │")
    print("      ▼")
    print("  Git Clone: Read _logger.py, check line 231")
    print("      │")
    print("      ▼")
    print("  Does 'logger' appear at line 231?")
    print("      │")
    print("      ▼")
    print("  ✓ VALIDATED: Yes, it does")
    print("")
    print("This step ensures CodeWiki links are STILL VALID")
    print("(code may have changed since documentation was written)")


def test_with_langgraph():
    """Test with actual LangGraph repo which we DO have cloned."""
    print_section("DEMO: CODEWIKI → LANGGRAPH")

    # Simulate CodeWiki content for LangGraph
    simulated_codewiki = """
# StateGraph

The [`StateGraph`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/state.py#L112)
class is the core abstraction for building stateful graphs.

The [`compile`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/state.py#L824)
method transforms a StateGraph into a [`CompiledStateGraph`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/state.py#L932).

For checkpointing, use [`MemorySaver`](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L1).
"""

    print("Simulated CodeWiki content:")
    print("-" * 50)
    print(simulated_codewiki[:300] + "...")
    print("-" * 50)

    # Extract refs
    refs = extract_codewiki_refs(simulated_codewiki)
    print(f"\nExtracted {len(refs)} references:")
    for ref in refs:
        print(f"  • {ref.concept} at {ref.file_path}:{ref.line}")

    # Try to validate against our cloned repo
    langgraph_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo" / "libs" / "langgraph"

    if langgraph_path.exists():
        print(f"\nValidating against {langgraph_path}...")
        verifier = CodeWikiVerifier(str(langgraph_path))

        for ref in refs:
            if "langgraph" in ref.file_path:
                # Adjust path for our repo structure
                adjusted_ref = module.CodeWikiRef(
                    concept=ref.concept,
                    repo=ref.repo,
                    file_path=ref.file_path.replace("libs/langgraph/", ""),
                    line=ref.line,
                    commit=ref.commit
                )

                result = verifier.validate_ref(adjusted_ref)
                status = "✓ VALID" if result.valid else "✗ INVALID"
                print(f"  {status}: {ref.concept}")
                if result.valid and result.actual_content:
                    # Show a snippet
                    snippet = result.actual_content.split('\n')[0][:60]
                    print(f"    Content: {snippet}...")
                elif result.error:
                    print(f"    Error: {result.error}")

                # Parse symbol if valid
                if result.valid:
                    symbol = verifier.parse_symbol_at_line(adjusted_ref)
                    if symbol:
                        print(f"    Parsed: {symbol.kind} '{symbol.name}'")
                        if symbol.methods:
                            print(f"    Methods: {symbol.methods[:5]}...")
    else:
        print(f"\nLangGraph repo not found at {langgraph_path}")


def test_full_flow():
    """Demonstrate the complete flow with the real CodeWiki."""
    print_section("COMPLETE FLOW DEMONSTRATION")

    print("""
THE CORRECT ORDER OF PROCEEDINGS:

┌─────────────────────────────────────────────────────────────────┐
│  1. CODEWIKI INPUT                                              │
│                                                                  │
│     "The [`logger`](github.com/.../loguru/_logger.py#L231)..."  │
│                                                                  │
│     This is DOCUMENTATION with EMBEDDED VERIFIED LINKS          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. LINK EXTRACTION                                             │
│                                                                  │
│     CodeWikiRef(                                                 │
│       concept="logger",                                          │
│       repo="delgan/loguru",                                      │
│       file="_logger.py",                                         │
│       line=231,                                                  │
│       commit="36da8cca"                                          │
│     )                                                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. VALIDATION (Against Git Clone)                              │
│                                                                  │
│     Read _logger.py line 231 → Contains "logger"?               │
│     ✓ YES → Link is STILL VALID                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. AST PARSING (At Verified Location)                          │
│                                                                  │
│     Parse symbol at line 231:                                    │
│     - Kind: class                                                │
│     - Name: Logger                                               │
│     - Methods: [add, remove, bind, catch, ...]                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. DEPENDENCY EXPANSION (LSP + AST)                            │
│                                                                  │
│     Logger uses: Handler, FileSink, Colorizer, ...              │
│     → Each becomes a new CodeWikiRef to validate                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. EXECUTION VERIFICATION (Sandbox)                            │
│                                                                  │
│     from loguru import logger                                    │
│     logger.add(sys.stderr) → Works? ✓                           │
└─────────────────────────────────────────────────────────────────┘

RESULT: Every fact is PROVEN by following verified links.
""")


def test_real_codewiki_stats():
    """Show statistics from real CodeWiki output."""
    print_section("REAL CODEWIKI STATISTICS")

    codewiki_path = Path(__file__).parent.parent / "older_project" / "play_prototypes" / "loguru_poc" / "loguru_docs_output" / "Delgan_loguru" / "Loguru_Core_Library" / "codewiki_Loguru_Core_Library.md"

    if not codewiki_path.exists():
        print("CodeWiki file not found")
        return

    content = codewiki_path.read_text()
    refs = extract_codewiki_refs(content)
    unique_refs = deduplicate_refs(refs)

    # Analyze references
    files = set(r.file_path for r in unique_refs)
    with_lines = [r for r in unique_refs if r.line > 0]
    concepts = set(r.concept for r in unique_refs)

    print(f"Total references:     {len(refs)}")
    print(f"Unique references:    {len(unique_refs)}")
    print(f"Unique files:         {len(files)}")
    print(f"With line numbers:    {len(with_lines)} ({100*len(with_lines)//len(unique_refs)}%)")
    print(f"Unique concepts:      {len(concepts)}")

    print("\nFiles referenced:")
    for f in sorted(files)[:10]:
        count = sum(1 for r in unique_refs if r.file_path == f)
        print(f"  {count:3d}× {f}")

    print("\nMost referenced concepts:")
    concept_counts = {}
    for r in refs:
        concept_counts[r.concept] = concept_counts.get(r.concept, 0) + 1
    for concept, count in sorted(concept_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:3d}× {concept}")


def main():
    print("\n" + "=" * 70)
    print("  CODEWIKI-FIRST PROOF-BASED UNDERSTANDING")
    print("  'Follow Verified Links, Don't Search'")
    print("=" * 70)

    test_extract_refs()
    test_validate_refs()
    test_with_langgraph()
    test_real_codewiki_stats()
    test_full_flow()

    print_section("KEY INSIGHT")
    print("""
I had NOT properly read the CodeWiki output before building the proof system.

The CodeWiki contains PRE-VERIFIED connections:
  - Concept names
  - Exact file paths
  - Exact line numbers
  - Commit hashes

These are not hints to search for - they are VERIFIED LINKS to follow.

The correct approach:
  1. Extract links from CodeWiki
  2. Validate each link (did code change?)
  3. Parse at verified locations
  4. Expand dependencies
  5. Execute for behavior

This is fundamentally different from "searching the codebase".
""")


if __name__ == "__main__":
    main()
