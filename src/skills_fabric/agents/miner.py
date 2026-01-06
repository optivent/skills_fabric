"""Miner Agent - Source code search and extraction.

Specializes in:
- Finding relevant source files
- Extracting symbols from code
- Pattern matching across codebase
- Building search indexes

Oh My OpenCode Inspiration:
Like the "Librarian" agent that manages code context,
but focused on mining source code for skill generation.

Model: Haiku (fast search operations)
"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from .base import BaseAgent, AgentRole, AgentResult, AgentStatus


@dataclass
class MiningTask:
    """Task for the miner agent."""
    query: str                    # Search query
    repo_path: str               # Repository to search
    file_patterns: list[str] = None  # e.g., ["*.py", "*.ts"]
    max_results: int = 50
    include_content: bool = True


@dataclass
class MiningResult:
    """Result from mining operation."""
    files_searched: int
    matches_found: int
    symbols: list[dict]
    code_snippets: list[dict]


class MinerAgent(BaseAgent[MiningResult]):
    """Agent that mines source code for relevant content.

    Responsibilities:
    - Search files matching patterns
    - Extract symbols using AST
    - Find code snippets matching queries
    - Build symbol indexes
    """

    def __init__(self):
        super().__init__(AgentRole.MINER)

    def execute(self, task: MiningTask, context: dict = None) -> AgentResult:
        """Execute mining task.

        Args:
            task: MiningTask with search parameters
            context: Shared context

        Returns:
            AgentResult with MiningResult
        """
        start = self._start_execution()

        try:
            repo_path = Path(task.repo_path)
            if not repo_path.exists():
                return self._end_execution(
                    start,
                    error=f"Repository not found: {task.repo_path}"
                )

            # Find matching files
            files = self._find_files(repo_path, task.file_patterns)

            # Extract symbols
            symbols = self._extract_symbols(files, task.query)

            # Extract code snippets
            snippets = self._extract_snippets(
                files, task.query, task.max_results
            ) if task.include_content else []

            result = MiningResult(
                files_searched=len(files),
                matches_found=len(symbols) + len(snippets),
                symbols=symbols[:task.max_results],
                code_snippets=snippets
            )

            # Send results to supervisor
            self.send_message(
                AgentRole.SUPERVISOR,
                f"Mined {result.matches_found} results from {result.files_searched} files",
                result_summary=True
            )

            return self._end_execution(start, output=result)

        except Exception as e:
            return self._end_execution(start, error=str(e))

    def _find_files(
        self,
        repo_path: Path,
        patterns: list[str] = None
    ) -> list[Path]:
        """Find files matching patterns."""
        patterns = patterns or ["*.py", "*.ts", "*.js"]
        files = []

        for pattern in patterns:
            for f in repo_path.rglob(pattern):
                # Skip common non-source directories
                skip_dirs = ['node_modules', '.git', '__pycache__', 'venv', '.venv']
                if not any(d in str(f) for d in skip_dirs):
                    files.append(f)

        return files

    def _extract_symbols(
        self,
        files: list[Path],
        query: str
    ) -> list[dict]:
        """Extract symbols matching query."""
        from ..trust.hard_content import HardContentVerifier

        verifier = HardContentVerifier()
        symbols = []
        query_lower = query.lower()

        for file in files:
            if file.suffix == '.py':
                extracted, result = verifier.extract_verified_symbols(str(file))
                if result.trusted:
                    for sym in extracted:
                        # Filter by query relevance
                        if query_lower in sym.name.lower():
                            symbols.append({
                                "name": sym.name,
                                "kind": sym.kind,
                                "file": str(file),
                                "line": sym.line,
                                "signature": sym.signature
                            })

        return symbols

    def _extract_snippets(
        self,
        files: list[Path],
        query: str,
        max_results: int
    ) -> list[dict]:
        """Extract code snippets containing query."""
        snippets = []
        query_lower = query.lower()

        for file in files:
            if len(snippets) >= max_results:
                break

            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # Get context (5 lines before and after)
                        start = max(0, i - 5)
                        end = min(len(lines), i + 6)
                        snippet = '\n'.join(lines[start:end])

                        snippets.append({
                            "file": str(file),
                            "line": i + 1,
                            "snippet": snippet,
                            "match_line": line.strip()
                        })

                        if len(snippets) >= max_results:
                            break

            except Exception:
                continue

        return snippets

    def search_symbols(
        self,
        repo_path: str,
        symbol_name: str
    ) -> list[dict]:
        """Quick search for a specific symbol."""
        task = MiningTask(
            query=symbol_name,
            repo_path=repo_path,
            max_results=20,
            include_content=False
        )
        result = self.execute(task)
        return result.output.symbols if result.success else []
