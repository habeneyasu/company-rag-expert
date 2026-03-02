"""
LLM client for RAG generation using OpenRouter.

This module handles LLM API calls via OpenRouter for generating answers from prompts.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for LLM API calls via OpenRouter."""
    
    def __init__(
        self,
        model: str = "openai/gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize LLM client.
        
        Args:
            model: Model identifier (e.g., "openai/gpt-3.5-turbo")
            api_key: OpenRouter API key (uses OPENROUTER_API_KEY env var if None)
            base_url: OpenRouter base URL (uses OPENROUTER_URL env var if None)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self._client = OpenAI(
            base_url=base_url or os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1"),
            api_key=api_key or os.getenv("OPENROUTER_API_KEY")
        )
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate response from prompts.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt with context and query
        
        Returns:
            Generated response text
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
