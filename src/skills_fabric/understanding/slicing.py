"""Program Slicing for Focused Understanding.

Based on research:
- "Programmers mentally form program slices when they debug"
- "Slicing helps focus on relevant parts of large programs"

Key concepts:
- Backward slice: What statements affect variable X at line Y?
- Forward slice: What statements are affected by variable X?
- Data dependence: Statement B depends on A if A writes a variable B reads
- Control dependence: Statement B depends on A if A controls whether B executes

For code understanding:
- To understand what a function returns → backward slice from return
- To understand impact of a parameter → forward slice from parameter
- To understand a bug → backward slice from the error point
"""
import ast
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional, Tuple
from pathlib import Path


@dataclass
class SlicingCriterion:
    """The point of interest for slicing.

    A slice is computed with respect to:
    - A program point (line number)
    - A variable of interest
    """
    line: int
    variable: str
    file_path: str = ""


@dataclass
class DependencyEdge:
    """An edge in the program dependence graph."""
    from_line: int
    to_line: int
    dependency_type: str  # "data" or "control"
    variable: str = ""    # For data dependencies


@dataclass
class ProgramSlice:
    """A slice of the program relevant to the criterion."""
    criterion: SlicingCriterion
    direction: str  # "backward" or "forward"
    lines: Set[int]  # Line numbers in the slice
    statements: List[str]  # The actual code
    dependencies: List[DependencyEdge]  # Why each line is included

    def summary(self) -> str:
        lines = [
            f"{self.direction.title()} Slice for '{self.criterion.variable}' at line {self.criterion.line}",
            f"Slice size: {len(self.lines)} lines",
            "",
            "Included lines:"
        ]
        for stmt in self.statements[:10]:
            lines.append(f"  {stmt}")
        if len(self.statements) > 10:
            lines.append(f"  ... and {len(self.statements) - 10} more")
        return "\n".join(lines)


class VariableTracker(ast.NodeVisitor):
    """Track variable definitions and uses in AST."""

    def __init__(self):
        # Maps line → variables defined on that line
        self.definitions: Dict[int, Set[str]] = {}
        # Maps line → variables used on that line
        self.uses: Dict[int, Set[str]] = {}
        # Current function scope
        self.current_scope: str = ""

    def visit_Assign(self, node: ast.Assign):
        line = node.lineno
        if line not in self.definitions:
            self.definitions[line] = set()
        if line not in self.uses:
            self.uses[line] = set()

        # Track definitions
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.definitions[line].add(target.id)
            elif isinstance(target, ast.Tuple):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.definitions[line].add(elt.id)

        # Track uses in the value
        for name in self._extract_names(node.value):
            self.uses[line].add(name)

        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        line = node.lineno
        if line not in self.definitions:
            self.definitions[line] = set()
        if line not in self.uses:
            self.uses[line] = set()

        if isinstance(node.target, ast.Name):
            self.definitions[line].add(node.target.id)
            self.uses[line].add(node.target.id)  # Also a use (x += y uses x)

        for name in self._extract_names(node.value):
            self.uses[line].add(name)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        line = node.lineno
        if line not in self.definitions:
            self.definitions[line] = set()
        self.definitions[line].add(node.name)

        # Parameters are definitions on the same line
        for arg in node.args.args:
            self.definitions[line].add(arg.arg)

        old_scope = self.current_scope
        self.current_scope = node.name
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        # Same as FunctionDef
        line = node.lineno
        if line not in self.definitions:
            self.definitions[line] = set()
        self.definitions[line].add(node.name)

        for arg in node.args.args:
            self.definitions[line].add(arg.arg)

        old_scope = self.current_scope
        self.current_scope = node.name
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_Name(self, node: ast.Name):
        line = node.lineno
        if line not in self.uses:
            self.uses[line] = set()

        if isinstance(node.ctx, ast.Load):
            self.uses[line].add(node.id)
        elif isinstance(node.ctx, ast.Store):
            if line not in self.definitions:
                self.definitions[line] = set()
            self.definitions[line].add(node.id)

        self.generic_visit(node)

    def visit_Return(self, node: ast.Return):
        line = node.lineno
        if line not in self.uses:
            self.uses[line] = set()

        if node.value:
            for name in self._extract_names(node.value):
                self.uses[line].add(name)

        self.generic_visit(node)

    def _extract_names(self, node: ast.AST) -> Set[str]:
        """Extract all Name nodes from an expression."""
        names = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                names.add(child.id)
        return names


class ControlFlowAnalyzer(ast.NodeVisitor):
    """Analyze control flow for control dependencies."""

    def __init__(self):
        # Maps line → lines it controls
        self.control_deps: Dict[int, Set[int]] = {}
        # Stack of control statements
        self.control_stack: List[int] = []

    def visit_If(self, node: ast.If):
        line = node.lineno
        if line not in self.control_deps:
            self.control_deps[line] = set()

        self.control_stack.append(line)

        # Body lines are controlled by this if
        for stmt in node.body:
            self._add_controlled(line, stmt)
        for stmt in node.orelse:
            self._add_controlled(line, stmt)

        self.generic_visit(node)
        self.control_stack.pop()

    def visit_For(self, node: ast.For):
        line = node.lineno
        if line not in self.control_deps:
            self.control_deps[line] = set()

        self.control_stack.append(line)

        for stmt in node.body:
            self._add_controlled(line, stmt)

        self.generic_visit(node)
        self.control_stack.pop()

    def visit_While(self, node: ast.While):
        line = node.lineno
        if line not in self.control_deps:
            self.control_deps[line] = set()

        self.control_stack.append(line)

        for stmt in node.body:
            self._add_controlled(line, stmt)

        self.generic_visit(node)
        self.control_stack.pop()

    def _add_controlled(self, controller: int, node: ast.AST):
        """Add all lines in node as controlled by controller."""
        for child in ast.walk(node):
            if hasattr(child, 'lineno'):
                self.control_deps[controller].add(child.lineno)


class ProgramSlicer:
    """Compute program slices for focused understanding."""

    def __init__(self, source_code: str, file_path: str = ""):
        self.source = source_code
        self.file_path = file_path
        self.lines = source_code.split('\n')

        try:
            self.tree = ast.parse(source_code)
        except SyntaxError:
            self.tree = None

        self.var_tracker = None
        self.control_analyzer = None

        if self.tree:
            self._analyze()

    def _analyze(self):
        """Run static analysis on the code."""
        self.var_tracker = VariableTracker()
        self.var_tracker.visit(self.tree)

        self.control_analyzer = ControlFlowAnalyzer()
        self.control_analyzer.visit(self.tree)

    def backward_slice(self, criterion: SlicingCriterion) -> ProgramSlice:
        """Compute backward slice: what affects the variable at this point?

        A backward slice includes all statements that may affect the value
        of the specified variable at the specified line.
        """
        if not self.tree or not self.var_tracker:
            return ProgramSlice(
                criterion=criterion,
                direction="backward",
                lines=set(),
                statements=[],
                dependencies=[]
            )

        slice_lines: Set[int] = set()
        dependencies: List[DependencyEdge] = []
        worklist: List[Tuple[int, str]] = [(criterion.line, criterion.variable)]
        visited: Set[Tuple[int, str]] = set()

        while worklist:
            current_line, current_var = worklist.pop()

            if (current_line, current_var) in visited:
                continue
            visited.add((current_line, current_var))

            slice_lines.add(current_line)

            # Find data dependencies: where was current_var defined?
            for line in range(current_line - 1, 0, -1):
                defs = self.var_tracker.definitions.get(line, set())
                if current_var in defs:
                    # This line defines the variable we're looking for
                    slice_lines.add(line)
                    dependencies.append(DependencyEdge(
                        from_line=line,
                        to_line=current_line,
                        dependency_type="data",
                        variable=current_var
                    ))

                    # Now add the variables used on that line to the worklist
                    uses = self.var_tracker.uses.get(line, set())
                    for use_var in uses:
                        if (line, use_var) not in visited:
                            worklist.append((line, use_var))

                    break  # Found the most recent definition

            # Find control dependencies
            for controller, controlled in self.control_analyzer.control_deps.items():
                if current_line in controlled:
                    slice_lines.add(controller)
                    dependencies.append(DependencyEdge(
                        from_line=controller,
                        to_line=current_line,
                        dependency_type="control"
                    ))

                    # Add variables used in control condition to worklist
                    uses = self.var_tracker.uses.get(controller, set())
                    for use_var in uses:
                        if (controller, use_var) not in visited:
                            worklist.append((controller, use_var))

        # Extract statements
        statements = []
        for line_no in sorted(slice_lines):
            if 0 < line_no <= len(self.lines):
                statements.append(f"{line_no}: {self.lines[line_no - 1]}")

        return ProgramSlice(
            criterion=criterion,
            direction="backward",
            lines=slice_lines,
            statements=statements,
            dependencies=dependencies
        )

    def forward_slice(self, criterion: SlicingCriterion) -> ProgramSlice:
        """Compute forward slice: what is affected by this variable?

        A forward slice includes all statements that may be affected by
        the value of the specified variable at the specified line.
        """
        if not self.tree or not self.var_tracker:
            return ProgramSlice(
                criterion=criterion,
                direction="forward",
                lines=set(),
                statements=[],
                dependencies=[]
            )

        slice_lines: Set[int] = set()
        dependencies: List[DependencyEdge] = []
        worklist: List[Tuple[int, str]] = [(criterion.line, criterion.variable)]
        visited: Set[Tuple[int, str]] = set()

        while worklist:
            current_line, current_var = worklist.pop()

            if (current_line, current_var) in visited:
                continue
            visited.add((current_line, current_var))

            slice_lines.add(current_line)

            # Find data dependencies: where is current_var used?
            for line in range(current_line + 1, len(self.lines) + 1):
                uses = self.var_tracker.uses.get(line, set())
                if current_var in uses:
                    # This line uses the variable
                    slice_lines.add(line)
                    dependencies.append(DependencyEdge(
                        from_line=current_line,
                        to_line=line,
                        dependency_type="data",
                        variable=current_var
                    ))

                    # Add variables defined on that line to worklist
                    defs = self.var_tracker.definitions.get(line, set())
                    for def_var in defs:
                        if (line, def_var) not in visited:
                            worklist.append((line, def_var))

            # Find control dependencies (where this line controls others)
            controlled = self.control_analyzer.control_deps.get(current_line, set())
            for controlled_line in controlled:
                slice_lines.add(controlled_line)
                dependencies.append(DependencyEdge(
                    from_line=current_line,
                    to_line=controlled_line,
                    dependency_type="control"
                ))

        # Extract statements
        statements = []
        for line_no in sorted(slice_lines):
            if 0 < line_no <= len(self.lines):
                statements.append(f"{line_no}: {self.lines[line_no - 1]}")

        return ProgramSlice(
            criterion=criterion,
            direction="forward",
            lines=slice_lines,
            statements=statements,
            dependencies=dependencies
        )

    def focus_on_method(self, method_name: str) -> ProgramSlice:
        """Create a slice focused on understanding a specific method.

        Combines backward slice from return with forward slice from parameters.
        """
        if not self.tree:
            return ProgramSlice(
                criterion=SlicingCriterion(0, method_name),
                direction="focused",
                lines=set(),
                statements=[],
                dependencies=[]
            )

        # Find the method
        method_lines = set()
        return_line = None
        param_lines = []

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == method_name:
                    # Get all lines in the method
                    method_lines.add(node.lineno)

                    # Find return statements
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return):
                            return_line = child.lineno
                        if hasattr(child, 'lineno'):
                            method_lines.add(child.lineno)

                    # Parameters are at the function definition line
                    for arg in node.args.args:
                        param_lines.append((node.lineno, arg.arg))

                    break

        # Extract statements
        statements = []
        for line_no in sorted(method_lines):
            if 0 < line_no <= len(self.lines):
                statements.append(f"{line_no}: {self.lines[line_no - 1]}")

        return ProgramSlice(
            criterion=SlicingCriterion(0, method_name),
            direction="focused",
            lines=method_lines,
            statements=statements,
            dependencies=[]
        )


def slice_for_understanding(
    source_code: str,
    criterion: SlicingCriterion,
    direction: str = "backward"
) -> ProgramSlice:
    """Convenience function to compute a slice.

    Args:
        source_code: The source code to analyze
        criterion: What to slice with respect to
        direction: "backward" or "forward"

    Returns:
        ProgramSlice with relevant lines
    """
    slicer = ProgramSlicer(source_code)

    if direction == "backward":
        return slicer.backward_slice(criterion)
    elif direction == "forward":
        return slicer.forward_slice(criterion)
    else:
        raise ValueError(f"Unknown direction: {direction}")
