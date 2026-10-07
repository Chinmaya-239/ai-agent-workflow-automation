"""Render an AgentResponse (and report dicts produced by ``make_report``) as readable text/markdown."""
from __future__ import annotations

MARK = {"ok": "[OK]  ", "skipped": "[SKIP]", "failed": "[FAIL]", "needs_input": "[ASK] ", "escalated": "[ESC] "}


def _cell(v, w=44):
    if v is None:
        return ""
    if isinstance(v, float):
        v = f"{v:.2f}".rstrip("0").rstrip(".")
    s = str(v).replace("\n", " ").replace("|", "/")
    return s if len(s) <= w else s[: w - 1] + "…"


def table_md(rows: list, columns: list | None = None, limit: int = 20) -> str:
    if not rows:
        return "_(none)_"
    cols = columns or [c for c in rows[0].keys() if not str(c).startswith("_")]
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows[:limit]:
        out.append("| " + " | ".join(_cell(r.get(c)) for c in cols) + " |")
    if len(rows) > limit:
        out.append(f"\n_… {len(rows) - limit} more row(s) not shown{' (full data in exported file)' if True else ''}_")
    return "\n".join(out)


def _content(c, indent="") -> str:
    if c is None or c == "" or c == [] or c == {}:
        return indent + "_(none)_"
    if isinstance(c, str):
        return "\n".join(indent + ln for ln in c.splitlines())
    if isinstance(c, list):
        if c and isinstance(c[0], dict):
            return table_md(c)
        return "\n".join(f"{indent}- {x}" for x in c)
    if isinstance(c, dict):
        return "\n".join(f"{indent}- **{k}**: {v}" for k, v in c.items())
    return indent + str(c)


def render_report(rep: dict) -> str:
    if not rep:
        return "_(no result produced)_"
    parts = []
    if rep.get("title"):
        parts.append(f"## {rep['title']}")
    if rep.get("summary"):
        parts.append(rep["summary"])
    if rep.get("metrics"):
        parts.append("\n".join(f"- **{k}**: {v}" for k, v in rep["metrics"].items()))
    for sec in rep.get("sections", []):
        parts.append(f"### {sec['heading']}\n{_content(sec['content'])}")
    for t in rep.get("tables", []):
        parts.append(f"### {t['name']} ({t['total']})\n{table_md(t['rows'], t.get('columns'), t.get('limit', 20))}")
    if rep.get("files"):
        parts.append("**Files written:**\n" + "\n".join(f"- {f}" for f in rep["files"]))
    if rep.get("notes"):
        parts.append("**Notes:**\n" + "\n".join(f"- {n}" for n in rep["notes"]))
    return "\n\n".join(parts)


def render_response(r) -> str:
    L = ["=" * 78, f"USER REQUEST: {r.request}", "=" * 78]
    if r.status == "clarify":
        L += ["", "Selected Workflow: (none - request is ambiguous)"]
        if r.routing:
            L.append(f"Reasoning: {r.routing.reasoning}")
        L += ["", r.message]
        return "\n".join(L)

    if r.workflow_id:
        L.append(f"\nSelected Workflow:\n  {r.workflow_id} - {r.workflow_name}")
    if r.routing:
        L.append(f"  (router: {r.routing.method}, confidence {r.routing.confidence:.2f}) {r.routing.reasoning}")
    if r.inputs:
        L.append("\nInputs resolved:")
        for k, v in r.inputs.items():
            if v is not None:
                L.append(f"  - {k} = {_cell(v, 70)}  [{r.input_sources.get(k, '')}]")
    if r.steps:
        L.append("\nSteps Executed:")
        for t in r.steps:
            extra = f" x{t.attempts} attempts" if t.attempts > 1 else ""
            L.append(f"  {t.no}. {MARK.get(t.status, '[?]   ')} {t.name}  <{t.tool}, {t.duration_sec:.2f}s{extra}> - {_cell(t.summary or t.error, 90)}")
            for n in t.notes:
                L.append(f"        note: {n}")
    if r.decisions:
        L.append("\nConditions / Decisions:")
        L += [f"  - {d}" for d in r.decisions]

    L.append("")
    if r.status == "success":
        L += ["Result:", render_report(r.result)]
    elif r.status == "needs_input":
        L += ["STATUS: More information needed before this workflow can continue.", r.message]
    elif r.status == "escalated":
        L += [f"STATUS: ESCALATION REQUIRED - {r.message}", "", render_report(r.result)]
    else:
        L += [f"STATUS: FAILED - {r.error}"]
    return "\n".join(L)
