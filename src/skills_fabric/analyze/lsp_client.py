"""Language Server Protocol client for deep code analysis.

Provides full LSP integration for:
- Hover information (types, docstrings)
- Go to definition
- Find all references
- Document symbols

Implements proper JSON-RPC 2.0 message framing with Content-Length headers
as specified in the Language Server Protocol specification.
"""
import subprocess
import json
import os
import threading
import queue
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from skills_fabric.observability.logging import get_logger

logger = get_logger("analyze.lsp_client")


@dataclass
class HoverInfo:
    """Hover information from LSP."""
    content: str
    language: str
    range_start: tuple[int, int]
    range_end: tuple[int, int]


@dataclass
class Location:
    """A location in source code.

    Represents a position in a file with file:line:column coordinates.
    Uses 0-indexed positions per LSP specification.
    """
    file: str
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def __str__(self) -> str:
        """Format as file:line for citations.

        Returns:
            String in format "file:line" or "file:line:column"
        """
        return f"{self.file}:{self.line + 1}"  # Convert to 1-indexed for display

    def to_citation(self) -> str:
        """Format as file:line citation for documentation.

        Returns:
            String in format "file:line" (1-indexed for human readability)
        """
        return f"{self.file}:{self.line + 1}"

    def to_full_citation(self) -> str:
        """Format as file:line:column citation.

        Returns:
            String in format "file:line:column" (1-indexed for human readability)
        """
        return f"{self.file}:{self.line + 1}:{self.column + 1}"

    @classmethod
    def from_lsp_location(cls, lsp_loc: dict) -> Optional["Location"]:
        """Create Location from LSP Location format.

        LSP Location format:
            {
                "uri": "file:///path/to/file.py",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                }
            }

        Args:
            lsp_loc: Dictionary in LSP Location format

        Returns:
            Location object or None if parsing fails
        """
        try:
            uri = lsp_loc.get("uri", "")
            file_path = uri.replace("file://", "")

            range_info = lsp_loc.get("range", {})
            start = range_info.get("start", {})
            end = range_info.get("end", {})

            return cls(
                file=file_path,
                line=start.get("line", 0),
                column=start.get("character", 0),
                end_line=end.get("line") if end else None,
                end_column=end.get("character") if end else None
            )
        except Exception:
            return None

    @classmethod
    def from_lsp_location_link(cls, lsp_link: dict) -> Optional["Location"]:
        """Create Location from LSP LocationLink format.

        LSP LocationLink format (LSP 3.14+):
            {
                "originSelectionRange": {...},  # optional
                "targetUri": "file:///path/to/file.py",
                "targetRange": {"start": {...}, "end": {...}},
                "targetSelectionRange": {"start": {...}, "end": {...}}
            }

        Args:
            lsp_link: Dictionary in LSP LocationLink format

        Returns:
            Location object or None if parsing fails
        """
        try:
            uri = lsp_link.get("targetUri", "")
            file_path = uri.replace("file://", "")

            # Use targetSelectionRange for precise location, fallback to targetRange
            range_info = lsp_link.get("targetSelectionRange") or lsp_link.get("targetRange", {})
            start = range_info.get("start", {})
            end = range_info.get("end", {})

            return cls(
                file=file_path,
                line=start.get("line", 0),
                column=start.get("character", 0),
                end_line=end.get("line") if end else None,
                end_column=end.get("character") if end else None
            )
        except Exception:
            return None


@dataclass
class LSPSymbol:
    """A symbol from document symbols."""
    name: str
    kind: str
    range_start: tuple[int, int]
    range_end: tuple[int, int]
    children: list["LSPSymbol"]


@dataclass
class JsonRpcMessage:
    """Represents a JSON-RPC 2.0 message.

    Per JSON-RPC 2.0 spec:
    - Requests have: jsonrpc, id, method, params (optional)
    - Responses have: jsonrpc, id, result OR error
    - Notifications have: jsonrpc, method, params (optional) - NO id
    """
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[dict] = None

    @property
    def is_notification(self) -> bool:
        """Notifications have no id field."""
        return self.id is None and self.method is not None

    @property
    def is_response(self) -> bool:
        """Responses have an id and either result or error."""
        return self.id is not None and (self.result is not None or self.error is not None)

    @property
    def is_request(self) -> bool:
        """Requests have an id and a method."""
        return self.id is not None and self.method is not None

    @classmethod
    def from_dict(cls, data: dict) -> "JsonRpcMessage":
        """Create a JsonRpcMessage from a dictionary."""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error")
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        d = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            d["id"] = self.id
        if self.method is not None:
            d["method"] = self.method
        if self.params is not None:
            d["params"] = self.params
        if self.result is not None:
            d["result"] = self.result
        if self.error is not None:
            d["error"] = self.error
        return d


class MessageBuffer:
    """Buffer for parsing JSON-RPC messages with Content-Length framing.

    The LSP protocol uses HTTP-like headers to frame JSON-RPC messages:
        Content-Length: <byte_length>\\r\\n
        [optional headers]\\r\\n
        \\r\\n
        <json body>

    This class accumulates bytes and parses complete messages.
    Content-Length is measured in bytes, not characters (important for UTF-8).
    """

    def __init__(self):
        self._buffer = b""
        self._content_length: Optional[int] = None
        self._headers_complete = False

    def append(self, data: bytes) -> None:
        """Append raw bytes to the buffer."""
        self._buffer += data

    def try_parse_message(self) -> Optional[JsonRpcMessage]:
        """Attempt to parse a complete message from the buffer.

        Returns:
            JsonRpcMessage if a complete message was parsed, None otherwise.
            The parsed message is removed from the buffer.
        """
        # Phase 1: Parse headers if we haven't yet
        if not self._headers_complete:
            header_end = self._buffer.find(b"\r\n\r\n")
            if header_end == -1:
                # Haven't received complete headers yet
                return None

            # Parse all headers
            headers_raw = self._buffer[:header_end].decode("utf-8", errors="replace")
            self._content_length = None

            for line in headers_raw.split("\r\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key == "content-length":
                        try:
                            self._content_length = int(value)
                        except ValueError:
                            logger.warning(f"Invalid Content-Length value: {value}")

            if self._content_length is None:
                # Required header missing - skip this malformed message
                logger.error("LSP message missing Content-Length header")
                self._buffer = self._buffer[header_end + 4:]
                return None

            # Move past headers
            self._buffer = self._buffer[header_end + 4:]
            self._headers_complete = True

        # Phase 2: Read body if we have complete headers
        if self._content_length is not None and len(self._buffer) >= self._content_length:
            body_bytes = self._buffer[:self._content_length]
            self._buffer = self._buffer[self._content_length:]

            # Reset for next message
            self._content_length = None
            self._headers_complete = False

            try:
                body = body_bytes.decode("utf-8")
                data = json.loads(body)
                return JsonRpcMessage.from_dict(data)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                logger.error(f"Failed to parse LSP message: {e}")
                return None

        return None

    def clear(self) -> None:
        """Clear all buffered data."""
        self._buffer = b""
        self._content_length = None
        self._headers_complete = False


class LSPClient:
    """Full Language Server Protocol client.

    Implements proper JSON-RPC 2.0 message framing with Content-Length headers.

    Supports:
    - Python (pylsp)
    - TypeScript (typescript-language-server)

    Usage:
        client = LSPClient()
        client.start_server(project_path, "python")
        hover = client.get_hover(file, line, col)
        definition = client.get_definition(file, line, col)
        references = client.get_references(file, line, col)

    JSON-RPC 2.0 Message Format:
        Request: {"jsonrpc": "2.0", "id": 1, "method": "...", "params": {...}}
        Response: {"jsonrpc": "2.0", "id": 1, "result": {...}} or {"jsonrpc": "2.0", "id": 1, "error": {...}}
        Notification: {"jsonrpc": "2.0", "method": "...", "params": {...}} (no id field)

    LSP Transport Format:
        Content-Length: <byte_length>\r\n
        \r\n
        <json body>
    """

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._language = None
        # Message buffer for proper Content-Length framing
        self._message_buffer = MessageBuffer()
        # Thread-safe queues for handling messages
        self._response_queue: queue.Queue[JsonRpcMessage] = queue.Queue()
        self._notification_queue: queue.Queue[JsonRpcMessage] = queue.Queue()
        # Pending responses indexed by request id
        self._pending_responses: dict[int, queue.Queue] = {}
        self._pending_lock = threading.Lock()
        # Reader thread for async message reading
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        # Lock for sending messages
        self._send_lock = threading.Lock()
        # Track if server initialization failed
        self._initialization_failed = False

    @property
    def is_available(self) -> bool:
        """Check if the LSP server is running and available.

        Returns:
            True if the server is running and initialized, False otherwise.
        """
        return (
            self._process is not None
            and self._process.poll() is None
            and self._running
            and not self._initialization_failed
        )
    
    def start_server(self, project_path: Path, language: str) -> bool:
        """Start the appropriate LSP server.

        Args:
            project_path: Root of the project
            language: python or typescript

        Returns:
            True if server started successfully
        """
        self._language = language

        try:
            if language == "python":
                cmd = ["pylsp"]
            elif language == "typescript":
                cmd = ["typescript-language-server", "--stdio"]
            else:
                logger.warning(f"Unsupported language: {language}")
                return False

            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_path)
            )

            # Start the reader thread for async message handling
            self._running = True
            self._reader_thread = threading.Thread(
                target=self._reader_loop,
                daemon=True,
                name="LSP-Reader"
            )
            self._reader_thread.start()

            # Send initialize request
            result = self._send_request("initialize", {
                "processId": os.getpid(),
                "rootUri": f"file://{project_path}",
                "capabilities": {
                    "textDocument": {
                        "hover": {"contentFormat": ["plaintext", "markdown"]},
                        "definition": {"linkSupport": True},
                        "references": {},
                        "documentSymbol": {"hierarchicalDocumentSymbolSupport": True}
                    }
                }
            })

            if result:
                # Send initialized notification (required by LSP spec)
                self._send_notification("initialized", {})
                logger.info(f"Started {language} server for {project_path}")
                return True
            else:
                logger.warning(f"Failed to initialize {language} server")
                self.stop_server()
                return False

        except FileNotFoundError:
            logger.warning(f"LSP server not installed: {cmd[0]}")
            self._initialization_failed = True
            return False
        except Exception as e:
            logger.error(f"Error starting LSP server: {e}")
            self._initialization_failed = True
            return False
    
    def stop_server(self):
        """Stop the LSP server and clean up resources."""
        self._running = False

        if self._process:
            try:
                # Send shutdown request and wait for response
                self._send_request("shutdown", None)
                # Send exit notification
                self._send_notification("exit", None)
            except Exception as e:
                logger.debug(f"Error during LSP shutdown: {e}")
            finally:
                self._process.terminate()
                try:
                    self._process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                self._process = None

        # Wait for reader thread to finish
        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1.0)
        self._reader_thread = None

        # Clear queues
        while not self._response_queue.empty():
            try:
                self._response_queue.get_nowait()
            except queue.Empty:
                break
        while not self._notification_queue.empty():
            try:
                self._notification_queue.get_nowait()
            except queue.Empty:
                break

        logger.debug("LSP server stopped")

    def open_document(self, file: Path) -> bool:
        """Notify the LSP server that a document is opened.

        Many LSP servers require documents to be opened before making
        requests about positions within them (hover, definition, etc.).

        The document content is read from the file.

        Args:
            file: Path to the file to open

        Returns:
            True if notification was sent successfully
        """
        try:
            file_path = Path(file)
            if not file_path.exists():
                logger.warning(f"Cannot open non-existent file: {file}")
                return False

            content = file_path.read_text(encoding="utf-8", errors="replace")

            # Determine language ID from file extension
            suffix = file_path.suffix.lower()
            language_id_map = {
                ".py": "python",
                ".ts": "typescript",
                ".tsx": "typescriptreact",
                ".js": "javascript",
                ".jsx": "javascriptreact",
                ".rs": "rust",
                ".go": "go",
                ".java": "java",
                ".c": "c",
                ".cpp": "cpp",
                ".h": "c",
                ".hpp": "cpp",
            }
            language_id = language_id_map.get(suffix, "plaintext")

            self._send_notification("textDocument/didOpen", {
                "textDocument": {
                    "uri": f"file://{file_path.absolute()}",
                    "languageId": language_id,
                    "version": 1,
                    "text": content
                }
            })

            logger.debug(f"Opened document: {file}")
            return True

        except Exception as e:
            logger.error(f"Error opening document {file}: {e}")
            return False

    def close_document(self, file: Path) -> bool:
        """Notify the LSP server that a document is closed.

        This should be called when done working with a document to
        free up resources in the LSP server.

        Args:
            file: Path to the file to close

        Returns:
            True if notification was sent successfully
        """
        try:
            file_path = Path(file)
            self._send_notification("textDocument/didClose", {
                "textDocument": {
                    "uri": f"file://{file_path.absolute()}"
                }
            })

            logger.debug(f"Closed document: {file}")
            return True

        except Exception as e:
            logger.error(f"Error closing document {file}: {e}")
            return False

    def get_hover(self, file: Path, line: int, col: int) -> Optional[HoverInfo]:
        """Get hover information at position.
        
        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)
        
        Returns:
            HoverInfo with type/docstring info
        """
        result = self._send_request("textDocument/hover", {
            "textDocument": {"uri": f"file://{file}"},
            "position": {"line": line, "character": col}
        })
        
        if not result:
            return None
        
        contents = result.get("contents", {})
        if isinstance(contents, str):
            content = contents
            language = ""
        elif isinstance(contents, dict):
            content = contents.get("value", "")
            language = contents.get("language", "")
        else:
            content = str(contents)
            language = ""
        
        range_info = result.get("range", {})
        start = range_info.get("start", {"line": 0, "character": 0})
        end = range_info.get("end", {"line": 0, "character": 0})
        
        return HoverInfo(
            content=content,
            language=language,
            range_start=(start["line"], start["character"]),
            range_end=(end["line"], end["character"])
        )
    
    def get_definition(self, file: Path, line: int, col: int) -> Optional[Location]:
        """Jump to definition.

        Gets the definition location for a symbol at the given position.
        Uses 0-indexed positions per LSP specification.

        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)

        Returns:
            Location of definition with file:line format, or None if not found
        """
        definitions = self.get_all_definitions(file, line, col)
        return definitions[0] if definitions else None

    def get_all_definitions(self, file: Path, line: int, col: int) -> list[Location]:
        """Get all definition locations for a symbol.

        LSP may return multiple definitions for:
        - Overloaded functions
        - Type stubs alongside implementations
        - Multiple inheritance scenarios

        Uses 0-indexed positions per LSP specification.

        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)

        Returns:
            List of Location objects with file:line citations
        """
        result = self._send_request("textDocument/definition", {
            "textDocument": {"uri": f"file://{file}"},
            "position": {"line": line, "character": col}
        })

        if not result:
            return []

        # Normalize to list - result can be Location, Location[], or LocationLink[]
        if not isinstance(result, list):
            result = [result]

        locations = []
        for item in result:
            location = self._parse_location_or_link(item)
            if location:
                locations.append(location)

        return locations

    def find_definition(self, file: Path, line: int, col: int, auto_open: bool = True) -> Optional[str]:
        """Find definition and return as file:line citation string.

        A convenience method that returns a ready-to-use file:line citation
        for documentation. Optionally handles document opening/closing automatically.

        Args:
            file: File path
            line: Line number (0-indexed per LSP spec)
            col: Column number (0-indexed per LSP spec)
            auto_open: If True, automatically open and close the document

        Returns:
            Citation string like "path/to/file.py:42" (1-indexed for readability),
            or None if definition not found

        Example:
            >>> client.find_definition(Path("src/main.py"), 10, 5)
            'src/utils.py:25'
        """
        try:
            if auto_open:
                self.open_document(file)

            location = self.get_definition(file, line, col)
            if location:
                return location.to_citation()
            return None

        finally:
            if auto_open:
                self.close_document(file)

    def find_all_definitions(
        self, file: Path, line: int, col: int, auto_open: bool = True
    ) -> list[str]:
        """Find all definitions and return as file:line citation strings.

        A convenience method that returns ready-to-use file:line citations
        for documentation. Useful when a symbol has multiple definitions
        (overloads, type stubs, etc.).

        Args:
            file: File path
            line: Line number (0-indexed per LSP spec)
            col: Column number (0-indexed per LSP spec)
            auto_open: If True, automatically open and close the document

        Returns:
            List of citation strings like ["path/to/file.py:42", "path/to/stubs.pyi:10"]
            (1-indexed for readability)

        Example:
            >>> client.find_all_definitions(Path("src/main.py"), 10, 5)
            ['src/utils.py:25', 'src/utils.pyi:30']
        """
        try:
            if auto_open:
                self.open_document(file)

            locations = self.get_all_definitions(file, line, col)
            return [loc.to_citation() for loc in locations]

        finally:
            if auto_open:
                self.close_document(file)

    def _parse_location_or_link(self, item: dict) -> Optional[Location]:
        """Parse LSP Location or LocationLink to our Location type.

        LSP 3.14+ supports LocationLink which has additional fields:
        - targetUri: target file URI
        - targetRange: full range of target
        - targetSelectionRange: exact range of symbol name
        - originSelectionRange: range of the originating symbol

        Args:
            item: LSP Location or LocationLink dict

        Returns:
            Location object or None if parsing failed
        """
        if not item:
            return None

        # Handle LocationLink (LSP 3.14+)
        if "targetUri" in item:
            uri = item.get("targetUri", "")
            # Use targetSelectionRange for precise positioning, fall back to targetRange
            range_info = item.get("targetSelectionRange") or item.get("targetRange", {})
        else:
            # Standard Location
            uri = item.get("uri", "")
            range_info = item.get("range", {})

        if not uri:
            return None

        start = range_info.get("start", {})
        end = range_info.get("end", {})

        return Location(
            file=uri.replace("file://", ""),
            line=start.get("line", 0),
            column=start.get("character", 0),
            end_line=end.get("line") if end else None,
            end_column=end.get("character") if end else None
        )
    
    def get_references(
        self,
        file: Path,
        line: int,
        col: int,
        include_declaration: bool = True
    ) -> list[Location]:
        """Find all references to symbol across the codebase.

        Returns all locations where the symbol at the given position is used.
        By default, includes the definition location in the results.

        Uses 0-indexed positions per LSP specification.

        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)
            include_declaration: If True, include the definition location in results

        Returns:
            List of Location objects with file:line citations
        """
        result = self._send_request("textDocument/references", {
            "textDocument": {"uri": f"file://{file}"},
            "position": {"line": line, "character": col},
            "context": {"includeDeclaration": include_declaration}
        })

        if not result or not isinstance(result, list):
            return []

        locations = []
        for item in result:
            location = self._parse_location_or_link(item)
            if location:
                locations.append(location)

        return locations

    def find_references(
        self,
        file: Path,
        line: int,
        col: int,
        include_declaration: bool = True,
        auto_open: bool = True
    ) -> list[str]:
        """Find all references and return as file:line citation strings.

        A convenience method that returns ready-to-use file:line citations
        for documentation. Optionally handles document opening/closing automatically.

        Args:
            file: File path
            line: Line number (0-indexed per LSP spec)
            col: Column number (0-indexed per LSP spec)
            include_declaration: If True, include the definition location in results
            auto_open: If True, automatically open and close the document

        Returns:
            List of citation strings like ["path/to/file.py:42", "path/to/other.py:10"]
            (1-indexed for human readability)

        Example:
            >>> client.find_references(Path("src/main.py"), 10, 5)
            ['src/main.py:11', 'src/utils.py:25', 'tests/test_main.py:42']
        """
        try:
            if auto_open:
                self.open_document(file)

            locations = self.get_references(file, line, col, include_declaration)
            return [loc.to_citation() for loc in locations]

        finally:
            if auto_open:
                self.close_document(file)

    def get_references_count(
        self,
        file: Path,
        line: int,
        col: int,
        include_declaration: bool = True
    ) -> int:
        """Get the count of references to a symbol.

        A quick way to check how many places reference a symbol
        without needing the full location details.

        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)
            include_declaration: If True, include the definition in the count

        Returns:
            Number of references found
        """
        return len(self.get_references(file, line, col, include_declaration))

    def get_references_by_file(
        self,
        file: Path,
        line: int,
        col: int,
        include_declaration: bool = True
    ) -> dict[str, list[Location]]:
        """Find all references grouped by file.

        Useful for understanding the scope of impact when refactoring
        or analyzing symbol usage patterns across the codebase.

        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)
            include_declaration: If True, include the definition location

        Returns:
            Dictionary mapping file paths to lists of Location objects
            in that file

        Example:
            >>> refs = client.get_references_by_file(Path("src/main.py"), 10, 5)
            >>> for filepath, locations in refs.items():
            ...     print(f"{filepath}: {len(locations)} references")
        """
        all_refs = self.get_references(file, line, col, include_declaration)

        by_file: dict[str, list[Location]] = {}
        for loc in all_refs:
            if loc.file not in by_file:
                by_file[loc.file] = []
            by_file[loc.file].append(loc)

        return by_file
    
    def get_document_symbols(self, file: Path) -> list[LSPSymbol]:
        """Get all symbols in a document.
        
        Args:
            file: File path
        
        Returns:
            List of symbols with hierarchy
        """
        result = self._send_request("textDocument/documentSymbol", {
            "textDocument": {"uri": f"file://{file}"}
        })
        
        if not result or not isinstance(result, list):
            return []
        
        def parse_symbol(item: dict) -> LSPSymbol:
            range_info = item.get("range", {})
            start = range_info.get("start", {"line": 0, "character": 0})
            end = range_info.get("end", {"line": 0, "character": 0})
            
            children = []
            for child in item.get("children", []):
                children.append(parse_symbol(child))
            
            return LSPSymbol(
                name=item.get("name", ""),
                kind=self._symbol_kind_name(item.get("kind", 0)),
                range_start=(start["line"], start["character"]),
                range_end=(end["line"], end["character"]),
                children=children
            )
        
        return [parse_symbol(item) for item in result]
    
    def _reader_loop(self) -> None:
        """Background thread that reads messages from LSP server.

        Runs continuously, parsing messages from stdout and routing them:
        - Responses (have id, no method) -> to pending response queue
        - Notifications (have method, no id) -> to notification queue
        - Requests from server (have id and method) -> logged for now
        """
        logger.debug("LSP reader thread started")

        while self._running and self._process and self._process.stdout:
            try:
                # Read available data in chunks
                data = self._process.stdout.read1(4096)  # type: ignore
                if not data:
                    if self._running:
                        logger.debug("LSP server closed stdout")
                    break

                self._message_buffer.append(data)

                # Try to parse complete messages
                while True:
                    message = self._message_buffer.try_parse_message()
                    if message is None:
                        break

                    self._dispatch_message(message)

            except Exception as e:
                if self._running:
                    logger.error(f"Error in LSP reader loop: {e}")
                break

        logger.debug("LSP reader thread stopped")

    def _dispatch_message(self, message: JsonRpcMessage) -> None:
        """Route a message to the appropriate handler.

        Args:
            message: The parsed JSON-RPC message
        """
        if message.is_response:
            # Response to a request we sent
            with self._pending_lock:
                response_queue = self._pending_responses.get(message.id)
                if response_queue:
                    response_queue.put(message)
                else:
                    logger.warning(f"Received response for unknown request id: {message.id}")
        elif message.is_notification:
            # Server-initiated notification
            self._notification_queue.put(message)
            logger.debug(f"Received notification: {message.method}")
        elif message.is_request:
            # Server-initiated request (needs response)
            logger.debug(f"Received server request: {message.method} (id={message.id})")
            # For now, we don't handle server requests
            # Could implement window/showMessage, workspace/configuration, etc.
        else:
            logger.warning(f"Unknown message type: {message.to_dict()}")

    def _send_message(self, message: dict) -> bool:
        """Send a JSON-RPC message with proper Content-Length framing.

        Args:
            message: The JSON-RPC message dict to send

        Returns:
            True if message was sent successfully
        """
        if not self._process or not self._process.stdin:
            return False

        try:
            # Encode to bytes first to get correct Content-Length
            content_bytes = json.dumps(message).encode("utf-8")
            header = f"Content-Length: {len(content_bytes)}\r\n\r\n".encode("utf-8")

            with self._send_lock:
                self._process.stdin.write(header + content_bytes)
                self._process.stdin.flush()

            return True
        except Exception as e:
            logger.error(f"Error sending LSP message: {e}")
            return False

    def _send_request(self, method: str, params: Optional[dict], timeout: float = 30.0) -> Optional[dict]:
        """Send LSP request and wait for response.

        Implements proper JSON-RPC 2.0 request/response protocol.
        Uses message queues for thread-safe response handling.

        Args:
            method: The LSP method name (e.g., "textDocument/hover")
            params: Optional parameters for the method
            timeout: Timeout in seconds to wait for response

        Returns:
            The result field from the response, or None on error/timeout
        """
        if not self._process:
            return None

        self._request_id += 1
        request_id = self._request_id

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        # Create a queue for this request's response
        response_queue: queue.Queue[JsonRpcMessage] = queue.Queue()
        with self._pending_lock:
            self._pending_responses[request_id] = response_queue

        try:
            if not self._send_message(message):
                return None

            # Wait for response
            try:
                response = response_queue.get(timeout=timeout)
            except queue.Empty:
                logger.warning(f"Timeout waiting for response to {method} (id={request_id})")
                return None

            if response.error:
                logger.warning(f"LSP error for {method}: {response.error}")
                return None

            return response.result

        except Exception as e:
            logger.error(f"Error in LSP request {method}: {e}")
            return None
        finally:
            # Clean up pending response entry
            with self._pending_lock:
                self._pending_responses.pop(request_id, None)

    def _send_notification(self, method: str, params: Optional[dict]) -> None:
        """Send LSP notification (no response expected).

        Notifications are fire-and-forget messages that don't have an id.

        Args:
            method: The LSP method name (e.g., "initialized")
            params: Optional parameters for the method
        """
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

        if not self._send_message(message):
            logger.warning(f"Failed to send notification: {method}")
    
    def get_pending_notifications(self) -> list[JsonRpcMessage]:
        """Get all pending notifications from the server.

        Notifications are server-initiated messages like diagnostics,
        log messages, or progress updates. This method drains the
        notification queue and returns all pending notifications.

        Returns:
            List of notification messages (may be empty)
        """
        notifications = []
        while True:
            try:
                msg = self._notification_queue.get_nowait()
                notifications.append(msg)
            except queue.Empty:
                break
        return notifications

    @staticmethod
    def _symbol_kind_name(kind: int) -> str:
        """Convert LSP symbol kind number to name."""
        kinds = {
            1: "file", 2: "module", 3: "namespace", 4: "package",
            5: "class", 6: "method", 7: "property", 8: "field",
            9: "constructor", 10: "enum", 11: "interface", 12: "function",
            13: "variable", 14: "constant", 15: "string", 16: "number",
            17: "boolean", 18: "array", 19: "object", 20: "key",
            21: "null", 22: "enum_member", 23: "struct", 24: "event",
            25: "operator", 26: "type_parameter"
        }
        return kinds.get(kind, "unknown")


# Note: CodeAnalyzer with LSP/AST fallback is now in code_analyzer.py
# This module focuses on pure LSP client functionality
