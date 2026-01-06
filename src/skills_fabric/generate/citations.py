"""Citation System - Add file:line references to generated content.

Every code reference in generated skills must have a verifiable citation.
This module transforms content to include source citations.

Citation Formats:
- Inline: `SymbolName` (file.py:123)
- Markdown: [`SymbolName`](path/to/file.py#L123)
- GitHub: [`SymbolName`](https://github.com/org/repo/blob/main/file.py#L123)

Integration:
- Works with DDR SourceRef objects
- Adds citations after verification
- Supports multiple output formats
"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import re

from ..verify.ddr import SourceRef


@dataclass
class CitationConfig:
    """Configuration for citation formatting."""
    format: str = "markdown"  # "inline", "markdown", "github"
    github_base: Optional[str] = None  # e.g., "https://github.com/org/repo/blob/main"
    include_line_range: bool = False
    max_context_lines: int = 5


@dataclass
class CitationResult:
    """Result from adding citations."""
    original_content: str
    cited_content: str
    citations_added: int
    uncited_symbols: list[str]
    citation_map: dict[str, str]  # symbol -> citation


class CitationSystem:
    """Add source citations to generated content.

    Zero-Hallucination Principle:
    - Every code symbol must have a citation
    - Citations link to actual file:line in source
    - Uncited symbols indicate potential hallucinations
    """

    def __init__(self, config: CitationConfig = None):
        self.config = config or CitationConfig()
        self._refs_by_symbol: dict[str, SourceRef] = {}

    def register_refs(self, refs: list[SourceRef]) -> None:
        """Register source references for citation."""
        for ref in refs:
            # Index by symbol name (case-insensitive)
            key = ref.symbol_name.lower()
            if key not in self._refs_by_symbol:
                self._refs_by_symbol[key] = ref
            # Also index by just the final part (e.g., "StateGraph" from "langgraph.StateGraph")
            parts = ref.symbol_name.split('.')
            if len(parts) > 1:
                self._refs_by_symbol[parts[-1].lower()] = ref

    def add_citations(
        self,
        content: str,
        refs: list[SourceRef] = None
    ) -> CitationResult:
        """Add citations to all code references in content.

        Args:
            content: Generated content with code references
            refs: Source references to use for citations

        Returns:
            CitationResult with cited content
        """
        if refs:
            self.register_refs(refs)

        cited_content = content
        citations_added = 0
        uncited_symbols = []
        citation_map = {}

        # Find all code references: `SymbolName` or `symbol_name`
        pattern = r'`([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)`'
        matches = list(re.finditer(pattern, content))

        # Process in reverse order to preserve positions
        for match in reversed(matches):
            symbol = match.group(1)
            symbol_lower = symbol.lower()

            # Look up source reference
            ref = self._refs_by_symbol.get(symbol_lower)

            if ref:
                citation = self._format_citation(symbol, ref)
                citation_map[symbol] = citation

                # Replace the match with cited version
                start, end = match.span()
                cited_content = cited_content[:start] + citation + cited_content[end:]
                citations_added += 1
            else:
                # Track uncited symbols (potential hallucinations)
                if symbol not in uncited_symbols:
                    uncited_symbols.append(symbol)

        return CitationResult(
            original_content=content,
            cited_content=cited_content,
            citations_added=citations_added,
            uncited_symbols=uncited_symbols,
            citation_map=citation_map,
        )

    def _format_citation(self, symbol: str, ref: SourceRef) -> str:
        """Format a citation based on config."""
        if self.config.format == "inline":
            return f"`{symbol}` ({ref.citation})"

        elif self.config.format == "github" and self.config.github_base:
            url = f"{self.config.github_base}/{ref.file_path}#L{ref.line_number}"
            if self.config.include_line_range and ref.end_line:
                url += f"-L{ref.end_line}"
            return f"[`{symbol}`]({url})"

        else:  # markdown (default)
            return f"[`{symbol}`]({ref.file_path}#L{ref.line_number})"

    def validate_all_cited(self, result: CitationResult) -> bool:
        """Check if all symbols have citations (zero-hallucination)."""
        return len(result.uncited_symbols) == 0

    def get_uncited_report(self, result: CitationResult) -> str:
        """Generate report of uncited symbols."""
        if not result.uncited_symbols:
            return "All symbols have citations."

        lines = [
            "Uncited Symbols (Potential Hallucinations):",
            "=" * 40,
        ]
        for symbol in result.uncited_symbols:
            lines.append(f"  - `{symbol}`: No source reference found")

        lines.append("")
        lines.append(f"Total: {len(result.uncited_symbols)} uncited symbols")
        lines.append("Action: Verify these symbols exist in source code")

        return '\n'.join(lines)


def add_citations(
    content: str,
    refs: list[SourceRef],
    github_base: Optional[str] = None,
) -> CitationResult:
    """Convenience function to add citations to content.

    Args:
        content: Generated content
        refs: Source references
        github_base: Optional GitHub base URL for links

    Returns:
        CitationResult with cited content
    """
    config = CitationConfig(
        format="github" if github_base else "markdown",
        github_base=github_base,
    )
    system = CitationSystem(config)
    return system.add_citations(content, refs)


def extract_cited_symbols(content: str) -> list[tuple[str, str]]:
    """Extract symbols and their citations from already-cited content.

    Returns list of (symbol, citation) tuples.
    """
    # Pattern for markdown links: [`Symbol`](path#L123)
    md_pattern = r'\[`([^`]+)`\]\(([^)]+)\)'
    md_matches = re.findall(md_pattern, content)

    # Pattern for inline: `Symbol` (path:123)
    inline_pattern = r'`([^`]+)`\s*\(([^)]+)\)'
    inline_matches = re.findall(inline_pattern, content)

    return md_matches + inline_matches


def verify_citations(
    content: str,
    repo_path: Optional[Path] = None
) -> dict[str, bool]:
    """Verify all citations in content resolve to actual files.

    Returns dict mapping citation to validity.
    """
    citations = extract_cited_symbols(content)
    results = {}

    for symbol, citation in citations:
        valid = False

        # Parse file:line from citation
        if '#L' in citation:
            file_path = citation.split('#L')[0]
        elif ':' in citation:
            file_path = citation.split(':')[0]
        else:
            file_path = citation

        # Check if file exists (if repo_path provided)
        if repo_path:
            full_path = repo_path / file_path
            valid = full_path.exists()
        else:
            # Just check format is valid
            valid = bool(file_path and (file_path.endswith('.py') or '.' in file_path))

        results[f"{symbol}@{citation}"] = valid

    return results
