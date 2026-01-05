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
        """Create a new skill in the database."""
        safe_q = skill.question.replace("'", "''")
        safe_code = skill.code.replace("'", "''").replace("\\", "\\\\")
        
        self.db.execute(f"""
            CREATE (s:Skill {{
                id: '{skill.id}',
                question: '{safe_q}',
                code: '{safe_code[:2000]}',
                source_url: '{skill.source_url}',
                library: '{skill.library}',
                verified: {str(skill.verified).lower()}
            }})
        """)
        
        return skill.id
    
    def get_skill(self, skill_id: str) -> Optional[SkillRecord]:
        """Retrieve a skill by ID."""
        res = self.db.execute(f"""
            MATCH (s:Skill {{id: '{skill_id}'}})
            RETURN s.question, s.code, s.source_url, s.library, s.verified
        """)
        
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
        """Create TEACHES relationship."""
        try:
            self.db.execute(f"""
                MATCH (sk:Skill {{id: '{skill_id}'}}), (c:Concept {{name: '{concept_name}'}})
                CREATE (sk)-[:TEACHES]->(c)
            """)
            return True
        except Exception:
            return False
    
    def link_uses(self, skill_id: str, symbol_name: str) -> bool:
        """Create USES relationship."""
        try:
            self.db.execute(f"""
                MATCH (sk:Skill {{id: '{skill_id}'}}), (s:Symbol {{name: '{symbol_name}'}})
                CREATE (sk)-[:USES]->(s)
            """)
            return True
        except Exception:
            return False
    
    def count_skills(self) -> int:
        """Count total skills."""
        return self.db.count("Skill")
    
    def list_skills(self, limit: int = 50) -> list[SkillRecord]:
        """List recent skills."""
        res = self.db.execute(f"""
            MATCH (s:Skill)
            RETURN s.id, s.question, s.code, s.source_url, s.library, s.verified
            LIMIT {limit}
        """)
        
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
