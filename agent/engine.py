"""Generic workflow executor.

It knows nothing about inventory, orders, SEO, ... It just:
  1. walks the ordered steps of a WorkflowDef
  2. resolves ``{{templates}}`` in each step's arguments from the shared context
  3. evaluates the step Condition (skip when false)
  4. calls the registered tool
  5. applies the step's On_Error policy (abort | skip | retry:N | retry:N+skip)
  6. records a trace (what ran, how long, what happened) and the decisions tools made
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from .config import Config
from .errors import AgentError, Escalation, NeedInput, ToolError, WorkflowConfigError
from .models import StepTrace, WorkflowDef
from .registry import get_tool
from .safe_eval import safe_eval
from .templating import resolve


@dataclass
class ToolContext:
    """Everything a tool may need besides its own arguments."""
    llm: object
    config: Config
    inputs: dict
    ctx: dict
    run_id: str
    workflow: WorkflowDef
    workflows: dict
    notes: list = field(default_factory=list)
    decisions: list = field(default_factory=list)
    step_name: str = ""

    def note(self, msg: str):
        self.notes.append(msg)

    def decide(self, msg: str):
        self.decisions.append(f"[{self.step_name}] {msg}")


@dataclass
class ExecutionResult:
    status: str                    # success | needs_input | escalated | failed
    ctx: dict
    trace: list
    decisions: list
    result: dict | None = None
    message: str = ""
    missing: list = field(default_factory=list)
    error: str = ""


_RETRY = re.compile(r"^retry:(\d+)(?:\+(skip|abort))?$")


def parse_policy(policy: str):
    policy = (policy or "abort").strip().lower()
    if policy in ("abort", "skip"):
        return 0, policy
    m = _RETRY.match(policy)
    if m:
        return int(m.group(1)), (m.group(2) or "abort")
    raise WorkflowConfigError(f"Invalid On_Error policy '{policy}' (use abort | skip | retry:N | retry:N+skip)")


def summarize_output(out) -> str:
    if out is None:
        return "no output"
    if isinstance(out, dict):
        for key in ("row_count", "count", "valid_count"):
            if key in out and isinstance(out[key], (int, float)):
                extra = f", total={out['total']}" if "total" in out else ""
                return f"{key}={out[key]}{extra}"
        if "title" in out and "tables" in out:
            return f"report built: {out['title']}"
        if "rows" in out and isinstance(out["rows"], list):
            return f"{len(out['rows'])} rows"
        return "keys: " + ", ".join(list(out.keys())[:5])
    if isinstance(out, list):
        return f"{len(out)} items"
    s = str(out)
    return s if len(s) <= 60 else s[:57] + "..."


class WorkflowEngine:
    def __init__(self, llm, config: Config, workflows: dict):
        self.llm, self.config, self.workflows = llm, config, workflows

    def execute(self, wf: WorkflowDef, inputs: dict, run_id: str) -> ExecutionResult:
        ctx: dict = {}
        trace: list[StepTrace] = []
        decisions: list[str] = []
        ns = {"inputs": inputs, "ctx": ctx,
              "run": {"id": run_id},
              "workflow": {"id": wf.id.lower(), "name": wf.name},
              "config": {"outputs_dir": str(self.config.outputs_dir)}}

        for step in wf.steps:
            t = StepTrace(no=step.no, name=step.name, tool=step.tool)
            trace.append(t)
            tc = ToolContext(self.llm, self.config, inputs, ctx, run_id, wf, self.workflows, step_name=step.name)

            try:
                if step.condition and not safe_eval(step.condition, {**inputs, **ctx, "inputs": inputs, "ctx": ctx}):
                    t.status, t.summary = "skipped", f"condition not met: {step.condition}"
                    ctx[step.output_key] = None
                    decisions.append(f"[{step.name}] skipped because condition `{step.condition}` was false")
                    continue
                spec = get_tool(step.tool)
                args = resolve(step.args, ns)
                retries, final = parse_policy(step.on_error)
            except WorkflowConfigError as e:
                t.status, t.error = "failed", str(e)
                return self._done("failed", ctx, trace, decisions, error=f"Step {step.no} ({step.name}): {e}")

            attempt, start = 0, time.perf_counter()
            while True:
                attempt += 1
                tc.notes, tc.decisions = [], []
                try:
                    out = spec.fn(args, tc)
                    ctx[step.output_key] = out
                    t.status, t.summary = "ok", summarize_output(out)
                    t.notes, t.attempts = list(tc.notes), attempt
                    decisions.extend(tc.decisions)
                    break
                except NeedInput as e:
                    t.status, t.summary, t.attempts = "needs_input", e.message, attempt
                    t.duration_sec = time.perf_counter() - start
                    return self._done("needs_input", ctx, trace, decisions, message=e.message, missing=e.fields)
                except Escalation as e:
                    t.status, t.summary, t.attempts = "escalated", e.message, attempt
                    t.duration_sec = time.perf_counter() - start
                    decisions.extend(tc.decisions)
                    return self._done("escalated", ctx, trace, decisions, result=e.report, message=e.message)
                except (ToolError, WorkflowConfigError) as e:
                    if attempt <= retries and isinstance(e, ToolError):
                        time.sleep(self.config.retry_backoff_sec * attempt)
                        t.notes.append(f"attempt {attempt} failed ({e}); retrying")
                        continue
                    t.attempts, t.error = attempt, str(e)
                    if final == "skip" and isinstance(e, ToolError):
                        t.status, t.summary = "skipped", f"failed after {attempt} attempt(s), skipped: {e}"
                        ctx[step.output_key] = None
                        decisions.append(f"[{step.name}] failed ({e}); On_Error=skip so the workflow continues without it")
                        break
                    t.status = "failed"
                    t.duration_sec = time.perf_counter() - start
                    return self._done("failed", ctx, trace, decisions, error=f"Step {step.no} ({step.name}): {e}")
                except Exception as e:  # unexpected bug in a tool: never crash the agent
                    t.status, t.attempts, t.error = "failed", attempt, f"{type(e).__name__}: {e}"
                    t.duration_sec = time.perf_counter() - start
                    return self._done("failed", ctx, trace, decisions, error=f"Step {step.no} ({step.name}): unexpected {type(e).__name__}: {e}")
            t.duration_sec = time.perf_counter() - start

        return self._done("success", ctx, trace, decisions, result=ctx.get("result"))

    @staticmethod
    def _done(status, ctx, trace, decisions, result=None, message="", missing=None, error=""):
        return ExecutionResult(status, ctx, trace, decisions, result, message, missing or [], error)
