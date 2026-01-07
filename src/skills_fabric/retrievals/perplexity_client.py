"""Perplexity AI Research Client for Skills Fabric.

Provides research and validation queries using Perplexity's sonar model.
Features:
- Citation extraction from responses
- Rate limiting with exponential backoff
- Iterative research loop with query refinement
- Related questions for follow-up research
- Citation validation and research depth tracking

Usage:
    from skills_fabric.retrievals import PerplexityClient

    # Basic research query
    client = PerplexityClient()
    response = await client.search("How does LangGraph StateGraph work?")
    print(f"Answer: {response.content}")
    for citation in response.citations:
        print(f"  - {citation.url}")

    # Simple research loop
    research = await client.research_loop(
        query="LangGraph agent orchestration patterns",
        max_iterations=3
    )
    for finding in research.findings:
        print(f"{finding.query}: {finding.summary}")

    # Advanced iterative research with refinement
    research = await client.iterative_research(
        query="How to implement custom agents in LangGraph",
        max_depth=3,
        strategy="refine",  # or "related", "validate", "comprehensive"
    )
    print(f"Research depth: {research.metrics.depth_reached}")
    print(f"Convergence: {research.metrics.convergence_score:.2f}")

    # Synchronous interface
    response = client.search_sync("Python async best practices")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any, AsyncIterator, Callable
from enum import Enum, auto
import os
import json
import time
import logging
import asyncio
import random

# Get logger for this module
logger = logging.getLogger(__name__)

# Try to import httpx for async support
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    import requests


class SonarModel(Enum):
    """Available Perplexity sonar models."""
    SONAR = "sonar"  # Standard sonar model
    SONAR_PRO = "sonar-pro"  # Enhanced model with larger context
    SONAR_REASONING = "sonar-reasoning"  # Model with reasoning capabilities


class SearchDomain(Enum):
    """Domain filters for search focus."""
    ALL = None  # No domain filter
    ACADEMIC = "academic"  # Academic papers and research
    NEWS = "news"  # Recent news articles
    YOUTUBE = "youtube"  # YouTube videos
    REDDIT = "reddit"  # Reddit discussions


@dataclass
class Citation:
    """A citation from a Perplexity response.

    Contains source URL and optional metadata extracted from the response.
    """
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    position: int = 0  # Position in citation list (1-indexed)

    def to_dict(self) -> dict:
        """Convert citation to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "position": self.position,
        }


@dataclass
class RelatedQuestion:
    """A related question suggested by Perplexity for follow-up research."""
    question: str
    relevance_score: float = 0.0  # Estimated relevance (0-1)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "question": self.question,
            "relevance_score": self.relevance_score,
        }


@dataclass
class TokenUsage:
    """Token usage statistics for a request."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost based on sonar pricing (approximate)."""
        # Sonar pricing: ~$1/1M input, ~$1/1M output (approximate)
        input_cost = (self.prompt_tokens / 1_000_000) * 1.0
        output_cost = (self.completion_tokens / 1_000_000) * 1.0
        return input_cost + output_cost


class RefinementStrategy(Enum):
    """Strategies for refining research queries."""
    RELATED = "related"  # Follow related questions from responses
    REFINE = "refine"  # Refine query based on gaps in findings
    VALIDATE = "validate"  # Validate and cross-check findings
    COMPREHENSIVE = "comprehensive"  # Combine all strategies
    CITATIONS = "citations"  # Dig deeper into cited sources


class ResearchStopReason(Enum):
    """Reasons for stopping the research loop."""
    MAX_DEPTH_REACHED = auto()
    CONVERGED = auto()  # Findings are consistent, no new insights
    NO_NEW_QUERIES = auto()  # No more valid follow-up queries
    USER_STOPPED = auto()
    ERROR = auto()
    BUDGET_EXHAUSTED = auto()  # Token budget reached


@dataclass
class CitationValidation:
    """Validation result for a citation."""
    citation: 'Citation'
    is_valid: bool = True
    is_reachable: bool = True  # URL is accessible
    relevance_score: float = 0.0  # 0-1 how relevant to the query
    error: Optional[str] = None


@dataclass
class ResearchMetrics:
    """Metrics for tracking research progress and quality."""
    depth_reached: int = 0
    total_queries: int = 0
    unique_citations: int = 0
    validated_citations: int = 0
    convergence_score: float = 0.0  # 0-1, higher means more consistent
    knowledge_gain: float = 0.0  # Estimated new information per iteration
    stop_reason: Optional[ResearchStopReason] = None

    @property
    def citation_validation_rate(self) -> float:
        """Proportion of citations that were validated."""
        if self.unique_citations == 0:
            return 0.0
        return self.validated_citations / self.unique_citations

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "depth_reached": self.depth_reached,
            "total_queries": self.total_queries,
            "unique_citations": self.unique_citations,
            "validated_citations": self.validated_citations,
            "convergence_score": self.convergence_score,
            "knowledge_gain": self.knowledge_gain,
            "citation_validation_rate": self.citation_validation_rate,
            "stop_reason": self.stop_reason.name if self.stop_reason else None,
        }


@dataclass
class RefinedQuery:
    """A query refined from previous findings."""
    query: str
    rationale: str  # Why this query was generated
    source_finding_idx: int = -1  # Which finding triggered this
    priority: float = 1.0  # Higher = more important to explore


@dataclass
class PerplexityResponse:
    """Response from Perplexity API.

    Contains the generated content, citations, and optional related questions.
    """
    content: str
    citations: list[Citation] = field(default_factory=list)
    related_questions: list[RelatedQuestion] = field(default_factory=list)
    model: str = "sonar"
    usage: TokenUsage = field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    search_context: Optional[str] = None  # Optional search context from sonar

    @property
    def has_citations(self) -> bool:
        """Check if response includes citations."""
        return len(self.citations) > 0

    @property
    def citation_count(self) -> int:
        """Get number of citations."""
        return len(self.citations)

    @property
    def citation_urls(self) -> list[str]:
        """Get list of citation URLs."""
        return [c.url for c in self.citations]

    def get_markdown_citations(self) -> str:
        """Get citations formatted as markdown."""
        if not self.citations:
            return ""
        lines = ["## Sources"]
        for c in self.citations:
            if c.title:
                lines.append(f"- [{c.title}]({c.url})")
            else:
                lines.append(f"- <{c.url}>")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert response to dictionary."""
        return {
            "content": self.content,
            "citations": [c.to_dict() for c in self.citations],
            "related_questions": [q.to_dict() for q in self.related_questions],
            "model": self.model,
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
            },
            "latency_ms": self.latency_ms,
        }


@dataclass
class ResearchFinding:
    """A finding from a research iteration."""
    query: str
    summary: str
    citations: list[Citation] = field(default_factory=list)
    iteration: int = 0
    depth: int = 0  # Depth level in research tree
    follow_up_questions: list[str] = field(default_factory=list)
    refined_queries: list[RefinedQuery] = field(default_factory=list)
    strategy_used: Optional[RefinementStrategy] = None
    parent_finding_idx: int = -1  # Index of finding that led to this one

    @property
    def has_citations(self) -> bool:
        """Check if this finding has citations."""
        return len(self.citations) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "summary": self.summary,
            "citations": [c.to_dict() for c in self.citations],
            "iteration": self.iteration,
            "depth": self.depth,
            "follow_up_questions": self.follow_up_questions,
            "refined_queries": [
                {"query": rq.query, "rationale": rq.rationale, "priority": rq.priority}
                for rq in self.refined_queries
            ],
            "strategy_used": self.strategy_used.value if self.strategy_used else None,
            "parent_finding_idx": self.parent_finding_idx,
        }


@dataclass
class ResearchResult:
    """Result of a research loop containing multiple findings."""
    initial_query: str
    findings: list[ResearchFinding] = field(default_factory=list)
    total_iterations: int = 0
    total_citations: int = 0
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    metrics: ResearchMetrics = field(default_factory=ResearchMetrics)
    validated_citations: list[CitationValidation] = field(default_factory=list)
    query_history: list[str] = field(default_factory=list)  # All queries executed

    @property
    def all_citations(self) -> list[Citation]:
        """Get all unique citations across findings."""
        seen_urls = set()
        unique = []
        for finding in self.findings:
            for citation in finding.citations:
                if citation.url not in seen_urls:
                    seen_urls.add(citation.url)
                    unique.append(citation)
        return unique

    @property
    def max_depth(self) -> int:
        """Get the maximum depth reached in research."""
        if not self.findings:
            return 0
        return max(f.depth for f in self.findings)

    @property
    def is_converged(self) -> bool:
        """Check if research converged (high consistency)."""
        return self.metrics.convergence_score >= 0.8

    def get_summary(self) -> str:
        """Get a combined summary of all findings."""
        if not self.findings:
            return ""
        summaries = []
        for i, finding in enumerate(self.findings, 1):
            depth_str = f"[Depth {finding.depth}]" if finding.depth > 0 else ""
            summaries.append(f"## Finding {i} {depth_str}: {finding.query}\n\n{finding.summary}")
        return "\n\n".join(summaries)

    def get_research_tree(self) -> str:
        """Get a tree representation of the research path."""
        if not self.findings:
            return ""
        lines = [f"Research: {self.initial_query}"]
        for i, finding in enumerate(self.findings):
            indent = "  " * finding.depth
            prefix = "├─" if i < len(self.findings) - 1 else "└─"
            strategy = f" [{finding.strategy_used.value}]" if finding.strategy_used else ""
            lines.append(f"{indent}{prefix} {finding.query[:60]}...{strategy}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "initial_query": self.initial_query,
            "findings": [f.to_dict() for f in self.findings],
            "total_iterations": self.total_iterations,
            "total_citations": self.total_citations,
            "total_tokens": self.total_tokens,
            "total_latency_ms": self.total_latency_ms,
            "metrics": self.metrics.to_dict(),
            "query_history": self.query_history,
            "max_depth": self.max_depth,
            "is_converged": self.is_converged,
        }


@dataclass
class PerplexityConfig:
    """Configuration for Perplexity client."""
    api_key: str = ""
    base_url: str = "https://api.perplexity.ai"
    model: SonarModel = SonarModel.SONAR
    max_tokens: int = 4096
    temperature: float = 0.2  # Lower for more factual responses
    timeout: int = 60
    # Rate limiting
    max_retries: int = 3
    initial_retry_delay: float = 1.0  # seconds
    max_retry_delay: float = 30.0  # seconds
    retry_multiplier: float = 2.0  # exponential backoff multiplier

    @classmethod
    def from_env(cls) -> "PerplexityConfig":
        """Create config from environment variables.

        Environment variables:
            PERPLEXITY_API_KEY: API key (required)
            PERPLEXITY_MODEL: Model name (default: sonar)
            PERPLEXITY_MAX_TOKENS: Max tokens (default: 4096)
            PERPLEXITY_TEMPERATURE: Temperature (default: 0.2)
            PERPLEXITY_TIMEOUT: Request timeout (default: 60)
        """
        model_str = os.getenv("PERPLEXITY_MODEL", "sonar").lower()
        try:
            model = SonarModel(model_str)
        except ValueError:
            model = SonarModel.SONAR
            logger.warning(f"Unknown model '{model_str}', using default: sonar")

        return cls(
            api_key=os.getenv("PERPLEXITY_API_KEY", ""),
            model=model,
            max_tokens=int(os.getenv("PERPLEXITY_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("PERPLEXITY_TEMPERATURE", "0.2")),
            timeout=int(os.getenv("PERPLEXITY_TIMEOUT", "60")),
        )


class PerplexityClient:
    """Client for Perplexity AI research API.

    Uses the sonar model for research queries with citation extraction
    and rate limiting with exponential backoff.

    Example:
        # Basic usage
        client = PerplexityClient()
        response = await client.search("What is LangGraph?")
        print(response.content)
        for citation in response.citations:
            print(f"Source: {citation.url}")

        # With custom configuration
        config = PerplexityConfig(model=SonarModel.SONAR_PRO)
        client = PerplexityClient(config=config)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[PerplexityConfig] = None,
    ):
        """Initialize Perplexity client.

        Args:
            api_key: Perplexity API key (or set PERPLEXITY_API_KEY env var)
            config: Optional full configuration
        """
        if config:
            self.config = config
        else:
            self.config = PerplexityConfig.from_env()
            if api_key:
                self.config.api_key = api_key

        if not self.config.api_key:
            raise ValueError(
                "Perplexity API key required. "
                "Set PERPLEXITY_API_KEY env var or pass api_key parameter."
            )

        if not HTTPX_AVAILABLE:
            logger.warning(
                "httpx not available. Async methods will use synchronous fallback. "
                "Install httpx for better async support: pip install httpx"
            )

        self._total_usage = TokenUsage()
        self._request_count = 0
        self._retry_count = 0

    @property
    def headers(self) -> dict:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    @property
    def chat_endpoint(self) -> str:
        """Get chat completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    async def search(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        search_domain: SearchDomain = SearchDomain.ALL,
        return_citations: bool = True,
        return_related_questions: bool = True,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> PerplexityResponse:
        """Search for information using Perplexity sonar.

        Args:
            query: Research query
            system_prompt: Optional custom system prompt
            search_domain: Domain to focus search on (academic, news, etc.)
            return_citations: Include citations in response
            return_related_questions: Include related questions
            max_tokens: Override max tokens
            temperature: Override temperature

        Returns:
            PerplexityResponse with content, citations, and related questions
        """
        # Build system prompt
        if system_prompt is None:
            system_prompt = (
                "You are a research assistant. Provide accurate, well-sourced "
                "information. Always cite your sources when making factual claims. "
                "Be concise but comprehensive."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        # Build request payload
        payload = {
            "model": self.config.model.value,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "return_citations": return_citations,
            "return_related_questions": return_related_questions,
        }

        # Add search domain filter if specified
        if search_domain != SearchDomain.ALL and search_domain.value:
            payload["search_domain_filter"] = [search_domain.value]

        # Make request with retry logic
        return await self._request_with_retry(payload)

    async def _request_with_retry(self, payload: dict) -> PerplexityResponse:
        """Make request with exponential backoff retry.

        Args:
            payload: Request payload

        Returns:
            PerplexityResponse

        Raises:
            Exception: If all retries fail
        """
        last_error = None
        delay = self.config.initial_retry_delay

        for attempt in range(self.config.max_retries + 1):
            try:
                return await self._make_request(payload)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check if this is a retryable error
                is_rate_limit = "429" in str(e) or "rate" in error_str
                is_server_error = any(code in str(e) for code in ["500", "502", "503", "504"])
                is_timeout = "timeout" in error_str

                if not (is_rate_limit or is_server_error or is_timeout):
                    # Non-retryable error
                    logger.error(f"Perplexity API error (non-retryable): {e}")
                    raise

                if attempt < self.config.max_retries:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0.5, 1.5)
                    sleep_time = min(delay * jitter, self.config.max_retry_delay)

                    logger.warning(
                        f"Perplexity request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    self._retry_count += 1

                    await asyncio.sleep(sleep_time)
                    delay *= self.config.retry_multiplier
                else:
                    logger.error(
                        f"Perplexity request failed after {self.config.max_retries + 1} attempts: {e}"
                    )

        raise last_error or Exception("Request failed with no error details")

    async def _make_request(self, payload: dict) -> PerplexityResponse:
        """Make a single API request.

        Args:
            payload: Request payload

        Returns:
            PerplexityResponse
        """
        start_time = time.time()
        self._request_count += 1

        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self.chat_endpoint,
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        else:
            # Fallback to synchronous requests
            response = requests.post(
                self.chat_endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = (time.time() - start_time) * 1000

        return self._parse_response(data, latency_ms)

    def _parse_response(self, data: dict, latency_ms: float) -> PerplexityResponse:
        """Parse API response into PerplexityResponse.

        Args:
            data: Raw API response
            latency_ms: Request latency

        Returns:
            PerplexityResponse
        """
        # Extract content
        choices = data.get("choices", [])
        if not choices:
            logger.warning("Perplexity response has no choices")
            content = ""
        else:
            message = choices[0].get("message", {})
            content = message.get("content", "")

        # Extract citations
        citations = []
        raw_citations = data.get("citations", [])
        for i, url in enumerate(raw_citations, 1):
            if isinstance(url, str):
                citations.append(Citation(url=url, position=i))
            elif isinstance(url, dict):
                citations.append(Citation(
                    url=url.get("url", ""),
                    title=url.get("title"),
                    snippet=url.get("snippet"),
                    position=i,
                ))

        # Extract related questions
        related_questions = []
        raw_questions = data.get("related_questions", [])
        for i, q in enumerate(raw_questions):
            if isinstance(q, str):
                # Estimate relevance based on position (first is most relevant)
                relevance = 1.0 - (i * 0.15)  # Decrease by 15% per position
                related_questions.append(RelatedQuestion(
                    question=q,
                    relevance_score=max(0.0, relevance),
                ))
            elif isinstance(q, dict):
                related_questions.append(RelatedQuestion(
                    question=q.get("question", ""),
                    relevance_score=q.get("relevance_score", 0.0),
                ))

        # Parse usage
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        # Track cumulative usage
        self._total_usage.prompt_tokens += usage.prompt_tokens
        self._total_usage.completion_tokens += usage.completion_tokens
        self._total_usage.total_tokens += usage.total_tokens

        return PerplexityResponse(
            content=content,
            citations=citations,
            related_questions=related_questions,
            model=data.get("model", self.config.model.value),
            usage=usage,
            latency_ms=latency_ms,
        )

    async def search_academic(
        self,
        query: str,
        max_tokens: Optional[int] = None,
    ) -> PerplexityResponse:
        """Search academic sources specifically.

        Args:
            query: Research query
            max_tokens: Override max tokens

        Returns:
            PerplexityResponse focused on academic sources
        """
        return await self.search(
            query=query,
            search_domain=SearchDomain.ACADEMIC,
            system_prompt=(
                "You are an academic research assistant. Focus on peer-reviewed "
                "sources, academic papers, and authoritative research. Cite all "
                "sources with academic rigor."
            ),
            max_tokens=max_tokens,
        )

    async def validate_claim(
        self,
        claim: str,
        context: Optional[str] = None,
    ) -> PerplexityResponse:
        """Validate a technical claim by searching for evidence.

        Args:
            claim: The claim to validate
            context: Optional context about the claim

        Returns:
            PerplexityResponse with validation and sources
        """
        query = f"Verify this claim: {claim}"
        if context:
            query = f"{query}\n\nContext: {context}"

        return await self.search(
            query=query,
            system_prompt=(
                "You are a fact-checker. Evaluate the given claim against "
                "available evidence. Cite sources that support or refute the claim. "
                "Be objective and indicate confidence level."
            ),
            temperature=0.1,  # More deterministic for fact-checking
        )

    async def iterative_research(
        self,
        query: str,
        max_depth: int = 3,
        max_iterations: int = 10,
        strategy: RefinementStrategy = RefinementStrategy.COMPREHENSIVE,
        min_convergence: float = 0.8,
        validate_citations: bool = True,
        on_finding: Optional[Callable[[ResearchFinding], None]] = None,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
    ) -> ResearchResult:
        """Perform iterative research with query refinement based on findings.

        This implements an advanced research loop pattern that:
        1. Executes initial query and extracts citations/findings
        2. Validates citations for reliability and relevance
        3. Identifies knowledge gaps in the findings
        4. Generates refined follow-up queries based on gaps
        5. Tracks convergence to determine when research is complete
        6. Builds a research tree with depth tracking

        Args:
            query: Initial research query
            max_depth: Maximum depth of research tree (default: 3)
            max_iterations: Maximum total queries to execute (default: 10)
            strategy: Query refinement strategy (default: COMPREHENSIVE)
            min_convergence: Stop when convergence score reaches this (default: 0.8)
            validate_citations: Whether to validate citations (default: True)
            on_finding: Optional callback for each finding
            on_progress: Optional progress callback (iteration, total, status)

        Returns:
            ResearchResult with all findings, metrics, and validated citations
        """
        result = ResearchResult(initial_query=query)
        result.query_history = [query]

        # Track research state
        seen_queries: set[str] = {query.lower()}
        seen_citation_urls: set[str] = set()
        all_key_concepts: set[str] = set()
        current_depth = 0
        iteration = 0

        # Queue of queries to explore: (query, depth, parent_idx, rationale)
        query_queue: list[tuple[str, int, int, str]] = [(query, 0, -1, "initial")]

        while query_queue and iteration < max_iterations:
            current_query, depth, parent_idx, rationale = query_queue.pop(0)

            if depth > max_depth:
                continue

            iteration += 1
            if on_progress:
                on_progress(iteration, max_iterations, f"Researching: {current_query[:50]}...")

            logger.info(
                f"Iterative research [{iteration}/{max_iterations}] depth={depth}: "
                f"{current_query[:60]}..."
            )

            # Execute search
            try:
                response = await self.search(
                    query=current_query,
                    return_citations=True,
                    return_related_questions=True,
                )
            except Exception as e:
                logger.error(f"Search failed for query '{current_query[:50]}...': {e}")
                result.metrics.stop_reason = ResearchStopReason.ERROR
                continue

            # Extract key concepts from content
            key_concepts = self._extract_key_concepts(response.content)
            new_concepts = key_concepts - all_key_concepts
            all_key_concepts.update(key_concepts)

            # Track unique citations
            new_citations = []
            for citation in response.citations:
                if citation.url not in seen_citation_urls:
                    seen_citation_urls.add(citation.url)
                    new_citations.append(citation)

            # Determine strategy for this finding based on depth and overall strategy
            finding_strategy = self._select_finding_strategy(
                strategy, depth, len(new_citations), len(new_concepts)
            )

            # Create finding
            finding = ResearchFinding(
                query=current_query,
                summary=response.content,
                citations=response.citations,
                iteration=iteration,
                depth=depth,
                follow_up_questions=[q.question for q in response.related_questions],
                strategy_used=finding_strategy,
                parent_finding_idx=parent_idx,
            )

            # Validate citations if requested
            if validate_citations and response.citations:
                validated = await self._validate_citations(
                    response.citations, current_query
                )
                result.validated_citations.extend(validated)
                result.metrics.validated_citations += sum(
                    1 for v in validated if v.is_valid
                )

            # Identify gaps and generate refined queries
            if depth < max_depth:
                refined_queries = self._generate_refined_queries(
                    finding=finding,
                    strategy=strategy,
                    seen_queries=seen_queries,
                    all_concepts=all_key_concepts,
                    finding_idx=len(result.findings),
                )
                finding.refined_queries = refined_queries

                # Add refined queries to queue
                for rq in refined_queries:
                    if rq.query.lower() not in seen_queries:
                        seen_queries.add(rq.query.lower())
                        result.query_history.append(rq.query)
                        # Prioritize by relevance score
                        insert_pos = 0
                        for i, (q, d, p, r) in enumerate(query_queue):
                            if d > depth + 1 or (d == depth + 1 and rq.priority < 0.5):
                                insert_pos = i + 1
                        query_queue.insert(insert_pos, (rq.query, depth + 1, len(result.findings), rq.rationale))

            result.findings.append(finding)
            result.total_iterations = iteration
            result.total_citations += len(response.citations)
            result.total_tokens += response.usage.total_tokens
            result.total_latency_ms += response.latency_ms

            if on_finding:
                on_finding(finding)

            # Update current depth
            current_depth = max(current_depth, depth)
            result.metrics.depth_reached = current_depth

            # Calculate convergence
            convergence = self._calculate_convergence(result.findings)
            result.metrics.convergence_score = convergence

            if convergence >= min_convergence:
                logger.info(f"Research converged at {convergence:.2f} >= {min_convergence}")
                result.metrics.stop_reason = ResearchStopReason.CONVERGED
                break

        # Final metrics calculation
        result.metrics.total_queries = result.total_iterations
        result.metrics.unique_citations = len(seen_citation_urls)
        result.metrics.knowledge_gain = self._calculate_knowledge_gain(result.findings)

        if not result.metrics.stop_reason:
            if iteration >= max_iterations:
                result.metrics.stop_reason = ResearchStopReason.MAX_DEPTH_REACHED
            elif not query_queue:
                result.metrics.stop_reason = ResearchStopReason.NO_NEW_QUERIES

        logger.info(
            f"Iterative research complete: {result.total_iterations} queries, "
            f"depth {result.metrics.depth_reached}, "
            f"{result.metrics.unique_citations} citations, "
            f"convergence {result.metrics.convergence_score:.2f}, "
            f"stop reason: {result.metrics.stop_reason.name if result.metrics.stop_reason else 'unknown'}"
        )

        return result

    def _extract_key_concepts(self, content: str) -> set[str]:
        """Extract key concepts from research content.

        Simple extraction based on common patterns. In production,
        this could use NER or more sophisticated NLP.
        """
        concepts: set[str] = set()

        # Extract capitalized multi-word terms (likely named concepts)
        import re
        # Match patterns like "StateGraph", "LangGraph", "API Gateway"
        pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b'
        for match in re.finditer(pattern, content):
            concepts.add(match.group(1))

        # Match quoted terms
        quoted_pattern = r'["\']([^"\']+)["\']'
        for match in re.finditer(quoted_pattern, content):
            term = match.group(1).strip()
            if 2 <= len(term) <= 50:  # Reasonable term length
                concepts.add(term)

        # Extract code-like terms (snake_case, camelCase in backticks)
        code_pattern = r'`([a-z_][a-z0-9_]*(?:_[a-z0-9]+)*)`'
        for match in re.finditer(code_pattern, content, re.IGNORECASE):
            concepts.add(match.group(1))

        return concepts

    def _select_finding_strategy(
        self,
        overall_strategy: RefinementStrategy,
        depth: int,
        new_citations_count: int,
        new_concepts_count: int,
    ) -> RefinementStrategy:
        """Select the best strategy for a specific finding based on context."""
        if overall_strategy != RefinementStrategy.COMPREHENSIVE:
            return overall_strategy

        # Comprehensive strategy adapts based on context
        if depth == 0:
            return RefinementStrategy.RELATED  # Start with related questions
        elif new_citations_count > 3:
            return RefinementStrategy.CITATIONS  # Rich sources to explore
        elif new_concepts_count < 2:
            return RefinementStrategy.REFINE  # Need to dig deeper
        else:
            return RefinementStrategy.VALIDATE  # Cross-check findings

    async def _validate_citations(
        self,
        citations: list[Citation],
        query: str,
    ) -> list[CitationValidation]:
        """Validate citations for relevance and basic checks.

        This performs lightweight validation without making HTTP requests
        to the citation URLs. For full validation, use a dedicated service.
        """
        validations = []

        # Domain trust scores (simplified)
        trusted_domains = {
            'github.com': 0.9,
            'docs.python.org': 0.95,
            'langchain.com': 0.85,
            'openai.com': 0.9,
            'anthropic.com': 0.9,
            'arxiv.org': 0.9,
            'stackoverflow.com': 0.7,
            'medium.com': 0.5,
            'dev.to': 0.5,
        }

        query_terms = set(query.lower().split())

        for citation in citations:
            # Parse domain
            try:
                from urllib.parse import urlparse
                parsed = urlparse(citation.url)
                domain = parsed.netloc.lower()
                # Remove www prefix
                if domain.startswith('www.'):
                    domain = domain[4:]
            except Exception:
                domain = ""

            # Calculate domain trust
            trust_score = 0.5  # Default
            for trusted, score in trusted_domains.items():
                if trusted in domain:
                    trust_score = score
                    break

            # Calculate relevance based on URL/title overlap with query
            url_lower = citation.url.lower()
            title_lower = (citation.title or "").lower()
            relevance = 0.0
            for term in query_terms:
                if len(term) > 3:  # Skip short words
                    if term in url_lower:
                        relevance += 0.2
                    if term in title_lower:
                        relevance += 0.3
            relevance = min(1.0, relevance)

            # Basic validity check
            is_valid = (
                citation.url.startswith(('http://', 'https://')) and
                len(citation.url) < 2000 and
                trust_score >= 0.4
            )

            validations.append(CitationValidation(
                citation=citation,
                is_valid=is_valid,
                is_reachable=True,  # Would need HTTP check for real validation
                relevance_score=relevance,
                error=None if is_valid else "Low trust domain or invalid URL",
            ))

        return validations

    def _generate_refined_queries(
        self,
        finding: ResearchFinding,
        strategy: RefinementStrategy,
        seen_queries: set[str],
        all_concepts: set[str],
        finding_idx: int,
    ) -> list[RefinedQuery]:
        """Generate refined follow-up queries based on the finding and strategy."""
        refined: list[RefinedQuery] = []

        # Strategy: RELATED - Use API-provided related questions
        if strategy in (RefinementStrategy.RELATED, RefinementStrategy.COMPREHENSIVE):
            for i, question in enumerate(finding.follow_up_questions[:3]):
                if question.lower() not in seen_queries:
                    priority = 1.0 - (i * 0.15)  # Decrease priority for later questions
                    refined.append(RefinedQuery(
                        query=question,
                        rationale="API-suggested related question",
                        source_finding_idx=finding_idx,
                        priority=priority,
                    ))

        # Strategy: REFINE - Generate queries to fill gaps
        if strategy in (RefinementStrategy.REFINE, RefinementStrategy.COMPREHENSIVE):
            # Look for gaps in the content
            gaps = self._identify_gaps(finding.summary)
            for gap in gaps[:2]:
                refined_query = f"{finding.query} {gap}"
                if refined_query.lower() not in seen_queries:
                    refined.append(RefinedQuery(
                        query=refined_query,
                        rationale=f"Fill gap: {gap}",
                        source_finding_idx=finding_idx,
                        priority=0.8,
                    ))

        # Strategy: VALIDATE - Cross-check claims
        if strategy in (RefinementStrategy.VALIDATE, RefinementStrategy.COMPREHENSIVE):
            # Extract a claim to validate
            claim = self._extract_main_claim(finding.summary)
            if claim:
                validation_query = f"Is it true that {claim}? Evidence and sources"
                if validation_query.lower() not in seen_queries:
                    refined.append(RefinedQuery(
                        query=validation_query,
                        rationale=f"Validate claim: {claim[:50]}...",
                        source_finding_idx=finding_idx,
                        priority=0.7,
                    ))

        # Strategy: CITATIONS - Dig into cited sources
        if strategy in (RefinementStrategy.CITATIONS, RefinementStrategy.COMPREHENSIVE):
            for citation in finding.citations[:2]:
                if citation.title:
                    citation_query = f"More details about {citation.title}"
                    if citation_query.lower() not in seen_queries:
                        refined.append(RefinedQuery(
                            query=citation_query,
                            rationale=f"Explore citation: {citation.title[:30]}...",
                            source_finding_idx=finding_idx,
                            priority=0.6,
                        ))

        return refined

    def _identify_gaps(self, content: str) -> list[str]:
        """Identify potential knowledge gaps in the content."""
        gaps = []

        # Look for hedging language indicating uncertainty
        hedging_phrases = [
            "may be", "might", "could be", "possibly",
            "not clear", "unclear", "unknown", "varies",
            "depends on", "in some cases", "sometimes",
        ]
        content_lower = content.lower()
        for phrase in hedging_phrases:
            if phrase in content_lower:
                # Extract context around the hedging phrase
                idx = content_lower.find(phrase)
                start = max(0, idx - 30)
                end = min(len(content), idx + len(phrase) + 30)
                context = content[start:end].strip()
                if context:
                    gaps.append(f"clarify: {context}")

        # Look for specific question markers in content
        question_markers = ["?", "how to", "what is", "why does"]
        for marker in question_markers:
            if marker in content_lower:
                gaps.append("implementation details")
                break

        return gaps[:3]  # Limit to 3 gaps

    def _extract_main_claim(self, content: str) -> Optional[str]:
        """Extract the main factual claim from content for validation."""
        # Simple heuristic: first sentence that contains action verbs
        sentences = content.split('.')
        action_words = ['is', 'are', 'uses', 'provides', 'allows', 'enables', 'supports']

        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence = sentence.strip()
            if 20 < len(sentence) < 200:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in action_words):
                    return sentence

        return None

    def _calculate_convergence(self, findings: list[ResearchFinding]) -> float:
        """Calculate how much the research findings converge.

        Higher convergence means findings are consistent and cover similar ground.
        """
        if len(findings) < 2:
            return 0.0

        # Simple convergence metric based on:
        # 1. Citation overlap between findings
        # 2. Content similarity (via shared terms)

        all_urls: list[set[str]] = [
            {c.url for c in f.citations} for f in findings
        ]

        # Calculate average pairwise citation overlap
        overlaps = []
        for i in range(len(all_urls)):
            for j in range(i + 1, len(all_urls)):
                if all_urls[i] and all_urls[j]:
                    intersection = len(all_urls[i] & all_urls[j])
                    union = len(all_urls[i] | all_urls[j])
                    if union > 0:
                        overlaps.append(intersection / union)

        if not overlaps:
            return 0.0

        avg_overlap = sum(overlaps) / len(overlaps)

        # Weight by depth - deeper findings contribute more to convergence
        depth_factor = 1.0 + (max(f.depth for f in findings) * 0.1)

        return min(1.0, avg_overlap * depth_factor * 2)  # Scale up slightly

    def _calculate_knowledge_gain(self, findings: list[ResearchFinding]) -> float:
        """Estimate the knowledge gain across all findings."""
        if not findings:
            return 0.0

        # Simple metric based on:
        # - Number of unique citations
        # - Variety of follow-up questions
        # - Depth achieved

        unique_urls = set()
        unique_questions = set()
        for f in findings:
            for c in f.citations:
                unique_urls.add(c.url)
            for q in f.follow_up_questions:
                unique_questions.add(q.lower())

        max_depth = max(f.depth for f in findings)

        # Normalize components
        citation_score = min(1.0, len(unique_urls) / 20)
        question_score = min(1.0, len(unique_questions) / 15)
        depth_score = min(1.0, max_depth / 3)

        return (citation_score + question_score + depth_score) / 3

    def iterative_research_sync(
        self,
        query: str,
        max_depth: int = 3,
        **kwargs,
    ) -> ResearchResult:
        """Synchronous wrapper for iterative_research()."""
        return asyncio.run(self.iterative_research(query, max_depth, **kwargs))

    async def research_loop(
        self,
        query: str,
        max_iterations: int = 3,
        follow_up_strategy: str = "related",
    ) -> ResearchResult:
        """Perform iterative research with follow-up queries.

        This implements the research loop pattern:
        1. Initial query
        2. Extract citations and related questions
        3. Follow up on most relevant questions
        4. Repeat until max_iterations or no new insights

        Args:
            query: Initial research query
            max_iterations: Maximum research iterations
            follow_up_strategy: "related" (use related questions) or "citations" (dig into citations)

        Returns:
            ResearchResult with all findings
        """
        result = ResearchResult(initial_query=query)
        current_query = query
        seen_questions = {query}  # Track to avoid duplicates

        for iteration in range(max_iterations):
            logger.info(f"Research loop iteration {iteration + 1}/{max_iterations}: {current_query[:50]}...")

            response = await self.search(
                query=current_query,
                return_citations=True,
                return_related_questions=True,
            )

            # Create finding for this iteration
            finding = ResearchFinding(
                query=current_query,
                summary=response.content,
                citations=response.citations,
                iteration=iteration + 1,
                follow_up_questions=[q.question for q in response.related_questions],
            )
            result.findings.append(finding)
            result.total_iterations = iteration + 1
            result.total_citations += len(response.citations)
            result.total_tokens += response.usage.total_tokens
            result.total_latency_ms += response.latency_ms

            # Determine next query
            if iteration + 1 < max_iterations:
                next_query = None

                if follow_up_strategy == "related" and response.related_questions:
                    # Find first related question not yet asked
                    for rq in response.related_questions:
                        if rq.question not in seen_questions:
                            next_query = rq.question
                            seen_questions.add(next_query)
                            break

                if not next_query:
                    # No more new questions to ask
                    logger.info(f"Research loop complete: no new questions after {iteration + 1} iterations")
                    break

                current_query = next_query

        logger.info(
            f"Research complete: {result.total_iterations} iterations, "
            f"{result.total_citations} citations, {result.total_tokens} tokens"
        )

        return result

    def search_sync(
        self,
        query: str,
        **kwargs,
    ) -> PerplexityResponse:
        """Synchronous wrapper for search().

        Args:
            query: Research query
            **kwargs: Additional arguments passed to search()

        Returns:
            PerplexityResponse
        """
        return asyncio.run(self.search(query, **kwargs))

    def validate_claim_sync(
        self,
        claim: str,
        context: Optional[str] = None,
    ) -> PerplexityResponse:
        """Synchronous wrapper for validate_claim()."""
        return asyncio.run(self.validate_claim(claim, context))

    def research_loop_sync(
        self,
        query: str,
        max_iterations: int = 3,
        **kwargs,
    ) -> ResearchResult:
        """Synchronous wrapper for research_loop()."""
        return asyncio.run(self.research_loop(query, max_iterations, **kwargs))

    def get_total_usage(self) -> TokenUsage:
        """Get cumulative token usage."""
        return self._total_usage

    def get_stats(self) -> dict:
        """Get client statistics."""
        return {
            "total_requests": self._request_count,
            "total_retries": self._retry_count,
            "total_tokens": self._total_usage.total_tokens,
            "estimated_cost_usd": self._total_usage.estimated_cost_usd,
        }

    def reset_stats(self) -> None:
        """Reset usage and statistics."""
        self._total_usage = TokenUsage()
        self._request_count = 0
        self._retry_count = 0


# CLI interface
async def _test_perplexity() -> None:
    """Test Perplexity client."""
    client = PerplexityClient()

    print("=== Basic Search Test ===")
    response = await client.search("What is LangGraph StateGraph?")
    print(f"Content: {response.content[:200]}...")
    print(f"Citations: {len(response.citations)}")
    for c in response.citations[:3]:
        print(f"  - {c.url}")
    print(f"Related questions: {len(response.related_questions)}")
    for q in response.related_questions[:3]:
        print(f"  - {q.question}")
    print()

    print("=== Simple Research Loop Test ===")
    result = await client.research_loop(
        "Python async patterns for API clients",
        max_iterations=2
    )
    print(f"Iterations: {result.total_iterations}")
    print(f"Total citations: {result.total_citations}")
    for finding in result.findings:
        print(f"  - Iteration {finding.iteration}: {finding.query[:50]}...")
    print()

    print("=== Iterative Research Test ===")
    result = await client.iterative_research(
        "LangGraph agent orchestration patterns",
        max_depth=2,
        max_iterations=4,
        strategy=RefinementStrategy.COMPREHENSIVE,
        validate_citations=True,
    )
    print(f"Depth reached: {result.metrics.depth_reached}")
    print(f"Total queries: {result.metrics.total_queries}")
    print(f"Unique citations: {result.metrics.unique_citations}")
    print(f"Validated citations: {result.metrics.validated_citations}")
    print(f"Convergence: {result.metrics.convergence_score:.2f}")
    print(f"Stop reason: {result.metrics.stop_reason.name if result.metrics.stop_reason else 'unknown'}")
    print()
    print("Research tree:")
    print(result.get_research_tree())
    print()

    print("=== Stats ===")
    stats = client.get_stats()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Total tokens: {stats['total_tokens']}")


def _cli() -> None:
    """CLI entry point for Perplexity client."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Perplexity AI Research Client - Search with citations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Basic research query
  python -m skills_fabric.retrievals.perplexity_client -q "What is LangGraph?"

  # Academic search
  python -m skills_fabric.retrievals.perplexity_client -q "transformer architectures" --academic

  # Validate a claim
  python -m skills_fabric.retrievals.perplexity_client --validate "LangGraph uses StateGraph for orchestration"

  # Simple research loop with multiple iterations
  python -m skills_fabric.retrievals.perplexity_client -q "Python async patterns" --loop --iterations 3

  # Advanced iterative research with query refinement
  python -m skills_fabric.retrievals.perplexity_client -q "LangGraph agents" --iterative --depth 3 --strategy comprehensive

  # Output as JSON
  python -m skills_fabric.retrievals.perplexity_client -q "REST API best practices" --json

REFINEMENT STRATEGIES:
  related      - Follow API-suggested related questions
  refine       - Refine query based on gaps in findings
  validate     - Cross-check and validate claims
  comprehensive - Combine all strategies adaptively
  citations    - Dig deeper into cited sources

ENVIRONMENT:
  PERPLEXITY_API_KEY: Required API key from https://www.perplexity.ai/settings/api
"""
    )
    parser.add_argument("--query", "-q", help="Research query")
    parser.add_argument("--validate", help="Claim to validate")
    parser.add_argument("--academic", action="store_true", help="Focus on academic sources")
    parser.add_argument("--loop", action="store_true", help="Run simple research loop")
    parser.add_argument("--iterative", action="store_true", help="Run iterative research with query refinement")
    parser.add_argument("--iterations", type=int, default=3, help="Max iterations for research")
    parser.add_argument("--depth", type=int, default=3, help="Max depth for iterative research")
    parser.add_argument("--strategy", type=str, default="comprehensive",
                       choices=["related", "refine", "validate", "comprehensive", "citations"],
                       help="Query refinement strategy for iterative research")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--test", action="store_true", help="Run test suite")

    args = parser.parse_args()

    if args.test:
        asyncio.run(_test_perplexity())
        return

    if not args.query and not args.validate:
        parser.error("Either --query or --validate is required")

    async def run() -> None:
        client = PerplexityClient()

        if args.validate:
            response = await client.validate_claim(args.validate)
            if args.json:
                print(json.dumps(response.to_dict(), indent=2))
            else:
                print(f"Validation: {response.content}")
                print(f"\nSources ({len(response.citations)}):")
                for c in response.citations:
                    print(f"  - {c.url}")

        elif args.loop:
            result = await client.research_loop(args.query, max_iterations=args.iterations)
            if args.json:
                print(json.dumps({
                    "initial_query": result.initial_query,
                    "total_iterations": result.total_iterations,
                    "total_citations": result.total_citations,
                    "findings": [
                        {
                            "query": f.query,
                            "summary": f.summary,
                            "citations": [c.to_dict() for c in f.citations],
                        }
                        for f in result.findings
                    ],
                }, indent=2))
            else:
                print(f"Research: {result.initial_query}")
                print(f"Iterations: {result.total_iterations}")
                print(f"Total citations: {result.total_citations}")
                print()
                for finding in result.findings:
                    print(f"=== Iteration {finding.iteration}: {finding.query[:60]}... ===")
                    print(finding.summary[:300] + "...")
                    print()

        elif args.iterative:
            # Map strategy string to enum
            strategy_map = {
                "related": RefinementStrategy.RELATED,
                "refine": RefinementStrategy.REFINE,
                "validate": RefinementStrategy.VALIDATE,
                "comprehensive": RefinementStrategy.COMPREHENSIVE,
                "citations": RefinementStrategy.CITATIONS,
            }
            strategy = strategy_map.get(args.strategy, RefinementStrategy.COMPREHENSIVE)

            def on_progress(iteration: int, total: int, status: str) -> None:
                if not args.json:
                    print(f"[{iteration}/{total}] {status}")

            result = await client.iterative_research(
                args.query,
                max_depth=args.depth,
                max_iterations=args.iterations,
                strategy=strategy,
                on_progress=on_progress,
            )

            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(f"\n{'='*60}")
                print(f"Iterative Research Complete: {result.initial_query}")
                print(f"{'='*60}")
                print(f"Depth reached: {result.metrics.depth_reached}")
                print(f"Total queries: {result.metrics.total_queries}")
                print(f"Unique citations: {result.metrics.unique_citations}")
                print(f"Validated citations: {result.metrics.validated_citations}")
                print(f"Convergence: {result.metrics.convergence_score:.2f}")
                print(f"Knowledge gain: {result.metrics.knowledge_gain:.2f}")
                print(f"Stop reason: {result.metrics.stop_reason.name if result.metrics.stop_reason else 'unknown'}")
                print()
                print("Research Tree:")
                print(result.get_research_tree())
                print()
                print("Summary:")
                print(result.get_summary()[:1000])
                if len(result.get_summary()) > 1000:
                    print("...")
                print()
                print(f"All unique citations ({len(result.all_citations)}):")
                for c in result.all_citations[:10]:
                    print(f"  - {c.url}")
                if len(result.all_citations) > 10:
                    print(f"  ... and {len(result.all_citations) - 10} more")

        elif args.academic:
            response = await client.search_academic(args.query)
            if args.json:
                print(json.dumps(response.to_dict(), indent=2))
            else:
                print(f"Academic Search: {args.query}")
                print(f"\n{response.content}")
                print(f"\nSources ({len(response.citations)}):")
                for c in response.citations:
                    print(f"  - {c.url}")

        else:
            response = await client.search(args.query)
            if args.json:
                print(json.dumps(response.to_dict(), indent=2))
            else:
                print(response.content)
                print(f"\n--- Sources ({len(response.citations)}) ---")
                for c in response.citations:
                    print(f"  - {c.url}")
                if response.related_questions:
                    print(f"\n--- Related Questions ---")
                    for q in response.related_questions:
                        print(f"  - {q.question}")

    asyncio.run(run())


if __name__ == "__main__":
    _cli()
