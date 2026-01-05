# Skills Fabric 🧵

**Zero-hallucination Claude skill generation pipeline**

Generate high-quality Claude skills grounded in real source code, documentation, and verified examples.

## Features

- **CodeWiki Integration**: Scrape and split documentation into concepts
- **Git Repository Analysis**: Clone repos, parse with AST/Tree-sitter
- **PROVEN Linking**: Match documentation concepts to source code symbols
- **Context7 API**: Fetch up-to-date library documentation
- **LLM Skill Generation**: Generate questions via GLM-4.7 or Claude
- **Bubblewrap Sandbox**: Safe code execution for testing
- **KuzuDB Storage**: Graph database for skills and relationships

## Architecture

```
CodeWiki Docs    Git Repository    Context7 API
      │               │                 │
      └───────────────┼─────────────────┘
                      ▼
              ┌───────────────┐
              │   Ingest      │
              │ (scrape/clone)│
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │   Analyze     │
              │ (AST/NER)     │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │    Link       │
              │ (PROVEN)      │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │   Generate    │
              │ (LangGraph)   │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │   Verify      │
              │ (Bubblewrap)  │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │    Store      │
              │  (KuzuDB)     │
              └───────────────┘
```

## Quick Start

```bash
# Install
pip install -e .

# Initialize database
python scripts/setup_db.py

# Generate skills from a repository
python scripts/generate_skills.py --repo https://github.com/langchain-ai/langgraph

# Run tests
pytest tests/
```

## Requirements

- Python 3.11+
- Bubblewrap (bwrap) for sandbox execution
- KuzuDB for graph storage
- API keys: ZAI_API_KEY (GLM-4.7) or ANTHROPIC_API_KEY

## License

MIT
