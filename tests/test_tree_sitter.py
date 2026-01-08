"""Unit tests for tree-sitter parsing.

This module tests the TreeSitterParser class for multi-language support:
- Python: class_definition, function_definition
- TypeScript: class_declaration, function_declaration, arrow functions
- JavaScript: class, function, arrow functions, async functions

Test coverage includes:
- Symbol extraction (classes, functions, methods)
- Line number accuracy
- Error handling for malformed files
- Directory parsing
- TSSymbol to EnhancedSymbol conversion
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

# Import tree_sitter module directly to avoid heavy dependencies from skills_fabric.__init__
# This uses importlib to bypass the normal import chain
_src_path = Path(__file__).parent.parent / "src"

# First, ensure observability.logging is available (tree_sitter depends on it)
_logging_path = _src_path / "skills_fabric" / "observability" / "logging.py"
_logging_spec = importlib.util.spec_from_file_location("skills_fabric.observability.logging", _logging_path)
_logging_module = importlib.util.module_from_spec(_logging_spec)
sys.modules["skills_fabric.observability.logging"] = _logging_module
_logging_spec.loader.exec_module(_logging_module)

# Now import the tree_sitter module
_tree_sitter_path = _src_path / "skills_fabric" / "analyze" / "tree_sitter" / "__init__.py"
_spec = importlib.util.spec_from_file_location("skills_fabric.analyze.tree_sitter", _tree_sitter_path)
_tree_sitter_module = importlib.util.module_from_spec(_spec)
sys.modules["skills_fabric.analyze.tree_sitter"] = _tree_sitter_module
_spec.loader.exec_module(_tree_sitter_module)

TreeSitterParser = _tree_sitter_module.TreeSitterParser
TSSymbol = _tree_sitter_module.TSSymbol


def _has_full_package() -> bool:
    """Check if the full skills_fabric package is available (including kuzu)."""
    try:
        import kuzu
        return True
    except ImportError:
        return False


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
# Local Fixtures (avoid importing from conftest to prevent heavy deps)
# =============================================================================

SAMPLE_PYTHON_CODE = '''"""Sample Python module for testing."""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SampleClass:
    """A sample class with various attributes."""
    name: str
    value: int = 0
    items: Optional[List[str]] = None

    def get_name(self) -> str:
        """Return the name."""
        return self.name

    def add_item(self, item: str) -> None:
        """Add an item to the list."""
        if self.items is None:
            self.items = []
        self.items.append(item)

    @property
    def item_count(self) -> int:
        """Return the number of items."""
        return len(self.items) if self.items else 0


def standalone_function(x: int, y: int = 10) -> int:
    """A standalone function with parameters."""
    return x + y


async def async_function(data: dict) -> list:
    """An async function for testing."""
    return list(data.keys())


class AnotherClass:
    """Another class for testing inheritance patterns."""

    def __init__(self, config: dict):
        self.config = config

    @staticmethod
    def static_method() -> str:
        return "static"

    @classmethod
    def class_method(cls) -> str:
        return cls.__name__
'''

SAMPLE_TYPESCRIPT_CODE = '''/**
 * Sample TypeScript module for testing.
 */

interface User {
    id: number;
    name: string;
    email?: string;
}

class UserService {
    private users: User[] = [];

    constructor(initialUsers?: User[]) {
        if (initialUsers) {
            this.users = initialUsers;
        }
    }

    getUser(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }

    addUser(user: User): void {
        this.users.push(user);
    }

    get userCount(): number {
        return this.users.length;
    }
}

function createUser(name: string, id: number): User {
    return { id, name };
}

const arrowFunction = (x: number): number => x * 2;

export { UserService, createUser, arrowFunction };
'''

SAMPLE_JAVASCRIPT_CODE = '''/**
 * Sample JavaScript module for testing.
 */

class DataProcessor {
    constructor(options = {}) {
        this.options = options;
        this.data = [];
    }

    process(input) {
        return input.map(item => this.transform(item));
    }

    transform(item) {
        return { ...item, processed: true };
    }

    static create(options) {
        return new DataProcessor(options);
    }
}

function processData(data, callback) {
    return data.map(callback);
}

const arrowProcessor = (data) => data.filter(d => d.active);

async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}

module.exports = { DataProcessor, processData, arrowProcessor, fetchData };
'''

SAMPLE_MALFORMED_CODE = '''
# This is intentionally malformed Python
def broken_function(
    # Missing closing paren and body
class incomplete:
    pass
'''


@pytest.fixture
def tree_sitter_parser() -> TreeSitterParser:
    """Create a TreeSitterParser instance."""
    return TreeSitterParser()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory."""
    return tmp_path


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(SAMPLE_PYTHON_CODE)
    return file_path


@pytest.fixture
def sample_typescript_file(tmp_path: Path) -> Path:
    """Create a sample TypeScript file for testing."""
    file_path = tmp_path / "sample.ts"
    file_path.write_text(SAMPLE_TYPESCRIPT_CODE)
    return file_path


@pytest.fixture
def sample_javascript_file(tmp_path: Path) -> Path:
    """Create a sample JavaScript file for testing."""
    file_path = tmp_path / "sample.js"
    file_path.write_text(SAMPLE_JAVASCRIPT_CODE)
    return file_path


@pytest.fixture
def sample_malformed_file(tmp_path: Path) -> Path:
    """Create a malformed Python file for error handling tests."""
    file_path = tmp_path / "malformed.py"
    file_path.write_text(SAMPLE_MALFORMED_CODE)
    return file_path


@pytest.fixture
def sample_project_dir(tmp_path: Path) -> Path:
    """Create a sample project directory with multiple files."""
    # Create Python files
    (tmp_path / "main.py").write_text(SAMPLE_PYTHON_CODE)
    (tmp_path / "utils.py").write_text('"""Utils module."""\n\ndef helper(): pass\n')

    # Create subdirectory with more files
    subdir = tmp_path / "src"
    subdir.mkdir()
    (subdir / "module.py").write_text('"""Module."""\n\nclass Module: pass\n')
    (subdir / "app.ts").write_text(SAMPLE_TYPESCRIPT_CODE)
    (subdir / "index.js").write_text(SAMPLE_JAVASCRIPT_CODE)

    return tmp_path


# =============================================================================
# Python Parsing Tests
# =============================================================================


class TestPythonParsing:
    """Test tree-sitter parsing for Python files."""

    def test_parse_python_class(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that Python classes are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        # Find SampleClass
        sample_class = assert_symbol_found(symbols, "SampleClass", kind="class")
        assert sample_class.line > 0
        assert sample_class.end_line >= sample_class.line
        assert sample_class.file_path == str(sample_python_file)

    def test_parse_python_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that Python standalone functions are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        # Find standalone_function
        func = assert_symbol_found(symbols, "standalone_function", kind="function")
        assert func.line > 0
        assert func.file_path == str(sample_python_file)

    def test_parse_python_async_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that Python async functions are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        # Find async_function
        async_func = assert_symbol_found(symbols, "async_function", kind="function")
        assert async_func.line > 0

    def test_parse_python_methods(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that Python class methods are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        # Methods should be extracted
        method_names = [s.name for s in symbols if s.kind == "function"]
        assert "get_name" in method_names
        assert "add_item" in method_names
        assert "item_count" in method_names  # property method

    def test_parse_python_multiple_classes(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that multiple Python classes are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        # Should find both classes
        class_names = [s.name for s in symbols if s.kind == "class"]
        assert "SampleClass" in class_names
        assert "AnotherClass" in class_names

    def test_parse_python_static_classmethod(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that static and class methods are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        method_names = [s.name for s in symbols if s.kind == "function"]
        assert "static_method" in method_names
        assert "class_method" in method_names
        assert "__init__" in method_names


# =============================================================================
# TypeScript Parsing Tests
# =============================================================================


class TestTypeScriptParsing:
    """Test tree-sitter parsing for TypeScript files."""

    def test_parse_typescript_class(
        self, tree_sitter_parser: "TreeSitterParser", sample_typescript_file: Path
    ):
        """Test that TypeScript classes are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_typescript_file)

        # Find UserService class
        user_service = assert_symbol_found(symbols, "UserService", kind="class")
        assert user_service.line > 0
        assert user_service.end_line >= user_service.line

    def test_parse_typescript_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_typescript_file: Path
    ):
        """Test that TypeScript functions are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_typescript_file)

        # Find createUser function
        create_user = assert_symbol_found(symbols, "createUser", kind="function")
        assert create_user.line > 0

    def test_parse_typescript_methods(
        self, tree_sitter_parser: "TreeSitterParser", sample_typescript_file: Path
    ):
        """Test that TypeScript class methods are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_typescript_file)

        method_names = [s.name for s in symbols if s.kind == "function"]
        assert "getUser" in method_names
        assert "addUser" in method_names

    def test_parse_typescript_arrow_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_typescript_file: Path
    ):
        """Test that TypeScript arrow functions are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_typescript_file)

        # Arrow function assigned to const should be found
        arrow_func = assert_symbol_found(symbols, "arrowFunction", kind="function")
        assert arrow_func.line > 0

    def test_typescript_line_numbers(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that TypeScript line numbers are accurate."""
        ts_code = """// Line 1
class MyClass {
    // Line 3
    myMethod() {
        // Line 5
    }
}
// Line 8
function standalone() {}
"""
        ts_file = temp_dir / "test.ts"
        ts_file.write_text(ts_code)

        symbols = tree_sitter_parser.parse_file(ts_file)

        # Class should be on line 2
        my_class = assert_symbol_found(symbols, "MyClass", kind="class")
        assert my_class.line == 2

        # Function should be on line 9
        standalone = assert_symbol_found(symbols, "standalone", kind="function")
        assert standalone.line == 9


# =============================================================================
# JavaScript Parsing Tests
# =============================================================================


class TestJavaScriptParsing:
    """Test tree-sitter parsing for JavaScript files."""

    def test_parse_javascript_class(
        self, tree_sitter_parser: "TreeSitterParser", sample_javascript_file: Path
    ):
        """Test that JavaScript classes are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_javascript_file)

        # Find DataProcessor class
        data_processor = assert_symbol_found(symbols, "DataProcessor", kind="class")
        assert data_processor.line > 0
        assert data_processor.end_line >= data_processor.line

    def test_parse_javascript_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_javascript_file: Path
    ):
        """Test that JavaScript functions are extracted correctly."""
        symbols = tree_sitter_parser.parse_file(sample_javascript_file)

        # Find processData function
        process_data = assert_symbol_found(symbols, "processData", kind="function")
        assert process_data.line > 0

    def test_parse_javascript_async_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_javascript_file: Path
    ):
        """Test that JavaScript async functions are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_javascript_file)

        # Find fetchData async function
        fetch_data = assert_symbol_found(symbols, "fetchData", kind="function")
        assert fetch_data.line > 0

    def test_parse_javascript_arrow_function(
        self, tree_sitter_parser: "TreeSitterParser", sample_javascript_file: Path
    ):
        """Test that JavaScript arrow functions are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_javascript_file)

        # Arrow function assigned to const
        arrow_proc = assert_symbol_found(symbols, "arrowProcessor", kind="function")
        assert arrow_proc.line > 0

    def test_parse_javascript_class_methods(
        self, tree_sitter_parser: "TreeSitterParser", sample_javascript_file: Path
    ):
        """Test that JavaScript class methods are extracted."""
        symbols = tree_sitter_parser.parse_file(sample_javascript_file)

        method_names = [s.name for s in symbols if s.kind == "function"]
        assert "process" in method_names
        assert "transform" in method_names
        assert "create" in method_names  # static method

    def test_javascript_jsx_support(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that .jsx files are parsed correctly."""
        jsx_code = """
import React from 'react';

class MyComponent extends React.Component {
    render() {
        return <div>Hello</div>;
    }
}

function FunctionalComponent(props) {
    return <span>{props.text}</span>;
}

const ArrowComponent = (props) => <div>{props.children}</div>;

export default MyComponent;
"""
        jsx_file = temp_dir / "component.jsx"
        jsx_file.write_text(jsx_code)

        symbols = tree_sitter_parser.parse_file(jsx_file)

        # Should find class and functions
        class_names = [s.name for s in symbols if s.kind == "class"]
        func_names = [s.name for s in symbols if s.kind == "function"]

        assert "MyComponent" in class_names
        assert "FunctionalComponent" in func_names
        assert "ArrowComponent" in func_names


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling for malformed files and edge cases."""

    def test_parse_malformed_python(
        self, tree_sitter_parser: "TreeSitterParser", sample_malformed_file: Path
    ):
        """Test that malformed Python files are handled gracefully."""
        # Should not raise an exception
        symbols = tree_sitter_parser.parse_file(sample_malformed_file)

        # Should return some symbols (tree-sitter is error-tolerant)
        # The malformed file has 'class incomplete' which should be found
        assert isinstance(symbols, list)
        # Note: tree-sitter may still extract partial symbols from malformed code

    def test_parse_nonexistent_file(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that non-existent files return empty list."""
        nonexistent = temp_dir / "does_not_exist.py"
        symbols = tree_sitter_parser.parse_file(nonexistent)

        assert symbols == []

    def test_parse_unsupported_extension(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that unsupported file extensions return empty list."""
        unsupported = temp_dir / "file.cpp"
        unsupported.write_text("int main() { return 0; }")

        symbols = tree_sitter_parser.parse_file(unsupported)
        assert symbols == []

    def test_parse_empty_file(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that empty files are handled gracefully."""
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")

        symbols = tree_sitter_parser.parse_file(empty_file)
        assert symbols == []

    def test_parse_file_with_syntax_error(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test parsing file with syntax errors."""
        bad_syntax = temp_dir / "bad_syntax.py"
        bad_syntax.write_text("""
def incomplete(
    # Missing closing paren

class AlsoIncomplete
    # Missing colon

def valid_function():
    pass
""")
        # Should not raise, may extract partial symbols
        symbols = tree_sitter_parser.parse_file(bad_syntax)
        assert isinstance(symbols, list)

    def test_parse_file_with_unicode(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test parsing files with unicode content."""
        unicode_file = temp_dir / "unicode.py"
        unicode_file.write_text("""
class UnicodeClass:
    '''Unicode docstring: \u4e2d\u6587'''

    def greet(self):
        return "\u3053\u3093\u306b\u3061\u306f"  # Japanese
""")
        symbols = tree_sitter_parser.parse_file(unicode_file)

        # Should find the class
        unicode_class = assert_symbol_found(symbols, "UnicodeClass", kind="class")
        assert unicode_class.line > 0


# =============================================================================
# Directory Parsing Tests
# =============================================================================


class TestDirectoryParsing:
    """Test parsing entire directories."""

    def test_parse_directory_all_languages(
        self, tree_sitter_parser: "TreeSitterParser", sample_project_dir: Path
    ):
        """Test parsing a directory with multiple languages."""
        symbols = tree_sitter_parser.parse_directory(sample_project_dir)

        # Should find symbols from all supported languages
        assert len(symbols) > 0

        # Get unique file extensions
        file_extensions = {
            Path(s.file_path).suffix.lower() for s in symbols
        }

        # Should have found Python, TypeScript, and JavaScript files
        assert ".py" in file_extensions
        assert ".ts" in file_extensions
        assert ".js" in file_extensions

    def test_parse_directory_excludes_pycache(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that __pycache__ directories are excluded."""
        # Create a Python file in root
        (temp_dir / "main.py").write_text("class Main: pass")

        # Create __pycache__ with a file
        pycache = temp_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "main.cpython-311.pyc.py").write_text("class Cached: pass")

        symbols = tree_sitter_parser.parse_directory(temp_dir)

        # Should not include anything from __pycache__
        file_paths = [s.file_path for s in symbols]
        assert not any("__pycache__" in fp for fp in file_paths)

    def test_parse_directory_excludes_node_modules(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that node_modules directories are excluded."""
        # Create a JS file in root
        (temp_dir / "app.js").write_text("class App {}")

        # Create node_modules with files
        node_modules = temp_dir / "node_modules" / "some_package"
        node_modules.mkdir(parents=True)
        (node_modules / "index.js").write_text("class Package {}")

        symbols = tree_sitter_parser.parse_directory(temp_dir)

        # Should not include anything from node_modules
        file_paths = [s.file_path for s in symbols]
        assert not any("node_modules" in fp for fp in file_paths)

    def test_parse_empty_directory(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test parsing an empty directory."""
        symbols = tree_sitter_parser.parse_directory(temp_dir)
        assert symbols == []

    def test_parse_directory_recursive(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test that subdirectories are parsed recursively."""
        # Create nested structure
        (temp_dir / "root.py").write_text("class Root: pass")
        subdir1 = temp_dir / "sub1"
        subdir1.mkdir()
        (subdir1 / "module1.py").write_text("class Module1: pass")
        subdir2 = subdir1 / "sub2"
        subdir2.mkdir()
        (subdir2 / "module2.py").write_text("class Module2: pass")

        symbols = tree_sitter_parser.parse_directory(temp_dir)

        class_names = [s.name for s in symbols if s.kind == "class"]
        assert "Root" in class_names
        assert "Module1" in class_names
        assert "Module2" in class_names


# =============================================================================
# TSSymbol Tests
# =============================================================================


class TestTSSymbol:
    """Test TSSymbol dataclass and conversion methods."""

    def test_ts_symbol_attributes(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test that TSSymbol has all expected attributes."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)
        assert len(symbols) > 0

        symbol = symbols[0]
        assert hasattr(symbol, "name")
        assert hasattr(symbol, "kind")
        assert hasattr(symbol, "file_path")
        assert hasattr(symbol, "line")
        assert hasattr(symbol, "end_line")

    @pytest.mark.skipif(
        not _has_full_package(),
        reason="Requires full package with kuzu dependency for EnhancedSymbol import"
    )
    def test_ts_symbol_to_enhanced(
        self, tree_sitter_parser: TreeSitterParser, sample_python_file: Path
    ):
        """Test TSSymbol.to_enhanced() conversion."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)
        sample_class = assert_symbol_found(symbols, "SampleClass", kind="class")

        # Convert to EnhancedSymbol
        enhanced = sample_class.to_enhanced()

        # Check basic attributes are preserved
        assert enhanced.name == sample_class.name
        assert enhanced.kind == sample_class.kind
        assert enhanced.file_path == sample_class.file_path
        assert enhanced.line == sample_class.line
        assert enhanced.end_line == sample_class.end_line

    @pytest.mark.skipif(
        not _has_full_package(),
        reason="Requires full package with kuzu dependency for EnhancedSymbol import"
    )
    def test_ts_symbol_enhanced_has_empty_rich_fields(
        self, tree_sitter_parser: TreeSitterParser, sample_python_file: Path
    ):
        """Test that EnhancedSymbol from TSSymbol has empty rich fields."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)
        func = assert_symbol_found(symbols, "standalone_function", kind="function")

        enhanced = func.to_enhanced()

        # Rich fields should be empty/None (tree-sitter doesn't extract them)
        assert enhanced.parameters == []
        assert enhanced.return_type is None
        assert enhanced.docstring is None
        assert enhanced.decorators == []
        assert enhanced.calls == []


# =============================================================================
# is_supported Tests
# =============================================================================


class TestIsSupported:
    """Test the is_supported method."""

    def test_supported_python(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .py files are supported."""
        assert tree_sitter_parser.is_supported(Path("test.py")) is True

    def test_supported_typescript(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .ts files are supported."""
        assert tree_sitter_parser.is_supported(Path("test.ts")) is True

    def test_supported_tsx(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .tsx files are supported."""
        assert tree_sitter_parser.is_supported(Path("test.tsx")) is True

    def test_supported_javascript(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .js files are supported."""
        assert tree_sitter_parser.is_supported(Path("test.js")) is True

    def test_supported_jsx(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .jsx files are supported."""
        assert tree_sitter_parser.is_supported(Path("test.jsx")) is True

    def test_unsupported_cpp(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .cpp files are not supported."""
        assert tree_sitter_parser.is_supported(Path("test.cpp")) is False

    def test_unsupported_java(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .java files are not supported."""
        assert tree_sitter_parser.is_supported(Path("test.java")) is False

    def test_unsupported_rust(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that .rs files are not supported."""
        assert tree_sitter_parser.is_supported(Path("test.rs")) is False

    def test_case_insensitive_extension(self, tree_sitter_parser: "TreeSitterParser"):
        """Test that extension checking is case-insensitive."""
        assert tree_sitter_parser.is_supported(Path("test.PY")) is True
        assert tree_sitter_parser.is_supported(Path("test.Ts")) is True
        assert tree_sitter_parser.is_supported(Path("test.JS")) is True


# =============================================================================
# Line Number Accuracy Tests
# =============================================================================


class TestLineNumberAccuracy:
    """Test that line numbers are accurate (1-indexed)."""

    def test_python_line_numbers(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test Python line number accuracy."""
        py_code = """# Line 1
# Line 2
class MyClass:  # Line 3
    pass

def my_function():  # Line 6
    pass
"""
        py_file = temp_dir / "lines.py"
        py_file.write_text(py_code)

        symbols = tree_sitter_parser.parse_file(py_file)

        my_class = assert_symbol_found(symbols, "MyClass", kind="class")
        assert my_class.line == 3

        my_function = assert_symbol_found(symbols, "my_function", kind="function")
        assert my_function.line == 6

    def test_javascript_line_numbers(
        self, tree_sitter_parser: "TreeSitterParser", temp_dir: Path
    ):
        """Test JavaScript line number accuracy."""
        js_code = """// Line 1
class JsClass {  // Line 2
    // Line 3
}

function jsFunction() {  // Line 6
}

const arrowFunc = () => {};  // Line 9
"""
        js_file = temp_dir / "lines.js"
        js_file.write_text(js_code)

        symbols = tree_sitter_parser.parse_file(js_file)

        js_class = assert_symbol_found(symbols, "JsClass", kind="class")
        assert js_class.line == 2

        js_function = assert_symbol_found(symbols, "jsFunction", kind="function")
        assert js_function.line == 6

        arrow_func = assert_symbol_found(symbols, "arrowFunc", kind="function")
        assert arrow_func.line == 9


# =============================================================================
# Symbol Count Tests
# =============================================================================


class TestSymbolCounts:
    """Test that the correct number of symbols are extracted."""

    def test_python_symbol_count(
        self, tree_sitter_parser: "TreeSitterParser", sample_python_file: Path
    ):
        """Test symbol count from sample Python file."""
        symbols = tree_sitter_parser.parse_file(sample_python_file)

        # Count classes and functions
        classes = [s for s in symbols if s.kind == "class"]
        functions = [s for s in symbols if s.kind == "function"]

        # Sample has: SampleClass, AnotherClass
        assert len(classes) >= 2

        # Sample has many functions/methods
        # get_name, add_item, item_count, standalone_function, async_function,
        # __init__, static_method, class_method
        assert len(functions) >= 6

    def test_typescript_symbol_count(
        self, tree_sitter_parser: "TreeSitterParser", sample_typescript_file: Path
    ):
        """Test symbol count from sample TypeScript file."""
        symbols = tree_sitter_parser.parse_file(sample_typescript_file)

        classes = [s for s in symbols if s.kind == "class"]
        functions = [s for s in symbols if s.kind == "function"]

        # Sample has: UserService
        assert len(classes) >= 1

        # Sample has: getUser, addUser, createUser, arrowFunction, etc.
        assert len(functions) >= 3

    def test_javascript_symbol_count(
        self, tree_sitter_parser: "TreeSitterParser", sample_javascript_file: Path
    ):
        """Test symbol count from sample JavaScript file."""
        symbols = tree_sitter_parser.parse_file(sample_javascript_file)

        classes = [s for s in symbols if s.kind == "class"]
        functions = [s for s in symbols if s.kind == "function"]

        # Sample has: DataProcessor
        assert len(classes) >= 1

        # Sample has: process, transform, create, processData, arrowProcessor, fetchData
        assert len(functions) >= 4
