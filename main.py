#!/usr/bin/env python
"""CLI for the AI Agent Workflow Automation system.

  python main.py "Which products need restocking?"        run one request
  python main.py                                          interactive chat loop
  python main.py --demo                                   run every example in examples/demo_scenarios.json
  python main.py --list | --validate                      inspect / lint the Excel workflow definitions
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from agent import Agent, Config
from agent.llm import get_llm
from agent.registry import list_tools
from agent.render import render_response

ROOT = Path(__file__).resolve().parent


def build_agent(args) -> Agent:
    cfg = Config()
    if args.workbook:
        cfg.workbook_path = Path(args.workbook)
    return Agent(cfg, llm=get_llm(args.llm) if args.llm else None)


def run_with_followups(agent: Agent, request: str, params=None, workflow_id=None, answers=None, interactive=True, max_turns=4, transcript=None):
    """Run; if the agent asks for more info, collect it (interactive prompt or scripted answers) and re-run."""
    params = dict(params or {})
    answers = dict(answers or {})
    resp = agent.run(request, params, workflow_id)
    for _ in range(max_turns):
        if resp.status == "clarify":
            if not interactive:
                break
            print(render_response(resp))
            pick = input("\nWorkflow id or number (blank to cancel): ").strip()
            if not pick:
                break
            alts = [w for w, _ in resp.routing.alternatives]
            workflow_id = alts[int(pick) - 1] if pick.isdigit() and 0 < int(pick) <= len(alts) else pick.upper()
            resp = agent.run(request, params, workflow_id)
            continue
        if resp.status != "needs_input":
            break
        wf_id = resp.workflow_id
        if interactive:
            print(render_response(resp))
        if transcript is not None:
            transcript.append(("agent asks", resp))
        got = False
        for m in resp.missing:
            val = answers.get(m["name"])
            if val is None and interactive:
                val = input(f"\n{m['ask']}\n> ").strip()
            if val:
                params[m["name"]] = val
                got = True
                if transcript is not None:
                    transcript.append((f"user answers ({m['name']})", val))
        if not got:
            break
        resp = agent.run(request, params, wf_id)
    return resp


def to_json(resp) -> str:
    d = asdict(resp)
    return json.dumps(d, indent=2, default=str)


def cmd_list(agent):
    print("WORKFLOWS (from Excel):")
    for wf in agent.workflows.values():
        print(f"  {wf.id}  {wf.name:<32} {len(wf.steps)} steps, {len(wf.input_specs)} inputs   e.g. \"{(wf.examples or [''])[0]}\"")
    print(f"\nREGISTERED TOOLS ({len(list_tools())}):")
    for name, t in sorted(list_tools().items()):
        print(f"  {name:<28} {t.description}")


def cmd_demo(agent, args):
    scen = json.loads((ROOT / "examples" / "demo_scenarios.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "examples" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    only = set(args.only.split(",")) if args.only else None
    combined = ["# Demo results (all scenarios)\n", f"_LLM mode: {agent.llm.name}_\n"]
    ok = 0
    for s in scen:
        if only and s["id"] not in only:
            continue
        tr = []
        resp = run_with_followups(agent, s["request"], s.get("params"), None, s.get("answers"), interactive=False, transcript=tr)
        parts = []
        for who, item in tr:
            if who == "agent asks":
                parts.append(f"--- TURN 1: agent stops and asks ---\n{item.message}\n")
            else:
                parts.append(f"--- {who}: {item}\n")
        if tr and s.get("answers"):
            parts.append("--- TURN 2: workflow re-run with the answers ---")
        text = "\n".join(parts + [render_response(resp)])
        print(text, "\n")
        (out_dir / f"{s['id']}.md").write_text(f"# {s['id']} - {s.get('title', '')}\n\n```text\n{text}\n```\n", encoding="utf-8")
        combined.append(f"\n## {s['id']} - {s.get('title', '')}\n\n```text\n{text}\n```\n")
        expected = s.get("expect_status", "success")
        flag = "PASS" if resp.status == expected and (not s.get("expect_workflow") or resp.workflow_id == s["expect_workflow"]) else "FAIL"
        ok += flag == "PASS"
        print(f">>> {s['id']}: {flag} (status={resp.status}, workflow={resp.workflow_id})\n")
    (out_dir / "ALL_RESULTS.md").write_text("".join(combined), encoding="utf-8")
    import shutil
    files_dir = out_dir / "files"
    files_dir.mkdir(exist_ok=True)
    for f in (ROOT / "outputs").glob("*.csv"):
        shutil.copy(f, files_dir / f.name)
    print(f"Demo finished: {ok}/{len([s for s in scen if not only or s['id'] in only])} scenarios behaved as expected. Saved to examples/outputs/")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request", nargs="*", help="natural-language request")
    ap.add_argument("--workflow", help="skip routing and force a workflow id (e.g. WF001)")
    ap.add_argument("--param", action="append", default=[], metavar="NAME=VALUE", help="provide a workflow input explicitly")
    ap.add_argument("--llm", choices=["auto", "anthropic", "openai", "none"], help="LLM provider (default: auto from env keys)")
    ap.add_argument("--workbook", help="use a different workflow workbook (e.g. the WF011 demo workbook)")
    ap.add_argument("--json", action="store_true", help="print the full response as JSON")
    ap.add_argument("--no-interactive", action="store_true", help="never prompt for missing inputs")
    ap.add_argument("--demo", action="store_true", help="run all demo scenarios and save outputs")
    ap.add_argument("--only", help="with --demo: comma separated scenario ids")
    ap.add_argument("--list", action="store_true", help="list workflows and tools")
    ap.add_argument("--validate", action="store_true", help="validate the Excel workflow definitions and exit")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        agent = build_agent(args)
    except Exception as e:
        print(f"Configuration error: {e}")
        return 2
    if args.validate:
        print(f"OK - {len(agent.workflows)} workflows, {sum(len(w.steps) for w in agent.workflows.values())} steps validated against {len(list_tools())} tools.")
        return 0
    if args.list:
        return cmd_list(agent) or 0
    print(f"[LLM: {agent.llm.name if agent.llm.available else 'none -> deterministic fallbacks'}]")
    if args.demo:
        return cmd_demo(agent, args) or 0

    params = dict(p.split("=", 1) for p in args.param if "=" in p)
    if args.request:
        resp = run_with_followups(agent, " ".join(args.request), params, args.workflow, interactive=not args.no_interactive)
        print(to_json(resp) if args.json else render_response(resp))
        return 0 if resp.status in ("success", "needs_input", "clarify", "escalated") else 1
    print("Interactive mode - type a request (blank line or 'exit' to quit).")
    while True:
        try:
            req = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if req.lower() in ("", "exit", "quit"):
            break
        resp = run_with_followups(agent, req, interactive=True)
        print(to_json(resp) if args.json else render_response(resp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
