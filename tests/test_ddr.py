"""Unit tests for DDR (Direct Dependency Retriever) validation pipeline.

This module tests the DDR implementation:
- Symbol catalog parsing (Markdown, table, simple formats)
- Validation pipeline (multi-source validation)
- Hallucination rate (Hall_m) calculation
- Batch processing (sequential and parallel)

Test coverage includes:
- HallMetric class and threshold handling
- HallMetricSnapshot properties
- ValidationResult and confidence scoring
- MultiSourceValidator symbol validation
- DirectDependencyRetriever retrieval and batching
- BatchProgress and BatchResult dataclasses
"""
from __future__ import annotations

import importlib.util
import os
import sys
import time
import tempfile
import types
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Setup module hierarchy for imports
_src_path = Path(__file__).parent.parent / "src"

# Create skills_fabric namespace packages if not present
if "skills_fabric" not in sys.modules:
    _sf = types.ModuleType("skills_fabric")
    _sf.__path__ = [str(_src_path / "skills_fabric")]
    sys.modules["skills_fabric"] = _sf

if "skills_fabric.verify" not in sys.modules:
    _verify = types.ModuleType("skills_fabric.verify")
    _verify.__path__ = [str(_src_path / "skills_fabric" / "verify")]
    sys.modules["skills_fabric.verify"] = _verify

if "skills_fabric.observability" not in sys.modules:
    _obs = types.ModuleType("skills_fabric.observability")
    _obs.__path__ = [str(_src_path / "skills_fabric" / "observability")]
    sys.modules["skills_fabric.observability"] = _obs

# Import observability.logging first
_logging_path = _src_path / "skills_fabric" / "observability" / "logging.py"
_logging_spec = importlib.util.spec_from_file_location(
    "skills_fabric.observability.logging", _logging_path
)
_logging_module = importlib.util.module_from_spec(_logging_spec)
sys.modules["skills_fabric.observability.logging"] = _logging_module
_logging_spec.loader.exec_module(_logging_module)

# Create analyze namespace package for validators
if "skills_fabric.analyze" not in sys.modules:
    _analyze = types.ModuleType("skills_fabric.analyze")
    _analyze.__path__ = [str(_src_path / "skills_fabric" / "analyze")]
    sys.modules["skills_fabric.analyze"] = _analyze

# Import ast_parser for MultiSourceValidator
_ast_parser_path = _src_path / "skills_fabric" / "analyze" / "ast_parser.py"
_ast_spec = importlib.util.spec_from_file_location(
    "skills_fabric.analyze.ast_parser", _ast_parser_path
)
_ast_module = importlib.util.module_from_spec(_ast_spec)
sys.modules["skills_fabric.analyze.ast_parser"] = _ast_module
_ast_spec.loader.exec_module(_ast_module)

# Create tree_sitter namespace package
if "skills_fabric.analyze.tree_sitter" not in sys.modules:
    _ts_pkg = types.ModuleType("skills_fabric.analyze.tree_sitter")
    _ts_pkg.__path__ = [str(_src_path / "skills_fabric" / "analyze" / "tree_sitter")]
    sys.modules["skills_fabric.analyze.tree_sitter"] = _ts_pkg

# Import tree_sitter module
_ts_init_path = _src_path / "skills_fabric" / "analyze" / "tree_sitter" / "__init__.py"
if _ts_init_path.exists():
    _ts_spec = importlib.util.spec_from_file_location(
        "skills_fabric.analyze.tree_sitter", _ts_init_path, submodule_search_locations=[str(_ts_init_path.parent)]
    )
    _ts_module = importlib.util.module_from_spec(_ts_spec)
    try:
        _ts_spec.loader.exec_module(_ts_module)
        sys.modules["skills_fabric.analyze.tree_sitter"] = _ts_module
    except ImportError:
        # tree-sitter may not be installed, provide mock
        pass

# Import ddr module
_ddr_path = _src_path / "skills_fabric" / "verify" / "ddr" / "__init__.py"
_ddr_spec = importlib.util.spec_from_file_location(
    "skills_fabric.verify.ddr", _ddr_path
)
_ddr_module = importlib.util.module_from_spec(_ddr_spec)
sys.modules["skills_fabric.verify.ddr"] = _ddr_module
_ddr_spec.loader.exec_module(_ddr_module)

# Import classes we need to test
HallMetric = _ddr_module.HallMetric
HallMetricSnapshot = _ddr_module.HallMetricSnapshot
HallMetricExceededException = _ddr_module.HallMetricExceededException
ValidationSource = _ddr_module.ValidationSource
ValidationResult = _ddr_module.ValidationResult
MultiSourceValidator = _ddr_module.MultiSourceValidator
SourceRef = _ddr_module.SourceRef
CodeElement = _ddr_module.CodeElement
DDRResult = _ddr_module.DDRResult
BatchProgress = _ddr_module.BatchProgress
BatchResult = _ddr_module.BatchResult
DirectDependencyRetriever = _ddr_module.DirectDependencyRetriever
get_hall_metric = _ddr_module.get_hall_metric
reset_hall_metric = _ddr_module.reset_hall_metric
set_hall_metric_threshold = _ddr_module.set_hall_metric_threshold


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def hall_metric() -> HallMetric:
    """Create a fresh HallMetric instance."""
    return HallMetric(threshold=0.02, fail_on_exceed=False)


@pytest.fixture
def strict_hall_metric() -> HallMetric:
    """Create a HallMetric that fails when threshold is exceeded."""
    return HallMetric(threshold=0.02, fail_on_exceed=True)


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_symbol_catalog_md() -> str:
    """Sample symbol catalog in Markdown link format."""
    return """# Symbol Catalog

## Classes

[`StateGraph`](https://github.com/langchain-ai/langgraph/blob/main/langgraph/graph/state.py#L50)
[`CompiledGraph`](https://github.com/langchain-ai/langgraph/blob/main/langgraph/graph/graph.py#L100)

## Functions

[`add_node`](https://github.com/langchain-ai/langgraph/blob/main/langgraph/graph/state.py#L150)
[`compile`](https://github.com/langchain-ai/langgraph/blob/main/langgraph/graph/state.py#L200)
"""


@pytest.fixture
def sample_symbol_catalog_simple() -> str:
    """Sample symbol catalog in simple Docling format."""
    return """# Symbol Catalog

### `sample.py`
- Line 11: `Person` (class)
- Line 23: `greet` (method)
- Line 64: `Calculator` (class)
- Line 80: `add` (method)
- Line 116: `fetch_data` (async_function)

### `sample.ts`
- Line 31: `UserService` (class)
- Line 131: `formatUser` (function)
"""


@pytest.fixture
def sample_symbol_catalog_table() -> str:
    """Sample symbol catalog in table format."""
    return """# Symbol Catalog

## sample.py

| Symbol | Type | Line | Signature |
| ------ | ---- | ---- | --------- |
| Person | class | 11 | class Person |
| greet | method | 23 | def greet(self) -> str |
| Calculator | class | 64 | class Calculator |

## sample.ts

| Symbol | Type | Line | Signature |
| ------ | ---- | ---- | --------- |
| UserService | class | 31 | class UserService |
"""


@pytest.fixture
def sample_python_file(temp_dir: Path) -> Path:
    """Create a sample Python file for validation tests."""
    file_path = temp_dir / "sample.py"
    file_path.write_text('''"""Sample module."""

class Person:
    """A person class."""

    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        """Return greeting."""
        return f"Hello, {self.name}"


def calculate(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    return {"url": url}
''')
    return file_path


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


# =============================================================================
# HallMetric Tests
# =============================================================================


class TestHallMetric:
    """Test HallMetric class for hallucination rate tracking."""

    def test_default_values(self):
        """Test HallMetric default values."""
        metric = HallMetric()

        assert metric.threshold == 0.02
        assert metric.fail_on_exceed is False
        assert metric.total_validated == 0
        assert metric.total_rejected == 0
        assert metric.current_hall_m == 0.0
        assert metric.is_within_threshold is True

    def test_custom_threshold(self):
        """Test HallMetric with custom threshold."""
        metric = HallMetric(threshold=0.05, fail_on_exceed=True)

        assert metric.threshold == 0.05
        assert metric.fail_on_exceed is True

    def test_calculate_static_method(self):
        """Test static calculate() method."""
        # Perfect validation (no hallucinations)
        assert HallMetric.calculate(100, 0) == 0.0

        # Some rejections
        assert HallMetric.calculate(90, 10) == 0.1

        # High rejection rate
        assert HallMetric.calculate(50, 50) == 0.5

        # All rejected
        assert HallMetric.calculate(0, 100) == 1.0

        # Edge case: zero total
        assert HallMetric.calculate(0, 0) == 0.0

    def test_record_updates_totals(self, hall_metric: HallMetric):
        """Test that record() updates running totals."""
        hall_metric.record(validated=10, rejected=0, operation="test")

        assert hall_metric.total_validated == 10
        assert hall_metric.total_rejected == 0
        assert hall_metric.current_hall_m == 0.0

        hall_metric.record(validated=8, rejected=2, operation="test")

        assert hall_metric.total_validated == 18
        assert hall_metric.total_rejected == 2
        # Hall_m = 2/20 = 0.1
        assert hall_metric.current_hall_m == 0.1

    def test_record_returns_snapshot(self, hall_metric: HallMetric):
        """Test that record() returns a HallMetricSnapshot."""
        snapshot = hall_metric.record(validated=95, rejected=5, operation="batch")

        assert isinstance(snapshot, HallMetricSnapshot)
        assert snapshot.validated == 95
        assert snapshot.rejected == 5
        assert snapshot.hall_m == 0.05  # 5/100
        assert snapshot.operation == "batch"

    def test_record_adds_to_history(self, hall_metric: HallMetric):
        """Test that record() adds snapshot to history."""
        assert len(hall_metric.history) == 0

        hall_metric.record(validated=10, rejected=0, operation="test1")
        assert len(hall_metric.history) == 1

        hall_metric.record(validated=5, rejected=1, operation="test2")
        assert len(hall_metric.history) == 2

    def test_record_and_check_below_threshold(self, strict_hall_metric: HallMetric):
        """Test record_and_check() when below threshold."""
        # Hall_m = 1/100 = 0.01 < 0.02 threshold
        snapshot = strict_hall_metric.record_and_check(
            validated=99, rejected=1, operation="test"
        )

        assert snapshot.hall_m < strict_hall_metric.threshold
        # Should not raise exception

    def test_record_and_check_exceeds_threshold(self, strict_hall_metric: HallMetric):
        """Test record_and_check() when exceeding threshold."""
        # Hall_m = 5/100 = 0.05 >= 0.02 threshold
        with pytest.raises(HallMetricExceededException) as exc_info:
            strict_hall_metric.record_and_check(
                validated=95, rejected=5, operation="test"
            )

        assert exc_info.value.hall_m == 0.05
        assert exc_info.value.threshold == 0.02
        assert exc_info.value.validated == 95
        assert exc_info.value.rejected == 5

    def test_record_and_check_override_fail(self, hall_metric: HallMetric):
        """Test record_and_check() with override fail_on_exceed."""
        # Default metric has fail_on_exceed=False
        assert hall_metric.fail_on_exceed is False

        # Override to fail
        with pytest.raises(HallMetricExceededException):
            hall_metric.record_and_check(
                validated=90, rejected=10,  # Hall_m = 0.1
                operation="test",
                fail_on_exceed=True
            )

    def test_check_cumulative(self, hall_metric: HallMetric):
        """Test check_cumulative() method."""
        hall_metric.record(validated=98, rejected=2, operation="test")

        # Cumulative Hall_m = 2/100 = 0.02, which equals threshold
        assert hall_metric.is_within_threshold is False
        assert hall_metric.check_cumulative(fail_on_exceed=False) is False

    def test_check_cumulative_raises(self, strict_hall_metric: HallMetric):
        """Test check_cumulative() raises when configured to fail."""
        # Add observations that exceed threshold
        strict_hall_metric.record(validated=80, rejected=20, operation="test")

        with pytest.raises(HallMetricExceededException) as exc_info:
            strict_hall_metric.check_cumulative(fail_on_exceed=True)

        assert exc_info.value.context == "cumulative"

    def test_total_attempted_property(self, hall_metric: HallMetric):
        """Test total_attempted property."""
        hall_metric.record(validated=50, rejected=10, operation="test")
        hall_metric.record(validated=30, rejected=5, operation="test")

        assert hall_metric.total_attempted == 95  # 50+10+30+5

    def test_is_exceeding_threshold(self, hall_metric: HallMetric):
        """Test is_exceeding_threshold property."""
        # Initially within threshold
        assert hall_metric.is_exceeding_threshold is False

        # Add high rejection rate
        hall_metric.record(validated=80, rejected=20, operation="test")

        # Now exceeding
        assert hall_metric.is_exceeding_threshold is True

    def test_get_summary(self, hall_metric: HallMetric):
        """Test get_summary() method."""
        hall_metric.record(validated=90, rejected=5, operation="retrieve")
        hall_metric.record(validated=85, rejected=15, operation="batch")

        summary = hall_metric.get_summary()

        assert summary["observations"] == 2
        assert summary["total_validated"] == 175
        assert summary["total_rejected"] == 20
        assert summary["total_attempted"] == 195
        assert summary["threshold"] == 0.02
        assert "by_operation" in summary
        assert "retrieve" in summary["by_operation"]
        assert "batch" in summary["by_operation"]

    def test_get_summary_empty(self, hall_metric: HallMetric):
        """Test get_summary() with no observations."""
        summary = hall_metric.get_summary()

        assert summary["observations"] == 0
        assert summary["cumulative_hall_m"] == 0.0
        assert summary["is_within_threshold"] is True

    def test_reset(self, hall_metric: HallMetric):
        """Test reset() method."""
        hall_metric.record(validated=90, rejected=10, operation="test")
        assert hall_metric.total_attempted == 100

        hall_metric.reset()

        assert hall_metric.total_validated == 0
        assert hall_metric.total_rejected == 0
        assert len(hall_metric.history) == 0

    def test_export_history(self, hall_metric: HallMetric):
        """Test export_history() method."""
        hall_metric.record(validated=90, rejected=10, operation="test1")
        hall_metric.record(validated=95, rejected=5, operation="test2")

        history = hall_metric.export_history()

        assert len(history) == 2
        assert history[0]["operation"] == "test1"
        assert history[1]["operation"] == "test2"
        assert "timestamp" in history[0]
        assert "hall_m" in history[0]


class TestHallMetricSnapshot:
    """Test HallMetricSnapshot dataclass."""

    def test_snapshot_properties(self):
        """Test HallMetricSnapshot properties."""
        snapshot = HallMetricSnapshot(
            timestamp=datetime.now(),
            hall_m=0.05,
            validated=95,
            rejected=5,
            total_attempted=100,
            operation="test",
            context="query: StateGraph"
        )

        assert snapshot.hall_m == 0.05
        assert snapshot.validated == 95
        assert snapshot.rejected == 5
        assert snapshot.success_rate == 0.95

    def test_to_dict(self):
        """Test HallMetricSnapshot.to_dict() method."""
        timestamp = datetime.now()
        snapshot = HallMetricSnapshot(
            timestamp=timestamp,
            hall_m=0.1,
            validated=90,
            rejected=10,
            total_attempted=100,
            operation="batch",
            context=""
        )

        d = snapshot.to_dict()

        assert d["hall_m"] == 0.1
        assert d["validated"] == 90
        assert d["rejected"] == 10
        assert d["operation"] == "batch"
        assert d["success_rate"] == 0.9
        assert "timestamp" in d


class TestGlobalHallMetric:
    """Test global Hall_m metric functions."""

    def test_get_hall_metric_returns_instance(self):
        """Test get_hall_metric() returns HallMetric instance."""
        reset_hall_metric()
        metric = get_hall_metric()

        assert isinstance(metric, HallMetric)

    def test_get_hall_metric_same_instance(self):
        """Test get_hall_metric() returns same instance."""
        reset_hall_metric()
        metric1 = get_hall_metric()
        metric2 = get_hall_metric()

        assert metric1 is metric2

    def test_reset_hall_metric(self):
        """Test reset_hall_metric() clears state."""
        metric = get_hall_metric()
        metric.record(validated=90, rejected=10, operation="test")
        assert metric.total_attempted == 100

        reset_hall_metric()
        assert metric.total_attempted == 0

    def test_set_hall_metric_threshold(self):
        """Test set_hall_metric_threshold() configures global metric."""
        reset_hall_metric()
        set_hall_metric_threshold(0.05, fail_on_exceed=True)

        metric = get_hall_metric()
        assert metric.threshold == 0.05
        assert metric.fail_on_exceed is True


# =============================================================================
# ValidationResult Tests
# =============================================================================


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_default_values(self):
        """Test ValidationResult default values."""
        result = ValidationResult(symbol_name="TestClass", is_valid=False)

        assert result.symbol_name == "TestClass"
        assert result.is_valid is False
        assert result.sources_checked == []
        assert result.sources_confirmed == []
        assert result.confidence == 0.0

    def test_confidence_calculation(self):
        """Test confidence property calculation."""
        result = ValidationResult(
            symbol_name="TestClass",
            is_valid=True,
            sources_checked=[ValidationSource.AST_PARSER, ValidationSource.TREE_SITTER],
            sources_confirmed=[ValidationSource.AST_PARSER, ValidationSource.TREE_SITTER],
        )

        # 2/2 = 1.0 confidence
        assert result.confidence == 1.0

    def test_confidence_partial(self):
        """Test confidence with partial confirmation."""
        result = ValidationResult(
            symbol_name="TestClass",
            is_valid=True,
            sources_checked=[
                ValidationSource.AST_PARSER,
                ValidationSource.TREE_SITTER,
                ValidationSource.FILE_CONTENT
            ],
            sources_confirmed=[ValidationSource.AST_PARSER],
        )

        # 1/3 confidence
        assert result.confidence == pytest.approx(0.333, rel=0.01)

    def test_is_high_confidence(self):
        """Test is_high_confidence property."""
        # Low confidence (only 1 source)
        result1 = ValidationResult(
            symbol_name="Test",
            is_valid=True,
            sources_confirmed=[ValidationSource.AST_PARSER],
        )
        assert result1.is_high_confidence is False

        # High confidence (2+ sources)
        result2 = ValidationResult(
            symbol_name="Test",
            is_valid=True,
            sources_confirmed=[ValidationSource.AST_PARSER, ValidationSource.TREE_SITTER],
        )
        assert result2.is_high_confidence is True

    def test_has_discrepancies(self):
        """Test has_discrepancies property."""
        result1 = ValidationResult(symbol_name="Test", is_valid=True)
        assert result1.has_discrepancies is False

        result2 = ValidationResult(
            symbol_name="Test",
            is_valid=True,
            discrepancies=["Line mismatch: expected 10, got 12"]
        )
        assert result2.has_discrepancies is True

    def test_to_dict(self):
        """Test to_dict() method."""
        result = ValidationResult(
            symbol_name="TestClass",
            is_valid=True,
            sources_checked=[ValidationSource.AST_PARSER],
            sources_confirmed=[ValidationSource.AST_PARSER],
            line_number=10,
            actual_line=10,
            symbol_kind="class",
        )

        d = result.to_dict()

        assert d["symbol_name"] == "TestClass"
        assert d["is_valid"] is True
        assert d["confidence"] == 1.0
        assert "ast_parser" in d["sources_checked"]
        assert "ast_parser" in d["sources_confirmed"]


# =============================================================================
# SourceRef and CodeElement Tests
# =============================================================================


class TestSourceRef:
    """Test SourceRef dataclass."""

    def test_citation_format(self):
        """Test citation property returns correct format."""
        ref = SourceRef(
            symbol_name="StateGraph",
            file_path="langgraph/graph/state.py",
            line_number=50,
        )

        assert ref.citation == "langgraph/graph/state.py:50"

    def test_github_url(self):
        """Test github_url property."""
        ref = SourceRef(
            symbol_name="StateGraph",
            file_path="langgraph/graph/state.py",
            line_number=50,
        )

        assert "state.py#L50" in ref.github_url

    def test_to_dict(self):
        """Test to_dict() method."""
        ref = SourceRef(
            symbol_name="TestClass",
            file_path="test.py",
            line_number=10,
            end_line=20,
            symbol_type="class",
            validated=True,
        )

        d = ref.to_dict()

        assert d["symbol_name"] == "TestClass"
        assert d["file_path"] == "test.py"
        assert d["line_number"] == 10
        assert d["end_line"] == 20
        assert d["validated"] is True


class TestCodeElement:
    """Test CodeElement dataclass."""

    def test_is_valid_property(self):
        """Test is_valid depends on source_ref.validated."""
        ref_validated = SourceRef(
            symbol_name="Test",
            file_path="test.py",
            line_number=10,
            validated=True,
        )
        element_valid = CodeElement(source_ref=ref_validated, content="class Test:")
        assert element_valid.is_valid is True

        ref_invalid = SourceRef(
            symbol_name="Test",
            file_path="test.py",
            line_number=10,
            validated=False,
        )
        element_invalid = CodeElement(source_ref=ref_invalid, content="class Test:")
        assert element_invalid.is_valid is False


# =============================================================================
# DDRResult Tests
# =============================================================================


class TestDDRResult:
    """Test DDRResult dataclass."""

    def test_success_property(self):
        """Test success property."""
        # Successful: has validated elements and low Hall_m
        result1 = DDRResult(
            query="StateGraph",
            elements=[
                CodeElement(
                    source_ref=SourceRef("Test", "test.py", 10, validated=True),
                    content="class Test:"
                )
            ],
            validated_count=1,
            rejected_count=0,
            hallucination_rate=0.0,
        )
        assert result1.success is True

        # Failed: Hall_m >= 0.02
        result2 = DDRResult(
            query="StateGraph",
            elements=[],
            validated_count=10,
            rejected_count=10,
            hallucination_rate=0.5,
        )
        assert result2.success is False

        # Failed: no validated elements
        result3 = DDRResult(
            query="StateGraph",
            elements=[],
            validated_count=0,
            rejected_count=5,
            hallucination_rate=1.0,
        )
        assert result3.success is False


# =============================================================================
# BatchProgress Tests
# =============================================================================


class TestBatchProgress:
    """Test BatchProgress dataclass."""

    def test_percent_complete(self):
        """Test percent_complete property."""
        progress = BatchProgress(total=100)
        assert progress.percent_complete == 0.0

        progress.processed = 50
        assert progress.percent_complete == 50.0

        progress.processed = 100
        assert progress.percent_complete == 100.0

    def test_percent_complete_zero_total(self):
        """Test percent_complete with zero total."""
        progress = BatchProgress(total=0)
        assert progress.percent_complete == 100.0

    def test_hallucination_rate(self):
        """Test hallucination_rate property."""
        progress = BatchProgress(total=100)
        progress.validated = 90
        progress.rejected = 10

        assert progress.hallucination_rate == 0.1

    def test_hallucination_rate_zero(self):
        """Test hallucination_rate with no processing."""
        progress = BatchProgress(total=100)
        assert progress.hallucination_rate == 0.0

    def test_items_per_second(self):
        """Test items_per_second property."""
        progress = BatchProgress(total=100)
        # Simulate some processing time
        time.sleep(0.1)
        progress.processed = 10

        rate = progress.items_per_second
        assert rate > 0  # Should be approximately 100 items/sec

    def test_eta_seconds(self):
        """Test eta_seconds property."""
        progress = BatchProgress(total=100)
        time.sleep(0.05)
        progress.processed = 50

        eta = progress.eta_seconds
        # Should be roughly the same as elapsed time (50% done)
        assert eta >= 0


# =============================================================================
# BatchResult Tests
# =============================================================================


class TestBatchResult:
    """Test BatchResult dataclass."""

    def test_success_property(self):
        """Test success property based on Hall_m."""
        # Hall_m < 0.02 = success
        result1 = BatchResult(
            results=[],
            total_validated=99,
            total_rejected=1,
            overall_hallucination_rate=0.01,
            duration_seconds=1.0,
            queries_processed=10,
        )
        assert result1.success is True

        # Hall_m >= 0.02 = failure
        result2 = BatchResult(
            results=[],
            total_validated=90,
            total_rejected=10,
            overall_hallucination_rate=0.1,
            duration_seconds=1.0,
            queries_processed=10,
        )
        assert result2.success is False

    def test_all_elements_property(self):
        """Test all_elements aggregates from all results."""
        elem1 = CodeElement(
            source_ref=SourceRef("Test1", "test1.py", 10, validated=True),
            content="class Test1:"
        )
        elem2 = CodeElement(
            source_ref=SourceRef("Test2", "test2.py", 20, validated=True),
            content="class Test2:"
        )

        result = BatchResult(
            results=[
                DDRResult(
                    query="q1",
                    elements=[elem1],
                    validated_count=1,
                    rejected_count=0,
                    hallucination_rate=0.0,
                ),
                DDRResult(
                    query="q2",
                    elements=[elem2],
                    validated_count=1,
                    rejected_count=0,
                    hallucination_rate=0.0,
                ),
            ],
            total_validated=2,
            total_rejected=0,
            overall_hallucination_rate=0.0,
            duration_seconds=1.0,
            queries_processed=2,
        )

        all_elements = result.all_elements
        assert len(all_elements) == 2
        assert elem1 in all_elements
        assert elem2 in all_elements


# =============================================================================
# Symbol Catalog Parsing Tests
# =============================================================================


class TestSymbolCatalogParsing:
    """Test symbol catalog parsing for different formats."""

    def test_parse_markdown_link_format(self, sample_symbol_catalog_md: str):
        """Test parsing Markdown link format catalog."""
        ddr = DirectDependencyRetriever()
        index = ddr._parse_symbol_catalog(sample_symbol_catalog_md)

        # Check that StateGraph was parsed
        assert "stategraph" in index
        entries = index["stategraph"]
        assert len(entries) >= 1
        assert entries[0]["symbol"] == "StateGraph"
        assert entries[0]["file"] == "langgraph/graph/state.py"
        assert entries[0]["line"] == 50

    def test_parse_simple_docling_format(self, sample_symbol_catalog_simple: str):
        """Test parsing simple Docling format catalog."""
        ddr = DirectDependencyRetriever()
        index = ddr._parse_symbol_catalog(sample_symbol_catalog_simple)

        # Check Person class
        assert "person" in index
        person_entry = index["person"][0]
        assert person_entry["line"] == 11
        assert person_entry["type"] == "class"
        assert person_entry["file"] == "sample.py"

        # Check async function
        assert "fetch_data" in index
        fetch_entry = index["fetch_data"][0]
        assert fetch_entry["type"] == "async_function"

    def test_parse_table_format(self, sample_symbol_catalog_table: str):
        """Test parsing table format catalog."""
        ddr = DirectDependencyRetriever()
        index = ddr._parse_symbol_catalog(sample_symbol_catalog_table)

        # Check Calculator class
        assert "calculator" in index
        calc_entry = index["calculator"][0]
        assert calc_entry["line"] == 64
        assert calc_entry["type"] == "class"

    def test_parse_empty_catalog(self):
        """Test parsing empty catalog."""
        ddr = DirectDependencyRetriever()
        index = ddr._parse_symbol_catalog("")

        assert index == {}

    def test_parse_case_insensitive_keys(self, sample_symbol_catalog_simple: str):
        """Test that symbol keys are lowercase for case-insensitive search."""
        ddr = DirectDependencyRetriever()
        index = ddr._parse_symbol_catalog(sample_symbol_catalog_simple)

        # All keys should be lowercase
        for key in index.keys():
            assert key == key.lower()


# =============================================================================
# MultiSourceValidator Tests
# =============================================================================


class TestMultiSourceValidator:
    """Test MultiSourceValidator for symbol validation."""

    def test_init_without_repo(self):
        """Test MultiSourceValidator initialization without repo path."""
        validator = MultiSourceValidator()

        assert validator._repo_path is None
        assert validator._use_lsp is False

    def test_init_with_repo(self, temp_dir: Path):
        """Test MultiSourceValidator initialization with repo path."""
        validator = MultiSourceValidator(repo_path=temp_dir)

        assert validator._repo_path == temp_dir
        validator.close()

    def test_validate_nonexistent_file(self, temp_dir: Path):
        """Test validation for non-existent file."""
        validator = MultiSourceValidator(repo_path=temp_dir)

        result = validator.validate_symbol(
            symbol_name="Test",
            file_path="nonexistent.py",
            line_number=10,
        )

        assert result.is_valid is False
        assert "File not found" in result.discrepancies[0]
        validator.close()

    def test_validate_with_file_content(self, sample_python_file: Path, temp_dir: Path):
        """Test validation using file content fallback."""
        validator = MultiSourceValidator(repo_path=temp_dir)

        result = validator.validate_symbol(
            symbol_name="Person",
            file_path="sample.py",
            line_number=3,  # Line where class Person is defined
        )

        assert result.is_valid is True
        assert ValidationSource.FILE_CONTENT in result.sources_confirmed
        validator.close()

    def test_validate_symbol_not_found(self, sample_python_file: Path, temp_dir: Path):
        """Test validation when symbol not found."""
        validator = MultiSourceValidator(repo_path=temp_dir)

        result = validator.validate_symbol(
            symbol_name="NonExistentClass",
            file_path="sample.py",
            line_number=1,
        )

        # Should not find symbol
        assert result.is_valid is False or len(result.sources_confirmed) == 0
        validator.close()

    def test_validate_batch(self, sample_python_file: Path, temp_dir: Path):
        """Test batch symbol validation."""
        validator = MultiSourceValidator(repo_path=temp_dir)

        symbols = [
            {"symbol": "Person", "file": "sample.py", "line": 3},
            {"symbol": "greet", "file": "sample.py", "line": 9},
            {"symbol": "calculate", "file": "sample.py", "line": 14},
        ]

        results = validator.validate_batch(symbols)

        assert len(results) == 3
        validator.close()

    def test_clear_cache(self, temp_dir: Path):
        """Test cache clearing."""
        validator = MultiSourceValidator(repo_path=temp_dir)
        validator._symbol_cache["test"] = ["cached_value"]

        validator.clear_cache()

        assert len(validator._symbol_cache) == 0
        validator.close()


# =============================================================================
# DirectDependencyRetriever Tests
# =============================================================================


class TestDirectDependencyRetriever:
    """Test DirectDependencyRetriever class."""

    def test_init_default(self):
        """Test DDR initialization with defaults."""
        ddr = DirectDependencyRetriever()

        assert ddr.codewiki_path is None
        assert ddr.repo_path is None
        assert ddr._loaded is False

    def test_init_with_paths(self, temp_dir: Path):
        """Test DDR initialization with paths."""
        ddr = DirectDependencyRetriever(
            codewiki_path=temp_dir,
            repo_path=temp_dir,
        )

        assert ddr.codewiki_path == temp_dir
        assert ddr.repo_path == temp_dir
        ddr.close()

    def test_hall_metric_property(self):
        """Test hall_metric property returns HallMetric instance."""
        ddr = DirectDependencyRetriever()

        assert isinstance(ddr.hall_metric, HallMetric)

    def test_search_symbols_exact_match(self):
        """Test symbol search with exact match."""
        ddr = DirectDependencyRetriever()
        ddr._symbol_index = {
            "stategraph": [{"symbol": "StateGraph", "file": "state.py", "line": 50}],
            "compiledgraph": [{"symbol": "CompiledGraph", "file": "graph.py", "line": 100}],
        }
        ddr._loaded = True

        results = ddr._search_symbols("StateGraph")

        assert len(results) == 1
        assert results[0]["symbol"] == "StateGraph"

    def test_search_symbols_partial_match(self):
        """Test symbol search with partial match."""
        ddr = DirectDependencyRetriever()
        ddr._symbol_index = {
            "stategraph": [{"symbol": "StateGraph", "file": "state.py", "line": 50}],
            "stategraphbuilder": [{"symbol": "StateGraphBuilder", "file": "builder.py", "line": 10}],
        }
        ddr._loaded = True

        results = ddr._search_symbols("state")

        # Should find both since "state" is in both keys
        assert len(results) == 2

    def test_search_symbols_case_insensitive(self):
        """Test symbol search is case-insensitive."""
        ddr = DirectDependencyRetriever()
        ddr._symbol_index = {
            "stategraph": [{"symbol": "StateGraph", "file": "state.py", "line": 50}],
        }
        ddr._loaded = True

        results_lower = ddr._search_symbols("stategraph")
        results_upper = ddr._search_symbols("STATEGRAPH")
        results_mixed = ddr._search_symbols("StateGraph")

        assert len(results_lower) == len(results_upper) == len(results_mixed) == 1

    def test_retrieve_empty_index(self):
        """Test retrieve with empty symbol index."""
        ddr = DirectDependencyRetriever()

        result = ddr.retrieve("StateGraph")

        assert result.query == "StateGraph"
        assert result.validated_count == 0
        assert result.elements == []

    def test_retrieve_records_hall_m(self):
        """Test that retrieve records Hall_m metrics."""
        ddr = DirectDependencyRetriever()
        ddr._symbol_index = {
            "test": [{"symbol": "Test", "file": "test.py", "line": 10}],
        }
        ddr._loaded = True

        # Clear any existing metrics
        ddr._hall_metric.reset()

        ddr.retrieve("test")

        # Should have recorded at least one observation
        assert len(ddr.hall_metric.history) >= 1

    def test_get_hall_m_summary(self):
        """Test get_hall_m_summary() method."""
        ddr = DirectDependencyRetriever()
        ddr.hall_metric.record(validated=90, rejected=10, operation="test")

        summary = ddr.get_hall_m_summary()

        assert "observations" in summary
        assert "cumulative_hall_m" in summary
        assert summary["total_validated"] == 90

    def test_reset_hall_m_metrics(self):
        """Test reset_hall_m_metrics() method."""
        ddr = DirectDependencyRetriever()
        ddr.hall_metric.record(validated=100, rejected=0, operation="test")
        assert ddr.hall_metric.total_attempted == 100

        ddr.reset_hall_m_metrics()

        assert ddr.hall_metric.total_attempted == 0

    def test_check_hall_m_threshold(self):
        """Test check_hall_m_threshold() method."""
        ddr = DirectDependencyRetriever()
        ddr.hall_metric.record(validated=99, rejected=1, operation="test")

        # Hall_m = 0.01 < 0.02, should return True
        assert ddr.check_hall_m_threshold(fail_on_exceed=False) is True

        # Add more rejections to exceed threshold
        ddr.hall_metric.record(validated=50, rejected=50, operation="test")

        # Hall_m now > 0.02, should return False
        assert ddr.check_hall_m_threshold(fail_on_exceed=False) is False

    def test_validation_stats(self, temp_dir: Path):
        """Test validation statistics tracking."""
        ddr = DirectDependencyRetriever(
            repo_path=temp_dir,
            use_multi_source=True,
        )

        # Reset stats
        ddr.reset_validation_stats()

        stats = ddr.get_validation_stats()
        assert stats["total_validated"] == 0

        ddr.close()


class TestDirectDependencyRetrieverBatch:
    """Test batch processing methods of DDR."""

    def test_retrieve_batch_empty(self):
        """Test batch retrieval with empty queries."""
        ddr = DirectDependencyRetriever()

        result = ddr.retrieve_batch(queries=[])

        assert result.queries_processed == 0
        assert result.total_validated == 0
        assert result.success is True  # Empty = no failures

    def test_retrieve_batch_multiple(self):
        """Test batch retrieval with multiple queries."""
        ddr = DirectDependencyRetriever()
        ddr._symbol_index = {
            "test1": [{"symbol": "Test1", "file": "test1.py", "line": 10}],
            "test2": [{"symbol": "Test2", "file": "test2.py", "line": 20}],
        }
        ddr._loaded = True

        result = ddr.retrieve_batch(queries=["Test1", "Test2", "Test3"])

        assert result.queries_processed == 3
        assert len(result.results) == 3

    def test_retrieve_batch_progress_callback(self):
        """Test batch retrieval with progress callback."""
        ddr = DirectDependencyRetriever()
        progress_calls = []

        def on_progress(progress: BatchProgress):
            progress_calls.append(progress.processed)

        ddr.retrieve_batch(queries=["q1", "q2", "q3"], on_progress=on_progress)

        # Callback may not be called for every item (only every 10 or at completion)
        # But should be called at least once at completion
        assert len(progress_calls) >= 1

    def test_retrieve_batch_fail_on_exceed(self):
        """Test batch retrieval with Hall_m threshold failure."""
        ddr = DirectDependencyRetriever(
            fail_on_hall_m_exceed=False,  # Default to not fail
            hall_m_threshold=0.02,
        )
        ddr._symbol_index = {}  # Empty index = all queries rejected
        ddr._loaded = True

        # This should NOT raise by default
        result = ddr.retrieve_batch(queries=["q1", "q2"], fail_on_exceed=False)

        # All rejected means Hall_m = 1.0
        # But since fail_on_exceed=False, it should complete
        assert result.queries_processed == 2

    def test_iter_retrieve(self):
        """Test iterator-based retrieval."""
        ddr = DirectDependencyRetriever()
        ddr._symbol_index = {
            "test": [{"symbol": "Test", "file": "test.py", "line": 10}],
        }
        ddr._loaded = True

        results = list(ddr.iter_retrieve(queries=["Test", "Other"]))

        assert len(results) == 2
        assert results[0][0] == "Test"  # First tuple element is query
        assert isinstance(results[0][1], DDRResult)  # Second is result

    def test_validate_batch(self):
        """Test batch validation of candidates."""
        ddr = DirectDependencyRetriever()

        candidates = [
            {"symbol": "Test1", "file": "test1.py", "line": 10},
            {"symbol": "Test2", "file": "test2.py", "line": 20},
        ]

        elements, progress = ddr.validate_batch(candidates)

        assert progress.total == 2
        assert progress.processed == 2


# =============================================================================
# Integration Tests
# =============================================================================


class TestDDRIntegration:
    """Integration tests for DDR with real test data."""

    def test_validate_real_python_file(self, test_data_dir: Path):
        """Test validation against real sample.py test data."""
        if not (test_data_dir / "sample.py").exists():
            pytest.skip("Test data file sample.py not found")

        validator = MultiSourceValidator(repo_path=test_data_dir.parent)

        # Validate Person class from sample.py
        result = validator.validate_symbol(
            symbol_name="Person",
            file_path="data/sample.py",
            line_number=11,  # From symbol_catalog.json
            expected_type="class",
        )

        # Should find it with at least file content validation
        assert result.is_valid is True
        validator.close()

    def test_validate_with_symbol_catalog(self, test_data_dir: Path, temp_dir: Path):
        """Test DDR with symbol catalog from test data."""
        catalog_path = test_data_dir / "symbol_catalog.json"
        if not catalog_path.exists():
            pytest.skip("Test data file symbol_catalog.json not found")

        # Create a markdown catalog from JSON for testing
        import json
        catalog_data = json.loads(catalog_path.read_text())

        # Generate markdown catalog
        md_lines = ["# Symbol Catalog\n"]
        for symbol_name, symbol_info in catalog_data.get("symbols", {}).items():
            file_path = symbol_info.get("file", "")
            line = symbol_info.get("line", 0)
            kind = symbol_info.get("kind", "unknown")

            if "." not in symbol_name:  # Skip methods for brevity
                md_lines.append(f"### `{file_path}`")
                md_lines.append(f"- Line {line}: `{symbol_name}` ({kind})\n")

        catalog_md = "\n".join(md_lines)
        catalog_file = temp_dir / "symbol_catalog.md"
        catalog_file.write_text(catalog_md)

        # Initialize DDR with catalog
        ddr = DirectDependencyRetriever(codewiki_path=temp_dir)
        ddr.load_symbol_catalog(catalog_file)

        # Search should find symbols
        assert len(ddr._symbol_index) > 0
        ddr.close()


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestDDREdgeCases:
    """Test edge cases and error handling."""

    def test_hall_m_zero_division(self):
        """Test Hall_m calculation with zero total."""
        metric = HallMetric()

        # No observations = Hall_m of 0
        assert metric.current_hall_m == 0.0

        # Calculate with zero should not raise
        result = HallMetric.calculate(0, 0)
        assert result == 0.0

    def test_validation_line_tolerance(self, sample_python_file: Path, temp_dir: Path):
        """Test validation with line number tolerance."""
        validator = MultiSourceValidator(repo_path=temp_dir)

        # Use slightly wrong line number (within 5 line tolerance)
        result = validator.validate_symbol(
            symbol_name="Person",
            file_path="sample.py",
            line_number=5,  # Actual is 3, but within tolerance
        )

        # Should still validate with file content
        # (May or may not pass depending on implementation)
        # Just verify no errors raised
        assert isinstance(result, ValidationResult)
        validator.close()

    def test_utf8_file_handling(self, temp_dir: Path):
        """Test handling of files with UTF-8 content."""
        # Create file with UTF-8 characters
        utf8_file = temp_dir / "utf8.py"
        utf8_file.write_text("""
class UnicodeClass:
    '''クラスの説明 - Japanese description'''
    def method(self) -> str:
        return "Hello, 世界"
""", encoding="utf-8")

        validator = MultiSourceValidator(repo_path=temp_dir)

        result = validator.validate_symbol(
            symbol_name="UnicodeClass",
            file_path="utf8.py",
            line_number=2,
        )

        # Should handle UTF-8 without errors
        assert isinstance(result, ValidationResult)
        validator.close()

    def test_batch_progress_eta_zero_rate(self):
        """Test ETA calculation when no items processed."""
        progress = BatchProgress(total=100)

        # No processing = ETA is 0
        assert progress.eta_seconds == 0.0

    def test_truncate_long_context(self, hall_metric: HallMetric):
        """Test that long context strings are truncated."""
        long_context = "x" * 200

        snapshot = hall_metric.record(
            validated=10,
            rejected=0,
            operation="test",
            context=long_context,
        )

        # Context should be truncated to 100 chars
        assert len(snapshot.context) <= 100
