"""
Vector Store for MARO v2.0

Provides semantic search and similarity features for papers:
- Embedding generation with sentence-transformers (all-mpnet-base-v2)
- Vector similarity search with tantivy
- Paper clustering by topic
- Embedding-based citation verification

The store combines dense vectors (embeddings) with sparse search (tantivy BM25)
for hybrid retrieval.
"""

import os
import json
import logging
import tempfile
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

# Import canonical types
from data_types.models import Paper, SearchResult

logger = logging.getLogger(__name__)

# Try imports
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available")

try:
    import tantivy
    TANTIVY_AVAILABLE = True
except ImportError:
    TANTIVY_AVAILABLE = False
    logger.warning("tantivy not available")

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("sklearn not available for clustering")


# Paper and SearchResult imported from types.models


class PaperVectorStore:
    """
    Vector store for semantic paper search.

    Combines:
    - Dense retrieval with sentence-transformers embeddings
    - Sparse retrieval with tantivy BM25

    Example:
        store = PaperVectorStore()
        store.add_papers([paper1, paper2, paper3])

        # Semantic search
        results = store.search_similar("dry eye treatment efficacy", top_k=5)

        # Find similar papers
        similar = store.find_similar_papers(paper1, top_k=3)

        # Cluster papers
        clusters = store.cluster_papers(n_clusters=5)
    """

    # Default embedding model (user preference: better quality)
    DEFAULT_MODEL = "all-mpnet-base-v2"  # 768-dim, better quality

    def __init__(
        self,
        model_name: Optional[str] = None,
        index_path: Optional[str] = None,
        use_gpu: bool = False,
    ):
        """
        Initialize vector store.

        Args:
            model_name: Sentence transformer model (default: all-mpnet-base-v2)
            index_path: Path to persist tantivy index (default: temp dir)
            use_gpu: Use GPU for embeddings if available
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.use_gpu = use_gpu
        self.index_path = index_path

        # Initialize components
        self.encoder = None
        self.index = None
        self.searcher = None
        self.papers: Dict[str, Paper] = {}
        self.embeddings: Dict[str, np.ndarray] = {}

        # Lazy load encoder on first use
        self._encoder_loaded = False

    def _load_encoder(self):
        """Load the sentence transformer model."""
        if self._encoder_loaded:
            return

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers required. Install: pip install sentence-transformers"
            )

        logger.info(f"Loading embedding model: {self.model_name}")
        device = "cuda" if self.use_gpu else "cpu"
        self.encoder = SentenceTransformer(self.model_name, device=device)
        self._encoder_loaded = True
        logger.info(f"Embedding model loaded (dim={self.encoder.get_sentence_embedding_dimension()})")

    def _init_tantivy(self):
        """Initialize tantivy index for BM25 search."""
        if not TANTIVY_AVAILABLE:
            logger.warning("tantivy not available - BM25 search disabled")
            return

        # Define schema
        schema_builder = tantivy.SchemaBuilder()
        schema_builder.add_text_field("paper_id", stored=True)
        schema_builder.add_text_field("title", stored=True)
        schema_builder.add_text_field("abstract", stored=True)
        schema_builder.add_text_field("authors", stored=True)
        schema_builder.add_integer_field("year", stored=True)
        schema_builder.add_text_field("content", stored=False)  # Combined for search
        schema = schema_builder.build()

        # Create index
        if self.index_path:
            Path(self.index_path).mkdir(parents=True, exist_ok=True)
            self.index = tantivy.Index(schema, path=self.index_path)
        else:
            # Use temp directory
            temp_dir = tempfile.mkdtemp()
            self.index = tantivy.Index(schema, path=temp_dir)

    def add_papers(self, papers: List[Paper], batch_size: int = 32) -> int:
        """
        Add papers to the vector store.

        Args:
            papers: List of Paper objects to index
            batch_size: Batch size for embedding generation

        Returns:
            Number of papers added
        """
        self._load_encoder()

        if self.index is None and TANTIVY_AVAILABLE:
            self._init_tantivy()

        # Generate embeddings in batches
        texts = [p.get_text_for_embedding() for p in papers]
        logger.info(f"Generating embeddings for {len(papers)} papers...")

        embeddings = self.encoder.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(papers) > 10,
            convert_to_numpy=True,
        )

        # Store papers and embeddings
        for paper, embedding in zip(papers, embeddings):
            self.papers[paper.paper_id] = paper
            self.embeddings[paper.paper_id] = embedding

        # Index in tantivy for BM25
        if self.index:
            writer = self.index.writer()
            for paper in papers:
                doc = tantivy.Document()
                doc.add_text("paper_id", paper.paper_id)
                doc.add_text("title", paper.title)
                doc.add_text("abstract", paper.abstract or "")
                doc.add_text("authors", ", ".join(paper.authors))
                doc.add_integer("year", paper.year or 0)
                doc.add_text("content", paper.get_text_for_embedding())
                writer.add_document(doc)
            writer.commit()
            self.index.reload()

        logger.info(f"Added {len(papers)} papers to vector store")
        return len(papers)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        self._load_encoder()
        return self.encoder.encode(text, convert_to_numpy=True)

    def search_similar(
        self,
        query: str,
        top_k: int = 10,
        method: str = "hybrid",
    ) -> List[SearchResult]:
        """
        Search for papers similar to a query.

        Args:
            query: Search query text
            top_k: Number of results to return
            method: "vector" (dense), "bm25" (sparse), or "hybrid"

        Returns:
            List of SearchResult objects sorted by score
        """
        results = []

        if method in ["vector", "hybrid"]:
            # Dense retrieval
            self._load_encoder()
            query_embedding = self.encoder.encode(query, convert_to_numpy=True)

            # Calculate similarities
            scores = []
            for paper_id, paper_embedding in self.embeddings.items():
                similarity = np.dot(query_embedding, paper_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(paper_embedding)
                )
                scores.append((paper_id, similarity))

            # Sort by similarity
            scores.sort(key=lambda x: x[1], reverse=True)

            for paper_id, score in scores[:top_k]:
                results.append(SearchResult(
                    paper=self.papers[paper_id],
                    score=float(score),
                    source="vector",
                ))

        if method in ["bm25", "hybrid"] and self.index:
            # Sparse retrieval with tantivy
            try:
                searcher = self.index.searcher()
                # Use tantivy's parse_query function
                tantivy_query = self.index.parse_query(query, ["title", "abstract", "content"])
                bm25_results = searcher.search(tantivy_query, top_k).hits

                for score, doc_addr in bm25_results:
                    doc = searcher.doc(doc_addr)
                    paper_id = doc.get_first("paper_id")
                    if paper_id in self.papers:
                        # Check if already in results (hybrid dedup)
                        existing = next((r for r in results if r.paper.paper_id == paper_id), None)
                        if existing:
                            # Combine scores for hybrid
                            existing.score = (existing.score + score / 10) / 2
                            existing.source = "hybrid"
                        else:
                            results.append(SearchResult(
                                paper=self.papers[paper_id],
                                score=score / 10,  # Normalize BM25 score
                                source="bm25",
                            ))
            except Exception as e:
                logger.warning(f"BM25 search failed, using vector-only: {e}")

        # Sort final results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def find_similar_papers(
        self,
        paper: Paper,
        top_k: int = 5,
        exclude_self: bool = True,
    ) -> List[SearchResult]:
        """
        Find papers similar to a given paper.

        Args:
            paper: Paper to find similar papers for
            top_k: Number of results
            exclude_self: Exclude the query paper from results

        Returns:
            List of SearchResult objects
        """
        # Get or compute embedding for query paper
        if paper.paper_id in self.embeddings:
            query_embedding = self.embeddings[paper.paper_id]
        else:
            self._load_encoder()
            query_embedding = self.encoder.encode(
                paper.get_text_for_embedding(),
                convert_to_numpy=True,
            )

        # Calculate similarities
        scores = []
        for paper_id, paper_embedding in self.embeddings.items():
            if exclude_self and paper_id == paper.paper_id:
                continue
            similarity = np.dot(query_embedding, paper_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(paper_embedding)
            )
            scores.append((paper_id, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for paper_id, score in scores[:top_k]:
            results.append(SearchResult(
                paper=self.papers[paper_id],
                score=float(score),
                source="vector",
            ))

        return results

    def cluster_papers(
        self,
        n_clusters: int = 5,
        paper_ids: Optional[List[str]] = None,
    ) -> Dict[int, List[Tuple[str, float]]]:
        """
        Cluster papers by embedding similarity.

        Args:
            n_clusters: Number of clusters
            paper_ids: Optional subset of paper IDs to cluster

        Returns:
            Dict mapping cluster ID to list of (paper_id, distance) tuples
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn required for clustering")

        # Get embeddings for clustering
        if paper_ids:
            ids = [pid for pid in paper_ids if pid in self.embeddings]
        else:
            ids = list(self.embeddings.keys())

        if len(ids) < n_clusters:
            n_clusters = len(ids)

        embeddings_matrix = np.array([self.embeddings[pid] for pid in ids])

        # Run K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings_matrix)

        # Calculate distances to cluster centers
        distances = kmeans.transform(embeddings_matrix)

        # Group papers by cluster
        clusters: Dict[int, List[Tuple[str, float]]] = {i: [] for i in range(n_clusters)}
        for idx, (paper_id, label) in enumerate(zip(ids, labels)):
            distance = distances[idx, label]
            clusters[label].append((paper_id, float(distance)))

        # Sort each cluster by distance to center
        for cluster_id in clusters:
            clusters[cluster_id].sort(key=lambda x: x[1])

        return clusters

    def verify_claim(
        self,
        claim: str,
        top_k: int = 5,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Find papers that may support or refute a claim.

        Uses semantic similarity to find relevant passages.

        Args:
            claim: The claim to verify
            top_k: Number of most relevant papers to return
            threshold: Minimum similarity threshold

        Returns:
            List of dicts with paper info and relevance scores
        """
        results = self.search_similar(claim, top_k=top_k, method="vector")

        verifications = []
        for result in results:
            if result.score >= threshold:
                verifications.append({
                    "paper_id": result.paper.paper_id,
                    "title": result.paper.title,
                    "relevance_score": result.score,
                    "abstract_snippet": result.paper.abstract[:300] if result.paper.abstract else "",
                    "doi": result.paper.doi,
                    "authors": result.paper.authors[:3],
                    "year": result.paper.year,
                })

        return verifications

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_papers": len(self.papers),
            "total_embeddings": len(self.embeddings),
            "embedding_dim": self.encoder.get_sentence_embedding_dimension() if self._encoder_loaded else None,
            "model": self.model_name,
            "tantivy_available": self.index is not None,
        }

    def save(self, path: str):
        """
        Save embeddings and paper metadata to disk.

        Args:
            path: Directory to save to
        """
        Path(path).mkdir(parents=True, exist_ok=True)

        # Save embeddings
        embeddings_array = np.array([self.embeddings[k] for k in sorted(self.embeddings.keys())])
        np.save(os.path.join(path, "embeddings.npy"), embeddings_array)

        # Save paper metadata
        papers_data = {
            pid: {
                "paper_id": p.paper_id,
                "title": p.title,
                "abstract": p.abstract,
                "authors": p.authors,
                "year": p.year,
                "doi": p.doi,
                "source": p.source,
                "metadata": p.metadata,
            }
            for pid, p in self.papers.items()
        }
        with open(os.path.join(path, "papers.json"), "w") as f:
            json.dump(papers_data, f)

        # Save embedding order
        with open(os.path.join(path, "order.json"), "w") as f:
            json.dump(sorted(self.embeddings.keys()), f)

        logger.info(f"Saved vector store to {path}")

    def load(self, path: str):
        """
        Load embeddings and paper metadata from disk.

        Args:
            path: Directory to load from
        """
        # Load embeddings
        embeddings_array = np.load(os.path.join(path, "embeddings.npy"))

        # Load order
        with open(os.path.join(path, "order.json")) as f:
            order = json.load(f)

        # Load papers
        with open(os.path.join(path, "papers.json")) as f:
            papers_data = json.load(f)

        # Reconstruct
        self.embeddings = {pid: embeddings_array[i] for i, pid in enumerate(order)}
        self.papers = {
            pid: Paper(**data) for pid, data in papers_data.items()
        }

        logger.info(f"Loaded vector store from {path} ({len(self.papers)} papers)")


# Test function
def _test_vector_store():
    """Test vector store functionality."""
    store = PaperVectorStore()

    # Create test papers
    papers = [
        Paper(
            paper_id="test1",
            title="Deep Learning for Diabetic Retinopathy Detection",
            abstract="We present a convolutional neural network approach for detecting diabetic retinopathy from fundus images.",
            authors=["Smith, J.", "Chen, L."],
            year=2023,
        ),
        Paper(
            paper_id="test2",
            title="Dry Eye Disease Treatment Guidelines 2024",
            abstract="Comprehensive guidelines for the management of dry eye disease including artificial tears, anti-inflammatory agents, and procedural interventions.",
            authors=["Jones, A.", "Wang, B."],
            year=2024,
        ),
        Paper(
            paper_id="test3",
            title="Machine Learning in Ophthalmology: A Review",
            abstract="This review covers applications of machine learning in eye care including glaucoma detection, AMD screening, and surgical planning.",
            authors=["Brown, C.", "Garcia, D."],
            year=2023,
        ),
    ]

    print("=== Adding Papers ===")
    store.add_papers(papers)
    print(f"Stats: {store.get_stats()}")
    print()

    print("=== Semantic Search ===")
    results = store.search_similar("artificial intelligence retinal imaging", top_k=2)
    for r in results:
        print(f"- [{r.score:.3f}] {r.paper.title}")
    print()

    print("=== Find Similar Papers ===")
    similar = store.find_similar_papers(papers[0], top_k=2)
    for r in similar:
        print(f"- [{r.score:.3f}] {r.paper.title}")
    print()

    print("=== Claim Verification ===")
    verifications = store.verify_claim("Deep learning can detect diabetic retinopathy")
    for v in verifications:
        print(f"- [{v['relevance_score']:.3f}] {v['title']}")


def _cli():
    """CLI entry point for vector store operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Vector Store CLI - Semantic search and paper clustering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Add papers from JSON and save index
  python -m embeddings.vector_store add -i papers.json -s ./my_index

  # Search for similar papers
  python -m embeddings.vector_store search -q "dry eye treatment efficacy" -l ./my_index -k 10

  # Cluster papers into topics
  python -m embeddings.vector_store cluster -l ./my_index -n 5

  # Verify a claim against corpus
  python -m embeddings.vector_store verify -c "Cyclosporine improves tear production" -l ./my_index

  # Show index statistics
  python -m embeddings.vector_store stats -l ./my_index

INPUT JSON FORMAT:
  Papers JSON should be an array or object with "papers" key:
  [
    {
      "paper_id": "doi:10.1234/example",
      "title": "Paper Title",
      "abstract": "Paper abstract text...",
      "authors": ["Author One", "Author Two"],
      "year": 2024,
      "doi": "10.1234/example"
    }
  ]

EMBEDDING MODEL:
  Uses all-mpnet-base-v2 (768 dimensions) for high-quality semantic similarity.
  First run downloads ~400MB model to cache.

SEARCH METHODS:
  vector  - Pure semantic similarity (cosine)
  bm25    - Keyword matching (requires tantivy)
  hybrid  - Combines both (recommended)

USE CASES:
  - Finding papers similar to a seed paper
  - Semantic search across large corpus
  - Clustering papers by topic for thematic analysis
  - Detecting duplicate/near-duplicate papers
  - Building evidence corpus for claim verification
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add papers from JSON
    add_parser = subparsers.add_parser("add", help="Add papers from JSON file")
    add_parser.add_argument("--input", "-i", required=True, help="JSON file with papers")
    add_parser.add_argument("--save", "-s", help="Save store to directory")

    # Search
    search_parser = subparsers.add_parser("search", help="Semantic search")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument("--load", "-l", required=True, help="Load store from directory")
    search_parser.add_argument("--top", "-k", type=int, default=10, help="Number of results")
    search_parser.add_argument("--method", choices=["vector", "bm25", "hybrid"], default="vector")

    # Cluster
    cluster_parser = subparsers.add_parser("cluster", help="Cluster papers")
    cluster_parser.add_argument("--load", "-l", required=True, help="Load store from directory")
    cluster_parser.add_argument("--clusters", "-n", type=int, default=5, help="Number of clusters")

    # Verify claim
    verify_parser = subparsers.add_parser("verify", help="Verify claim against papers")
    verify_parser.add_argument("--claim", "-c", required=True, help="Claim to verify")
    verify_parser.add_argument("--load", "-l", required=True, help="Load store from directory")
    verify_parser.add_argument("--threshold", type=float, default=0.5, help="Similarity threshold")

    # Stats
    stats_parser = subparsers.add_parser("stats", help="Show store statistics")
    stats_parser.add_argument("--load", "-l", required=True, help="Load store from directory")

    # Test
    subparsers.add_parser("test", help="Run test suite")

    args = parser.parse_args()

    if args.command == "test" or args.command is None:
        _test_vector_store()
        return

    store = PaperVectorStore()

    if args.command == "add":
        with open(args.input) as f:
            data = json.load(f)
        papers = []
        for item in data if isinstance(data, list) else data.get("papers", []):
            papers.append(Paper(
                paper_id=item.get("paper_id", item.get("id", "")),
                title=item.get("title", ""),
                abstract=item.get("abstract", ""),
                authors=item.get("authors", []),
                year=item.get("year"),
                doi=item.get("doi"),
            ))
        store.add_papers(papers)
        print(f"Added {len(papers)} papers")
        if args.save:
            store.save(args.save)
            print(f"Saved to {args.save}")

    elif args.command == "search":
        store.load(args.load)
        results = store.search_similar(args.query, top_k=args.top, method=args.method)
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r.score:.3f}] {r.paper.title}")
            if r.paper.authors:
                print(f"   Authors: {', '.join(r.paper.authors[:3])}")
            print()

    elif args.command == "cluster":
        store.load(args.load)
        clusters = store.cluster_papers(n_clusters=args.clusters)
        for cluster_id, papers in clusters.items():
            print(f"\nCluster {cluster_id + 1} ({len(papers)} papers):")
            for paper_id, distance in papers[:5]:
                paper = store.papers[paper_id]
                print(f"  - {paper.title[:60]}...")

    elif args.command == "verify":
        store.load(args.load)
        results = store.verify_claim(args.claim, threshold=args.threshold)
        print(f"\nClaim: {args.claim}\n")
        for v in results:
            print(f"[{v['relevance_score']:.3f}] {v['title']}")
            print(f"  {v['abstract_snippet'][:100]}...")
            print()

    elif args.command == "stats":
        store.load(args.load)
        stats = store.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    _cli()
