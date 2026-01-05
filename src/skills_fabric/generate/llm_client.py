"""LLM clients for skill generation."""
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    model: str
    success: bool


class GLMClient:
    """Client for GLM-4.7 API."""
    
    def __init__(self):
        from ..core.config import config
        self.api_key = config.zai_api_key
        self.api_url = config.glm_api_url
        self.model = config.glm_model
    
    def generate(self, prompt: str, max_tokens: int = 200) -> LLMResponse:
        """Generate text using GLM-4.7."""
        if not self.api_key:
            return LLMResponse(content="", model=self.model, success=False)
        
        try:
            resp = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                return LLMResponse(content=content, model=self.model, success=True)
        except Exception as e:
            print(f"[GLM] Error: {e}")
        
        return LLMResponse(content="", model=self.model, success=False)
    
    def generate_question(self, source_code: str, context: str = "") -> str:
        """Generate a skill question from source code."""
        prompt = f"""Based on this source code, generate ONE practical question a developer might ask.

{source_code[:2000]}

{f"Context: {context}" if context else ""}

Return ONLY the question, nothing else."""
        
        response = self.generate(prompt, max_tokens=100)
        return response.content if response.success else ""
