"""Call Graph - Function call relationship analysis.

Builds and analyzes call graphs from source code:
- Function call relationships
- Dependency ordering
- Dead code detection
- Impact analysis (what's affected by a change)
"""
from dataclasses import dataclass, field
from typing import Optional, Set
from pathlib import Path
import ast


@dataclass
class CallNode:
    """A node in the call graph (function/method)."""
    name: str
    file_path: str
    line: int
    kind: str  # function, method, class
    calls: Set[str] = field(default_factory=set)     # Functions this calls
    called_by: Set[str] = field(default_factory=set)  # Functions that call this

    @property
    def id(self) -> str:
        """Unique identifier for this node."""
        return f"{self.file_path}:{self.name}"


class CallGraphBuilder(ast.NodeVisitor):
    """AST visitor that builds call graph."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.nodes: dict[str, CallNode] = {}
        self.current_function: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit a function definition."""
        self._process_function(node, "function")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit an async function definition."""
        self._process_function(node, "async_function")

    def _process_function(self, node, kind: str):
        """Process a function definition."""
        # Create node
        call_node = CallNode(
            name=node.name,
            file_path=self.file_path,
            line=node.lineno,
            kind=kind
        )
        self.nodes[node.name] = call_node

        # Process body
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Call(self, node: ast.Call):
        """Visit a function call."""
        if self.current_function:
            # Get called function name
            called_name = self._get_call_name(node)
            if called_name:
                # Record call relationship
                if self.current_function in self.nodes:
                    self.nodes[self.current_function].calls.add(called_name)

        self.generic_visit(node)

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract function name from call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None


class CallGraph:
    """Manages call graph for a codebase.

    Usage:
        graph = CallGraph()
        graph.build_from_directory("/path/to/repo")

        # Find what a function calls
        calls = graph.get_calls("process_data")

        # Find what calls a function
        callers = graph.get_callers("helper_function")

        # Find dead code
        dead = graph.find_dead_code(entry_points=["main"])
    """

    def __init__(self):
        self.nodes: dict[str, CallNode] = {}

    def build_from_file(self, file_path: Path) -> int:
        """Build call graph from a single file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)

            builder = CallGraphBuilder(str(file_path))
            builder.visit(tree)

            # Merge nodes
            for name, node in builder.nodes.items():
                self.nodes[node.id] = node

            return len(builder.nodes)
        except Exception:
            return 0

    def build_from_directory(self, directory: Path) -> int:
        """Build call graph from all Python files in directory."""
        directory = Path(directory)
        total = 0

        for py_file in directory.rglob("*.py"):
            skip_dirs = ['node_modules', '.git', '__pycache__', 'venv', '.venv']
            if not any(d in str(py_file) for d in skip_dirs):
                total += self.build_from_file(py_file)

        # Build reverse relationships
        self._build_callers()

        return total

    def _build_callers(self):
        """Build the called_by relationships."""
        for node in self.nodes.values():
            for called_name in node.calls:
                # Find the called node
                for other in self.nodes.values():
                    if other.name == called_name:
                        other.called_by.add(node.id)

    def get_node(self, name: str) -> Optional[CallNode]:
        """Get a node by name (searches all files)."""
        for node in self.nodes.values():
            if node.name == name:
                return node
        return None

    def get_calls(self, function_name: str) -> Set[str]:
        """Get all functions called by the given function."""
        node = self.get_node(function_name)
        return node.calls if node else set()

    def get_callers(self, function_name: str) -> Set[str]:
        """Get all functions that call the given function."""
        node = self.get_node(function_name)
        return node.called_by if node else set()

    def get_transitive_calls(
        self,
        function_name: str,
        max_depth: int = 10
    ) -> Set[str]:
        """Get all functions called directly or indirectly."""
        visited = set()
        to_visit = {function_name}
        depth = 0

        while to_visit and depth < max_depth:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)

            calls = self.get_calls(current)
            to_visit.update(calls - visited)
            depth += 1

        visited.discard(function_name)
        return visited

    def find_dead_code(self, entry_points: list[str]) -> Set[str]:
        """Find functions not reachable from entry points."""
        reachable = set()

        for entry in entry_points:
            reachable.add(entry)
            reachable.update(self.get_transitive_calls(entry))

        all_functions = {node.name for node in self.nodes.values()}
        return all_functions - reachable

    def impact_analysis(self, changed_function: str) -> Set[str]:
        """Find all functions affected by a change.

        Returns functions that directly or indirectly call the changed function.
        """
        affected = set()
        to_check = {changed_function}
        depth = 0

        while to_check and depth < 20:
            current = to_check.pop()
            if current in affected:
                continue
            affected.add(current)

            # Get callers
            node = self.get_node(current)
            if node:
                for caller_id in node.called_by:
                    caller_node = self.nodes.get(caller_id)
                    if caller_node:
                        to_check.add(caller_node.name)

            depth += 1

        affected.discard(changed_function)
        return affected

    def get_summary(self) -> dict:
        """Get summary statistics."""
        total_functions = len(self.nodes)
        total_calls = sum(len(n.calls) for n in self.nodes.values())
        orphans = sum(1 for n in self.nodes.values() if not n.called_by)
        leaves = sum(1 for n in self.nodes.values() if not n.calls)

        return {
            "total_functions": total_functions,
            "total_call_relationships": total_calls,
            "orphan_functions": orphans,  # Not called by anything
            "leaf_functions": leaves,      # Don't call anything
            "avg_calls_per_function": total_calls / total_functions if total_functions else 0
        }

    def to_dot(self) -> str:
        """Export call graph to DOT format for visualization."""
        lines = ["digraph callgraph {", '  rankdir=LR;']

        for node in self.nodes.values():
            # Node
            lines.append(f'  "{node.name}" [label="{node.name}"];')

            # Edges
            for called in node.calls:
                lines.append(f'  "{node.name}" -> "{called}";')

        lines.append("}")
        return "\n".join(lines)
