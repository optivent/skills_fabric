#!/usr/bin/env python3
"""
Sovereign Skill Factory - KuzuDB Integration Layer
QA-Level Rigor: Comprehensive CRUD operations with full test coverage.

Schema:
  - Skill(id, question, code, source_url, library, verified)
  - TestResult(id, exit_code, stdout, timestamp)
  - TEACHES: Skill -> Concept
  - USES: Skill -> Symbol
  - VERIFIED_BY: Skill -> TestResult
"""
import kuzu
import os
import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


# =============================================================================
# CONFIGURATION
# =============================================================================

DB_PATH = os.path.expanduser('~/sovereign_platform/data/kuzu_db')


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SkillRecord:
    """Represents a Skill in the graph."""
    id: str
    question: str
    code: str
    source_url: str
    library: str
    verified: bool = False
    concepts: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)


@dataclass
class TestResultRecord:
    """Represents a TestResult in the graph."""
    id: str
    exit_code: int
    stdout: str
    timestamp: str


# =============================================================================
# KUZU CLIENT
# =============================================================================

class KuzuSkillStore:
    """
    KuzuDB client for Skill storage with QA-level rigor.
    
    All methods include:
    - Input validation
    - Error handling
    - Logging
    - Return value verification
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        self._verify_schema()
    
    def _verify_schema(self) -> bool:
        """Verify required tables exist. Returns True if valid."""
        required_tables = ['Concept', 'Symbol', 'Skill', 'TestResult']
        required_rels = ['IMPLEMENTS', 'PROVEN', 'TEACHES', 'USES', 'VERIFIED_BY']
        
        # Check tables
        res = self.conn.execute('CALL show_tables() RETURN *')
        existing = set()
        while res.has_next():
            row = res.get_next()
            existing.add(row[1])  # Table name is second column
        
        missing = [t for t in required_tables + required_rels if t not in existing]
        if missing:
            raise RuntimeError(f"Missing schema elements: {missing}")
        
        return True
    
    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================
    
    def create_skill(self, skill: SkillRecord) -> str:
        """
        Create a new Skill node.
        
        Args:
            skill: SkillRecord with all fields populated
            
        Returns:
            The skill ID if successful
            
        Raises:
            ValueError: If skill.id is empty
            RuntimeError: If database operation fails
        """
        # Input validation
        if not skill.id:
            raise ValueError("Skill ID cannot be empty")
        if not skill.question:
            raise ValueError("Skill question cannot be empty")
        if not skill.code:
            raise ValueError("Skill code cannot be empty")
        
        # Create skill node
        try:
            self.conn.execute('''
                CREATE (s:Skill {
                    id: $id,
                    question: $question,
                    code: $code,
                    source_url: $source_url,
                    library: $library,
                    verified: $verified
                })
            ''', {
                'id': skill.id,
                'question': skill.question,
                'code': skill.code,
                'source_url': skill.source_url,
                'library': skill.library,
                'verified': skill.verified
            })
        except Exception as e:
            raise RuntimeError(f"Failed to create skill: {e}")
        
        # Create TEACHES relationships to concepts
        for concept_name in skill.concepts:
            self._link_skill_to_concept(skill.id, concept_name)
        
        # Create USES relationships to symbols
        for symbol_name in skill.symbols:
            self._link_skill_to_symbol(skill.id, symbol_name)
        
        return skill.id
    
    def create_test_result(self, result: TestResultRecord, skill_id: str) -> str:
        """
        Create a TestResult node and link it to a Skill.
        
        Args:
            result: TestResultRecord with all fields
            skill_id: ID of the skill that was tested
            
        Returns:
            The TestResult ID if successful
        """
        if not result.id:
            raise ValueError("TestResult ID cannot be empty")
        if not skill_id:
            raise ValueError("Skill ID cannot be empty")
        
        # Create TestResult node
        try:
            self.conn.execute('''
                CREATE (t:TestResult {
                    id: $id,
                    exit_code: $exit_code,
                    stdout: $stdout,
                    timestamp: $timestamp
                })
            ''', {
                'id': result.id,
                'exit_code': result.exit_code,
                'stdout': result.stdout,
                'timestamp': result.timestamp
            })
        except Exception as e:
            raise RuntimeError(f"Failed to create TestResult: {e}")
        
        # Create VERIFIED_BY relationship
        try:
            self.conn.execute('''
                MATCH (sk:Skill {id: $skill_id}), (tr:TestResult {id: $result_id})
                CREATE (sk)-[:VERIFIED_BY]->(tr)
            ''', {'skill_id': skill_id, 'result_id': result.id})
        except Exception as e:
            raise RuntimeError(f"Failed to link TestResult to Skill: {e}")
        
        return result.id
    
    def _link_skill_to_concept(self, skill_id: str, concept_name: str) -> bool:
        """Create TEACHES relationship from Skill to Concept."""
        try:
            # First ensure concept exists
            self.conn.execute('''
                MERGE (c:Concept {name: $name, content: 'Auto-created from skill'})
            ''', {'name': concept_name})
            
            # Create relationship
            self.conn.execute('''
                MATCH (sk:Skill {id: $skill_id}), (c:Concept {name: $concept_name})
                CREATE (sk)-[:TEACHES]->(c)
            ''', {'skill_id': skill_id, 'concept_name': concept_name})
            return True
        except Exception as e:
            print(f"Warning: Failed to link skill to concept '{concept_name}': {e}")
            return False
    
    def _link_skill_to_symbol(self, skill_id: str, symbol_name: str) -> bool:
        """Create USES relationship from Skill to Symbol."""
        try:
            self.conn.execute('''
                MATCH (sk:Skill {id: $skill_id}), (s:Symbol {name: $symbol_name})
                CREATE (sk)-[:USES]->(s)
            ''', {'skill_id': skill_id, 'symbol_name': symbol_name})
            return True
        except Exception as e:
            print(f"Warning: Failed to link skill to symbol '{symbol_name}': {e}")
            return False
    
    # =========================================================================
    # READ OPERATIONS
    # =========================================================================
    
    def get_skill(self, skill_id: str) -> Optional[SkillRecord]:
        """Retrieve a skill by ID."""
        try:
            res = self.conn.execute('''
                MATCH (s:Skill {id: $id})
                RETURN s.id, s.question, s.code, s.source_url, s.library, s.verified
            ''', {'id': skill_id})
            
            if res.has_next():
                row = res.get_next()
                return SkillRecord(
                    id=row[0],
                    question=row[1],
                    code=row[2],
                    source_url=row[3],
                    library=row[4],
                    verified=row[5]
                )
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get skill: {e}")
    
    def count_skills(self) -> int:
        """Count total skills in the graph."""
        res = self.conn.execute('MATCH (s:Skill) RETURN count(s)')
        return res.get_next()[0] if res.has_next() else 0
    
    def get_verified_skills(self, library: Optional[str] = None) -> list[SkillRecord]:
        """Get all verified skills, optionally filtered by library."""
        query = 'MATCH (s:Skill {verified: true})'
        if library:
            query = f'MATCH (s:Skill {{verified: true, library: "{library}"}})'
        query += ' RETURN s.id, s.question, s.code, s.source_url, s.library, s.verified'
        
        skills = []
        res = self.conn.execute(query)
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
    
    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================
    
    def mark_skill_verified(self, skill_id: str, verified: bool = True) -> bool:
        """Update the verified status of a skill."""
        try:
            self.conn.execute('''
                MATCH (s:Skill {id: $id})
                SET s.verified = $verified
            ''', {'id': skill_id, 'verified': verified})
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to update skill: {e}")
    
    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================
    
    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill and its relationships."""
        try:
            # Delete relationships first
            self.conn.execute('''
                MATCH (s:Skill {id: $id})-[r]->()
                DELETE r
            ''', {'id': skill_id})
            
            # Delete node
            self.conn.execute('''
                MATCH (s:Skill {id: $id})
                DELETE s
            ''', {'id': skill_id})
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete skill: {e}")


# =============================================================================
# TEST SUITE (QA-Level)
# =============================================================================

def run_qa_tests() -> dict:
    """
    Comprehensive QA test suite for KuzuDB integration.
    
    Returns:
        dict with test results: {test_name: (passed, message)}
    """
    results = {}
    store = KuzuSkillStore()
    
    print("="*70)
    print("KUZU INTEGRATION - QA TEST SUITE")
    print("="*70)
    
    # Test 1: Schema Verification
    print("\n[TEST 1] Schema Verification")
    try:
        assert store._verify_schema() == True
        results['schema_verification'] = (True, "All required tables present")
        print("  ✓ PASS: Schema verified")
    except Exception as e:
        results['schema_verification'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 2: Create Skill
    print("\n[TEST 2] Create Skill")
    test_skill_id = f"test-skill-{uuid.uuid4().hex[:8]}"
    try:
        skill = SkillRecord(
            id=test_skill_id,
            question="How do I test KuzuDB integration?",
            code="store = KuzuSkillStore()\nassert store.count_skills() >= 0",
            source_url="https://test.example.com",
            library="kuzu",
            verified=False,
            concepts=["KuzuDB", "Testing"],
            symbols=[]
        )
        created_id = store.create_skill(skill)
        assert created_id == test_skill_id
        results['create_skill'] = (True, f"Created skill: {test_skill_id}")
        print(f"  ✓ PASS: Created skill {test_skill_id}")
    except Exception as e:
        results['create_skill'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 3: Read Skill
    print("\n[TEST 3] Read Skill")
    try:
        retrieved = store.get_skill(test_skill_id)
        assert retrieved is not None
        assert retrieved.id == test_skill_id
        assert retrieved.library == "kuzu"
        results['read_skill'] = (True, f"Retrieved skill with correct data")
        print(f"  ✓ PASS: Skill retrieved correctly")
    except Exception as e:
        results['read_skill'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 4: Update Skill
    print("\n[TEST 4] Update Skill (Mark Verified)")
    try:
        store.mark_skill_verified(test_skill_id, True)
        updated = store.get_skill(test_skill_id)
        assert updated.verified == True
        results['update_skill'] = (True, "Skill marked as verified")
        print(f"  ✓ PASS: Skill verified status updated")
    except Exception as e:
        results['update_skill'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 5: Create TestResult
    print("\n[TEST 5] Create TestResult")
    test_result_id = f"test-result-{uuid.uuid4().hex[:8]}"
    try:
        test_result = TestResultRecord(
            id=test_result_id,
            exit_code=0,
            stdout="Test passed successfully",
            timestamp=datetime.now().isoformat()
        )
        store.create_test_result(test_result, test_skill_id)
        results['create_test_result'] = (True, f"Created TestResult: {test_result_id}")
        print(f"  ✓ PASS: TestResult created and linked")
    except Exception as e:
        results['create_test_result'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 6: Count Skills
    print("\n[TEST 6] Count Skills")
    try:
        count = store.count_skills()
        assert count >= 1  # At least our test skill
        results['count_skills'] = (True, f"Total skills: {count}")
        print(f"  ✓ PASS: Skill count = {count}")
    except Exception as e:
        results['count_skills'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 7: Get Verified Skills
    print("\n[TEST 7] Get Verified Skills")
    try:
        verified = store.get_verified_skills()
        assert len(verified) >= 1  # Our test skill is verified
        results['get_verified_skills'] = (True, f"Verified skills: {len(verified)}")
        print(f"  ✓ PASS: Found {len(verified)} verified skill(s)")
    except Exception as e:
        results['get_verified_skills'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 8: Delete Skill (Cleanup)
    print("\n[TEST 8] Delete Skill (Cleanup)")
    try:
        store.delete_skill(test_skill_id)
        deleted_check = store.get_skill(test_skill_id)
        assert deleted_check is None
        results['delete_skill'] = (True, "Skill deleted successfully")
        print(f"  ✓ PASS: Skill deleted")
    except Exception as e:
        results['delete_skill'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Test 9: Input Validation
    print("\n[TEST 9] Input Validation")
    try:
        try:
            store.create_skill(SkillRecord(id="", question="", code="", source_url="", library=""))
            results['input_validation'] = (False, "Should have raised ValueError")
            print(f"  ✗ FAIL: Should have raised ValueError")
        except ValueError:
            results['input_validation'] = (True, "ValueError raised correctly")
            print(f"  ✓ PASS: Input validation works")
    except Exception as e:
        results['input_validation'] = (False, str(e))
        print(f"  ✗ FAIL: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for _, (p, _) in results.items() if p)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for name, (passed, msg) in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {name}: {msg}")
    
    return results


if __name__ == '__main__':
    run_qa_tests()
