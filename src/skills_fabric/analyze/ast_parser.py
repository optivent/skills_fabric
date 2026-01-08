"""Python AST parsing for symbol extraction with rich metadata.

Enhanced Python AST parser that extracts:
- Function parameters with type annotations
- Return type annotations
- Docstrings for classes and functions
- Decorators
- Call graphs (which functions call which)

Usage:
    parser = ASTParser()
    symbols = parser.parse_file(Path("example.py"))
    # Returns list of EnhancedSymbol with full metadata
"""
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Union

from skills_fabric.observability.logging import get_logger

logger = get_logger("analyze.ast_parser")


@dataclass
class Parameter:
    """A function parameter with type annotation."""
    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation like 'name: type = default'."""
        parts = [self.name]
        if self.type_annotation:
            parts[0] = f"{self.name}: {self.type_annotation}"
        if self.default_value:
            parts.append(f"= {self.default_value}")
        return " ".join(parts)


@dataclass
class Symbol:
    """A code symbol extracted from source (basic version for compatibility)."""
    name: str
    kind: str  # 'class', 'function', 'method'
    file_path: str
    line: int


@dataclass
class EnhancedSymbol:
    """A code symbol with rich metadata extracted from Python AST.

    Attributes:
        name: Symbol name (e.g., 'MyClass', 'my_function')
        kind: Symbol type ('class', 'function', 'method', 'async_function', 'async_method')
        file_path: Path to the source file
        line: Line number where the symbol is defined
        end_line: Line number where the symbol definition ends
        parameters: List of function/method parameters with type annotations
        return_type: Function return type annotation
        docstring: Docstring content if present
        decorators: List of decorator names
        calls: List of function/method names called by this symbol
        parent_class: Name of the containing class (for methods)
        is_async: Whether the function/method is async
        is_static: Whether the method is a static method
        is_classmethod: Whether the method is a class method
        is_property: Whether the method is a property
    """
    name: str
    kind: str  # 'class', 'function', 'method', 'async_function', 'async_method'
    file_path: str
    line: int
    end_line: Optional[int] = None
    parameters: list[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    parent_class: Optional[str] = None
    is_async: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    is_property: bool = False

    @property
    def signature(self) -> str:
        """Return the full signature string."""
        params_str = ", ".join(str(p) for p in self.parameters)
        sig = f"{self.name}({params_str})"
        if self.return_type:
            sig += f" -> {self.return_type}"
        return sig

    @property
    def qualified_name(self) -> str:
        """Return the fully qualified name including parent class."""
        if self.parent_class:
            return f"{self.parent_class}.{self.name}"
        return self.name

    def to_basic_symbol(self) -> Symbol:
        """Convert to basic Symbol for compatibility."""
        return Symbol(
            name=self.name,
            kind=self.kind,
            file_path=self.file_path,
            line=self.line
        )


class CallGraphVisitor(ast.NodeVisitor):
    """AST visitor that extracts function/method calls."""

    def __init__(self):
        self.calls: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract the name from a function call."""
        call_name = self._extract_call_name(node.func)
        if call_name:
            self.calls.append(call_name)
        # Continue visiting child nodes
        self.generic_visit(node)

    def _extract_call_name(self, node: ast.expr) -> Optional[str]:
        """Extract the callable name from various node types."""
        if isinstance(node, ast.Name):
            # Simple function call: func()
            return node.id
        elif isinstance(node, ast.Attribute):
            # Attribute access: obj.method() or module.func()
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        elif isinstance(node, ast.Subscript):
            # Subscript call: List[int]() - typically type constructors
            return self._extract_call_name(node.value)
        return None


class ASTParser:
    """Parse Python files and extract enhanced symbol information.

    Provides both basic and enhanced extraction modes for compatibility.
    The enhanced mode extracts parameters, return types, docstrings,
    decorators, and call graphs.
    """

    def __init__(self):
        self._call_graph: dict[str, list[str]] = {}  # symbol -> [calls]
        self._callers: dict[str, list[str]] = {}  # symbol -> [callers]

    def parse_file(self, file_path: Path, enhanced: bool = True) -> Union[list[Symbol], list[EnhancedSymbol]]:
        """Parse a Python file and extract symbols.

        Args:
            file_path: Path to the Python source file.
            enhanced: If True, return EnhancedSymbol with full metadata.
                     If False, return basic Symbol for compatibility.

        Returns:
            List of symbols. Type depends on enhanced parameter.
        """
        if enhanced:
            return self.parse_file_enhanced(file_path)

        # Basic parsing for backwards compatibility
        symbols = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                source = f.read()

            tree = ast.parse(source)
            rel_path = str(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append(Symbol(
                        name=node.name,
                        kind="class",
                        file_path=rel_path,
                        line=node.lineno
                    ))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(Symbol(
                        name=node.name,
                        kind="function",
                        file_path=rel_path,
                        line=node.lineno
                    ))
        except SyntaxError as e:
            logger.debug(f"Syntax error parsing {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")

        return symbols

    def parse_file_enhanced(self, file_path: Path) -> list[EnhancedSymbol]:
        """Parse a Python file and extract enhanced symbol information.

        Args:
            file_path: Path to the Python source file.

        Returns:
            List of EnhancedSymbol with full metadata including parameters,
            return types, docstrings, decorators, and call graphs.
        """
        symbols = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                source = f.read()

            tree = ast.parse(source)
            rel_path = str(file_path)

            # Process top-level definitions
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    # Extract class symbol
                    class_symbol = self._extract_class(node, rel_path)
                    symbols.append(class_symbol)

                    # Extract methods from the class
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_symbol = self._extract_function(
                                item, rel_path, parent_class=node.name
                            )
                            symbols.append(method_symbol)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_symbol = self._extract_function(node, rel_path)
                    symbols.append(func_symbol)

            logger.debug(f"Extracted {len(symbols)} enhanced symbols from {file_path}")

        except SyntaxError as e:
            logger.debug(f"Syntax error parsing {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")

        return symbols

    def _extract_class(self, node: ast.ClassDef, file_path: str) -> EnhancedSymbol:
        """Extract enhanced symbol information from a class definition.

        Args:
            node: The AST ClassDef node.
            file_path: Path to the source file.

        Returns:
            EnhancedSymbol with class metadata.
        """
        # Extract decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        decorators = [d for d in decorators if d]  # Filter None values

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Extract calls from class body (e.g., class-level attribute assignments)
        call_visitor = CallGraphVisitor()
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                call_visitor.visit(item)

        return EnhancedSymbol(
            name=node.name,
            kind="class",
            file_path=file_path,
            line=node.lineno,
            end_line=node.end_lineno,
            docstring=docstring,
            decorators=decorators,
            calls=call_visitor.calls
        )

    def _extract_function(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        file_path: str,
        parent_class: Optional[str] = None
    ) -> EnhancedSymbol:
        """Extract enhanced symbol information from a function/method definition.

        Args:
            node: The AST FunctionDef or AsyncFunctionDef node.
            file_path: Path to the source file.
            parent_class: Name of the containing class if this is a method.

        Returns:
            EnhancedSymbol with function/method metadata.
        """
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Extract decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        decorators = [d for d in decorators if d]  # Filter None values

        # Determine special method types
        is_static = "staticmethod" in decorators
        is_classmethod = "classmethod" in decorators
        is_property = "property" in decorators

        # Determine kind
        if parent_class:
            kind = "async_method" if is_async else "method"
        else:
            kind = "async_function" if is_async else "function"

        # Extract parameters
        parameters = self._extract_parameters(node.args)

        # Extract return type
        return_type = self._annotation_to_string(node.returns) if node.returns else None

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Extract function calls from body
        call_visitor = CallGraphVisitor()
        for item in node.body:
            call_visitor.visit(item)

        return EnhancedSymbol(
            name=node.name,
            kind=kind,
            file_path=file_path,
            line=node.lineno,
            end_line=node.end_lineno,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            calls=call_visitor.calls,
            parent_class=parent_class,
            is_async=is_async,
            is_static=is_static,
            is_classmethod=is_classmethod,
            is_property=is_property
        )

    def _extract_parameters(self, args: ast.arguments) -> list[Parameter]:
        """Extract parameters with type annotations from function arguments.

        Args:
            args: The AST arguments object from a function definition.

        Returns:
            List of Parameter objects with name, type, and default value.
        """
        parameters = []

        # Calculate defaults offset (defaults are right-aligned to positional args)
        num_positional = len(args.posonlyargs) + len(args.args)
        num_defaults = len(args.defaults)
        defaults_offset = num_positional - num_defaults

        # Process positional-only arguments (Python 3.8+)
        for i, arg in enumerate(args.posonlyargs):
            default_idx = i - defaults_offset
            default = None
            if default_idx >= 0 and default_idx < len(args.defaults):
                default = self._value_to_string(args.defaults[default_idx])

            parameters.append(Parameter(
                name=arg.arg,
                type_annotation=self._annotation_to_string(arg.annotation),
                default_value=default
            ))

        # Process regular positional arguments
        for i, arg in enumerate(args.args):
            default_idx = i + len(args.posonlyargs) - defaults_offset
            default = None
            if default_idx >= 0 and default_idx < len(args.defaults):
                default = self._value_to_string(args.defaults[default_idx])

            parameters.append(Parameter(
                name=arg.arg,
                type_annotation=self._annotation_to_string(arg.annotation),
                default_value=default
            ))

        # Process *args (variadic positional)
        if args.vararg:
            parameters.append(Parameter(
                name=f"*{args.vararg.arg}",
                type_annotation=self._annotation_to_string(args.vararg.annotation)
            ))

        # Process keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            default = None
            if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
                default = self._value_to_string(args.kw_defaults[i])

            parameters.append(Parameter(
                name=arg.arg,
                type_annotation=self._annotation_to_string(arg.annotation),
                default_value=default
            ))

        # Process **kwargs (variadic keyword)
        if args.kwarg:
            parameters.append(Parameter(
                name=f"**{args.kwarg.arg}",
                type_annotation=self._annotation_to_string(args.kwarg.annotation)
            ))

        return parameters

    def _annotation_to_string(self, annotation: Optional[ast.expr]) -> Optional[str]:
        """Convert an AST annotation node to a string representation.

        Args:
            annotation: The AST node representing a type annotation.

        Returns:
            String representation of the annotation, or None if not present.
        """
        if annotation is None:
            return None

        try:
            return ast.unparse(annotation)
        except Exception:
            # Fallback for complex annotations
            return self._format_annotation(annotation)

    def _format_annotation(self, node: ast.expr) -> str:
        """Format an annotation node to string (fallback method).

        Args:
            node: The AST expression node.

        Returns:
            String representation of the annotation.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Subscript):
            value = self._format_annotation(node.value)
            slice_val = self._format_annotation(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Attribute):
            value = self._format_annotation(node.value)
            return f"{value}.{node.attr}"
        elif isinstance(node, ast.Tuple):
            elts = ", ".join(self._format_annotation(e) for e in node.elts)
            return elts
        elif isinstance(node, ast.BinOp):
            # Handle Union types with | syntax (Python 3.10+)
            left = self._format_annotation(node.left)
            right = self._format_annotation(node.right)
            if isinstance(node.op, ast.BitOr):
                return f"{left} | {right}"
            return f"{left} {type(node.op).__name__} {right}"
        else:
            return str(type(node).__name__)

    def _value_to_string(self, node: ast.expr) -> str:
        """Convert an AST value node to a string representation.

        Args:
            node: The AST expression node representing a default value.

        Returns:
            String representation of the value.
        """
        try:
            return ast.unparse(node)
        except Exception:
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.List):
                return "[]"
            elif isinstance(node, ast.Dict):
                return "{}"
            elif isinstance(node, ast.Tuple):
                return "()"
            return "..."

    def _get_decorator_name(self, decorator: ast.expr) -> Optional[str]:
        """Extract the name from a decorator node.

        Args:
            decorator: The AST node representing a decorator.

        Returns:
            The decorator name as a string, or None if unrecognized.
        """
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            parts = []
            current = decorator
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        elif isinstance(decorator, ast.Call):
            # Decorator with arguments: @decorator(args)
            return self._get_decorator_name(decorator.func)
        return None

    def parse_directory(
        self,
        dir_path: Path,
        enhanced: bool = True
    ) -> Union[list[Symbol], list[EnhancedSymbol]]:
        """Parse all Python files in a directory.

        Args:
            dir_path: Path to the directory to scan.
            enhanced: If True, return EnhancedSymbol with full metadata.

        Returns:
            List of symbols from all Python files in the directory.
        """
        all_symbols = []

        for py_file in dir_path.rglob("*.py"):
            # Skip test files and common non-source dirs
            path_str = str(py_file)
            if any(skip in path_str for skip in [
                "__pycache__", ".venv", "node_modules", ".git", "dist", "build"
            ]):
                continue

            symbols = self.parse_file(py_file, enhanced=enhanced)
            all_symbols.extend(symbols)

        logger.info(f"Parsed {len(all_symbols)} symbols from {dir_path}")
        return all_symbols

    def build_call_graph(
        self,
        symbols: list[EnhancedSymbol]
    ) -> dict[str, list[str]]:
        """Build a call graph from a list of enhanced symbols.

        Args:
            symbols: List of EnhancedSymbol with call information.

        Returns:
            Dictionary mapping symbol qualified names to lists of called functions.
        """
        call_graph = {}

        for symbol in symbols:
            if symbol.kind in ("function", "method", "async_function", "async_method"):
                call_graph[symbol.qualified_name] = symbol.calls

        return call_graph

    def get_callers(
        self,
        symbols: list[EnhancedSymbol],
        target_name: str
    ) -> list[str]:
        """Find all functions/methods that call a specific symbol.

        Args:
            symbols: List of EnhancedSymbol to search.
            target_name: Name of the function/method to find callers for.

        Returns:
            List of qualified names of symbols that call the target.
        """
        callers = []

        for symbol in symbols:
            if symbol.kind in ("function", "method", "async_function", "async_method"):
                # Check if target_name appears in the calls (full match or suffix)
                for call in symbol.calls:
                    if call == target_name or call.endswith(f".{target_name}"):
                        callers.append(symbol.qualified_name)
                        break

        return callers


def parse_python_file(file_path: Path) -> list[EnhancedSymbol]:
    """Convenience function to parse a single Python file.

    Args:
        file_path: Path to the Python file.

    Returns:
        List of EnhancedSymbol from the file.
    """
    parser = ASTParser()
    return parser.parse_file_enhanced(file_path)


def parse_python_directory(dir_path: Path) -> list[EnhancedSymbol]:
    """Convenience function to parse all Python files in a directory.

    Args:
        dir_path: Path to the directory.

    Returns:
        List of EnhancedSymbol from all Python files.
    """
    parser = ASTParser()
    return parser.parse_directory(dir_path, enhanced=True)
