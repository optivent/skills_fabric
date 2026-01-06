#!/usr/bin/env python3
"""
Build CodeWiki-style output for LangGraph repository.
Extracts documentation sections and links them to source symbols.
"""

import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import json


@dataclass
class SourceSymbol:
    """A symbol extracted from source code."""
    name: str
    kind: str  # 'class', 'function', 'method', 'constant'
    file_path: str
    line: int
    docstring: str = ""
    parent: Optional[str] = None  # For methods, the class name
    module: str = ""  # Which langgraph module (langgraph, checkpoint, prebuilt, etc.)


@dataclass
class DocSection:
    """A documentation section from markdown files."""
    title: str
    file_path: str
    content: str
    level: int  # Heading level (1-6)
    subsections: List['DocSection'] = field(default_factory=list)


def get_commit_hash(repo_path: Path) -> str:
    """Get the current commit hash of the repo."""
    git_head = repo_path / ".git" / "HEAD"
    if git_head.exists():
        ref = git_head.read_text().strip()
        if ref.startswith("ref: "):
            ref_path = repo_path / ".git" / ref[5:]
            if ref_path.exists():
                return ref_path.read_text().strip()[:12]
        return ref[:12]
    return "main"


def extract_symbols_from_file(file_path: Path, base_path: Path, module_name: str) -> List[SourceSymbol]:
    """Extract all classes, functions, and methods from a Python file."""
    symbols = []

    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return symbols

    rel_path = str(file_path.relative_to(base_path))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node) or ""
            symbols.append(SourceSymbol(
                name=node.name,
                kind='class',
                file_path=rel_path,
                line=node.lineno,
                docstring=docstring[:200] if docstring else "",
                module=module_name
            ))

            # Extract methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                    method_doc = ast.get_docstring(item) or ""
                    symbols.append(SourceSymbol(
                        name=item.name,
                        kind='method',
                        file_path=rel_path,
                        line=item.lineno,
                        docstring=method_doc[:200] if method_doc else "",
                        parent=node.name,
                        module=module_name
                    ))

        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            # Top-level functions only
            if any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                # Skip if it's a method (already handled)
                pass
            docstring = ast.get_docstring(node) or ""
            symbols.append(SourceSymbol(
                name=node.name,
                kind='function',
                file_path=rel_path,
                line=node.lineno,
                docstring=docstring[:200] if docstring else "",
                module=module_name
            ))

    return symbols


def parse_markdown_sections(file_path: Path, base_path: Path) -> List[DocSection]:
    """Parse markdown file into sections by headings."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return []

    try:
        rel_path = str(file_path.relative_to(base_path / "docs"))
    except ValueError:
        rel_path = str(file_path.relative_to(base_path))

    sections = []
    current_section = None
    current_content = []

    for line in content.split('\n'):
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if heading_match:
            # Save previous section
            if current_section:
                current_section.content = '\n'.join(current_content).strip()
                sections.append(current_section)

            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()

            current_section = DocSection(
                title=title,
                file_path=rel_path,
                content="",
                level=level
            )
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        current_section.content = '\n'.join(current_content).strip()
        sections.append(current_section)

    return sections


def find_related_symbols(section: DocSection, symbols: Dict[str, SourceSymbol]) -> List[SourceSymbol]:
    """Find symbols mentioned in a documentation section."""
    related = []
    text = f"{section.title} {section.content}".lower()

    # Key patterns to look for
    patterns = [
        r'`([A-Z][a-zA-Z0-9_]+)`',  # Class names in backticks
        r'`([a-z_][a-zA-Z0-9_]+)\(`',  # Function calls in backticks
        r'class\s+`?([A-Z][a-zA-Z0-9_]+)`?',  # Class mentions
        r'function\s+`?([a-z_][a-zA-Z0-9_]+)`?',  # Function mentions
    ]

    mentioned = set()
    full_text = f"{section.title} {section.content}"

    for pattern in patterns:
        for match in re.finditer(pattern, full_text):
            mentioned.add(match.group(1))

    # Also check for exact symbol name matches
    for name, symbol in symbols.items():
        if name in mentioned or name.lower() in text:
            related.append(symbol)

    return related[:10]  # Limit to top 10


def create_codewiki_section(section: DocSection, symbols: Dict[str, SourceSymbol],
                            commit: str, repo: str = "langchain-ai/langgraph") -> str:
    """Create CodeWiki-style markdown with embedded source links."""
    lines = [f"## {section.title}", ""]

    if section.content:
        # Process content to add source links
        content = section.content

        # Find related symbols
        related = find_related_symbols(section, symbols)

        lines.append(content)
        lines.append("")

        if related:
            lines.append("### Source References")
            lines.append("")
            for sym in related:
                if sym.parent:
                    display = f"{sym.parent}.{sym.name}"
                else:
                    display = sym.name

                link = f"https://github.com/{repo}/blob/{commit}/{sym.file_path}#L{sym.line}"
                lines.append(f"- [`{display}`]({link}) ({sym.kind} in {sym.module})")
            lines.append("")

    return '\n'.join(lines)


def build_codewiki(repo_path: Path, output_dir: Path):
    """Build complete CodeWiki-style documentation."""
    print(f"Building CodeWiki for LangGraph from {repo_path}")

    commit = get_commit_hash(repo_path)
    print(f"Commit: {commit}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    sections_dir = output_dir / "sections"
    sections_dir.mkdir(exist_ok=True)

    # Extract symbols from all modules
    all_symbols: Dict[str, SourceSymbol] = {}
    module_counts = {}

    libs_path = repo_path / "libs"
    for module_dir in libs_path.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith('.'):
            module_name = module_dir.name
            module_counts[module_name] = 0

            for py_file in module_dir.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                symbols = extract_symbols_from_file(py_file, repo_path, module_name)
                for sym in symbols:
                    key = f"{sym.parent}.{sym.name}" if sym.parent else sym.name
                    all_symbols[key] = sym
                    module_counts[module_name] += 1

    print(f"Extracted {len(all_symbols)} symbols from {len(module_counts)} modules")
    for mod, count in sorted(module_counts.items(), key=lambda x: -x[1]):
        print(f"  {mod}: {count} symbols")

    # Parse documentation sections
    all_sections: List[DocSection] = []
    docs_path = repo_path / "docs"

    for md_file in docs_path.rglob("*.md"):
        sections = parse_markdown_sections(md_file, repo_path)
        all_sections.extend(sections)

    print(f"Parsed {len(all_sections)} documentation sections")

    # Generate CodeWiki-style output
    combined_output = [
        "# LangGraph CodeWiki",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Commit: {commit}",
        f"Repository: langchain-ai/langgraph",
        "",
        f"Total symbols: {len(all_symbols)}",
        f"Total sections: {len(all_sections)}",
        "",
        "---",
        ""
    ]

    # Group sections by file
    sections_by_file: Dict[str, List[DocSection]] = {}
    for section in all_sections:
        if section.file_path not in sections_by_file:
            sections_by_file[section.file_path] = []
        sections_by_file[section.file_path].append(section)

    # Write individual section files
    section_index = 0
    for file_path, sections in sorted(sections_by_file.items()):
        for section in sections:
            codewiki_content = create_codewiki_section(section, all_symbols, commit)
            combined_output.append(codewiki_content)

            # Write individual section file
            safe_title = re.sub(r'[^\w\s-]', '', section.title)[:50].strip()
            section_file = sections_dir / f"{section_index:03d}_{safe_title.replace(' ', '_')}.md"
            section_file.write_text(codewiki_content, encoding='utf-8')
            section_index += 1

    # Write combined output
    combined_file = output_dir / "codewiki_langgraph.md"
    combined_file.write_text('\n'.join(combined_output), encoding='utf-8')
    print(f"Written combined CodeWiki to {combined_file}")

    # Write symbol catalog
    catalog_lines = [
        "# LangGraph Source Symbol Catalog",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        f"Total symbols: {len(all_symbols)}",
        "",
        "## Symbols by Module",
        ""
    ]

    # Group by module
    by_module: Dict[str, List[SourceSymbol]] = {}
    for sym in all_symbols.values():
        if sym.module not in by_module:
            by_module[sym.module] = []
        by_module[sym.module].append(sym)

    for module, syms in sorted(by_module.items()):
        catalog_lines.append(f"### {module}")
        catalog_lines.append("")

        # Group by kind
        classes = [s for s in syms if s.kind == 'class']
        functions = [s for s in syms if s.kind == 'function']
        methods = [s for s in syms if s.kind == 'method']

        if classes:
            catalog_lines.append("#### Classes")
            for sym in sorted(classes, key=lambda x: x.name):
                link = f"https://github.com/langchain-ai/langgraph/blob/{commit}/{sym.file_path}#L{sym.line}"
                catalog_lines.append(f"- [`{sym.name}`]({link})")
                if sym.docstring:
                    catalog_lines.append(f"  - {sym.docstring[:100]}...")
            catalog_lines.append("")

        if functions:
            catalog_lines.append("#### Functions")
            for sym in sorted(functions, key=lambda x: x.name)[:50]:  # Limit per module
                link = f"https://github.com/langchain-ai/langgraph/blob/{commit}/{sym.file_path}#L{sym.line}"
                catalog_lines.append(f"- [`{sym.name}`]({link})")
            if len(functions) > 50:
                catalog_lines.append(f"  ... and {len(functions) - 50} more functions")
            catalog_lines.append("")

    catalog_file = output_dir / "symbol_catalog.md"
    catalog_file.write_text('\n'.join(catalog_lines), encoding='utf-8')
    print(f"Written symbol catalog to {catalog_file}")

    # Write summary stats
    stats = {
        "commit": commit,
        "total_symbols": len(all_symbols),
        "total_sections": len(all_sections),
        "modules": module_counts,
        "docs_files": len(sections_by_file),
        "generated": datetime.now().isoformat()
    }

    stats_file = output_dir / "stats.json"
    stats_file.write_text(json.dumps(stats, indent=2), encoding='utf-8')

    print(f"\nCodeWiki build complete!")
    print(f"  Sections: {section_index}")
    print(f"  Symbols: {len(all_symbols)}")
    print(f"  Output: {output_dir}")


if __name__ == "__main__":
    repo_path = Path("/home/user/skills_fabric/langgraph_repo")
    output_dir = Path("/home/user/skills_fabric/crawl_output/langgraph")

    if not repo_path.exists():
        print(f"Error: Repository not found at {repo_path}")
        print("Please clone LangGraph first:")
        print("  git clone https://github.com/langchain-ai/langgraph.git langgraph_repo")
        exit(1)

    build_codewiki(repo_path, output_dir)
