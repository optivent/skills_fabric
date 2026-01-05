# Skills Fabric Quick Start

## Installation

```bash
# Clone repository
git clone https://github.com/optivent/skills_fabric
cd skills_fabric

# Install with dependencies
pip install -e .
```

## Prerequisites

- Python 3.11+
- Bubblewrap (`apt install bubblewrap`)
- API Key: `ZAI_API_KEY` for GLM-4.7 or `ANTHROPIC_API_KEY`

## Step 1: Initialize Database

```bash
python scripts/setup_db.py
```

This creates the KuzuDB schema with tables:
- `Concept`, `Symbol`, `Skill`, `TestResult`
- Relationships: `PROVEN`, `TEACHES`, `USES`, `VERIFIED_BY`

## Step 2: Clone Target Repository

```python
from skills_fabric.ingest.gitclone import GitCloner

cloner = GitCloner()
repo = cloner.clone("https://github.com/langchain-ai/langgraph")
print(f"Cloned to: {repo}")
```

## Step 3: Fetch Context7 Documentation

```python
from skills_fabric.ingest.context7 import Context7Client

c7 = Context7Client()

# Resolve library ID
lib_id = c7.resolve_library_id("langgraph")
print(f"Library ID: {lib_id}")

# Fetch and cache docs
cache = c7.fetch_and_cache("langgraph", "how to create StateGraph")
print(f"Cached to: {cache}")
```

## Step 4: Generate Skills

```bash
python scripts/generate_skills.py --repo langgraph
```

Or programmatically:

```python
from skills_fabric.generate.skill_factory import SkillFactory

factory = SkillFactory()
result = factory.run(library_name="langgraph")

print(f"Created {result[skills_created]} skills")
```

## Step 5: Query Skills

```python
from skills_fabric.store.kuzu_store import KuzuSkillStore

store = KuzuSkillStore()
skills = store.list_skills(limit=10)

for skill in skills:
    print(f"{skill.id}: {skill.question[:50]}...")
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ZAI_API_KEY` | GLM-4.7 API key |
| `ANTHROPIC_API_KEY` | Claude API key (alternative) |

## Full Pipeline

```
1. INGEST    → Clone repo, list files
2. ANALYZE   → AST parsing, symbol extraction
3. LINK      → Create PROVEN relationships
4. ENRICH    → Fetch Context7 docs
5. GENERATE  → GLM-4.7 question generation
6. VERIFY    → Bubblewrap sandbox test
7. STORE     → KuzuDB with relationships
```
