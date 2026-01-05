"""Linker Agent - Creates PROVEN relationships.

Specializes in:
- Matching documentation to source code
- Creating verified links between concepts and symbols
- Confidence scoring for link quality
- Building the knowledge graph

Model: Sonnet (reasoning for matching)
"""
from dataclasses import dataclass
from typing import Optional

from .base import BaseAgent, AgentRole, AgentResult


@dataclass
class LinkingTask:
    """Task for the linker agent."""
    concepts: list[dict]     # Concepts to link
    symbols: list[dict]      # Available symbols
    min_confidence: float = 0.5
    strategy: str = "multi"  # exact, filename, content, multi


@dataclass
class LinkingResult:
    """Result from linking operation."""
    links_created: int
    high_confidence: int  # Links with confidence > 0.8
    medium_confidence: int  # 0.5 - 0.8
    failed_matches: int
    links: list[dict]


class LinkerAgent(BaseAgent[LinkingResult]):
    """Agent that creates PROVEN relationships.

    Responsibilities:
    - Match concepts to symbols using multiple strategies
    - Score confidence for each match
    - Create PROVEN links in database
    - Report unmatched concepts
    """

    def __init__(self):
        super().__init__(AgentRole.LINKER)

    def execute(self, task: LinkingTask, context: dict = None) -> AgentResult:
        """Execute linking task.

        Args:
            task: LinkingTask with concepts and symbols
            context: Shared context

        Returns:
            AgentResult with LinkingResult
        """
        start = self._start_execution()

        try:
            links = []
            failed = 0

            for concept in task.concepts:
                matches = self._find_matches(
                    concept, task.symbols, task.strategy
                )

                if matches:
                    # Take best match
                    best = max(matches, key=lambda m: m['confidence'])
                    if best['confidence'] >= task.min_confidence:
                        links.append(best)
                        self._create_link(best)
                    else:
                        failed += 1
                else:
                    failed += 1

            result = LinkingResult(
                links_created=len(links),
                high_confidence=sum(1 for l in links if l['confidence'] > 0.8),
                medium_confidence=sum(1 for l in links if 0.5 <= l['confidence'] <= 0.8),
                failed_matches=failed,
                links=links
            )

            self.send_message(
                AgentRole.SUPERVISOR,
                f"Created {result.links_created} PROVEN links ({result.high_confidence} high confidence)",
                result_summary=True
            )

            return self._end_execution(start, output=result)

        except Exception as e:
            return self._end_execution(start, error=str(e))

    def _find_matches(
        self,
        concept: dict,
        symbols: list[dict],
        strategy: str
    ) -> list[dict]:
        """Find symbol matches for a concept."""
        matches = []
        concept_name = concept.get('name', '').lower()
        concept_content = concept.get('content', '').lower()

        for symbol in symbols:
            symbol_name = symbol.get('name', '')
            file_path = symbol.get('file_path', '')

            confidence = 0.0
            match_type = None

            # Strategy 1: Exact name match
            if strategy in ['exact', 'multi']:
                if symbol_name.lower() in concept_name:
                    confidence = max(confidence, 0.9)
                    match_type = 'exact'

            # Strategy 2: Filename match
            if strategy in ['filename', 'multi'] and file_path:
                from pathlib import Path
                filename = Path(file_path).stem.lower()
                if filename in concept_content:
                    confidence = max(confidence, 0.7)
                    match_type = match_type or 'filename'

            # Strategy 3: Content match
            if strategy in ['content', 'multi']:
                if symbol_name.lower() in concept_content:
                    confidence = max(confidence, 0.5)
                    match_type = match_type or 'content'

            if confidence > 0:
                matches.append({
                    'concept_name': concept.get('name'),
                    'symbol_name': symbol_name,
                    'file_path': file_path,
                    'confidence': confidence,
                    'match_type': match_type
                })

        return matches

    def _create_link(self, link: dict) -> bool:
        """Create PROVEN link in database."""
        try:
            from ..core.database import db

            db.execute(
                """
                MATCH (c:Concept {name: $concept_name}), (s:Symbol {name: $symbol_name})
                CREATE (c)-[:PROVEN {confidence: $confidence, match_type: $match_type}]->(s)
                """,
                {
                    "concept_name": link['concept_name'],
                    "symbol_name": link['symbol_name'],
                    "confidence": link['confidence'],
                    "match_type": link['match_type']
                }
            )
            return True
        except Exception:
            return False

    def link_single(
        self,
        concept_name: str,
        symbol_name: str,
        confidence: float = 0.7
    ) -> bool:
        """Create a single PROVEN link."""
        link = {
            'concept_name': concept_name,
            'symbol_name': symbol_name,
            'confidence': confidence,
            'match_type': 'manual'
        }
        return self._create_link(link)
