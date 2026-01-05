"""Multi-Source Fusion Layer.

Combines Context7, Exa Search, and local grep for
comprehensive example retrieval with consensus scoring.
"""
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FusedSource:
    """A source contribution to the fusion."""
    origin: str  # "context7", "exa", "grep"
    content: str
    code_blocks: int
    confidence: float


@dataclass
class FusedResult:
    """Result of multi-source fusion."""
    query: str
    sources: list[FusedSource] = field(default_factory=list)
    merged_content: str = ""
    consensus_score: float = 0.0
    contradictions: list[str] = field(default_factory=list)


class SourceFusion:
    """Fuse multiple sources for comprehensive examples.
    
    The fusion layer queries:
    1. Context7 (3 queries per concept for coverage)
    2. Exa Search (semantic web search)
    3. Local grep (pattern matching in git clone)
    
    Results are merged, deduplicated, and ranked by consensus.
    
    Usage:
        fusion = SourceFusion()
        result = fusion.get_examples("StateGraph", "langgraph")
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        from .context7 import Context7Client
        from .exa_search import ExaClient
        
        self.context7 = Context7Client()
        self.exa = ExaClient()
        self.repo_path = repo_path
    
    def get_examples(self, concept: str, library: str) -> FusedResult:
        """Get examples from all sources, fused with consensus.
        
        Args:
            concept: The concept to find examples for
            library: The library name (for Context7 lookup)
        
        Returns:
            FusedResult with merged content and consensus score
        """
        result = FusedResult(query=f"{library} {concept}")
        
        # 1. Context7 multi-query
        c7_sources = self._query_context7(concept, library)
        result.sources.extend(c7_sources)
        
        # 2. Exa semantic search
        exa_sources = self._query_exa(concept, library)
        result.sources.extend(exa_sources)
        
        # 3. Local grep (if repo available)
        if self.repo_path:
            grep_sources = self._query_grep(concept)
            result.sources.extend(grep_sources)
        
        # 4. Merge and score
        result.merged_content = self._merge_sources(result.sources)
        result.consensus_score = self._calculate_consensus(result.sources)
        result.contradictions = self._find_contradictions(result.sources)
        
        return result
    
    def _query_context7(self, concept: str, library: str) -> list[FusedSource]:
        """Query Context7 from multiple angles."""
        sources = []
        
        # Resolve library ID
        lib_id = self.context7.resolve_library_id(library, concept)
        if not lib_id:
            return sources
        
        # Multi-angle queries
        queries = [
            f"how to use {concept}",
            f"{concept} tutorial example code",
            f"{concept} api reference documentation"
        ]
        
        for query in queries:
            content = self.context7.query_docs(lib_id, query)
            if content and len(content) > 100:
                code_blocks = content.count("```") // 2
                sources.append(FusedSource(
                    origin="context7",
                    content=content[:3000],
                    code_blocks=code_blocks,
                    confidence=0.9 if code_blocks > 0 else 0.6
                ))
        
        return sources
    
    def _query_exa(self, concept: str, library: str) -> list[FusedSource]:
        """Query Exa for tutorials and examples."""
        sources = []
        
        results = self.exa.search_code(f"{library} {concept}", language="python")
        
        for r in results[:3]:  # Top 3
            if r.text and len(r.text) > 100:
                code_blocks = r.text.count("```") // 2
                # Also check for inline code patterns
                if "def " in r.text or "class " in r.text:
                    code_blocks += 1
                
                sources.append(FusedSource(
                    origin="exa",
                    content=r.text[:2000],
                    code_blocks=code_blocks,
                    confidence=r.score * 0.8
                ))
        
        return sources
    
    def _query_grep(self, concept: str) -> list[FusedSource]:
        """Search local repo with grep."""
        sources = []
        
        if not self.repo_path or not self.repo_path.exists():
            return sources
        
        try:
            result = subprocess.run(
                ["grep", "-r", "-l", concept, str(self.repo_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            files = result.stdout.strip().split("\n")[:5]  # Top 5 files
            
            for f in files:
                if f and Path(f).exists():
                    with open(f, "r", errors="ignore") as fp:
                        content = fp.read()[:2000]
                    
                    sources.append(FusedSource(
                        origin="grep",
                        content=content,
                        code_blocks=1,  # Its source code
                        confidence=1.0  # Ground truth
                    ))
        except Exception:
            pass
        
        return sources
    
    def _merge_sources(self, sources: list[FusedSource]) -> str:
        """Merge sources, prioritizing by confidence and code blocks."""
        if not sources:
            return ""
        
        # Sort by (code_blocks, confidence) descending
        sorted_sources = sorted(
            sources,
            key=lambda s: (s.code_blocks, s.confidence),
            reverse=True
        )
        
        # Take top 5, dedupe by similarity
        merged = []
        seen_snippets = set()
        
        for source in sorted_sources[:5]:
            # Simple deduplication by first 100 chars
            snippet = source.content[:100].strip()
            if snippet not in seen_snippets:
                merged.append(f"**[{source.origin}]**\n{source.content}")
                seen_snippets.add(snippet)
        
        return "\n\n---\n\n".join(merged)
    
    def _calculate_consensus(self, sources: list[FusedSource]) -> float:
        """Calculate consensus score based on source agreement."""
        if not sources:
            return 0.0
        
        # Count sources per origin
        origins = set(s.origin for s in sources)
        
        # More origins = higher consensus
        origin_score = len(origins) / 3.0  # Max 3 origins
        
        # Average confidence
        avg_confidence = sum(s.confidence for s in sources) / len(sources)
        
        # Combined score
        return (origin_score * 0.4) + (avg_confidence * 0.6)
    
    def _find_contradictions(self, sources: list[FusedSource]) -> list[str]:
        """Identify contradictions between sources."""
        # TODO: Implement semantic contradiction detection
        # For now, return empty
        return []
