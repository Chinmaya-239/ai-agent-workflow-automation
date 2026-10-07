# Adding an 11th workflow

**Case 1 - uses existing tools (no code).** Worked example: `python scripts/add_wf011_example.py` creates a workbook with "Margin Analysis".

1. `Workflows` sheet: add a row (ID, name, trigger, inputs, steps, decision logic, tools, expected output).
2. `Input_Spec`: one row per input (`Type` = text | number | file | file_list | identifier | date_range | date | object; `Required` Y/N; `Default`; `Ask_Prompt`; optional `Extract_Regex`).
3. `Step_Bindings`: one row per step - `Tool`, `Args_JSON` (use `{{inputs.x}}`, `{{ctx.previous_output.field}}`, `{{config.outputs_dir}}`), `Output_Key`, optional `Condition`, `On_Error`. The last step must write `Output_Key = result` (use `make_report`).
4. `Routing_Hints`: a few words users would say. (Optional) add a `Test_Questions` row.
5. `python main.py --validate` - catches unknown tools, missing args, bad templates.

**Case 2 - needs a new capability.** Add one function anywhere in `agent/tools/`:

```python
from agent.registry import tool
@tool("my_new_tool", required=("rows",))
def my_new_tool(args, tc):          # tc.llm, tc.inputs, tc.ctx, tc.note(), tc.decide()
    ...
    return {...}
```
It is auto-discovered and can be referenced by name from `Step_Bindings`. Raise `NeedInput` to ask the user, `Escalation` to hand off, `ToolError` for retry/skip/abort handling.
