# Skills Fabric Retrievals

Comprehensive retrieval tools for AI skill development and research.

## Tools Overview

| Tool | Purpose | Key Features |
|------|---------|--------------|
| **Perplexity** | Research & Deep Research | Real-time web, citations, F=0.858 factuality |
| **Brave Search** | Web Search | 30B+ pages, news, images, free tier |
| **arXiv** | Academic Papers | 2M+ papers, Docling processing |
| **Brightdata** | Web Scraping | JS rendering, anti-bot, CodeWiki |

## Quick Start

```bash
# Install dependencies
pip install httpx arxiv docling

# Set API keys
export PERPLEXITY_API_KEY="pplx-..."
export BRAVE_SEARCH_API_KEY="BSA..."
export BRIGHTDATA_API_KEY="user:pass"
```

## Usage Examples

### Perplexity Deep Research

```python
from retrievals import PerplexityClient, deep_research, SonarModel

client = PerplexityClient()

# Quick search
response = await client.quick_search("What is LangGraph?")

# Deep research with domain filtering
response = await client.deep_research(
    "Latest advances in agentic AI",
    domains=["arxiv.org", "github.com"],
    recency="month"
)

print(response.content)
for citation in response.citations:
    print(f"  - {citation.url}")
```

### Brave Search

```python
from retrievals import BraveSearchClient, Freshness

client = BraveSearchClient()

# Web search
results = await client.search("Python machine learning", count=10)
for result in results.web_results:
    print(f"{result.title}: {result.url}")

# News search (past week)
news = await client.news_search("AI technology", freshness=Freshness.WEEK)

# Image search
images = await client.image_search("neural network diagram")
```

### arXiv Papers

```python
from retrievals import ArxivClient

client = ArxivClient()

# Search papers
papers = await client.search("transformer attention", max_results=10)
for paper in papers:
    print(f"[{paper.id}] {paper.title}")
    print(f"  Authors: {', '.join(a.name for a in paper.authors[:3])}")

# Search by category
ai_papers = await client.search_category("cs.AI", days_back=7)

# Download and process with Docling
processed = await client.process_paper(papers[0])
print(processed.markdown)
print(f"Sections: {len(processed.sections)}")
print(f"References: {len(processed.references)}")
```

### Brightdata Web Scraping

```python
from retrievals import BrightdataClient

client = BrightdataClient()

# Scrape with JS rendering
page = await client.scrape("https://example.com/spa")
print(page.html)

# Extract text
text = await client.scrape_text("https://docs.example.com")

# Scrape CodeWiki
codewiki = await client.scrape_codewiki("langchain")
```

## API Reference Documents

- [PERPLEXITY_API_REFERENCE.md](./PERPLEXITY_API_REFERENCE.md) - Complete Perplexity API guide

## Directory Structure

```
retrievals/
├── __init__.py                  # Module exports
├── README.md                    # This file
├── PERPLEXITY_API_REFERENCE.md  # Perplexity complete guide
├── perplexity_client.py         # Perplexity Sonar API
├── brave_search_client.py       # Brave Search API
├── arxiv_client.py              # arXiv + Docling
└── brightdata_client.py         # Brightdata Web Unlocker
```

## Configuration

### Environment Variables

```bash
# Perplexity (Required for research)
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxx

# Brave Search (Required for web search)
BRAVE_SEARCH_API_KEY=BSAxxxxxxxxxxxxxxxxxxxx

# Brightdata (Optional, for JS scraping)
BRIGHTDATA_API_KEY=username:password
```

### Model Selection (Perplexity)

| Model | Cost | Use Case |
|-------|------|----------|
| `sonar` | $ | Quick lookups, simple Q&A |
| `sonar-pro` | $$ | Best factuality (F=0.858) |
| `sonar-reasoning` | $$$ | Complex reasoning |
| `sonar-deep-research` | $$$$ | Multi-step research |

## Best Practices

### Research Workflow

```python
# 1. Quick search for overview
overview = await quick_search("topic overview")

# 2. Deep research for details
details = await deep_research(
    "specific question about topic",
    domains=["authoritative-sources.com"],
    recency="week"
)

# 3. Academic papers for depth
papers = await arxiv_search("topic", max_results=5)
for paper in papers:
    processed = await process_paper(paper)
    # Extract key findings
```

### Cost Optimization

1. Use `sonar` for simple queries (3x cheaper)
2. Set `context_size="low"` when not needed
3. Use `search_recency_filter` to reduce noise
4. Cache frequent queries
5. Batch related questions

## Error Handling

```python
import httpx

try:
    response = await client.search(query)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        # Rate limited
        await asyncio.sleep(60)
        response = await client.search(query)
    elif e.response.status_code == 401:
        raise ValueError("Invalid API key")
```

## Integration with Skills Fabric

```python
from retrievals import deep_research
from skills_fabric.memory import AgentMemorySystem

# Initialize memory
memory = AgentMemorySystem(Path("./memory"))
memory.start_session("session_001", "Research task")

# Research
response = await deep_research("topic")

# Store in memory
memory.mirix.add_episodic("session_001", response.content)
for citation in response.citations:
    memory.mirix.add_semantic(citation.url, topic="research")
```

## Changelog

- **2026-01-06**: Initial release with Perplexity, Brave, arXiv, Brightdata
