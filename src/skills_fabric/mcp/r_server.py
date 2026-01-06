"""FastMCP R Language Server - First MCP Server for R.

Based on research: No MCP server exists for R - first-mover opportunity.
Provides R code intelligence via tree-sitter and CRAN metadata.

Features:
- Parse R code (functions, S3/S4/R6 classes)
- Extract symbols and documentation
- CRAN/Bioconductor package metadata
- R-specific code patterns
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path
import re
import json

# Try to import MCP SDK (FastMCP for decorator API)
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Stub for development/testing without MCP
    class FastMCP:
        def __init__(self, name: str = ""):
            self.name = name
            self._tools = {}
            self._resources = {}
            self._prompts = {}

        def tool(self):
            def decorator(f):
                self._tools[f.__name__] = f
                return f
            return decorator

        def resource(self, uri: str):
            def decorator(f):
                self._resources[uri] = f
                return f
            return decorator

        def prompt(self):
            def decorator(f):
                self._prompts[f.__name__] = f
                return f
            return decorator

        def run(self):
            raise RuntimeError("MCP SDK not installed")


# Try tree-sitter for R parsing
try:
    import tree_sitter_r as tsr
    from tree_sitter import Language, Parser
    TREE_SITTER_R_AVAILABLE = True
except ImportError:
    TREE_SITTER_R_AVAILABLE = False


@dataclass
class RSymbol:
    """An R symbol extracted from source code."""
    name: str
    kind: str  # function, s3_method, s4_class, r6_class, variable
    file_path: str
    line_number: int
    documentation: Optional[str] = None
    parameters: list[str] = field(default_factory=list)
    returns: Optional[str] = None
    package: Optional[str] = None

    def to_citation(self) -> str:
        """Generate file:line citation."""
        return f"{self.file_path}:{self.line_number}"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'kind': self.kind,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'documentation': self.documentation,
            'parameters': self.parameters,
            'returns': self.returns,
            'package': self.package,
            'citation': self.to_citation(),
        }


@dataclass
class RPackageInfo:
    """CRAN/Bioconductor package metadata."""
    name: str
    version: str
    title: str
    description: str
    depends: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    maintainer: Optional[str] = None
    url: Optional[str] = None


class RCodeParser:
    """Parse R code using tree-sitter or regex fallback."""

    def __init__(self):
        self.parser = None
        self.language = None

        if TREE_SITTER_R_AVAILABLE:
            try:
                self.language = Language(tsr.language())
                self.parser = Parser(self.language)
            except Exception:
                pass

    def parse(self, code: str, file_path: str = "unknown.R") -> list[RSymbol]:
        """Parse R code and extract symbols."""
        if self.parser:
            return self._parse_with_tree_sitter(code, file_path)
        return self._parse_with_regex(code, file_path)

    def _parse_with_tree_sitter(self, code: str, file_path: str) -> list[RSymbol]:
        """Parse using tree-sitter."""
        symbols = []
        tree = self.parser.parse(code.encode())

        # Query for function definitions
        func_query = self.language.query("""
            (binary_operator
                lhs: (identifier) @func_name
                operator: "<-"
                rhs: (function_definition
                    parameters: (parameters) @params
                    body: (_) @body))
        """)

        captures = func_query.captures(tree.root_node)

        current_func = {}
        for node, name in captures:
            if name == "func_name":
                if current_func.get('name'):
                    symbols.append(self._create_symbol(current_func, file_path))
                current_func = {
                    'name': code[node.start_byte:node.end_byte],
                    'line': node.start_point[0] + 1,
                    'kind': 'function',
                }
            elif name == "params":
                params_text = code[node.start_byte:node.end_byte]
                current_func['params'] = self._extract_params(params_text)

        if current_func.get('name'):
            symbols.append(self._create_symbol(current_func, file_path))

        # Also use regex for comprehensive extraction
        symbols.extend(self._parse_with_regex(code, file_path))

        # Deduplicate by name
        seen = set()
        unique = []
        for sym in symbols:
            if sym.name not in seen:
                seen.add(sym.name)
                unique.append(sym)

        return unique

    def _parse_with_regex(self, code: str, file_path: str) -> list[RSymbol]:
        """Fallback regex-based parsing."""
        symbols = []
        lines = code.split('\n')

        # Pattern: name <- function(params) or name = function(params)
        func_pattern = re.compile(
            r'^([a-zA-Z_.][a-zA-Z0-9_.]*)\s*(<-|=)\s*function\s*\(([^)]*)\)',
            re.MULTILINE
        )

        for match in func_pattern.finditer(code):
            name = match.group(1)
            params_str = match.group(3)
            line_num = code[:match.start()].count('\n') + 1

            # Check for roxygen comments above
            doc = self._extract_roxygen(lines, line_num - 1)

            symbols.append(RSymbol(
                name=name,
                kind=self._infer_kind(name),
                file_path=file_path,
                line_number=line_num,
                documentation=doc,
                parameters=self._extract_params(params_str),
            ))

        # S4 class definitions: setClass("ClassName", ...)
        s4_pattern = re.compile(r'setClass\s*\(\s*["\']([^"\']+)["\']')
        for match in s4_pattern.finditer(code):
            name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            symbols.append(RSymbol(
                name=name,
                kind='s4_class',
                file_path=file_path,
                line_number=line_num,
            ))

        # R6 class definitions: R6Class("ClassName", ...)
        r6_pattern = re.compile(r'R6Class\s*\(\s*["\']([^"\']+)["\']')
        for match in r6_pattern.finditer(code):
            name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            symbols.append(RSymbol(
                name=name,
                kind='r6_class',
                file_path=file_path,
                line_number=line_num,
            ))

        # S3 method definitions: func.classname <- function(...)
        s3_pattern = re.compile(
            r'^([a-zA-Z_.]+)\.([a-zA-Z_.]+)\s*(<-|=)\s*function',
            re.MULTILINE
        )
        for match in s3_pattern.finditer(code):
            generic = match.group(1)
            classname = match.group(2)
            line_num = code[:match.start()].count('\n') + 1
            symbols.append(RSymbol(
                name=f"{generic}.{classname}",
                kind='s3_method',
                file_path=file_path,
                line_number=line_num,
            ))

        return symbols

    def _infer_kind(self, name: str) -> str:
        """Infer symbol kind from name."""
        if '.' in name and not name.startswith('.'):
            parts = name.split('.')
            if parts[0] in ['print', 'summary', 'plot', 'predict', 'coef']:
                return 's3_method'
        return 'function'

    def _extract_params(self, params_str: str) -> list[str]:
        """Extract parameter names from function signature."""
        if not params_str.strip():
            return []

        params = []
        for param in params_str.split(','):
            param = param.strip()
            # Handle default values: param = value
            if '=' in param:
                param = param.split('=')[0].strip()
            if param and not param.startswith('...'):
                params.append(param)
            elif param == '...':
                params.append('...')

        return params

    def _extract_roxygen(self, lines: list[str], end_line: int) -> Optional[str]:
        """Extract roxygen2 documentation above a function."""
        doc_lines = []

        for i in range(end_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("#'"):
                doc_lines.insert(0, line[2:].strip())
            elif line.startswith('#'):
                continue  # Regular comment, keep looking
            elif not line:
                continue  # Empty line
            else:
                break  # Hit code

        if doc_lines:
            return '\n'.join(doc_lines)
        return None

    def _create_symbol(self, info: dict, file_path: str) -> RSymbol:
        """Create RSymbol from parsed info."""
        return RSymbol(
            name=info.get('name', 'unknown'),
            kind=info.get('kind', 'function'),
            file_path=file_path,
            line_number=info.get('line', 1),
            parameters=info.get('params', []),
        )


class RMCPServer:
    """FastMCP server for R language support."""

    def __init__(self, name: str = "r-language-server"):
        self.mcp = FastMCP(name)
        self.parser = RCodeParser()
        self.symbols: dict[str, RSymbol] = {}  # name -> symbol
        self.packages: dict[str, RPackageInfo] = {}

        self._setup_tools()
        self._setup_resources()
        self._setup_prompts()

    def _setup_tools(self):
        """Register MCP tools."""

        @self.mcp.tool()
        async def parse_r_code(code: str, file_path: str = "script.R") -> list[dict]:
            """Parse R code and extract symbols.

            Args:
                code: R source code to parse
                file_path: Path for citation generation

            Returns:
                List of extracted symbols with citations
            """
            symbols = self.parser.parse(code, file_path)

            # Cache symbols
            for sym in symbols:
                self.symbols[sym.name] = sym

            return [s.to_dict() for s in symbols]

        @self.mcp.tool()
        async def search_r_symbol(name: str, exact: bool = False) -> list[dict]:
            """Search for R symbols by name.

            Args:
                name: Symbol name to search
                exact: If True, exact match only

            Returns:
                Matching symbols
            """
            results = []
            name_lower = name.lower()

            for sym_name, sym in self.symbols.items():
                if exact:
                    if sym_name == name:
                        results.append(sym.to_dict())
                else:
                    if name_lower in sym_name.lower():
                        results.append(sym.to_dict())

            return results

        @self.mcp.tool()
        async def verify_r_symbol(symbol_name: str) -> dict:
            """Verify an R symbol exists in parsed code.

            Args:
                symbol_name: Name of symbol to verify

            Returns:
                Verification result with citation if found
            """
            if symbol_name in self.symbols:
                sym = self.symbols[symbol_name]
                return {
                    'exists': True,
                    'symbol': sym.to_dict(),
                    'citation': sym.to_citation(),
                }

            # Try fuzzy match
            for name, sym in self.symbols.items():
                if symbol_name.lower() == name.lower():
                    return {
                        'exists': True,
                        'symbol': sym.to_dict(),
                        'citation': sym.to_citation(),
                        'fuzzy_match': True,
                    }

            return {
                'exists': False,
                'symbol': None,
                'citation': None,
            }

        @self.mcp.tool()
        async def get_r_function_signature(name: str) -> Optional[dict]:
            """Get function signature for an R function.

            Args:
                name: Function name

            Returns:
                Function signature info or None
            """
            if name in self.symbols:
                sym = self.symbols[name]
                if sym.kind in ['function', 's3_method']:
                    return {
                        'name': sym.name,
                        'parameters': sym.parameters,
                        'documentation': sym.documentation,
                        'citation': sym.to_citation(),
                    }
            return None

        @self.mcp.tool()
        async def index_r_directory(path: str) -> dict:
            """Index all R files in a directory.

            Args:
                path: Directory path to index

            Returns:
                Indexing statistics
            """
            dir_path = Path(path)
            if not dir_path.exists():
                return {'error': f'Directory not found: {path}'}

            r_files = list(dir_path.rglob("*.R")) + list(dir_path.rglob("*.r"))

            total_symbols = 0
            indexed_files = 0

            for r_file in r_files:
                try:
                    code = r_file.read_text(encoding='utf-8', errors='ignore')
                    rel_path = str(r_file.relative_to(dir_path))
                    symbols = self.parser.parse(code, rel_path)

                    for sym in symbols:
                        self.symbols[sym.name] = sym
                        total_symbols += 1

                    indexed_files += 1
                except Exception:
                    continue

            return {
                'indexed_files': indexed_files,
                'total_files': len(r_files),
                'total_symbols': total_symbols,
                'symbol_kinds': self._count_by_kind(),
            }

    def _setup_resources(self):
        """Register MCP resources."""

        @self.mcp.resource("r://symbols")
        async def list_symbols() -> str:
            """List all indexed R symbols."""
            return json.dumps([s.to_dict() for s in self.symbols.values()], indent=2)

        @self.mcp.resource("r://symbol/{name}")
        async def get_symbol(name: str) -> str:
            """Get a specific R symbol."""
            if name in self.symbols:
                return json.dumps(self.symbols[name].to_dict(), indent=2)
            return json.dumps({'error': 'Symbol not found'})

    def _setup_prompts(self):
        """Register MCP prompts."""

        @self.mcp.prompt()
        async def r_function_doc() -> str:
            """Generate documentation for an R function."""
            return """Generate roxygen2 documentation for the following R function.
Include @param for each parameter, @return, @export, and @examples.
Follow tidyverse documentation style."""

    def _count_by_kind(self) -> dict[str, int]:
        """Count symbols by kind."""
        counts = {}
        for sym in self.symbols.values():
            counts[sym.kind] = counts.get(sym.kind, 0) + 1
        return counts

    def run(self):
        """Run the MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP SDK not available")
        self.mcp.run()


# Standalone usage for testing
def parse_r_file(file_path: str) -> list[dict]:
    """Parse an R file and return symbols."""
    parser = RCodeParser()
    code = Path(file_path).read_text()
    symbols = parser.parse(code, file_path)
    return [s.to_dict() for s in symbols]


def index_r_package(package_path: str) -> dict:
    """Index an R package directory."""
    parser = RCodeParser()
    pkg_path = Path(package_path)

    r_dir = pkg_path / "R"
    if not r_dir.exists():
        return {'error': 'No R/ directory found'}

    symbols = []
    for r_file in r_dir.glob("*.R"):
        code = r_file.read_text(encoding='utf-8', errors='ignore')
        rel_path = str(r_file.relative_to(pkg_path))
        symbols.extend(parser.parse(code, rel_path))

    return {
        'package': pkg_path.name,
        'symbols': [s.to_dict() for s in symbols],
        'total': len(symbols),
    }


if __name__ == "__main__":
    import asyncio

    # Demo usage
    sample_r = '''
#' Calculate the mean of a vector
#'
#' @param x A numeric vector
#' @param na.rm Remove NA values
#' @return The arithmetic mean
#' @export
#' @examples
#' my_mean(c(1, 2, 3))
my_mean <- function(x, na.rm = FALSE) {
  sum(x, na.rm = na.rm) / length(x)
}

# S3 method for print
print.myclass <- function(x, ...) {
  cat("MyClass object\\n")
  invisible(x)
}

# S4 class definition
setClass("Person",
  slots = c(
    name = "character",
    age = "numeric"
  )
)

# R6 class definition
Animal <- R6Class("Animal",
  public = list(
    name = NULL,
    initialize = function(name) {
      self$name <- name
    }
  )
)
'''

    parser = RCodeParser()
    symbols = parser.parse(sample_r, "example.R")

    print("R Code Parser Demo")
    print("=" * 50)
    print(f"Parsed {len(symbols)} symbols:\n")

    for sym in symbols:
        print(f"  {sym.kind}: {sym.name}")
        print(f"    Citation: {sym.to_citation()}")
        if sym.parameters:
            print(f"    Params: {', '.join(sym.parameters)}")
        if sym.documentation:
            doc_preview = sym.documentation[:60].replace('\n', ' ')
            print(f"    Doc: {doc_preview}...")
        print()
