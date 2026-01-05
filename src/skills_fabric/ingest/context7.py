"""Context7 API client for fetching documentation."""
import json
import hashlib
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Context7Doc:
    """A documentation snippet from Context7."""
    title: str
    content: str
    source_url: str
    code_blocks: int


class Context7Client:
    """HTTP client for Context7 MCP API."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        from ..core.config import config
        self.url = config.context7_url
        self.cache_dir = cache_dir or config.context7_cache_dir
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    
    def resolve_library_id(self, library_name: str, query: str = "documentation") -> Optional[str]:
        """Resolve a library name to a Context7 library ID."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "resolve-library-id",
                "arguments": {"query": query, "libraryName": library_name}
            },
            "id": 1
        }
        
        try:
            resp = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            data = resp.json()
            
            if "result" in data:
                text = data["result"]["content"][0]["text"]
                # Extract library ID from response
                import re
                match = re.search(r"/[\w-]+/[\w-]+", text)
                if match:
                    return match.group()
        except Exception as e:
            print(f"[Context7] Error resolving library: {e}")
        
        return None
    
    def query_docs(self, library_id: str, query: str) -> Optional[str]:
        """Query documentation for a specific library."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query-docs",
                "arguments": {"libraryId": library_id, "query": query}
            },
            "id": 2
        }
        
        try:
            resp = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            data = resp.json()
            
            if "result" in data:
                return data["result"]["content"][0]["text"]
        except Exception as e:
            print(f"[Context7] Error querying docs: {e}")
        
        return None
    
    def fetch_and_cache(self, library_name: str, query: str) -> Optional[Path]:
        """Fetch documentation and save to cache."""
        # Resolve library ID
        lib_id = self.resolve_library_id(library_name, query)
        if not lib_id:
            return None
        
        # Query docs
        docs = self.query_docs(lib_id, query)
        if not docs or len(docs) < 100:
            return None
        
        # Save to cache
        hash_id = hashlib.md5(f"{lib_id}{query}".encode()).hexdigest()[:12]
        filename = f"{library_name}_{hash_id}.json"
        cache_file = self.cache_dir / filename
        
        with open(cache_file, "w") as f:
            json.dump({
                "library_id": lib_id,
                "query": query,
                "response": docs,
                "fetched_at": str(__import__("datetime").datetime.now().isoformat())
            }, f, indent=2)
        
        return cache_file
    
    def load_all_cached(self) -> list[dict]:
        """Load all cached documentation."""
        docs = []
        for f in self.cache_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                docs.append(data)
            except Exception:
                pass
        return docs
