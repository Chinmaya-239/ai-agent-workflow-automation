"""Provider-neutral LLM interface.

Two operations are enough for the whole system:
  * structured()  - *forced tool call* returning JSON that matches a schema
                    (used for workflow routing, parameter extraction, classification)
  * text()        - free-text generation (descriptions, messaging)

Every caller has a deterministic fallback, so the system still runs (and is testable)
without an API key or when the provider errors out.
"""
from __future__ import annotations

from ..errors import LLMError


class LLMClient:
    name = "base"
    available = True

    def structured(self, system: str, user: str, tool_name: str, tool_description: str, schema: dict) -> dict:
        raise NotImplementedError

    def text(self, system: str, user: str, max_tokens: int = 700) -> str:
        raise NotImplementedError


class NullLLM(LLMClient):
    name = "none"
    available = False

    def structured(self, *a, **k):
        raise LLMError("No LLM configured (set ANTHROPIC_API_KEY or OPENAI_API_KEY)")

    def text(self, *a, **k):
        raise LLMError("No LLM configured (set ANTHROPIC_API_KEY or OPENAI_API_KEY)")
