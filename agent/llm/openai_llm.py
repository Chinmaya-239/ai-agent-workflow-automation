from __future__ import annotations

import json
import os

from ..errors import LLMError
from .base import LLMClient


class OpenAILLM(LLMClient):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        try:
            from openai import OpenAI
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install openai") from e
        self.client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"], timeout=45, max_retries=2)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def structured(self, system, user, tool_name, tool_description, schema):
        try:
            resp = self.client.chat.completions.create(
                model=self.model, temperature=0,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                tools=[{"type": "function", "function": {"name": tool_name, "description": tool_description, "parameters": schema}}],
                tool_choice={"type": "function", "function": {"name": tool_name}},
            )
            calls = resp.choices[0].message.tool_calls
            if not calls:
                raise LLMError("Model did not return a tool call")
            return json.loads(calls[0].function.arguments)
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"OpenAI call failed: {e}") from e

    def text(self, system, user, max_tokens=700):
        try:
            resp = self.client.chat.completions.create(
                model=self.model, temperature=0.4, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
        except Exception as e:
            raise LLMError(f"OpenAI call failed: {e}") from e
        out = (resp.choices[0].message.content or "").strip()
        if not out:
            raise LLMError("Empty response from model")
        return out
