import ast
import json
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Forensic-Bedrock")

@mcp.tool()
async def list_python_files(directory: str) -> str:
    """List all Python files in the given directory recursively."""
    path = Path(directory)
    if not path.exists():
        return f"Error: Directory {directory} does not exist."
    
    files = [str(f.relative_to(path)) for f in path.glob("**/*.py")]
    return json.dumps(files, indent=2)

@mcp.tool()
async def get_file_symbols(file_path: str) -> str:
    """Extract all classes and functions from a Python file with line numbers."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: File {file_path} does not exist."
        
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        symbols = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append({"type": "class", "name": node.name, "line": node.lineno})
            elif isinstance(node, ast.FunctionDef):
                symbols.append({"type": "function", "name": node.name, "line": node.lineno})
                
        return json.dumps(symbols, indent=2)
    except Exception as e:
        return f"Error parsing file: {e}"

@mcp.tool()
async def get_symbol_source(file_path: str, symbol_name: str) -> str:
    """Get the full source code for a specific class or function in a file."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: File {file_path} does not exist."
        
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        lines = content.splitlines()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == symbol_name:
                # Basic range extraction
                end_lineno = getattr(node, "end_lineno", len(lines))
                # Note: node.lineno is 1-indexed
                return "\n".join(lines[node.lineno - 1 : end_lineno])
                
        return f"Error: Symbol {symbol_name} not found in {file_path}."
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run()
