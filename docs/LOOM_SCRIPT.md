# Loom walkthrough (aim for ~8-10 min) - talk in your own words

**0. Hook (20s)** "One generic agent that turns Excel-defined workflows into executable pipelines. No per-workflow chatbots."

**1. Architecture (1.5 min)** Show the diagram in README. Router → input resolver → engine → tools → result. Say *why*: config-driven, own small engine instead of a graph framework (linear flow, easier to test/explain), LLM for judgement, code for numbers.

**2. How Excel is processed (1.5 min)** Open `workflows/ai_agent_workflows.xlsx`. Original sheets untouched; show `Input_Spec`, `Step_Bindings` (tool, args, Condition, On_Error), `Routing_Hints`. Run `python main.py --validate` and `python main.py --list`.

**3. Workflow identification (1 min)** Explain LLM tool call `select_workflow` + TF-IDF fallback + confidence threshold. Demo: `python main.py "Anything running low in the warehouse?"` (paraphrase) and `python main.py "What's the weather?"` → asks instead of guessing.

**4. Live examples (3 min)** Run in the CLI (point at *Selected Workflow / Steps Executed / Decisions / Result*):
- `Which products need restocking?` (WF001: threshold rule, bad rows quarantined)
- `Find products where vendor price differs by more than 10%.` (WF002: boundary cases)
- `Where is order ORD-1006?` (WF005: carrier timeout → **retry** → success) and `Track order ORD-1005` (retries exhausted → **skip**)
- `Where is order ORD-9999?` (asks for another identifier)
- `Create a campaign brief for the new collection.` (stops, asks goal/dates, then runs)
- `Assign a Kubernetes migration task that needs about 20 hours` (**escalation**)
- `Which workflows are failing most often?` (WF010 reading the agent's own logs)
Mention the others are in `examples/outputs/ALL_RESULTS.md` (`python main.py --demo`).

**5. Tools, conditions, errors (1 min)** Show `agent/engine.py` (condition, On_Error policies) and `agent/tools/data_tools.py` (generic tools). Mention safe expression evaluator, no `eval`.

**6. 11th workflow (1 min)** `python scripts/add_wf011_example.py` then `python main.py --workbook workflows/ai_agent_workflows_with_wf011.xlsx "Which products have a low margin?"` - zero Python changes. Show `docs/ADDING_A_WORKFLOW.md`.

**7. Decisions & limits (30s)** Tests (`pytest -q`), fallback mode, simulated APIs, what you'd do next (vector routing, real DB/API connectors, async/parallel steps, UI).

Tip: set an API key in `.env` before recording so the router/extraction run through the LLM, and say which mode shows in the `[LLM: ...]` line.
