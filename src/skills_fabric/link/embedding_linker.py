"""Embedding-based PROVEN linking using Voyage AI."""
import os
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmbeddingLink:
    concept_name: str
    symbol_name: str
    similarity: float
    file_path: str

class EmbeddingLinker:
    """Use embeddings for semantic linking between concepts and symbols."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('VOYAGE_API_KEY', '')
        self.model = 'voyage-code-3'
        self.url = 'https://api.voyageai.com/v1/embeddings'
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            return []
        try:
            resp = requests.post(self.url,
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={'model': self.model, 'input': texts}, timeout=30)
            if resp.status_code == 200:
                return [d['embedding'] for d in resp.json()['data']]
        except Exception as e:
            print(f'[Embed] Error: {e}')
        return []
    
    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x*y for x,y in zip(a,b))
        norm_a = sum(x*x for x in a) ** 0.5
        norm_b = sum(x*x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
    
    def find_links(self, concepts: list[dict], symbols: list[dict], threshold: float = 0.75) -> list[EmbeddingLink]:
        """Find semantic links between concepts and symbols using embeddings."""
        if not concepts or not symbols:
            return []
        
        concept_texts = [c.get('content', c.get('name', ''))[:500] for c in concepts]
        symbol_texts = [s.get('docstring', s.get('name', '')) for s in symbols]
        
        concept_embs = self.embed(concept_texts)
        symbol_embs = self.embed(symbol_texts)
        
        if not concept_embs or not symbol_embs:
            return []
        
        links = []
        for i, c in enumerate(concepts):
            for j, s in enumerate(symbols):
                sim = self.cosine_similarity(concept_embs[i], symbol_embs[j])
                if sim >= threshold:
                    links.append(EmbeddingLink(
                        concept_name=c.get('name', ''),
                        symbol_name=s.get('name', ''),
                        similarity=sim,
                        file_path=s.get('file_path', '')
                    ))
        
        links.sort(key=lambda x: x.similarity, reverse=True)
        return links
