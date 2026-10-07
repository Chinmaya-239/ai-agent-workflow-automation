"""PROOF OF EXTENSIBILITY: add an 11th workflow using ONLY spreadsheet rows - no Python changes.

Creates workflows/ai_agent_workflows_with_wf011.xlsx (a copy of the main workbook + WF011 'Margin Analysis')
built entirely from existing generic tools (load_table, join_tables, compute_columns, filter_rows, make_report).

  python scripts/add_wf011_example.py
  python main.py --workbook workflows/ai_agent_workflows_with_wf011.xlsx --llm none "Which products have a low margin?"
"""
import json
import shutil
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "workflows" / "ai_agent_workflows.xlsx"
OUT = ROOT / "workflows" / "ai_agent_workflows_with_wf011.xlsx"
shutil.copy(SRC, OUT)
wb = openpyxl.load_workbook(OUT)

wb["Workflows"].append(["WF011", "Margin Analysis", "User asks which products have low margins",
                        "Product CSV; vendor cost list; minimum margin %",
                        "Load products → load vendor costs → match by SKU → calculate margin → flag low-margin products → report",
                        "Flag products whose margin % is below the minimum margin", "CSV reader; calculator",
                        "List of low-margin products with price, cost and margin %"])
wb["Test_Questions"].append(["WF011", "Which products have a low margin?", "Tests that a new workflow works with zero code changes"])
wb["Routing_Hints"].append(["WF011", "margin margins profit profitability low margin cost markup"])

for row in [
    ("WF011", "products_path", "file", "N", "data/products.csv", "Internal product CSV", "", "", ""),
    ("WF011", "costs_path", "file", "N", "data/vendor_prices.csv", "Vendor cost list", "", "", ""),
    ("WF011", "min_margin_pct", "number", "N", "15", "Minimum acceptable margin %", "", r"(\d+(?:\.\d+)?)\s*%", ""),
]:
    wb["Input_Spec"].append(list(row))

steps = [
    (1, "Load products", "load_table", dict(path="{{inputs.products_path}}", required_columns=["sku", "product_name", "price"], numeric_columns=["price"]), "products", "", "abort"),
    (2, "Load vendor costs", "load_table", dict(path="{{inputs.costs_path}}", required_columns=["sku", "vendor_price"], numeric_columns=["vendor_price"]), "costs", "", "abort"),
    (3, "Match by SKU", "join_tables", dict(left="{{ctx.products.rows}}", right="{{ctx.costs.rows}}", key="sku", bring=["vendor_price"]), "matched", "", "abort"),
    (4, "Calculate margin", "compute_columns", dict(rows="{{ctx.matched.rows}}", columns={"margin_pct": "round((price - vendor_price) / price * 100, 1) if price else None"}), "margins", "", "abort"),
    (5, "Flag low-margin products", "filter_rows", dict(rows="{{ctx.margins.rows}}", where="margin_pct is not None and margin_pct < min_margin_pct", rule="margin_pct < min_margin_pct"), "low", "", "abort"),
    (6, "Generate margin report", "make_report", dict(title="Low-margin products", summary="{{ctx.low.count}} of {{ctx.low.total}} matched products have a margin below {{inputs.min_margin_pct}}%.",
        tables={"Low-margin products": {"rows": "{{ctx.low.rows}}", "columns": ["sku", "product_name", "price", "vendor_price", "margin_pct"], "sort_by": "margin_pct"}}), "result", "", "abort"),
]
for no, name, tool, args, out, cond, err in steps:
    wb["Step_Bindings"].append(["WF011", no, name, tool, json.dumps(args), out, cond, err, ""])
wb.save(OUT)
print("wrote", OUT)
