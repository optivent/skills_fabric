#!/usr/bin/env python3
"""
Unified API Manager for Skills Fabric

Connects all optimal tools into a single interface:
- Anthropic (Claude Hierarchy: Opus/Sonnet/Haiku)
- Mem0 (Memory with 90% token savings)
- Voyage AI (Code embeddings)
- Jina (Reranking)
- Qdrant (Vector store)
- Perplexity (Research)
- E2B (Code execution)
- LangSmith (Observability)

Usage:
    api = UnifiedAPI()

    # Memory-aware chat
    response = await api.chat("How do I use StateGraph?", user_id="dev1")

    # Code search with reranking
    results = await api.search_code("state machine implementation", top_k=10)

    # Execute code safely
    output = await api.execute_code("print('hello')")

    # Deep research
    answer = await api.research("Latest LangGraph patterns 2025")
"""

import os
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuration for all API connections."""
    # Intelligence
    anthropic_key: str = ""

    # Memory
    mem0_key: str = ""
    zep_key: str = ""

    # Embeddings & Search
    voyage_key: str = ""
    jina_key: str = ""
    qdrant_key: str = ""
    qdrant_url: str = "https://localhost:6333"

    # Research & Scraping
    perplexity_key: str = ""
    brave_key: str = ""
    firecrawl_key: str = ""
    brightdata_key: str = ""

    # Code Execution
    e2b_key: str = ""

    # Observability
    langsmith_key: str = ""

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load configuration from environment variables."""
        return cls(
            anthropic_key=os.getenv("ANTHROPIC_API_KEY", ""),
            mem0_key=os.getenv("MEM0_API_KEY", ""),
            zep_key=os.getenv("ZEP_API_KEY", ""),
            voyage_key=os.getenv("VOYAGE_API_KEY", ""),
            jina_key=os.getenv("JINA_API_KEY", ""),
            qdrant_key=os.getenv("QDRANT_API_KEY", ""),
            qdrant_url=os.getenv("QDRANT_URL", "https://localhost:6333"),
            perplexity_key=os.getenv("PERPLEXITY_API_KEY", ""),
            brave_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
            firecrawl_key=os.getenv("FIRECRAWL_API_KEY", ""),
            brightdata_key=os.getenv("BRIGHTDATA_API_KEY", ""),
            e2b_key=os.getenv("E2B_API_KEY", ""),
            langsmith_key=os.getenv("LANGCHAIN_API_KEY", ""),
        )


@dataclass
class SearchResult:
    """A search result with metadata."""
    content: str
    score: float
    source: str
    file_path: Optional[str] = None
    line: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryEntry:
    """A memory entry."""
    id: str
    content: str
    user_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    stdout: str
    stderr: str
    return_value: Any = None
    execution_time_ms: int = 0


class UnifiedAPI:
    """
    Unified interface to all skill development tools.

    Provides:
    - Memory-aware conversations (Mem0)
    - Tiered intelligence (Opus/Sonnet/Haiku)
    - Code search with embeddings (Voyage + Qdrant + Jina)
    - Safe code execution (E2B)
    - Deep research (Perplexity)
    - Observability (LangSmith)
    """

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig.from_env()
        self._initialized = False

        # Client instances (lazy loaded)
        self._anthropic = None
        self._mem0 = None
        self._voyage = None
        self._qdrant = None
        self._e2b = None

        # Status tracking
        self.status: Dict[str, bool] = {}

    async def initialize(self) -> Dict[str, bool]:
        """
        Initialize all configured services.

        Returns dict of service -> connected status.
        """
        logger.info("Initializing Unified API...")

        # Check each service
        self.status = {
            "anthropic": await self._init_anthropic(),
            "mem0": await self._init_mem0(),
            "voyage": await self._init_voyage(),
            "qdrant": await self._init_qdrant(),
            "jina": bool(self.config.jina_key),
            "perplexity": bool(self.config.perplexity_key),
            "e2b": await self._init_e2b(),
            "langsmith": bool(self.config.langsmith_key),
        }

        self._initialized = True

        # Log status
        connected = sum(1 for v in self.status.values() if v)
        logger.info(f"Initialized: {connected}/{len(self.status)} services connected")

        return self.status

    async def _init_anthropic(self) -> bool:
        """Initialize Anthropic client."""
        if not self.config.anthropic_key:
            logger.warning("ANTHROPIC_API_KEY not set")
            return False

        try:
            import anthropic
            self._anthropic = anthropic.Anthropic(api_key=self.config.anthropic_key)
            return True
        except ImportError:
            logger.warning("anthropic package not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to init Anthropic: {e}")
            return False

    async def _init_mem0(self) -> bool:
        """Initialize Mem0 client."""
        if not self.config.mem0_key:
            logger.warning("MEM0_API_KEY not set")
            return False

        try:
            from mem0 import Memory
            self._mem0 = Memory()
            return True
        except ImportError:
            logger.warning("mem0ai package not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to init Mem0: {e}")
            return False

    async def _init_voyage(self) -> bool:
        """Initialize Voyage AI client."""
        if not self.config.voyage_key:
            logger.warning("VOYAGE_API_KEY not set")
            return False

        try:
            import voyageai
            self._voyage = voyageai.Client(api_key=self.config.voyage_key)
            return True
        except ImportError:
            logger.warning("voyageai package not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to init Voyage: {e}")
            return False

    async def _init_qdrant(self) -> bool:
        """Initialize Qdrant client."""
        try:
            from qdrant_client import QdrantClient

            if self.config.qdrant_key:
                self._qdrant = QdrantClient(
                    url=self.config.qdrant_url,
                    api_key=self.config.qdrant_key
                )
            else:
                # Local instance
                self._qdrant = QdrantClient(host="localhost", port=6333)

            return True
        except ImportError:
            logger.warning("qdrant-client package not installed")
            return False
        except Exception as e:
            logger.warning(f"Failed to init Qdrant: {e}")
            return False

    async def _init_e2b(self) -> bool:
        """Initialize E2B client."""
        if not self.config.e2b_key:
            logger.warning("E2B_API_KEY not set")
            return False

        try:
            from e2b_code_interpreter import Sandbox
            # Just verify import works - sandbox created per-execution
            return True
        except ImportError:
            logger.warning("e2b-code-interpreter package not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to init E2B: {e}")
            return False

    # =========================================================================
    # INTELLIGENCE LAYER (Claude Hierarchy)
    # =========================================================================

    async def chat(
        self,
        message: str,
        tier: str = "auto",
        user_id: Optional[str] = None,
        system: Optional[str] = None,
        use_memory: bool = True,
    ) -> str:
        """
        Chat with Claude using tiered intelligence.

        Args:
            message: The user message
            tier: "opus", "sonnet", "haiku", or "auto" (selects based on task)
            user_id: User ID for memory context
            system: System prompt
            use_memory: Whether to use Mem0 for context

        Returns:
            Claude's response
        """
        if not self.status.get("anthropic"):
            return "[Anthropic not initialized - check API key]"

        # Select model based on tier
        model_map = {
            "opus": "claude-opus-4-5-20251101",
            "sonnet": "claude-sonnet-4-5-20251101",
            "haiku": "claude-haiku-4-5-20251101",
        }

        if tier == "auto":
            tier = self._select_tier(message)

        model = model_map.get(tier, model_map["haiku"])

        # Get memory context if enabled
        context = ""
        if use_memory and user_id and self.status.get("mem0"):
            memories = await self.recall_memories(message, user_id)
            if memories:
                context = "\n\n<relevant_memories>\n"
                for mem in memories[:5]:
                    context += f"- {mem.content}\n"
                context += "</relevant_memories>\n"

        # Build messages
        messages = [{"role": "user", "content": context + message}]

        try:
            response = self._anthropic.messages.create(
                model=model,
                max_tokens=4096,
                system=system or "You are a helpful assistant for code understanding.",
                messages=messages,
            )

            answer = response.content[0].text

            # Store interaction in memory
            if use_memory and user_id and self.status.get("mem0"):
                await self.add_memory(
                    content=f"Q: {message[:100]}\nA: {answer[:200]}",
                    user_id=user_id
                )

            return answer

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"[Error: {str(e)}]"

    def _select_tier(self, message: str) -> str:
        """Auto-select tier based on task complexity."""
        message_lower = message.lower()

        # Opus for architecture/design
        opus_keywords = ["architect", "design", "framework", "system", "trade-off", "complex"]
        if any(kw in message_lower for kw in opus_keywords):
            return "opus"

        # Sonnet for coordination/search
        sonnet_keywords = ["verify", "review", "search", "find", "analyze", "test", "check"]
        if any(kw in message_lower for kw in sonnet_keywords):
            return "sonnet"

        # Haiku for execution (default)
        return "haiku"

    # =========================================================================
    # MEMORY LAYER (Mem0)
    # =========================================================================

    async def add_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add a memory entry.

        Args:
            content: The content to remember
            user_id: User identifier
            metadata: Optional metadata

        Returns:
            Memory ID or None if failed
        """
        if not self.status.get("mem0"):
            return None

        try:
            result = self._mem0.add(
                content,
                user_id=user_id,
                metadata=metadata or {}
            )
            return result.get("id")
        except Exception as e:
            logger.error(f"Memory add error: {e}")
            return None

    async def recall_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """
        Recall relevant memories.

        Args:
            query: Search query
            user_id: User identifier
            limit: Max memories to return

        Returns:
            List of relevant memories
        """
        if not self.status.get("mem0"):
            return []

        try:
            results = self._mem0.search(query, user_id=user_id, limit=limit)

            return [
                MemoryEntry(
                    id=r.get("id", ""),
                    content=r.get("memory", ""),
                    user_id=user_id,
                    timestamp=datetime.now(),
                    metadata=r.get("metadata", {})
                )
                for r in results
            ]
        except Exception as e:
            logger.error(f"Memory recall error: {e}")
            return []

    # =========================================================================
    # SEARCH & RETRIEVAL LAYER (Voyage + Qdrant + Jina)
    # =========================================================================

    async def embed_code(
        self,
        texts: List[str],
        input_type: str = "document"
    ) -> List[List[float]]:
        """
        Generate code embeddings using Voyage AI.

        Args:
            texts: List of code/text to embed
            input_type: "document" or "query"

        Returns:
            List of embedding vectors
        """
        if not self.status.get("voyage"):
            logger.warning("Voyage not initialized")
            return []

        try:
            result = self._voyage.embed(
                texts,
                model="voyage-code-3",
                input_type=input_type
            )
            return result.embeddings
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    async def index_code(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        vector_size: int = 2048
    ) -> bool:
        """
        Index code documents in Qdrant.

        Args:
            collection_name: Name of the collection
            documents: List of dicts with 'content', 'file_path', 'line', etc.
            vector_size: Embedding dimension

        Returns:
            Success status
        """
        if not self.status.get("qdrant") or not self.status.get("voyage"):
            return False

        try:
            from qdrant_client.models import VectorParams, Distance, PointStruct

            # Create collection if needed
            collections = self._qdrant.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if not exists:
                self._qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )

            # Embed documents
            contents = [d["content"] for d in documents]
            embeddings = await self.embed_code(contents, input_type="document")

            if not embeddings:
                return False

            # Upload points
            points = [
                PointStruct(
                    id=i,
                    vector=embeddings[i],
                    payload={
                        "content": documents[i]["content"],
                        "file_path": documents[i].get("file_path", ""),
                        "line": documents[i].get("line", 0),
                        **documents[i].get("metadata", {})
                    }
                )
                for i in range(len(documents))
            ]

            self._qdrant.upsert(collection_name=collection_name, points=points)
            return True

        except Exception as e:
            logger.error(f"Index error: {e}")
            return False

    async def search_code(
        self,
        query: str,
        collection_name: str,
        top_k: int = 10,
        rerank: bool = True
    ) -> List[SearchResult]:
        """
        Search code with embeddings and reranking.

        Args:
            query: Search query
            collection_name: Collection to search
            top_k: Number of results
            rerank: Whether to use Jina reranking

        Returns:
            List of search results
        """
        if not self.status.get("qdrant") or not self.status.get("voyage"):
            return []

        try:
            # Embed query
            query_embedding = await self.embed_code([query], input_type="query")
            if not query_embedding:
                return []

            # Search Qdrant
            results = self._qdrant.search(
                collection_name=collection_name,
                query_vector=query_embedding[0],
                limit=top_k * 2 if rerank else top_k  # Get more for reranking
            )

            search_results = [
                SearchResult(
                    content=r.payload.get("content", ""),
                    score=r.score,
                    source="qdrant",
                    file_path=r.payload.get("file_path"),
                    line=r.payload.get("line"),
                    metadata=r.payload
                )
                for r in results
            ]

            # Rerank with Jina
            if rerank and self.status.get("jina"):
                search_results = await self._rerank_jina(query, search_results, top_k)

            return search_results[:top_k]

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def _rerank_jina(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """Rerank results using Jina."""
        if not self.config.jina_key:
            return results

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.jina.ai/v1/rerank",
                    headers={"Authorization": f"Bearer {self.config.jina_key}"},
                    json={
                        "model": "jina-reranker-v2-base-multilingual",
                        "query": query,
                        "documents": [r.content for r in results],
                        "top_n": top_k
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    reranked = []
                    for item in data.get("results", []):
                        idx = item.get("index", 0)
                        if idx < len(results):
                            result = results[idx]
                            result.score = item.get("relevance_score", result.score)
                            result.source = "jina_reranked"
                            reranked.append(result)
                    return reranked

        except Exception as e:
            logger.error(f"Rerank error: {e}")

        return results

    # =========================================================================
    # CODE EXECUTION LAYER (E2B)
    # =========================================================================

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout_ms: int = 30000
    ) -> ExecutionResult:
        """
        Execute code safely in E2B sandbox.

        Args:
            code: Code to execute
            language: Programming language
            timeout_ms: Timeout in milliseconds

        Returns:
            Execution result
        """
        if not self.status.get("e2b"):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="E2B not initialized - check API key"
            )

        try:
            from e2b_code_interpreter import Sandbox
            import time

            start_time = time.time()

            with Sandbox() as sandbox:
                execution = sandbox.run_code(code)

                elapsed_ms = int((time.time() - start_time) * 1000)

                return ExecutionResult(
                    success=not execution.error,
                    stdout="\n".join(str(r) for r in execution.results),
                    stderr=execution.error or "",
                    return_value=execution.results[-1] if execution.results else None,
                    execution_time_ms=elapsed_ms
                )

        except Exception as e:
            logger.error(f"Execution error: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e)
            )

    # =========================================================================
    # RESEARCH LAYER (Perplexity)
    # =========================================================================

    async def research(
        self,
        query: str,
        mode: str = "pro"
    ) -> str:
        """
        Perform deep research using Perplexity.

        Args:
            query: Research query
            mode: "fast" (sonar), "pro" (sonar-pro), or "deep" (deep-research)

        Returns:
            Research answer with citations
        """
        if not self.config.perplexity_key:
            return "[Perplexity not configured]"

        try:
            import httpx

            model_map = {
                "fast": "sonar",
                "pro": "sonar-pro",
                "deep": "sonar-deep-research"
            }

            model = model_map.get(mode, "sonar-pro")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.perplexity_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": query}]
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"[Research error: {response.status_code}]"

        except Exception as e:
            logger.error(f"Research error: {e}")
            return f"[Research error: {str(e)}]"

    # =========================================================================
    # STATUS & DIAGNOSTICS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get full status of all services."""
        return {
            "initialized": self._initialized,
            "services": self.status,
            "connected": sum(1 for v in self.status.values() if v),
            "total": len(self.status),
            "config_keys_set": {
                "anthropic": bool(self.config.anthropic_key),
                "mem0": bool(self.config.mem0_key),
                "voyage": bool(self.config.voyage_key),
                "qdrant": bool(self.config.qdrant_key),
                "jina": bool(self.config.jina_key),
                "perplexity": bool(self.config.perplexity_key),
                "e2b": bool(self.config.e2b_key),
                "langsmith": bool(self.config.langsmith_key),
            }
        }

    def print_status(self):
        """Print human-readable status."""
        status = self.get_status()

        print("\n" + "=" * 60)
        print("UNIFIED API STATUS")
        print("=" * 60)

        print(f"\nInitialized: {status['initialized']}")
        print(f"Services Connected: {status['connected']}/{status['total']}")

        print("\nService Status:")
        for service, connected in status['services'].items():
            icon = "✓" if connected else "✗"
            print(f"  {icon} {service}")

        print("\nAPI Keys Configured:")
        for key, configured in status['config_keys_set'].items():
            icon = "✓" if configured else "✗"
            print(f"  {icon} {key.upper()}_API_KEY")


async def demo():
    """Demonstrate the Unified API."""
    print("=" * 60)
    print("Unified API Manager Demo")
    print("=" * 60)

    api = UnifiedAPI()
    status = await api.initialize()

    api.print_status()

    # Demo chat if available
    if status.get("anthropic"):
        print("\n" + "-" * 60)
        print("Demo: Tiered Chat")
        print("-" * 60)

        response = await api.chat(
            "What is a good pattern for state machines?",
            tier="haiku"
        )
        print(f"Haiku says: {response[:200]}...")


if __name__ == "__main__":
    asyncio.run(demo())
