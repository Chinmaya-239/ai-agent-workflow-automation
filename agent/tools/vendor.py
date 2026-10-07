"""WF003 - vendor file processing: detect columns, normalise, validate."""
from __future__ import annotations

import difflib

from ..errors import ToolError
from ..registry import tool
from ..util import norm_header, to_number

SYNONYMS = {
    "sku": ["sku", "item_no", "item_number", "item_code", "item_id", "product_code", "product_id", "part_no", "part_number", "article_no", "upc", "code"],
    "product_name": ["product_name", "product_title", "title", "name", "item_name", "description", "product", "item_description"],
    "price": ["price", "unit_price", "unit_cost", "cost", "cost_price", "vendor_price", "wholesale_price", "msrp", "rate"],
    "quantity": ["quantity", "qty", "qty_on_hand", "stock", "on_hand", "units", "inventory"],
    "category": ["category", "product_category", "dept", "department", "type", "group"],
    "color": ["color", "colour"],
    "brand": ["brand", "manufacturer", "vendor", "supplier"],
}


@tool("detect_columns", required=("columns",))
def detect_columns(args, tc):
    """Map arbitrary vendor headers to canonical fields (exact synonym > substring > fuzzy match)."""
    syn = args.get("synonyms") or SYNONYMS
    headers = {h: norm_header(h) for h in args["columns"] if not str(h).startswith("_")}
    mapping, method, used = {}, {}, set()
    for canon, alts in syn.items():
        pick = None
        for h, n in headers.items():                       # 1. exact synonym
            if h not in used and n in alts:
                pick, how = h, "exact synonym"
                break
        if not pick:                                        # 2. canonical / synonym token inside header
            for h, n in headers.items():
                if h not in used and any(a in n.split("_") for a in alts if "_" not in a):
                    pick, how = h, "keyword in header"
                    break
        if not pick:                                        # 3. fuzzy
            for h, n in headers.items():
                if h not in used and difflib.get_close_matches(n, alts, n=1, cutoff=0.8):
                    pick, how = h, "fuzzy match"
                    break
        if pick:
            mapping[canon], method[canon] = pick, how
            used.add(pick)
    unmapped = [h for h in headers if h not in used]
    for canon, h in mapping.items():
        tc.note(f"'{h}' -> {canon} ({method[canon]})")
    for need in args.get("required", ["sku", "product_name"]):
        if need not in mapping:
            raise ToolError(f"Could not detect a '{need}' column. Headers found: {list(headers)}")
    return {"mapping": mapping, "methods": method, "unmapped": unmapped}


@tool("normalize_vendor_rows", required=("rows", "mapping"))
def normalize_vendor_rows(args, tc):
    """Rename columns to canonical names, trim whitespace, upper-case SKUs, parse prices."""
    inv = {v: k for k, v in args["mapping"].items()}
    out, bad_price = [], 0
    for r in args["rows"]:
        n = {"_row": r.get("_row")}
        for col, val in r.items():
            if col == "_row":
                continue
            n[inv.get(col, col)] = val.strip() if isinstance(val, str) else val
        if n.get("sku"):
            n["sku"] = str(n["sku"]).strip().upper()
        for numeric in ("price", "quantity"):
            if numeric in n and n[numeric] not in (None, ""):
                try:
                    n[numeric] = to_number(n[numeric])
                except ValueError:
                    n[f"{numeric}_warning"] = f"unparseable {numeric} '{n[numeric]}'"
                    n[numeric] = None
                    bad_price += 1
        out.append(n)
    if bad_price:
        tc.note(f"{bad_price} unparseable numeric value(s) set to blank (flagged in *_warning columns)")
    return {"rows": out, "count": len(out)}


@tool("validate_rows", required=("rows", "required"))
def validate_rows(args, tc):
    """Flag each row valid/invalid. Business rule: rows missing SKU or product name are invalid."""
    req = args["required"]
    out = []
    for r in args["rows"]:
        missing = [f for f in req if r.get(f) in (None, "")]
        r = dict(r)
        r["is_valid"] = not missing
        r["row_number"] = r.get("_row")
        r["invalid_reason"] = ("missing " + ", ".join(missing)) if missing else ""
        out.append(r)
    n_bad = sum(1 for r in out if not r["is_valid"])
    tc.decide(f"Required fields {req}: {n_bad} of {len(out)} rows invalid")
    return {"rows": out, "count": len(out)}
