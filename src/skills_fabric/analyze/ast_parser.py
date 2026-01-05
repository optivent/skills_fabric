"""Python AST parsing for symbol extraction."""
import ast
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Symbol:
    """A code symbol extracted from source."""
    name: str
    kind: str  # 'class', 'function', 'method'
    file_path: str
    line: int


class ASTParser:
    """Parse Python files and extract symbols."""
    
    def parse_file(self, file_path: Path) -> list[Symbol]:
        """Parse a Python file and extract classes and functions."""
        symbols = []
        
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                source = f.read()
            
            tree = ast.parse(source)
            rel_path = str(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append(Symbol(
                        name=node.name,
                        kind="class",
                        file_path=rel_path,
                        line=node.lineno
                    ))
                elif isinstance(node, ast.FunctionDef):
                    symbols.append(Symbol(
                        name=node.name,
                        kind="function",
                        file_path=rel_path,
                        line=node.lineno
                    ))
        except SyntaxError:
            pass  # Skip files with syntax errors
        except Exception as e:
            print(f"[AST] Error parsing {file_path}: {e}")
        
        return symbols
    
    def parse_directory(self, dir_path: Path) -> list[Symbol]:
        """Parse all Python files in a directory."""
        all_symbols = []
        
        for py_file in dir_path.rglob("*.py"):
            # Skip test files and common non-source dirs
            if ".test." in py_file.name or "test_" in py_file.name:
                continue
            if any(d in str(py_file) for d in ["__pycache__", ".venv", "node_modules"]):
                continue
            
            symbols = self.parse_file(py_file)
            all_symbols.extend(symbols)
        
        return all_symbols
