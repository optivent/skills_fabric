# Z.AI GLM Integration Guide

## Overview

The Skills Fabric leverages **Z.AI GLM-4.7** (via the Coding Plan API) for:
- Cost-effective skill generation (6x cheaper than Claude for extraction tasks)
- High-concurrency batch processing
- Vision capabilities (GLM-4.5V)
- Image generation (CogView-4)

---

## API Configuration

```python
# Base URLs
API_BASE = "https://api.z.ai/api/coding/paas/v4"
CHAT_ENDPOINT = f"{API_BASE}/chat/completions"
EMBEDDINGS_ENDPOINT = f"{API_BASE}/embeddings"
IMAGES_ENDPOINT = f"{API_BASE}/images/generations"

# Authentication
ZAI_API_KEY = os.environ.get("ZAI_API_KEY")
```

---

## Pricing (per 1M tokens)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| GLM-4.7 Chat | $0.60 | $2.20 | General purpose |
| GLM-4.7 Cached | $0.11 | $2.20 | 50% savings on input |
| GLM-4.5V Vision | $0.60 | $1.80 | Image understanding |
| Embeddings | $0.60 | N/A | Text embedding |
| CogView-4 | $0.01/image | N/A | Image generation |

---

## Basic Usage

### Chat Completion

```python
import requests

def call_glm(prompt: str, model: str = "GLM-4.7-128K") -> str:
    response = requests.post(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['ZAI_API_KEY']}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

### With Web Search

```python
def call_glm_with_search(query: str) -> str:
    response = requests.post(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['ZAI_API_KEY']}",
            "Content-Type": "application/json"
        },
        json={
            "model": "GLM-4.7-128K",
            "messages": [{"role": "user", "content": query}],
            "tools": [{"type": "web_search", "web_search": {"enable": True}}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

---

## Integration with Skills Fabric

### In `llm_client.py`

```python
from skills_fabric.generate.llm_client import LLMClient

client = LLMClient()  # Uses ZAI_API_KEY from env

# Generate a skill question
question = client.generate_question(
    concept="StateGraph",
    context="LangGraph state management"
)

# Generate skill code
code = client.generate(f"Write Python code to {question}")
```

---

## Model Selection Strategy

| Task | Recommended Model | Reason |
|------|-------------------|--------|
| Skill question generation | GLM-4.7-128K | Fast, cheap |
| Code generation | GLM-4.7-128K | Good at code |
| Documentation parsing | GLM-4.5V | Vision for diagrams |
| Batch extraction | GLM-4.7 (cached) | 50% cost savings |

---

## Oh-My-OpenCode Integration

The Skills Fabric can coordinate with **oh-my-opencode** agents:

### Agent Roles (from `~/.opencode/skill/`)

| Agent | Role | Integration |
|-------|------|-------------|
| **Sisyphus** | Lead Orchestrator | Coordinates skill generation pipeline |
| **Oracle** | Deep Auditor | Validates generated skills |
| **Librarian** | Context Manager | Manages CodeWiki/Context7 retrieval |
| **Explore** | Codebase Navigator | Maps symbol graphs |

### Coordination Pattern

```
User Request
    │
    ▼
Sisyphus (orchestrator)
    │
    ├──► Librarian: "Fetch docs for StateGraph"
    │         └── Returns: CodeWiki content with GitHub links
    │
    ├──► Explore: "Map StateGraph symbol graph"
    │         └── Returns: AST analysis, dependencies
    │
    ├──► GLM-4.7: "Generate skill from this context"
    │         └── Returns: Skill code and question
    │
    └──► Oracle: "Verify this skill in sandbox"
              └── Returns: Verification result
```

---

## Environment Variables

```bash
# Z.AI API Key (required)
export ZAI_API_KEY="your-zai-api-key"

# Alternative: Anthropic for fallback
export ANTHROPIC_API_KEY="your-anthropic-key"
```

---

## Files in Archive

| File | Purpose |
|------|---------|
| `zai_glm_integration/glm_api_client.py` | Full API client (38KB) |
| `zai_glm_integration/glm_research.py` | Research-oriented wrapper |
| `zai_glm_integration/model_router.py` | Intelligent model selection |

---

## Key Advantages

1. **Cost Efficiency**: 6x cheaper than Claude for extraction
2. **128K Context**: Large context window for full file analysis
3. **Web Search**: Built-in web search capability
4. **Vision**: Diagram and image understanding
5. **High Concurrency**: Handle batch skill generation
