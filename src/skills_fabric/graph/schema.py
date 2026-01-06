"""KuzuDB schema for code knowledge graph.

This module defines the schema for storing code symbols, relationships,
and skills in a graph database for efficient querying and navigation.
"""

import kuzu
from pathlib import Path
from typing import Optional


# Schema DDL statements
NODE_TABLES = [
    """
    CREATE NODE TABLE IF NOT EXISTS File (
        path STRING PRIMARY KEY,
        language STRING,
        size INT64,
        last_modified INT64
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Symbol (
        id STRING PRIMARY KEY,
        name STRING,
        kind STRING,
        file_path STRING,
        line_start INT32,
        line_end INT32,
        documentation STRING
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Concept (
        id STRING PRIMARY KEY,
        name STRING,
        description STRING,
        level INT32
    )
    """,
    """
    CREATE NODE TABLE IF NOT EXISTS Skill (
        id STRING PRIMARY KEY,
        name STRING,
        library STRING,
        content STRING,
        created_at INT64
    )
    """,
]

REL_TABLES = [
    """
    CREATE REL TABLE IF NOT EXISTS CONTAINS (
        FROM File TO Symbol
    )
    """,
    """
    CREATE REL TABLE IF NOT EXISTS CALLS (
        FROM Symbol TO Symbol,
        call_site INT32
    )
    """,
    """
    CREATE REL TABLE IF NOT EXISTS INHERITS (
        FROM Symbol TO Symbol
    )
    """,
    """
    CREATE REL TABLE IF NOT EXISTS IMPORTS (
        FROM File TO File
    )
    """,
    """
    CREATE REL TABLE IF NOT EXISTS REFERENCES (
        FROM Symbol TO Symbol,
        ref_type STRING
    )
    """,
    """
    CREATE REL TABLE IF NOT EXISTS DOCUMENTS (
        FROM Symbol TO Concept
    )
    """,
    """
    CREATE REL TABLE IF NOT EXISTS SKILL_USES (
        FROM Skill TO Symbol,
        citation STRING
    )
    """,
]


class CodeGraph:
    """KuzuDB-backed code knowledge graph."""

    def __init__(self, db_path: str = "./code_graph"):
        """Initialize the graph database.

        Args:
            db_path: Path to the database directory
        """
        self.db_path = Path(db_path)
        self.db = kuzu.Database(str(self.db_path))
        self.conn = kuzu.Connection(self.db)
        self._initialized = False

    def initialize_schema(self) -> None:
        """Create all node and relationship tables."""
        if self._initialized:
            return

        # Create node tables
        for ddl in NODE_TABLES:
            try:
                self.conn.execute(ddl)
            except Exception as e:
                # Table might already exist
                if "already exists" not in str(e).lower():
                    print(f"Warning creating table: {e}")

        # Create relationship tables
        for ddl in REL_TABLES:
            try:
                self.conn.execute(ddl)
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"Warning creating relationship: {e}")

        self._initialized = True

    def add_file(self, path: str, language: str, size: int, last_modified: int) -> None:
        """Add a file node to the graph."""
        self.conn.execute(
            "MERGE (f:File {path: $path}) SET f.language = $lang, f.size = $size, f.last_modified = $mod",
            {"path": path, "lang": language, "size": size, "mod": last_modified}
        )

    def add_symbol(
        self,
        id: str,
        name: str,
        kind: str,
        file_path: str,
        line_start: int,
        line_end: int = None,
        documentation: str = None
    ) -> None:
        """Add a symbol node to the graph."""
        self.conn.execute(
            """
            MERGE (s:Symbol {id: $id})
            SET s.name = $name, s.kind = $kind, s.file_path = $file_path,
                s.line_start = $line_start, s.line_end = $line_end,
                s.documentation = $doc
            """,
            {
                "id": id,
                "name": name,
                "kind": kind,
                "file_path": file_path,
                "line_start": line_start,
                "line_end": line_end or line_start,
                "doc": documentation or ""
            }
        )

    def add_skill(
        self,
        id: str,
        name: str,
        library: str,
        content: str,
        created_at: int
    ) -> None:
        """Add a skill node to the graph."""
        self.conn.execute(
            """
            MERGE (s:Skill {id: $id})
            SET s.name = $name, s.library = $library, s.content = $content,
                s.created_at = $created_at
            """,
            {"id": id, "name": name, "library": library, "content": content, "created_at": created_at}
        )

    def add_concept(
        self,
        id: str,
        name: str,
        description: str,
        level: int
    ) -> None:
        """Add a concept node for progressive disclosure."""
        self.conn.execute(
            """
            MERGE (c:Concept {id: $id})
            SET c.name = $name, c.description = $description, c.level = $level
            """,
            {"id": id, "name": name, "description": description, "level": level}
        )

    def link_file_contains_symbol(self, file_path: str, symbol_id: str) -> None:
        """Create CONTAINS relationship between file and symbol."""
        self.conn.execute(
            """
            MATCH (f:File {path: $file_path}), (s:Symbol {id: $symbol_id})
            MERGE (f)-[:CONTAINS]->(s)
            """,
            {"file_path": file_path, "symbol_id": symbol_id}
        )

    def link_symbol_calls(self, caller_id: str, callee_id: str, call_site: int = 0) -> None:
        """Create CALLS relationship between symbols."""
        self.conn.execute(
            """
            MATCH (caller:Symbol {id: $caller_id}), (callee:Symbol {id: $callee_id})
            MERGE (caller)-[:CALLS {call_site: $call_site}]->(callee)
            """,
            {"caller_id": caller_id, "callee_id": callee_id, "call_site": call_site}
        )

    def link_skill_uses_symbol(self, skill_id: str, symbol_id: str, citation: str) -> None:
        """Create SKILL_USES relationship for citation tracking."""
        self.conn.execute(
            """
            MATCH (skill:Skill {id: $skill_id}), (sym:Symbol {id: $symbol_id})
            MERGE (skill)-[:SKILL_USES {citation: $citation}]->(sym)
            """,
            {"skill_id": skill_id, "symbol_id": symbol_id, "citation": citation}
        )

    def query_symbols_for_skill(self, skill_id: str) -> list:
        """Get all symbols referenced by a skill."""
        result = self.conn.execute(
            """
            MATCH (s:Skill {id: $skill_id})-[r:SKILL_USES]->(sym:Symbol)
            RETURN sym.name, sym.kind, r.citation, sym.file_path, sym.line_start
            """,
            {"skill_id": skill_id}
        )
        return result.get_as_df().to_dict('records')

    def query_call_graph(self, symbol_name: str, depth: int = 3) -> list:
        """Trace the call graph from a symbol."""
        result = self.conn.execute(
            f"""
            MATCH path = (s:Symbol)-[:CALLS*1..{depth}]->(target:Symbol)
            WHERE s.name = $name
            RETURN path
            """,
            {"name": symbol_name}
        )
        return result.get_as_df().to_dict('records')

    def query_concepts_for_symbol(self, symbol_name: str) -> list:
        """Get progressive disclosure concepts for a symbol."""
        result = self.conn.execute(
            """
            MATCH (sym:Symbol)-[:DOCUMENTS]->(c:Concept)
            WHERE sym.name = $name
            RETURN c.name, c.level, c.description
            ORDER BY c.level
            """,
            {"name": symbol_name}
        )
        return result.get_as_df().to_dict('records')

    def get_stats(self) -> dict:
        """Get database statistics."""
        stats = {}

        for table in ["File", "Symbol", "Concept", "Skill"]:
            try:
                result = self.conn.execute(f"MATCH (n:{table}) RETURN count(n) as cnt")
                df = result.get_as_df()
                stats[table] = int(df['cnt'].iloc[0]) if len(df) > 0 else 0
            except:
                stats[table] = 0

        return stats

    def close(self) -> None:
        """Close the database connection."""
        # KuzuDB handles cleanup automatically
        pass


def create_test_graph(db_path: str = "./test_code_graph") -> CodeGraph:
    """Create a test graph with sample data."""
    import time

    graph = CodeGraph(db_path)
    graph.initialize_schema()

    # Add sample file
    graph.add_file(
        path="src/skills_fabric/verify/ddr.py",
        language="python",
        size=17751,
        last_modified=int(time.time())
    )

    # Add sample symbols
    graph.add_symbol(
        id="ddr:DirectDependencyRetriever",
        name="DirectDependencyRetriever",
        kind="class",
        file_path="src/skills_fabric/verify/ddr.py",
        line_start=50,
        documentation="Zero-hallucination retriever that only returns validated source symbols."
    )

    graph.add_symbol(
        id="ddr:retrieve",
        name="retrieve",
        kind="method",
        file_path="src/skills_fabric/verify/ddr.py",
        line_start=100,
        documentation="Retrieve validated symbols for a query."
    )

    # Add sample skill
    graph.add_skill(
        id="skill:docling_pdf",
        name="docling_pdf_conversion",
        library="docling",
        content="# PDF Conversion with Docling\n\nThis skill demonstrates...",
        created_at=int(time.time())
    )

    # Add sample concept
    graph.add_concept(
        id="concept:ddr_overview",
        name="DDR Overview",
        description="High-level overview of DirectDependencyRetriever",
        level=0
    )

    # Link file to symbol
    graph.link_file_contains_symbol(
        "src/skills_fabric/verify/ddr.py",
        "ddr:DirectDependencyRetriever"
    )

    # Link skill to symbol
    graph.link_skill_uses_symbol(
        "skill:docling_pdf",
        "ddr:DirectDependencyRetriever",
        "src/skills_fabric/verify/ddr.py:50"
    )

    return graph
