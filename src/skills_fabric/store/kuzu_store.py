"""KuzuDB skill storage operations."""
import uuid
from typing import Optional
from dataclasses import dataclass


@dataclass
class SkillRecord:
    """A skill record for storage."""
    question: str
    code: str
    source_url: str
    library: str
    verified: bool = False
    id: str = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"skill-{uuid.uuid4().hex[:8]}"


class KuzuSkillStore:
    """Store and retrieve skills from KuzuDB."""
    
    def __init__(self):
        from ..core.database import db
        self.db = db
    
    def create_skill(self, skill: SkillRecord) -> str:
        """Create a new skill in the database.

        Uses parameterized queries to prevent Cypher injection.
        """
        self.db.execute(
            """
            CREATE (s:Skill {
                id: $id,
                question: $question,
                code: $code,
                source_url: $source_url,
                library: $library,
                verified: $verified
            })
            """,
            {
                "id": skill.id,
                "question": skill.question,
                "code": skill.code[:2000],
                "source_url": skill.source_url,
                "library": skill.library,
                "verified": skill.verified
            }
        )

        return skill.id
    
    def get_skill(self, skill_id: str) -> Optional[SkillRecord]:
        """Retrieve a skill by ID.

        Uses parameterized queries to prevent Cypher injection.
        """
        res = self.db.execute(
            """
            MATCH (s:Skill {id: $skill_id})
            RETURN s.question, s.code, s.source_url, s.library, s.verified
            """,
            {"skill_id": skill_id}
        )
        
        if res.has_next():
            row = res.get_next()
            return SkillRecord(
                id=skill_id,
                question=row[0],
                code=row[1],
                source_url=row[2],
                library=row[3],
                verified=row[4]
            )
        return None
    
    def link_teaches(self, skill_id: str, concept_name: str) -> bool:
        """Create TEACHES relationship.

        Uses parameterized queries to prevent Cypher injection.
        """
        try:
            self.db.execute(
                """
                MATCH (sk:Skill {id: $skill_id}), (c:Concept {name: $concept_name})
                CREATE (sk)-[:TEACHES]->(c)
                """,
                {"skill_id": skill_id, "concept_name": concept_name}
            )
            return True
        except Exception:
            return False
    
    def link_uses(self, skill_id: str, symbol_name: str) -> bool:
        """Create USES relationship.

        Uses parameterized queries to prevent Cypher injection.
        """
        try:
            self.db.execute(
                """
                MATCH (sk:Skill {id: $skill_id}), (s:Symbol {name: $symbol_name})
                CREATE (sk)-[:USES]->(s)
                """,
                {"skill_id": skill_id, "symbol_name": symbol_name}
            )
            return True
        except Exception:
            return False
    
    def count_skills(self) -> int:
        """Count total skills."""
        return self.db.count("Skill")
    
    def list_skills(self, limit: int = 50) -> list[SkillRecord]:
        """List recent skills.

        Uses parameterized queries to prevent Cypher injection.
        """
        res = self.db.execute(
            """
            MATCH (s:Skill)
            RETURN s.id, s.question, s.code, s.source_url, s.library, s.verified
            LIMIT $limit
            """,
            {"limit": limit}
        )
        
        skills = []
        while res.has_next():
            row = res.get_next()
            skills.append(SkillRecord(
                id=row[0],
                question=row[1],
                code=row[2],
                source_url=row[3],
                library=row[4],
                verified=row[5]
            ))
        return skills
