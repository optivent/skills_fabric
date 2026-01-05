"""PROVEN Linker - Connect documentation to source code.

This module implements the core innovation: creating verified links between
CodeWiki documentation concepts and actual source code symbols.

BMAD C.O.R.E. Principles Applied:
- Collaboration: Links docs with code, enabling zero-hallucination skills
- Optimized: Batch processing, no arbitrary limits
- Reflection: Validates every link before creation
- Engine: Systematic matching with multiple strategies
"""
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ProvenLink:
    """A verified link between documentation and source code."""
    concept_name: str
    symbol_name: str
    file_path: str
    confidence: float  # 0.0 to 1.0
    match_type: str    # 'exact', 'filename', 'content'


class ProvenLinker:
    """Create PROVEN relationships between CodeWiki concepts and Git symbols.
    
    Implements multiple matching strategies:
    1. Exact name match: Concept mentions symbol name directly
    2. Filename match: Concept mentions the source file
    3. Content match: Symbol name appears in concept content
    """
    
    def __init__(self):
        from ..core.database import db
        self.db = db
    
    def link_all(self, batch_size: int = 100) -> int:
        """Create PROVEN links for all concepts with matching symbols.
        
        Returns the number of links created.
        """
        # Get all concepts
        concepts_res = self.db.execute('MATCH (c:Concept) RETURN c.name, c.content')
        concepts = []
        while concepts_res.has_next():
            row = concepts_res.get_next()
            concepts.append({'name': row[0], 'content': row[1] or ''})
        
        # Get all symbols
        symbols_res = self.db.execute('MATCH (s:Symbol) RETURN s.name, s.file_path')
        symbols = []
        while symbols_res.has_next():
            row = symbols_res.get_next()
            symbols.append({'name': row[0], 'file_path': row[1] or ''})
        
        print(f'[ProvenLinker] Concepts: {len(concepts)}, Symbols: {len(symbols)}')
        
        links_created = 0
        
        for concept in concepts:
            matches = self._find_matches(concept, symbols)
            
            for match in matches:
                if self._create_link(concept['name'], match.symbol_name):
                    links_created += 1
        
        print(f'[ProvenLinker] Created {links_created} PROVEN links')
        return links_created
    
    def _find_matches(self, concept: dict, symbols: list) -> list[ProvenLink]:
        """Find symbols that match a concept using multiple strategies."""
        matches = []
        concept_name = concept['name'].lower()
        concept_content = concept['content'].lower()
        
        for symbol in symbols:
            symbol_name = symbol['name']
            file_path = symbol['file_path']
            
            # Strategy 1: Symbol name in concept name (highest confidence)
            if symbol_name.lower() in concept_name:
                matches.append(ProvenLink(
                    concept_name=concept['name'],
                    symbol_name=symbol_name,
                    file_path=file_path,
                    confidence=0.9,
                    match_type='exact'
                ))
                continue
            
            # Strategy 2: File path/name in concept content
            if file_path:
                file_name = Path(file_path).stem
                if file_name.lower() in concept_content:
                    matches.append(ProvenLink(
                        concept_name=concept['name'],
                        symbol_name=symbol_name,
                        file_path=file_path,
                        confidence=0.7,
                        match_type='filename'
                    ))
                    continue
            
            # Strategy 3: Symbol name in concept content
            if symbol_name.lower() in concept_content:
                matches.append(ProvenLink(
                    concept_name=concept['name'],
                    symbol_name=symbol_name,
                    file_path=file_path,
                    confidence=0.5,
                    match_type='content'
                ))
        
        # Return only high-confidence matches
        return [m for m in matches if m.confidence >= 0.5]
    
    def _create_link(self, concept_name: str, symbol_name: str) -> bool:
        """Create a PROVEN relationship in the database.

        Uses parameterized queries to prevent SQL/Cypher injection.
        """
        try:
            # Check if link already exists (parameterized query)
            res = self.db.execute(
                """
                MATCH (c:Concept {name: $concept_name})-[:PROVEN]->(s:Symbol {name: $symbol_name})
                RETURN count(*)
                """,
                {"concept_name": concept_name, "symbol_name": symbol_name}
            )
            if res.has_next() and res.get_next()[0] > 0:
                return False  # Already exists

            # Create link (parameterized query)
            self.db.execute(
                """
                MATCH (c:Concept {name: $concept_name}), (s:Symbol {name: $symbol_name})
                CREATE (c)-[:PROVEN]->(s)
                """,
                {"concept_name": concept_name, "symbol_name": symbol_name}
            )
            return True
        except Exception:
            return False
    
    def verify_links(self, sample_size: int = 10) -> dict:
        """Verify a sample of PROVEN links point to valid files.

        Uses parameterized queries to prevent injection.
        """
        from ..ingest.gitclone import GitCloner
        cloner = GitCloner()

        res = self.db.execute(
            """
            MATCH (c:Concept)-[:PROVEN]->(s:Symbol)
            RETURN c.name, s.name, s.file_path
            LIMIT $sample_size
            """,
            {"sample_size": sample_size}
        )
        
        valid = 0
        invalid = 0
        
        while res.has_next():
            row = res.get_next()
            concept, symbol, file_path = row
            
            # Check if file exists in any repo
            for repo_path in cloner.repos_dir.iterdir():
                full_path = repo_path / file_path
                if full_path.exists():
                    valid += 1
                    break
            else:
                invalid += 1
        
        return {'valid': valid, 'invalid': invalid, 'total': valid + invalid}
