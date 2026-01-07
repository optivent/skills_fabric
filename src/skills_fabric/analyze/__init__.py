"""Code analysis modules for skills_fabric.

This package provides various code analysis tools:
- ast_parser: Python AST parsing with rich metadata extraction
- tree_sitter: Multi-language parsing using Tree-sitter
- lsp_client: Language Server Protocol client
- symbol_graph: Symbol relationship graph building

Symbol Types:
- EnhancedSymbol: Rich symbol with full metadata (params, docstring, decorators, calls)
- Symbol: Basic symbol with name, kind, file_path, line (backwards compatible)
- TSSymbol: Tree-sitter symbol for multi-language parsing (convertible to EnhancedSymbol)

Usage:
    from skills_fabric.analyze import EnhancedSymbol, ASTParser, TreeSitterParser

    # Python AST parsing (rich metadata)
    ast_parser = ASTParser()
    symbols = ast_parser.parse_file(Path("example.py"))  # Returns EnhancedSymbol

    # Multi-language parsing (Python, TypeScript, JavaScript)
    ts_parser = TreeSitterParser()
    ts_symbols = ts_parser.parse_file(Path("example.ts"))  # Returns TSSymbol
    enhanced = ts_symbols[0].to_enhanced()  # Convert to EnhancedSymbol
"""

from skills_fabric.analyze.ast_parser import (
    ASTParser,
    EnhancedSymbol,
    Parameter,
    Symbol,
    parse_python_file,
    parse_python_directory,
)
from skills_fabric.analyze.tree_sitter import (
    TreeSitterParser,
    TSSymbol,
)

__all__ = [
    # AST Parser
    "ASTParser",
    "EnhancedSymbol",
    "Parameter",
    "Symbol",
    "parse_python_file",
    "parse_python_directory",
    # Tree-sitter Parser
    "TreeSitterParser",
    "TSSymbol",
]
