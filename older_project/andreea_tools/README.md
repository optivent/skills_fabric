# Andreea Tools Archive

## Source: /Users/aig/Andreea_Schmitz/tools

Advanced research and LLM orchestration tools relevant to the Progressive Iceberg goal.

---

## Contents

### discovery/
| File | Size | Purpose |
|------|------|---------|
| `arxiv_client.py` | 13KB | ArXiv paper search API |
| `brave_client.py` | 14KB | Brave web search API |
| `semantic_scholar_api.py` | 10KB | Academic paper search |
| `glm_research.py` | 6KB | GLM-oriented research wrapper |

### research/
| File | Size | Purpose |
|------|------|---------|
| `deep_research.py` | 15KB | LangGraph-based autonomous research agent |

### embeddings/
| File | Size | Purpose |
|------|------|---------|
| `vector_store.py` | 24KB | Hybrid search (sentence-transformers + tantivy) |

### zai_sdk/
| File | Size | Purpose |
|------|------|---------|
| `_client.py` | 8KB | Z.AI SDK main client |
| `cost_tracker.py` | 3KB | Token and cost tracking |

### Root
| File | Size | Purpose |
|------|------|---------|
| `model_router.py` | 9KB | Multi-model orchestration (Gemini + GLM) |

---

## Relevance to Progressive Iceberg

| Iceberg Layer | Tool | Application |
|---------------|------|-------------|
| Surface (1) | `brave_client.py`, `semantic_scholar_api.py` | Additional search sources |
| Structure (2) | `vector_store.py` | Local embedding-based linking |
| Behavior (3) | `deep_research.py` | Iterative verification pattern |
| Navigation (4) | `model_router.py` | Cost-efficient model selection |
| Foundation (5) | `zai_sdk/` | Robust API client |

---

## Key Patterns

### Model Routing (model_router.py)
```python
class TaskType(Enum):
    PICO_EXTRACTION = "pico"     # → Gemini (low hallucination)
    SYNTHESIZE = "synthesize"    # → GLM-4.7 (deep reasoning)
    VERIFY = "verify"            # → Multi-model consensus
```

### Deep Research (deep_research.py)
```python
# LangGraph state machine:
# Plan → Search (S2/ArXiv/Brave) → Curate → Synthesize → Verify → Iterate
```

### Hybrid Vector Store (vector_store.py)
```python
# Combines:
# - Dense: sentence-transformers (all-mpnet-base-v2)
# - Sparse: tantivy BM25
# - Clustering: sklearn KMeans
```
