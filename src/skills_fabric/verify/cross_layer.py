"""Cross-Layer Verification - verify claims across all iceberg layers."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class LayerVerification:
    layer: str
    verified: bool
    evidence: str
    confidence: float

@dataclass
class CrossLayerResult:
    claim: str
    verifications: list[LayerVerification]
    overall_verified: bool
    overall_confidence: float

class CrossLayerVerifier:
    """Verify claims by checking all 5 iceberg layers."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path
    
    def verify_claim(self, claim: str, library: str = None) -> CrossLayerResult:
        """Check claim against all layers."""
        verifications = []
        
        # Layer 1: Surface (Context7/Exa)
        v1 = self._verify_surface(claim, library)
        verifications.append(v1)
        
        # Layer 2: Structure (AST/LSP)
        v2 = self._verify_structure(claim)
        verifications.append(v2)
        
        # Layer 3: Behavior (Bubblewrap trace)
        v3 = self._verify_behavior(claim)
        verifications.append(v3)
        
        # Layer 4: Navigation (KuzuDB)
        v4 = self._verify_navigation(claim)
        verifications.append(v4)
        
        # Layer 5: Foundation (Git)
        v5 = self._verify_foundation(claim)
        verifications.append(v5)
        
        # Calculate overall
        verified_count = sum(1 for v in verifications if v.verified)
        overall_verified = verified_count >= 3
        overall_confidence = sum(v.confidence for v in verifications) / len(verifications)
        
        return CrossLayerResult(
            claim=claim,
            verifications=verifications,
            overall_verified=overall_verified,
            overall_confidence=overall_confidence
        )
    
    def _verify_surface(self, claim: str, library: str) -> LayerVerification:
        try:
            from ..ingest.fusion import SourceFusion
            fusion = SourceFusion(self.repo_path)
            result = fusion.get_examples(claim, library or 'python')
            verified = result.consensus_score > 0.5
            return LayerVerification('surface', verified, 
                f'Consensus: {result.consensus_score:.2f}', result.consensus_score)
        except Exception as e:
            return LayerVerification('surface', False, str(e), 0.0)
    
    def _verify_structure(self, claim: str) -> LayerVerification:
        try:
            if self.repo_path:
                from ..analyze.symbol_graph import SymbolGraphBuilder
                builder = SymbolGraphBuilder()
                graph = builder.build(self.repo_path)
                # Check if claim mentions any known symbol
                for symbol in graph.nodes:
                    if claim.lower() in symbol.lower():
                        return LayerVerification('structure', True, 
                            f'Found symbol: {symbol}', 0.9)
            return LayerVerification('structure', False, 'No matching symbol', 0.0)
        except Exception as e:
            return LayerVerification('structure', False, str(e), 0.0)
    
    def _verify_behavior(self, claim: str) -> LayerVerification:
        # Would execute related code and trace
        return LayerVerification('behavior', False, 'Not implemented', 0.0)
    
    def _verify_navigation(self, claim: str) -> LayerVerification:
        try:
            from ..core.database import db
            res = db.execute(f"MATCH (c:Concept) WHERE c.name CONTAINS '{claim[:20]}' RETURN count(c)")
            count = res.get_next()[0] if res.has_next() else 0
            verified = count > 0
            return LayerVerification('navigation', verified, f'{count} concepts found', 0.8 if verified else 0.0)
        except Exception as e:
            return LayerVerification('navigation', False, str(e), 0.0)
    
    def _verify_foundation(self, claim: str) -> LayerVerification:
        if self.repo_path and self.repo_path.exists():
            # Search for claim in actual files
            import subprocess
            result = subprocess.run(['grep', '-r', '-l', claim[:30], str(self.repo_path)],
                capture_output=True, text=True, timeout=5)
            files = result.stdout.strip().split('\n') if result.stdout else []
            verified = len(files) > 0 and files[0] != ''
            return LayerVerification('foundation', verified, 
                f'{len(files)} files match' if verified else 'No files', 1.0 if verified else 0.0)
        return LayerVerification('foundation', False, 'No repo path', 0.0)
