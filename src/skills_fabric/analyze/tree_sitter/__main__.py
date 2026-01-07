"""CLI interface for Tree-sitter parsing module.

Usage:
    python -m skills_fabric.analyze.tree_sitter --file example.py
    python -m skills_fabric.analyze.tree_sitter --directory src/
    python -m skills_fabric.analyze.tree_sitter --file example.ts --output json

Examples:
    # Parse a single Python file
    python -m skills_fabric.analyze.tree_sitter --file src/skills_fabric/analyze/tree_sitter.py

    # Parse all files in a directory
    python -m skills_fabric.analyze.tree_sitter --directory src/skills_fabric/

    # Output as JSON for programmatic use
    python -m skills_fabric.analyze.tree_sitter --file example.py --output json
"""

import argparse
import json
import sys
from pathlib import Path

from skills_fabric.analyze.tree_sitter import TreeSitterParser, TSSymbol


def format_symbol_text(symbol: TSSymbol) -> str:
    """Format a symbol for text output.

    Args:
        symbol: The TSSymbol to format.

    Returns:
        Formatted string representation.
    """
    return f"  {symbol.kind:10} {symbol.name:40} {symbol.file_path}:{symbol.line}"


def format_symbols_table(symbols: list[TSSymbol]) -> str:
    """Format symbols as a readable text table.

    Args:
        symbols: List of symbols to format.

    Returns:
        Formatted table string.
    """
    if not symbols:
        return "No symbols found."

    lines = []
    lines.append(f"{'Kind':10} {'Name':40} Location")
    lines.append("-" * 80)

    for symbol in symbols:
        lines.append(format_symbol_text(symbol))

    lines.append("-" * 80)
    lines.append(f"Total: {len(symbols)} symbol(s)")

    return "\n".join(lines)


def symbols_to_dict(symbols: list[TSSymbol]) -> list[dict]:
    """Convert symbols to dictionary representation.

    Args:
        symbols: List of TSSymbol objects.

    Returns:
        List of dictionaries suitable for JSON serialization.
    """
    return [
        {
            "name": s.name,
            "kind": s.kind,
            "file_path": s.file_path,
            "line": s.line,
        }
        for s in symbols
    ]


def main() -> int:
    """Main entry point for tree-sitter CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        prog="python -m skills_fabric.analyze.tree_sitter",
        description="Parse source files using Tree-sitter and extract symbol information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single Python file
  %(prog)s --file src/example.py

  # Parse a TypeScript file
  %(prog)s --file components/App.tsx

  # Parse all supported files in a directory
  %(prog)s --directory src/

  # Output as JSON
  %(prog)s --file example.py --output json

  # Filter by symbol kind
  %(prog)s --file example.py --kind class

Supported file types:
  Python:     .py
  TypeScript: .ts, .tsx
  JavaScript: .js, .jsx
        """
    )

    # Input source arguments
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--file", "-f",
        type=Path,
        help="Path to a single source file to parse"
    )
    source_group.add_argument(
        "--directory", "-d",
        type=Path,
        help="Path to a directory to recursively parse"
    )

    # Output format
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' (readable table) or 'json' (machine-readable)"
    )

    # Filter options
    parser.add_argument(
        "--kind", "-k",
        choices=["class", "function"],
        help="Filter symbols by kind (class or function)"
    )

    # Verbosity
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages, only show results"
    )

    args = parser.parse_args()

    # Initialize parser
    ts_parser = TreeSitterParser()

    # Parse source(s)
    symbols: list[TSSymbol] = []

    if args.file:
        file_path = args.file.resolve()

        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            return 1

        if not file_path.is_file():
            print(f"Error: Path is not a file: {file_path}", file=sys.stderr)
            return 1

        if not ts_parser.is_supported(file_path):
            print(
                f"Error: Unsupported file type: {file_path.suffix}. "
                f"Supported: {', '.join(sorted(TreeSitterParser.SUPPORTED_EXTENSIONS))}",
                file=sys.stderr
            )
            return 1

        if not args.quiet:
            print(f"Parsing: {file_path}", file=sys.stderr)

        symbols = ts_parser.parse_file(file_path)

    elif args.directory:
        dir_path = args.directory.resolve()

        if not dir_path.exists():
            print(f"Error: Directory not found: {dir_path}", file=sys.stderr)
            return 1

        if not dir_path.is_dir():
            print(f"Error: Path is not a directory: {dir_path}", file=sys.stderr)
            return 1

        if not args.quiet:
            print(f"Scanning directory: {dir_path}", file=sys.stderr)

        symbols = ts_parser.parse_directory(dir_path)

    # Apply filters
    if args.kind:
        symbols = [s for s in symbols if s.kind == args.kind]

    # Format output
    if args.output == "json":
        result = {
            "symbols": symbols_to_dict(symbols),
            "count": len(symbols),
        }
        if args.file:
            result["source"] = str(args.file)
        elif args.directory:
            result["source"] = str(args.directory)

        print(json.dumps(result, indent=2))
    else:
        # Text output
        if args.file:
            print(f"\nSymbols in {args.file}:\n")
        elif args.directory:
            print(f"\nSymbols in {args.directory}:\n")

        print(format_symbols_table(symbols))

    return 0


if __name__ == "__main__":
    sys.exit(main())
