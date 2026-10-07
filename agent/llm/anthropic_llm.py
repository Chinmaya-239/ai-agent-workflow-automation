from __future__ import annotations

import os

from ..errors import LLMError
from .base import LLMClient


class AnthropicLLM(LLMClient):
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install anthropic") from e
        self._anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"], timeout=45, max_retries=2)
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    def structured(self, system, user, tool_name, tool_description, schema):
        try:
            resp = self.client.messages.create(
                model=self.model, max_tokens=2048, system=system,
                messages=[{"role": "user", "content": user}],
                tools=[{"name": tool_name, "description": tool_description, "input_schema": schema}],
                tool_choice={"type": "tool", "name": tool_name},
            )
        except Exception as e:
            raise LLMError(f"Anthropic call failed: {e}") from e
        for block in resp.content:
            if block.type == "tool_use":
                return dict(block.input)
        raise LLMError("Model did not return a tool call")

    def text(self, system, user, max_tokens=700):
        try:
            resp = self.client.messages.create(
                model=self.model, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as e:
            raise LLMError(f"Anthropic call failed: {e}") from e
        out = "".join(b.text for b in resp.content if b.type == "text").strip()
        if not out:
            raise LLMError("Empty response from model")
        return out
