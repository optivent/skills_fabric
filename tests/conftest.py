"""Shared pytest fixtures for skills_fabric tests.

This module provides fixtures for:
- API client mocks (GLM, Perplexity, Brave)
- Code analysis tools (ASTParser, TreeSitterParser, LSPClient, CodeAnalyzer)
- Verification tools (DDR, HallMetric, MultiSourceValidator)
- Utility fixtures (temp files, sample code)

Usage:
    def test_something(mock_glm_client, sample_python_file):
        # Use fixtures in your tests
        pass
"""
from __future__ import annotations

import os
import tempfile
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# =============================================================================
# Configuration Fixtures
# =============================================================================

@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio for async tests."""
    return "asyncio"


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file path (not yet created)."""
    yield temp_dir / "test_file.py"


# =============================================================================
# Sample Code Fixtures
# =============================================================================

SAMPLE_PYTHON_CODE = '''"""Sample Python module for testing."""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SampleClass:
    """A sample class with various attributes."""
    name: str
    value: int = 0
    items: Optional[List[str]] = None

    def get_name(self) -> str:
        """Return the name."""
        return self.name

    def add_item(self, item: str) -> None:
        """Add an item to the list."""
        if self.items is None:
            self.items = []
        self.items.append(item)

    @property
    def item_count(self) -> int:
        """Return the number of items."""
        return len(self.items) if self.items else 0


def standalone_function(x: int, y: int = 10) -> int:
    """A standalone function with parameters."""
    return x + y


async def async_function(data: dict) -> list:
    """An async function for testing."""
    return list(data.keys())


class AnotherClass:
    """Another class for testing inheritance patterns."""

    def __init__(self, config: dict):
        self.config = config

    @staticmethod
    def static_method() -> str:
        return "static"

    @classmethod
    def class_method(cls) -> str:
        return cls.__name__
'''

SAMPLE_TYPESCRIPT_CODE = '''/**
 * Sample TypeScript module for testing.
 */

interface User {
    id: number;
    name: string;
    email?: string;
}

class UserService {
    private users: User[] = [];

    constructor(initialUsers?: User[]) {
        if (initialUsers) {
            this.users = initialUsers;
        }
    }

    getUser(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }

    addUser(user: User): void {
        this.users.push(user);
    }

    get userCount(): number {
        return this.users.length;
    }
}

function createUser(name: string, id: number): User {
    return { id, name };
}

const arrowFunction = (x: number): number => x * 2;

export { UserService, createUser, arrowFunction };
'''

SAMPLE_JAVASCRIPT_CODE = '''/**
 * Sample JavaScript module for testing.
 */

class DataProcessor {
    constructor(options = {}) {
        this.options = options;
        this.data = [];
    }

    process(input) {
        return input.map(item => this.transform(item));
    }

    transform(item) {
        return { ...item, processed: true };
    }

    static create(options) {
        return new DataProcessor(options);
    }
}

function processData(data, callback) {
    return data.map(callback);
}

const arrowProcessor = (data) => data.filter(d => d.active);

async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}

module.exports = { DataProcessor, processData, arrowProcessor, fetchData };
'''

SAMPLE_MALFORMED_CODE = '''
# This is intentionally malformed Python
def broken_function(
    # Missing closing paren and body
class incomplete:
    pass
'''


@pytest.fixture
def sample_python_code() -> str:
    """Return sample Python code string."""
    return SAMPLE_PYTHON_CODE


@pytest.fixture
def sample_typescript_code() -> str:
    """Return sample TypeScript code string."""
    return SAMPLE_TYPESCRIPT_CODE


@pytest.fixture
def sample_javascript_code() -> str:
    """Return sample JavaScript code string."""
    return SAMPLE_JAVASCRIPT_CODE


@pytest.fixture
def sample_malformed_code() -> str:
    """Return malformed code for error handling tests."""
    return SAMPLE_MALFORMED_CODE


@pytest.fixture
def sample_python_file(temp_dir: Path, sample_python_code: str) -> Path:
    """Create a sample Python file for testing."""
    file_path = temp_dir / "sample.py"
    file_path.write_text(sample_python_code)
    return file_path


@pytest.fixture
def sample_typescript_file(temp_dir: Path, sample_typescript_code: str) -> Path:
    """Create a sample TypeScript file for testing."""
    file_path = temp_dir / "sample.ts"
    file_path.write_text(sample_typescript_code)
    return file_path


@pytest.fixture
def sample_javascript_file(temp_dir: Path, sample_javascript_code: str) -> Path:
    """Create a sample JavaScript file for testing."""
    file_path = temp_dir / "sample.js"
    file_path.write_text(sample_javascript_code)
    return file_path


@pytest.fixture
def sample_malformed_file(temp_dir: Path, sample_malformed_code: str) -> Path:
    """Create a malformed Python file for error handling tests."""
    file_path = temp_dir / "malformed.py"
    file_path.write_text(sample_malformed_code)
    return file_path


@pytest.fixture
def sample_project_dir(
    temp_dir: Path,
    sample_python_code: str,
    sample_typescript_code: str,
    sample_javascript_code: str,
) -> Path:
    """Create a sample project directory with multiple files."""
    # Create Python files
    (temp_dir / "main.py").write_text(sample_python_code)
    (temp_dir / "utils.py").write_text('"""Utils module."""\n\ndef helper(): pass\n')

    # Create subdirectory with more files
    subdir = temp_dir / "src"
    subdir.mkdir()
    (subdir / "module.py").write_text('"""Module."""\n\nclass Module: pass\n')
    (subdir / "app.ts").write_text(sample_typescript_code)
    (subdir / "index.js").write_text(sample_javascript_code)

    return temp_dir


# =============================================================================
# AST Parser Fixtures
# =============================================================================

@pytest.fixture
def ast_parser():
    """Create an ASTParser instance."""
    from skills_fabric.analyze import ASTParser
    return ASTParser()


# =============================================================================
# Tree-sitter Parser Fixtures
# =============================================================================

@pytest.fixture
def tree_sitter_parser():
    """Create a TreeSitterParser instance with all languages initialized."""
    from skills_fabric.analyze import TreeSitterParser
    return TreeSitterParser()


# =============================================================================
# LSP Client Fixtures
# =============================================================================

@pytest.fixture
def mock_lsp_client():
    """Create a mock LSP client for tests that don't need real LSP."""
    from skills_fabric.analyze import Location, HoverInfo

    client = MagicMock()
    client.is_available = True
    client.is_initialized = True

    # Mock hover response
    client.get_hover.return_value = HoverInfo(
        contents="Sample hover content",
        range=None
    )

    # Mock definition response
    client.get_definition.return_value = Location(
        file_path="/test/file.py",
        line=10,
        column=0
    )

    # Mock references response
    client.get_references.return_value = [
        Location(file_path="/test/file.py", line=10, column=0),
        Location(file_path="/test/file.py", line=20, column=5),
    ]

    return client


@pytest.fixture
def lsp_client_unavailable():
    """Create a mock LSP client that simulates unavailability."""
    client = MagicMock()
    client.is_available = False
    client.is_initialized = False
    return client


# =============================================================================
# Code Analyzer Fixtures
# =============================================================================

@pytest.fixture
def code_analyzer_with_fallback(temp_dir: Path, mock_lsp_client):
    """Create a CodeAnalyzer with mocked LSP (will use fallback)."""
    from skills_fabric.analyze import CodeAnalyzer, AnalysisMode

    # Patch LSPClient to return mock
    with patch("skills_fabric.analyze.code_analyzer.LSPClient") as MockLSP:
        mock_instance = MagicMock()
        mock_instance.is_available = False  # Force fallback mode
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=None)
        MockLSP.return_value = mock_instance

        analyzer = CodeAnalyzer(project_path=temp_dir)
        yield analyzer


# =============================================================================
# GLM Client Fixtures (Mocked)
# =============================================================================

@dataclass
class MockGLMResponse:
    """Mock response from GLM API."""
    content: str
    thinking: str | None = None
    usage: dict | None = None
    finish_reason: str = "stop"


@pytest.fixture
def mock_glm_config():
    """Create a mock GLM configuration."""
    return {
        "api_key": "test-api-key",
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "model": "GLM-4.7-128K",
        "thinking_budget": 16000,
    }


@pytest.fixture
def mock_glm_client(mock_glm_config):
    """Create a mock GLM client for testing."""
    client = MagicMock()
    client.config = mock_glm_config

    # Default response
    default_response = MockGLMResponse(
        content="Sample response content",
        thinking="Internal reasoning...",
        usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    )

    client.generate.return_value = default_response
    client.chat.return_value = default_response
    client.explain_code.return_value = default_response

    # Async methods
    client.generate_stream_async = AsyncMock()

    return client


@pytest.fixture
def mock_glm_client_with_fallback(mock_glm_client):
    """Create a mock GLM client that simulates fallback behavior."""
    from skills_fabric.llm import ReasoningFailureType

    # Simulate reasoning failure followed by fallback
    failure_response = MockGLMResponse(
        content="Fallback response",
        thinking=None,
        usage={"prompt_tokens": 100, "completion_tokens": 30, "total_tokens": 130},
    )

    mock_glm_client.generate_with_fallback.return_value = failure_response
    mock_glm_client.reasoning_failure_type = ReasoningFailureType.BUDGET_EXHAUSTED

    return mock_glm_client


# =============================================================================
# Perplexity Client Fixtures (Mocked)
# =============================================================================

@pytest.fixture
def mock_perplexity_config():
    """Create a mock Perplexity configuration."""
    return {
        "api_key": "test-perplexity-key",
        "base_url": "https://api.perplexity.ai",
        "model": "sonar",
    }


@pytest.fixture
def mock_perplexity_response():
    """Create a mock Perplexity API response."""
    return {
        "id": "test-id",
        "model": "sonar",
        "created": 1234567890,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a test response with citations.",
            },
            "finish_reason": "stop",
        }],
        "citations": [
            "https://docs.example.com/guide",
            "https://github.com/example/repo",
        ],
        "related_questions": [
            "What are the best practices?",
            "How does this compare to alternatives?",
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
        },
    }


@pytest.fixture
def mock_perplexity_client(mock_perplexity_config, mock_perplexity_response):
    """Create a mock Perplexity client for testing."""
    client = MagicMock()
    client.config = mock_perplexity_config

    # Create mock research result
    client.research.return_value = MagicMock(
        answer="Test answer",
        citations=[
            MagicMock(url="https://example.com", title="Example"),
        ],
        related_questions=["Follow-up question?"],
        token_usage=MagicMock(prompt_tokens=50, completion_tokens=100),
    )

    # Async research
    client.research_async = AsyncMock(return_value=client.research.return_value)

    # Iterative research
    client.iterative_research.return_value = MagicMock(
        findings=[
            MagicMock(query="test query", answer="test answer", depth=0),
        ],
        metrics=MagicMock(
            depth_reached=1,
            total_queries=1,
            convergence_score=0.8,
        ),
    )

    return client


# =============================================================================
# Brave Search Client Fixtures (Mocked)
# =============================================================================

@pytest.fixture
def mock_brave_config():
    """Create a mock Brave Search configuration."""
    return {
        "api_key": "test-brave-key",
        "base_url": "https://api.search.brave.com/res/v1",
    }


@pytest.fixture
def mock_brave_response():
    """Create a mock Brave Search API response."""
    return {
        "web": {
            "results": [
                {
                    "title": "Example Result",
                    "url": "https://example.com/result",
                    "description": "This is an example search result.",
                    "age": "2 days ago",
                    "extra_snippets": ["Additional context"],
                },
                {
                    "title": "Another Result",
                    "url": "https://docs.python.org/3/",
                    "description": "Python documentation.",
                    "age": "1 week ago",
                },
            ],
        },
        "query": {
            "original": "test query",
        },
    }


@pytest.fixture
def mock_brave_client(mock_brave_config, mock_brave_response):
    """Create a mock Brave Search client for testing."""
    client = MagicMock()
    client.config = mock_brave_config

    # Mock search results
    mock_result = MagicMock(
        title="Example Result",
        url="https://example.com",
        description="Example description",
        relevance_score=0.85,
        domain_authority=0.9,
        content_type="DOCUMENTATION",
    )

    client.search.return_value = MagicMock(
        results=[mock_result],
        query="test query",
        total_results=1,
    )

    # Async search
    client.search_async = AsyncMock(return_value=client.search.return_value)

    return client


# =============================================================================
# DDR (Direct Dependency Retriever) Fixtures
# =============================================================================

@pytest.fixture
def mock_source_ref():
    """Create a mock SourceRef for testing."""
    from skills_fabric.verify import SourceRef

    return SourceRef(
        file_path="/test/module.py",
        line=42,
        column=0,
        end_line=50,
        symbol_name="TestClass",
        symbol_kind="class",
    )


@pytest.fixture
def mock_code_element(mock_source_ref):
    """Create a mock CodeElement for testing."""
    from skills_fabric.verify import CodeElement

    return CodeElement(
        name="TestClass",
        kind="class",
        source_ref=mock_source_ref,
        docstring="A test class.",
        is_valid=True,
    )


@pytest.fixture
def mock_ddr_result(mock_code_element):
    """Create a mock DDRResult for testing."""
    from skills_fabric.verify import DDRResult

    return DDRResult(
        query="TestClass",
        elements=[mock_code_element],
        validated_count=1,
        rejected_count=0,
        hallucination_rate=0.0,
    )


@pytest.fixture
def mock_ddr(mock_ddr_result):
    """Create a mock DirectDependencyRetriever for testing."""
    ddr = MagicMock()
    ddr.retrieve.return_value = mock_ddr_result
    ddr.retrieve_batch.return_value = [mock_ddr_result]
    ddr.hall_metric = MagicMock()
    ddr.hall_metric.get_summary.return_value = {
        "total_validated": 10,
        "total_rejected": 0,
        "cumulative_hall_m": 0.0,
    }
    return ddr


# =============================================================================
# Hall_m Metric Fixtures
# =============================================================================

@pytest.fixture
def hall_metric():
    """Create a fresh HallMetric instance for testing."""
    from skills_fabric.verify import HallMetric, reset_hall_metric

    # Reset global metric before test
    reset_hall_metric()
    return HallMetric(threshold=0.02, fail_on_exceed=False)


@pytest.fixture
def strict_hall_metric():
    """Create a HallMetric that fails when threshold is exceeded."""
    from skills_fabric.verify import HallMetric

    return HallMetric(threshold=0.02, fail_on_exceed=True)


# =============================================================================
# Multi-Source Validator Fixtures
# =============================================================================

@pytest.fixture
def mock_multi_source_validator():
    """Create a mock MultiSourceValidator for testing."""
    from skills_fabric.verify import ValidationSource, ValidationResult

    validator = MagicMock()

    # Default validation result
    validator.validate.return_value = ValidationResult(
        is_valid=True,
        confidence=0.95,
        sources=[ValidationSource.AST, ValidationSource.TREE_SITTER],
        errors=[],
    )

    return validator


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture
def env_with_api_keys(monkeypatch):
    """Set up environment with mock API keys."""
    monkeypatch.setenv("ZAI_API_KEY", "test-zai-key")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test-perplexity-key")
    monkeypatch.setenv("BRAVE_API_KEY", "test-brave-key")
    monkeypatch.setenv("LANGCHAIN_API_KEY", "test-langchain-key")
    monkeypatch.setenv("LANGCHAIN_PROJECT", "test-project")


@pytest.fixture
def env_without_api_keys(monkeypatch):
    """Remove API keys from environment to test missing key handling."""
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)


# =============================================================================
# Skip Markers
# =============================================================================

# Marker for tests requiring real API keys
requires_api_keys = pytest.mark.skipif(
    not os.environ.get("ZAI_API_KEY"),
    reason="Requires ZAI_API_KEY environment variable"
)

requires_perplexity = pytest.mark.skipif(
    not os.environ.get("PERPLEXITY_API_KEY"),
    reason="Requires PERPLEXITY_API_KEY environment variable"
)

requires_brave = pytest.mark.skipif(
    not os.environ.get("BRAVE_API_KEY"),
    reason="Requires BRAVE_API_KEY environment variable"
)

# Marker for slow tests
slow = pytest.mark.slow

# Marker for integration tests
integration = pytest.mark.integration
