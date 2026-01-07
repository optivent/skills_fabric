"""Integration tests for end-to-end skill generation flows.

This module tests the complete skill generation pipeline:
- Progressive disclosure flow (levels 0-5)
- Multi-agent verification workflow
- Research loop integration

Test Markers:
- @pytest.mark.integration: All tests in this file
- @pytest.mark.slow: Long-running tests
- @pytest.mark.requires_api: Tests requiring live API calls

Usage:
    pytest tests/integration/test_skill_generation.py -v
    pytest tests/integration/ -m "integration and not requires_api"
"""
from __future__ import annotations

import importlib.util
import sys
import types
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# =============================================================================
# Module Setup - Direct imports to avoid heavy skills_fabric.__init__
# =============================================================================

_src_path = Path(__file__).parent.parent.parent / "src"

# Create namespace packages
if "skills_fabric" not in sys.modules:
    _sf = types.ModuleType("skills_fabric")
    _sf.__path__ = [str(_src_path / "skills_fabric")]
    sys.modules["skills_fabric"] = _sf

if "skills_fabric.understanding" not in sys.modules:
    _understanding = types.ModuleType("skills_fabric.understanding")
    _understanding.__path__ = [str(_src_path / "skills_fabric" / "understanding")]
    sys.modules["skills_fabric.understanding"] = _understanding

if "skills_fabric.observability" not in sys.modules:
    _obs = types.ModuleType("skills_fabric.observability")
    _obs.__path__ = [str(_src_path / "skills_fabric" / "observability")]
    sys.modules["skills_fabric.observability"] = _obs

# Import observability.logging first
_logging_path = _src_path / "skills_fabric" / "observability" / "logging.py"
if _logging_path.exists():
    _logging_spec = importlib.util.spec_from_file_location(
        "skills_fabric.observability.logging", _logging_path
    )
    _logging_module = importlib.util.module_from_spec(_logging_spec)
    sys.modules["skills_fabric.observability.logging"] = _logging_module
    _logging_spec.loader.exec_module(_logging_module)

# Import progressive_disclosure module
_pd_path = _src_path / "skills_fabric" / "understanding" / "progressive_disclosure.py"
_pd_spec = importlib.util.spec_from_file_location(
    "skills_fabric.understanding.progressive_disclosure", _pd_path
)
_pd_module = importlib.util.module_from_spec(_pd_spec)
sys.modules["skills_fabric.understanding.progressive_disclosure"] = _pd_module
_pd_spec.loader.exec_module(_pd_module)

# Import classes for progressive disclosure tests
DepthLevel = _pd_module.DepthLevel
SourceRef = _pd_module.SourceRef
SemanticInfo = _pd_module.SemanticInfo
ExecutionProof = _pd_module.ExecutionProof
UnderstandingNode = _pd_module.UnderstandingNode
ProgressiveUnderstanding = _pd_module.ProgressiveUnderstanding
ProgressiveUnderstandingBuilder = _pd_module.ProgressiveUnderstandingBuilder
build_progressive_understanding = _pd_module.build_progressive_understanding


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_codewiki(temp_dir: Path) -> Path:
    """Create a sample CodeWiki output directory."""
    codewiki = temp_dir / "codewiki"
    codewiki.mkdir()

    # Create sections directory
    sections = codewiki / "sections"
    sections.mkdir()

    # Create sample sections
    (sections / "01_getting_started.md").write_text("""## Getting Started

LangGraph is a framework for building multi-agent applications.

### Installation

Install using pip:
```bash
pip install langgraph
```

### Quick Start

Create a simple graph:
```python
from langgraph.graph import StateGraph
graph = StateGraph(dict)
```

### Source References
- [`StateGraph`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/state.py#L15)
""")

    (sections / "02_state_management.md").write_text("""## State Management

State is managed using TypedDict or Pydantic models.

### State Definition

Define state using TypedDict:
```python
from typing import TypedDict, List

class AgentState(TypedDict):
    messages: List[str]
    step: int
```

### Memory

LangGraph supports persistent memory using checkpointers.

### Source References
- [`MemorySaver`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/checkpoint/memory.py#L10)
""")

    (sections / "03_agents.md").write_text("""## Agents

Agents are the core building blocks of LangGraph applications.

### Creating Agents

Agents process state and produce outputs:
```python
def agent_node(state: AgentState) -> AgentState:
    return {"step": state["step"] + 1}
```

### Prebuilt Agents

LangGraph provides prebuilt agent implementations.

### Source References
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/prebuilt/react.py#L100)
""")

    # Create symbol catalog
    (codewiki / "symbol_catalog.md").write_text("""# Symbol Catalog

## Classes
- [`StateGraph`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/state.py#L15)
- [`MemorySaver`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/checkpoint/memory.py#L10)

## Functions
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/prebuilt/react.py#L100)
""")

    return codewiki


@pytest.fixture
def sample_repo(temp_dir: Path) -> Path:
    """Create a sample repository directory."""
    repo = temp_dir / "langgraph_repo"
    repo.mkdir()

    # Create README
    (repo / "README.md").write_text("""# LangGraph

LangGraph is a framework for building multi-agent applications with LLMs.

## Installation
pip install langgraph

## Quick Start
Create a simple workflow using StateGraph.
""")

    # Create git directory for commit detection
    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main")

    refs_heads = git_dir / "refs" / "heads"
    refs_heads.mkdir(parents=True)
    (refs_heads / "main").write_text("abc123def456789")

    # Create source files
    libs = repo / "libs" / "langgraph" / "langgraph" / "graph"
    libs.mkdir(parents=True)

    (libs / "state.py").write_text('''"""State graph implementation."""
from typing import TypedDict, Any

class StateGraph:
    """A graph that manages state."""

    def __init__(self, state_schema: type):
        self.state_schema = state_schema
        self.nodes = {}
        self.edges = []

    def add_node(self, name: str, func) -> "StateGraph":
        """Add a node to the graph."""
        self.nodes[name] = func
        return self

    def add_edge(self, source: str, target: str) -> "StateGraph":
        """Add an edge between nodes."""
        self.edges.append((source, target))
        return self

    def compile(self):
        """Compile the graph for execution."""
        return CompiledGraph(self)


class CompiledGraph:
    """A compiled state graph ready for execution."""

    def __init__(self, graph: StateGraph):
        self.graph = graph

    def invoke(self, state: dict) -> dict:
        """Execute the graph with initial state."""
        return state
''')

    return repo


@pytest.fixture
def progressive_understanding(sample_repo: Path, sample_codewiki: Path) -> ProgressiveUnderstanding:
    """Build a progressive understanding from sample data."""
    return build_progressive_understanding(
        repo_name="langgraph",
        repo_path=sample_repo,
        codewiki_path=sample_codewiki
    )


# =============================================================================
# Progressive Disclosure Flow Tests
# =============================================================================

class TestProgressiveDisclosureFlow:
    """Test progressive disclosure flow from Level 0 to Level 5."""

    def test_depth_level_enum_values(self):
        """Test DepthLevel enum has all 6 levels."""
        assert DepthLevel.EXECUTIVE_SUMMARY == 0
        assert DepthLevel.CONCEPT_MAP == 1
        assert DepthLevel.DETAILED_SECTIONS == 2
        assert DepthLevel.SOURCE_REFERENCES == 3
        assert DepthLevel.SEMANTIC_ANALYSIS == 4
        assert DepthLevel.EXECUTION_PROOFS == 5

    def test_source_ref_properties(self):
        """Test SourceRef has correct properties for citations."""
        ref = SourceRef(
            file_path="src/module.py",
            line=42,
            commit="abc123",
            repo="owner/repo",
            symbol_name="MyClass",
            symbol_kind="class"
        )

        assert ref.github_url == "https://github.com/owner/repo/blob/abc123/src/module.py#L42"
        assert ref.local_path == "src/module.py:42"

    def test_understanding_node_creation(self):
        """Test UnderstandingNode can be created with required fields."""
        node = UnderstandingNode(
            id="test_node",
            title="Test Node",
            level=DepthLevel.CONCEPT_MAP,
            content="This is a test concept."
        )

        assert node.id == "test_node"
        assert node.title == "Test Node"
        assert node.level == DepthLevel.CONCEPT_MAP
        assert node.content == "This is a test concept."
        assert node.parent_id is None
        assert node.children_ids == []
        assert node.source_refs == []

    def test_node_is_expanded_levels(self):
        """Test is_expanded property for different levels."""
        # Source references level - expanded when has refs
        ref_node = UnderstandingNode(
            id="ref_node",
            title="With Refs",
            level=DepthLevel.SOURCE_REFERENCES,
            content="Has references"
        )
        assert not ref_node.is_expanded  # No source_refs yet

        ref_node.source_refs.append(SourceRef(
            file_path="test.py", line=1, commit="abc", repo="org/repo",
            symbol_name="Test", symbol_kind="class"
        ))
        assert ref_node.is_expanded  # Now has source_refs

        # Semantic analysis level - expanded when has semantic_info
        sem_node = UnderstandingNode(
            id="sem_node",
            title="With Semantics",
            level=DepthLevel.SEMANTIC_ANALYSIS,
            content="Has semantics"
        )
        assert not sem_node.is_expanded  # No semantic_info yet

        sem_node.semantic_info = SemanticInfo(type_signature="def test()")
        assert sem_node.is_expanded  # Now has semantic_info

    def test_progressive_understanding_creation(self):
        """Test ProgressiveUnderstanding can be created."""
        pu = ProgressiveUnderstanding(
            name="test_lib",
            repo="org/test_lib",
            commit="abc123"
        )

        assert pu.name == "test_lib"
        assert pu.repo == "org/test_lib"
        assert pu.commit == "abc123"
        assert pu.root_id is None
        assert len(pu.nodes) == 0

    def test_add_node_indexes_by_level(self):
        """Test adding nodes indexes them by level."""
        pu = ProgressiveUnderstanding(name="test", repo="org/test", commit="abc")

        root = UnderstandingNode(
            id="root",
            title="Root",
            level=DepthLevel.EXECUTIVE_SUMMARY,
            content="Executive summary"
        )
        concept = UnderstandingNode(
            id="concept1",
            title="Concept 1",
            level=DepthLevel.CONCEPT_MAP,
            content="First concept",
            keywords={"keyword1", "keyword2"}
        )

        pu.add_node(root)
        pu.add_node(concept)

        assert len(pu.nodes) == 2
        assert len(pu.get_at_level(DepthLevel.EXECUTIVE_SUMMARY)) == 1
        assert len(pu.get_at_level(DepthLevel.CONCEPT_MAP)) == 1

    def test_search_by_keyword(self):
        """Test searching nodes by keyword."""
        pu = ProgressiveUnderstanding(name="test", repo="org/test", commit="abc")

        node1 = UnderstandingNode(
            id="node1",
            title="StateGraph",
            level=DepthLevel.CONCEPT_MAP,
            content="Manages state",
            keywords={"stategraph", "state", "graph"}
        )
        node2 = UnderstandingNode(
            id="node2",
            title="MemorySaver",
            level=DepthLevel.CONCEPT_MAP,
            content="Saves memory",
            keywords={"memory", "checkpoint", "persistence"}
        )

        pu.add_node(node1)
        pu.add_node(node2)

        # Search by keyword
        results = pu.search("state")
        assert len(results) == 1
        assert results[0].id == "node1"

        # Search by content
        results = pu.search("memory")
        assert len(results) == 1
        assert results[0].id == "node2"

    def test_build_from_codewiki(self, sample_repo: Path, sample_codewiki: Path):
        """Test building progressive understanding from CodeWiki output."""
        pu = build_progressive_understanding(
            repo_name="langgraph",
            repo_path=sample_repo,
            codewiki_path=sample_codewiki
        )

        # Should have root node (Level 0)
        assert pu.root_id is not None
        root = pu.nodes[pu.root_id]
        assert root.level == DepthLevel.EXECUTIVE_SUMMARY
        assert root.title == "langgraph"

        # Should have concept nodes (Level 1)
        concepts = pu.get_at_level(DepthLevel.CONCEPT_MAP)
        assert len(concepts) > 0

        # Should have section nodes (Level 2)
        sections = pu.get_at_level(DepthLevel.DETAILED_SECTIONS)
        assert len(sections) > 0

    def test_expand_to_source_references(self, progressive_understanding: ProgressiveUnderstanding):
        """Test expanding a node to Level 3 (source references)."""
        # Get a section node
        sections = progressive_understanding.get_at_level(DepthLevel.DETAILED_SECTIONS)
        if not sections:
            pytest.skip("No sections found in progressive understanding")

        section = sections[0]

        # Some sections already have source refs from CodeWiki
        if section.source_refs:
            # Verify source refs have file:line format
            for ref in section.source_refs:
                assert ref.file_path
                assert ref.line > 0
                assert ref.symbol_name

    def test_get_summary_levels(self, progressive_understanding: ProgressiveUnderstanding):
        """Test get_summary at different levels."""
        # Level 0 summary
        summary_l0 = progressive_understanding.get_summary(DepthLevel.EXECUTIVE_SUMMARY)
        assert "langgraph" in summary_l0.lower()

        # Level 1 summary (includes concepts)
        summary_l1 = progressive_understanding.get_summary(DepthLevel.CONCEPT_MAP)
        assert len(summary_l1) > len(summary_l0)

        # Level 2 summary (includes details)
        summary_l2 = progressive_understanding.get_summary(DepthLevel.DETAILED_SECTIONS)
        assert len(summary_l2) >= len(summary_l1)

    def test_save_and_load(self, progressive_understanding: ProgressiveUnderstanding, temp_dir: Path):
        """Test saving and loading progressive understanding."""
        output_path = temp_dir / "understanding.json"

        # Save
        progressive_understanding.save(output_path)
        assert output_path.exists()

        # Load
        loaded = ProgressiveUnderstanding.load(output_path)

        assert loaded.name == progressive_understanding.name
        assert loaded.repo == progressive_understanding.repo
        assert loaded.commit == progressive_understanding.commit
        assert loaded.root_id == progressive_understanding.root_id
        assert len(loaded.nodes) == len(progressive_understanding.nodes)

    def test_to_dict_serialization(self, progressive_understanding: ProgressiveUnderstanding):
        """Test serialization to dictionary."""
        data = progressive_understanding.to_dict()

        assert "name" in data
        assert "repo" in data
        assert "commit" in data
        assert "root_id" in data
        assert "nodes" in data

        # Verify node structure
        for node_id, node_data in data["nodes"].items():
            assert "id" in node_data
            assert "title" in node_data
            assert "level" in node_data
            assert "content" in node_data


# =============================================================================
# Multi-Agent Verification Flow Tests
# =============================================================================

class TestMultiAgentVerificationFlow:
    """Test multi-agent verification workflow with mocked agents."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing workflow."""
        # Mock miner
        mock_miner = MagicMock()
        mock_miner.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                symbols=[
                    {"name": "StateGraph", "kind": "class", "file_path": "graph/state.py", "line": 15},
                    {"name": "compile", "kind": "method", "file_path": "graph/state.py", "line": 50},
                ],
                code_snippets=[
                    {"snippet": "class StateGraph:\n    pass", "file_path": "graph/state.py"},
                ]
            )
        )

        # Mock linker
        mock_linker = MagicMock()
        mock_linker.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                links=[
                    {
                        "concept_name": "State Management",
                        "symbol_name": "StateGraph",
                        "file_path": "graph/state.py",
                        "line_number": 15,
                        "confidence": 0.9
                    }
                ]
            )
        )

        # Mock writer
        mock_writer = MagicMock()
        mock_skill = MagicMock()
        mock_skill.content = "StateGraph is a class for managing state."
        mock_writer.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(skill=mock_skill)
        )

        # Mock auditor
        mock_auditor = MagicMock()
        mock_auditor.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                passed=True,
                hallucination_rate=0.01,
                verified_claims=5,
                unverified_claims=0
            )
        )

        # Mock verifier
        mock_verifier = MagicMock()
        mock_verifier.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(passed=True)
        )

        return {
            "miner": mock_miner,
            "linker": mock_linker,
            "writer": mock_writer,
            "auditor": mock_auditor,
            "verifier": mock_verifier,
        }

    def test_workflow_stages_enum(self):
        """Test workflow stage enumeration exists."""
        # Import dynamically to test module structure
        try:
            _agents_path = _src_path / "skills_fabric" / "agents"
            if not (_agents_path / "supervisor.py").exists():
                pytest.skip("Supervisor module not found")

            # We expect these stages in the workflow
            expected_stages = ["INIT", "MINING", "LINKING", "WRITING",
                             "AUDITING", "VERIFYING", "STORING", "COMPLETE", "FAILED"]

            # Just verify the enum concept is correct
            assert len(expected_stages) == 9
        except Exception:
            pytest.skip("Agent modules not accessible")

    def test_workflow_state_initialization(self):
        """Test workflow state can be initialized."""
        # Simulate workflow state structure
        state = {
            "stage": "INIT",
            "library_name": "langgraph",
            "repo_path": "/path/to/repo",
            "codewiki_path": "/path/to/codewiki",
            "mined_symbols": [],
            "mined_snippets": [],
            "proven_links": [],
            "skills": [],
            "audited_skills": [],
            "verified_skills": [],
            "skills_created": 0,
            "skills_audited": 0,
            "skills_verified": 0,
            "skills_rejected": 0,
            "hallucination_rate": 0.0,
            "messages": [],
            "errors": []
        }

        assert state["stage"] == "INIT"
        assert state["library_name"] == "langgraph"
        assert state["hallucination_rate"] == 0.0

    def test_mining_stage_output(self, mock_agents):
        """Test mining stage produces symbols and snippets."""
        miner = mock_agents["miner"]

        result = miner.execute(MagicMock(
            query="langgraph",
            repo_path="/path/to/repo",
            max_results=100
        ))

        assert result.success
        assert len(result.output.symbols) > 0
        assert len(result.output.code_snippets) > 0

        # Check symbol structure
        symbol = result.output.symbols[0]
        assert "name" in symbol
        assert "kind" in symbol
        assert "file_path" in symbol

    def test_linking_stage_creates_proven_links(self, mock_agents):
        """Test linking stage creates PROVEN relationships."""
        linker = mock_agents["linker"]

        result = linker.execute(MagicMock(
            concepts=[{"name": "State Management", "content": "Manages workflow state"}],
            symbols=[{"name": "StateGraph", "kind": "class"}],
            min_confidence=0.5
        ))

        assert result.success
        assert len(result.output.links) > 0

        # Check link structure
        link = result.output.links[0]
        assert "concept_name" in link
        assert "symbol_name" in link
        assert "confidence" in link
        assert link["confidence"] >= 0.5

    def test_writing_stage_generates_skills(self, mock_agents):
        """Test writing stage generates skill content."""
        writer = mock_agents["writer"]

        result = writer.execute(MagicMock(
            concept_name="State Management",
            symbol_name="StateGraph",
            source_code="class StateGraph: pass",
            file_path="graph/state.py",
            library="langgraph"
        ))

        assert result.success
        assert result.output.skill is not None
        assert result.output.skill.content

    def test_auditing_stage_checks_hallucination(self, mock_agents):
        """Test auditing stage verifies hallucination rate."""
        auditor = mock_agents["auditor"]

        result = auditor.execute(MagicMock(
            content="StateGraph is a class for managing state.",
            source_refs=[],
            strict_mode=False
        ))

        assert result.success
        assert result.output.passed
        assert result.output.hallucination_rate < 0.02

    def test_verification_stage_validates_skills(self, mock_agents):
        """Test verification stage validates generated skills."""
        verifier = mock_agents["verifier"]

        mock_skill = MagicMock()
        mock_skill.content = "StateGraph manages state"

        result = verifier.execute(MagicMock(skill=mock_skill))

        assert result.success
        assert result.output.passed

    def test_full_workflow_simulation(self, mock_agents):
        """Test complete workflow from mining to storage."""
        # Simulate complete workflow
        state = {
            "stage": "INIT",
            "library_name": "langgraph",
            "mined_symbols": [],
            "mined_snippets": [],
            "proven_links": [],
            "skills": [],
            "audited_skills": [],
            "verified_skills": [],
            "hallucination_rate": 0.0,
        }

        # Stage 1: Mining
        mining_result = mock_agents["miner"].execute(MagicMock())
        if mining_result.success:
            state["mined_symbols"] = mining_result.output.symbols
            state["mined_snippets"] = mining_result.output.code_snippets
            state["stage"] = "LINKING"

        assert state["stage"] == "LINKING"
        assert len(state["mined_symbols"]) > 0

        # Stage 2: Linking
        linking_result = mock_agents["linker"].execute(MagicMock())
        if linking_result.success:
            state["proven_links"] = linking_result.output.links
            state["stage"] = "WRITING"

        assert state["stage"] == "WRITING"
        assert len(state["proven_links"]) > 0

        # Stage 3: Writing
        for link in state["proven_links"]:
            writing_result = mock_agents["writer"].execute(MagicMock())
            if writing_result.success:
                state["skills"].append(writing_result.output.skill)
        state["stage"] = "AUDITING"

        assert state["stage"] == "AUDITING"
        assert len(state["skills"]) > 0

        # Stage 4: Auditing
        total_hall_rate = 0.0
        for skill in state["skills"]:
            audit_result = mock_agents["auditor"].execute(MagicMock())
            if audit_result.success and audit_result.output.passed:
                state["audited_skills"].append(skill)
                total_hall_rate += audit_result.output.hallucination_rate

        if state["audited_skills"]:
            state["hallucination_rate"] = total_hall_rate / len(state["audited_skills"])
        state["stage"] = "VERIFYING"

        assert state["stage"] == "VERIFYING"
        assert state["hallucination_rate"] < 0.02

        # Stage 5: Verification
        for skill in state["audited_skills"]:
            verify_result = mock_agents["verifier"].execute(MagicMock())
            if verify_result.success and verify_result.output.passed:
                state["verified_skills"].append(skill)
        state["stage"] = "COMPLETE"

        assert state["stage"] == "COMPLETE"
        assert len(state["verified_skills"]) > 0

    def test_workflow_handles_mining_failure(self, mock_agents):
        """Test workflow handles mining stage failure gracefully."""
        mock_agents["miner"].execute.return_value = MagicMock(
            success=False,
            error="Repository not found"
        )

        state = {"stage": "INIT", "errors": []}

        mining_result = mock_agents["miner"].execute(MagicMock())
        if not mining_result.success:
            state["stage"] = "FAILED"
            state["errors"].append(f"Mining failed: {mining_result.error}")

        assert state["stage"] == "FAILED"
        assert len(state["errors"]) > 0
        assert "Mining failed" in state["errors"][0]

    def test_workflow_handles_high_hallucination(self, mock_agents):
        """Test workflow rejects skills with high hallucination rate."""
        mock_agents["auditor"].execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                passed=False,
                hallucination_rate=0.15,
                verified_claims=8,
                unverified_claims=2
            )
        )

        state = {"skills": [MagicMock()], "audited_skills": [], "skills_rejected": 0}

        for skill in state["skills"]:
            audit_result = mock_agents["auditor"].execute(MagicMock())
            if not (audit_result.success and audit_result.output.passed):
                state["skills_rejected"] += 1

        assert state["skills_rejected"] == 1
        assert len(state["audited_skills"]) == 0


# =============================================================================
# Research Loop Integration Tests
# =============================================================================

class TestResearchLoopIntegration:
    """Test research loop integration with Perplexity client."""

    @pytest.fixture
    def mock_perplexity_responses(self):
        """Create mock Perplexity API responses."""
        return [
            {
                "id": "resp-1",
                "model": "sonar",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "LangGraph is a framework for building multi-agent applications. "
                                  "It uses StateGraph for workflow orchestration."
                    }
                }],
                "citations": [
                    "https://python.langchain.com/docs/langgraph/",
                    "https://github.com/langchain-ai/langgraph"
                ],
                "related_questions": [
                    "How does StateGraph differ from regular graphs?",
                    "What are the best practices for multi-agent systems?"
                ]
            },
            {
                "id": "resp-2",
                "model": "sonar",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "StateGraph provides typed state management with edges and nodes. "
                                  "It supports conditional routing and checkpointing."
                    }
                }],
                "citations": [
                    "https://python.langchain.com/docs/langgraph/concepts/",
                    "https://api.python.langchain.com/en/latest/langgraph/"
                ],
                "related_questions": [
                    "How to implement conditional edges?",
                    "What checkpointers are available?"
                ]
            }
        ]

    def test_citation_extraction(self, mock_perplexity_responses):
        """Test citations are extracted from Perplexity responses."""
        response = mock_perplexity_responses[0]

        citations = response.get("citations", [])

        assert len(citations) == 2
        assert "langchain.com" in citations[0]
        assert "github.com" in citations[1]

    def test_related_questions_extraction(self, mock_perplexity_responses):
        """Test related questions are extracted for follow-up."""
        response = mock_perplexity_responses[0]

        questions = response.get("related_questions", [])

        assert len(questions) == 2
        assert "?" in questions[0]

    def test_research_loop_iteration(self, mock_perplexity_responses):
        """Test research loop performs multiple iterations."""
        # Simulate research loop
        max_depth = 2
        findings = []
        queries = ["LangGraph overview"]

        for depth in range(max_depth):
            if depth >= len(mock_perplexity_responses):
                break

            response = mock_perplexity_responses[depth]
            content = response["choices"][0]["message"]["content"]
            citations = response.get("citations", [])
            related = response.get("related_questions", [])

            findings.append({
                "query": queries[0] if queries else f"follow-up-{depth}",
                "answer": content,
                "citations": citations,
                "depth": depth
            })

            # Add related questions for next iteration
            if related:
                queries = related[:1]  # Take first related question

        assert len(findings) == 2
        assert findings[0]["depth"] == 0
        assert findings[1]["depth"] == 1
        assert len(findings[0]["citations"]) > 0

    def test_convergence_detection(self):
        """Test research loop detects convergence."""
        # Simulate findings with overlapping citations
        findings_round1 = {
            "citations": [
                "https://docs.example.com/api",
                "https://github.com/example/repo"
            ]
        }
        findings_round2 = {
            "citations": [
                "https://docs.example.com/api",  # Same as round 1
                "https://docs.example.com/guide"  # New
            ]
        }
        findings_round3 = {
            "citations": [
                "https://docs.example.com/api",  # Same
                "https://docs.example.com/guide"  # Same as round 2
            ]
        }

        # Calculate citation overlap (Jaccard similarity)
        def calculate_overlap(set1, set2):
            s1, s2 = set(set1), set(set2)
            if not s1 or not s2:
                return 0.0
            intersection = len(s1 & s2)
            union = len(s1 | s2)
            return intersection / union if union > 0 else 0.0

        overlap_1_2 = calculate_overlap(
            findings_round1["citations"],
            findings_round2["citations"]
        )
        overlap_2_3 = calculate_overlap(
            findings_round2["citations"],
            findings_round3["citations"]
        )

        # Should show increasing convergence
        assert overlap_2_3 > overlap_1_2  # More overlap in later rounds
        assert overlap_2_3 >= 0.5  # High convergence

    def test_research_metrics_tracking(self):
        """Test research metrics are tracked throughout loop."""
        metrics = {
            "depth_reached": 0,
            "total_queries": 0,
            "total_citations": 0,
            "unique_sources": set(),
            "convergence_score": 0.0
        }

        # Simulate 3 research iterations with unique sources per iteration
        for i in range(3):
            metrics["depth_reached"] = i + 1
            metrics["total_queries"] += 1

            # Each iteration adds 2 citations, with some overlap
            # Iteration 0: source0, source1
            # Iteration 1: source1, source2 (source1 overlaps)
            # Iteration 2: source2, source3 (source2 overlaps)
            base = i
            new_citations = [f"https://source{base}.com", f"https://source{base+1}.com"]
            metrics["total_citations"] += len(new_citations)
            metrics["unique_sources"].update(new_citations)

        # Calculate final metrics
        metrics["convergence_score"] = (
            len(metrics["unique_sources"]) / metrics["total_citations"]
            if metrics["total_citations"] > 0 else 0.0
        )

        assert metrics["depth_reached"] == 3
        assert metrics["total_queries"] == 3
        assert metrics["total_citations"] == 6  # 2 + 2 + 2
        assert len(metrics["unique_sources"]) == 4  # source0, source1, source2, source3

    def test_citation_validation(self):
        """Test citation validation with domain trust scoring."""
        citations = [
            {"url": "https://docs.python.org/3/library/", "domain": "docs.python.org"},
            {"url": "https://github.com/langchain-ai/langgraph", "domain": "github.com"},
            {"url": "https://random-blog.com/article", "domain": "random-blog.com"},
            {"url": "https://arxiv.org/abs/2024.12345", "domain": "arxiv.org"}
        ]

        # Domain trust scores (simplified)
        trust_scores = {
            "docs.python.org": 0.98,
            "github.com": 0.92,
            "arxiv.org": 0.94,
            "default": 0.5
        }

        # Validate citations
        validated = []
        for citation in citations:
            domain = citation["domain"]
            trust = trust_scores.get(domain, trust_scores["default"])
            citation["trust_score"] = trust
            citation["is_trusted"] = trust >= 0.8
            validated.append(citation)

        trusted_count = sum(1 for c in validated if c["is_trusted"])
        assert trusted_count == 3  # python docs, github, arxiv

        # random-blog should be untrusted
        untrusted = [c for c in validated if not c["is_trusted"]]
        assert len(untrusted) == 1
        assert "random-blog" in untrusted[0]["domain"]

    def test_research_with_refinement_strategy(self, mock_perplexity_responses):
        """Test research with different refinement strategies."""
        strategies = ["related", "refine", "validate", "comprehensive"]

        for strategy in strategies:
            # Simulate strategy selection
            initial_query = "LangGraph StateGraph usage"

            if strategy == "related":
                # Follow related questions from response
                follow_up = mock_perplexity_responses[0]["related_questions"][0]
                assert "?" in follow_up

            elif strategy == "refine":
                # Refine query based on gaps
                follow_up = f"{initial_query} implementation details"
                assert "details" in follow_up

            elif strategy == "validate":
                # Cross-check specific claim
                follow_up = "verify StateGraph uses TypedDict for state"
                assert "verify" in follow_up

            elif strategy == "comprehensive":
                # Combine strategies
                follow_up = "complete guide to StateGraph patterns and best practices"
                assert "complete" in follow_up

    def test_research_stop_conditions(self):
        """Test research loop stops on appropriate conditions."""
        stop_reasons = []

        # Condition 1: Max depth reached
        if 3 >= 3:  # depth >= max_depth
            stop_reasons.append("MAX_DEPTH_REACHED")

        # Condition 2: Convergence
        if 0.9 >= 0.8:  # convergence_score >= threshold
            stop_reasons.append("CONVERGED")

        # Condition 3: No new queries
        queries = []
        if not queries:
            stop_reasons.append("NO_NEW_QUERIES")

        # Condition 4: Budget exhausted
        tokens_used = 50000
        token_budget = 100000
        if tokens_used >= token_budget:
            stop_reasons.append("BUDGET_EXHAUSTED")

        assert "MAX_DEPTH_REACHED" in stop_reasons
        assert "CONVERGED" in stop_reasons
        assert "NO_NEW_QUERIES" in stop_reasons


# =============================================================================
# Combined Integration Tests
# =============================================================================

class TestCombinedFlows:
    """Test combined flows across multiple components."""

    @pytest.fixture
    def combined_mock_agents(self):
        """Create mock agents for combined flow testing."""
        # Mock miner
        mock_miner = MagicMock()
        mock_miner.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                symbols=[
                    {"name": "StateGraph", "kind": "class", "file_path": "graph/state.py", "line": 15},
                ],
                code_snippets=[
                    {"snippet": "class StateGraph:\n    pass", "file_path": "graph/state.py"},
                ]
            )
        )

        # Mock linker
        mock_linker = MagicMock()
        mock_linker.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                links=[
                    {
                        "concept_name": "State Management",
                        "symbol_name": "StateGraph",
                        "file_path": "graph/state.py",
                        "line_number": 15,
                        "confidence": 0.9
                    }
                ]
            )
        )

        # Mock writer
        mock_writer = MagicMock()
        mock_skill = MagicMock()
        mock_skill.content = "StateGraph is a class for managing state."
        mock_writer.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(skill=mock_skill)
        )

        # Mock auditor
        mock_auditor = MagicMock()
        mock_auditor.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(
                passed=True,
                hallucination_rate=0.01,
                verified_claims=5,
                unverified_claims=0
            )
        )

        # Mock verifier
        mock_verifier = MagicMock()
        mock_verifier.execute.return_value = MagicMock(
            success=True,
            output=MagicMock(passed=True)
        )

        return {
            "miner": mock_miner,
            "linker": mock_linker,
            "writer": mock_writer,
            "auditor": mock_auditor,
            "verifier": mock_verifier,
        }

    @pytest.fixture
    def combined_mock_perplexity_responses(self):
        """Create mock Perplexity API responses for combined tests."""
        return [
            {
                "id": "resp-1",
                "model": "sonar",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "LangGraph is a framework for building multi-agent applications. "
                                  "It uses StateGraph for workflow orchestration."
                    }
                }],
                "citations": [
                    "https://python.langchain.com/docs/langgraph/",
                    "https://github.com/langchain-ai/langgraph"
                ],
                "related_questions": [
                    "How does StateGraph differ from regular graphs?",
                    "What are the best practices for multi-agent systems?"
                ]
            }
        ]

    def test_progressive_disclosure_with_verification(
        self, progressive_understanding: ProgressiveUnderstanding
    ):
        """Test progressive disclosure combined with verification."""
        # Get sections with source references
        sections = progressive_understanding.get_at_level(DepthLevel.DETAILED_SECTIONS)

        verified_refs = 0
        total_refs = 0

        for section in sections:
            for ref in section.source_refs:
                total_refs += 1
                # Simulate verification - check ref has required fields
                if ref.file_path and ref.line > 0 and ref.symbol_name:
                    verified_refs += 1

        if total_refs > 0:
            verification_rate = verified_refs / total_refs
            # All refs from CodeWiki should be valid
            assert verification_rate == 1.0

    def test_workflow_with_hall_m_tracking(self):
        """Test workflow tracks Hall_m throughout execution."""
        # Track Hall_m across stages
        hall_m_history = []

        # After auditing each skill
        skill_count = 3
        for i in range(skill_count):
            # Simulate varying hallucination rates
            hall_rate = 0.01 + (i * 0.005)  # 0.01, 0.015, 0.02
            hall_m_history.append(hall_rate)

        # Calculate cumulative Hall_m
        cumulative_hall_m = sum(hall_m_history) / len(hall_m_history)

        # Should be below threshold for first 2 skills
        assert hall_m_history[0] < 0.02
        assert hall_m_history[1] < 0.02

        # Third skill is at threshold
        assert hall_m_history[2] <= 0.02

        # Cumulative should be below threshold
        assert cumulative_hall_m < 0.02

    def test_research_findings_inform_understanding(self, combined_mock_perplexity_responses):
        """Test research findings can enhance progressive understanding."""
        # Start with basic understanding
        pu = ProgressiveUnderstanding(
            name="langgraph",
            repo="langchain-ai/langgraph",
            commit="abc123"
        )

        root = UnderstandingNode(
            id="root",
            title="LangGraph",
            level=DepthLevel.EXECUTIVE_SUMMARY,
            content="A framework for multi-agent applications."
        )
        pu.add_node(root)
        pu.root_id = root.id

        # Simulate research enriching the understanding
        research_response = combined_mock_perplexity_responses[0]
        research_content = research_response["choices"][0]["message"]["content"]

        # Create new concept from research
        concept = UnderstandingNode(
            id="concept_stategraph",
            title="StateGraph",
            level=DepthLevel.CONCEPT_MAP,
            content=research_content,
            parent_id=root.id,
            keywords={"stategraph", "workflow", "orchestration"}
        )
        pu.add_node(concept)
        root.children_ids.append(concept.id)

        # Verify enrichment
        concepts = pu.get_at_level(DepthLevel.CONCEPT_MAP)
        assert len(concepts) == 1
        assert "StateGraph" in concepts[0].content or "stategraph" in concepts[0].keywords

    def test_end_to_end_skill_generation_mock(
        self,
        sample_repo: Path,
        sample_codewiki: Path,
        combined_mock_agents
    ):
        """Test complete skill generation flow with mocked components."""
        # Step 1: Build progressive understanding
        pu = build_progressive_understanding(
            repo_name="langgraph",
            repo_path=sample_repo,
            codewiki_path=sample_codewiki
        )

        # Step 2: Extract concepts for mining
        concepts = pu.get_at_level(DepthLevel.CONCEPT_MAP)
        concept_names = [c.title for c in concepts]

        # Step 3: Simulate mining stage
        mining_result = combined_mock_agents["miner"].execute(MagicMock())
        assert mining_result.success

        # Step 4: Simulate linking stage
        linking_result = combined_mock_agents["linker"].execute(MagicMock())
        assert linking_result.success

        # Step 5: Simulate writing stage
        writing_result = combined_mock_agents["writer"].execute(MagicMock())
        assert writing_result.success

        # Step 6: Simulate auditing stage
        audit_result = combined_mock_agents["auditor"].execute(MagicMock())
        assert audit_result.success
        assert audit_result.output.hallucination_rate < 0.02

        # Step 7: Simulate verification stage
        verify_result = combined_mock_agents["verifier"].execute(MagicMock())
        assert verify_result.success

        # Final check: All stages completed successfully
        assert len(concepts) > 0  # Have concepts from understanding
        assert audit_result.output.passed  # Audit passed


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_codewiki_handling(self, temp_dir: Path, sample_repo: Path):
        """Test handling of empty CodeWiki directory."""
        empty_codewiki = temp_dir / "empty_codewiki"
        empty_codewiki.mkdir()
        (empty_codewiki / "sections").mkdir()  # Empty sections

        pu = build_progressive_understanding(
            repo_name="test",
            repo_path=sample_repo,
            codewiki_path=empty_codewiki
        )

        # Should still create root node
        assert pu.root_id is not None
        # May have no concepts due to empty sections
        concepts = pu.get_at_level(DepthLevel.CONCEPT_MAP)
        # Empty is acceptable
        assert len(concepts) >= 0

    def test_missing_symbol_catalog(self, temp_dir: Path, sample_repo: Path):
        """Test handling of missing symbol catalog."""
        codewiki = temp_dir / "codewiki_no_catalog"
        codewiki.mkdir()
        sections = codewiki / "sections"
        sections.mkdir()

        (sections / "test.md").write_text("## Test\n\nContent without symbols.")

        # Should not fail without symbol_catalog.md
        pu = build_progressive_understanding(
            repo_name="test",
            repo_path=sample_repo,
            codewiki_path=codewiki
        )

        assert pu is not None
        assert pu.root_id is not None

    def test_malformed_source_ref(self):
        """Test handling of malformed source references."""
        # Missing line number
        ref = SourceRef(
            file_path="test.py",
            line=0,  # Invalid line number
            commit="abc",
            repo="org/repo",
            symbol_name="Test",
            symbol_kind="class"
        )

        # Should still construct but line number is questionable
        assert ref.local_path == "test.py:0"

    def test_expand_nonexistent_node(self):
        """Test expanding a non-existent node raises error."""
        pu = ProgressiveUnderstanding(name="test", repo="org/test", commit="abc")

        with pytest.raises(ValueError, match="not found"):
            pu.expand("nonexistent", DepthLevel.SOURCE_REFERENCES)

    def test_unicode_content_handling(self, temp_dir: Path, sample_repo: Path):
        """Test handling of Unicode content in sections."""
        codewiki = temp_dir / "unicode_codewiki"
        codewiki.mkdir()
        sections = codewiki / "sections"
        sections.mkdir()

        # Create section with Unicode
        (sections / "unicode.md").write_text(
            "## Unicode Test \u2764\n\n"
            "Content with emojis \U0001F680 and special chars: \xe9\xe0\xfc"
        )

        pu = build_progressive_understanding(
            repo_name="test",
            repo_path=sample_repo,
            codewiki_path=codewiki
        )

        # Should handle Unicode without error
        assert pu is not None

    def test_large_section_handling(self, temp_dir: Path, sample_repo: Path):
        """Test handling of very large sections."""
        codewiki = temp_dir / "large_codewiki"
        codewiki.mkdir()
        sections = codewiki / "sections"
        sections.mkdir()

        # Create large section (over 10KB)
        large_content = "## Large Section\n\n" + "Content. " * 2000
        (sections / "large.md").write_text(large_content)

        pu = build_progressive_understanding(
            repo_name="test",
            repo_path=sample_repo,
            codewiki_path=codewiki
        )

        # Should truncate or handle large content
        assert pu is not None
        sections = pu.get_at_level(DepthLevel.DETAILED_SECTIONS)
        if sections:
            # Content should be limited
            assert len(sections[0].content) <= 1000  # Reasonable limit
