"""Code Embeddings - Semantic code understanding.

Uses code-specific embedding models for:
- Semantic similarity between code snippets
- Cross-language code search
- Intent classification
- Function clustering

Models:
- GraphCodeBERT: Graph-based code understanding
- CodeBERT: General code embeddings
- Local fallback: sentence-transformers

Based on research:
- "GraphCodeBERT: Pre-training Code Representations with Data Flow"
- Microsoft's CodeBERT family
"""
from dataclasses import dataclass
from typing import Optional, Any
from abc import ABC, abstractmethod
import hashlib


@dataclass
class CodeEmbedding:
    """Embedding for a code snippet."""
    code: str
    language: str
    embedding: list[float]
    model: str
    metadata: dict = None

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.code.encode()).hexdigest()[:16]


class CodeEmbeddingProvider(ABC):
    """Base class for code embedding providers."""

    @abstractmethod
    def embed_code(self, code: str, language: str = "python") -> Optional[CodeEmbedding]:
        """Embed a code snippet."""
        pass

    @abstractmethod
    def embed_batch(self, codes: list[tuple[str, str]]) -> list[CodeEmbedding]:
        """Embed multiple code snippets. Each tuple is (code, language)."""
        pass

    @abstractmethod
    def similarity(self, emb1: CodeEmbedding, emb2: CodeEmbedding) -> float:
        """Calculate similarity between two embeddings."""
        pass


class GraphCodeBERTProvider(CodeEmbeddingProvider):
    """GraphCodeBERT embeddings for code understanding.

    Best for:
    - Understanding code semantics
    - Data flow analysis
    - Cross-language similarity
    """

    def __init__(self, model_name: str = "microsoft/graphcodebert-base"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from transformers import AutoModel, AutoTokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModel.from_pretrained(self.model_name)
            except ImportError:
                return False
        return True

    def embed_code(self, code: str, language: str = "python") -> Optional[CodeEmbedding]:
        """Embed code using GraphCodeBERT."""
        if not self._load_model():
            return None

        try:
            import torch

            # Tokenize with language prefix
            inputs = self._tokenizer(
                code,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            with torch.no_grad():
                outputs = self._model(**inputs)
                # Use [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()

            return CodeEmbedding(
                code=code,
                language=language,
                embedding=embedding,
                model=self.model_name,
                metadata={"tokens": len(inputs["input_ids"][0])}
            )
        except Exception:
            return None

    def embed_batch(self, codes: list[tuple[str, str]]) -> list[CodeEmbedding]:
        """Embed multiple code snippets."""
        results = []
        for code, lang in codes:
            emb = self.embed_code(code, lang)
            if emb:
                results.append(emb)
        return results

    def similarity(self, emb1: CodeEmbedding, emb2: CodeEmbedding) -> float:
        """Cosine similarity between embeddings."""
        return self._cosine_similarity(emb1.embedding, emb2.embedding)

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class LocalCodeEmbeddingProvider(CodeEmbeddingProvider):
    """Local code embeddings using sentence-transformers.

    Fallback when transformers models are not available.
    """

    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                return False
        return True

    def embed_code(self, code: str, language: str = "python") -> Optional[CodeEmbedding]:
        if not self._load_model():
            return None

        try:
            # Add language context
            text = f"# {language}\n{code}"
            embedding = self._model.encode(text).tolist()

            return CodeEmbedding(
                code=code,
                language=language,
                embedding=embedding,
                model=self.model_name
            )
        except Exception:
            return None

    def embed_batch(self, codes: list[tuple[str, str]]) -> list[CodeEmbedding]:
        if not self._load_model():
            return []

        try:
            texts = [f"# {lang}\n{code}" for code, lang in codes]
            embeddings = self._model.encode(texts)

            return [
                CodeEmbedding(
                    code=code,
                    language=lang,
                    embedding=emb.tolist(),
                    model=self.model_name
                )
                for (code, lang), emb in zip(codes, embeddings)
            ]
        except Exception:
            return []

    def similarity(self, emb1: CodeEmbedding, emb2: CodeEmbedding) -> float:
        return self._cosine_similarity(emb1.embedding, emb2.embedding)

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class CodeSimilaritySearch:
    """Search for similar code snippets.

    Usage:
        search = CodeSimilaritySearch()

        # Index code
        search.index("func1", "def add(a, b): return a + b", "python")
        search.index("func2", "def multiply(x, y): return x * y", "python")

        # Find similar
        results = search.find_similar("def sum(x, y): return x + y", limit=5)
    """

    def __init__(self, provider: CodeEmbeddingProvider = None):
        self.provider = provider or self._get_default_provider()
        self._index: dict[str, CodeEmbedding] = {}

    def _get_default_provider(self) -> CodeEmbeddingProvider:
        """Get default provider (try GraphCodeBERT, fallback to local)."""
        try:
            provider = GraphCodeBERTProvider()
            if provider._load_model():
                return provider
        except Exception:
            pass

        return LocalCodeEmbeddingProvider()

    def index(self, id: str, code: str, language: str = "python") -> bool:
        """Index a code snippet."""
        embedding = self.provider.embed_code(code, language)
        if embedding:
            self._index[id] = embedding
            return True
        return False

    def find_similar(
        self,
        code: str,
        language: str = "python",
        limit: int = 10
    ) -> list[tuple[str, float]]:
        """Find code similar to the query.

        Returns list of (id, similarity) tuples.
        """
        query_emb = self.provider.embed_code(code, language)
        if not query_emb:
            return []

        similarities = []
        for id, emb in self._index.items():
            sim = self.provider.similarity(query_emb, emb)
            similarities.append((id, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def cluster_similar(
        self,
        threshold: float = 0.8
    ) -> list[list[str]]:
        """Cluster similar code snippets.

        Returns list of clusters (each cluster is list of ids).
        """
        if len(self._index) < 2:
            return [list(self._index.keys())]

        # Simple single-linkage clustering
        ids = list(self._index.keys())
        embeddings = [self._index[id] for id in ids]

        clusters = [[i] for i in range(len(ids))]
        cluster_map = {i: i for i in range(len(ids))}

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sim = self.provider.similarity(embeddings[i], embeddings[j])
                if sim >= threshold:
                    # Merge clusters
                    ci, cj = cluster_map[i], cluster_map[j]
                    if ci != cj:
                        clusters[ci].extend(clusters[cj])
                        for k in clusters[cj]:
                            cluster_map[k] = ci
                        clusters[cj] = []

        # Convert indices to ids and filter empty
        return [
            [ids[i] for i in cluster]
            for cluster in clusters
            if cluster
        ]
