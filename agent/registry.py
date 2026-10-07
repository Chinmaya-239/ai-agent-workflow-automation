"""Tool registry. A tool is a plain function ``fn(args: dict, tc: ToolContext) -> Any``.

Adding a new tool = write one decorated function. The Excel ``Step_Bindings`` sheet then
refers to it by name.
"""
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import Callable

from .errors import WorkflowConfigError


@dataclass
class ToolSpec:
    name: str
    fn: Callable
    description: str
    required_args: tuple


_TOOLS: dict[str, ToolSpec] = {}


def tool(name: str, description: str = "", required: tuple = ()):
    def deco(fn):
        _TOOLS[name] = ToolSpec(name, fn, description or (fn.__doc__ or "").strip().split("\n")[0], tuple(required))
        return fn
    return deco


def get_tool(name: str) -> ToolSpec:
    load_all_tools()
    if name not in _TOOLS:
        raise WorkflowConfigError(f"Unknown tool '{name}'. Registered: {', '.join(sorted(_TOOLS))}")
    return _TOOLS[name]


def list_tools() -> dict[str, ToolSpec]:
    load_all_tools()
    return dict(_TOOLS)


_loaded = False


def load_all_tools():
    """Import every module in agent.tools so their @tool decorators run (auto-discovery)."""
    global _loaded
    if _loaded:
        return
    from . import tools as pkg
    for m in pkgutil.iter_modules(pkg.__path__):
        importlib.import_module(f"{pkg.__name__}.{m.name}")
    _loaded = True
