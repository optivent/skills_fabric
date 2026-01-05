"""GLiNER Named Entity Recognition for concept extraction.

Uses GLiNER to extract technical entities from documentation
and source code for improved linking accuracy.
"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class Entity:
    """An extracted named entity."""
    text: str
    label: str
    start: int
    end: int
    score: float


class NERExtractor:
    """Extract named entities using GLiNER."""
    
    def __init__(self):
        self._model = None
    
    def _load_model(self):
        """Lazy load the GLiNER model."""
        if self._model is None:
            try:
                from gliner import GLiNER
                self._model = GLiNER.from_pretrained('urchade/gliner_base')
            except ImportError:
                print('[NER] GLiNER not installed')
                return False
        return True
    
    def extract(self, text: str, labels: list[str] = None) -> list[Entity]:
        """Extract named entities from text.
        
        Args:
            text: Text to analyze
            labels: Entity types to extract (default: code entities)
        
        Returns:
            List of extracted entities
        """
        if not self._load_model():
            return []
        
        if labels is None:
            labels = ['function', 'class', 'module', 'library', 'variable', 'parameter']
        
        try:
            predictions = self._model.predict_entities(text, labels)
            
            entities = []
            for pred in predictions:
                entities.append(Entity(
                    text=pred['text'],
                    label=pred['label'],
                    start=pred['start'],
                    end=pred['end'],
                    score=pred.get('score', 1.0)
                ))
            
            return entities
        except Exception as e:
            print(f'[NER] Error: {e}')
            return []
    
    def extract_code_entities(self, code: str) -> list[str]:
        """Extract function and class names from code."""
        entities = self.extract(code, labels=['function', 'class'])
        return [e.text for e in entities if e.score > 0.5]
    
    def extract_doc_concepts(self, doc: str) -> list[str]:
        """Extract concepts from documentation."""
        entities = self.extract(doc, labels=['module', 'library', 'function', 'class'])
        return [e.text for e in entities if e.score > 0.5]
