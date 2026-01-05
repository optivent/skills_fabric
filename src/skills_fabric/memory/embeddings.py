"""Embedding Search - Semantic similarity for memory retrieval.

Provides semantic search capabilities using embeddings:
- Convert text to vector embeddings
- Find semantically similar memories
- Cluster related skills
- Support multiple embedding providers

Providers:
- Voyage AI (recommended for code)
- OpenAI text-embedding
- Local sentence-transformers (fallback)
"""
from dataclasses import dataclass
from typing import Optional, Any
from abc import ABC, abstractmethod
import hashlib


@dataclass
class EmbeddingResult:
    """Result of embedding a text."""
    text: str
    embedding: list[float]
    model: str
    dimensions: int

    @property
    def hash(self) -> str:
        """Hash of the text for caching."""
        return hashlib.sha256(self.text.encode()).hexdigest()[:16]


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> Optional[EmbeddingResult]:
        """Embed a single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed multiple texts."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Embedding dimensions."""
        pass


class VoyageAIProvider(EmbeddingProvider):
    """Voyage AI embeddings - optimized for code.

    Recommended for Skills Fabric as it's trained on code.
    """

    def __init__(self, api_key: str = None):
        import os
        self.api_key = api_key or os.environ.get("VOYAGE_API_KEY")
        self._dimensions = 1024

    def embed(self, text: str) -> Optional[EmbeddingResult]:
        """Embed text using Voyage AI."""
        if not self.api_key:
            return None

        try:
            import httpx

            response = httpx.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "input": text[:8000],  # Max input length
                    "model": "voyage-code-2"
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                embedding = data["data"][0]["embedding"]
                return EmbeddingResult(
                    text=text,
                    embedding=embedding,
                    model="voyage-code-2",
                    dimensions=len(embedding)
                )
        except Exception:
            pass

        return None

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed multiple texts."""
        results = []
        for text in texts:
            result = self.embed(text)
            if result:
                results.append(result)
        return results

    @property
    def dimensions(self) -> int:
        return self._dimensions


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embeddings using sentence-transformers.

    Fallback when API keys are not available.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimensions = 384

    def _get_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                return None
        return self._model

    def embed(self, text: str) -> Optional[EmbeddingResult]:
        """Embed text using local model."""
        model = self._get_model()
        if model is None:
            return None

        try:
            embedding = model.encode(text).tolist()
            return EmbeddingResult(
                text=text,
                embedding=embedding,
                model=self.model_name,
                dimensions=len(embedding)
            )
        except Exception:
            return None

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed multiple texts."""
        model = self._get_model()
        if model is None:
            return []

        try:
            embeddings = model.encode(texts)
            return [
                EmbeddingResult(
                    text=text,
                    embedding=emb.tolist(),
                    model=self.model_name,
                    dimensions=len(emb)
                )
                for text, emb in zip(texts, embeddings)
            ]
        except Exception:
            return []

    @property
    def dimensions(self) -> int:
        return self._dimensions


class EmbeddingCache:
    """Cache for embeddings to avoid recomputation."""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: dict[str, EmbeddingResult] = {}

    def get(self, text: str) -> Optional[EmbeddingResult]:
        """Get cached embedding."""
        key = hashlib.sha256(text.encode()).hexdigest()[:16]
        return self._cache.get(key)

    def set(self, result: EmbeddingResult) -> None:
        """Cache an embedding result."""
        if len(self._cache) >= self.max_size:
            # Remove oldest entries
            keys = list(self._cache.keys())[:self.max_size // 2]
            for k in keys:
                del self._cache[k]

        self._cache[result.hash] = result


class SemanticSearch:
    """Semantic search using embeddings.

    Usage:
        search = SemanticSearch()

        # Index memories
        search.index("skill-1", "How to use state management in LangGraph")
        search.index("skill-2", "Creating a chatbot with memory")

        # Search
        results = search.search("state handling", limit=5)
    """

    def __init__(self, provider: EmbeddingProvider = None):
        self.provider = provider or self._get_default_provider()
        self.cache = EmbeddingCache()
        self._index: dict[str, EmbeddingResult] = {}

    def _get_default_provider(self) -> EmbeddingProvider:
        """Get default embedding provider."""
        import os

        if os.environ.get("VOYAGE_API_KEY"):
            return VoyageAIProvider()

        return LocalEmbeddingProvider()

    def index(self, id: str, text: str) -> bool:
        """Index a text for search."""
        # Check cache
        cached = self.cache.get(text)
        if cached:
            self._index[id] = cached
            return True

        # Compute embedding
        result = self.provider.embed(text)
        if result:
            self.cache.set(result)
            self._index[id] = result
            return True

        return False

    def search(
        self,
        query: str,
        limit: int = 10
    ) -> list[tuple[str, float]]:
        """Search for similar items.

        Returns list of (id, similarity) tuples.
        """
        # Get query embedding
        query_result = self.cache.get(query) or self.provider.embed(query)
        if not query_result:
            return []

        # Calculate similarities
        similarities = []
        for id, result in self._index.items():
            sim = self._cosine_similarity(query_result.embedding, result.embedding)
            similarities.append((id, sim))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def find_similar(
        self,
        id: str,
        limit: int = 10
    ) -> list[tuple[str, float]]:
        """Find items similar to a given indexed item."""
        if id not in self._index:
            return []

        source = self._index[id]
        similarities = []

        for other_id, result in self._index.items():
            if other_id != id:
                sim = self._cosine_similarity(source.embedding, result.embedding)
                similarities.append((other_id, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def clear(self) -> None:
        """Clear the index."""
        self._index.clear()
