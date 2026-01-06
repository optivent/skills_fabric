#!/usr/bin/env python3
"""Build CodeWiki-style output from cloned docling repo.

Since CodeWiki requires JavaScript rendering and we have network issues,
we build the same structure from the cloned repo:
1. Extract documentation from docs/ folder
2. Analyze source code in docling/ folder
3. Create links between documentation concepts and source locations
4. Output CodeWiki-style sections with embedded GitHub links
"""
import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime


REPO_PATH = Path(__file__).parent.parent / "crawl_output" / "docling_repo" / "docling"
OUTPUT_PATH = Path(__file__).parent.parent / "crawl_output" / "docling"
GITHUB_BASE = "https://github.com/docling-project/docling/blob/main"


@dataclass
class SourceSymbol:
    """A symbol extracted from source code."""
    name: str
    kind: str  # "class", "function", "method"
    file_path: str
    line: int
    docstring: str = ""
    signature: str = ""


@dataclass
class DocSection:
    """A documentation section."""
    title: str
    content: str
    file_path: str
    level: int = 0
    symbols: List[SourceSymbol] = field(default_factory=list)


@dataclass
class CodeWikiLink:
    """A link in CodeWiki format."""
    concept: str
    file_path: str
    line: int

    def to_markdown(self) -> str:
        return f"[`{self.concept}`]({GITHUB_BASE}/{self.file_path}#L{self.line})"


def extract_symbols_from_file(file_path: Path, base_path: Path) -> List[SourceSymbol]:
    """Extract classes and functions from a Python file."""
    symbols = []

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        rel_path = str(file_path.relative_to(base_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(SourceSymbol(
                    name=node.name,
                    kind="class",
                    file_path=rel_path,
                    line=node.lineno,
                    docstring=ast.get_docstring(node) or ""
                ))

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                        symbols.append(SourceSymbol(
                            name=f"{node.name}.{item.name}",
                            kind="method",
                            file_path=rel_path,
                            line=item.lineno,
                            docstring=ast.get_docstring(item) or ""
                        ))

            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                # Top-level functions
                symbols.append(SourceSymbol(
                    name=node.name,
                    kind="function",
                    file_path=rel_path,
                    line=node.lineno,
                    docstring=ast.get_docstring(node) or ""
                ))

    except Exception as e:
        print(f"  Warning: Could not parse {file_path}: {e}")

    return symbols


def extract_all_symbols(repo_path: Path) -> Dict[str, SourceSymbol]:
    """Extract all symbols from the docling source code."""
    symbols = {}
    source_dir = repo_path / "docling"

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return symbols

    for py_file in source_dir.rglob("*.py"):
        file_symbols = extract_symbols_from_file(py_file, repo_path)
        for sym in file_symbols:
            # Use lowercase name as key for matching
            key = sym.name.lower().split('.')[-1]  # Last part for methods
            if key not in symbols:
                symbols[key] = sym

    return symbols


def link_documentation_to_source(doc_content: str, symbols: Dict[str, SourceSymbol]) -> Tuple[str, List[CodeWikiLink]]:
    """Find mentions of symbols in documentation and create links."""
    links = []
    enhanced_content = doc_content

    # Find code references like `DocumentConverter` or `convert()`
    code_pattern = r'`([A-Z][a-zA-Z0-9_]+(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)`'

    for match in re.finditer(code_pattern, doc_content):
        concept = match.group(1)
        key = concept.lower().split('.')[-1]

        if key in symbols:
            sym = symbols[key]
            link = CodeWikiLink(
                concept=concept,
                file_path=sym.file_path,
                line=sym.line
            )
            links.append(link)

    return enhanced_content, links


def process_doc_file(file_path: Path, base_path: Path, symbols: Dict[str, SourceSymbol]) -> DocSection:
    """Process a documentation markdown file."""
    content = file_path.read_text()
    try:
        rel_path = str(file_path.relative_to(base_path / "docs"))
    except ValueError:
        rel_path = str(file_path.relative_to(base_path))

    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem.replace('_', ' ').title()

    # Link to source symbols
    enhanced_content, links = link_documentation_to_source(content, symbols)

    # Convert links to symbols
    section_symbols = []
    for link in links:
        for sym in symbols.values():
            if sym.file_path == link.file_path and sym.line == link.line:
                section_symbols.append(sym)
                break

    return DocSection(
        title=title,
        content=enhanced_content,
        file_path=rel_path,
        level=1,
        symbols=section_symbols
    )


def create_codewiki_section(section: DocSection, symbols: Dict[str, SourceSymbol]) -> str:
    """Create CodeWiki-style markdown for a section."""
    output = f"# {section.title}\n\n"

    # Add content with links
    content = section.content

    # Create links for mentioned symbols
    code_pattern = r'`([A-Z][a-zA-Z0-9_]+(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)`'

    def replace_with_link(match):
        concept = match.group(1)
        key = concept.lower().split('.')[-1]
        if key in symbols:
            sym = symbols[key]
            return f"[`{concept}`]({GITHUB_BASE}/{sym.file_path}#L{sym.line})"
        return f"`{concept}`"

    linked_content = re.sub(code_pattern, replace_with_link, content)
    output += linked_content

    # Add source references section
    if section.symbols:
        output += "\n\n---\n\n## Source References\n\n"
        seen = set()
        for sym in section.symbols:
            key = (sym.name, sym.file_path, sym.line)
            if key not in seen:
                seen.add(key)
                output += f"- [`{sym.name}`]({GITHUB_BASE}/{sym.file_path}#L{sym.line})"
                if sym.docstring:
                    first_line = sym.docstring.split('\n')[0][:80]
                    output += f" - {first_line}"
                output += "\n"

    return output


def generate_link_catalog(symbols: Dict[str, SourceSymbol], output_path: Path):
    """Generate a catalog of all source symbols."""
    content = f"# Docling Source Symbol Catalog\n\n"
    content += f"Generated: {datetime.now().isoformat()}\n\n"
    content += f"Total symbols: {len(symbols)}\n\n"

    # Group by file
    by_file = {}
    for sym in symbols.values():
        if sym.file_path not in by_file:
            by_file[sym.file_path] = []
        by_file[sym.file_path].append(sym)

    content += f"## By File ({len(by_file)} files)\n\n"

    for file_path in sorted(by_file.keys()):
        file_symbols = by_file[file_path]
        content += f"### `{file_path}`\n\n"
        for sym in sorted(file_symbols, key=lambda s: s.line):
            content += f"- Line {sym.line}: `{sym.name}` ({sym.kind})\n"
        content += "\n"

    output_path.write_text(content)
    print(f"Saved symbol catalog to {output_path}")


def main():
    """Build CodeWiki-style output from docling repo."""
    print("=" * 70)
    print("  BUILDING CODEWIKI-STYLE OUTPUT FROM DOCLING REPO")
    print("=" * 70)

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract all source symbols
    print("\n[1/4] Extracting source symbols...")
    symbols = extract_all_symbols(REPO_PATH)
    print(f"  Found {len(symbols)} symbols")

    # Step 2: Process documentation files
    print("\n[2/4] Processing documentation...")
    docs_dir = REPO_PATH / "docs"
    sections = []

    if docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue
            section = process_doc_file(md_file, REPO_PATH, symbols)
            sections.append(section)
            print(f"  Processed: {section.file_path}")
    else:
        print(f"  Docs directory not found: {docs_dir}")

    # Also process README
    readme = REPO_PATH / "README.md"
    if readme.exists():
        section = process_doc_file(readme, REPO_PATH, symbols)
        section.title = "Docling Overview"
        section.file_path = "README.md"
        sections.insert(0, section)

    print(f"  Total sections: {len(sections)}")

    # Step 3: Save CodeWiki-style sections
    print("\n[3/4] Saving CodeWiki-style sections...")
    sections_dir = OUTPUT_PATH / "sections"
    sections_dir.mkdir(exist_ok=True)

    for i, section in enumerate(sections):
        safe_title = re.sub(r'[^\w\s-]', '', section.title)
        safe_title = re.sub(r'\s+', '_', safe_title)[:50]
        filename = f"{i:02d}_{safe_title}.md"

        codewiki_content = create_codewiki_section(section, symbols)
        (sections_dir / filename).write_text(codewiki_content)

    print(f"  Saved {len(sections)} section files")

    # Step 4: Generate catalogs
    print("\n[4/4] Generating catalogs...")
    generate_link_catalog(symbols, OUTPUT_PATH / "symbol_catalog.md")

    # Create combined CodeWiki output
    combined = f"# Docling CodeWiki\n\n"
    combined += f"Generated: {datetime.now().isoformat()}\n\n"
    combined += f"Repository: https://github.com/docling-project/docling\n\n"
    combined += f"---\n\n"

    for section in sections:
        combined += create_codewiki_section(section, symbols)
        combined += "\n\n---\n\n"

    (OUTPUT_PATH / "codewiki_docling.md").write_text(combined)
    print(f"  Saved combined CodeWiki to codewiki_docling.md")

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Sections: {len(sections)}")
    print(f"  Symbols: {len(symbols)}")
    print(f"  Output: {OUTPUT_PATH}")

    # Show key symbols
    key_classes = [s for s in symbols.values() if s.kind == "class"]
    print(f"\n  Key classes ({len(key_classes)}):")
    for sym in sorted(key_classes, key=lambda s: s.name)[:15]:
        print(f"    • {sym.name} ({sym.file_path}:{sym.line})")

    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("  1. Review sections in crawl_output/docling/sections/")
    print("  2. Use symbol_catalog.md for proof-based understanding")
    print("  3. Follow links to validate against source code")


if __name__ == "__main__":
    main()
