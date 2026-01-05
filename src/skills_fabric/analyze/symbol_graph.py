"""Project-wide Symbol Graph.

Builds a complete cross-reference graph of all symbols
in a project for navigation and dependency analysis.
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import ast


@dataclass
class SymbolNode:
    """A node in the symbol graph."""
    name: str
    full_name: str  # e.g., "module.Class.method"
    kind: str  # "class", "function", "method", "variable"
    file_path: str
    line: int
    docstring: Optional[str] = None
    type_hint: Optional[str] = None


@dataclass
class SymbolEdge:
    """An edge between symbols (calls/uses)."""
    source: str  # full_name of caller
    target: str  # full_name of callee
    edge_type: str  # "calls", "imports", "inherits", "uses"
    line: int  # where the reference occurs


@dataclass
class SymbolGraph:
    """Complete symbol graph for a project."""
    nodes: dict[str, SymbolNode] = field(default_factory=dict)
    edges: list[SymbolEdge] = field(default_factory=list)
    
    def add_node(self, node: SymbolNode):
        """Add a symbol node."""
        self.nodes[node.full_name] = node
    
    def add_edge(self, edge: SymbolEdge):
        """Add a relationship edge."""
        self.edges.append(edge)
    
    def get_callers(self, full_name: str) -> list[str]:
        """Get all symbols that call this symbol."""
        return [e.source for e in self.edges 
                if e.target == full_name and e.edge_type == "calls"]
    
    def get_callees(self, full_name: str) -> list[str]:
        """Get all symbols this symbol calls."""
        return [e.target for e in self.edges 
                if e.source == full_name and e.edge_type == "calls"]
    
    def get_dependencies(self, full_name: str) -> list[str]:
        """Get all dependencies (imports, inherits, uses)."""
        return [e.target for e in self.edges 
                if e.source == full_name and e.edge_type in ("imports", "inherits", "uses")]


class SymbolGraphBuilder:
    """Build a SymbolGraph from a project directory.
    
    Usage:
        builder = SymbolGraphBuilder()
        graph = builder.build(Path("/path/to/project"))
        
        # Find who calls a function
        callers = graph.get_callers("module.Class.method")
        
        # Find what a function calls
        callees = graph.get_callees("module.function")
    """
    
    def __init__(self):
        self.graph = SymbolGraph()
        self._current_file = ""
        self._current_scope = []
    
    def build(self, project_path: Path, extensions: list[str] = None) -> SymbolGraph:
        """Build symbol graph for entire project.
        
        Args:
            project_path: Root of the project
            extensions: File extensions to analyze (default: [".py"])
        
        Returns:
            Complete SymbolGraph
        """
        if extensions is None:
            extensions = [".py"]
        
        self.graph = SymbolGraph()
        
        for ext in extensions:
            for file_path in project_path.rglob(f"*{ext}"):
                # Skip non-source dirs
                if any(d in str(file_path) for d in [".git", "__pycache__", "node_modules", ".venv"]):
                    continue
                
                try:
                    self._analyze_file(file_path, project_path)
                except Exception as e:
                    print(f"[SymbolGraph] Error analyzing {file_path}: {e}")
        
        print(f"[SymbolGraph] Built graph: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
        return self.graph
    
    def _analyze_file(self, file_path: Path, project_root: Path):
        """Analyze a single Python file."""
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return
        
        # Calculate module name from path
        rel_path = file_path.relative_to(project_root)
        module_name = str(rel_path.with_suffix("")).replace("/", ".")
        
        self._current_file = str(file_path)
        self._current_scope = [module_name]
        
        self._visit(tree)
    
    def _visit(self, node):
        """Visit AST node and children."""
        # Handle different node types
        if isinstance(node, ast.ClassDef):
            self._handle_class(node)
        elif isinstance(node, ast.FunctionDef):
            self._handle_function(node)
        elif isinstance(node, ast.Import):
            self._handle_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._handle_import_from(node)
        elif isinstance(node, ast.Call):
            self._handle_call(node)
        
        # Visit children
        for child in ast.iter_child_nodes(node):
            self._visit(child)
    
    def _handle_class(self, node: ast.ClassDef):
        """Handle class definition."""
        full_name = ".".join(self._current_scope + [node.name])
        
        docstring = ast.get_docstring(node)
        
        self.graph.add_node(SymbolNode(
            name=node.name,
            full_name=full_name,
            kind="class",
            file_path=self._current_file,
            line=node.lineno,
            docstring=docstring
        ))
        
        # Handle inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.graph.add_edge(SymbolEdge(
                    source=full_name,
                    target=base.id,
                    edge_type="inherits",
                    line=node.lineno
                ))
        
        # Visit class body with updated scope
        old_scope = self._current_scope
        self._current_scope = self._current_scope + [node.name]
        for child in node.body:
            self._visit(child)
        self._current_scope = old_scope
    
    def _handle_function(self, node: ast.FunctionDef):
        """Handle function/method definition."""
        full_name = ".".join(self._current_scope + [node.name])
        
        kind = "method" if len(self._current_scope) > 1 else "function"
        docstring = ast.get_docstring(node)
        
        # Extract return type hint
        type_hint = None
        if node.returns:
            type_hint = ast.unparse(node.returns) if hasattr(ast, "unparse") else None
        
        self.graph.add_node(SymbolNode(
            name=node.name,
            full_name=full_name,
            kind=kind,
            file_path=self._current_file,
            line=node.lineno,
            docstring=docstring,
            type_hint=type_hint
        ))
        
        # Visit function body with updated scope
        old_scope = self._current_scope
        self._current_scope = self._current_scope + [node.name]
        for child in node.body:
            self._visit(child)
        self._current_scope = old_scope
    
    def _handle_import(self, node: ast.Import):
        """Handle import statement."""
        current = ".".join(self._current_scope)
        for alias in node.names:
            self.graph.add_edge(SymbolEdge(
                source=current,
                target=alias.name,
                edge_type="imports",
                line=node.lineno
            ))
    
    def _handle_import_from(self, node: ast.ImportFrom):
        """Handle from ... import statement."""
        current = ".".join(self._current_scope)
        module = node.module or ""
        
        for alias in node.names:
            target = f"{module}.{alias.name}" if module else alias.name
            self.graph.add_edge(SymbolEdge(
                source=current,
                target=target,
                edge_type="imports",
                line=node.lineno
            ))
    
    def _handle_call(self, node: ast.Call):
        """Handle function call."""
        current = ".".join(self._current_scope)
        
        # Extract callee name
        callee = None
        if isinstance(node.func, ast.Name):
            callee = node.func.id
        elif isinstance(node.func, ast.Attribute):
            callee = node.func.attr
        
        if callee:
            self.graph.add_edge(SymbolEdge(
                source=current,
                target=callee,
                edge_type="calls",
                line=node.lineno
            ))
