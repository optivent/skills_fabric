"""Progressive Depth Controller - Levels 0-5 code analysis.

Implements the Progressive Iceberg Architecture for configurable depth analysis:

Level 0: Validate link exists (simple syntax examples)
Level 1: Parse symbol structure (API reference)
Level 2: Immediate dependencies (behavioral understanding)
Level 3: Call graph (1 level) (mechanics)
Level 4: Full recursive expansion (master class)
Level 5: Execution trace in sandbox (debugging)

Each level builds on the previous, progressively deepening understanding.
The key insight: CodeWiki links are PRE-VERIFIED connections from docs to code.

Usage:
    from skills_fabric.intelligence.depth_controller import (
        DepthController, DepthLevel, CodeWikiRef
    )

    controller = DepthController(repo_path="/path/to/langgraph")

    ref = CodeWikiRef(
        concept="StateGraph",
        file_path="libs/langgraph/langgraph/graph/state.py",
        line=112,
        repo="langchain-ai/langgraph"
    )

    # Expand to Level 2 (dependencies)
    result = controller.expand(ref, DepthLevel.DEPENDENCIES)

    print(f"Symbol: {result.symbol}")
    print(f"Methods: {result.methods}")
    print(f"Dependencies: {result.dependencies}")
"""
import ast
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from enum import IntEnum
from datetime import datetime


class DepthLevel(IntEnum):
    """Progressive deepening levels.

    Each level provides more information but requires more computation.
    Choose based on skill type:
    - "How to use X" → Level 0-1
    - "What does X do" → Level 1-2
    - "How does X work" → Level 2-3
    - "Debug why X fails" → Level 4-5
    """
    VALIDATE = 0      # Just check link exists
    PARSE_SYMBOL = 1  # Extract symbol structure (methods, params)
    DEPENDENCIES = 2  # Immediate dependencies
    CALL_GRAPH = 3    # One-level call expansion
    FULL_GRAPH = 4    # Recursive expansion
    EXEC_TRACE = 5    # Runtime execution trace


@dataclass
class CodeWikiRef:
    """A pre-verified reference from CodeWiki documentation.

    CodeWiki embeds GitHub links with:
    - Repository path
    - File path
    - Commit hash (optional)
    - Line numbers

    Example:
        [StateGraph](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/graph/state.py#L112)
    """
    concept: str
    file_path: str
    line: int
    repo: str = ""
    commit: str = ""
    url: str = ""

    @classmethod
    def from_url(cls, concept: str, url: str) -> "CodeWikiRef":
        """Parse a GitHub URL into a CodeWikiRef."""
        # Pattern: https://github.com/{owner}/{repo}/blob/{commit}/{path}#L{line}
        pattern = r"https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#]+)(?:#L(\d+))?"
        match = re.match(pattern, url)
        if match:
            return cls(
                concept=concept,
                repo=match.group(1),
                commit=match.group(2),
                file_path=match.group(3),
                line=int(match.group(4)) if match.group(4) else 0,
                url=url
            )
        raise ValueError(f"Invalid GitHub URL: {url}")


@dataclass
class SymbolInfo:
    """Extracted symbol information."""
    name: str
    kind: str  # class, function, method, variable
    line: int
    end_line: int = 0
    docstring: str = ""
    signature: str = ""
    decorators: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)  # For classes


@dataclass
class MethodInfo:
    """Method/function details."""
    name: str
    parameters: list[str]
    return_type: str = ""
    docstring: str = ""
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)


@dataclass
class DependencyInfo:
    """Import/dependency information."""
    name: str
    module: str
    alias: str = ""
    is_from_import: bool = False


@dataclass
class CallInfo:
    """Function call information for call graph."""
    caller: str
    callee: str
    line: int
    arguments: list[str] = field(default_factory=list)


@dataclass
class DepthResult:
    """Result of progressive deepening analysis."""
    ref: CodeWikiRef
    level: DepthLevel
    validated: bool = False

    # Level 1: Symbol info
    symbol: Optional[SymbolInfo] = None
    methods: list[MethodInfo] = field(default_factory=list)
    source_code: str = ""

    # Level 2: Dependencies
    dependencies: list[DependencyInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)

    # Level 3-4: Call graph
    calls: list[CallInfo] = field(default_factory=list)
    called_by: list[CallInfo] = field(default_factory=list)

    # Level 5: Execution
    execution_trace: list[dict] = field(default_factory=list)
    execution_success: bool = False
    execution_output: str = ""

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0


class DepthController:
    """Progressive deepening controller for code analysis.

    Implements the 6-level Progressive Iceberg model:
    - Each level validates the level above
    - Each level is grounded in the level below
    - Git clone is the foundation (immutable truth)
    """

    def __init__(self, repo_path: Path | str):
        """Initialize with path to cloned repository.

        Args:
            repo_path: Path to the git-cloned repository
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def expand(self, ref: CodeWikiRef, depth: DepthLevel) -> DepthResult:
        """Expand a CodeWiki reference to the specified depth.

        Args:
            ref: CodeWiki reference with file path and line
            depth: How deep to analyze (0-5)

        Returns:
            DepthResult with information at the requested depth
        """
        start = datetime.now()
        result = DepthResult(ref=ref, level=depth)

        # Level 0: Validate link
        if depth >= DepthLevel.VALIDATE:
            result.validated = self._validate(ref)
            if not result.validated:
                return result

        # Level 1: Parse symbol
        if depth >= DepthLevel.PARSE_SYMBOL:
            result.source_code = self._read_source(ref)
            result.symbol = self._parse_symbol(ref, result.source_code)
            result.methods = self._extract_methods(result.source_code, ref.line)

        # Level 2: Immediate dependencies
        if depth >= DepthLevel.DEPENDENCIES:
            result.dependencies = self._find_dependencies(ref)
            result.imports = self._extract_imports(ref)

        # Level 3: Call graph (1 level)
        if depth >= DepthLevel.CALL_GRAPH:
            result.calls = self._build_call_graph(ref, recursive=False)

        # Level 4: Full recursive expansion
        if depth >= DepthLevel.FULL_GRAPH:
            result.calls = self._build_call_graph(ref, recursive=True)
            result.called_by = self._find_callers(ref)

        # Level 5: Execution trace
        if depth >= DepthLevel.EXEC_TRACE:
            trace_result = self._execute_and_trace(ref)
            result.execution_trace = trace_result.get("trace", [])
            result.execution_success = trace_result.get("success", False)
            result.execution_output = trace_result.get("output", "")

        result.duration_ms = (datetime.now() - start).total_seconds() * 1000
        return result

    def _validate(self, ref: CodeWikiRef) -> bool:
        """Level 0: Validate that the reference exists and is correct."""
        file_path = self.repo_path / ref.file_path
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if ref.line > 0 and ref.line <= len(lines):
                    # Check if the concept name appears near the line
                    context = ''.join(lines[max(0, ref.line-3):ref.line+3])
                    return ref.concept.lower() in context.lower()
                return True  # Line 0 means just file existence
        except Exception:
            return False

    def _read_source(self, ref: CodeWikiRef) -> str:
        """Read source code from the reference location."""
        file_path = self.repo_path / ref.file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def _parse_symbol(self, ref: CodeWikiRef, source: str) -> Optional[SymbolInfo]:
        """Level 1: Parse the symbol at the referenced line."""
        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):
                # Check if this node is at or near our target line
                if hasattr(node, 'lineno') and abs(node.lineno - ref.line) <= 2:
                    if isinstance(node, ast.ClassDef):
                        return SymbolInfo(
                            name=node.name,
                            kind="class",
                            line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            docstring=ast.get_docstring(node) or "",
                            bases=[self._get_name(b) for b in node.bases],
                            decorators=[self._get_name(d) for d in node.decorator_list]
                        )
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        return SymbolInfo(
                            name=node.name,
                            kind="async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                            line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            docstring=ast.get_docstring(node) or "",
                            signature=self._get_signature(node),
                            decorators=[self._get_name(d) for d in node.decorator_list]
                        )

            return None
        except SyntaxError:
            return None

    def _extract_methods(self, source: str, class_line: int) -> list[MethodInfo]:
        """Extract methods from a class definition."""
        methods = []
        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and abs(node.lineno - class_line) <= 2:
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.append(MethodInfo(
                                name=item.name,
                                parameters=self._get_parameters(item),
                                return_type=self._get_return_type(item),
                                docstring=ast.get_docstring(item) or "",
                                is_async=isinstance(item, ast.AsyncFunctionDef),
                                decorators=[self._get_name(d) for d in item.decorator_list]
                            ))
        except SyntaxError:
            pass

        return methods

    def _find_dependencies(self, ref: CodeWikiRef) -> list[DependencyInfo]:
        """Level 2: Find immediate dependencies (imports)."""
        deps = []
        file_path = self.repo_path / ref.file_path

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        deps.append(DependencyInfo(
                            name=alias.name,
                            module=alias.name,
                            alias=alias.asname or "",
                            is_from_import=False
                        ))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        deps.append(DependencyInfo(
                            name=alias.name,
                            module=module,
                            alias=alias.asname or "",
                            is_from_import=True
                        ))
        except Exception:
            pass

        return deps

    def _extract_imports(self, ref: CodeWikiRef) -> list[str]:
        """Extract import statements as strings."""
        imports = []
        file_path = self.repo_path / ref.file_path

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith(('import ', 'from ')):
                        imports.append(stripped)
                    elif imports and not stripped.startswith(('#', '"""', "'''")):
                        # Stop at first non-import, non-comment line
                        if stripped and not stripped.startswith(('import ', 'from ')):
                            if not line[0].isspace():  # Not a continuation
                                break
        except Exception:
            pass

        return imports

    def _build_call_graph(self, ref: CodeWikiRef, recursive: bool = False) -> list[CallInfo]:
        """Level 3-4: Build call graph from the symbol."""
        calls = []
        source = self._read_source(ref)

        try:
            tree = ast.parse(source)

            # Find the target function/method
            target_node = None
            for node in ast.walk(tree):
                if hasattr(node, 'lineno') and abs(node.lineno - ref.line) <= 2:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        target_node = node
                        break

            if target_node:
                for node in ast.walk(target_node):
                    if isinstance(node, ast.Call):
                        callee = self._get_name(node.func)
                        if callee:
                            calls.append(CallInfo(
                                caller=ref.concept,
                                callee=callee,
                                line=node.lineno if hasattr(node, 'lineno') else 0,
                                arguments=[self._get_name(arg) for arg in node.args]
                            ))
        except Exception:
            pass

        return calls

    def _find_callers(self, ref: CodeWikiRef) -> list[CallInfo]:
        """Find functions that call the target symbol."""
        callers = []
        # Search all Python files in the repo
        for py_file in self.repo_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        callee = self._get_name(node.func)
                        if callee and ref.concept in callee:
                            # Find the enclosing function
                            # (simplified - just record the call)
                            callers.append(CallInfo(
                                caller=str(py_file.relative_to(self.repo_path)),
                                callee=ref.concept,
                                line=node.lineno if hasattr(node, 'lineno') else 0
                            ))
            except Exception:
                continue

        return callers[:50]  # Limit to 50 callers

    def _execute_and_trace(self, ref: CodeWikiRef) -> dict:
        """Level 5: Execute code in sandbox and capture trace."""
        # This would integrate with the sandbox module
        # For now, return a placeholder
        return {
            "success": False,
            "output": "Sandbox execution not yet implemented in depth controller",
            "trace": []
        }

    # Helper methods
    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ""

    def _get_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract function signature."""
        params = self._get_parameters(node)
        return_type = self._get_return_type(node)
        sig = f"({', '.join(params)})"
        if return_type:
            sig += f" -> {return_type}"
        return sig

    def _get_parameters(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        """Extract parameter names and types."""
        params = []
        for arg in node.args.args:
            param = arg.arg
            if arg.annotation:
                param += f": {self._get_name(arg.annotation)}"
            params.append(param)
        return params

    def _get_return_type(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract return type annotation."""
        if node.returns:
            return self._get_name(node.returns)
        return ""


# =============================================================================
# Skill Type to Depth Mapping
# =============================================================================

SKILL_DEPTH_MAP = {
    "how_to_use": DepthLevel.PARSE_SYMBOL,       # Level 1
    "what_does": DepthLevel.DEPENDENCIES,         # Level 2
    "how_works": DepthLevel.CALL_GRAPH,           # Level 3
    "internals": DepthLevel.FULL_GRAPH,           # Level 4
    "debug": DepthLevel.EXEC_TRACE,               # Level 5
    "master_class": DepthLevel.EXEC_TRACE,        # Level 5
}


def determine_depth(skill_type: str) -> DepthLevel:
    """Determine appropriate depth for a skill type.

    Args:
        skill_type: Type of skill to generate

    Returns:
        Appropriate DepthLevel
    """
    return SKILL_DEPTH_MAP.get(skill_type, DepthLevel.DEPENDENCIES)


# =============================================================================
# CodeWiki Link Extractor
# =============================================================================

def extract_codewiki_refs(markdown: str) -> list[CodeWikiRef]:
    """Extract GitHub links from CodeWiki-style markdown.

    Finds patterns like:
    [`StateGraph`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/graph/state.py#L112)

    Args:
        markdown: Markdown content with embedded GitHub links

    Returns:
        List of CodeWikiRef objects
    """
    pattern = r"\[`?([^`\]]+)`?\]\(https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#)]+)(?:#L(\d+))?\)"

    refs = []
    for match in re.finditer(pattern, markdown):
        refs.append(CodeWikiRef(
            concept=match.group(1),
            repo=match.group(2),
            commit=match.group(3),
            file_path=match.group(4),
            line=int(match.group(5)) if match.group(5) else 0,
            url=f"https://github.com/{match.group(2)}/blob/{match.group(3)}/{match.group(4)}" +
                (f"#L{match.group(5)}" if match.group(5) else "")
        ))
    return refs
