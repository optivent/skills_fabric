"""Configuration management for Skills Fabric."""
import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    """Global configuration for Skills Fabric."""
    
    # Paths
    data_dir: Path = field(default_factory=lambda: Path.home() / "skills_fabric" / "data")
    kuzu_db_path: Path = field(default_factory=lambda: Path.home() / "skills_fabric" / "data" / "kuzu_db")
    context7_cache_dir: Path = field(default_factory=lambda: Path.home() / "skills_fabric" / "data" / "context7_cache")
    
    # API Keys
    zai_api_key: str = field(default_factory=lambda: os.environ.get("ZAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    
    # Context7 API
    context7_url: str = "https://mcp.context7.com/mcp"
    
    # GLM-4.7 API
    glm_api_url: str = "https://api.z.ai/api/coding/paas/v4/chat/completions"
    glm_model: str = "glm-4.7"
    
    # Limits
    # max_context7_files: 0 means no limit (use ALL available files)
    max_context7_files: int = 0
    max_skills_per_run: int = 100
    
    def __post_init__(self):
        """Ensure directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.context7_cache_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
