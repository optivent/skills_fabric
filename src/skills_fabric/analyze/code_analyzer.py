"""Unified code analyzer with LSP-to-AST graceful degradation.

Provides a unified interface for code analysis that:
1. Tries LSP for rich code intelligence (hover, definitions, references)
2. Falls back to AST/Tree-sitter parsing when LSP is unavailable
3. Logs warnings about degraded mode operation

This ensures code analysis always works, even without LSP servers installed.

Usage:
    from skills_fabric.analyze import CodeAnalyzer

    # Create analyzer with automatic fallback
    analyzer = CodeAnalyzer(project_path=Path("/path/to/project"))

    # Get symbols from a file (uses best available method)
    symbols = analyzer.get_symbols(Path("example.py"))

    # Get type information (LSP if available, otherwise from AST)
    hover = analyzer.get_hover_info(Path("example.py"), line=10, col=5)

    # Check if running in degraded mode
    if analyzer.is_degraded:
        print("Running in AST-only mode (LSP unavailable)")
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from skills_fabric.analyze.ast_parser import ASTParser, EnhancedSymbol, Parameter
from skills_fabric.analyze.tree_sitter import TreeSitterParser, TSSymbol
from skills_fabric.analyze.lsp_client import LSPClient, HoverInfo, Location, LSPSymbol
from skills_fabric.observability.logging import get_logger

logger = get_logger("analyze.code_analyzer")


class AnalysisMode(Enum):
    """Analysis mode indicator."""
    LSP = "lsp"          # Full LSP capabilities available
    AST_ONLY = "ast"     # Degraded to AST-only analysis
    TREE_SITTER = "tree_sitter"  # Using tree-sitter for non-Python files


@dataclass
class AnalysisResult:
    """Result from code analysis with source tracking.

    Tracks which analysis method was used and provides appropriate
    fallback information when LSP is unavailable.
    """
    mode: AnalysisMode
    symbols: list[EnhancedSymbol] = field(default_factory=list)
    hover_info: Optional[str] = None
    definition_location: Optional[str] = None  # file:line citation
    references: list[str] = field(default_factory=list)  # file:line citations
    warning: Optional[str] = None  # Degradation warning if applicable


class CodeAnalyzer:
    """Unified code analyzer with graceful LSP-to-AST degradation.

    Provides consistent code analysis across different environments by:
    - Attempting to use LSP for rich type information
    - Automatically falling back to AST parsing when LSP unavailable
    - Using Tree-sitter for multi-language support
    - Logging clear warnings about degraded operation

    The analyzer is stateful and manages LSP server lifecycle.

    Attributes:
        project_path: Root path of the project being analyzed
        is_degraded: True if running in AST-only mode (LSP unavailable)
        mode: Current analysis mode (LSP, AST_ONLY, or TREE_SITTER)
    """

    def __init__(
        self,
        project_path: Optional[Path] = None,
        language: str = "python",
        try_lsp: bool = True
    ):
        """Initialize the code analyzer.

        Args:
            project_path: Root of the project (required for LSP).
                If None, LSP is disabled and only AST analysis is used.
            language: Primary language for LSP server (python or typescript).
            try_lsp: If True, attempt to start LSP server. If False,
                skip LSP and use AST-only mode directly.
        """
        self._project_path = project_path
        self._language = language
        self._lsp_client: Optional[LSPClient] = None
        self._ast_parser = ASTParser()
        self._tree_sitter_parser = TreeSitterParser()
        self._mode = AnalysisMode.AST_ONLY
        self._lsp_tried = False
        self._degradation_logged = False

        if try_lsp and project_path:
            self._initialize_lsp()

    def _initialize_lsp(self) -> bool:
        """Attempt to initialize LSP server.

        Returns:
            True if LSP is available, False otherwise.
        """
        if self._lsp_tried:
            return self._mode == AnalysisMode.LSP

        self._lsp_tried = True

        try:
            self._lsp_client = LSPClient()
            if self._lsp_client.start_server(self._project_path, self._language):
                self._mode = AnalysisMode.LSP
                logger.info(
                    f"LSP server started successfully for {self._language}"
                )
                return True
            else:
                self._log_degradation("LSP server failed to initialize")
                self._lsp_client = None
                return False
        except Exception as e:
            self._log_degradation(f"LSP initialization error: {e}")
            self._lsp_client = None
            return False

    def _log_degradation(self, reason: str) -> None:
        """Log warning about degraded mode operation.

        Only logs once per session to avoid log spam.

        Args:
            reason: Reason for degradation
        """
        if not self._degradation_logged:
            self._degradation_logged = True
            logger.warning(
                f"Code analysis degraded to AST-only mode: {reason}. "
                "Type information and cross-references may be limited."
            )

    @property
    def is_degraded(self) -> bool:
        """Check if running in degraded (AST-only) mode.

        Returns:
            True if LSP is unavailable and using AST fallback.
        """
        return self._mode != AnalysisMode.LSP

    @property
    def mode(self) -> AnalysisMode:
        """Get the current analysis mode.

        Returns:
            Current AnalysisMode (LSP, AST_ONLY, or TREE_SITTER).
        """
        return self._mode

    @property
    def lsp_available(self) -> bool:
        """Check if LSP server is available and running.

        Returns:
            True if LSP client is connected and responding.
        """
        return (
            self._lsp_client is not None
            and self._lsp_client.is_available
        )

    def get_symbols(
        self,
        file_path: Path,
        use_tree_sitter: bool = False
    ) -> list[EnhancedSymbol]:
        """Extract symbols from a source file.

        Uses the best available method:
        - For Python files: AST parser for rich metadata
        - For other languages: Tree-sitter parser
        - Falls back gracefully if parsing fails

        Args:
            file_path: Path to the source file.
            use_tree_sitter: Force tree-sitter parsing even for Python files.

        Returns:
            List of EnhancedSymbol with available metadata.
        """
        suffix = file_path.suffix.lower()

        # Determine which parser to use
        if suffix == ".py" and not use_tree_sitter:
            # Python: Use AST parser for rich metadata
            symbols = self._ast_parser.parse_file_enhanced(file_path)
            if symbols:
                logger.debug(
                    f"Extracted {len(symbols)} symbols from {file_path} using AST"
                )
            return symbols

        # Non-Python or forced tree-sitter: Use tree-sitter
        if self._tree_sitter_parser.is_supported(file_path):
            ts_symbols = self._tree_sitter_parser.parse_file(file_path)
            # Convert to EnhancedSymbol for unified interface
            symbols = [sym.to_enhanced() for sym in ts_symbols]
            if symbols:
                logger.debug(
                    f"Extracted {len(symbols)} symbols from {file_path} using Tree-sitter"
                )
            return symbols

        logger.debug(f"No parser available for file type: {suffix}")
        return []

    def get_hover_info(
        self,
        file_path: Path,
        line: int,
        col: int
    ) -> AnalysisResult:
        """Get type/documentation info at a position.

        Tries LSP first for rich hover information, falls back to
        finding the symbol at the position using AST.

        Args:
            file_path: Path to the source file.
            line: Line number (0-indexed).
            col: Column number (0-indexed).

        Returns:
            AnalysisResult with hover information or AST fallback.
        """
        result = AnalysisResult(mode=self._mode)

        # Try LSP first
        if self.lsp_available:
            try:
                hover = self._lsp_client.get_hover(file_path, line, col)
                if hover:
                    result.hover_info = hover.content
                    result.mode = AnalysisMode.LSP
                    return result
            except Exception as e:
                logger.debug(f"LSP hover failed, falling back to AST: {e}")
                self._log_degradation(f"LSP hover error: {e}")

        # Fallback: Find symbol at position using AST
        result.mode = AnalysisMode.AST_ONLY
        result.warning = "LSP unavailable - showing symbol info from AST"

        symbols = self.get_symbols(file_path)
        for symbol in symbols:
            # Check if the position is within this symbol's range
            # Line numbers in AST are 1-indexed, input is 0-indexed
            if symbol.line - 1 <= line:
                end_line = symbol.end_line or symbol.line
                if line <= end_line - 1:
                    # Found a symbol containing this position
                    hover_parts = [f"**{symbol.kind}** `{symbol.qualified_name}`"]
                    if symbol.signature:
                        hover_parts.append(f"```python\n{symbol.signature}\n```")
                    if symbol.docstring:
                        hover_parts.append(symbol.docstring)
                    result.hover_info = "\n\n".join(hover_parts)
                    break

        return result

    def get_definition(
        self,
        file_path: Path,
        line: int,
        col: int
    ) -> AnalysisResult:
        """Get definition location for a symbol.

        Tries LSP first for accurate go-to-definition, falls back to
        AST-based symbol search.

        Args:
            file_path: Path to the source file.
            line: Line number (0-indexed).
            col: Column number (0-indexed).

        Returns:
            AnalysisResult with definition location or AST fallback.
        """
        result = AnalysisResult(mode=self._mode)

        # Try LSP first
        if self.lsp_available:
            try:
                self._lsp_client.open_document(file_path)
                location = self._lsp_client.get_definition(file_path, line, col)
                self._lsp_client.close_document(file_path)

                if location:
                    result.definition_location = location.to_citation()
                    result.mode = AnalysisMode.LSP
                    return result
            except Exception as e:
                logger.debug(f"LSP definition failed, falling back to AST: {e}")
                self._log_degradation(f"LSP definition error: {e}")

        # Fallback: AST can only provide definitions within the same file
        result.mode = AnalysisMode.AST_ONLY
        result.warning = (
            "LSP unavailable - definition search limited to current file. "
            "Cross-file navigation requires LSP."
        )

        # For AST, we can at least find symbols in the same file
        symbols = self.get_symbols(file_path)
        for symbol in symbols:
            if symbol.line - 1 <= line <= (symbol.end_line or symbol.line) - 1:
                result.definition_location = f"{file_path}:{symbol.line}"
                break

        return result

    def get_references(
        self,
        file_path: Path,
        line: int,
        col: int,
        include_declaration: bool = True
    ) -> AnalysisResult:
        """Find all references to a symbol.

        Tries LSP first for cross-file references, falls back to
        AST-based same-file search.

        Args:
            file_path: Path to the source file.
            line: Line number (0-indexed).
            col: Column number (0-indexed).
            include_declaration: Include the declaration in results.

        Returns:
            AnalysisResult with reference locations or AST fallback.
        """
        result = AnalysisResult(mode=self._mode)

        # Try LSP first
        if self.lsp_available:
            try:
                self._lsp_client.open_document(file_path)
                refs = self._lsp_client.find_references(
                    file_path, line, col,
                    include_declaration=include_declaration
                )
                self._lsp_client.close_document(file_path)

                if refs:
                    result.references = refs
                    result.mode = AnalysisMode.LSP
                    return result
            except Exception as e:
                logger.debug(f"LSP references failed, falling back to AST: {e}")
                self._log_degradation(f"LSP references error: {e}")

        # Fallback: AST cannot find cross-file references
        result.mode = AnalysisMode.AST_ONLY
        result.warning = (
            "LSP unavailable - cross-file references not available. "
            "Only same-file symbol definitions found."
        )

        # For AST, we can only list symbols in the same file
        # This is a severe limitation but better than nothing
        symbols = self.get_symbols(file_path)
        result.references = [
            f"{file_path}:{sym.line}" for sym in symbols
            if sym.line - 1 <= line <= (sym.end_line or sym.line) - 1
        ]

        return result

    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Perform comprehensive analysis of a file.

        Extracts all symbols with available metadata using the best
        available method.

        Args:
            file_path: Path to the source file.

        Returns:
            AnalysisResult with all extracted symbols.
        """
        result = AnalysisResult(mode=self._mode)
        result.symbols = self.get_symbols(file_path)

        if self.is_degraded:
            result.warning = (
                "Running in AST-only mode. Type information may be limited. "
                "Install pylsp for richer analysis."
            )

        return result

    def analyze_directory(
        self,
        dir_path: Path,
        extensions: Optional[set[str]] = None
    ) -> AnalysisResult:
        """Analyze all source files in a directory.

        Args:
            dir_path: Path to the directory.
            extensions: File extensions to include (default: .py, .ts, .js, etc.)

        Returns:
            AnalysisResult with symbols from all files.
        """
        if extensions is None:
            extensions = {".py", ".ts", ".tsx", ".js", ".jsx"}

        result = AnalysisResult(mode=self._mode)
        all_symbols = []

        for ext in extensions:
            for source_file in dir_path.rglob(f"*{ext}"):
                # Skip common non-source directories
                path_str = str(source_file)
                if any(skip in path_str for skip in [
                    "__pycache__", ".venv", "node_modules", ".git", "dist", "build"
                ]):
                    continue

                symbols = self.get_symbols(source_file)
                all_symbols.extend(symbols)

        result.symbols = all_symbols
        logger.info(
            f"Analyzed {len(all_symbols)} symbols from {dir_path} "
            f"(mode: {self._mode.value})"
        )

        if self.is_degraded:
            result.warning = (
                f"Analyzed {len(all_symbols)} symbols in AST-only mode. "
                "Some type information may be missing."
            )

        return result

    def close(self) -> None:
        """Clean up resources and stop LSP server."""
        if self._lsp_client:
            try:
                self._lsp_client.stop_server()
            except Exception as e:
                logger.debug(f"Error stopping LSP server: {e}")
            self._lsp_client = None
        self._mode = AnalysisMode.AST_ONLY

    def __enter__(self) -> "CodeAnalyzer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - clean up resources."""
        self.close()


def analyze_file_with_fallback(
    file_path: Path,
    project_path: Optional[Path] = None
) -> AnalysisResult:
    """Convenience function to analyze a single file with automatic fallback.

    Creates a temporary CodeAnalyzer, analyzes the file, and cleans up.

    Args:
        file_path: Path to the file to analyze.
        project_path: Optional project root for LSP initialization.

    Returns:
        AnalysisResult with extracted symbols and any warnings.

    Example:
        >>> result = analyze_file_with_fallback(Path("example.py"))
        >>> if result.warning:
        ...     print(f"Warning: {result.warning}")
        >>> for symbol in result.symbols:
        ...     print(f"{symbol.kind}: {symbol.name} at line {symbol.line}")
    """
    with CodeAnalyzer(project_path=project_path, try_lsp=project_path is not None) as analyzer:
        return analyzer.analyze_file(file_path)
