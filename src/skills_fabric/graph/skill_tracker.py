"""Skill Tracker - Track skills and their symbol references in KuzuDB.

This module connects the skill generation pipeline with the KuzuDB
code knowledge graph, enabling:
- Symbol citation tracking for skills
- Graph-based skill discovery
- Relationship analysis between skills and code
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path
import time
import re

try:
    from .schema import CodeGraph
except ImportError:
    # Load directly for standalone testing
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "schema",
        str(Path(__file__).parent / "schema.py")
    )
    schema_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema_module)
    CodeGraph = schema_module.CodeGraph


@dataclass
class SkillCitation:
    """A citation from a skill to source code."""
    symbol_name: str
    file_path: str
    line_number: int
    citation_text: str  # e.g., "path/file.py:123"


@dataclass
class TrackedSkill:
    """A skill tracked in the knowledge graph."""
    skill_id: str
    name: str
    library: str
    content: str
    citations: list[SkillCitation] = field(default_factory=list)
    created_at: int = 0


class SkillTracker:
    """Tracks skills and their symbol references in KuzuDB.

    This enables:
    - Querying which symbols a skill uses
    - Finding skills that use a particular symbol
    - Tracking skill-to-skill relationships via shared symbols
    - Verifying citation integrity
    """

    def __init__(self, db_path: str = "./skills_graph"):
        """Initialize tracker.

        Args:
            db_path: Path to KuzuDB database
        """
        self.graph = CodeGraph(db_path)
        self.graph.initialize_schema()

    def register_skill(
        self,
        skill_id: str,
        name: str,
        library: str,
        content: str,
    ) -> TrackedSkill:
        """Register a new skill in the graph.

        Args:
            skill_id: Unique skill identifier
            name: Skill name
            library: Library the skill is for
            content: Skill markdown content

        Returns:
            TrackedSkill with extracted citations
        """
        # Extract citations from content
        citations = self._extract_citations(content)

        # Add skill to graph
        created_at = int(time.time())
        self.graph.add_skill(
            id=skill_id,
            name=name,
            library=library,
            content=content,
            created_at=created_at,
        )

        # Add symbols and link to skill
        for citation in citations:
            symbol_id = f"{library}:{citation.symbol_name}"

            # Add symbol if not exists
            self.graph.add_symbol(
                id=symbol_id,
                name=citation.symbol_name,
                kind="reference",
                file_path=citation.file_path,
                line_start=citation.line_number,
            )

            # Link skill to symbol
            self.graph.link_skill_uses_symbol(
                skill_id=skill_id,
                symbol_id=symbol_id,
                citation=citation.citation_text,
            )

        return TrackedSkill(
            skill_id=skill_id,
            name=name,
            library=library,
            content=content,
            citations=citations,
            created_at=created_at,
        )

    def _extract_citations(self, content: str) -> list[SkillCitation]:
        """Extract citations from skill content.

        Looks for patterns like:
        - `file.py:123`
        - See `path/to/file.py:456`
        - [src/module.py:789](url)
        """
        citations = []
        seen = set()

        # Pattern: file.py:line
        pattern = r'`?([a-zA-Z0-9_/.-]+\.py):(\d+)`?'
        for match in re.finditer(pattern, content):
            file_path = match.group(1)
            line_num = int(match.group(2))
            citation_text = f"{file_path}:{line_num}"

            if citation_text not in seen:
                seen.add(citation_text)

                # Extract symbol name from context (word before file path)
                start = max(0, match.start() - 50)
                context = content[start:match.start()]
                symbol_match = re.search(r'`([A-Z][a-zA-Z0-9_]+)`[^`]*$', context)
                symbol_name = symbol_match.group(1) if symbol_match else f"symbol_{line_num}"

                citations.append(SkillCitation(
                    symbol_name=symbol_name,
                    file_path=file_path,
                    line_number=line_num,
                    citation_text=citation_text,
                ))

        return citations

    def get_skill_symbols(self, skill_id: str) -> list[dict]:
        """Get all symbols referenced by a skill.

        Args:
            skill_id: Skill identifier

        Returns:
            List of symbol info dicts
        """
        return self.graph.query_symbols_for_skill(skill_id)

    def find_skills_using_symbol(self, symbol_name: str) -> list[dict]:
        """Find all skills that reference a particular symbol.

        Args:
            symbol_name: Name of symbol to search for

        Returns:
            List of skill info dicts
        """
        result = self.graph.conn.execute(
            """
            MATCH (s:Skill)-[r:SKILL_USES]->(sym:Symbol)
            WHERE sym.name = $name
            RETURN s.id, s.name, s.library, r.citation
            """,
            {"name": symbol_name}
        )
        return result.get_as_df().to_dict('records')

    def find_related_skills(self, skill_id: str) -> list[dict]:
        """Find skills related via shared symbol references.

        Args:
            skill_id: Source skill identifier

        Returns:
            List of related skill info dicts with shared symbol count
        """
        result = self.graph.conn.execute(
            """
            MATCH (s1:Skill {id: $skill_id})-[:SKILL_USES]->(sym:Symbol)<-[:SKILL_USES]-(s2:Skill)
            WHERE s1.id <> s2.id
            RETURN s2.id, s2.name, s2.library, count(sym) as shared_symbols
            ORDER BY shared_symbols DESC
            """,
            {"skill_id": skill_id}
        )
        return result.get_as_df().to_dict('records')

    def get_citation_integrity(self, skill_id: str) -> dict:
        """Check citation integrity for a skill.

        Args:
            skill_id: Skill identifier

        Returns:
            Dict with citation stats and any issues
        """
        symbols = self.get_skill_symbols(skill_id)

        total = len(symbols)
        valid = sum(1 for s in symbols if s.get('sym.file_path'))
        invalid = total - valid

        return {
            'total_citations': total,
            'valid_citations': valid,
            'invalid_citations': invalid,
            'integrity_score': valid / total if total > 0 else 1.0,
            'symbols': symbols,
        }

    def get_library_stats(self, library: str) -> dict:
        """Get statistics for skills in a library.

        Args:
            library: Library name

        Returns:
            Statistics dict
        """
        # Count skills
        skill_result = self.graph.conn.execute(
            "MATCH (s:Skill) WHERE s.library = $lib RETURN count(s) as cnt",
            {"lib": library}
        )
        skill_count = skill_result.get_as_df()['cnt'].iloc[0] if len(skill_result.get_as_df()) > 0 else 0

        # Count unique symbols
        symbol_result = self.graph.conn.execute(
            """
            MATCH (s:Skill)-[:SKILL_USES]->(sym:Symbol)
            WHERE s.library = $lib
            RETURN count(DISTINCT sym) as cnt
            """,
            {"lib": library}
        )
        symbol_count = symbol_result.get_as_df()['cnt'].iloc[0] if len(symbol_result.get_as_df()) > 0 else 0

        return {
            'library': library,
            'skill_count': int(skill_count),
            'symbol_count': int(symbol_count),
            'avg_symbols_per_skill': symbol_count / skill_count if skill_count > 0 else 0,
        }

    def close(self):
        """Close the database connection."""
        self.graph.close()


def populate_from_skills_directory(
    tracker: SkillTracker,
    skills_dir: str,
    library: str,
) -> list[TrackedSkill]:
    """Populate tracker from a directory of skill files.

    Args:
        tracker: SkillTracker instance
        skills_dir: Path to directory containing skill markdown files
        library: Library name for all skills

    Returns:
        List of tracked skills
    """
    skills_path = Path(skills_dir)
    tracked = []

    for skill_file in skills_path.glob("*.md"):
        content = skill_file.read_text()

        # Generate skill ID from filename
        skill_id = f"{library}:{skill_file.stem}"
        name = skill_file.stem.replace('_', ' ').title()

        skill = tracker.register_skill(
            skill_id=skill_id,
            name=name,
            library=library,
            content=content,
        )

        tracked.append(skill)

    return tracked
