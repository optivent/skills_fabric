"""KuzuDB connection and schema management.

Thread-safe database access using thread-local connections.
"""
import kuzu
import threading
from pathlib import Path
from typing import Optional


class KuzuDatabase:
    """Thread-safe KuzuDB wrapper for Skills Fabric.

    Uses thread-local storage to ensure each thread gets its own connection,
    preventing race conditions and connection corruption.
    """

    def __init__(self, db_path: Optional[Path] = None):
        from .config import config
        self.db_path = db_path or config.kuzu_db_path
        self._db: Optional[kuzu.Database] = None
        self._db_lock = threading.Lock()
        self._local = threading.local()

    @property
    def db(self) -> kuzu.Database:
        """Get or create the database instance (thread-safe singleton)."""
        if self._db is None:
            with self._db_lock:
                # Double-check locking pattern
                if self._db is None:
                    self._db = kuzu.Database(str(self.db_path))
        return self._db

    @property
    def conn(self) -> kuzu.Connection:
        """Get thread-local connection.

        Each thread gets its own connection to prevent race conditions.
        """
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = kuzu.Connection(self.db)
        return self._local.conn
    
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
    
    # Valid table names (whitelist for security)
    VALID_TABLES = frozenset(["Concept", "Symbol", "Skill", "TestResult"])

    def count(self, table: str) -> int:
        """Count nodes in a table.

        Validates table name against whitelist to prevent injection.
        """
        if table not in self.VALID_TABLES:
            raise ValueError(f"Invalid table name: {table}. Must be one of: {self.VALID_TABLES}")
        res = self.conn.execute(f"MATCH (n:{table}) RETURN count(n)")
        return res.get_next()[0]

    def close(self) -> None:
        """Close thread-local connection."""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn = None


# Global database instance (thread-safe)
db = KuzuDatabase()
