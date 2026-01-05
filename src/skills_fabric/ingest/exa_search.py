"""Exa Search client for semantic web search.

Provides semantic search across the web for tutorials,
documentation, and code examples.
"""
import os
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExaResult:
    """A search result from Exa."""
    title: str
    url: str
    text: str
    score: float
    published_date: Optional[str] = None


class ExaClient:
    """Client for Exa semantic search API.
    
    Usage:
        client = ExaClient()
        results = client.search("langgraph state graph tutorial")
        answer = client.answer("how to create a StateGraph in LangGraph")
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("EXA_API_KEY", "")
        self.base_url = "https://api.exa.ai"
    
    def search(
        self,
        query: str,
        num_results: int = 5,
        include_text: bool = True,
        use_autoprompt: bool = True
    ) -> list[ExaResult]:
        """Semantic search for web content.
        
        Args:
            query: Natural language search query
            num_results: Number of results to return
            include_text: Whether to include page text
            use_autoprompt: Let Exa optimize the query
        
        Returns:
            List of ExaResult objects
        """
        if not self.api_key:
            print("[Exa] No API key configured")
            return []
        
        try:
            resp = requests.post(
                f"{self.base_url}/search",
                headers={"x-api-key": self.api_key},
                json={
                    "query": query,
                    "numResults": num_results,
                    "contents": {"text": True} if include_text else {},
                    "useAutoprompt": use_autoprompt
                },
                timeout=30
            )
            
            if resp.status_code != 200:
                print(f"[Exa] Search failed: {resp.status_code}")
                return []
            
            data = resp.json()
            results = []
            
            for item in data.get("results", []):
                results.append(ExaResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    text=item.get("text", "")[:2000],  # Limit text size
                    score=item.get("score", 0.0),
                    published_date=item.get("publishedDate")
                ))
            
            return results
        except Exception as e:
            print(f"[Exa] Error: {e}")
            return []
    
    def answer(self, query: str, num_results: int = 3) -> str:
        """Get a direct answer with citations.
        
        Args:
            query: Natural language question
            num_results: Number of sources to use
        
        Returns:
            Answer text with source citations
        """
        results = self.search(query, num_results=num_results)
        
        if not results:
            return ""
        
        # Compile answer from top results
        texts = []
        citations = []
        
        for i, r in enumerate(results):
            if r.text:
                texts.append(r.text[:500])
                citations.append(f"[{i+1}] {r.url}")
        
        answer = "\n\n".join(texts)
        answer += "\n\n**Sources:**\n" + "\n".join(citations)
        
        return answer
    
    def search_code(self, query: str, language: str = "python") -> list[ExaResult]:
        """Search specifically for code examples.
        
        Args:
            query: What code to search for
            language: Programming language filter
        
        Returns:
            List of results likely containing code
        """
        enhanced_query = f"{query} {language} code example tutorial github"
        return self.search(enhanced_query, num_results=10)
