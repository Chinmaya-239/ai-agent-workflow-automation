"""Resolve ``{{ctx.some.path}}`` / ``{{inputs.x}}`` references inside step arguments."""
from __future__ import annotations

import re

from .errors import WorkflowConfigError

_TPL = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
_TOKEN = re.compile(r"([A-Za-z_][\w]*)|\[(\d+)\]")


def lookup(path: str, ns: dict):
    cur = ns
    for part in path.split("."):
        # a part may look like  rows[0]
        for m in _TOKEN.finditer(part):
            key, idx = m.group(1), m.group(2)
            try:
                if key is not None:
                    cur = cur[key]
                else:
                    cur = cur[int(idx)]
            except (KeyError, IndexError, TypeError):
                raise WorkflowConfigError(f"Template '{{{{{path}}}}}' could not be resolved (failed at '{part}')")
    return cur


def _fmt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def resolve(value, ns: dict):
    """Recursively resolve templates. A string that is *exactly* one template keeps the
    referenced object's native type (list, dict, number...)."""
    if isinstance(value, str):
        m = _TPL.fullmatch(value.strip())
        if m:
            return lookup(m.group(1), ns)
        return _TPL.sub(lambda mm: _fmt(lookup(mm.group(1), ns)), value)
    if isinstance(value, dict):
        return {k: resolve(v, ns) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, ns) for v in value]
    return value
