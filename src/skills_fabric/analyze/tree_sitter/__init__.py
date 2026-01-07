"""Tree-sitter parsing for multi-language support.

Supports Python, TypeScript, JavaScript, and JSX parsing with graceful
error handling. All parse errors are logged rather than raising exceptions.

Usage:
    from skills_fabric.analyze.tree_sitter import TreeSitterParser, TSSymbol

    parser = TreeSitterParser()
    symbols = parser.parse_file(Path("example.py"))
    # Returns list of TSSymbol with name, kind, file_path, line

CLI Usage:
    python -m skills_fabric.analyze.tree_sitter --file example.py
    python -m skills_fabric.analyze.tree_sitter --directory src/
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from skills_fabric.observability.logging import get_logger

logger = get_logger("analyze.tree_sitter")

__all__ = ["TSSymbol", "TreeSitterParser"]


@dataclass
class TSSymbol:
    """A symbol extracted via Tree-sitter."""
    name: str
    kind: str
    file_path: str
    line: int


class TreeSitterParser:
    """Multi-language parser using Tree-sitter.

    Supports:
    - Python (.py)
    - TypeScript (.ts, .tsx)
    - JavaScript (.js, .jsx)

    Tree-sitter parse errors are handled gracefully with logging.
    """

    SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx"}

    def __init__(self):
        self._parsers = {}
        self._languages = {}

    def _init_python(self) -> bool:
        """Initialize Python parser.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if "python" in self._languages:
            return True
        try:
            import tree_sitter_python as ts_py
            from tree_sitter import Language, Parser
            self._languages["python"] = Language(ts_py.language())
            self._parsers["python"] = Parser(self._languages["python"])
            logger.debug("Python tree-sitter parser initialized")
            return True
        except ImportError as e:
            logger.warning(f"Failed to import tree-sitter-python: {e}")
            return False

    def _init_typescript(self) -> bool:
        """Initialize TypeScript parser.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if "typescript" in self._languages:
            return True
        try:
            import tree_sitter_typescript as ts_ts
            from tree_sitter import Language, Parser
            self._languages["typescript"] = Language(ts_ts.language_typescript())
            self._parsers["typescript"] = Parser(self._languages["typescript"])
            logger.debug("TypeScript tree-sitter parser initialized")
            return True
        except ImportError as e:
            logger.warning(f"Failed to import tree-sitter-typescript: {e}")
            return False

    def _init_tsx(self) -> bool:
        """Initialize TSX parser.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if "tsx" in self._languages:
            return True
        try:
            import tree_sitter_typescript as ts_ts
            from tree_sitter import Language, Parser
            self._languages["tsx"] = Language(ts_ts.language_tsx())
            self._parsers["tsx"] = Parser(self._languages["tsx"])
            logger.debug("TSX tree-sitter parser initialized")
            return True
        except ImportError as e:
            logger.warning(f"Failed to import tree-sitter-typescript (tsx): {e}")
            return False

    def _init_javascript(self) -> bool:
        """Initialize JavaScript parser.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if "javascript" in self._languages:
            return True
        try:
            import tree_sitter_javascript as ts_js
            from tree_sitter import Language, Parser
            self._languages["javascript"] = Language(ts_js.language())
            self._parsers["javascript"] = Parser(self._languages["javascript"])
            logger.debug("JavaScript tree-sitter parser initialized")
            return True
        except ImportError as e:
            logger.warning(f"Failed to import tree-sitter-javascript: {e}")
            return False

    def _get_language_for_file(self, file_path: Path) -> Optional[str]:
        """Determine the language based on file extension.

        Args:
            file_path: Path to the source file.

        Returns:
            Language name or None if unsupported.
        """
        ext = file_path.suffix.lower()

        if ext == ".py":
            return "python" if self._init_python() else None
        elif ext == ".ts":
            return "typescript" if self._init_typescript() else None
        elif ext == ".tsx":
            return "tsx" if self._init_tsx() else None
        elif ext in (".js", ".jsx"):
            return "javascript" if self._init_javascript() else None

        return None

    def parse_file(self, file_path: Path) -> list[TSSymbol]:
        """Parse a source file and extract symbols.

        Args:
            file_path: Path to the source file to parse.

        Returns:
            List of extracted symbols. Empty list if parsing fails or
            file type is not supported.
        """
        symbols = []

        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.debug(f"Unsupported file extension: {file_path.suffix}")
            return symbols

        # Initialize appropriate language parser
        language = self._get_language_for_file(file_path)
        if language is None:
            logger.warning(f"Could not initialize parser for: {file_path}")
            return symbols

        parser = self._parsers.get(language)
        if parser is None:
            logger.warning(f"No parser available for language: {language}")
            return symbols

        # Read file as bytes (required by tree-sitter)
        try:
            with open(file_path, "rb") as f:
                source = f.read()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return symbols
        except IOError as e:
            logger.warning(f"IO error reading {file_path}: {e}")
            return symbols

        # Parse with tree-sitter, handling ParseError gracefully
        try:
            tree = parser.parse(source)
        except Exception as e:
            # Handle tree_sitter.ParseError and any other parsing exceptions
            error_type = type(e).__name__
            logger.warning(
                f"Tree-sitter parse error for {file_path}: [{error_type}] {e}"
            )
            return symbols

        rel_path = str(file_path)

        # Traverse the AST and extract symbols
        def traverse(node, depth=0):
            """Recursively traverse the AST to extract symbols."""
            # Python: class_definition, function_definition
            # TypeScript/JavaScript: class_declaration, function_declaration,
            #                        method_definition, arrow_function

            if node.type in ("class_declaration", "class_definition"):
                name = self._extract_identifier(node, ["identifier", "type_identifier"])
                if name:
                    symbols.append(TSSymbol(
                        name=name,
                        kind="class",
                        file_path=rel_path,
                        line=node.start_point[0] + 1
                    ))

            elif node.type in (
                "function_declaration",
                "function_definition",
                "method_definition",
                "generator_function_declaration",
            ):
                name = self._extract_identifier(node, ["identifier", "property_identifier"])
                if name:
                    symbols.append(TSSymbol(
                        name=name,
                        kind="function",
                        file_path=rel_path,
                        line=node.start_point[0] + 1
                    ))

            # Handle arrow functions assigned to variables (common in JS/JSX)
            elif node.type == "lexical_declaration":
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = None
                        has_arrow = False
                        for subchild in child.children:
                            if subchild.type == "identifier":
                                name_node = subchild
                            elif subchild.type == "arrow_function":
                                has_arrow = True
                        if name_node and has_arrow:
                            symbols.append(TSSymbol(
                                name=name_node.text.decode(),
                                kind="function",
                                file_path=rel_path,
                                line=child.start_point[0] + 1
                            ))

            # Recurse into children
            for child in node.children:
                traverse(child, depth + 1)

        try:
            traverse(tree.root_node)
        except Exception as e:
            logger.warning(f"Error traversing AST for {file_path}: {e}")

        logger.debug(f"Extracted {len(symbols)} symbols from {file_path}")
        return symbols

    def _extract_identifier(self, node, identifier_types: list[str]) -> Optional[str]:
        """Extract the identifier name from a node.

        Args:
            node: The tree-sitter node.
            identifier_types: List of node types to look for.

        Returns:
            The identifier name or None.
        """
        for child in node.children:
            if child.type in identifier_types:
                return child.text.decode()
        return None

    def parse_directory(self, dir_path: Path) -> list[TSSymbol]:
        """Parse all supported files in a directory.

        Args:
            dir_path: Path to the directory to scan.

        Returns:
            List of all extracted symbols from supported files.
        """
        all_symbols = []

        for ext in self.SUPPORTED_EXTENSIONS:
            for source_file in dir_path.rglob(f"*{ext}"):
                # Skip common non-source directories
                path_str = str(source_file)
                if any(skip in path_str for skip in [
                    "__pycache__", ".venv", "node_modules", ".git", "dist", "build"
                ]):
                    continue

                symbols = self.parse_file(source_file)
                all_symbols.extend(symbols)

        logger.info(f"Parsed {len(all_symbols)} symbols from {dir_path}")
        return all_symbols

    def is_supported(self, file_path: Path) -> bool:
        """Check if a file type is supported by this parser.

        Args:
            file_path: Path to check.

        Returns:
            True if the file extension is supported.
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
