"""Turn a free-text request into the typed inputs a workflow declares in Input_Spec.

Order of precedence for every input:  explicit params  >  extracted from request  >  default.
Extraction uses an LLM tool call when available and falls back to regex / heuristics, so the
behaviour is identical (just less flexible) without an API key.
"""
from __future__ import annotations

import re
from pathlib import Path

from .errors import LLMError
from .models import InputSpec, WorkflowDef
from .util import find_dates, parse_date_range

FILE_RE = re.compile(r"[\w\-./\\:]+\.(?:csv|xlsx|xls|json|tsv)\b", re.I)
ORDER_RE = re.compile(r"\bORD[-\s]?\d{3,}\b", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

OBJECT_ALIASES = {
    "product_name": ["product name", "product", "name", "title", "item"],
    "category": ["category", "type"],
    "material": ["material", "made of", "made from"],
    "color": ["color", "colour"],
    "target_audience": ["target audience", "audience", "for"],
    "features": ["features", "feature", "attributes", "key features", "specs"],
}


def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "") or (isinstance(v, (dict, list)) and not v)


def _file_exists(config, token: str) -> bool:
    return any(p.exists() for p in (Path(token), config.root / token, config.root / "data" / token))


def _parse_object(text: str, fields: list[str]):
    out = {}
    for f in fields:
        for alias in OBJECT_ALIASES.get(f, [f.replace("_", " ")]) + [f.replace("_", " ")]:
            m = re.search(rf"(?i)\b{re.escape(alias)}\s*[:=]\s*([^,;\n]+)", text)
            if m and m.group(1).strip():
                out[f] = m.group(1).strip()
                break
    return out or None


def regex_extract(request: str, specs: list[InputSpec], config) -> dict:
    out: dict = {}
    files = FILE_RE.findall(request)
    file_specs = [s for s in specs if s.type == "file"]
    unassigned = list(file_specs)
    for token in files:
        stem_toks = set(re.findall(r"[a-z]+", Path(token).stem.lower()))
        best = max(unassigned, key=lambda s: len(stem_toks & set(s.name.lower().replace("_path", "").split("_"))), default=None)
        if best:
            out[best.name] = token
            unassigned.remove(best)
    for s in specs:
        if s.name in out:
            continue
        val = None
        if s.type == "identifier":
            m = ORDER_RE.search(request) or EMAIL_RE.search(request)
            val = m.group(0) if m else None
        elif s.type == "date_range":
            val = parse_date_range(request)
        elif s.type == "date":
            d = find_dates(request)
            val = d[0].isoformat() if d else None
        elif s.type == "object":
            val = _parse_object(request, s.fields)
        elif s.extract_regex == "REQUEST":
            val = request.strip()
        elif s.extract_regex:
            m = re.search(s.extract_regex, request, re.I | re.S)
            val = (m.group(1) if m and m.groups() else (m.group(0) if m else None))
            val = val.strip() if isinstance(val, str) else val
        if not _blank(val):
            out[s.name] = val
    return out


def llm_extract(llm, request: str, specs: list[InputSpec]) -> dict:
    props = {}
    for s in specs:
        if s.type in ("file", "file_list"):
            props[s.name] = {"type": "string", "description": f"{s.description} (only if the user names a file)"}
        elif s.type == "number":
            props[s.name] = {"type": "number", "description": s.description}
        elif s.type == "date_range":
            props[s.name] = {"type": "object", "description": s.description + " (ISO dates)",
                             "properties": {"start": {"type": "string"}, "end": {"type": "string"}}}
        elif s.type == "object":
            props[s.name] = {"type": "object", "description": s.description,
                             "properties": {f: {"type": "string"} for f in s.fields}}
        else:
            props[s.name] = {"type": "string", "description": s.description}
    schema = {"type": "object", "properties": props}
    system = ("Extract workflow inputs from the user's request. Only include a field when the user explicitly "
              "stated it. NEVER guess or invent values; omit anything not stated.")
    out = llm.structured(system, request, "extract_inputs", "Record the inputs found in the request", schema)
    return {k: v for k, v in out.items() if k in props and not _blank(v)}


def coerce(spec: InputSpec, raw, llm=None, config=None):
    """Convert user-provided text (CLI answers / params) into the type the workflow expects."""
    if _blank(raw):
        return None
    t = spec.type
    try:
        if t == "number":
            return float(str(raw).replace("%", "").strip()) if not isinstance(raw, (int, float)) else raw
        if t == "date_range":
            return parse_date_range(raw)
        if t == "date":
            d = find_dates(str(raw))
            return d[0].isoformat() if d else None
        if t == "object":
            if isinstance(raw, dict):
                return raw
            got = None
            if llm is not None and llm.available:
                try:
                    got = llm_extract(llm, str(raw), [spec]).get(spec.name)
                except LLMError:
                    got = None
            return got or _parse_object(str(raw), spec.fields)
        if t == "file_list":
            return [p.strip() for p in re.split(r"[;,]", raw) if p.strip()] if isinstance(raw, str) else list(raw)
    except (ValueError, TypeError):
        return None
    return raw


def resolve_inputs(wf: WorkflowDef, request: str, params: dict | None, llm, config):
    params = params or {}
    specs = wf.input_specs
    extractable = [s for s in specs if s.type != "file_list"]
    found: dict = {}
    sources: dict = {}

    if llm.available and extractable:
        try:
            for k, v in llm_extract(llm, request, extractable).items():
                found[k] = coerce(next(s for s in specs if s.name == k), v, llm, config)
                sources[k] = "llm-extracted"
        except LLMError:
            pass
    for k, v in regex_extract(request, extractable, config).items():
        if _blank(found.get(k)):
            found[k] = coerce(next(s for s in specs if s.name == k), v, llm, config)
            sources[k] = "extracted"

    inputs, missing = {}, []
    for s in specs:
        val, src = None, None
        if s.name in params and not _blank(params[s.name]):
            val, src = coerce(s, params[s.name], llm, config), "user-provided"
        elif not _blank(found.get(s.name)):
            val, src = found[s.name], sources.get(s.name, "extracted")
        elif not _blank(s.default):
            val, src = coerce(s, s.default, llm, config), "default"
            if s.type == "number" and isinstance(s.default, str):
                val = float(s.default)
        if _blank(val):
            val, src = None, None
            if s.required:
                missing.append({"name": s.name, "ask": s.ask or f"Please provide {s.description or s.name}."})
        inputs[s.name] = val
        if src:
            sources[s.name] = src
    return inputs, {k: v for k, v in sources.items() if k in inputs and inputs[k] is not None}, missing
