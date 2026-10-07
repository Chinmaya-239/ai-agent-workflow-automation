"""WF009 - employee task assignment (skills -> workload -> ranking -> selection / escalation)."""
from __future__ import annotations

import re
from datetime import date, timedelta

from ..errors import Escalation, LLMError, NeedInput, ToolError
from ..registry import tool
from ..util import parse_deadline, read_table, to_number

ROLE_SYNONYMS = {"developer": ["developer", "dev", "engineer", "programmer", "coder"],
                 "designer": ["designer", "ui", "ux"], "qa": ["qa", "tester", "quality"],
                 "analyst": ["analyst", "data analyst"]}
SLA_DAYS = {"high": 2, "medium": 5, "low": 10}
# Skills we recognise in a task even when no employee lists them. A required skill nobody has
# must lead to escalation - it must never be silently ignored.
KNOWN_TECH = ["kubernetes", "terraform", "golang", "rust", "swift", "kotlin", "php", "ruby", "scala", "angular", "vue",
              "node", "nodejs", "mongodb", "postgres", "postgresql", "graphql", "redis", "kafka", "spark", "devops",
              "machine learning", "ios", "android", "flutter", "c++", "c#", ".net", "azure", "gcp", "security", "blockchain"]


def _employees(tc, path):
    rows, cols = read_table(tc.config.resolve_path(path))
    need = {"name", "role", "skills", "current_workload_hours", "weekly_capacity_hours"}
    low = {c.strip().lower() for c in cols}
    if need - low:
        raise ToolError(f"Employee file missing columns: {sorted(need - low)}")
    out = []
    for r in rows:
        r = {k.strip().lower(): v for k, v in r.items()}
        r["skill_list"] = [s.strip().lower() for s in re.split(r"[;,|]", r.get("skills", "")) if s.strip()]
        r["workload"] = to_number(r["current_workload_hours"]) or 0
        r["capacity"] = to_number(r["weekly_capacity_hours"]) or 0
        r["active"] = str(r.get("status", "active")).lower() in ("active", "available", "")
        out.append(r)
    if not out:
        raise ToolError("Employee file has no rows")
    return out


@tool("analyze_task", required=("description", "employees_path"))
def analyze_task(args, tc):
    desc = args["description"]
    emps = _employees(tc, args["employees_path"])
    vocab = sorted({s for e in emps for s in e["skill_list"]})
    low = desc.lower()
    detect = sorted(set(vocab) | set(KNOWN_TECH))
    skills = [s for s in detect if re.search(rf"(?<![a-z0-9+#]){re.escape(s)}(?![a-z0-9+#])", low)]
    role = next((r for r, syn in ROLE_SYNONYMS.items() if any(re.search(rf"\b{re.escape(x)}s?\b", low) for x in syn)), None)
    priority = next((p for p, pat in (("high", r"urgent|asap|critical|immediately|high priority|blocker"),
                                      ("low", r"low priority|whenever|no rush|not urgent")) if re.search(pat, low)), "medium")
    mode = "rules"
    if tc.llm.available:
        try:
            out = tc.llm.structured(
                "Extract task requirements. List every skill the task genuinely needs as lowercase names. Prefer names "
                "from the team skill list when they fit, but DO include a needed skill even if nobody on the team has it.",
                f"Task: {desc}\nTeam skill list: {vocab}\nAllowed roles: {sorted(ROLE_SYNONYMS)}", "task_requirements", "Task requirements",
                {"type": "object", "properties": {"required_skills": {"type": "array", "items": {"type": "string"}},
                                                  "role": {"type": "string"}, "priority": {"type": "string", "enum": ["high", "medium", "low"]}}})
            llm_sk = [str(s).strip().lower() for s in out.get("required_skills", []) if str(s).strip()]
            skills = sorted(set(skills) | set(llm_sk))
            role = out.get("role") if out.get("role") in ROLE_SYNONYMS else role
            priority = out.get("priority", priority)
            mode = tc.llm.name
        except LLMError as e:
            tc.note(f"LLM unavailable ({e}); rule-based requirement extraction used")
    if args.get("priority"):
        priority = str(args["priority"]).lower()
    m = re.search(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|days?)\b", low)
    effort, effort_src = 8.0, "assumed default (not stated)"
    if args.get("effort_hours"):
        effort, effort_src = float(args["effort_hours"]), "provided"
    elif m:
        effort = float(m.group(1)) * (8 if m.group(2).startswith("day") else 1)
        effort_src = "parsed from request"
    dl_src = "provided"
    deadline = parse_deadline(str(args["deadline"])) if args.get("deadline") else parse_deadline(desc)
    if not deadline:
        deadline, dl_src = date.today() + timedelta(days=SLA_DAYS[priority]), f"assumed {priority}-priority SLA ({SLA_DAYS[priority]} days)"
    tc.decide(f"Requirements ({mode}): skills={skills or 'none stated'}, role={role or 'any'}, priority={priority}, "
              f"effort={effort:g}h ({effort_src}), deadline={deadline} ({dl_src})")
    return {"description": desc, "skills": skills, "role": role, "priority": priority, "effort_hours": effort,
            "deadline": deadline.isoformat(), "deadline_source": dl_src, "effort_source": effort_src}


@tool("match_employee_skills", required=("employees_path", "requirements"))
def match_employee_skills(args, tc):
    req, out = args["requirements"], []
    for e in _employees(tc, args["employees_path"]):
        have = [s for s in req["skills"] if s in e["skill_list"]]
        role_ok = (not req["role"]) or any(x in e["role"].lower() for x in ROLE_SYNONYMS[req["role"]])
        skill_score = (len(have) / len(req["skills"])) if req["skills"] else 1.0
        out.append({**e, "matched_skills": have, "missing_skills": [s for s in req["skills"] if s not in have],
                    "skill_score": round(skill_score, 2), "role_match": role_ok})
    return {"rows": out, "count": len(out)}


@tool("check_workload", required=("rows", "requirements"))
def check_workload(args, tc):
    effort, out = args["requirements"]["effort_hours"], []
    for e in args["rows"]:
        remaining = e["capacity"] - e["workload"]
        out.append({**e, "remaining_hours": round(remaining, 1),
                    "utilization_pct": round(100 * e["workload"] / e["capacity"], 0) if e["capacity"] else 100,
                    "has_capacity": e["active"] and remaining >= effort})
    return {"rows": out, "count": len(out)}


@tool("rank_candidates", required=("rows",))
def rank_candidates(args, tc):
    """score = 40% skill match + 20% role match + 30% free-capacity ratio + 10% if the task fits in remaining hours."""
    out = []
    for e in args["rows"]:
        free_ratio = max(e["remaining_hours"], 0) / e["capacity"] if e["capacity"] else 0
        score = 100 * (0.4 * e["skill_score"] + 0.2 * (1 if e["role_match"] else 0) + 0.3 * free_ratio + 0.1 * (1 if e["has_capacity"] else 0))
        out.append({**e, "score": round(score, 1)})
    out.sort(key=lambda e: (-e["score"], e["name"]))
    return {"rows": out, "count": len(out)}


@tool("select_employee", required=("rows", "requirements"))
def select_employee(args, tc):
    req = args["requirements"]
    suitable = [e for e in args["rows"] if e["role_match"] and e["skill_score"] >= 1.0 and e["has_capacity"]]
    cand_rows = [{"name": e["name"], "role": e["role"], "skills_matched": ", ".join(e["matched_skills"]) or "-",
                  "skills_missing": ", ".join(e["missing_skills"]) or "-", "remaining_hours": e["remaining_hours"],
                  "has_capacity": "yes" if e["has_capacity"] else "no", "score": e["score"]} for e in args["rows"][:5]]
    if not suitable:
        reasons = []
        if not any(e["role_match"] and e["skill_score"] >= 1.0 for e in args["rows"]):
            reasons.append("nobody has the required skills/role" + (f" ({', '.join(req['skills'])})" if req["skills"] else ""))
        else:
            reasons.append(f"everyone with the required skills lacks {req['effort_hours']:g}h of free capacity")
        msg = "No suitable employee found: " + "; ".join(reasons) + ". Escalating to the manager."
        raise Escalation(msg, {"title": "Task assignment - escalated", "summary": msg,
                               "sections": [{"heading": "Task", "content": req["description"]},
                                            {"heading": "Suggested next steps", "content": [
                                                "Re-prioritise someone's current work to free capacity",
                                                "Approve overtime or contractor support", "Relax the skill requirement / split the task"]}],
                               "tables": [{"name": "Closest candidates", "rows": cand_rows, "total": len(cand_rows), "columns": None, "limit": 5}],
                               "metrics": {}, "files": [], "notes": []})
    best = suitable[0]
    why = []
    if req["skills"]:
        why.append(f"Covers all required skills: {', '.join(req['skills'])}")
    if req["role"]:
        why.append(f"Role matches the requested '{req['role']}'")
    why.append(f"Has {best['remaining_hours']:g}h free this week (utilisation {best['utilization_pct']:.0f}%) vs {req['effort_hours']:g}h needed")
    if len(suitable) > 1:
        why.append(f"Ranked above {len(suitable) - 1} other suitable candidate(s) (score {best['score']} vs {suitable[1]['score']})")
    tc.decide(f"Selected {best['name']} - {len(suitable)} suitable candidate(s) out of {len(args['rows'])}")
    return {"selected": {"name": best["name"], "role": best["role"], "score": best["score"], "remaining_hours": best["remaining_hours"]},
            "reasoning": why, "candidates": cand_rows}
