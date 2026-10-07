from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InputSpec:
    name: str
    type: str = "text"          # text | number | file | file_list | identifier | date_range | date | object
    required: bool = False
    default: Any = None
    description: str = ""
    ask: str = ""
    extract_regex: str = ""
    fields: list = field(default_factory=list)   # for type=object


@dataclass
class StepDef:
    no: int
    name: str
    tool: str
    args: dict
    output_key: str
    condition: str = ""
    on_error: str = "abort"
    note: str = ""


@dataclass
class WorkflowDef:
    id: str
    name: str
    trigger: str = ""
    inputs_text: str = ""
    steps_text: str = ""
    decision_logic: str = ""
    tools_text: str = ""
    expected_output: str = ""
    keywords: str = ""
    examples: list = field(default_factory=list)
    input_specs: list = field(default_factory=list)
    steps: list = field(default_factory=list)


@dataclass
class StepTrace:
    no: int
    name: str
    tool: str
    status: str = "ok"          # ok | skipped | failed | needs_input | escalated
    duration_sec: float = 0.0
    attempts: int = 1
    summary: str = ""
    error: str = ""
    notes: list = field(default_factory=list)


@dataclass
class Routing:
    workflow_id: str | None
    confidence: float = 0.0
    method: str = ""            # llm-tool-call | keyword-tfidf | explicit
    reasoning: str = ""
    alternatives: list = field(default_factory=list)   # [(id, score)]


@dataclass
class AgentResponse:
    request: str
    status: str                 # success | needs_input | clarify | escalated | failed
    run_id: str = ""
    workflow_id: str | None = None
    workflow_name: str = ""
    routing: Routing | None = None
    inputs: dict = field(default_factory=dict)
    input_sources: dict = field(default_factory=dict)
    steps: list = field(default_factory=list)
    decisions: list = field(default_factory=list)
    result: dict | None = None
    message: str = ""
    missing: list = field(default_factory=list)   # [{"name","ask"}] when needs_input
    error: str = ""
    llm_mode: str = "none"
