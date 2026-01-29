import os
import logging
import time
import httpx
from typing import Optional, Dict, Any, Type
from backend.services.llm import LLMService, LLMResponse

logger = logging.getLogger(__name__)

class OpenRouterLLMService(LLMService):
    """
    LLM service implementation for OpenRouter API.
    Supports model selection, retries, timeouts, and structured JSON output.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.timeout = float(os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set in environment.")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-Title": "AiEngineer Copilot"
        }
        for attempt in range(self.max_retries + 1):
            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(self.base_url, json=payload, headers=headers)
                latency = int((time.time() - start) * 1000)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    model=self.model,
                    provider="openrouter",
                    latency_ms=latency,
                )
            except Exception as e:
                logger.warning(f"OpenRouter LLM call failed (attempt {attempt+1}): {e}")
                if attempt == self.max_retries:
                    raise
                await self._backoff(attempt)

    async def generate_structured(self, prompt: str, output_schema: type, system_prompt: Optional[str] = None) -> LLMResponse:
        # Instruct model to return JSON matching output_schema
        schema_hint = f"\nRespond ONLY with valid JSON matching this schema: {output_schema.__doc__ or output_schema}"  # Use docstring or type
        full_prompt = prompt + schema_hint
        resp = await self.generate(full_prompt, system_prompt=system_prompt, temperature=self.temperature)
        # Try to parse JSON
        import json
        structured = None
        try:
            structured = json.loads(resp.content)
        except Exception as e:
            logger.warning(f"Failed to parse structured LLM output as JSON: {e}")
        resp.structured_output = structured
        return resp

    async def _backoff(self, attempt: int):
        import asyncio
        await asyncio.sleep(2 ** attempt)
