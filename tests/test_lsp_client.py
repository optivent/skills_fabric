"""Unit tests for LSP client communication and parsing.

This module tests the LSP client implementation:
- JSON-RPC 2.0 message framing with Content-Length headers
- JsonRpcMessage dataclass for request/response/notification handling
- MessageBuffer for parsing LSP messages from byte streams
- Hover request/response parsing
- Definition request/response parsing (Location and LocationLink)
- References request/response parsing
- Fallback mode when LSP server is unavailable

Test coverage includes:
- Message framing and parsing
- Request ID handling
- Error handling and edge cases
- Location parsing from LSP formats
- CodeAnalyzer fallback behavior
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# Import lsp_client module directly to avoid heavy dependencies from skills_fabric.__init__
_src_path = Path(__file__).parent.parent / "src"

# First, ensure observability.logging is available (lsp_client depends on it)
_logging_path = _src_path / "skills_fabric" / "observability" / "logging.py"
_logging_spec = importlib.util.spec_from_file_location("skills_fabric.observability.logging", _logging_path)
_logging_module = importlib.util.module_from_spec(_logging_spec)
sys.modules["skills_fabric.observability.logging"] = _logging_module
_logging_spec.loader.exec_module(_logging_module)

# Now import the lsp_client module
_lsp_client_path = _src_path / "skills_fabric" / "analyze" / "lsp_client.py"
_spec = importlib.util.spec_from_file_location("skills_fabric.analyze.lsp_client", _lsp_client_path)
_lsp_client_module = importlib.util.module_from_spec(_spec)
sys.modules["skills_fabric.analyze.lsp_client"] = _lsp_client_module
_spec.loader.exec_module(_lsp_client_module)

# Import classes we need to test
LSPClient = _lsp_client_module.LSPClient
MessageBuffer = _lsp_client_module.MessageBuffer
JsonRpcMessage = _lsp_client_module.JsonRpcMessage
Location = _lsp_client_module.Location
HoverInfo = _lsp_client_module.HoverInfo
LSPSymbol = _lsp_client_module.LSPSymbol


# =============================================================================
# Sample Data for Testing
# =============================================================================

SAMPLE_PYTHON_CODE = '''"""Sample module for LSP testing."""

class SampleClass:
    """A sample class."""

    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        """Return the name."""
        return self.name


def standalone_function(x: int) -> int:
    """A standalone function."""
    return x * 2
'''


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def message_buffer() -> MessageBuffer:
    """Create a fresh MessageBuffer instance."""
    return MessageBuffer()


@pytest.fixture
def sample_json_rpc_request() -> dict:
    """Create a sample JSON-RPC request."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "textDocument/hover",
        "params": {
            "textDocument": {"uri": "file:///test/file.py"},
            "position": {"line": 5, "character": 10}
        }
    }


@pytest.fixture
def sample_json_rpc_response() -> dict:
    """Create a sample JSON-RPC response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef sample_function() -> str\n```"
            },
            "range": {
                "start": {"line": 5, "character": 4},
                "end": {"line": 5, "character": 20}
            }
        }
    }


@pytest.fixture
def sample_json_rpc_notification() -> dict:
    """Create a sample JSON-RPC notification (no id)."""
    return {
        "jsonrpc": "2.0",
        "method": "textDocument/publishDiagnostics",
        "params": {
            "uri": "file:///test/file.py",
            "diagnostics": []
        }
    }


@pytest.fixture
def sample_json_rpc_error() -> dict:
    """Create a sample JSON-RPC error response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32600,
            "message": "Invalid Request"
        }
    }


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory."""
    return tmp_path


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(SAMPLE_PYTHON_CODE)
    return file_path


# =============================================================================
# JsonRpcMessage Tests
# =============================================================================


class TestJsonRpcMessage:
    """Test JSON-RPC 2.0 message dataclass."""

    def test_from_dict_request(self, sample_json_rpc_request: dict):
        """Test creating JsonRpcMessage from request dict."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_request)

        assert message.jsonrpc == "2.0"
        assert message.id == 1
        assert message.method == "textDocument/hover"
        assert message.params is not None
        assert message.result is None
        assert message.error is None

    def test_from_dict_response(self, sample_json_rpc_response: dict):
        """Test creating JsonRpcMessage from response dict."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_response)

        assert message.jsonrpc == "2.0"
        assert message.id == 1
        assert message.method is None
        assert message.result is not None
        assert message.error is None

    def test_from_dict_notification(self, sample_json_rpc_notification: dict):
        """Test creating JsonRpcMessage from notification dict."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_notification)

        assert message.jsonrpc == "2.0"
        assert message.id is None
        assert message.method == "textDocument/publishDiagnostics"

    def test_from_dict_error(self, sample_json_rpc_error: dict):
        """Test creating JsonRpcMessage from error response dict."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_error)

        assert message.jsonrpc == "2.0"
        assert message.id == 1
        assert message.error is not None
        assert message.error["code"] == -32600

    def test_is_request(self, sample_json_rpc_request: dict):
        """Test is_request property."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_request)

        assert message.is_request is True
        assert message.is_response is False
        assert message.is_notification is False

    def test_is_response(self, sample_json_rpc_response: dict):
        """Test is_response property."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_response)

        assert message.is_request is False
        assert message.is_response is True
        assert message.is_notification is False

    def test_is_notification(self, sample_json_rpc_notification: dict):
        """Test is_notification property."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_notification)

        assert message.is_request is False
        assert message.is_response is False
        assert message.is_notification is True

    def test_to_dict_round_trip(self, sample_json_rpc_request: dict):
        """Test that to_dict produces correct output."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_request)
        result = message.to_dict()

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert result["method"] == "textDocument/hover"
        assert "params" in result

    def test_to_dict_omits_none_fields(self):
        """Test that to_dict omits None fields."""
        message = JsonRpcMessage(jsonrpc="2.0", id=1, result={"test": "value"})
        result = message.to_dict()

        assert "method" not in result
        assert "params" not in result
        assert "error" not in result

    def test_error_response_is_response(self, sample_json_rpc_error: dict):
        """Test that error responses are identified as responses."""
        message = JsonRpcMessage.from_dict(sample_json_rpc_error)

        assert message.is_response is True


# =============================================================================
# MessageBuffer Tests (JSON-RPC Message Framing)
# =============================================================================


class TestMessageBuffer:
    """Test MessageBuffer for LSP Content-Length framing."""

    def test_empty_buffer_returns_none(self, message_buffer: MessageBuffer):
        """Test that empty buffer returns None."""
        result = message_buffer.try_parse_message()
        assert result is None

    def test_parse_complete_message(self, message_buffer: MessageBuffer):
        """Test parsing a complete LSP message."""
        message = {"jsonrpc": "2.0", "id": 1, "result": {}}
        body = json.dumps(message).encode("utf-8")
        content = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body

        message_buffer.append(content)
        result = message_buffer.try_parse_message()

        assert result is not None
        assert result.jsonrpc == "2.0"
        assert result.id == 1

    def test_parse_message_with_unicode(self, message_buffer: MessageBuffer):
        """Test parsing message with unicode content (UTF-8 bytes)."""
        message = {"jsonrpc": "2.0", "id": 1, "result": {"content": "日本語"}}
        body = json.dumps(message).encode("utf-8")
        # Content-Length must be byte length, not character length
        content = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body

        message_buffer.append(content)
        result = message_buffer.try_parse_message()

        assert result is not None
        assert result.result["content"] == "日本語"

    def test_partial_header_returns_none(self, message_buffer: MessageBuffer):
        """Test that partial headers return None."""
        message_buffer.append(b"Content-Leng")
        result = message_buffer.try_parse_message()
        assert result is None

    def test_partial_body_returns_none(self, message_buffer: MessageBuffer):
        """Test that partial body returns None."""
        message = {"jsonrpc": "2.0", "id": 1}
        body = json.dumps(message).encode("utf-8")
        # Send header but only part of body
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        partial_body = body[:5]

        message_buffer.append(header + partial_body)
        result = message_buffer.try_parse_message()

        assert result is None

    def test_multiple_messages(self, message_buffer: MessageBuffer):
        """Test parsing multiple consecutive messages."""
        messages = [
            {"jsonrpc": "2.0", "id": 1, "result": {"first": True}},
            {"jsonrpc": "2.0", "id": 2, "result": {"second": True}},
        ]

        # Build combined content
        combined = b""
        for msg in messages:
            body = json.dumps(msg).encode("utf-8")
            combined += f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body

        message_buffer.append(combined)

        # Parse first message
        result1 = message_buffer.try_parse_message()
        assert result1 is not None
        assert result1.id == 1
        assert result1.result["first"] is True

        # Parse second message
        result2 = message_buffer.try_parse_message()
        assert result2 is not None
        assert result2.id == 2
        assert result2.result["second"] is True

        # No more messages
        result3 = message_buffer.try_parse_message()
        assert result3 is None

    def test_incremental_append(self, message_buffer: MessageBuffer):
        """Test building up a message incrementally."""
        message = {"jsonrpc": "2.0", "id": 1, "result": {}}
        body = json.dumps(message).encode("utf-8")
        full_content = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body

        # Append in chunks
        for i in range(len(full_content)):
            message_buffer.append(full_content[i:i + 1])

        result = message_buffer.try_parse_message()
        assert result is not None
        assert result.id == 1

    def test_clear_buffer(self, message_buffer: MessageBuffer):
        """Test clearing the buffer."""
        message = {"jsonrpc": "2.0", "id": 1, "result": {}}
        body = json.dumps(message).encode("utf-8")
        content = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8") + body

        message_buffer.append(content)
        message_buffer.clear()

        result = message_buffer.try_parse_message()
        assert result is None

    def test_missing_content_length_skips_message(self, message_buffer: MessageBuffer):
        """Test that missing Content-Length is handled gracefully."""
        # Invalid header without Content-Length
        message_buffer.append(b"X-Custom-Header: value\r\n\r\n{}")
        result = message_buffer.try_parse_message()
        # Should return None and skip to next message
        assert result is None

    def test_invalid_json_skips_message(self, message_buffer: MessageBuffer):
        """Test that invalid JSON is handled gracefully."""
        invalid_body = b"not valid json"
        content = f"Content-Length: {len(invalid_body)}\r\n\r\n".encode("utf-8") + invalid_body

        message_buffer.append(content)
        result = message_buffer.try_parse_message()
        # Should return None due to JSON parse error
        assert result is None

    def test_extra_headers_ignored(self, message_buffer: MessageBuffer):
        """Test that extra headers are ignored but message still parses."""
        message = {"jsonrpc": "2.0", "id": 1, "result": {}}
        body = json.dumps(message).encode("utf-8")
        content = (
            f"Content-Length: {len(body)}\r\n"
            "Content-Type: application/json\r\n"
            "X-Custom-Header: value\r\n"
            "\r\n"
        ).encode("utf-8") + body

        message_buffer.append(content)
        result = message_buffer.try_parse_message()

        assert result is not None
        assert result.id == 1


# =============================================================================
# Location Tests
# =============================================================================


class TestLocation:
    """Test Location dataclass and parsing."""

    def test_location_str(self):
        """Test Location.__str__() returns file:line format."""
        loc = Location(file="/path/to/file.py", line=10, column=5)
        # Should be 1-indexed for display
        assert str(loc) == "/path/to/file.py:11"

    def test_location_to_citation(self):
        """Test Location.to_citation() returns file:line format."""
        loc = Location(file="/path/to/file.py", line=10, column=5)
        assert loc.to_citation() == "/path/to/file.py:11"

    def test_location_to_full_citation(self):
        """Test Location.to_full_citation() returns file:line:column format."""
        loc = Location(file="/path/to/file.py", line=10, column=5)
        assert loc.to_full_citation() == "/path/to/file.py:11:6"

    def test_from_lsp_location(self):
        """Test Location.from_lsp_location() with standard LSP Location."""
        lsp_loc = {
            "uri": "file:///path/to/file.py",
            "range": {
                "start": {"line": 5, "character": 10},
                "end": {"line": 5, "character": 20}
            }
        }

        loc = Location.from_lsp_location(lsp_loc)

        assert loc is not None
        assert loc.file == "/path/to/file.py"
        assert loc.line == 5
        assert loc.column == 10
        assert loc.end_line == 5
        assert loc.end_column == 20

    def test_from_lsp_location_link(self):
        """Test Location.from_lsp_location_link() with LSP LocationLink (3.14+)."""
        lsp_link = {
            "originSelectionRange": {
                "start": {"line": 10, "character": 0},
                "end": {"line": 10, "character": 10}
            },
            "targetUri": "file:///path/to/target.py",
            "targetRange": {
                "start": {"line": 20, "character": 0},
                "end": {"line": 30, "character": 0}
            },
            "targetSelectionRange": {
                "start": {"line": 21, "character": 4},
                "end": {"line": 21, "character": 15}
            }
        }

        loc = Location.from_lsp_location_link(lsp_link)

        assert loc is not None
        assert loc.file == "/path/to/target.py"
        # Should use targetSelectionRange for precise position
        assert loc.line == 21
        assert loc.column == 4

    def test_from_lsp_location_missing_uri(self):
        """Test Location.from_lsp_location() returns None for missing uri."""
        lsp_loc = {"range": {"start": {"line": 0, "character": 0}}}
        loc = Location.from_lsp_location(lsp_loc)
        # Should handle missing uri gracefully
        assert loc is not None  # Still creates location with empty file

    def test_from_lsp_location_empty_dict(self):
        """Test Location.from_lsp_location() handles empty dict."""
        loc = Location.from_lsp_location({})
        assert loc is not None
        assert loc.file == ""
        assert loc.line == 0

    def test_from_lsp_location_link_fallback_to_target_range(self):
        """Test LocationLink uses targetRange when targetSelectionRange missing."""
        lsp_link = {
            "targetUri": "file:///path/to/file.py",
            "targetRange": {
                "start": {"line": 10, "character": 0},
                "end": {"line": 15, "character": 0}
            }
        }

        loc = Location.from_lsp_location_link(lsp_link)

        assert loc is not None
        assert loc.line == 10


# =============================================================================
# HoverInfo Tests
# =============================================================================


class TestHoverInfo:
    """Test HoverInfo dataclass."""

    def test_hover_info_creation(self):
        """Test creating HoverInfo with all fields."""
        hover = HoverInfo(
            content="def sample() -> str",
            language="python",
            range_start=(5, 0),
            range_end=(5, 20)
        )

        assert hover.content == "def sample() -> str"
        assert hover.language == "python"
        assert hover.range_start == (5, 0)
        assert hover.range_end == (5, 20)


# =============================================================================
# LSPSymbol Tests
# =============================================================================


class TestLSPSymbol:
    """Test LSPSymbol dataclass."""

    def test_lsp_symbol_creation(self):
        """Test creating LSPSymbol."""
        symbol = LSPSymbol(
            name="TestClass",
            kind="class",
            range_start=(1, 0),
            range_end=(10, 0),
            children=[]
        )

        assert symbol.name == "TestClass"
        assert symbol.kind == "class"
        assert symbol.range_start == (1, 0)
        assert symbol.range_end == (10, 0)
        assert symbol.children == []

    def test_lsp_symbol_with_children(self):
        """Test LSPSymbol with nested children."""
        child = LSPSymbol(
            name="method",
            kind="method",
            range_start=(5, 4),
            range_end=(8, 0),
            children=[]
        )

        parent = LSPSymbol(
            name="MyClass",
            kind="class",
            range_start=(1, 0),
            range_end=(10, 0),
            children=[child]
        )

        assert len(parent.children) == 1
        assert parent.children[0].name == "method"


# =============================================================================
# LSPClient Tests (Mocked)
# =============================================================================


class TestLSPClientProperties:
    """Test LSPClient properties and basic state."""

    def test_is_available_false_when_not_started(self):
        """Test is_available returns False when server not started."""
        client = LSPClient()
        assert client.is_available is False

    def test_initialization_defaults(self):
        """Test LSPClient initialization with default values."""
        client = LSPClient()

        assert client._process is None
        assert client._request_id == 0
        assert client._language is None
        assert client._running is False

    def test_symbol_kind_name_mapping(self):
        """Test _symbol_kind_name returns correct names."""
        assert LSPClient._symbol_kind_name(5) == "class"
        assert LSPClient._symbol_kind_name(6) == "method"
        assert LSPClient._symbol_kind_name(12) == "function"
        assert LSPClient._symbol_kind_name(13) == "variable"
        assert LSPClient._symbol_kind_name(999) == "unknown"


class TestLSPClientHover:
    """Test LSP hover functionality."""

    def test_get_hover_returns_none_when_no_process(self):
        """Test get_hover returns None when server not running."""
        client = LSPClient()
        result = client.get_hover(Path("/test/file.py"), 0, 0)
        assert result is None

    def test_get_hover_parses_string_contents(self):
        """Test get_hover handles string contents."""
        client = LSPClient()
        client._process = MagicMock()

        # Mock _send_request to return hover result with string contents
        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = {
                "contents": "Simple hover text"
            }

            result = client.get_hover(Path("/test/file.py"), 5, 10)

            assert result is not None
            assert result.content == "Simple hover text"
            assert result.language == ""

    def test_get_hover_parses_dict_contents(self):
        """Test get_hover handles dict contents with language."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = {
                "contents": {
                    "value": "```python\ndef foo():\n    pass\n```",
                    "language": "markdown"
                },
                "range": {
                    "start": {"line": 5, "character": 4},
                    "end": {"line": 5, "character": 10}
                }
            }

            result = client.get_hover(Path("/test/file.py"), 5, 5)

            assert result is not None
            assert "def foo()" in result.content
            assert result.language == "markdown"
            assert result.range_start == (5, 4)
            assert result.range_end == (5, 10)

    def test_get_hover_handles_empty_result(self):
        """Test get_hover handles None/empty result from server."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = None

            result = client.get_hover(Path("/test/file.py"), 5, 5)
            assert result is None


class TestLSPClientDefinition:
    """Test LSP go-to-definition functionality."""

    def test_get_definition_returns_none_when_no_process(self):
        """Test get_definition returns None when server not running."""
        client = LSPClient()
        result = client.get_definition(Path("/test/file.py"), 0, 0)
        assert result is None

    def test_get_definition_parses_single_location(self):
        """Test get_definition with single Location result."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            # LSP can return a single Location object
            mock_request.return_value = {
                "uri": "file:///path/to/def.py",
                "range": {
                    "start": {"line": 10, "character": 0},
                    "end": {"line": 10, "character": 15}
                }
            }

            result = client.get_definition(Path("/test/file.py"), 5, 5)

            assert result is not None
            assert result.file == "/path/to/def.py"
            assert result.line == 10

    def test_get_all_definitions_parses_location_array(self):
        """Test get_all_definitions with array of Locations."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = [
                {
                    "uri": "file:///path/to/def1.py",
                    "range": {"start": {"line": 10, "character": 0}, "end": {"line": 10, "character": 10}}
                },
                {
                    "uri": "file:///path/to/def2.py",
                    "range": {"start": {"line": 20, "character": 0}, "end": {"line": 20, "character": 10}}
                }
            ]

            results = client.get_all_definitions(Path("/test/file.py"), 5, 5)

            assert len(results) == 2
            assert results[0].file == "/path/to/def1.py"
            assert results[1].file == "/path/to/def2.py"

    def test_get_all_definitions_parses_location_link(self):
        """Test get_all_definitions handles LocationLink (LSP 3.14+)."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = [{
                "targetUri": "file:///path/to/target.py",
                "targetRange": {
                    "start": {"line": 15, "character": 0},
                    "end": {"line": 20, "character": 0}
                },
                "targetSelectionRange": {
                    "start": {"line": 16, "character": 4},
                    "end": {"line": 16, "character": 12}
                }
            }]

            results = client.get_all_definitions(Path("/test/file.py"), 5, 5)

            assert len(results) == 1
            assert results[0].file == "/path/to/target.py"
            assert results[0].line == 16  # Uses targetSelectionRange

    def test_find_definition_returns_citation(self):
        """Test find_definition returns citation string."""
        client = LSPClient()
        client._process = MagicMock()
        client._running = True

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = {
                "uri": "file:///path/to/def.py",
                "range": {"start": {"line": 10, "character": 0}, "end": {"line": 10, "character": 10}}
            }

            # Mock open/close document
            with patch.object(client, "open_document", return_value=True):
                with patch.object(client, "close_document", return_value=True):
                    result = client.find_definition(Path("/test/file.py"), 5, 5)

            # Line should be 1-indexed for citation
            assert result == "/path/to/def.py:11"


class TestLSPClientReferences:
    """Test LSP find-references functionality."""

    def test_get_references_returns_empty_when_no_process(self):
        """Test get_references returns empty list when server not running."""
        client = LSPClient()
        result = client.get_references(Path("/test/file.py"), 0, 0)
        assert result == []

    def test_get_references_parses_locations(self):
        """Test get_references parses array of locations."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = [
                {"uri": "file:///test/file1.py", "range": {"start": {"line": 5, "character": 0}, "end": {"line": 5, "character": 10}}},
                {"uri": "file:///test/file2.py", "range": {"start": {"line": 10, "character": 0}, "end": {"line": 10, "character": 10}}},
                {"uri": "file:///test/file3.py", "range": {"start": {"line": 15, "character": 0}, "end": {"line": 15, "character": 10}}},
            ]

            results = client.get_references(Path("/test/file.py"), 5, 5)

            assert len(results) == 3
            assert results[0].file == "/test/file1.py"
            assert results[1].file == "/test/file2.py"
            assert results[2].file == "/test/file3.py"

    def test_get_references_count(self):
        """Test get_references_count returns correct count."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "get_references") as mock_refs:
            mock_refs.return_value = [
                Location(file="/test/file1.py", line=5, column=0),
                Location(file="/test/file2.py", line=10, column=0),
            ]

            count = client.get_references_count(Path("/test/file.py"), 5, 5)
            assert count == 2

    def test_get_references_by_file(self):
        """Test get_references_by_file groups results."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "get_references") as mock_refs:
            mock_refs.return_value = [
                Location(file="/test/file1.py", line=5, column=0),
                Location(file="/test/file1.py", line=10, column=0),
                Location(file="/test/file2.py", line=15, column=0),
            ]

            grouped = client.get_references_by_file(Path("/test/file.py"), 5, 5)

            assert len(grouped) == 2
            assert "/test/file1.py" in grouped
            assert "/test/file2.py" in grouped
            assert len(grouped["/test/file1.py"]) == 2
            assert len(grouped["/test/file2.py"]) == 1

    def test_find_references_returns_citations(self):
        """Test find_references returns citation strings."""
        client = LSPClient()
        client._process = MagicMock()
        client._running = True

        with patch.object(client, "get_references") as mock_refs:
            mock_refs.return_value = [
                Location(file="/test/file1.py", line=5, column=0),
                Location(file="/test/file2.py", line=10, column=0),
            ]

            with patch.object(client, "open_document", return_value=True):
                with patch.object(client, "close_document", return_value=True):
                    results = client.find_references(Path("/test/file.py"), 5, 5)

            # Lines should be 1-indexed in citations
            assert "/test/file1.py:6" in results
            assert "/test/file2.py:11" in results


class TestLSPClientDocumentLifecycle:
    """Test document open/close lifecycle."""

    def test_open_document_nonexistent_file(self, temp_dir: Path):
        """Test open_document returns False for non-existent file."""
        client = LSPClient()
        client._process = MagicMock()
        client._running = True

        with patch.object(client, "_send_notification"):
            result = client.open_document(temp_dir / "does_not_exist.py")
            assert result is False

    def test_open_document_sends_notification(self, sample_python_file: Path):
        """Test open_document sends didOpen notification."""
        client = LSPClient()
        client._process = MagicMock()
        client._running = True

        with patch.object(client, "_send_notification") as mock_notify:
            result = client.open_document(sample_python_file)

            assert result is True
            mock_notify.assert_called_once()
            call_args = mock_notify.call_args[0]
            assert call_args[0] == "textDocument/didOpen"
            assert "textDocument" in call_args[1]

    def test_close_document_sends_notification(self, sample_python_file: Path):
        """Test close_document sends didClose notification."""
        client = LSPClient()
        client._process = MagicMock()
        client._running = True

        with patch.object(client, "_send_notification") as mock_notify:
            result = client.close_document(sample_python_file)

            assert result is True
            mock_notify.assert_called_once()
            call_args = mock_notify.call_args[0]
            assert call_args[0] == "textDocument/didClose"


# =============================================================================
# Fallback Mode Tests (CodeAnalyzer Integration)
# =============================================================================


class TestFallbackMode:
    """Test LSP-to-AST fallback behavior."""

    def test_lsp_client_unavailable_flag(self):
        """Test LSPClient.is_available when initialization fails."""
        client = LSPClient()
        client._initialization_failed = True
        assert client.is_available is False

    def test_lsp_client_available_when_running(self):
        """Test LSPClient.is_available when properly running."""
        client = LSPClient()
        client._process = MagicMock()
        client._process.poll.return_value = None  # Process running
        client._running = True
        client._initialization_failed = False

        assert client.is_available is True

    def test_lsp_client_unavailable_when_process_stopped(self):
        """Test LSPClient.is_available when process has stopped."""
        client = LSPClient()
        client._process = MagicMock()
        client._process.poll.return_value = 1  # Process exited
        client._running = True

        assert client.is_available is False

    def test_lsp_client_unavailable_when_not_running_flag(self):
        """Test LSPClient.is_available when _running is False."""
        client = LSPClient()
        client._process = MagicMock()
        client._process.poll.return_value = None
        client._running = False

        assert client.is_available is False


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestLSPClientErrorHandling:
    """Test error handling in LSP client."""

    def test_get_hover_handles_non_dict_contents(self):
        """Test get_hover handles list or other contents types."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            # Some servers return contents as array
            mock_request.return_value = {
                "contents": ["line1", "line2"]
            }

            result = client.get_hover(Path("/test/file.py"), 5, 5)

            assert result is not None
            # Should convert to string representation
            assert "line1" in result.content

    def test_get_definition_handles_empty_result(self):
        """Test get_definition handles empty/None result."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = None

            result = client.get_definition(Path("/test/file.py"), 5, 5)
            assert result is None

    def test_get_references_handles_non_list_result(self):
        """Test get_references handles non-list result."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = {"unexpected": "format"}

            result = client.get_references(Path("/test/file.py"), 5, 5)
            assert result == []

    def test_parse_location_or_link_handles_empty_item(self):
        """Test _parse_location_or_link handles empty dict."""
        client = LSPClient()
        result = client._parse_location_or_link({})
        assert result is None

    def test_parse_location_or_link_handles_none(self):
        """Test _parse_location_or_link handles None."""
        client = LSPClient()
        result = client._parse_location_or_link(None)
        assert result is None


# =============================================================================
# Document Symbol Tests
# =============================================================================


class TestLSPClientDocumentSymbols:
    """Test document symbol extraction."""

    def test_get_document_symbols_returns_empty_when_no_process(self):
        """Test get_document_symbols returns empty when server not running."""
        client = LSPClient()
        result = client.get_document_symbols(Path("/test/file.py"))
        assert result == []

    def test_get_document_symbols_parses_hierarchy(self):
        """Test get_document_symbols parses hierarchical symbols."""
        client = LSPClient()
        client._process = MagicMock()

        with patch.object(client, "_send_request") as mock_request:
            mock_request.return_value = [
                {
                    "name": "MyClass",
                    "kind": 5,  # class
                    "range": {"start": {"line": 0, "character": 0}, "end": {"line": 10, "character": 0}},
                    "children": [
                        {
                            "name": "my_method",
                            "kind": 6,  # method
                            "range": {"start": {"line": 2, "character": 4}, "end": {"line": 5, "character": 0}},
                            "children": []
                        }
                    ]
                }
            ]

            result = client.get_document_symbols(Path("/test/file.py"))

            assert len(result) == 1
            assert result[0].name == "MyClass"
            assert result[0].kind == "class"
            assert len(result[0].children) == 1
            assert result[0].children[0].name == "my_method"
            assert result[0].children[0].kind == "method"


# =============================================================================
# Integration-Style Tests (With Mocked Server)
# =============================================================================


class TestLSPClientRequestResponse:
    """Test request/response patterns."""

    def test_send_message_fails_without_process(self):
        """Test _send_message returns False without process."""
        client = LSPClient()
        result = client._send_message({"jsonrpc": "2.0", "method": "test"})
        assert result is False

    def test_send_request_fails_without_process(self):
        """Test _send_request returns None without process."""
        client = LSPClient()
        result = client._send_request("test/method", {})
        assert result is None

    def test_pending_notifications_empty_by_default(self):
        """Test get_pending_notifications returns empty when no notifications."""
        client = LSPClient()
        notifications = client.get_pending_notifications()
        assert notifications == []
