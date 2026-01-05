#!/usr/bin/env python3
"""
Z.ai GLM-4.6 API Client for Claude Code Integration

This module provides a simple interface to call GLM-4.6 with:
- Authentication via Z.ai API key
- Chat completions with optional web search
- Error handling with retries
- Cost calculation
- Token tracking

Used by Claude Skills to delegate tasks to GLM-4.6.
"""

import os
import sys
import json
import time
import argparse
import requests
from typing import Dict, Optional, Tuple, Union, List
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================

API_BASE = "https://api.z.ai/api/coding/paas/v4"  # GLM Coding Plan endpoint
CHAT_ENDPOINT = f"{API_BASE}/chat/completions"
EMBEDDINGS_ENDPOINT = f"{API_BASE}/embeddings"
IMAGES_ENDPOINT = f"{API_BASE}/images/generations"

# Pricing per 1M tokens (from Z.ai API documentation)
# Chat completions
COST_INPUT = 0.60          # $0.60 per million input tokens
COST_OUTPUT = 2.20         # $2.20 per million output tokens
COST_CACHED_INPUT = 0.11   # $0.11 per million cached input tokens (50% savings)

# Embeddings (input-only, no output tokens)
COST_EMBEDDINGS_INPUT = 0.60  # $0.60 per million input tokens

# Vision model (GLM-4.5V)
COST_VISION_INPUT = 0.60      # $0.60 per million input tokens
COST_VISION_OUTPUT = 1.80     # $1.80 per million output tokens (cheaper than GLM-4.6)

# Image generation (CogView-4)
COST_IMAGE_GENERATION = 0.01  # $0.01 per image

# API configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 60  # seconds


# ============================================================================
# API Client
# ============================================================================

class GLM46Client:
    """Client for Z.ai GLM-4.6 API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GLM-4.6 client

        Args:
            api_key: Z.ai API key (or reads from ZAI_API_KEY env var)
        """
        self.api_key = api_key or self._get_api_key()
        self.base_url = API_BASE
        self.model = "glm-4.6"

    def _get_api_key(self) -> str:
        """Get API key from environment or config file"""
        # Try environment variable first
        api_key = os.getenv("ZAI_API_KEY")
        if api_key:
            return api_key

        # Try config file
        config_path = os.path.expanduser("~/.config/zai/api_key")
        if os.path.exists(config_path):
            with open(config_path) as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key

        # Try settings file
        settings_path = os.path.expanduser("~/.claude/settings.local.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path) as f:
                    settings = json.load(f)
                    api_key = settings.get("plugins", {}).get("z-ai-glm", {}).get("api_key")
                    if api_key:
                        return api_key
            except:
                pass

        raise ValueError(
            "Z.ai API key not found. Set ZAI_API_KEY environment variable or "
            "create ~/.config/zai/api_key or update ~/.claude/settings.local.json"
        )

    def chat(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        web_search: bool = False,
        thinking_mode: bool = False,
        stream: bool = False,
        tools: Optional[list] = None,
        image_urls: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> Dict:
        """
        Call GLM API with a prompt (text, images, or multimodal)

        Args:
            prompt: User prompt/message
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            web_search: Enable web search capability (auto-generates tool definition)
            thinking_mode: Enable extended thinking/reasoning
            stream: Whether to stream response (not yet implemented)
            tools: Optional list of tool definitions (OpenAI-style function calling)
            image_urls: Optional list of image URLs for multimodal input
                - Auto-switches to glm-4.5v when provided
                - Supported formats: JPG, PNG, GIF, WebP, PDF, etc.
            model: Optional model override (default: glm-4.6, auto-switches to glm-4.5v for images)

        Returns:
            Dict containing:
            {
                "success": bool,
                "response": str (if successful),
                "input_tokens": int,
                "output_tokens": int,
                "cached_tokens": int,
                "cost": float,
                "model": str (model used),
                "timestamp": str,
                "error": str (if failed),
                "error_code": int (if failed)
            }
        """

        # Determine model: auto-switch to glm-4.5v if images provided
        selected_model = model or self.model
        is_vision_mode = image_urls and len(image_urls) > 0
        if is_vision_mode:
            selected_model = "glm-4.5v"  # Auto-switch to vision model

        # Build message content - handle multimodal input
        message_content = []

        # Add text content
        message_content.append({
            "type": "text",
            "text": prompt
        })

        # Add image content if provided
        if image_urls:
            for image_url in image_urls:
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })

        # Build request payload
        payload = {
            "model": selected_model,
            "messages": [{"role": "user", "content": message_content if is_vision_mode else prompt}],
            "temperature": min(max(temperature, 0.0), 1.0),  # Clamp to [0, 1]
            "max_tokens": max_tokens,
        }

        # Add optional features
        # Thinking mode enables autonomous tool use and reasoning
        # GLM-4.7 supports thinking_budget for extended reasoning
        if thinking_mode:
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": 16000  # Up to 16K thinking tokens for GLM-4.7
            }

        # Web search: Three approaches supported
        # Note: Not available with vision model
        if not is_vision_mode:
            if tools:
                # Custom tool definitions (OpenAI-style function calling)
                payload["tools"] = tools
            elif web_search:
                # Auto-generate web_search tool (Z.ai SDK format)
                payload["tools"] = [
                    {
                        "type": "web_search",
                        "web_search": {
                            "search_query": prompt,  # Use the prompt as search query
                            "search_result": True,
                        },
                    }
                ]

        if stream:
            payload["stream"] = stream

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Claude-Code-GLM-Bridge/1.0"
        }

        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                response = requests.post(
                    CHAT_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                elapsed_time = time.time() - start_time

                # Check for HTTP errors
                if response.status_code != 200:
                    error_data = self._parse_error_response(response)

                    # Decide if we should retry
                    if self._should_retry(response.status_code, attempt):
                        wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue

                    return {
                        "success": False,
                        "error": error_data.get("message", f"HTTP {response.status_code}"),
                        "error_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    }

                # Parse successful response
                data = response.json()
                result = self._parse_response(data, selected_model)
                result["model"] = selected_model  # Include model used
                result["timestamp"] = datetime.now().isoformat()
                result["latency_seconds"] = elapsed_time

                return result

            except requests.exceptions.Timeout:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "error": f"Request timeout after {REQUEST_TIMEOUT}s",
                        "error_code": 504,
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(RETRY_DELAY * (2 ** attempt))

            except requests.exceptions.ConnectionError:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "error": "Connection error to Z.ai API",
                        "error_code": 503,
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(RETRY_DELAY * (2 ** attempt))

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": 500,
                    "timestamp": datetime.now().isoformat()
                }

        return {
            "success": False,
            "error": "Max retries exceeded",
            "error_code": 503,
            "timestamp": datetime.now().isoformat()
        }

    def embeddings(
        self,
        input: Union[str, List[str]],
        model: str = "embedding-2",
        dimensions: Optional[int] = None,
        encoding_format: str = "float"
    ) -> Dict:
        """
        Generate vector embeddings for text using Z.ai Embeddings API

        Args:
            input: Text or list of texts to embed
            model: Embedding model (default: "embedding-2")
            dimensions: Optional dimension configuration for the embeddings
            encoding_format: Format for embeddings ("float" or "base64", default: "float")

        Returns:
            Dict containing:
            {
                "success": bool,
                "embeddings": List[Dict] (if successful, contains embedding vectors),
                "data": List[Dict] (raw API response data),
                "input_tokens": int,
                "cost": float,
                "timestamp": str,
                "error": str (if failed),
                "error_code": int (if failed)
            }
        """

        # Normalize input to list
        if isinstance(input, str):
            input_list = [input]
        elif isinstance(input, list):
            input_list = input
        else:
            return {
                "success": False,
                "error": f"Input must be string or list of strings, got {type(input).__name__}",
                "error_code": 400,
                "timestamp": datetime.now().isoformat()
            }

        # Build request payload
        payload = {
            "model": model,
            "input": input_list if len(input_list) > 1 else input_list[0],
            "encoding_format": encoding_format
        }

        # Add optional dimensions parameter
        if dimensions is not None:
            payload["dimensions"] = dimensions

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Claude-Code-GLM-Bridge/1.0"
        }

        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                response = requests.post(
                    EMBEDDINGS_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                elapsed_time = time.time() - start_time

                # Check for HTTP errors
                if response.status_code != 200:
                    error_data = self._parse_error_response(response)

                    # Decide if we should retry
                    if self._should_retry(response.status_code, attempt):
                        wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue

                    return {
                        "success": False,
                        "error": error_data.get("message", f"HTTP {response.status_code}"),
                        "error_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    }

                # Parse successful response
                data = response.json()
                result = self._parse_embeddings_response(data)
                result["timestamp"] = datetime.now().isoformat()
                result["latency_seconds"] = elapsed_time

                return result

            except requests.exceptions.Timeout:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "error": f"Request timeout after {REQUEST_TIMEOUT}s",
                        "error_code": 504,
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(RETRY_DELAY * (2 ** attempt))

            except requests.exceptions.ConnectionError:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "error": "Connection error to Z.ai API",
                        "error_code": 503,
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(RETRY_DELAY * (2 ** attempt))

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": 500,
                    "timestamp": datetime.now().isoformat()
                }

        return {
            "success": False,
            "error": "Max retries exceeded",
            "error_code": 503,
            "timestamp": datetime.now().isoformat()
        }

    def _parse_response(self, data: dict, model: str = "glm-4.6") -> Dict:
        """Parse successful API response with correct pricing based on model"""
        try:
            # Extract message content
            choice = data["choices"][0]
            message = choice["message"]
            content = message.get("content", "")

            # GLM-4.7 uses reasoning_content for thinking output
            reasoning_content = message.get("reasoning_content", "")
            if not content and reasoning_content:
                # If content is empty but reasoning exists, use reasoning
                content = reasoning_content

            # Extract token usage
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cached_tokens = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)

            # Select pricing based on model
            if model == "glm-4.5v":
                input_cost_rate = COST_VISION_INPUT
                output_cost_rate = COST_VISION_OUTPUT
            elif model in ["glm-4.5", "glm-4.5-air"]:
                # GLM-4.5 variants are cheaper
                input_cost_rate = 0.20 / 1000  # $0.20 per million tokens
                output_cost_rate = 0.60 / 1000  # $0.60 per million tokens
            else:
                # Default to GLM-4.6 pricing
                input_cost_rate = COST_INPUT
                output_cost_rate = COST_OUTPUT

            # Calculate cost (accounting for caching)
            cached_input = min(cached_tokens, input_tokens)
            non_cached_input = input_tokens - cached_input

            input_cost = (non_cached_input / 1_000_000) * input_cost_rate
            cached_cost = (cached_input / 1_000_000) * COST_CACHED_INPUT
            output_cost = (output_tokens / 1_000_000) * output_cost_rate
            total_cost = input_cost + cached_cost + output_cost

            return {
                "success": True,
                "response": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cached_tokens": cached_tokens,
                "cost": total_cost,
                "cost_breakdown": {
                    "non_cached_input": non_cached_input,
                    "non_cached_input_cost": input_cost,
                    "cached_input": cached_input,
                    "cached_input_cost": cached_cost,
                    "output_cost": output_cost
                },
                "finish_reason": choice.get("finish_reason", "unknown")
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "error_code": 500
            }

    def _parse_embeddings_response(self, data: dict) -> Dict:
        """Parse embeddings API response"""
        try:
            # Extract embeddings data
            embeddings_data = data.get("data", [])

            # Extract token usage
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)

            # Calculate cost (embeddings are input-only)
            input_cost = (input_tokens / 1_000_000) * COST_EMBEDDINGS_INPUT

            return {
                "success": True,
                "data": embeddings_data,
                "embeddings": embeddings_data,  # Alias for convenience
                "input_tokens": input_tokens,
                "cost": input_cost,
                "model": data.get("model", "embedding-2"),
                "object": data.get("object", "list")
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                "success": False,
                "error": f"Failed to parse embeddings response: {str(e)}",
                "error_code": 500
            }

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        num_images: int = 1,
        model: str = "cogView-4-250304"
    ) -> Dict:
        """
        Generate images using CogView-4 text-to-image model

        Args:
            prompt: Text description of image to generate
                   - Supports bilingual input (English and Chinese)
                   - Any length prompt supported
            size: Image dimensions as "WIDTHxHEIGHT" (e.g., "1024x1024", "1280x960")
                  - Supports any resolution within specified range
                  - Default: 1024x1024
            num_images: Number of images to generate (default: 1)
            model: Model identifier (default: "cogView-4-250304")

        Returns:
            Dict containing:
            {
                "success": bool,
                "image_urls": List[str] (image URLs if successful),
                "num_images": int (number of images generated),
                "cost": float (cost per image * num_images),
                "cost_per_image": float,
                "model": str,
                "timestamp": str,
                "error": str (if failed),
                "error_code": int (if failed)
            }
        """

        # Validate inputs
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "error": "Prompt cannot be empty",
                "error_code": 400,
                "timestamp": datetime.now().isoformat()
            }

        if num_images < 1 or num_images > 10:
            return {
                "success": False,
                "error": "num_images must be between 1 and 10",
                "error_code": 400,
                "timestamp": datetime.now().isoformat()
            }

        # Validate size format
        try:
            width, height = map(int, size.split('x'))
            if width < 256 or height < 256 or width > 2048 or height > 2048:
                return {
                    "success": False,
                    "error": "Image dimensions must be between 256 and 2048 pixels",
                    "error_code": 400,
                    "timestamp": datetime.now().isoformat()
                }
        except (ValueError, AttributeError):
            return {
                "success": False,
                "error": f"Invalid size format. Use 'WIDTHxHEIGHT' (e.g., '1024x1024')",
                "error_code": 400,
                "timestamp": datetime.now().isoformat()
            }

        # Build request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": num_images
        }

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Claude-Code-GLM-Bridge/1.0"
        }

        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                response = requests.post(
                    IMAGES_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                elapsed_time = time.time() - start_time

                # Check for HTTP errors
                if response.status_code != 200:
                    error_data = self._parse_error_response(response)

                    # Decide if we should retry
                    if self._should_retry(response.status_code, attempt):
                        wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue

                    return {
                        "success": False,
                        "error": error_data.get("message", f"HTTP {response.status_code}"),
                        "error_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    }

                # Parse successful response
                data = response.json()
                result = self._parse_image_response(data, num_images)
                result["timestamp"] = datetime.now().isoformat()
                result["latency_seconds"] = elapsed_time

                return result

            except requests.exceptions.Timeout:
                if attempt == MAX_RETRIES - 1:
                    return {
                        "success": False,
                        "error": "Request timeout - image generation took too long",
                        "error_code": 504,
                        "timestamp": datetime.now().isoformat()
                    }
                wait_time = RETRY_DELAY * (2 ** attempt)
                time.sleep(wait_time)

            except requests.exceptions.RequestException as e:
                return {
                    "success": False,
                    "error": f"Request failed: {str(e)}",
                    "error_code": 500,
                    "timestamp": datetime.now().isoformat()
                }

            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse JSON response",
                    "error_code": 500,
                    "timestamp": datetime.now().isoformat()
                }

        return {
            "success": False,
            "error": "Max retries exceeded",
            "error_code": 500,
            "timestamp": datetime.now().isoformat()
        }

    def _parse_image_response(self, data: dict, num_requested: int) -> Dict:
        """Parse image generation API response"""
        try:
            # Extract image data
            image_data = data.get("data", [])

            # Extract image URLs
            image_urls = []
            for item in image_data:
                if isinstance(item, dict) and "url" in item:
                    image_urls.append(item["url"])
                elif isinstance(item, str):
                    image_urls.append(item)

            if not image_urls:
                return {
                    "success": False,
                    "error": "No image URLs in response",
                    "error_code": 500
                }

            # Calculate cost
            cost_per_image = COST_IMAGE_GENERATION
            total_cost = cost_per_image * len(image_urls)

            return {
                "success": True,
                "image_urls": image_urls,
                "num_images": len(image_urls),
                "cost_per_image": cost_per_image,
                "cost": total_cost,
                "model": data.get("model", "cogView-4-250304"),
                "object": data.get("object", "list")
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                "success": False,
                "error": f"Failed to parse image response: {str(e)}",
                "error_code": 500
            }

    def _parse_error_response(self, response: requests.Response) -> Dict:
        """Parse error response from API"""
        try:
            data = response.json()
            return data.get("error", {"message": "Unknown error"})
        except:
            return {"message": response.text or f"HTTP {response.status_code}"}

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Decide if request should be retried based on status code"""
        # Retry on server errors and rate limits
        retryable_codes = {429, 500, 502, 503, 504}
        return status_code in retryable_codes and attempt < MAX_RETRIES - 1


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0
) -> float:
    """
    Calculate cost of API call in USD

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cached_tokens: Number of cached input tokens

    Returns:
        Cost in USD
    """
    non_cached_input = input_tokens - cached_tokens
    input_cost = (non_cached_input / 1_000_000) * COST_INPUT
    cached_cost = (cached_tokens / 1_000_000) * COST_CACHED_INPUT
    output_cost = (output_tokens / 1_000_000) * COST_OUTPUT
    return input_cost + cached_cost + output_cost


def calculate_claude_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculate equivalent cost using Claude Sonnet 4.5 for comparison

    Claude pricing: $3/M input, $15/M output
    """
    CLAUDE_INPUT = 3.0
    CLAUDE_OUTPUT = 15.0
    input_cost = (input_tokens / 1_000_000) * CLAUDE_INPUT
    output_cost = (output_tokens / 1_000_000) * CLAUDE_OUTPUT
    return input_cost + output_cost


def estimate_tokens(text: str) -> int:
    """
    Quick estimate of token count (1 token ~= 4 characters, 1.3x word count)

    Note: This is an approximation. Actual token count comes from API response.
    """
    word_count = len(text.split())
    return int(word_count * 1.3)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Command-line interface for GLM API client"""
    parser = argparse.ArgumentParser(
        description="Call Z.ai GLM API (Chat, Embeddings, or Image Generation) from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple chat query
  %(prog)s --prompt "What is machine learning?"

  # Chat with web search
  %(prog)s --prompt "Latest AI news" --web-search

  # Bulk generation
  %(prog)s --prompt "Generate 10 Python functions" --max-tokens 8192

  # Generate embeddings for a single text
  %(prog)s --embeddings "The quick brown fox jumps over the lazy dog"

  # Generate embeddings for multiple texts
  %(prog)s --embeddings "Text 1" "Text 2" "Text 3"

  # Generate an image with CogView-4
  %(prog)s --generate-image "A serene mountain landscape at sunset"

  # Generate multiple images with custom size
  %(prog)s --generate-image "A futuristic city" --num-images 3 --image-size 1280x960

  # Cost analysis
  %(prog)s --prompt "..." --output json | jq .cost
        """
    )

    parser.add_argument(
        "--prompt", "-p",
        help="Prompt/message for GLM chat"
    )
    parser.add_argument(
        "--model",
        default="glm-4.7",
        help="Model to use: glm-4.6, glm-4.7, glm-4.5-air (default: glm-4.7)"
    )
    parser.add_argument(
        "--thinking-budget",
        type=int,
        default=16000,
        help="Max thinking tokens for reasoning models (default: 16000)"
    )
    parser.add_argument(
        "--embeddings", "-e",
        nargs="+",
        help="Generate embeddings for text(s)"
    )
    parser.add_argument(
        "--generate-image", "-g",
        help="Generate image(s) with CogView-4 text-to-image model"
    )
    parser.add_argument(
        "--num-images",
        type=int,
        default=1,
        help="Number of images to generate (default: 1, max: 10)"
    )
    parser.add_argument(
        "--image-size",
        default="1024x1024",
        help="Image size as WIDTHxHEIGHT (default: 1024x1024)"
    )
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.7,
        help="Sampling temperature (0.0-1.0, default: 0.7)"
    )
    parser.add_argument(
        "--max-tokens", "-m",
        type=int,
        default=4096,
        help="Maximum tokens to generate (default: 4096)"
    )
    parser.add_argument(
        "--web-search", "-w",
        action="store_true",
        help="Enable web search capability for chat"
    )
    parser.add_argument(
        "--thinking-mode",
        action="store_true",
        help="Enable extended thinking/reasoning mode for chat"
    )
    parser.add_argument(
        "--embedding-model",
        default="embedding-2",
        help="Embedding model to use (default: embedding-2)"
    )
    parser.add_argument(
        "--dimensions",
        type=int,
        help="Optional dimension configuration for embeddings"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--show-cost-breakdown",
        action="store_true",
        help="Show detailed cost breakdown"
    )
    parser.add_argument(
        "--compare-claude",
        action="store_true",
        help="Compare cost vs Claude Sonnet 4.5"
    )

    args = parser.parse_args()

    # Validate that exactly one mode is provided
    modes_provided = sum([
        bool(args.prompt),
        bool(args.embeddings),
        bool(args.generate_image)
    ])

    if modes_provided == 0:
        parser.error("One of --prompt, --embeddings, or --generate-image must be provided")
    elif modes_provided > 1:
        parser.error("Only one of --prompt, --embeddings, or --generate-image can be provided at a time")

    # Create client and make request
    try:
        client = GLM46Client()
        client.model = args.model  # Override model from command line

        # Handle embeddings request
        if args.embeddings:
            # Normalize input
            if len(args.embeddings) == 1:
                input_text = args.embeddings[0]
            else:
                input_text = args.embeddings

            result = client.embeddings(
                input=input_text,
                model=args.embedding_model,
                dimensions=args.dimensions
            )

            # Format output
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                # Text output for embeddings
                if result["success"]:
                    embeddings_data = result.get("embeddings", [])
                    print(f"Generated {len(embeddings_data)} embedding(s)")
                    print(f"Model: {result.get('model', 'unknown')}")
                    print(f"Tokens: {result['input_tokens']} input")
                    print(f"Cost: ${result['cost']:.6f}")

                    if result.get("latency_seconds"):
                        print(f"Latency: {result['latency_seconds']:.2f}s")

                    # Show embedding dimensions
                    if embeddings_data:
                        first_embedding = embeddings_data[0].get("embedding", [])
                        print(f"Embedding dimensions: {len(first_embedding)}")

                        if args.show_cost_breakdown:
                            print(f"\nCost calculation:")
                            print(f"  Input tokens: {result['input_tokens']}")
                            print(f"  Rate: $0.60 per million tokens")
                            print(f"  Total: ${result['cost']:.6f}")
                else:
                    print(f"ERROR: {result.get('error', 'Unknown error')}")
                    if result.get("error_code"):
                        print(f"Code: {result['error_code']}")
                    sys.exit(1)

        # Handle image generation request
        elif args.generate_image:
            result = client.generate_image(
                prompt=args.generate_image,
                size=args.image_size,
                num_images=args.num_images
            )

            # Format output
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                # Text output for image generation
                if result["success"]:
                    print(f"Generated {result['num_images']} image(s)")
                    print(f"Model: {result.get('model', 'unknown')}")
                    print(f"Size: {args.image_size}")
                    print(f"Cost per image: ${result['cost_per_image']:.4f}")
                    print(f"Total cost: ${result['cost']:.4f}")

                    if result.get("latency_seconds"):
                        print(f"Generation time: {result['latency_seconds']:.2f}s")

                    print("\nImage URLs:")
                    for i, url in enumerate(result["image_urls"], 1):
                        print(f"  {i}. {url}")

                    if args.show_cost_breakdown:
                        print(f"\nCost calculation:")
                        print(f"  Images: {result['num_images']}")
                        print(f"  Rate: ${result['cost_per_image']} per image")
                        print(f"  Total: ${result['cost']:.4f}")
                else:
                    print(f"ERROR: {result.get('error', 'Unknown error')}")
                    if result.get("error_code"):
                        print(f"Code: {result['error_code']}")
                    sys.exit(1)

        # Handle chat request
        else:
            result = client.chat(
                prompt=args.prompt,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                web_search=args.web_search,
                thinking_mode=args.thinking_mode
            )

            # Format output
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                # Text output
                if result["success"]:
                    print(result["response"])
                    print("\n" + "="*60)
                    print(f"Tokens: {result['input_tokens']} input, {result['output_tokens']} output")
                    if result.get("cached_tokens", 0) > 0:
                        print(f"Cached: {result['cached_tokens']} tokens (50% savings)")
                    print(f"Cost: ${result['cost']:.4f}")

                    if args.compare_claude:
                        claude_cost = calculate_claude_cost(
                            result["input_tokens"],
                            result["output_tokens"]
                        )
                        savings = claude_cost - result["cost"]
                        savings_pct = (savings / claude_cost) * 100 if claude_cost > 0 else 0
                        print(f"Claude cost: ${claude_cost:.4f}")
                        print(f"Savings: ${savings:.4f} ({savings_pct:.1f}%)")

                    if args.show_cost_breakdown:
                        breakdown = result.get("cost_breakdown", {})
                        print("\nCost breakdown:")
                        print(f"  Non-cached input: ${breakdown.get('non_cached_input_cost', 0):.4f}")
                        print(f"  Cached input: ${breakdown.get('cached_input_cost', 0):.4f}")
                        print(f"  Output: ${breakdown.get('output_cost', 0):.4f}")

                    if result.get("latency_seconds"):
                        print(f"Latency: {result['latency_seconds']:.2f}s")
                else:
                    print(f"ERROR: {result.get('error', 'Unknown error')}")
                    if result.get("error_code"):
                        print(f"Code: {result['error_code']}")
                    sys.exit(1)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
