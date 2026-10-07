"""WF006 - duplicate product detection (exact SKU = definite, attribute+name similarity = possible)."""
from __future__ import annotations

import difflib
import re
from collections import defaultdict
from itertools import combinations

from ..registry import tool
from ..util import norm_key


def _norm_name(s) -> str:
    s = str(s or "").lower().replace("'", "")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(sorted(s.split()))


@tool("normalize_fields", required=("rows",))
def normalize_fields(args, tc):
    out = [{**r, "norm_sku": norm_key(r.get("sku")), "norm_name": _norm_name(r.get("product_name"))} for r in args["rows"]]
    return {"rows": out, "count": len(out)}


@tool("group_exact", required=("rows", "key"))
def group_exact(args, tc):
    g = defaultdict(list)
    for i, r in enumerate(args["rows"]):
        if r.get(args["key"]):
            g[r[args["key"]]].append(i)
    groups = [{"key": k, "members": v} for k, v in g.items() if len(v) > 1]
    tc.decide(f"{len(groups)} group(s) share an exact normalised SKU -> definite duplicates")
    return {"groups": groups, "count": len(groups)}


def _name_sim(a: str, b: str) -> float:
    ta, tb = set(a.split()), set(b.split())
    jac = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
    return 0.5 * jac + 0.5 * difflib.SequenceMatcher(None, a, b).ratio()


@tool("find_similar_pairs", required=("rows", "attribute_fields"))
def find_similar_pairs(args, tc):
    """Pairwise name + attribute similarity within blocks (blocking avoids O(n^2) over a full catalog)."""
    rows, attrs = args["rows"], args["attribute_fields"]
    thr = float(args.get("threshold") or 0.75)
    block_field = args.get("block_field")
    exact_pairs = set()
    for g in (args.get("exclude_groups") or []):
        for a, b in combinations(g["members"], 2):
            exact_pairs.add((a, b))
    blocks = defaultdict(list)
    for i, r in enumerate(rows):
        blocks[(str(r.get(block_field, "")).lower() if block_field else "*")].append(i)
    pairs = []
    for idxs in blocks.values():
        for i, j in combinations(idxs, 2):
            if (i, j) in exact_pairs:
                continue
            a, b = rows[i], rows[j]
            ns = _name_sim(a["norm_name"], b["norm_name"])
            comparable = [(f, str(a[f]).strip().lower() == str(b[f]).strip().lower())
                          for f in attrs if a.get(f) not in (None, "") and b.get(f) not in (None, "")]
            attr = (sum(1 for _, ok in comparable if ok) / len(comparable)) if comparable else 0.5
            score = 0.6 * ns + 0.4 * attr
            variant_diff = [f for f, ok in comparable if not ok and f in ("color", "size", "model", "variant")]
            if variant_diff:
                score = min(score, 0.69)          # same family, different colour/size => a variant, not a duplicate
            if score >= thr:
                pairs.append({"a": i, "b": j, "score": round(score, 3), "name_similarity": round(ns, 3),
                              "matching": [f for f, ok in comparable if ok],
                              "differing": [f for f, ok in comparable if not ok]})
    tc.decide(f"{len(pairs)} pair(s) reached similarity >= {thr} (colour/size mismatch caps a pair below the threshold)")
    return {"pairs": pairs, "count": len(pairs), "threshold": thr}


@tool("build_duplicate_groups", required=("rows", "exact", "similar"))
def build_duplicate_groups(args, tc):
    rows = args["rows"]
    groups = []
    for g in args["exact"]["groups"]:
        groups.append({"members": g["members"], "type": "exact_sku", "score": 1.0,
                       "matching": ["sku"], "differing": []})
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    info = defaultdict(list)
    for p in args["similar"]["pairs"]:
        parent[find(p["a"])] = find(p["b"])
    for p in args["similar"]["pairs"]:
        info[find(p["a"])].append(p)
    for root, plist in info.items():
        members = sorted({m for p in plist for m in (p["a"], p["b"])})
        groups.append({"members": members, "type": "similar", "score": min(p["score"] for p in plist),
                       "matching": sorted(set.intersection(*[set(p["matching"]) for p in plist])),
                       "differing": sorted(set().union(*[set(p["differing"]) for p in plist]))})
    return {"groups": groups, "rows": rows, "count": len(groups)}


@tool("assign_confidence", required=("groups", "rows"))
def assign_confidence(args, tc):
    high = float(args.get("high_threshold") or 0.9)
    rows, out = args["rows"], []
    for n, g in enumerate(sorted(args["groups"], key=lambda g: (g["type"] != "exact_sku", -g["score"])), start=1):
        if g["type"] == "exact_sku":
            conf = "DEFINITE"
        elif g["score"] >= high:
            conf = "POSSIBLE - HIGH"
        else:
            conf = "POSSIBLE - MEDIUM"
        members = [str(rows[i].get("sku")) for i in g["members"]]
        out.append({"group": f"G{n}", "confidence": conf, "score": round(g["score"], 2), "members": ", ".join(members),
                    "example_name": rows[g["members"][0]].get("product_name"),
                    "matching_fields": ", ".join(g["matching"]) or "-", "differing_fields": ", ".join(g["differing"]) or "-"})
    tc.decide("Exact SKU match => DEFINITE; name/attribute similarity => POSSIBLE (HIGH if score >= %.2f)" % high)
    return {"rows": out, "count": len(out),
            "definite": sum(1 for r in out if r["confidence"] == "DEFINITE"),
            "possible": sum(1 for r in out if r["confidence"] != "DEFINITE")}
