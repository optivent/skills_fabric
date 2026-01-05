"""Git repository cloning and indexing."""
import subprocess
from pathlib import Path
from typing import Optional


class GitCloner:
    """Clone and manage git repositories."""
    
    def __init__(self, repos_dir: Optional[Path] = None):
        from ..core.config import config
        self.repos_dir = repos_dir or (config.data_dir / "repos")
        self.repos_dir.mkdir(parents=True, exist_ok=True)
    
    def clone(self, url: str, name: Optional[str] = None, depth: int = 1) -> Optional[Path]:
        """Clone a git repository."""
        if name is None:
            # Extract name from URL
            name = url.rstrip("/").split("/")[-1].replace(".git", "")
        
        repo_path = self.repos_dir / name
        
        if repo_path.exists():
            print(f"[Git] Repository already exists: {name}")
            return repo_path
        
        try:
            cmd = ["git", "clone", "--depth", str(depth), url, str(repo_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"[Git] Cloned: {name}")
                return repo_path
            else:
                print(f"[Git] Clone failed: {result.stderr}")
        except Exception as e:
            print(f"[Git] Error: {e}")
        
        return None
    
    def list_source_files(self, repo_path: Path, extensions: list[str] = None) -> list[Path]:
        """List source files in a repository."""
        if extensions is None:
            extensions = [".py", ".ts", ".js", ".rs", ".go"]
        
        files = []
        for ext in extensions:
            files.extend(repo_path.rglob(f"*{ext}"))
        
        # Exclude common non-source directories
        exclude = [".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"]
        files = [f for f in files if not any(ex in str(f) for ex in exclude)]
        
        return files
    
    def get_repo(self, name: str) -> Optional[Path]:
        """Get path to an existing repository."""
        repo_path = self.repos_dir / name
        return repo_path if repo_path.exists() else None
