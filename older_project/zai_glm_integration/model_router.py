"""
MARO v2.0 - Multi-Model Orchestration Layer

Intelligent routing between LLM providers based on task type:
- Gemini 2.0 Flash (OpenRouter) → Factual extraction, low hallucination
- GLM-4.7 (Z.ai) → Deep reasoning, complex synthesis
- Multi-model consensus → Critical decisions

Uses litellm for unified API access across providers.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum

try:
    import litellm
    from litellm import acompletion, completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logging.warning("litellm not available - falling back to GLM-only mode")

# Configure logging (centralized in logging_config.py)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Task types for model routing."""
    # Factual tasks → Gemini 2.0 (low hallucination)
    PICO_EXTRACTION = "pico"
    SAMPLE_SIZE = "sample_size"
    VERIFY = "verify"
    CLASSIFY = "classify"
    EXTRACT = "extract"
    BIAS_EVIDENCE = "bias_evidence"

    # Reasoning tasks → GLM-4.7 (deep thinking)
    SYNTHESIZE = "synthesize"
    REVIEW = "review"
    GAP_ANALYSIS = "gap_analysis"
    RESEARCH = "research"
    META_ANALYZE = "meta_analyze"

    # Consensus tasks → Multiple models
    CONSENSUS = "consensus"
    CRITICAL_REVIEW = "critical_review"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    model_id: str
    provider: str
    temperature: float = 0.1
    max_tokens: int = 4096
    thinking_budget: Optional[int] = None  # For GLM thinking models
    api_key_env: str = ""

    def get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        if self.api_key_env:
            return os.getenv(self.api_key_env)
        return None


@dataclass
class RoutingResult:
    """Result from a model call."""
    content: str
    model_used: str
    task_type: str
    tokens_used: int = 0
    cost_estimate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelRouter:
    """
    Intelligent router for multi-model orchestration.

    Routes tasks to optimal models:
    - Factual extraction → Gemini 2.0 Flash (low hallucination)
    - Deep reasoning → GLM-4.7 (16K thinking budget)
    - Consensus → Multiple models for diversity

    Example:
        router = ModelRouter()
        result = await router.call(
            task_type="pico",
            prompt="Extract PICO elements from: ...",
            response_format={"type": "json_object"}
        )
    """

    # Model configurations
    MODELS = {
        "gemini-2.0-flash": ModelConfig(
            model_id="openrouter/google/gemini-2.0-flash-001",
            provider="openrouter",
            temperature=0.1,
            max_tokens=8192,
            api_key_env="OPENROUTER_API_KEY"
        ),
        "glm-4.6-thinking": ModelConfig(
            model_id="glm-4.6",
            provider="zai",
            temperature=0.3,
            max_tokens=16384,
            thinking_budget=16000,  # Extended thinking mode
            api_key_env="ZAI_API_KEY"
        ),
        "glm-4.6": ModelConfig(
            model_id="glm-4.6",
            provider="zai",
            temperature=0.3,
            max_tokens=8192,
            api_key_env="ZAI_API_KEY"
        ),
        "claude-3.5-sonnet": ModelConfig(
            model_id="openrouter/anthropic/claude-3.5-sonnet",
            provider="openrouter",
            temperature=0.2,
            max_tokens=8192,
            api_key_env="OPENROUTER_API_KEY"
        ),
    }

    # Task → Model routing
    ROUTING_CONFIG = {
        # Factual tasks → Gemini 2.0 (structured, low hallucination)
        "factual": {
            "model": "gemini-2.0-flash",
            "fallback": "glm-4.6",
            "tasks": ["pico", "sample_size", "verify", "classify", "extract", "bias_evidence"]
        },
        # Reasoning tasks → GLM-4.6 with thinking (deep analysis)
        "reasoning": {
            "model": "glm-4.6-thinking",
            "fallback": "glm-4.6",
            "tasks": ["synthesize", "review", "gap_analysis", "research", "meta_analyze"]
        },
        # Consensus tasks → Multiple models
        "consensus": {
            "models": ["glm-4.6", "gemini-2.0-flash", "claude-3.5-sonnet"],
            "tasks": ["consensus", "critical_review"]
        }
    }

    def __init__(self, default_model: str = "glm-4.6"):
        """
        Initialize the model router.

        Args:
            default_model: Fallback model when routing fails
        """
        self.default_model = default_model
        self._validate_environment()

        # Cost tracking (approximate per 1K tokens, Z.ai prices)
        self.cost_per_1k_tokens = {
            "gemini-2.0-flash": {"input": 0.00015, "output": 0.0006},
            "glm-4.6": {"input": 0.0006, "output": 0.0022},  # Z.ai pricing
            "glm-4.6-thinking": {"input": 0.0006, "output": 0.0022},
            "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
        }

    def _validate_environment(self):
        """Check that required API keys are available."""
        self.available_models = []

        # Check OpenRouter (Gemini, Claude)
        if os.getenv("OPENROUTER_API_KEY"):
            self.available_models.extend(["gemini-2.0-flash", "claude-3.5-sonnet"])
            logger.info("OpenRouter API key found - Gemini 2.0 and Claude available")
        else:
            logger.warning("OPENROUTER_API_KEY not set - Gemini/Claude unavailable")

        # Check Z.ai (GLM)
        if os.getenv("ZAI_API_KEY"):
            self.available_models.extend(["glm-4.6", "glm-4.6-thinking"])
            logger.info("Z.ai API key found - GLM-4.6 available")
        else:
            logger.warning("ZAI_API_KEY not set - GLM unavailable")

        if not self.available_models:
            raise ValueError("No API keys configured. Set OPENROUTER_API_KEY or ZAI_API_KEY")

    def _get_category_for_task(self, task_type: str) -> str:
        """Determine routing category for a task type."""
        for category, config in self.ROUTING_CONFIG.items():
            if task_type in config.get("tasks", []):
                return category
        return "reasoning"  # Default to reasoning

    def _select_model(self, task_type: str) -> str:
        """Select optimal model for a task type."""
        category = self._get_category_for_task(task_type)
        config = self.ROUTING_CONFIG.get(category, {})

        # Get preferred model
        preferred = config.get("model", self.default_model)

        # Check if preferred model is available
        if preferred in self.available_models:
            return preferred

        # Try fallback
        fallback = config.get("fallback", self.default_model)
        if fallback in self.available_models:
            logger.info(f"Using fallback model {fallback} for task {task_type}")
            return fallback

        # Use any available model
        if self.available_models:
            return self.available_models[0]

        raise ValueError("No models available")

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a model call."""
        rates = self.cost_per_1k_tokens.get(model, {"input": 0.001, "output": 0.002})
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])

    async def _call_glm(
        self,
        model_config: ModelConfig,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call GLM via Z.ai API directly."""
        import httpx

        api_key = model_config.get_api_key()
        if not api_key:
            raise ValueError("ZAI_API_KEY not set")

        # Z.ai Coding Plan API endpoint
        url = "https://api.z.ai/api/coding/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_config.model_id,
            "messages": messages,
            "temperature": kwargs.get("temperature", model_config.temperature),
            "max_tokens": kwargs.get("max_tokens", model_config.max_tokens),
        }

        # Add thinking budget for thinking models (Z.ai format)
        if model_config.thinking_budget:
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": model_config.thinking_budget
            }

        # Add response format for JSON output
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def _call_openrouter(
        self,
        model_config: ModelConfig,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call model via OpenRouter."""
        if not LITELLM_AVAILABLE:
            raise ImportError("litellm required for OpenRouter calls")

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

        # Configure litellm for OpenRouter
        completion_kwargs = {
            "model": model_config.model_id,
            "messages": messages,
            "temperature": kwargs.get("temperature", model_config.temperature),
            "max_tokens": kwargs.get("max_tokens", model_config.max_tokens),
            "api_key": api_key,
        }

        if response_format:
            completion_kwargs["response_format"] = response_format

        response = await acompletion(**completion_kwargs)

        # Convert to standard format
        return {
            "choices": [{
                "message": {
                    "content": response.choices[0].message.content
                }
            }],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0
            }
        }

    async def call(
        self,
        task_type: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict] = None,
        model_override: Optional[str] = None,
        **kwargs
    ) -> RoutingResult:
        """
        Route a task to the optimal model and execute.

        Args:
            task_type: Type of task (pico, synthesize, verify, etc.)
            prompt: The user prompt
            system_prompt: Optional system prompt
            response_format: Optional format (e.g., {"type": "json_object"})
            model_override: Force a specific model
            **kwargs: Additional model parameters

        Returns:
            RoutingResult with content, model used, and metadata
        """
        # Select model
        model_name = model_override or self._select_model(task_type)
        model_config = self.MODELS.get(model_name)

        if not model_config:
            raise ValueError(f"Unknown model: {model_name}")

        logger.info(f"Routing task '{task_type}' to model '{model_name}'")

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Call appropriate provider
        try:
            if model_config.provider == "zai":
                response = await self._call_glm(model_config, messages, response_format, **kwargs)
            elif model_config.provider == "openrouter":
                response = await self._call_openrouter(model_config, messages, response_format, **kwargs)
            else:
                raise ValueError(f"Unknown provider: {model_config.provider}")

            # Extract content
            content = response["choices"][0]["message"]["content"]
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            return RoutingResult(
                content=content,
                model_used=model_name,
                task_type=task_type,
                tokens_used=input_tokens + output_tokens,
                cost_estimate=self._estimate_cost(model_name, input_tokens, output_tokens),
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model_id": model_config.model_id,
                    "provider": model_config.provider
                }
            )

        except Exception as e:
            logger.error(f"Error calling {model_name}: {e}")
            # Try fallback
            category = self._get_category_for_task(task_type)
            fallback = self.ROUTING_CONFIG.get(category, {}).get("fallback")

            if fallback and fallback != model_name and fallback in self.available_models:
                logger.info(f"Trying fallback model: {fallback}")
                return await self.call(
                    task_type=task_type,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    response_format=response_format,
                    model_override=fallback,
                    **kwargs
                )
            raise

    async def consensus(
        self,
        task_type: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        models: Optional[List[str]] = None,
        aggregation: Literal["majority", "union", "intersection"] = "majority"
    ) -> RoutingResult:
        """
        Get consensus from multiple models.

        Args:
            task_type: Type of task
            prompt: The user prompt
            system_prompt: Optional system prompt
            models: List of models to query (defaults to consensus models)
            aggregation: How to aggregate results

        Returns:
            RoutingResult with aggregated consensus
        """
        # Get models for consensus
        if models is None:
            models = self.ROUTING_CONFIG.get("consensus", {}).get("models", [])

        # Filter to available models
        available = [m for m in models if m in self.available_models]

        if len(available) < 2:
            logger.warning("Less than 2 models available for consensus, using single model")
            return await self.call(task_type, prompt, system_prompt)

        # Call all models in parallel
        tasks = [
            self.call(task_type, prompt, system_prompt, model_override=model)
            for model in available
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        successful = [r for r in results if isinstance(r, RoutingResult)]

        if not successful:
            raise ValueError("All model calls failed in consensus")

        # Aggregate results
        total_tokens = sum(r.tokens_used for r in successful)
        total_cost = sum(r.cost_estimate for r in successful)

        # Build consensus response
        consensus_content = self._aggregate_responses(
            [r.content for r in successful],
            [r.model_used for r in successful],
            aggregation
        )

        return RoutingResult(
            content=consensus_content,
            model_used="consensus",
            task_type=task_type,
            tokens_used=total_tokens,
            cost_estimate=total_cost,
            metadata={
                "models_used": [r.model_used for r in successful],
                "aggregation": aggregation,
                "individual_responses": [
                    {"model": r.model_used, "content": r.content[:500]}
                    for r in successful
                ]
            }
        )

    def _aggregate_responses(
        self,
        responses: List[str],
        models: List[str],
        method: str
    ) -> str:
        """Aggregate multiple model responses."""
        if method == "majority":
            # For JSON responses, try to find common elements
            # For text, concatenate with model attribution
            aggregated = "## Multi-Model Consensus\n\n"
            for model, response in zip(models, responses):
                aggregated += f"### {model}\n{response}\n\n"
            aggregated += "---\n*Consensus from {} models*".format(len(responses))
            return aggregated

        elif method == "union":
            # Combine all unique information
            return "\n\n---\n\n".join(responses)

        elif method == "intersection":
            # Would need semantic analysis - fallback to first
            return responses[0] if responses else ""

        return responses[0] if responses else ""

    def get_status(self) -> Dict[str, Any]:
        """Get router status and available models."""
        return {
            "available_models": self.available_models,
            "default_model": self.default_model,
            "routing_config": {
                category: {
                    "model": config.get("model"),
                    "tasks": config.get("tasks", []),
                    "available": config.get("model") in self.available_models
                }
                for category, config in self.ROUTING_CONFIG.items()
                if "model" in config
            },
            "consensus_models": [
                m for m in self.ROUTING_CONFIG.get("consensus", {}).get("models", [])
                if m in self.available_models
            ]
        }


# Convenience functions for direct usage
_router: Optional[ModelRouter] = None

def get_router() -> ModelRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


async def route_task(
    task_type: str,
    prompt: str,
    **kwargs
) -> RoutingResult:
    """Route a task to the optimal model."""
    router = get_router()
    return await router.call(task_type, prompt, **kwargs)


# Test function
async def _test_router():
    """Test the model router with sample tasks."""
    router = ModelRouter()

    print("Router Status:")
    print(json.dumps(router.get_status(), indent=2))
    print()

    # Test factual task (should route to Gemini)
    print("Testing factual extraction (PICO)...")
    result = await router.call(
        task_type="pico",
        prompt="Extract PICO elements from: A randomized trial of 100 diabetic patients comparing metformin vs placebo for HbA1c reduction over 12 weeks.",
        response_format={"type": "json_object"}
    )
    print(f"Model used: {result.model_used}")
    print(f"Tokens: {result.tokens_used}, Cost: ${result.cost_estimate:.4f}")
    print(f"Response: {result.content[:200]}...")
    print()

    # Test reasoning task (should route to GLM)
    print("Testing reasoning (synthesis)...")
    result = await router.call(
        task_type="synthesize",
        prompt="Synthesize the evidence on metformin efficacy for diabetes management based on recent systematic reviews.",
        system_prompt="You are a medical research synthesizer. Provide evidence-based analysis."
    )
    print(f"Model used: {result.model_used}")
    print(f"Tokens: {result.tokens_used}, Cost: ${result.cost_estimate:.4f}")
    print(f"Response: {result.content[:200]}...")


if __name__ == "__main__":
    asyncio.run(_test_router())
