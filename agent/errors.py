"""Exception types that drive the engine's condition / error handling."""
from __future__ import annotations


class AgentError(Exception):
    """Base class for all agent errors."""


class WorkflowConfigError(AgentError):
    """The Excel workflow definition is invalid (bad tool name, bad template, ...)."""


class ToolError(AgentError):
    """A tool failed. The engine applies the step's On_Error policy (retry / skip / abort)."""


class NeedInput(AgentError):
    """A tool/engine needs information from the user before it can continue.

    fields: [{"name": <input name>, "ask": <question to show the user>}]
    """

    def __init__(self, fields, message: str | None = None):
        self.fields = fields
        self.message = message or " ".join(f["ask"] for f in fields)
        super().__init__(self.message)


class Escalation(AgentError):
    """Business rule says a human must decide (e.g. no suitable employee)."""

    def __init__(self, message: str, report: dict | None = None):
        self.message = message
        self.report = report or {}
        super().__init__(message)


class LLMError(AgentError):
    """LLM unavailable or returned unusable output. Callers fall back to deterministic logic."""
