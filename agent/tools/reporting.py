"""WF010 - workflow performance report computed from execution logs.

Log schema (one row per executed step): run_id, workflow_id, step_no, step_name, status, duration_sec, error
Run outcome: any step 'failed' -> failed; else any 'needs_input'/'escalated' -> incomplete (excluded from
failure-rate maths because the user/manager, not the workflow, was the blocker); else success.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from ..errors import LLMError, ToolError
from ..registry import tool


def _runs(rows):
    runs = defaultdict(lambda: {"wf": None, "dur": 0.0, "failed": False, "incomplete": False, "error": "", "failed_step": ""})
    for r in rows:
        k = r["run_id"]
        x = runs[k]
        x["wf"] = r["workflow_id"]
        x["dur"] += float(r.get("duration_sec") or 0)
        st = str(r.get("status", "")).lower()
        if st == "failed":
            x["failed"], x["error"], x["failed_step"] = True, str(r.get("error") or "unknown error"), r.get("step_name", "")
        elif st in ("needs_input", "escalated"):
            x["incomplete"] = True
    for x in runs.values():
        x["outcome"] = "failed" if x["failed"] else "incomplete" if x["incomplete"] else "success"
    return runs


def _name(tc, wid):
    wf = tc.workflows.get(wid)
    return wf.name if wf else wid


@tool("calc_failure_rates", required=("rows",))
def calc_failure_rates(args, tc):
    per = defaultdict(lambda: Counter())
    for x in _runs(args["rows"]).values():
        per[x["wf"]][x["outcome"]] += 1
    out = []
    for wid, c in per.items():
        done = c["success"] + c["failed"]
        out.append({"workflow_id": wid, "workflow": _name(tc, wid), "runs": sum(c.values()), "success": c["success"],
                    "failed": c["failed"], "incomplete": c["incomplete"],
                    "failure_rate_pct": round(100 * c["failed"] / done, 1) if done else 0.0})
    out.sort(key=lambda r: (-r["failure_rate_pct"], r["workflow_id"]))
    return {"rows": out, "count": len(out), "total_runs": sum(r["runs"] for r in out)}


@tool("calc_execution_times", required=("rows",))
def calc_execution_times(args, tc):
    per = defaultdict(list)
    for x in _runs(args["rows"]).values():
        if x["outcome"] != "incomplete":
            per[x["wf"]].append(x["dur"])
    out = [{"workflow_id": w, "avg_exec_sec": round(sum(v) / len(v), 2), "max_exec_sec": round(max(v), 2)} for w, v in per.items() if v]
    out.sort(key=lambda r: -r["avg_exec_sec"])
    return {"rows": out, "count": len(out)}


@tool("frequent_errors", required=("rows",))
def frequent_errors(args, tc):
    c, by_wf = Counter(), defaultdict(set)
    for r in args["rows"]:
        if str(r.get("status", "")).lower() == "failed":
            msg = re.sub(r"\d+", "N", str(r.get("error") or "unknown error"))[:90]
            c[msg] += 1
            by_wf[msg].add(r["workflow_id"])
    top = [{"error": m, "occurrences": n, "workflows": ", ".join(sorted(by_wf[m]))} for m, n in c.most_common(int(args.get("top_n", 5)))]
    return {"rows": top, "count": len(top)}


@tool("slow_steps", required=("rows",))
def slow_steps(args, tc):
    thr = float(args.get("threshold_sec") or 5)
    acc = defaultdict(list)
    for r in args["rows"]:
        try:
            acc[(r["workflow_id"], r["step_name"])].append(float(r.get("duration_sec") or 0))
        except ValueError:
            continue
    rows = [{"workflow_id": w, "step": s, "avg_sec": round(sum(v) / len(v), 2), "samples": len(v)} for (w, s), v in acc.items()]
    rows.sort(key=lambda r: -r["avg_sec"])
    slow = [r for r in rows if r["avg_sec"] > thr][: int(args.get("top_n", 5))]
    tc.decide(f"{len(slow)} step(s) have average duration above {thr:g}s")
    return {"rows": slow, "count": len(slow), "threshold_sec": thr}


ADVICE = [
    (r"timeout|timed out|unavailable|503", "add retries with exponential backoff and a circuit breaker for the flaky dependency"),
    (r"rate limit|429", "throttle/queue requests and cache repeated LLM or API calls"),
    (r"missing required column|schema|column", "add schema validation up-front and return a clear, fixable message to the user"),
    (r"not found|no such file|no order", "validate identifiers/paths before the step and ask the user for corrections"),
    (r"invalid|malformed|parse", "harden parsing and quarantine bad rows instead of failing the whole run"),
]


@tool("generate_recommendations", required=("rates", "timings", "errors", "slow"))
def generate_recommendations(args, tc):
    fthr = float(args.get("failure_rate_threshold_pct") or 10)
    tthr = float(args.get("exec_time_threshold_sec") or 20)
    times = {r["workflow_id"]: r for r in args["timings"]["rows"]}
    flagged = []
    for r in args["rates"]["rows"]:
        flags = []
        if r["failure_rate_pct"] > fthr:
            flags.append(f"failure rate {r['failure_rate_pct']}% > {fthr:g}%")
        t = times.get(r["workflow_id"])
        if t and t["avg_exec_sec"] > tthr:
            flags.append(f"avg time {t['avg_exec_sec']}s > {tthr:g}s")
        if flags:
            flagged.append({"workflow_id": r["workflow_id"], "workflow": r["workflow"], "runs": r["runs"],
                            "failure_rate_pct": r["failure_rate_pct"], "avg_exec_sec": t["avg_exec_sec"] if t else None,
                            "flags": "; ".join(flags)})
    tc.decide(f"Flag rule: failure rate > {fthr:g}% OR average execution time > {tthr:g}s -> {len(flagged)} workflow(s) flagged")
    recs = []
    for f in flagged:
        w = f["workflow_id"]
        errs = [e for e in args["errors"]["rows"] if w in e["workflows"].split(", ")]
        for e in errs[:1]:
            adv = next((a for pat, a in ADVICE if re.search(pat, e["error"], re.I)), "investigate root cause and add error handling")
            recs.append(f"{w} {f['workflow']}: most frequent error '{e['error']}' ({e['occurrences']}x) - {adv}.")
        slow = [s for s in args["slow"]["rows"] if s["workflow_id"] == w][:1]
        for s in slow:
            recs.append(f"{w} {f['workflow']}: step '{s['step']}' averages {s['avg_sec']}s - cache, batch or parallelise this step.")
        if not errs and not slow:
            recs.append(f"{w} {f['workflow']}: {f['flags']} - review recent runs for the cause.")
    if tc.llm.available and flagged:
        try:
            out = tc.llm.structured("You are an SRE reviewing workflow metrics. Give 3-6 concrete, prioritised recommendations. Reference only the data given.",
                                    f"Flagged: {flagged}\nTop errors: {args['errors']['rows']}\nSlow steps: {args['slow']['rows']}",
                                    "recommendations", "Recommendations",
                                    {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "string"}}}, "required": ["items"]})
            if out.get("items"):
                recs = [str(x) for x in out["items"]]
                tc.note(f"recommendations written by {tc.llm.name}")
        except LLMError as e:
            tc.note(f"LLM unavailable ({e}); rule-based recommendations used")
    if not flagged:
        recs = ["No workflow breaches the thresholds - keep monitoring."]
    return {"flagged": flagged, "recommendations": recs, "flagged_count": len(flagged)}
