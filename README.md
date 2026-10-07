# AI Agent Workflow Automation

An agent that reads **10 business workflows from an Excel file**, understands a plain-English request, picks the right workflow, runs its steps through tools, handles conditions/errors, and returns the result - showing *which workflow was selected, which steps ran, and the final output*.

**Key design decision:** there are **no 10 hard-coded chatbots**. One generic engine executes whatever the Excel workbook describes. Adding an 11th workflow = adding spreadsheet rows (proven in [`scripts/add_wf011_example.py`](scripts/add_wf011_example.py), zero Python changes).

```
User request
    │
    ▼
┌─────────┐  LLM tool-call `select_workflow` over a catalog built from Excel
│ Router  │  └─ fallback: TF-IDF keyword router · low confidence ⇒ asks, never guesses
└────┬────┘
     ▼
┌────────────────┐  typed inputs from Input_Spec: LLM extraction → regex fallback → defaults
│ Input resolver │  └─ required input missing ⇒ agent STOPS and asks the user
└────┬───────────┘
     ▼
┌─────────────────────────── Workflow engine (generic) ───────────────────────────┐
│ for each row of Step_Bindings: resolve {{templates}} → check Condition →       │
│ call registered Tool → apply On_Error (abort | skip | retry:N[+skip]) → trace   │
└────┬──────────────────────────────────────────────────────────────────────────┘
     ▼
Tools (registry) ── generic: load_table, filter_rows, compute_columns, join_tables, make_report …
                    domain:  detect_columns, find_similar_pairs, analyze_task, classify_intent …
     ▼
Final result + step trace + decisions  (CLI text / JSON / markdown files, CSV exports)
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                      # optional: add ANTHROPIC_API_KEY or OPENAI_API_KEY

python main.py "Which products need restocking?"          # one request
python main.py                                            # interactive chat (agent asks follow-ups)
python main.py --demo                                     # runs 21 scenarios, saves to examples/outputs/
python main.py --list                                     # workflows (from Excel) + registered tools
python main.py --validate                                 # lint the Excel workflow definitions
pytest -q                                                 # 47 tests
```

**No API key?** Everything still runs: every LLM call has a deterministic fallback (keyword router, regex extraction, rule-based classifier, template copy). With a key, routing, input extraction, content generation, intent classification, task analysis and recommendations use the LLM through *tool calling* (forced `tool_use` / function call returning schema-validated JSON). Output shows `[LLM: ...]` so you always know which mode ran.

## The Excel file is the source of truth (`workflows/ai_agent_workflows.xlsx`)

| Sheet | Origin | Purpose |
|---|---|---|
| `Workflows`, `Test_Questions` | **original, untouched** | Name, trigger, inputs, steps, decision logic, tools, expected output; sample requests |
| `Input_Spec` | added | Per workflow input: type, required?, default, question to ask the user, extraction regex |
| `Step_Bindings` | added | Each Excel step → registered **tool**, templated args, optional **Condition**, **On_Error** policy, output key |
| `Routing_Hints` | added | Extra vocabulary for the router |

Business rules live in the sheet, not in Python, e.g. WF001 step 3 `where = below_threshold` (`current_stock < threshold`), WF002 `status != 'OK'` where status uses `abs(pct_diff) > threshold_pct`. `python scripts/build_workbook.py` regenerates the three added sheets from the original (documented authoring script; the runtime only reads the xlsx).

## The 10 workflows

| ID | Workflow | Key logic / how conditions & errors are handled |
|---|---|---|
| WF001 | Inventory Restock | `stock < minimum` (equal is *not* low); reorder up to target; non-numeric rows quarantined and reported |
| WF002 | Price Validation | SKU matched ignoring case/dashes/spaces; flag `\|diff%\| > 10` (exactly 10 is OK); zero vendor price → "CANNOT VALIDATE"; unmatched SKUs on both sides reported |
| WF003 | Vendor File Processing | CSV/XLSX; header detection (synonym → keyword → fuzzy); rows missing SKU/name invalid with source row number; writes cleaned + invalid CSVs |
| WF004 | Product Content | Name mandatory (else asks); missing attributes **never invented** and listed as MISSING; length limits + invented-colour/material guard |
| WF005 | Order Status | ID/email validated; not found ⇒ asks for another identifier; shipment step has a **Condition** (skipped if nothing shipped) and **retry:2+skip** against a simulated flaky carrier API |
| WF006 | Duplicate Detection | exact normalised SKU = DEFINITE; name+attribute similarity = POSSIBLE (HIGH/MEDIUM); colour/size differences ⇒ variant, not duplicate; blocking by category for scale |
| WF007 | Campaign Brief | Missing goal/dates ⇒ asks **before** any step runs; invalid date range re-asked; unspecified audience/promotion shown as "Not specified", not invented |
| WF008 | SEO Keywords | De-dupe → intent (LLM tool call; rule fallback; invalid labels rejected) → category/page mapping → priority score → CSV export; unmapped keywords flagged as content gaps |
| WF009 | Task Assignment | skills → workload → rank → select; role/skill/capacity/on-leave aware; **escalates** when nobody suitable (incl. a required skill nobody has) |
| WF010 | Performance Report | Reads seeded history **plus the agent's own `logs/runtime_logs.csv`**; flags failure rate > 10% or avg time > threshold; top errors, slow steps, recommendations |

Example inputs/outputs for all of them (plus failure-path scenarios): [`examples/demo_scenarios.json`](examples/demo_scenarios.json) → [`examples/outputs/`](examples/outputs/) (`ALL_RESULTS.md`, per-scenario `.md`, exported CSVs in `files/`).

## Sample output

```
Selected Workflow:
  WF001 - Inventory Restock Check   (router: keyword-tfidf, confidence 0.89)
Steps Executed:
  1. [OK]   Load inventory  <load_table> - row_count=11
  2. [OK]   Compare current stock with minimum threshold  <compute_columns>
  3. [OK]   Identify low-stock products  <filter_rows> - count=6, total=11
  4. [OK]   Calculate reorder quantity  <compute_columns>
  5. [OK]   Generate restock list  <make_report>
Conditions / Decisions:
  - Rule `current_stock < minimum_stock (threshold)` matched 6 of 11 rows
Result: 6 of 11 products need restocking … (table with current stock, threshold, suggested reorder qty)
```

## Why this architecture (technical decisions)

* **Config-driven engine over per-workflow code** - the assignment's core requirement. Reusability: ~20 generic tools cover most steps. Scalability: new workflow = rows; new capability = one `@tool` function (auto-discovered). Maintainability: `--validate` lints the workbook (unknown tools, missing args, templates referencing outputs that don't exist yet, bad error policies) so a spreadsheet typo fails at load, not mid-run.
* **Own small engine instead of LangGraph/LangChain** - the flow is a linear pipeline with conditions/retries, so a ~150-line engine is easier to explain, test and debug than a graph framework, and it keeps the LLM provider-neutral (Anthropic/OpenAI behind one interface). The tool registry + state dict maps 1:1 onto LangGraph nodes if a graph is ever needed.
* **LLM where judgement is needed, code where correctness is needed** - LLM: routing, extraction, classification, copy. Deterministic code: thresholds, joins, maths, validation. Numbers are never produced by an LLM.
* **Safe by construction** - rules in Excel run through a whitelisted AST evaluator (no `eval`); LLM output is schema-constrained then validated (unknown workflow id, invalid intent label, invented attributes → fallback/flag); the engine never crashes on a tool bug (returns `failed` with the step and reason).
* **Ask, don't guess** - low routing confidence, missing required inputs, unknown order, bad dates all return a question instead of a fabricated answer; the CLI then re-runs with the answer.
* **Observability** - every response lists workflow, router method/confidence, input sources (user / extracted / default), per-step status/time/attempts, and decisions; every step is logged to CSV (and WF010 analyses it).

## Error / condition handling summary

`On_Error` per step: `abort` (default) · `skip` · `retry:N` · `retry:N+skip`. Tools can raise `NeedInput` (agent asks the user), `Escalation` (hand to a human), or `ToolError` (retry/skip/abort policy). `Condition` skips steps (WF005 shipment lookup). Statuses: `success | needs_input | clarify | escalated | failed`.

## Project layout

```
main.py                     CLI (single request, chat, --demo, --list, --validate, --workbook)
agent/                      engine.py router.py input_resolver.py agent.py excel_loader.py registry.py render.py …
agent/llm/                  provider-neutral interface + Anthropic / OpenAI implementations
agent/tools/                data_tools (generic) + vendor, content, orders, duplicates, campaign, keywords, hr, reporting
workflows/                  ai_agent_workflows.xlsx (source of truth) · original_assessment.xlsx · WF011 demo workbook
data/                       sample CSV/JSON (inventory, products, vendor prices, orders, shipments, catalog, keywords, employees, execution logs)
examples/                   demo_scenarios.json + saved outputs
tests/                      47 tests (business rules, failure paths, router, LLM paths via fake provider, 11th workflow)
docs/                       ADDING_A_WORKFLOW.md · LOOM_SCRIPT.md
scripts/                    generate_sample_data.py · build_workbook.py · add_wf011_example.py
```

## Testing

`pytest -q` covers every workflow's business rules (boundaries such as stock == minimum and exactly 10% price gap), failure paths (missing file/column, tool exception, carrier outage, retries), routing (14 phrasings incl. paraphrases, out-of-scope), workbook lint, and the LLM code paths through a fake provider (valid tool call, unknown id, outage ⇒ fallback). Live-provider calls need your API key: run `python main.py --demo` after setting it.

## Assumptions

* Sample data is synthetic; the order DB and carrier API are simulated (`data/orders.json`, `data/shipments.json`, with injected timeout/outage cases).
* WF002 % difference is relative to the vendor price. WF001 reorder qty = `reorder_target - stock` (or 2× threshold when no target). WF009 assumes 8h effort and a priority-based deadline when not stated (and says so in the output).
* WF010 treats runs ending in a question to the user or an escalation as *incomplete*, not failures.
