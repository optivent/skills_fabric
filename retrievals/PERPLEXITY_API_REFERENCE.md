# Perplexity API Complete Reference

> **Last Updated**: January 2026
> **Documentation**: https://docs.perplexity.ai/
> **API Endpoint**: `https://api.perplexity.ai`

## Quick Start

```python
from retrievals import PerplexityClient, deep_research, quick_search

# Initialize client
client = PerplexityClient()

# Quick search (fast, cheap)
response = await client.quick_search("What is LangGraph?")
print(response.content)

# Deep research (comprehensive, citations)
response = await client.deep_research(
    "Latest advances in agentic AI",
    domains=["arxiv.org", "github.com"],
    recency="month"
)
print(response.content)
for citation in response.citations:
    print(f"  - {citation.url}")
```

---

## Models

| Model | Use Case | Context | Pricing |
|-------|----------|---------|---------|
| `sonar` | Quick searches, Q&A | 128K | $1/M in, $1/M out |
| `sonar-pro` | Best factuality (F=0.858) | 200K | $3/M in, $15/M out |
| `sonar-reasoning` | Reasoning chains | 128K | Higher |
| `sonar-reasoning-pro` | Advanced reasoning | 128K | Higher |
| `sonar-deep-research` | Multi-step research | 128K | Highest |

### Model Selection Guide

```python
from retrievals import SonarModel

# Quick lookup - use sonar (fastest, cheapest)
model = SonarModel.SONAR

# Factual accuracy needed - use sonar-pro (F-score 0.858)
model = SonarModel.SONAR_PRO

# Complex reasoning - use sonar-reasoning-pro
model = SonarModel.SONAR_REASONING_PRO

# Deep multi-step research - use sonar-deep-research
model = SonarModel.SONAR_DEEP_RESEARCH
```

---

## API Parameters

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `sonar-pro` | Model to use |
| `messages` | array | required | Conversation messages |
| `temperature` | float | 0.2 | Sampling temperature (0-2) |
| `top_p` | float | 0.9 | Nucleus sampling |
| `max_tokens` | int | 4096 | Max response tokens |
| `stream` | bool | false | Enable streaming |

### Search Parameters

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `search_recency_filter` | string | `hour`, `day`, `week`, `month` | Filter by time |
| `search_context_size` | string | `low`, `medium`, `high` | Context amount |
| `search_domain_filter` | array | Max 20 domains | Domain allow/deny list |

### Response Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `return_citations` | bool | true | Include source URLs |
| `return_images` | bool | false | Include images (Tier-2+) |
| `return_related_questions` | bool | false | Include related questions |

---

## Search Recency Filter

Filter results by when they were discovered:

```python
from retrievals import SearchRecency

# Only results from past hour
response = await client.search(query, recency=SearchRecency.HOUR)

# Only results from past day
response = await client.search(query, recency=SearchRecency.DAY)

# Only results from past week
response = await client.search(query, recency=SearchRecency.WEEK)

# Only results from past month
response = await client.search(query, recency=SearchRecency.MONTH)
```

---

## Search Domain Filter

Control which domains are searched. **Maximum 20 domains**.

### Allowlist Mode (Include Only)

```python
# Only search these domains
response = await client.search(
    "transformer architecture",
    domains=["arxiv.org", "github.com", "huggingface.co"]
)
```

### Denylist Mode (Exclude)

```python
# Exclude these domains
response = await client.search(
    "AI news",
    exclude_domains=["reddit.com", "twitter.com"]
)
```

**Important**: Cannot use both allowlist and denylist simultaneously.

---

## Search Context Size

Control the amount of search context included:

```python
from retrievals import SearchContextSize

# LOW: Minimize context, lower cost, less comprehensive
response = await client.search(query, context_size=SearchContextSize.LOW)

# MEDIUM: Balanced (default)
response = await client.search(query, context_size=SearchContextSize.MEDIUM)

# HIGH: Maximum context, higher cost, most comprehensive
response = await client.search(query, context_size=SearchContextSize.HIGH)
```

---

## Complete Usage Examples

### 1. Quick Fact Check

```python
response = await client.quick_search("What is the capital of Japan?")
print(response.content)
# Tokyo
```

### 2. Research with Citations

```python
response = await client.search(
    "What are the key differences between GPT-4 and Claude?",
    model=SonarModel.SONAR_PRO,
    return_citations=True,
    return_related_questions=True,
)

print(response.content)
print("\nSources:")
for citation in response.citations:
    print(f"  - {citation.url}")

print("\nRelated Questions:")
for question in response.related_questions:
    print(f"  - {question}")
```

### 3. Time-Filtered Search

```python
# Only news from the past week
response = await client.search(
    "AI regulation news",
    recency=SearchRecency.WEEK,
    return_citations=True,
)
```

### 4. Domain-Specific Research

```python
# Only academic sources
response = await client.search(
    "attention mechanism neural networks",
    domains=["arxiv.org", "paperswithcode.com", "nature.com"],
    context_size=SearchContextSize.HIGH,
)
```

### 5. Deep Research Mode

```python
response = await client.deep_research(
    "What are the latest advances in multi-agent AI systems?",
    domains=["arxiv.org", "github.com"],
    recency=SearchRecency.MONTH,
)

# Returns comprehensive analysis with citations
print(response.content)
print(f"Citations: {len(response.citations)}")
```

### 6. Streaming Response

```python
async for chunk in client.stream("Explain quantum computing"):
    print(chunk, end="", flush=True)
print()  # Newline at end
```

### 7. Reasoning Mode

```python
response = await client.reasoning_search(
    "Should I use LangGraph or AutoGen for building agents?"
)
# Returns step-by-step reasoning with conclusion
```

---

## Response Structure

```python
@dataclass
class PerplexityResponse:
    content: str                    # Main response text
    model: str                      # Model used
    citations: List[Citation]       # Source URLs
    images: List[str]               # Image URLs (if enabled)
    related_questions: List[str]    # Related questions (if enabled)
    usage: Dict[str, int]           # Token usage stats
    raw_response: Dict[str, Any]    # Full API response

@dataclass
class Citation:
    url: str
    title: str = ""
    snippet: str = ""
```

---

## Error Handling

```python
try:
    response = await client.search(query)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        print("Rate limited - wait and retry")
    elif e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 400:
        print("Invalid request parameters")
except Exception as e:
    print(f"Error: {e}")
```

---

## Rate Limits & Tiers

| Tier | Queries/Minute | Features |
|------|----------------|----------|
| Free | 5 | Basic search |
| Tier-1 | 50 | + Domain filter |
| Tier-2 | 200 | + Images, JSON mode |
| Enterprise | Custom | Full features |

---

## Cost Optimization Tips

1. **Use `sonar` for simple queries** - 3x cheaper than `sonar-pro`
2. **Set `context_size="low"`** when detailed context isn't needed
3. **Use `search_recency_filter`** to reduce irrelevant results
4. **Cache responses** for frequently asked questions
5. **Batch related queries** into single comprehensive questions

---

## Environment Setup

```bash
# Set API key
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxx"

# Verify
python -c "from retrievals import PerplexityClient; print('OK')"
```

---

## Integration with Skills Fabric

```python
from retrievals import deep_research
from skills_fabric.memory import AgentMemorySystem

# Research with memory integration
memory = AgentMemorySystem(Path("./memory"))
memory.start_session("research_001", "AI agents research")

# Perform research
response = await deep_research("Multi-agent AI architectures")

# Store findings in episodic memory
memory.mirix.add_episodic(
    "research_001",
    f"Research findings: {response.content[:500]}",
    {"citations": len(response.citations)}
)

# Store key facts in semantic memory
for citation in response.citations:
    memory.mirix.add_semantic(
        f"Source: {citation.url}",
        topic="multi-agent AI"
    )
```

---

## Comparison: Perplexity vs Other Tools

| Feature | Perplexity | Brave Search | Web Search |
|---------|------------|--------------|------------|
| Real-time data | ✅ | ✅ | ✅ |
| Citations | ✅ Native | ❌ Manual | ❌ |
| Summarization | ✅ LLM | ❌ | ❌ |
| Deep research | ✅ Multi-step | ❌ | ❌ |
| Cost | $$ | $ | Free |
| Factuality | F=0.858 | N/A | N/A |

**Use Perplexity when**: You need summarized, cited answers with high factuality.

**Use Brave Search when**: You need raw search results for custom processing.

---

## Changelog

- **2026-01**: Added `sonar-deep-research` model
- **2025-11**: Added `search_context_size` parameter
- **2025-09**: Added `return_related_questions` parameter
