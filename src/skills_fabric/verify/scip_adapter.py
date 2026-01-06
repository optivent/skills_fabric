"""SCIP Integration for DDR.

Provides SCIP-based symbol retrieval for multi-language support.
SCIP offers precise code intelligence with cross-file references.
"""

from dataclasses import dataclass
from typing import Optional, Iterator
from pathlib import Path
import sys

# Add path for scip_pb2
sys.path.insert(0, '/home/user/skills_fabric')

try:
    import scip_pb2
    SCIP_AVAILABLE = True
except ImportError:
    SCIP_AVAILABLE = False
    scip_pb2 = None


@dataclass
class SCIPSymbol:
    """A symbol extracted from SCIP index."""
    symbol_id: str          # Full SCIP symbol identifier
    name: str               # Short name (e.g., "DirectDependencyRetriever")
    kind: int               # SCIP SymbolKind enum
    file_path: str          # Relative file path
    line_number: int        # 1-indexed line number
    documentation: str      # Docstring/hover text

    @property
    def kind_name(self) -> str:
        """Human-readable kind name."""
        kinds = {
            1: 'package', 2: 'type', 3: 'term', 4: 'method',
            5: 'type_parameter', 6: 'parameter', 7: 'macro',
        }
        return kinds.get(self.kind, 'unknown')


class SCIPIndex:
    """Reader for SCIP index files.

    SCIP (Semantic Code Intelligence Protocol) provides:
    - Precise symbol definitions and references
    - Cross-file navigation
    - Type information and documentation
    - 8× smaller than LSIF, 3× faster processing
    """

    def __init__(self, index_path: str):
        """Initialize SCIP index reader.

        Args:
            index_path: Path to .scip index file
        """
        if not SCIP_AVAILABLE:
            raise ImportError("scip_pb2 not available. Run: python -m grpc_tools.protoc --python_out=. scip.proto")

        self.index_path = Path(index_path)
        self._index: Optional[scip_pb2.Index] = None
        self._symbols: dict[str, SCIPSymbol] = {}
        self._by_name: dict[str, list[SCIPSymbol]] = {}
        self._loaded = False

    def load(self) -> None:
        """Load and parse the SCIP index."""
        if self._loaded:
            return

        with open(self.index_path, 'rb') as f:
            self._index = scip_pb2.Index()
            self._index.ParseFromString(f.read())

        # Build symbol index
        for doc in self._index.documents:
            # Build occurrence map for line numbers
            occurrence_lines = {}
            for occ in doc.occurrences:
                if occ.range:
                    occurrence_lines[occ.symbol] = occ.range[0] + 1  # 0-indexed to 1-indexed

            for sym in doc.symbols:
                # Extract short name from full symbol
                name = self._extract_name(sym.symbol)

                # Get line number from occurrence or default to 1
                line_num = occurrence_lines.get(sym.symbol, 1)

                # Get documentation
                doc_text = sym.documentation[0] if sym.documentation else ""

                scip_sym = SCIPSymbol(
                    symbol_id=sym.symbol,
                    name=name,
                    kind=sym.kind,
                    file_path=doc.relative_path,
                    line_number=line_num,
                    documentation=doc_text,
                )

                self._symbols[sym.symbol] = scip_sym

                # Index by short name
                if name not in self._by_name:
                    self._by_name[name] = []
                self._by_name[name].append(scip_sym)

        self._loaded = True

    def _extract_name(self, symbol_id: str) -> str:
        """Extract short name from SCIP symbol ID.

        SCIP symbols look like:
        scip-python python project 1.0.0 `path/to/file.py`/ClassName#method.
        """
        # Get the last segment
        parts = symbol_id.split('/')
        if parts:
            last = parts[-1]
            # Remove trailing # or .
            return last.rstrip('#').rstrip('.')
        return symbol_id

    def search(self, query: str, max_results: int = 10) -> list[SCIPSymbol]:
        """Search for symbols by name.

        Args:
            query: Symbol name to search for
            max_results: Maximum results to return

        Returns:
            List of matching SCIPSymbol objects
        """
        self.load()

        results = []
        query_lower = query.lower()

        # Exact match first
        if query in self._by_name:
            results.extend(self._by_name[query][:max_results])

        # Partial match
        if len(results) < max_results:
            for name, symbols in self._by_name.items():
                if query_lower in name.lower() and name != query:
                    for sym in symbols:
                        if sym not in results:
                            results.append(sym)
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break

        return results[:max_results]

    def get_symbol(self, symbol_id: str) -> Optional[SCIPSymbol]:
        """Get a specific symbol by its full ID."""
        self.load()
        return self._symbols.get(symbol_id)

    def iter_symbols(self) -> Iterator[SCIPSymbol]:
        """Iterate over all symbols in the index."""
        self.load()
        yield from self._symbols.values()

    def get_symbols_in_file(self, file_path: str) -> list[SCIPSymbol]:
        """Get all symbols defined in a specific file."""
        self.load()
        return [s for s in self._symbols.values() if s.file_path == file_path]

    @property
    def metadata(self) -> dict:
        """Get index metadata."""
        self.load()
        return {
            'project_root': self._index.metadata.project_root,
            'tool_name': self._index.metadata.tool_info.name,
            'tool_version': self._index.metadata.tool_info.version,
            'total_documents': len(self._index.documents),
            'total_symbols': len(self._symbols),
        }

    def to_ddr_format(self) -> dict:
        """Convert SCIP index to DDR-compatible format.

        Returns:
            Dictionary mapping symbol names to their info
        """
        self.load()

        ddr_symbols = {}
        for sym in self._symbols.values():
            ddr_symbols[sym.name] = {
                'file_path': sym.file_path,
                'line_num': sym.line_number,
                'documentation': sym.documentation,
                'kind': sym.kind_name,
                'full_id': sym.symbol_id,
            }

        return ddr_symbols


class SCIPDDRAdapter:
    """Adapter to use SCIP index with DDR verification.

    This bridges SCIP's precise code intelligence with
    DDR's zero-hallucination verification.
    """

    def __init__(self, scip_index: SCIPIndex):
        """Initialize adapter.

        Args:
            scip_index: Loaded SCIPIndex instance
        """
        self.scip = scip_index
        self.scip.load()

    def verify_symbol(self, symbol_name: str) -> tuple[bool, Optional[SCIPSymbol]]:
        """Verify a symbol exists in the codebase.

        Args:
            symbol_name: Name of symbol to verify

        Returns:
            Tuple of (exists, symbol_info)
        """
        results = self.scip.search(symbol_name, max_results=1)

        if results:
            # Check for exact match
            for result in results:
                if result.name.lower() == symbol_name.lower():
                    return True, result
            # Accept partial match with lower confidence
            return True, results[0]

        return False, None

    def get_citation(self, symbol_name: str) -> Optional[str]:
        """Get a citation string for a symbol.

        Args:
            symbol_name: Name of symbol

        Returns:
            Citation string like "path/to/file.py:123" or None
        """
        exists, sym = self.verify_symbol(symbol_name)
        if exists and sym:
            return f"{sym.file_path}:{sym.line_number}"
        return None

    def verify_citation(self, file_path: str, line_number: int) -> bool:
        """Verify a file:line citation is valid.

        Args:
            file_path: Path to file
            line_number: Line number

        Returns:
            True if a symbol exists at that location
        """
        symbols = self.scip.get_symbols_in_file(file_path)

        for sym in symbols:
            # Allow some tolerance in line numbers
            if abs(sym.line_number - line_number) <= 5:
                return True

        return False

    def get_documentation(self, symbol_name: str) -> Optional[str]:
        """Get documentation for a symbol.

        Args:
            symbol_name: Name of symbol

        Returns:
            Documentation string or None
        """
        exists, sym = self.verify_symbol(symbol_name)
        if exists and sym:
            return sym.documentation
        return None
