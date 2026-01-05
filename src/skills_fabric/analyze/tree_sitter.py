"""Tree-sitter parsing for multi-language support."""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class TSSymbol:
    """A symbol extracted via Tree-sitter."""
    name: str
    kind: str
    file_path: str
    line: int


class TreeSitterParser:
    """Multi-language parser using Tree-sitter."""
    
    def __init__(self):
        self._ts_parser = None
        self._py_lang = None
        self._ts_lang = None
    
    def _init_python(self):
        """Initialize Python parser."""
        if self._py_lang is None:
            try:
                import tree_sitter_python as ts_py
                from tree_sitter import Language, Parser
                self._py_lang = Language(ts_py.language())
                self._ts_parser = Parser(self._py_lang)
            except ImportError:
                pass
    
    def _init_typescript(self):
        """Initialize TypeScript parser."""
        if self._ts_lang is None:
            try:
                import tree_sitter_typescript as ts_ts
                from tree_sitter import Language, Parser
                self._ts_lang = Language(ts_ts.language_typescript())
                self._ts_parser = Parser(self._ts_lang)
            except ImportError:
                pass
    
    def parse_file(self, file_path: Path) -> list[TSSymbol]:
        """Parse a source file and extract symbols."""
        symbols = []
        
        ext = file_path.suffix
        if ext == ".py":
            self._init_python()
        elif ext in (".ts", ".tsx"):
            self._init_typescript()
        else:
            return symbols
        
        if self._ts_parser is None:
            return symbols
        
        try:
            with open(file_path, "rb") as f:
                source = f.read()
            
            tree = self._ts_parser.parse(source)
            rel_path = str(file_path)
            
            def traverse(node, depth=0):
                if node.type in ("class_declaration", "class_definition"):
                    for child in node.children:
                        if child.type in ("identifier", "type_identifier"):
                            symbols.append(TSSymbol(
                                name=child.text.decode(),
                                kind="class",
                                file_path=rel_path,
                                line=node.start_point[0] + 1
                            ))
                            break
                elif node.type in ("function_declaration", "function_definition", "method_definition"):
                    for child in node.children:
                        if child.type == "identifier":
                            symbols.append(TSSymbol(
                                name=child.text.decode(),
                                kind="function",
                                file_path=rel_path,
                                line=node.start_point[0] + 1
                            ))
                            break
                
                for child in node.children:
                    traverse(child, depth + 1)
            
            traverse(tree.root_node)
        except Exception as e:
            print(f"[TreeSitter] Error parsing {file_path}: {e}")
        
        return symbols
