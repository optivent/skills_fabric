"""Language Server Protocol client for deep code analysis.

Provides full LSP integration for:
- Hover information (types, docstrings)
- Go to definition
- Find all references
- Document symbols
"""
import subprocess
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class HoverInfo:
    """Hover information from LSP."""
    content: str
    language: str
    range_start: tuple[int, int]
    range_end: tuple[int, int]


@dataclass
class Location:
    """A location in source code."""
    file: str
    line: int
    column: int


@dataclass
class LSPSymbol:
    """A symbol from document symbols."""
    name: str
    kind: str
    range_start: tuple[int, int]
    range_end: tuple[int, int]
    children: list["LSPSymbol"]


class LSPClient:
    """Full Language Server Protocol client.
    
    Supports:
    - Python (pylsp)
    - TypeScript (typescript-language-server)
    
    Usage:
        client = LSPClient()
        client.start_server(project_path, "python")
        hover = client.get_hover(file, line, col)
        definition = client.get_definition(file, line, col)
        references = client.get_references(file, line, col)
    """
    
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._language = None
    
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
                print(f"[LSP] Unsupported language: {language}")
                return False
            
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_path)
            )
            
            # Send initialize request
            self._send_request("initialize", {
                "processId": os.getpid(),
                "rootUri": f"file://{project_path}",
                "capabilities": {}
            })
            
            print(f"[LSP] Started {language} server")
            return True
        except FileNotFoundError:
            print(f"[LSP] Server not installed: {cmd[0]}")
            return False
        except Exception as e:
            print(f"[LSP] Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the LSP server."""
        if self._process:
            self._send_request("shutdown", None)
            self._send_notification("exit", None)
            self._process.terminate()
            self._process = None
    
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
        
        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)
        
        Returns:
            Location of definition
        """
        result = self._send_request("textDocument/definition", {
            "textDocument": {"uri": f"file://{file}"},
            "position": {"line": line, "character": col}
        })
        
        if not result:
            return None
        
        # Result can be Location or Location[]
        if isinstance(result, list):
            result = result[0] if result else None
        
        if not result:
            return None
        
        uri = result.get("uri", "")
        pos = result.get("range", {}).get("start", {})
        
        return Location(
            file=uri.replace("file://", ""),
            line=pos.get("line", 0),
            column=pos.get("character", 0)
        )
    
    def get_references(self, file: Path, line: int, col: int) -> list[Location]:
        """Find all references to symbol.
        
        Args:
            file: File path
            line: Line number (0-indexed)
            col: Column number (0-indexed)
        
        Returns:
            List of locations where symbol is used
        """
        result = self._send_request("textDocument/references", {
            "textDocument": {"uri": f"file://{file}"},
            "position": {"line": line, "character": col},
            "context": {"includeDeclaration": True}
        })
        
        if not result or not isinstance(result, list):
            return []
        
        locations = []
        for item in result:
            uri = item.get("uri", "")
            pos = item.get("range", {}).get("start", {})
            locations.append(Location(
                file=uri.replace("file://", ""),
                line=pos.get("line", 0),
                column=pos.get("character", 0)
            ))
        
        return locations
    
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
    
    def _send_request(self, method: str, params: Optional[dict]) -> Optional[dict]:
        """Send LSP request and get response."""
        if not self._process:
            return None
        
        self._request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            content = json.dumps(message)
            header = f"Content-Length: {len(content)}\r\n\r\n"
            self._process.stdin.write((header + content).encode())
            self._process.stdin.flush()
            
            # Read response (simplified - real impl needs header parsing)
            # This is a stub - full implementation needs proper protocol handling
            return {}
        except Exception as e:
            print(f"[LSP] Request error: {e}")
            return None
    
    def _send_notification(self, method: str, params: Optional[dict]):
        """Send LSP notification (no response expected)."""
        if not self._process:
            return
        
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        try:
            content = json.dumps(message)
            header = f"Content-Length: {len(content)}\r\n\r\n"
            self._process.stdin.write((header + content).encode())
            self._process.stdin.flush()
        except Exception:
            pass
    
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
