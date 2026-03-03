"""LLM client for RAG generation using OpenRouter."""

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
        max_tokens: Optional[int] = None,
        use_openai_direct: bool = False
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: uv pip install openai"
            )
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Get API key and base URL
        if use_openai_direct:
            final_api_key = api_key or os.getenv("OPENAI_API_KEY")
            base_url_env = base_url or "https://api.openai.com/v1"
            if not final_api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY in .env file or pass api_key parameter. "
                    "Get your key from: https://platform.openai.com/api-keys"
                )
            # Remove model prefix if using OpenAI directly
            if model.startswith("openai/"):
                self.model = model.replace("openai/", "")
            else:
                self.model = model
        else:
            # Use OPENROUTER_API_KEY and OPENROUTER_BASE_URL
            final_api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            base_url_env = base_url or os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
            if not final_api_key:
                raise ValueError(
                    "OpenRouter API key not found. Set OPENROUTER_API_KEY in .env file or pass api_key parameter. "
                    "Get your key from: https://openrouter.ai/keys"
                )
            self.model = model
        
        self._client = OpenAI(
            base_url=base_url_env,
            api_key=final_api_key
        )
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response from prompts."""
        try:
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
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "User not found" in error_msg:
                raise ValueError(
                    "OpenRouter authentication failed. Please check your API key:\n"
                    "1. Verify OPENROUTER_API_KEY in .env file\n"
                    "2. Get a valid key from: https://openrouter.ai/keys\n"
                    "3. Make sure there are no extra spaces or quotes in .env"
                ) from e
            raise
