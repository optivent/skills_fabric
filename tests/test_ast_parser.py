"""Unit tests for enhanced AST extraction.

This module tests the ASTParser class for Python code analysis:
- Parameter extraction with type annotations and default values
- Return type extraction
- Docstring extraction
- Decorator extraction
- Call graph extraction
- Method type detection (async, static, classmethod, property)

Test coverage includes:
- Basic parsing functionality
- Enhanced symbol extraction
- Edge cases and error handling
- Call graph building
- Directory parsing
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

# Import ast_parser module directly to avoid heavy dependencies from skills_fabric.__init__
_src_path = Path(__file__).parent.parent / "src"

# First, ensure observability.logging is available (ast_parser depends on it)
_logging_path = _src_path / "skills_fabric" / "observability" / "logging.py"
_logging_spec = importlib.util.spec_from_file_location("skills_fabric.observability.logging", _logging_path)
_logging_module = importlib.util.module_from_spec(_logging_spec)
sys.modules["skills_fabric.observability.logging"] = _logging_module
_logging_spec.loader.exec_module(_logging_module)

# Now import the ast_parser module
_ast_parser_path = _src_path / "skills_fabric" / "analyze" / "ast_parser.py"
_spec = importlib.util.spec_from_file_location("skills_fabric.analyze.ast_parser", _ast_parser_path)
_ast_parser_module = importlib.util.module_from_spec(_spec)
sys.modules["skills_fabric.analyze.ast_parser"] = _ast_parser_module
_spec.loader.exec_module(_ast_parser_module)

ASTParser = _ast_parser_module.ASTParser
EnhancedSymbol = _ast_parser_module.EnhancedSymbol
Parameter = _ast_parser_module.Parameter
Symbol = _ast_parser_module.Symbol
parse_python_file = _ast_parser_module.parse_python_file
parse_python_directory = _ast_parser_module.parse_python_directory


def assert_symbol_found(
    symbols: list,
    name: str,
    kind: str | None = None,
) -> Any:
    """Assert that a symbol with the given name exists.

    Args:
        symbols: List of symbols to search.
        name: Name of the symbol to find.
        kind: Optional kind to match (class, function, method).

    Returns:
        The found symbol.

    Raises:
        AssertionError: If symbol not found or kind doesn't match.
    """
    for symbol in symbols:
        symbol_name = getattr(symbol, "name", str(symbol))
        if symbol_name == name:
            if kind is not None:
                symbol_kind = getattr(symbol, "kind", None)
                assert symbol_kind == kind, (
                    f"Expected {name} to be {kind}, got {symbol_kind}"
                )
            return symbol

    symbol_names = [getattr(s, "name", str(s)) for s in symbols]
    raise AssertionError(f"Symbol '{name}' not found in: {symbol_names}")


# =============================================================================
# Sample Code for Testing
# =============================================================================

SAMPLE_PYTHON_WITH_PARAMETERS = '''"""Module with various parameter patterns."""
from typing import Optional, List, Dict, Union


def simple_params(a, b, c):
    """Function with simple parameters."""
    pass


def typed_params(x: int, y: str, z: float) -> bool:
    """Function with typed parameters."""
    return True


def default_params(a: int = 10, b: str = "default", c: bool = True):
    """Function with default values."""
    pass


def mixed_params(required: int, optional: str = "opt", *args, **kwargs):
    """Function with mixed parameter types."""
    pass


def complex_types(
    items: List[str],
    mapping: Dict[str, int],
    optional: Optional[float] = None,
    union: Union[int, str] = 0
) -> Dict[str, List[int]]:
    """Function with complex type annotations."""
    return {}


def keyword_only_params(*, name: str, value: int = 0):
    """Function with keyword-only parameters."""
    pass


def positional_only_params(a: int, b: int, /, c: int = 0):
    """Function with positional-only parameters (Python 3.8+)."""
    pass
'''

SAMPLE_PYTHON_WITH_DOCSTRINGS = '''"""Module docstring for testing."""


class DocstringClass:
    """A class with a detailed docstring.

    This class demonstrates docstring extraction from
    class definitions. It includes multiple lines.

    Attributes:
        name: The name of the instance.
        value: An integer value.
    """

    def method_with_docstring(self):
        """A method with a docstring.

        Returns:
            None
        """
        pass

    def method_without_docstring(self):
        pass


def function_with_docstring(x: int) -> int:
    """A function with a docstring.

    Args:
        x: The input value.

    Returns:
        The doubled value.
    """
    return x * 2


def function_without_docstring(x):
    return x


def function_with_short_docstring():
    """Short docstring."""
    pass
'''

SAMPLE_PYTHON_WITH_DECORATORS = '''"""Module demonstrating decorator patterns."""
from functools import lru_cache, wraps


def my_decorator(func):
    """A custom decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@my_decorator
def decorated_function():
    """A decorated function."""
    pass


@lru_cache(maxsize=128)
def cached_function(x: int) -> int:
    """A function with lru_cache decorator."""
    return x * 2


class DecoratedClass:
    """Class with decorated methods."""

    @property
    def name(self) -> str:
        """A property method."""
        return "name"

    @staticmethod
    def static_method():
        """A static method."""
        pass

    @classmethod
    def class_method(cls):
        """A class method."""
        return cls.__name__

    @my_decorator
    def custom_decorated(self):
        """A method with custom decorator."""
        pass

    @property
    @lru_cache(maxsize=1)
    def cached_property(self) -> int:
        """A property with multiple decorators."""
        return 42
'''

SAMPLE_PYTHON_WITH_RETURN_TYPES = '''"""Module demonstrating return type annotations."""
from typing import Optional, List, Tuple, Dict, Any, Union


def returns_int() -> int:
    """Function that returns int."""
    return 42


def returns_str() -> str:
    """Function that returns str."""
    return "hello"


def returns_none() -> None:
    """Function that explicitly returns None."""
    pass


def returns_optional() -> Optional[str]:
    """Function that returns Optional."""
    return None


def returns_list() -> List[int]:
    """Function that returns List."""
    return [1, 2, 3]


def returns_dict() -> Dict[str, int]:
    """Function that returns Dict."""
    return {"a": 1}


def returns_tuple() -> Tuple[int, str, float]:
    """Function that returns Tuple."""
    return (1, "a", 1.0)


def returns_union() -> Union[int, str]:
    """Function that returns Union."""
    return 42


def returns_any() -> Any:
    """Function that returns Any."""
    return None


def no_return_type():
    """Function without return type annotation."""
    return 42


class ClassWithReturnTypes:
    """Class with methods having return types."""

    def method_returns_self(self) -> "ClassWithReturnTypes":
        """Method returning self type."""
        return self

    async def async_returns_list(self) -> List[str]:
        """Async method with return type."""
        return []
'''

SAMPLE_PYTHON_WITH_CALLS = '''"""Module demonstrating function calls for call graph."""


def helper_function():
    """A helper function."""
    pass


def another_helper(x):
    """Another helper function."""
    return x


def caller_function():
    """Function that calls other functions."""
    helper_function()
    result = another_helper(10)
    print(result)
    return result


class Calculator:
    """A calculator class."""

    def __init__(self, initial: int = 0):
        self.value = initial
        self.reset()

    def add(self, x: int) -> int:
        """Add to value."""
        self._validate(x)
        self.value += x
        return self.value

    def _validate(self, x: int) -> None:
        """Private validation method."""
        if not isinstance(x, int):
            raise ValueError("Must be int")

    def reset(self) -> None:
        """Reset the calculator."""
        self.value = 0

    def compute(self, values: list) -> int:
        """Compute sum of values."""
        for v in values:
            self.add(v)
        return self.value
'''

SAMPLE_PYTHON_ASYNC = '''"""Module with async functions and methods."""
import asyncio


async def async_function() -> str:
    """An async function."""
    await asyncio.sleep(0.1)
    return "done"


async def async_with_params(url: str, timeout: float = 30.0) -> dict:
    """Async function with parameters."""
    await asyncio.sleep(timeout)
    return {"url": url}


class AsyncClass:
    """Class with async methods."""

    async def fetch(self, url: str) -> bytes:
        """Async method to fetch data."""
        return b""

    async def process(self, data: bytes) -> str:
        """Async method to process data."""
        result = await self._transform(data)
        return result

    async def _transform(self, data: bytes) -> str:
        """Private async method."""
        return data.decode()

    def sync_method(self) -> int:
        """A regular sync method in async class."""
        return 42
'''

SAMPLE_MALFORMED_PYTHON = '''
# This is intentionally malformed Python
def broken_function(
    # Missing closing paren and body
class incomplete:
    pass
'''


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def ast_parser() -> ASTParser:
    """Create an ASTParser instance."""
    return ASTParser()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory."""
    return tmp_path


@pytest.fixture
def sample_params_file(tmp_path: Path) -> Path:
    """Create a file with various parameter patterns."""
    file_path = tmp_path / "params.py"
    file_path.write_text(SAMPLE_PYTHON_WITH_PARAMETERS)
    return file_path


@pytest.fixture
def sample_docstrings_file(tmp_path: Path) -> Path:
    """Create a file with docstrings."""
    file_path = tmp_path / "docstrings.py"
    file_path.write_text(SAMPLE_PYTHON_WITH_DOCSTRINGS)
    return file_path


@pytest.fixture
def sample_decorators_file(tmp_path: Path) -> Path:
    """Create a file with decorators."""
    file_path = tmp_path / "decorators.py"
    file_path.write_text(SAMPLE_PYTHON_WITH_DECORATORS)
    return file_path


@pytest.fixture
def sample_return_types_file(tmp_path: Path) -> Path:
    """Create a file with return type annotations."""
    file_path = tmp_path / "return_types.py"
    file_path.write_text(SAMPLE_PYTHON_WITH_RETURN_TYPES)
    return file_path


@pytest.fixture
def sample_calls_file(tmp_path: Path) -> Path:
    """Create a file demonstrating function calls."""
    file_path = tmp_path / "calls.py"
    file_path.write_text(SAMPLE_PYTHON_WITH_CALLS)
    return file_path


@pytest.fixture
def sample_async_file(tmp_path: Path) -> Path:
    """Create a file with async functions."""
    file_path = tmp_path / "async_code.py"
    file_path.write_text(SAMPLE_PYTHON_ASYNC)
    return file_path


@pytest.fixture
def sample_malformed_file(tmp_path: Path) -> Path:
    """Create a malformed Python file."""
    file_path = tmp_path / "malformed.py"
    file_path.write_text(SAMPLE_MALFORMED_PYTHON)
    return file_path


# =============================================================================
# Parameter Extraction Tests
# =============================================================================


class TestParameterExtraction:
    """Test extraction of function parameters."""

    def test_simple_params(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of simple parameters without types."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "simple_params", kind="function")

        assert len(func.parameters) == 3
        param_names = [p.name for p in func.parameters]
        assert param_names == ["a", "b", "c"]

        # No type annotations for simple params
        for param in func.parameters:
            assert param.type_annotation is None

    def test_typed_params(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of parameters with type annotations."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "typed_params", kind="function")

        assert len(func.parameters) == 3

        # Check parameter types
        param_x = func.parameters[0]
        assert param_x.name == "x"
        assert param_x.type_annotation == "int"

        param_y = func.parameters[1]
        assert param_y.name == "y"
        assert param_y.type_annotation == "str"

        param_z = func.parameters[2]
        assert param_z.name == "z"
        assert param_z.type_annotation == "float"

    def test_default_params(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of parameters with default values."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "default_params", kind="function")

        assert len(func.parameters) == 3

        # Check defaults
        param_a = func.parameters[0]
        assert param_a.name == "a"
        assert param_a.type_annotation == "int"
        assert param_a.default_value == "10"

        param_b = func.parameters[1]
        assert param_b.name == "b"
        assert param_b.type_annotation == "str"
        assert param_b.default_value == "'default'"

        param_c = func.parameters[2]
        assert param_c.name == "c"
        assert param_c.type_annotation == "bool"
        assert param_c.default_value == "True"

    def test_mixed_params(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of mixed parameter types (args, kwargs)."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "mixed_params", kind="function")

        param_names = [p.name for p in func.parameters]
        assert "required" in param_names
        assert "optional" in param_names
        assert "*args" in param_names
        assert "**kwargs" in param_names

    def test_complex_type_annotations(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of complex type annotations (List, Dict, Optional, Union)."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "complex_types", kind="function")

        # Check complex types are parsed
        param_items = func.parameters[0]
        assert param_items.name == "items"
        assert "List" in param_items.type_annotation

        param_mapping = func.parameters[1]
        assert param_mapping.name == "mapping"
        assert "Dict" in param_mapping.type_annotation

        param_optional = func.parameters[2]
        assert param_optional.name == "optional"
        assert "Optional" in param_optional.type_annotation

        param_union = func.parameters[3]
        assert param_union.name == "union"
        assert "Union" in param_union.type_annotation

    def test_keyword_only_params(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of keyword-only parameters."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "keyword_only_params", kind="function")

        # Should have 2 keyword-only params
        assert len(func.parameters) == 2

        param_name = func.parameters[0]
        assert param_name.name == "name"
        assert param_name.type_annotation == "str"

        param_value = func.parameters[1]
        assert param_value.name == "value"
        assert param_value.default_value == "0"

    def test_positional_only_params(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test extraction of positional-only parameters (Python 3.8+)."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "positional_only_params", kind="function")

        # Should have 3 params (a, b positional-only, c regular)
        assert len(func.parameters) == 3

        param_a = func.parameters[0]
        assert param_a.name == "a"
        assert param_a.type_annotation == "int"

    def test_parameter_string_representation(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test Parameter.__str__() method."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "default_params", kind="function")

        # a: int = 10
        param_a_str = str(func.parameters[0])
        assert "a" in param_a_str
        assert "int" in param_a_str
        assert "10" in param_a_str


# =============================================================================
# Return Type Extraction Tests
# =============================================================================


class TestReturnTypeExtraction:
    """Test extraction of return type annotations."""

    def test_returns_int(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of int return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_int", kind="function")

        assert func.return_type == "int"

    def test_returns_str(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of str return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_str", kind="function")

        assert func.return_type == "str"

    def test_returns_none(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of None return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_none", kind="function")

        assert func.return_type == "None"

    def test_returns_optional(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of Optional return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_optional", kind="function")

        assert "Optional" in func.return_type

    def test_returns_list(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of List return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_list", kind="function")

        assert "List" in func.return_type

    def test_returns_dict(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of Dict return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_dict", kind="function")

        assert "Dict" in func.return_type

    def test_returns_tuple(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of Tuple return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_tuple", kind="function")

        assert "Tuple" in func.return_type

    def test_returns_union(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of Union return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_union", kind="function")

        assert "Union" in func.return_type

    def test_returns_any(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test extraction of Any return type."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "returns_any", kind="function")

        assert func.return_type == "Any"

    def test_no_return_type(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test function without return type annotation."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        func = assert_symbol_found(symbols, "no_return_type", kind="function")

        assert func.return_type is None

    def test_complex_return_type(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test complex nested return type (Dict[str, List[int]])."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "complex_types", kind="function")

        assert "Dict" in func.return_type
        assert "List" in func.return_type

    def test_method_return_type(self, ast_parser: ASTParser, sample_return_types_file: Path):
        """Test method return type including self reference."""
        symbols = ast_parser.parse_file_enhanced(sample_return_types_file)
        method = assert_symbol_found(symbols, "method_returns_self", kind="method")

        assert "ClassWithReturnTypes" in method.return_type


# =============================================================================
# Docstring Extraction Tests
# =============================================================================


class TestDocstringExtraction:
    """Test extraction of docstrings."""

    def test_class_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test extraction of class docstring."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        cls = assert_symbol_found(symbols, "DocstringClass", kind="class")

        assert cls.docstring is not None
        assert "A class with a detailed docstring" in cls.docstring
        assert "Attributes:" in cls.docstring

    def test_method_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test extraction of method docstring."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        method = assert_symbol_found(symbols, "method_with_docstring", kind="method")

        assert method.docstring is not None
        assert "A method with a docstring" in method.docstring
        assert "Returns:" in method.docstring

    def test_method_without_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test method without docstring returns None."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        method = assert_symbol_found(symbols, "method_without_docstring", kind="method")

        assert method.docstring is None

    def test_function_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test extraction of function docstring."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        func = assert_symbol_found(symbols, "function_with_docstring", kind="function")

        assert func.docstring is not None
        assert "A function with a docstring" in func.docstring
        assert "Args:" in func.docstring
        assert "Returns:" in func.docstring

    def test_function_without_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test function without docstring returns None."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        func = assert_symbol_found(symbols, "function_without_docstring", kind="function")

        assert func.docstring is None

    def test_short_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test extraction of single-line docstring."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        func = assert_symbol_found(symbols, "function_with_short_docstring", kind="function")

        assert func.docstring == "Short docstring."

    def test_multiline_docstring(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test extraction of multiline docstring preserves content."""
        symbols = ast_parser.parse_file_enhanced(sample_docstrings_file)
        cls = assert_symbol_found(symbols, "DocstringClass", kind="class")

        # Should preserve multiline content
        assert "multiple lines" in cls.docstring


# =============================================================================
# Decorator Extraction Tests
# =============================================================================


class TestDecoratorExtraction:
    """Test extraction of decorators."""

    def test_simple_decorator(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test extraction of simple decorator."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        func = assert_symbol_found(symbols, "decorated_function", kind="function")

        assert "my_decorator" in func.decorators

    def test_decorator_with_args(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test extraction of decorator with arguments."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        func = assert_symbol_found(symbols, "cached_function", kind="function")

        assert "lru_cache" in func.decorators

    def test_property_decorator(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test extraction of @property decorator."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        method = assert_symbol_found(symbols, "name", kind="method")

        assert "property" in method.decorators
        assert method.is_property is True

    def test_staticmethod_decorator(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test extraction of @staticmethod decorator."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        method = assert_symbol_found(symbols, "static_method", kind="method")

        assert "staticmethod" in method.decorators
        assert method.is_static is True

    def test_classmethod_decorator(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test extraction of @classmethod decorator."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        method = assert_symbol_found(symbols, "class_method", kind="method")

        assert "classmethod" in method.decorators
        assert method.is_classmethod is True

    def test_multiple_decorators(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test extraction of multiple decorators on same method."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        method = assert_symbol_found(symbols, "cached_property", kind="method")

        # Should have both property and lru_cache
        assert "property" in method.decorators
        assert "lru_cache" in method.decorators
        assert len(method.decorators) >= 2

    def test_no_decorators(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test function without decorators returns empty list."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "simple_params", kind="function")

        assert func.decorators == []


# =============================================================================
# Call Graph Tests
# =============================================================================


class TestCallGraph:
    """Test extraction of function calls and call graph building."""

    def test_function_calls_extraction(self, ast_parser: ASTParser, sample_calls_file: Path):
        """Test extraction of function calls from function body."""
        symbols = ast_parser.parse_file_enhanced(sample_calls_file)
        func = assert_symbol_found(symbols, "caller_function", kind="function")

        assert "helper_function" in func.calls
        assert "another_helper" in func.calls
        assert "print" in func.calls

    def test_method_calls_extraction(self, ast_parser: ASTParser, sample_calls_file: Path):
        """Test extraction of method calls from method body."""
        symbols = ast_parser.parse_file_enhanced(sample_calls_file)
        method = assert_symbol_found(symbols, "add", kind="method")

        # Should call _validate
        assert "self._validate" in method.calls

    def test_init_calls(self, ast_parser: ASTParser, sample_calls_file: Path):
        """Test extraction of calls in __init__."""
        symbols = ast_parser.parse_file_enhanced(sample_calls_file)
        method = assert_symbol_found(symbols, "__init__", kind="method")

        # Should call reset()
        assert "self.reset" in method.calls

    def test_build_call_graph(self, ast_parser: ASTParser, sample_calls_file: Path):
        """Test building call graph from symbols."""
        symbols = ast_parser.parse_file_enhanced(sample_calls_file)
        call_graph = ast_parser.build_call_graph(symbols)

        assert "caller_function" in call_graph
        assert "helper_function" in call_graph["caller_function"]

    def test_get_callers(self, ast_parser: ASTParser, sample_calls_file: Path):
        """Test finding callers of a function."""
        symbols = ast_parser.parse_file_enhanced(sample_calls_file)
        callers = ast_parser.get_callers(symbols, "helper_function")

        assert "caller_function" in callers

    def test_method_callers(self, ast_parser: ASTParser, sample_calls_file: Path):
        """Test finding callers of a method."""
        symbols = ast_parser.parse_file_enhanced(sample_calls_file)
        callers = ast_parser.get_callers(symbols, "_validate")

        # add() calls _validate
        assert "Calculator.add" in callers


# =============================================================================
# Async Function Tests
# =============================================================================


class TestAsyncFunctions:
    """Test extraction of async functions and methods."""

    def test_async_function_detection(self, ast_parser: ASTParser, sample_async_file: Path):
        """Test that async functions are detected."""
        symbols = ast_parser.parse_file_enhanced(sample_async_file)
        func = assert_symbol_found(symbols, "async_function", kind="async_function")

        assert func.is_async is True

    def test_async_function_with_params(self, ast_parser: ASTParser, sample_async_file: Path):
        """Test async function with parameters."""
        symbols = ast_parser.parse_file_enhanced(sample_async_file)
        func = assert_symbol_found(symbols, "async_with_params", kind="async_function")

        assert func.is_async is True
        assert len(func.parameters) == 2

        param_url = func.parameters[0]
        assert param_url.name == "url"
        assert param_url.type_annotation == "str"

    def test_async_method_detection(self, ast_parser: ASTParser, sample_async_file: Path):
        """Test that async methods are detected."""
        symbols = ast_parser.parse_file_enhanced(sample_async_file)
        method = assert_symbol_found(symbols, "fetch", kind="async_method")

        assert method.is_async is True
        assert method.parent_class == "AsyncClass"

    def test_sync_method_in_async_class(self, ast_parser: ASTParser, sample_async_file: Path):
        """Test sync method in class with async methods."""
        symbols = ast_parser.parse_file_enhanced(sample_async_file)
        method = assert_symbol_found(symbols, "sync_method", kind="method")

        assert method.is_async is False
        assert method.parent_class == "AsyncClass"


# =============================================================================
# EnhancedSymbol Tests
# =============================================================================


class TestEnhancedSymbol:
    """Test EnhancedSymbol properties and methods."""

    def test_signature_property(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test EnhancedSymbol.signature property."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "typed_params", kind="function")

        signature = func.signature
        assert "typed_params" in signature
        assert "x: int" in signature
        assert "y: str" in signature
        assert "-> bool" in signature

    def test_qualified_name_function(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test qualified_name for standalone function."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "typed_params", kind="function")

        assert func.qualified_name == "typed_params"

    def test_qualified_name_method(self, ast_parser: ASTParser, sample_decorators_file: Path):
        """Test qualified_name for class method."""
        symbols = ast_parser.parse_file_enhanced(sample_decorators_file)
        method = assert_symbol_found(symbols, "static_method", kind="method")

        assert method.qualified_name == "DecoratedClass.static_method"

    def test_to_basic_symbol(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test conversion to basic Symbol."""
        symbols = ast_parser.parse_file_enhanced(sample_params_file)
        func = assert_symbol_found(symbols, "simple_params", kind="function")

        basic = func.to_basic_symbol()

        assert isinstance(basic, Symbol)
        assert basic.name == func.name
        assert basic.kind == func.kind
        assert basic.line == func.line
        assert basic.file_path == func.file_path

    def test_line_numbers(self, ast_parser: ASTParser, temp_dir: Path):
        """Test line number accuracy."""
        code = '''# Line 1
# Line 2
class MyClass:  # Line 3
    pass

def my_function():  # Line 6
    pass
'''
        py_file = temp_dir / "lines.py"
        py_file.write_text(code)

        symbols = ast_parser.parse_file_enhanced(py_file)

        my_class = assert_symbol_found(symbols, "MyClass", kind="class")
        assert my_class.line == 3

        my_function = assert_symbol_found(symbols, "my_function", kind="function")
        assert my_function.line == 6

    def test_end_line_numbers(self, ast_parser: ASTParser, temp_dir: Path):
        """Test end_line numbers are extracted."""
        code = '''class MultiLine:
    \"\"\"A class.\"\"\"

    def method(self):
        pass
'''
        py_file = temp_dir / "multiline.py"
        py_file.write_text(code)

        symbols = ast_parser.parse_file_enhanced(py_file)

        cls = assert_symbol_found(symbols, "MultiLine", kind="class")
        assert cls.end_line is not None
        assert cls.end_line > cls.line


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling for malformed and edge cases."""

    def test_malformed_file(self, ast_parser: ASTParser, sample_malformed_file: Path):
        """Test that malformed files are handled gracefully."""
        # Should not raise exception
        symbols = ast_parser.parse_file_enhanced(sample_malformed_file)

        # Should return empty list (syntax error prevents parsing)
        assert isinstance(symbols, list)

    def test_nonexistent_file(self, ast_parser: ASTParser, temp_dir: Path):
        """Test that non-existent files return empty list."""
        nonexistent = temp_dir / "does_not_exist.py"
        symbols = ast_parser.parse_file_enhanced(nonexistent)

        assert symbols == []

    def test_empty_file(self, ast_parser: ASTParser, temp_dir: Path):
        """Test that empty files are handled gracefully."""
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")

        symbols = ast_parser.parse_file_enhanced(empty_file)
        assert symbols == []

    def test_comments_only_file(self, ast_parser: ASTParser, temp_dir: Path):
        """Test file with only comments."""
        comments_file = temp_dir / "comments.py"
        comments_file.write_text("# Just a comment\n# Another comment\n")

        symbols = ast_parser.parse_file_enhanced(comments_file)
        assert symbols == []

    def test_unicode_content(self, ast_parser: ASTParser, temp_dir: Path):
        """Test file with unicode content."""
        unicode_file = temp_dir / "unicode.py"
        unicode_file.write_text('''
class UnicodeClass:
    """Unicode: \u4e2d\u6587 \u65e5\u672c\u8a9e"""

    def greet(self) -> str:
        return "\u3053\u3093\u306b\u3061\u306f"
''')

        symbols = ast_parser.parse_file_enhanced(unicode_file)

        cls = assert_symbol_found(symbols, "UnicodeClass", kind="class")
        assert cls.docstring is not None


# =============================================================================
# Directory Parsing Tests
# =============================================================================


class TestDirectoryParsing:
    """Test parsing entire directories."""

    def test_parse_directory(self, ast_parser: ASTParser, temp_dir: Path):
        """Test parsing a directory with multiple files."""
        # Create files
        (temp_dir / "main.py").write_text("class Main: pass\n")
        (temp_dir / "utils.py").write_text("def helper(): pass\n")

        subdir = temp_dir / "src"
        subdir.mkdir()
        (subdir / "module.py").write_text("class Module: pass\n")

        symbols = ast_parser.parse_directory(temp_dir, enhanced=True)

        # Should find all symbols
        symbol_names = [s.name for s in symbols]
        assert "Main" in symbol_names
        assert "helper" in symbol_names
        assert "Module" in symbol_names

    def test_parse_directory_excludes_pycache(self, ast_parser: ASTParser, temp_dir: Path):
        """Test that __pycache__ directories are excluded."""
        (temp_dir / "main.py").write_text("class Main: pass")

        pycache = temp_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.py").write_text("class Cached: pass")

        symbols = ast_parser.parse_directory(temp_dir, enhanced=True)

        file_paths = [s.file_path for s in symbols]
        assert not any("__pycache__" in fp for fp in file_paths)

    def test_parse_directory_basic_mode(self, ast_parser: ASTParser, temp_dir: Path):
        """Test directory parsing in basic (non-enhanced) mode."""
        (temp_dir / "main.py").write_text("class Main: pass\n")

        symbols = ast_parser.parse_directory(temp_dir, enhanced=False)

        assert len(symbols) > 0
        assert isinstance(symbols[0], Symbol)


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_parse_python_file(self, sample_params_file: Path):
        """Test parse_python_file convenience function."""
        symbols = parse_python_file(sample_params_file)

        assert len(symbols) > 0
        assert isinstance(symbols[0], EnhancedSymbol)

    def test_parse_python_directory(self, temp_dir: Path):
        """Test parse_python_directory convenience function."""
        (temp_dir / "main.py").write_text("def main(): pass\n")

        symbols = parse_python_directory(temp_dir)

        assert len(symbols) > 0
        assert isinstance(symbols[0], EnhancedSymbol)


# =============================================================================
# Basic Mode Tests (Backward Compatibility)
# =============================================================================


class TestBasicMode:
    """Test basic parsing mode for backward compatibility."""

    def test_basic_mode_returns_symbol(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test that basic mode returns Symbol objects."""
        symbols = ast_parser.parse_file(sample_params_file, enhanced=False)

        assert len(symbols) > 0
        assert isinstance(symbols[0], Symbol)

    def test_basic_mode_extracts_classes(self, ast_parser: ASTParser, sample_docstrings_file: Path):
        """Test that basic mode extracts classes."""
        symbols = ast_parser.parse_file(sample_docstrings_file, enhanced=False)

        class_names = [s.name for s in symbols if s.kind == "class"]
        assert "DocstringClass" in class_names

    def test_basic_mode_extracts_functions(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test that basic mode extracts functions."""
        symbols = ast_parser.parse_file(sample_params_file, enhanced=False)

        function_names = [s.name for s in symbols if s.kind == "function"]
        assert "simple_params" in function_names

    def test_default_is_enhanced(self, ast_parser: ASTParser, sample_params_file: Path):
        """Test that default parsing mode is enhanced."""
        symbols = ast_parser.parse_file(sample_params_file)

        assert len(symbols) > 0
        assert isinstance(symbols[0], EnhancedSymbol)
