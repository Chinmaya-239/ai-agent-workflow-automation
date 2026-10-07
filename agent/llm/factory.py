from __future__ import annotations

import os

from ..errors import LLMError
from .base import LLMClient, NullLLM


def get_llm(provider: str | None = None) -> LLMClient:
    """LLM_PROVIDER = auto (default) | anthropic | openai | none"""
    provider = (provider or os.getenv("LLM_PROVIDER", "auto")).lower()
    try:
        if provider in ("anthropic", "auto") and os.getenv("ANTHROPIC_API_KEY"):
            from .anthropic_llm import AnthropicLLM
            return AnthropicLLM()
        if provider in ("openai", "auto") and os.getenv("OPENAI_API_KEY"):
            from .openai_llm import OpenAILLM
            return OpenAILLM()
    except LLMError:
        pass
    return NullLLM()
