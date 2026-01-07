"""Context7 API client for fetching documentation.

This module provides a comprehensive Context7 MCP API client with:
- Batch fetching and caching of library documentation
- Memory-efficient iteration for large doc sets
- Proper error handling with retry logic
- Progress tracking for large operations

SPEC REQUIREMENT: Always call get-library-docs after successful resolve-library-id.
Use resolve_and_fetch_docs() or resolve_and_fetch_docs_simple() for automatic chaining.

RECOMMENDED PATTERN:
    # Single query - returns (resolution, docs)
    client = Context7Client()
    resolution, docs = client.resolve_and_fetch_docs("langgraph", "getting started")
    if resolution.is_success and docs:
        print(docs)

    # Simple version - returns just docs
    docs = client.resolve_and_fetch_docs_simple("langgraph", "StateGraph")

    # Multiple queries - resolves once, fetches all
    results = client.get_docs_for_multiple_queries(
        "langgraph",
        ["getting started", "StateGraph", "nodes and edges"]
    )

BMAD C.O.R.E. Principles:
- Collaboration: Fetches ALL available documentation (no arbitrary [:3] limits)
- Optimized: Batch processing with efficient caching
- Reflection: Honest error reporting, graceful fallbacks
- Engine: Systematic API interaction with retries
"""
import json
import hashlib
import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Iterator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from skills_fabric.observability.logging import get_logger

logger = get_logger("ingest.context7")


class FetchStatus(Enum):
    """Status of a fetch operation."""
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    LIBRARY_NOT_FOUND = "library_not_found"  # Library couldn't be resolved in Context7


class LibraryResolutionStatus(Enum):
    """Status of a library resolution operation."""
    RESOLVED = "resolved"  # Successfully resolved to a library ID
    NOT_FOUND = "not_found"  # Library not found in Context7
    EMPTY_RESULTS = "empty_results"  # API returned empty/no results
    API_ERROR = "api_error"  # API returned an error
    INVALID_RESPONSE = "invalid_response"  # Response couldn't be parsed
    CACHED = "cached"  # Retrieved from cache


@dataclass
class Context7Doc:
    """A documentation snippet from Context7."""
    title: str
    content: str
    source_url: str
    code_blocks: int
    library_id: Optional[str] = None
    query: Optional[str] = None
    fetched_at: Optional[str] = None

    @property
    def is_substantial(self) -> bool:
        """Check if doc has substantial content."""
        return len(self.content) >= 100 and self.code_blocks > 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "code_blocks": self.code_blocks,
            "library_id": self.library_id,
            "query": self.query,
            "fetched_at": self.fetched_at,
        }


@dataclass
class FetchProgress:
    """Progress tracking for batch fetch operations."""
    total: int
    completed: int = 0
    successful: int = 0
    failed: int = 0
    cached: int = 0
    library_not_found: int = 0  # Track library resolution failures separately

    @property
    def percent(self) -> float:
        """Completion percentage."""
        return (self.completed / self.total * 100) if self.total > 0 else 0.0

    @property
    def is_complete(self) -> bool:
        """Check if all items processed."""
        return self.completed >= self.total

    @property
    def all_library_not_found(self) -> bool:
        """Check if all failures were due to library not found (graceful failure)."""
        return self.library_not_found > 0 and self.failed == 0


@dataclass
class FetchResult:
    """Result of a fetch operation."""
    library_name: str
    query: str
    status: FetchStatus
    doc: Optional[Context7Doc] = None
    cache_file: Optional[Path] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class LibraryResolutionResult:
    """Result of a library resolution operation.

    Provides detailed information about library resolution attempts,
    enabling graceful fallback handling when libraries aren't found.
    """
    library_name: str
    status: LibraryResolutionStatus
    library_id: Optional[str] = None
    query: str = "documentation"
    message: Optional[str] = None
    raw_response: Optional[str] = None  # For debugging

    @property
    def is_success(self) -> bool:
        """Check if resolution was successful."""
        return self.status in (LibraryResolutionStatus.RESOLVED, LibraryResolutionStatus.CACHED)

    @property
    def is_not_found(self) -> bool:
        """Check if library was not found (vs other errors)."""
        return self.status in (
            LibraryResolutionStatus.NOT_FOUND,
            LibraryResolutionStatus.EMPTY_RESULTS
        )

    @property
    def is_error(self) -> bool:
        """Check if resolution failed due to an error."""
        return self.status in (
            LibraryResolutionStatus.API_ERROR,
            LibraryResolutionStatus.INVALID_RESPONSE
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "library_name": self.library_name,
            "status": self.status.value,
            "library_id": self.library_id,
            "query": self.query,
            "message": self.message,
        }


@dataclass
class BatchFetchResult:
    """Result of a batch fetch operation."""
    results: list[FetchResult] = field(default_factory=list)
    progress: FetchProgress = field(default_factory=lambda: FetchProgress(total=0))

    @property
    def docs(self) -> list[Context7Doc]:
        """Get all successfully fetched documents."""
        return [r.doc for r in self.results if r.doc is not None]

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if not self.results:
            return 0.0
        return self.progress.successful / len(self.results)

    @property
    def is_library_not_found(self) -> bool:
        """Check if all results indicate library not found.

        This is useful for graceful fallback handling - when a library
        isn't in Context7, we return an empty result set instead of an error.
        """
        return (
            self.progress.library_not_found > 0 and
            self.progress.successful == 0 and
            self.progress.cached == 0
        )

    @property
    def has_any_results(self) -> bool:
        """Check if any documents were successfully fetched."""
        return len(self.docs) > 0

    def get_library_not_found_message(self) -> Optional[str]:
        """Get a human-readable message if library was not found."""
        if not self.is_library_not_found:
            return None

        # Get the library name from the first result
        library_name = self.results[0].library_name if self.results else "unknown"
        return f"Library '{library_name}' is not available in Context7. This is expected for libraries not in the Context7 index."


class Context7Client:
    """HTTP client for Context7 MCP API.

    Enhanced client with:
    - Automatic retry on failures
    - Rate limiting handling
    - Batch operations with progress tracking
    - Memory-efficient iteration
    - Comprehensive caching

    Usage:
        client = Context7Client()

        # Fetch single library docs
        result = client.fetch_and_cache("langgraph", "getting started")

        # Batch fetch with progress
        results = client.fetch_batch("langgraph", [
            "getting started", "StateGraph", "nodes and edges"
        ], on_progress=lambda p: print(f"{p.percent:.1f}% done"))

        # Iterate over all cached docs (memory-efficient)
        for doc in client.iter_cached():
            process(doc)
    """

    # Default queries for comprehensive coverage
    DEFAULT_QUERIES = [
        "getting started tutorial",
        "api reference documentation",
        "examples code snippets",
        "concepts overview architecture",
        "best practices patterns",
        "advanced features",
        "configuration setup",
        "troubleshooting common issues",
    ]

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 30,
    ):
        from ..core.config import config
        self.url = config.context7_url
        self.cache_dir = cache_dir or config.context7_cache_dir
        self.max_files = config.max_context7_files  # Configurable limit
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Track resolved library IDs for caching
        self._library_id_cache: dict[str, Optional[str]] = {}

        # Statistics
        self._stats = {
            "requests": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0,
            "cache_hits": 0,
        }

    def _request_with_retry(
        self,
        payload: dict,
        operation: str = "request"
    ) -> Optional[dict]:
        """Execute request with retry logic.

        Args:
            payload: JSON-RPC payload
            operation: Operation name for logging

        Returns:
            Response data or None on failure
        """
        last_error = None

        for attempt in range(self.max_retries):
            self._stats["requests"] += 1

            try:
                resp = requests.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )

                # Handle rate limiting
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", self.retry_delay * (attempt + 1)))
                    logger.warning(
                        f"Rate limited on {operation}, waiting {retry_after}s",
                        extra={"attempt": attempt + 1}
                    )
                    time.sleep(retry_after)
                    self._stats["retries"] += 1
                    continue

                resp.raise_for_status()
                data = resp.json()

                if "error" in data:
                    last_error = data["error"].get("message", "Unknown error")
                    logger.warning(
                        f"API error on {operation}: {last_error}",
                        extra={"attempt": attempt + 1}
                    )
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        self._stats["retries"] += 1
                        continue
                    return None

                self._stats["successful"] += 1
                return data

            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                logger.warning(
                    f"Timeout on {operation}",
                    extra={"attempt": attempt + 1}
                )
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(
                    f"Request error on {operation}: {e}",
                    extra={"attempt": attempt + 1}
                )

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))
                self._stats["retries"] += 1

        self._stats["failed"] += 1
        logger.error(f"Failed {operation} after {self.max_retries} attempts: {last_error}")
        return None

    def resolve_library_id_detailed(
        self,
        library_name: str,
        query: str = "documentation"
    ) -> LibraryResolutionResult:
        """Resolve a library name to a Context7 library ID with detailed status.

        This method provides detailed information about the resolution attempt,
        enabling graceful fallback handling when libraries aren't found.

        Args:
            library_name: Name of the library (e.g., "langgraph")
            query: Query hint for resolution

        Returns:
            LibraryResolutionResult with status and library_id (if found)
        """
        # Check cache first
        cache_key = f"{library_name}:{query}"
        if cache_key in self._library_id_cache:
            cached = self._library_id_cache[cache_key]
            if cached is not None:
                self._stats["cache_hits"] += 1
                logger.debug(f"Library ID cache hit: {library_name} -> {cached}")
                return LibraryResolutionResult(
                    library_name=library_name,
                    status=LibraryResolutionStatus.CACHED,
                    library_id=cached,
                    query=query,
                    message="Retrieved from cache"
                )
            else:
                # Cached "not found" result
                return LibraryResolutionResult(
                    library_name=library_name,
                    status=LibraryResolutionStatus.NOT_FOUND,
                    query=query,
                    message="Library not found (cached result)"
                )

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "resolve-library-id",
                "arguments": {"query": query, "libraryName": library_name}
            },
            "id": 1
        }

        data = self._request_with_retry(payload, f"resolve-library-id({library_name})")

        # Handle API errors (network, timeout, etc.)
        if data is None:
            logger.warning(
                f"API error resolving library: {library_name}",
                extra={"library": library_name, "query": query}
            )
            return LibraryResolutionResult(
                library_name=library_name,
                status=LibraryResolutionStatus.API_ERROR,
                query=query,
                message="Failed to connect to Context7 API"
            )

        # Check for result presence
        if "result" not in data:
            # Check if there's an error in the response
            error_msg = data.get("error", {}).get("message", "Unknown error")
            logger.warning(
                f"Context7 API error for {library_name}: {error_msg}",
                extra={"library": library_name, "query": query, "error": error_msg}
            )
            return LibraryResolutionResult(
                library_name=library_name,
                status=LibraryResolutionStatus.API_ERROR,
                query=query,
                message=f"API error: {error_msg}",
                raw_response=str(data)
            )

        # Try to extract library ID from response
        try:
            content_list = data["result"].get("content", [])

            # Handle empty content list - library not found
            if not content_list:
                self._library_id_cache[cache_key] = None
                logger.warning(
                    f"Library not found in Context7: {library_name} (empty results)",
                    extra={"library": library_name, "query": query}
                )
                return LibraryResolutionResult(
                    library_name=library_name,
                    status=LibraryResolutionStatus.EMPTY_RESULTS,
                    query=query,
                    message="Context7 returned no results for this library"
                )

            text = content_list[0].get("text", "")

            # Check for "no results" indicators in the response text
            no_results_indicators = [
                "no results found",
                "no libraries found",
                "not found",
                "no matching",
                "could not find",
                "unable to find",
            ]
            text_lower = text.lower()
            if any(indicator in text_lower for indicator in no_results_indicators):
                self._library_id_cache[cache_key] = None
                logger.warning(
                    f"Library not found in Context7: {library_name}",
                    extra={
                        "library": library_name,
                        "query": query,
                        "response_snippet": text[:200]
                    }
                )
                return LibraryResolutionResult(
                    library_name=library_name,
                    status=LibraryResolutionStatus.NOT_FOUND,
                    query=query,
                    message="Library not available in Context7",
                    raw_response=text[:500] if text else None
                )

            # Extract library ID from response
            match = re.search(r"/[\w-]+/[\w-]+", text)
            if match:
                lib_id = match.group()
                self._library_id_cache[cache_key] = lib_id
                logger.info(
                    f"Resolved library: {library_name} -> {lib_id}",
                    extra={"library": library_name, "library_id": lib_id}
                )
                return LibraryResolutionResult(
                    library_name=library_name,
                    status=LibraryResolutionStatus.RESOLVED,
                    library_id=lib_id,
                    query=query,
                    message=f"Successfully resolved to {lib_id}"
                )
            else:
                # No match found - response didn't contain a valid library ID
                self._library_id_cache[cache_key] = None
                logger.warning(
                    f"No valid library ID found in response for: {library_name}",
                    extra={
                        "library": library_name,
                        "query": query,
                        "response_snippet": text[:200]
                    }
                )
                return LibraryResolutionResult(
                    library_name=library_name,
                    status=LibraryResolutionStatus.NOT_FOUND,
                    query=query,
                    message="No valid library ID in Context7 response",
                    raw_response=text[:500] if text else None
                )

        except (KeyError, IndexError, TypeError) as e:
            logger.warning(
                f"Failed to parse library ID response for {library_name}: {e}",
                extra={"library": library_name, "error": str(e)}
            )
            return LibraryResolutionResult(
                library_name=library_name,
                status=LibraryResolutionStatus.INVALID_RESPONSE,
                query=query,
                message=f"Invalid response format: {e}",
                raw_response=str(data.get("result", {}))[:500]
            )

    def resolve_library_id(
        self,
        library_name: str,
        query: str = "documentation"
    ) -> Optional[str]:
        """Resolve a library name to a Context7 library ID.

        This is a convenience wrapper around resolve_library_id_detailed()
        that returns just the library ID or None.

        Args:
            library_name: Name of the library (e.g., "langgraph")
            query: Query hint for resolution

        Returns:
            Library ID (e.g., "/langchain-ai/langgraph") or None if not found
        """
        result = self.resolve_library_id_detailed(library_name, query)
        return result.library_id

    def get_library_docs(
        self,
        library_id: str,
        query: str,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """Get documentation for a specific library.

        NOTE: This method requires a pre-resolved library_id. For most use cases,
        prefer `resolve_and_fetch_docs()` which chains resolve -> get_library_docs
        automatically per spec requirement.

        Args:
            library_id: Resolved library ID (from resolve_library_id)
            query: Documentation query
            max_tokens: Optional max tokens limit

        Returns:
            Documentation content or None
        """
        arguments = {"libraryId": library_id, "query": query}
        if max_tokens:
            arguments["maxTokens"] = max_tokens

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get-library-docs",
                "arguments": arguments
            },
            "id": 2
        }

        data = self._request_with_retry(payload, f"get-library-docs({library_id}, {query[:30]}...)")

        if data and "result" in data:
            try:
                return data["result"]["content"][0]["text"]
            except (KeyError, IndexError) as e:
                logger.warning(f"Failed to parse docs response: {e}")

        return None

    def query_docs(self, library_id: str, query: str) -> Optional[str]:
        """Query documentation for a specific library.

        Alias for get_library_docs for backwards compatibility.

        NOTE: For most use cases, prefer `resolve_and_fetch_docs()` which
        chains resolve -> get_library_docs automatically per spec requirement.
        """
        return self.get_library_docs(library_id, query)

    def resolve_and_fetch_docs(
        self,
        library_name: str,
        query: str = "documentation",
        max_tokens: Optional[int] = None
    ) -> tuple[LibraryResolutionResult, Optional[str]]:
        """Resolve library and fetch docs in one call.

        RECOMMENDED: This method implements the spec requirement to ALWAYS call
        get-library-docs after a successful resolve-library-id. It chains the
        two operations and handles caching of the resolved library ID.

        Args:
            library_name: Library name to resolve (e.g., "langgraph")
            query: Documentation query (default: "documentation")
            max_tokens: Optional max tokens limit for docs

        Returns:
            Tuple of (LibraryResolutionResult, documentation_content or None)

        Example:
            >>> client = Context7Client()
            >>> resolution, docs = client.resolve_and_fetch_docs("langgraph", "getting started")
            >>> if resolution.is_success and docs:
            ...     print(f"Found docs for {resolution.library_id}")
            >>> elif resolution.is_not_found:
            ...     print(f"Library not found: {resolution.message}")
        """
        # Step 1: Resolve library ID (uses cache if available)
        resolution = self.resolve_library_id_detailed(library_name, query)

        # Step 2: If resolution failed, return early
        if not resolution.is_success:
            logger.warning(
                f"Cannot fetch docs - library resolution failed: {library_name}",
                extra={
                    "library": library_name,
                    "status": resolution.status.value,
                    "message": resolution.message
                }
            )
            return resolution, None

        # Step 3: ALWAYS call get-library-docs after successful resolution (per spec)
        docs = self.get_library_docs(resolution.library_id, query, max_tokens)

        if docs:
            logger.info(
                f"Successfully fetched docs for {library_name}",
                extra={
                    "library": library_name,
                    "library_id": resolution.library_id,
                    "query": query[:50],
                    "docs_length": len(docs)
                }
            )
        else:
            logger.warning(
                f"Library resolved but docs fetch returned empty: {library_name}",
                extra={
                    "library": library_name,
                    "library_id": resolution.library_id,
                    "query": query
                }
            )

        return resolution, docs

    def resolve_and_fetch_docs_simple(
        self,
        library_name: str,
        query: str = "documentation",
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """Simplified version that returns only the docs content.

        Chains resolve-library-id -> get-library-docs automatically per spec.
        Returns None if resolution fails OR if docs fetch fails.

        Args:
            library_name: Library name to resolve (e.g., "langgraph")
            query: Documentation query (default: "documentation")
            max_tokens: Optional max tokens limit

        Returns:
            Documentation content or None

        Example:
            >>> docs = client.resolve_and_fetch_docs_simple("langgraph", "StateGraph")
            >>> if docs:
            ...     print(docs)
        """
        _, docs = self.resolve_and_fetch_docs(library_name, query, max_tokens)
        return docs

    def get_docs_for_multiple_queries(
        self,
        library_name: str,
        queries: list[str],
        max_tokens: Optional[int] = None
    ) -> dict[str, Optional[str]]:
        """Fetch docs for multiple queries, resolving library ID once.

        Efficiently chains resolve -> multiple get_library_docs calls.
        The library ID is resolved once and cached, then get_library_docs
        is called for each query (per spec requirement).

        Args:
            library_name: Library to fetch docs for
            queries: List of documentation queries
            max_tokens: Optional max tokens limit per query

        Returns:
            Dict mapping query -> documentation content (or None if failed)

        Example:
            >>> results = client.get_docs_for_multiple_queries(
            ...     "langgraph",
            ...     ["getting started", "StateGraph", "nodes and edges"]
            ... )
            >>> for query, docs in results.items():
            ...     print(f"{query}: {'Found' if docs else 'Not found'}")
        """
        results: dict[str, Optional[str]] = {}

        if not queries:
            return results

        # Resolve library ID once (uses cache if available)
        resolution = self.resolve_library_id_detailed(library_name, queries[0])

        if not resolution.is_success:
            logger.warning(
                f"Library resolution failed, returning empty results: {library_name}",
                extra={"library": library_name, "status": resolution.status.value}
            )
            # Return all queries with None
            return {q: None for q in queries}

        library_id = resolution.library_id

        # Fetch docs for each query using the resolved ID (per spec requirement)
        for query in queries:
            docs = self.get_library_docs(library_id, query, max_tokens)
            results[query] = docs
            if docs:
                logger.debug(f"Fetched docs for {library_name}/{query}: {len(docs)} chars")
            else:
                logger.debug(f"No docs found for {library_name}/{query}")

        logger.info(
            f"Fetched docs for {library_name}: {sum(1 for d in results.values() if d)}/{len(queries)} succeeded",
            extra={"library": library_name, "total_queries": len(queries)}
        )

        return results

    def fetch_and_cache_detailed(
        self,
        library_name: str,
        query: str,
        force_refresh: bool = False
    ) -> FetchResult:
        """Fetch documentation and save to cache with detailed status.

        This method provides detailed information about the fetch result,
        enabling graceful handling of library-not-found scenarios.

        Args:
            library_name: Library to fetch docs for
            query: Query string
            force_refresh: If True, bypass cache and re-fetch

        Returns:
            FetchResult with status and detailed information
        """
        start_time = time.time()

        # Check if already cached
        hash_id = hashlib.md5(f"{library_name}{query}".encode()).hexdigest()[:12]
        filename = f"{library_name}_{hash_id}.json"
        cache_file = self.cache_dir / filename

        if cache_file.exists() and not force_refresh:
            self._stats["cache_hits"] += 1
            logger.debug(f"Cache hit: {cache_file.name}")
            try:
                with open(cache_file, encoding="utf-8") as f:
                    data = json.load(f)
                doc = Context7Doc(
                    title=f"{library_name}: {query}",
                    content=data.get("response", ""),
                    source_url=f"context7://{library_name}/{query}",
                    code_blocks=data.get("code_blocks", 0),
                    library_id=data.get("library_id"),
                    query=query,
                    fetched_at=data.get("fetched_at")
                )
                return FetchResult(
                    library_name=library_name,
                    query=query,
                    status=FetchStatus.CACHED,
                    doc=doc,
                    cache_file=cache_file,
                    duration_ms=(time.time() - start_time) * 1000
                )
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cached file {cache_file.name}: {e}")
                # Continue to fetch fresh

        # Resolve library ID with detailed status
        resolution = self.resolve_library_id_detailed(library_name, query)

        # Handle library not found gracefully
        if not resolution.is_success:
            duration_ms = (time.time() - start_time) * 1000

            # Determine appropriate status
            if resolution.is_not_found:
                logger.warning(
                    f"Library not found in Context7: {library_name}",
                    extra={
                        "library": library_name,
                        "query": query,
                        "resolution_status": resolution.status.value,
                        "message": resolution.message
                    }
                )
                return FetchResult(
                    library_name=library_name,
                    query=query,
                    status=FetchStatus.LIBRARY_NOT_FOUND,
                    error=resolution.message,
                    duration_ms=duration_ms
                )
            else:
                # API error or invalid response
                logger.error(
                    f"Failed to resolve library: {library_name}",
                    extra={
                        "library": library_name,
                        "query": query,
                        "resolution_status": resolution.status.value,
                        "message": resolution.message
                    }
                )
                return FetchResult(
                    library_name=library_name,
                    query=query,
                    status=FetchStatus.FAILED,
                    error=resolution.message,
                    duration_ms=duration_ms
                )

        lib_id = resolution.library_id

        # Get docs using get-library-docs (per spec requirement)
        docs = self.get_library_docs(lib_id, query)
        if not docs or len(docs) < 100:
            duration_ms = (time.time() - start_time) * 1000
            logger.warning(
                f"Insufficient documentation for: {library_name}/{query}",
                extra={"library": library_name, "query": query, "library_id": lib_id}
            )
            return FetchResult(
                library_name=library_name,
                query=query,
                status=FetchStatus.NOT_FOUND,
                error="Insufficient documentation content",
                duration_ms=duration_ms
            )

        # Count code blocks
        code_blocks = docs.count("```") // 2

        # Save to cache
        cache_data = {
            "library_id": lib_id,
            "library_name": library_name,
            "query": query,
            "response": docs,
            "code_blocks": code_blocks,
            "fetched_at": datetime.now().isoformat()
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Cached documentation: {cache_file.name}",
                extra={
                    "library": library_name,
                    "query": query[:50],
                    "code_blocks": code_blocks,
                    "size_bytes": len(docs),
                    "duration_ms": duration_ms
                }
            )

            doc = Context7Doc(
                title=f"{library_name}: {query}",
                content=docs,
                source_url=f"context7://{library_name}/{query}",
                code_blocks=code_blocks,
                library_id=lib_id,
                query=query,
                fetched_at=datetime.now().isoformat()
            )

            return FetchResult(
                library_name=library_name,
                query=query,
                status=FetchStatus.SUCCESS,
                doc=doc,
                cache_file=cache_file,
                duration_ms=duration_ms
            )

        except IOError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed to write cache file: {e}")
            return FetchResult(
                library_name=library_name,
                query=query,
                status=FetchStatus.FAILED,
                error=f"Cache write failed: {e}",
                duration_ms=duration_ms
            )

    def fetch_and_cache(
        self,
        library_name: str,
        query: str,
        force_refresh: bool = False
    ) -> Optional[Path]:
        """Fetch documentation and save to cache.

        This is a convenience wrapper around fetch_and_cache_detailed()
        that returns just the cache file path or None.

        Args:
            library_name: Library to fetch docs for
            query: Query string
            force_refresh: If True, bypass cache and re-fetch

        Returns:
            Path to cached file or None on failure
        """
        result = self.fetch_and_cache_detailed(library_name, query, force_refresh)
        return result.cache_file if result.status in (FetchStatus.SUCCESS, FetchStatus.CACHED) else None

    def fetch_batch(
        self,
        library_name: str,
        queries: Optional[list[str]] = None,
        on_progress: Optional[Callable[[FetchProgress], None]] = None,
        parallel: bool = True,
        max_workers: int = 4
    ) -> BatchFetchResult:
        """Fetch multiple queries for a library in batch.

        BMAD: No [:3] limit - fetches ALL queries.

        Args:
            library_name: Library to fetch docs for
            queries: List of queries (uses DEFAULT_QUERIES if None)
            on_progress: Callback for progress updates
            parallel: Use parallel fetching
            max_workers: Max parallel workers

        Returns:
            BatchFetchResult with all fetched documents
        """
        queries = queries or self.DEFAULT_QUERIES
        progress = FetchProgress(total=len(queries))
        results: list[FetchResult] = []

        logger.info(
            f"Starting batch fetch for {library_name}",
            extra={"query_count": len(queries), "parallel": parallel}
        )

        def fetch_single(query: str) -> FetchResult:
            """Fetch a single query using detailed method for proper status tracking."""
            try:
                # Use detailed method to get proper status (LIBRARY_NOT_FOUND, etc.)
                return self.fetch_and_cache_detailed(library_name, query)
            except Exception as e:
                return FetchResult(
                    library_name=library_name,
                    query=query,
                    status=FetchStatus.FAILED,
                    error=str(e),
                    duration_ms=0.0
                )

        def update_progress(result: FetchResult) -> None:
            """Update progress based on fetch result status."""
            progress.completed += 1
            if result.status == FetchStatus.SUCCESS:
                progress.successful += 1
            elif result.status == FetchStatus.CACHED:
                progress.cached += 1
            elif result.status == FetchStatus.LIBRARY_NOT_FOUND:
                progress.library_not_found += 1
            else:
                progress.failed += 1

        if parallel and len(queries) > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch_single, q): q for q in queries}

                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    update_progress(result)

                    if on_progress:
                        on_progress(progress)
        else:
            for query in queries:
                result = fetch_single(query)
                results.append(result)
                update_progress(result)

                if on_progress:
                    on_progress(progress)

        # Log with appropriate level based on results
        if progress.library_not_found > 0 and progress.successful == 0:
            # All queries failed due to library not found - graceful fallback
            logger.warning(
                f"Library '{library_name}' not found in Context7 (all {progress.total} queries returned no results)",
                extra={
                    "total": progress.total,
                    "library_not_found": progress.library_not_found,
                }
            )
        else:
            logger.info(
                f"Batch fetch complete for {library_name}",
                extra={
                    "total": progress.total,
                    "successful": progress.successful,
                    "failed": progress.failed,
                    "cached": progress.cached,
                    "library_not_found": progress.library_not_found
                }
            )

        return BatchFetchResult(results=results, progress=progress)

    def fetch_comprehensive(
        self,
        library_name: str,
        topics: Optional[list[str]] = None,
        on_progress: Optional[Callable[[FetchProgress], None]] = None
    ) -> BatchFetchResult:
        """Fetch comprehensive documentation for a library.

        BMAD: Uses ALL available documentation topics, no [:3] limit.

        Args:
            library_name: Library to fetch docs for
            topics: Additional topics to query
            on_progress: Progress callback

        Returns:
            BatchFetchResult with all documentation
        """
        # Combine default queries with additional topics
        queries = list(self.DEFAULT_QUERIES)
        if topics:
            for topic in topics:
                queries.append(f"{topic} documentation")
                queries.append(f"{topic} examples")

        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_queries.append(q)

        # Respect configurable limit (0 means no limit - use ALL files!)
        if self.max_files > 0 and len(unique_queries) > self.max_files:
            logger.warning(
                f"Query count ({len(unique_queries)}) exceeds max_files ({self.max_files}), truncating"
            )
            unique_queries = unique_queries[:self.max_files]
        else:
            logger.info(f"Fetching ALL {len(unique_queries)} queries (no limit applied)")

        return self.fetch_batch(library_name, unique_queries, on_progress)

    def load_all_cached(self) -> list[dict]:
        """Load all cached documentation.

        BMAD: Returns ALL cached docs, no [:3] limit.

        Returns:
            List of all cached documentation dictionaries
        """
        docs = []
        cache_files = list(self.cache_dir.glob("*.json"))

        logger.debug(f"Loading {len(cache_files)} cached documents")

        for f in cache_files:
            try:
                with open(f, encoding="utf-8") as fp:
                    data = json.load(fp)
                docs.append(data)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache file {f.name}: {e}")

        logger.info(f"Loaded {len(docs)} cached Context7 documents")
        return docs

    def iter_cached(self) -> Iterator[Context7Doc]:
        """Iterate over all cached documents (memory-efficient).

        BMAD: Iterates over ALL cached docs, no [:3] limit.
        Yields documents one at a time for memory efficiency.

        Yields:
            Context7Doc for each cached document
        """
        cache_files = list(self.cache_dir.glob("*.json"))

        for f in cache_files:
            try:
                with open(f, encoding="utf-8") as fp:
                    data = json.load(fp)

                yield Context7Doc(
                    title=f"{data.get('library_name', 'unknown')}: {data.get('query', '')}",
                    content=data.get("response", ""),
                    source_url=f"context7://{data.get('library_id', 'unknown')}",
                    code_blocks=data.get("code_blocks", 0),
                    library_id=data.get("library_id"),
                    query=data.get("query"),
                    fetched_at=data.get("fetched_at")
                )
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache file {f.name}: {e}")

    def load_cached_for_library(self, library_name: str) -> list[Context7Doc]:
        """Load all cached documents for a specific library.

        Args:
            library_name: Library to filter by

        Returns:
            List of Context7Doc for the library
        """
        docs = []
        pattern = f"{library_name}_*.json"

        for f in self.cache_dir.glob(pattern):
            try:
                with open(f, encoding="utf-8") as fp:
                    data = json.load(fp)

                docs.append(Context7Doc(
                    title=f"{library_name}: {data.get('query', '')}",
                    content=data.get("response", ""),
                    source_url=f"context7://{data.get('library_id', 'unknown')}",
                    code_blocks=data.get("code_blocks", 0),
                    library_id=data.get("library_id"),
                    query=data.get("query"),
                    fetched_at=data.get("fetched_at")
                ))
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache file {f.name}: {e}")

        logger.info(f"Loaded {len(docs)} cached documents for {library_name}")
        return docs

    def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        # Count by library
        libraries: dict[str, int] = {}
        for f in cache_files:
            lib = f.name.split("_")[0]
            libraries[lib] = libraries.get(lib, 0) + 1

        return {
            "total_files": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "libraries": libraries,
            "cache_dir": str(self.cache_dir),
        }

    def get_client_stats(self) -> dict:
        """Get client operation statistics.

        Returns:
            Dictionary with client statistics
        """
        return {
            **self._stats,
            "library_id_cache_size": len(self._library_id_cache),
            "success_rate": (
                self._stats["successful"] / self._stats["requests"]
                if self._stats["requests"] > 0 else 0.0
            ),
        }

    def clear_cache(self, library_name: Optional[str] = None) -> int:
        """Clear cached documentation.

        Args:
            library_name: If provided, only clear cache for this library

        Returns:
            Number of files deleted
        """
        if library_name:
            pattern = f"{library_name}_*.json"
        else:
            pattern = "*.json"

        deleted = 0
        for f in self.cache_dir.glob(pattern):
            try:
                f.unlink()
                deleted += 1
            except IOError as e:
                logger.warning(f"Failed to delete cache file {f.name}: {e}")

        logger.info(f"Cleared {deleted} cache files")
        return deleted
