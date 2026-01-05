"""KuzuDB connection and schema management."""
import kuzu
from pathlib import Path
from typing import Optional


class KuzuDatabase:
    """KuzuDB wrapper for Skills Fabric."""
    
    def __init__(self, db_path: Optional[Path] = None):
        from .config import config
        self.db_path = db_path or config.kuzu_db_path
        self._db: Optional[kuzu.Database] = None
        self._conn: Optional[kuzu.Connection] = None
    
    @property
    def db(self) -> kuzu.Database:
        if self._db is None:
            self._db = kuzu.Database(str(self.db_path))
        return self._db
    
    @property
    def conn(self) -> kuzu.Connection:
        if self._conn is None:
            self._conn = kuzu.Connection(self.db)
        return self._conn
    
    def init_schema(self) -> None:
        """Initialize the database schema."""
        # Node tables
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Concept(
                name STRING PRIMARY KEY,
                content STRING,
                source_doc STRING
            )
        """)
        
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Symbol(
                name STRING PRIMARY KEY,
                file_path STRING,
                line INT64
            )
        """)
        
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Skill(
                id STRING PRIMARY KEY,
                question STRING,
                code STRING,
                source_url STRING,
                library STRING,
                verified BOOL
            )
        """)
        
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS TestResult(
                id STRING PRIMARY KEY,
                passed BOOL,
                output STRING,
                error STRING
            )
        """)
        
        # Relationship tables
        relationships = [
            "CREATE REL TABLE IF NOT EXISTS PROVEN(FROM Concept TO Symbol)",
            "CREATE REL TABLE IF NOT EXISTS TEACHES(FROM Skill TO Concept)",
            "CREATE REL TABLE IF NOT EXISTS USES(FROM Skill TO Symbol)",
            "CREATE REL TABLE IF NOT EXISTS VERIFIED_BY(FROM Skill TO TestResult)",
        ]
        for rel in relationships:
            try:
                self.conn.execute(rel)
            except Exception:
                pass  # Already exists
    
    def execute(self, query: str, params: dict = None):
        """Execute a Cypher query."""
        return self.conn.execute(query, params or {})
    
    def count(self, table: str) -> int:
        """Count nodes in a table."""
        res = self.conn.execute(f"MATCH (n:{table}) RETURN count(n)")
        return res.get_next()[0]


# Global database instance
db = KuzuDatabase()
