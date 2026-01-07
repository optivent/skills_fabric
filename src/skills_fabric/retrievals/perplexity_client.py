"""Perplexity AI Research Client for Skills Fabric.

Provides research and validation queries using Perplexity's sonar model.
Features:
- Citation extraction from responses
- Rate limiting with exponential backoff
- Research loop pattern for iterative refinement
- Related questions for follow-up research

Usage:
    from skills_fabric.retrievals import PerplexityClient

    # Basic research query
    client = PerplexityClient()
    response = await client.search("How does LangGraph StateGraph work?")
    print(f"Answer: {response.content}")
    for citation in response.citations:
        print(f"  - {citation.url}")

    # Research loop for deeper understanding
    research = await client.research_loop(
        query="LangGraph agent orchestration patterns",
        max_iterations=3
    )
    for finding in research.findings:
        print(f"{finding.query}: {finding.summary}")

    # Synchronous interface
    response = client.search_sync("Python async best practices")
"""
from dataclasses import dataclass, field
from typing import Optional, Any, AsyncIterator
from enum import Enum
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
    follow_up_questions: list[str] = field(default_factory=list)


@dataclass
class ResearchResult:
    """Result of a research loop containing multiple findings."""
    initial_query: str
    findings: list[ResearchFinding] = field(default_factory=list)
    total_iterations: int = 0
    total_citations: int = 0
    total_tokens: int = 0
    total_latency_ms: float = 0.0

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

    def get_summary(self) -> str:
        """Get a combined summary of all findings."""
        if not self.findings:
            return ""
        summaries = []
        for i, finding in enumerate(self.findings, 1):
            summaries.append(f"## Finding {i}: {finding.query}\n\n{finding.summary}")
        return "\n\n".join(summaries)


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

    print("=== Research Loop Test ===")
    result = await client.research_loop(
        "Python async patterns for API clients",
        max_iterations=2
    )
    print(f"Iterations: {result.total_iterations}")
    print(f"Total citations: {result.total_citations}")
    for finding in result.findings:
        print(f"  - Iteration {finding.iteration}: {finding.query[:50]}...")
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

  # Research loop with multiple iterations
  python -m skills_fabric.retrievals.perplexity_client -q "Python async patterns" --loop --iterations 3

  # Output as JSON
  python -m skills_fabric.retrievals.perplexity_client -q "REST API best practices" --json

ENVIRONMENT:
  PERPLEXITY_API_KEY: Required API key from https://www.perplexity.ai/settings/api
"""
    )
    parser.add_argument("--query", "-q", help="Research query")
    parser.add_argument("--validate", help="Claim to validate")
    parser.add_argument("--academic", action="store_true", help="Focus on academic sources")
    parser.add_argument("--loop", action="store_true", help="Run research loop")
    parser.add_argument("--iterations", type=int, default=3, help="Max iterations for research loop")
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
