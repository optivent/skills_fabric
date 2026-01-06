"""CodeWiki-First Proof-Based Understanding.

The CORRECT order of operations:
1. Start from CodeWiki (pre-verified documentation with GitHub links)
2. Extract all links (concept → file:line:commit)
3. Validate each link against git clone
4. AST parse at verified locations
5. LSP expand dependencies
6. Execute for behavioral verification

Key insight: CodeWiki links are PRE-VERIFIED connections.
We don't search for code - we FOLLOW verified links.
"""
import re
import ast
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from enum import IntEnum


class DepthLevel(IntEnum):
    """Progressive depth levels for understanding."""
    VALIDATE = 0      # Just check link exists
    PARSE_SYMBOL = 1  # Extract symbol structure
    DEPENDENCIES = 2  # Immediate deps
    CALL_GRAPH = 3    # One-level call expansion
    FULL_GRAPH = 4    # Recursive expansion
    EXEC_TRACE = 5    # Runtime execution


@dataclass
class CodeWikiRef:
    """A reference extracted from CodeWiki.

    These are PRE-VERIFIED connections from documentation to source.
    """
    concept: str        # The concept name (e.g., "logger", "Handler")
    repo: str           # Repository (e.g., "delgan/loguru")
    file_path: str      # File path within repo
    line: int           # Line number (0 if not specified)
    commit: str         # Commit hash
    context: str = ""   # Surrounding text from CodeWiki

    def github_url(self) -> str:
        base = f"https://github.com/{self.repo}/blob/{self.commit}/{self.file_path}"
        if self.line > 0:
            return f"{base}#L{self.line}"
        return base


@dataclass
class ValidationResult:
    """Result of validating a CodeWiki reference."""
    ref: CodeWikiRef
    valid: bool
    actual_content: str = ""
    error: str = ""


@dataclass
class SymbolStructure:
    """Extracted structure of a symbol."""
    name: str
    kind: str  # "class", "function", "variable"
    line: int
    methods: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    docstring: str = ""
    bases: List[str] = field(default_factory=list)


@dataclass
class ProvenUnderstanding:
    """Understanding proven through CodeWiki → Code verification."""
    ref: CodeWikiRef
    depth: DepthLevel
    validation: ValidationResult
    symbol: Optional[SymbolStructure] = None
    dependencies: List[str] = field(default_factory=list)
    call_graph: Dict[str, List[str]] = field(default_factory=dict)
    execution_result: Optional[str] = None


def extract_codewiki_refs(markdown: str) -> List[CodeWikiRef]:
    """Extract GitHub links from CodeWiki markdown.

    Pattern matches:
    [`concept`](https://github.com/owner/repo/blob/commit/path#L123)
    [concept](https://github.com/owner/repo/blob/commit/path)
    """
    # Pattern for GitHub links with optional line number
    pattern = r"\[`?([^`\]]+)`?\]\(https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#\)]+)(?:#L(\d+))?\)"

    refs = []
    for match in re.finditer(pattern, markdown):
        refs.append(CodeWikiRef(
            concept=match.group(1),
            repo=match.group(2),
            file_path=match.group(4),
            line=int(match.group(5)) if match.group(5) else 0,
            commit=match.group(3)
        ))

    return refs


def deduplicate_refs(refs: List[CodeWikiRef]) -> List[CodeWikiRef]:
    """Remove duplicate references, keeping first occurrence."""
    seen = set()
    unique = []
    for ref in refs:
        key = (ref.concept, ref.file_path, ref.line)
        if key not in seen:
            seen.add(key)
            unique.append(ref)
    return unique


class CodeWikiVerifier:
    """Verify CodeWiki references against actual code."""

    def __init__(self, repo_path: str):
        """Initialize with path to cloned repository."""
        self.repo_path = Path(repo_path)

    def validate_ref(self, ref: CodeWikiRef) -> ValidationResult:
        """Validate that a CodeWiki reference exists in code.

        This is STEP 3: Check that the link actually points to what it claims.
        """
        file_path = self.repo_path / ref.file_path

        if not file_path.exists():
            return ValidationResult(
                ref=ref,
                valid=False,
                error=f"File not found: {ref.file_path}"
            )

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            if ref.line > 0:
                if ref.line > len(lines):
                    return ValidationResult(
                        ref=ref,
                        valid=False,
                        error=f"Line {ref.line} out of range (file has {len(lines)} lines)"
                    )

                # Get context around the line
                start = max(0, ref.line - 3)
                end = min(len(lines), ref.line + 3)
                context = '\n'.join(lines[start:end])

                # Check if concept appears near the line
                concept_found = ref.concept.lower() in lines[ref.line - 1].lower()

                return ValidationResult(
                    ref=ref,
                    valid=concept_found,
                    actual_content=context,
                    error="" if concept_found else f"'{ref.concept}' not found at line {ref.line}"
                )
            else:
                # No line number - check if file contains concept
                concept_found = ref.concept.lower() in content.lower()
                return ValidationResult(
                    ref=ref,
                    valid=concept_found,
                    actual_content=content[:500] if concept_found else "",
                    error="" if concept_found else f"'{ref.concept}' not found in file"
                )

        except Exception as e:
            return ValidationResult(
                ref=ref,
                valid=False,
                error=str(e)
            )

    def parse_symbol_at_line(self, ref: CodeWikiRef) -> Optional[SymbolStructure]:
        """Parse the symbol at a verified location.

        This is STEP 4: Extract structure from validated code.
        """
        file_path = self.repo_path / ref.file_path

        if not file_path.exists():
            return None

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            # Find the node at or near the specified line
            for node in ast.walk(tree):
                if hasattr(node, 'lineno'):
                    # Check if this node is at/near our target line
                    if abs(node.lineno - ref.line) <= 2:
                        if isinstance(node, ast.ClassDef):
                            methods = []
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    methods.append(item.name)

                            bases = []
                            for base in node.bases:
                                if isinstance(base, ast.Name):
                                    bases.append(base.id)
                                elif isinstance(base, ast.Attribute):
                                    bases.append(f"{ast.unparse(base)}")

                            return SymbolStructure(
                                name=node.name,
                                kind="class",
                                line=node.lineno,
                                methods=methods,
                                docstring=ast.get_docstring(node) or "",
                                bases=bases
                            )

                        elif isinstance(node, ast.FunctionDef):
                            params = []
                            for arg in node.args.args:
                                param_str = arg.arg
                                if arg.annotation:
                                    param_str += f": {ast.unparse(arg.annotation)}"
                                params.append(param_str)

                            return_type = ""
                            if node.returns:
                                return_type = ast.unparse(node.returns)

                            return SymbolStructure(
                                name=node.name,
                                kind="function",
                                line=node.lineno,
                                parameters=params,
                                return_type=return_type,
                                docstring=ast.get_docstring(node) or ""
                            )

            return None

        except Exception:
            return None

    def find_dependencies(self, ref: CodeWikiRef) -> List[str]:
        """Find immediate dependencies of a symbol.

        This is STEP 5: What does this symbol use?
        """
        file_path = self.repo_path / ref.file_path

        if not file_path.exists():
            return []

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            dependencies = set()

            # Find imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        dependencies.add(f"{module}.{alias.name}")

            # Find class bases and used names
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            dependencies.add(base.id)
                        elif isinstance(base, ast.Attribute):
                            dependencies.add(ast.unparse(base))

            return sorted(dependencies)

        except Exception:
            return []


def process_codewiki(markdown: str, repo_path: str, depth: DepthLevel = DepthLevel.PARSE_SYMBOL) -> List[ProvenUnderstanding]:
    """Process CodeWiki markdown and prove understanding.

    This is the MAIN ENTRY POINT for the correct order of operations.
    """
    # STEP 1 & 2: Extract references from CodeWiki
    refs = extract_codewiki_refs(markdown)
    refs = deduplicate_refs(refs)

    print(f"Extracted {len(refs)} unique references from CodeWiki")

    verifier = CodeWikiVerifier(repo_path)
    results = []

    for ref in refs:
        # STEP 3: Validate against git clone
        validation = verifier.validate_ref(ref)

        understanding = ProvenUnderstanding(
            ref=ref,
            depth=depth,
            validation=validation
        )

        if validation.valid and depth >= DepthLevel.PARSE_SYMBOL:
            # STEP 4: Parse symbol structure
            understanding.symbol = verifier.parse_symbol_at_line(ref)

        if validation.valid and depth >= DepthLevel.DEPENDENCIES:
            # STEP 5: Find dependencies
            understanding.dependencies = verifier.find_dependencies(ref)

        results.append(understanding)

    return results


def summarize_understanding(results: List[ProvenUnderstanding]) -> str:
    """Generate summary of proven understanding."""
    lines = [
        "=" * 70,
        "  CODEWIKI-VERIFIED UNDERSTANDING",
        "=" * 70,
        "",
        f"Total references: {len(results)}",
        f"Validated: {sum(1 for r in results if r.validation.valid)}",
        f"Invalid: {sum(1 for r in results if not r.validation.valid)}",
        "",
        "VALIDATED CONCEPTS:",
        ""
    ]

    for r in results:
        if r.validation.valid:
            status = "✓"
            lines.append(f"  {status} {r.ref.concept}")
            lines.append(f"      File: {r.ref.file_path}:{r.ref.line}")
            if r.symbol:
                lines.append(f"      Kind: {r.symbol.kind}")
                if r.symbol.methods:
                    lines.append(f"      Methods: {len(r.symbol.methods)}")
                if r.symbol.bases:
                    lines.append(f"      Bases: {', '.join(r.symbol.bases)}")
            lines.append("")

    invalid = [r for r in results if not r.validation.valid]
    if invalid:
        lines.append("INVALID REFERENCES:")
        lines.append("")
        for r in invalid:
            lines.append(f"  ✗ {r.ref.concept}")
            lines.append(f"      File: {r.ref.file_path}:{r.ref.line}")
            lines.append(f"      Error: {r.validation.error}")
            lines.append("")

    lines.append("=" * 70)
    lines.append("THE KEY INSIGHT:")
    lines.append("CodeWiki links are PRE-VERIFIED connections.")
    lines.append("We don't search - we VALIDATE and EXPAND.")
    lines.append("=" * 70)

    return "\n".join(lines)


# Example usage pattern
if __name__ == "__main__":
    # Sample CodeWiki markdown
    sample_codewiki = """
    The [`logger`](https://github.com/delgan/loguru/blob/36da8cca/loguru/_logger.py#L231)
    object is the main interface. The [`Handler`](https://github.com/delgan/loguru/blob/36da8cca/loguru/_handler.py#L31)
    class manages output.
    """

    refs = extract_codewiki_refs(sample_codewiki)
    print(f"Extracted {len(refs)} references")
    for ref in refs:
        print(f"  - {ref.concept} at {ref.file_path}:{ref.line}")
