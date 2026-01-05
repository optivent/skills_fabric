import ast
import os
from pathlib import Path

def extract_symbols(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        symbols = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append({"type": "class", "name": node.name, "line": node.lineno})
            elif isinstance(node, ast.FunctionDef):
                symbols.append({"type": "function", "name": node.name, "line": node.lineno})
        return symbols
    except Exception as e:
        return []

def main():
    repo_path = Path("loguru")
    package_path = repo_path / "loguru"
    if not package_path.exists(): package_path = repo_path
    
    all_symbols = {}
    for root, _, files in os.walk(package_path):
        for file in files:
            if file.endswith(".py"):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(repo_path)
                symbols = extract_symbols(full_path)
                if symbols: all_symbols[str(rel_path)] = symbols
                
    with open("source_symbols.md", "w") as f:
        f.write("# Loguru Source Symbols\n\n")
        sorted_paths = sorted(all_symbols.keys())
        for path in sorted_paths:
            f.write("## `" + path + "`\n")
            for s in all_symbols[path]:
                msg = "- " + s["type"] + ": `" + s["name"] + "` (L" + str(s["line"]) + ")\n"
                f.write(msg)
            f.write("\n")
    print("Symbols extracted successfully")

if __name__ == "__main__":
    main()
