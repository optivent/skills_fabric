"""Hard Content Verification - Trust Level 1 (100% Trust).

Verifies content using methods that involve ZERO LLM:
- AST parsing: Extract symbols from Python AST
- SCIP indexing: Compiler-grade semantic analysis
- Regex extraction: Pattern-based extraction from source
- File verification: Check if paths point to real files

BMAD Principle:
> "HardContent has 100% trust because it comes directly from
>  the source code with no LLM interpretation."
"""
import ast
import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from .hierarchy import (
    TrustResult,
    TrustLevel,
    hard_content_result,
    unverified_result,
)


@dataclass
class VerifiedSymbol:
    """A symbol verified through AST parsing."""
    name: str
    kind: str  # function, class, method, variable
    file_path: str
    line: int
    end_line: Optional[int] = None
    signature: Optional[str] = None


class HardContentVerifier:
    """Verifies content is HardContent (Trust Level 1).

    All methods return TrustResult with either:
    - HARD_CONTENT: Verified through non-LLM methods
    - UNVERIFIED: Failed verification, REJECTED
    """

    def verify_file_exists(self, path: str) -> TrustResult:
        """Verify a file path points to a real file.

        This is the most basic HardContent check - the file exists.
        """
        if not path:
            return unverified_result(
                source="file_check",
                rejection_reason="Empty file path"
            )

        # Handle file:// URLs
        clean_path = path.replace("file://", "")

        if os.path.isfile(clean_path):
            return hard_content_result(
                source="file_exists",
                grounding_evidence=[f"file:{clean_path}"]
            )

        return unverified_result(
            source="file_check",
            rejection_reason=f"File does not exist: {clean_path}"
        )

    def verify_symbol_in_file(
        self,
        symbol_name: str,
        file_path: str
    ) -> TrustResult:
        """Verify a symbol exists in a file using AST parsing.

        Parses the file with Python's AST module (no LLM)
        and checks if the symbol is defined.
        """
        # First verify file exists
        file_result = self.verify_file_exists(file_path)
        if not file_result.trusted:
            return file_result

        clean_path = file_path.replace("file://", "")

        try:
            with open(clean_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            tree = ast.parse(source)

            # Extract all defined symbols
            symbols = self._extract_symbols(tree, clean_path)
            symbol_names = {s.name for s in symbols}

            if symbol_name in symbol_names:
                return hard_content_result(
                    source="ast_parse",
                    grounding_evidence=[
                        f"file:{clean_path}",
                        f"symbol:{symbol_name}",
                        f"ast_verified:true"
                    ]
                )

            return unverified_result(
                source="ast_parse",
                rejection_reason=f"Symbol '{symbol_name}' not found in {clean_path}"
            )

        except SyntaxError as e:
            return unverified_result(
                source="ast_parse",
                rejection_reason=f"File has syntax errors: {e}"
            )
        except Exception as e:
            return unverified_result(
                source="ast_parse",
                rejection_reason=f"Failed to parse file: {e}"
            )

    def verify_code_parseable(self, code: str) -> TrustResult:
        """Verify code can be parsed by Python AST.

        This doesn't verify the code is correct, just that
        it's valid Python syntax.
        """
        if not code or not code.strip():
            return unverified_result(
                source="code_parse",
                rejection_reason="Empty code"
            )

        try:
            ast.parse(code)
            return hard_content_result(
                source="ast_parse",
                grounding_evidence=["syntax_valid:true"]
            )
        except SyntaxError as e:
            return unverified_result(
                source="code_parse",
                rejection_reason=f"Invalid Python syntax: {e}"
            )

    def verify_import_exists(
        self,
        module_name: str,
        symbol_name: Optional[str] = None
    ) -> TrustResult:
        """Verify an import statement references a real module.

        Attempts to import the module (HardContent verification)
        to confirm it exists.
        """
        try:
            module = __import__(module_name)

            if symbol_name:
                if hasattr(module, symbol_name):
                    return hard_content_result(
                        source="import_check",
                        grounding_evidence=[
                            f"module:{module_name}",
                            f"symbol:{symbol_name}",
                            f"importable:true"
                        ]
                    )
                else:
                    return unverified_result(
                        source="import_check",
                        rejection_reason=f"'{symbol_name}' not found in module '{module_name}'"
                    )

            return hard_content_result(
                source="import_check",
                grounding_evidence=[
                    f"module:{module_name}",
                    f"importable:true"
                ]
            )

        except ImportError:
            return unverified_result(
                source="import_check",
                rejection_reason=f"Module '{module_name}' not importable"
            )

    def extract_verified_symbols(
        self,
        file_path: str
    ) -> tuple[list[VerifiedSymbol], TrustResult]:
        """Extract all symbols from a file with HardContent verification.

        Returns:
            Tuple of (symbols, trust_result)
        """
        file_result = self.verify_file_exists(file_path)
        if not file_result.trusted:
            return [], file_result

        clean_path = file_path.replace("file://", "")

        try:
            with open(clean_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            tree = ast.parse(source)
            symbols = self._extract_symbols(tree, clean_path)

            return symbols, hard_content_result(
                source="ast_extract",
                grounding_evidence=[
                    f"file:{clean_path}",
                    f"symbols_extracted:{len(symbols)}"
                ]
            )

        except Exception as e:
            return [], unverified_result(
                source="ast_extract",
                rejection_reason=f"Failed to extract symbols: {e}"
            )

    def _extract_symbols(
        self,
        tree: ast.AST,
        file_path: str
    ) -> list[VerifiedSymbol]:
        """Extract symbols from AST tree."""
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append(VerifiedSymbol(
                    name=node.name,
                    kind="function",
                    file_path=file_path,
                    line=node.lineno,
                    end_line=getattr(node, 'end_lineno', None),
                    signature=self._get_function_signature(node)
                ))
            elif isinstance(node, ast.AsyncFunctionDef):
                symbols.append(VerifiedSymbol(
                    name=node.name,
                    kind="async_function",
                    file_path=file_path,
                    line=node.lineno,
                    end_line=getattr(node, 'end_lineno', None),
                    signature=self._get_function_signature(node)
                ))
            elif isinstance(node, ast.ClassDef):
                symbols.append(VerifiedSymbol(
                    name=node.name,
                    kind="class",
                    file_path=file_path,
                    line=node.lineno,
                    end_line=getattr(node, 'end_lineno', None)
                ))

        return symbols

    def _get_function_signature(self, node) -> str:
        """Extract function signature from AST node."""
        args = []

        # Positional args
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        signature = f"({', '.join(args)})"

        # Return annotation
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"

        return signature


# =============================================================================
# Regex-based Extraction (HardContent)
# =============================================================================

class RegexExtractor:
    """Extract patterns from source code using regex (HardContent).

    No LLM involved - pure pattern matching.
    """

    # Common patterns for code extraction
    PATTERNS = {
        "python_function": r"def\s+(\w+)\s*\(",
        "python_class": r"class\s+(\w+)\s*[:\(]",
        "python_import": r"(?:from\s+(\S+)\s+)?import\s+(.+)",
        "typescript_function": r"(?:export\s+)?(?:async\s+)?function\s+(\w+)",
        "typescript_class": r"(?:export\s+)?class\s+(\w+)",
        "typescript_interface": r"(?:export\s+)?interface\s+(\w+)",
    }

    def extract_pattern(
        self,
        source: str,
        pattern_name: str
    ) -> tuple[list[str], TrustResult]:
        """Extract matches for a named pattern.

        Args:
            source: Source code to search
            pattern_name: Name of pattern from PATTERNS

        Returns:
            Tuple of (matches, trust_result)
        """
        if pattern_name not in self.PATTERNS:
            return [], unverified_result(
                source="regex_extract",
                rejection_reason=f"Unknown pattern: {pattern_name}"
            )

        pattern = self.PATTERNS[pattern_name]
        matches = re.findall(pattern, source)

        # Flatten tuples from groups
        flat_matches = []
        for match in matches:
            if isinstance(match, tuple):
                flat_matches.extend(m for m in match if m)
            else:
                flat_matches.append(match)

        return flat_matches, hard_content_result(
            source="regex_extract",
            grounding_evidence=[
                f"pattern:{pattern_name}",
                f"matches:{len(flat_matches)}"
            ]
        )

    def extract_custom_pattern(
        self,
        source: str,
        pattern: str
    ) -> tuple[list[str], TrustResult]:
        """Extract matches for a custom regex pattern.

        Args:
            source: Source code to search
            pattern: Regex pattern

        Returns:
            Tuple of (matches, trust_result)
        """
        try:
            matches = re.findall(pattern, source)

            flat_matches = []
            for match in matches:
                if isinstance(match, tuple):
                    flat_matches.extend(m for m in match if m)
                else:
                    flat_matches.append(match)

            return flat_matches, hard_content_result(
                source="regex_extract",
                grounding_evidence=[
                    f"custom_pattern",
                    f"matches:{len(flat_matches)}"
                ]
            )

        except re.error as e:
            return [], unverified_result(
                source="regex_extract",
                rejection_reason=f"Invalid regex pattern: {e}"
            )
