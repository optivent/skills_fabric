"""
Skills Fabric Retrievals Module

Comprehensive retrieval tools for AI skill development:

1. PERPLEXITY (Research & Deep Research)
   - Sonar models with real-time web search
   - Domain filtering, recency control
   - Citations and related questions

2. BRAVE SEARCH (Web Search)
   - 30B+ page index
   - News, images, web results
   - Freshness and safety filtering

3. ARXIV (Academic Papers)
   - 2M+ paper database
   - Category-based search
   - Docling integration for PDF processing

4. BRIGHTDATA (Web Scraping)
   - JavaScript rendering
   - Anti-bot bypass
   - CodeWiki scraping

Usage:
    from retrievals import (
        # Perplexity
        PerplexityClient,
        deep_research,
        quick_search,

        # Brave Search
        BraveSearchClient,
        search as brave_search,
        news_search,

        # arXiv
        ArxivClient,
        search as arxiv_search,
        process_paper,

        # Brightdata
        BrightdataClient,
        scrape,
        scrape_codewiki,
    )

    # Deep research with Perplexity
    response = await deep_research("Latest advances in LLM agents")
    print(response.content)
    for citation in response.citations:
        print(f"  - {citation.url}")

    # Search arXiv and process papers
    papers = await arxiv_search("transformer attention", max_results=5)
    processed = await process_paper(papers[0])
    print(processed.markdown)
"""

# Perplexity
from .perplexity_client import (
    PerplexityClient,
    PerplexityConfig,
    PerplexityResponse,
    SonarModel,
    SearchRecency,
    SearchContextSize,
    Citation,
    search as perplexity_search,
    deep_research,
    quick_search,
)

# Brave Search
from .brave_search_client import (
    BraveSearchClient,
    BraveConfig,
    BraveSearchResponse,
    WebResult,
    NewsResult,
    ImageResult,
    SafeSearch,
    Freshness,
    search as brave_search,
    news_search,
    image_search,
)

# arXiv
from .arxiv_client import (
    ArxivClient,
    ArxivPaper,
    ProcessedPaper,
    Author,
    search as arxiv_search,
    get_paper,
    process_paper,
)

# Brightdata
from .brightdata_client import (
    BrightdataClient,
    BrightdataConfig,
    ScrapedPage,
    scrape,
    scrape_text,
    scrape_codewiki,
)

__all__ = [
    # Perplexity
    "PerplexityClient",
    "PerplexityConfig",
    "PerplexityResponse",
    "SonarModel",
    "SearchRecency",
    "SearchContextSize",
    "Citation",
    "perplexity_search",
    "deep_research",
    "quick_search",
    # Brave Search
    "BraveSearchClient",
    "BraveConfig",
    "BraveSearchResponse",
    "WebResult",
    "NewsResult",
    "ImageResult",
    "SafeSearch",
    "Freshness",
    "brave_search",
    "news_search",
    "image_search",
    # arXiv
    "ArxivClient",
    "ArxivPaper",
    "ProcessedPaper",
    "Author",
    "arxiv_search",
    "get_paper",
    "process_paper",
    # Brightdata
    "BrightdataClient",
    "BrightdataConfig",
    "ScrapedPage",
    "scrape",
    "scrape_text",
    "scrape_codewiki",
]
