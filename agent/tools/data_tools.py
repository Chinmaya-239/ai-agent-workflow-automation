"""Generic, reusable data tools (CSV/XLSX reader, calculator, filter, join, export, report).

These are deliberately workflow-agnostic: the *business rule* (e.g. ``current_stock < minimum_stock``)
lives in the Excel Step_Bindings sheet, not here.
"""
from __future__ import annotations

import re

from ..errors import ToolError
from ..registry import tool
from ..safe_eval import safe_eval
from ..util import norm_header, norm_key, read_table, to_number, write_csv


def _env(row: dict, tc, extra: dict | None = None) -> dict:
    env = dict(tc.inputs)
    env.update({k: v for k, v in row.items() if not str(k).startswith("_")})
    if extra:
        env.update(extra)
    return env


@tool("load_table", required=("path",))
def load_table(args, tc):
    """Read CSV/XLSX file(s), validate columns, coerce numeric columns, quarantine bad rows."""
    paths = args["path"] if isinstance(args["path"], list) else [args["path"]]
    sheet = args.get("sheet")
    rows, columns, used = [], [], []
    for p in paths:
        fp = tc.config.resolve_path(p)
        if not fp.exists() and args.get("skip_missing"):
            tc.note(f"optional file not found, skipped: {p}")
            continue
        r, c = read_table(fp, sheet)
        used.append(str(p))
        if args.get("normalize_headers", True):
            mp = {h: norm_header(h) for h in c}
            r = [{**{mp.get(k, k): v for k, v in row.items()}} for row in r]
            c = [mp[h] for h in c]
        rows += r
        columns = columns or c
    if not used:
        raise ToolError("No input file could be read")
    required = args.get("required_columns", [])
    missing = [c for c in required if c not in columns]
    if missing:
        raise ToolError(f"Missing required column(s) {missing} in {', '.join(used)}. Found: {columns}")

    strict = args.get("numeric_columns", [])
    optional = args.get("optional_numeric_columns", [])
    good, bad = [], []
    for row in rows:
        reason = None
        for col in strict + optional:
            if col not in row:
                continue
            try:
                val = to_number(row[col])
            except ValueError:
                reason = f"non-numeric value '{row[col]}' in column '{col}'"
                break
            if val is None and col in strict:
                reason = f"missing value in column '{col}'"
                break
            row[col] = val
        if reason:
            bad.append({**row, "row_number": row.get("_row"), "invalid_reason": reason})
        else:
            good.append(row)
    if bad:
        tc.note(f"{len(bad)} row(s) quarantined for bad numeric data (not processed)")
    if not good and not bad:
        raise ToolError(f"{', '.join(used)} contains no data rows")
    return {"path": ", ".join(used), "rows": good, "columns": columns, "row_count": len(good),
            "invalid_rows": bad, "invalid_count": len(bad)}


@tool("filter_rows", required=("rows", "where"))
def filter_rows(args, tc):
    """Keep rows for which the Excel-defined expression is true."""
    keep, errs = [], 0
    for row in args["rows"]:
        try:
            if safe_eval(args["where"], _env(row, tc)):
                keep.append(row)
        except TypeError:
            errs += 1
    total = len(args["rows"])
    tc.decide(f"Rule `{args.get('rule') or args['where']}` matched {len(keep)} of {total} rows")
    if errs:
        tc.note(f"{errs} row(s) could not be evaluated (missing data) and were excluded")
    return {"rows": keep, "count": len(keep), "total": total}


@tool("compute_columns", required=("rows", "columns"))
def compute_columns(args, tc):
    """Calculator: add derived columns using safe expressions (evaluated in order)."""
    out = []
    for row in args["rows"]:
        new = dict(row)
        for name, expr in args["columns"].items():
            try:
                new[name] = safe_eval(expr, _env(new, tc))
            except (TypeError, ZeroDivisionError):
                new[name] = None
        out.append(new)
    return {"rows": out, "count": len(out)}


@tool("sort_rows", required=("rows", "by"))
def sort_rows(args, tc):
    by = args["by"]
    rows = sorted(args["rows"], key=lambda r: (r.get(by) is None, r.get(by)), reverse=bool(args.get("descending")))
    return {"rows": rows, "count": len(rows)}


@tool("join_tables", required=("left", "right", "key"))
def join_tables(args, tc):
    """Join two tables on a (normalised) key, e.g. internal SKU = vendor SKU ignoring case/dashes/spaces."""
    key, rkey = args["key"], args.get("right_key") or args["key"]
    bring = args.get("bring")
    idx, dup = {}, 0
    for r in args["right"]:
        k = norm_key(r.get(rkey))
        if k in idx:
            dup += 1
            continue
        idx[k] = r
    matched, unmatched_left, seen = [], [], set()
    for l in args["left"]:
        k = norm_key(l.get(key))
        r = idx.get(k)
        if r is None:
            unmatched_left.append(l)
            continue
        seen.add(k)
        extra = {c: r.get(c) for c in (bring or [c for c in r if not c.startswith("_") and c != rkey])}
        matched.append({**l, **extra})
    unmatched_right = [r for k, r in idx.items() if k not in seen]
    if dup:
        tc.note(f"{dup} duplicate key(s) in right table ignored (first occurrence kept)")
    tc.decide(f"Matched {len(matched)} rows on '{key}'; {len(unmatched_left)} left-only, {len(unmatched_right)} right-only")
    return {"rows": matched, "count": len(matched), "unmatched_left": unmatched_left,
            "unmatched_right": [x for x in unmatched_right], "unmatched_left_count": len(unmatched_left),
            "unmatched_right_count": len(unmatched_right)}


@tool("dedupe_rows", required=("rows", "key"))
def dedupe_rows(args, tc):
    key, seen, keep, removed = args["key"], {}, [], []
    for r in args["rows"]:
        k = re.sub(r"\s+", " ", str(r.get(key, "")).strip().lower())
        if not k:
            continue
        if k in seen:
            removed.append({**r, "duplicate_of": seen[k]})
        else:
            seen[k] = r.get(key)
            keep.append(r)
    tc.decide(f"Removed {len(removed)} duplicate '{key}' value(s) (case/whitespace-insensitive)")
    return {"rows": keep, "removed": removed, "count": len(keep), "removed_count": len(removed)}


@tool("partition_rows", required=("rows", "flag"))
def partition_rows(args, tc):
    flag = args["flag"]
    valid = [r for r in args["rows"] if r.get(flag)]
    invalid = [r for r in args["rows"] if not r.get(flag)]
    return {"valid_rows": valid, "invalid_rows": invalid, "valid_count": len(valid), "invalid_count": len(invalid),
            "total": len(args["rows"])}


@tool("export_tables", required=("tables",))
def export_tables(args, tc):
    """Write each named table to <directory>/<prefix>_<name>.csv"""
    directory = tc.config.resolve_path(args.get("directory") or tc.config.outputs_dir)
    prefix = args.get("prefix") or tc.workflow.id.lower()
    files = []
    for name, rows in args["tables"].items():
        cols = (args.get("columns") or {}).get(name)
        p = write_csv(rows or [], directory / f"{prefix}_{name}.csv", cols)
        files.append(_rel(p, tc))
    return {"files": files, "count": len(files)}


def _rel(p, tc) -> str:
    try:
        return str(p.relative_to(tc.config.root))
    except ValueError:
        return str(p)


@tool("make_report", required=("title",))
def make_report(args, tc):
    """Assemble the final, renderable result: summary + metrics + sections + tables (+ optional CSV export)."""
    tables = []
    files = list(args.get("files") or [])
    for name, spec in (args.get("tables") or {}).items():
        spec = spec if isinstance(spec, dict) and "rows" in spec else {"rows": spec}
        rows = list(spec.get("rows") or [])
        if spec.get("sort_by"):
            sb = spec["sort_by"]
            rows.sort(key=lambda r: (r.get(sb) is None, r.get(sb)), reverse=bool(spec.get("descending")))
        cols = spec.get("columns")
        if spec.get("export") and rows:
            slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            p = write_csv(rows, tc.config.outputs_dir / f"{tc.workflow.id.lower()}_{slug}.csv", cols)
            files.append(_rel(p, tc))
        tables.append({"name": name, "rows": rows, "total": len(rows), "columns": cols, "limit": spec.get("limit", 20)})
    sections = [{"heading": h, "content": c} for h, c in (args.get("sections") or {}).items()]
    return {"title": args["title"], "summary": args.get("summary", ""), "metrics": args.get("metrics") or {},
            "sections": sections, "tables": tables, "files": files, "notes": [n for n in (args.get("notes") or []) if n]}
