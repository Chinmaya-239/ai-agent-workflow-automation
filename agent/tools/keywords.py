"""WF008 - SEO keyword classification, category mapping and prioritisation."""
from __future__ import annotations

import math
import re
from collections import Counter

from ..errors import LLMError, ToolError
from ..registry import tool
from ..util import read_table, tokenize

INTENTS = ["informational", "commercial", "transactional", "navigational"]
RULES = [  # evaluated in order; first match wins
    ("navigational", r"\b(login|log in|sign in|official site|official website|website|homepage|contact|customer service|store locator|app download|\.com)\b"),
    ("transactional", r"\b(buy|purchase|order|shop|discount|coupon|deal|deals|sale|cheap|cheapest|price|pricing|for sale|near me|free shipping|online store|add to cart)\b"),
    ("commercial", r"\b(best|top|review|reviews|vs|versus|compare|comparison|alternative|alternatives|recommended|rated|worth it|which)\b"),
    ("informational", r"\b(how|what|why|when|where|who|guide|tutorial|tips|ideas|meaning|definition|difference|examples?|learn|can i|does)\b"),
]


def rule_intent(kw: str, brand_terms=()):
    k = kw.lower()
    if any(b in k for b in brand_terms):
        return "navigational", "brand term"
    for intent, pat in RULES:
        m = re.search(pat, k)
        if m:
            return intent, f"keyword '{m.group(1)}'"
    return "commercial", "no modifier found; product-type query defaulted to commercial"


@tool("classify_intent", required=("rows", "field"))
def classify_intent(args, tc):
    rows, field = args["rows"], args["field"]
    brand = [b.lower() for b in (args.get("brand_terms") or [])]
    labels = {}
    mode = "rules"
    if tc.llm.available and rows:
        try:
            for i in range(0, len(rows), 40):
                chunk = [r[field] for r in rows[i:i + 40]]
                out = tc.llm.structured(
                    "Classify each search keyword's intent as informational, commercial, transactional or navigational.",
                    "Keywords:\n" + "\n".join(f"{n}. {k}" for n, k in enumerate(chunk)),
                    "classify_keywords", "Return one intent per keyword index",
                    {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
                        "index": {"type": "integer"}, "intent": {"type": "string", "enum": INTENTS}}, "required": ["index", "intent"]}}},
                     "required": ["items"]})
                for it in out.get("items", []):
                    if it.get("intent") in INTENTS and isinstance(it.get("index"), int) and 0 <= it["index"] < len(chunk):
                        labels[i + it["index"]] = it["intent"]
            mode = f"{tc.llm.name} (rules used for any keyword the model skipped)"
        except LLMError as e:
            tc.note(f"LLM classification failed ({e}); rule-based classifier used")
            labels = {}
    out, from_rules = [], 0
    for n, r in enumerate(rows):
        if n in labels:
            intent, src = labels[n], "llm"
        else:
            intent, why = rule_intent(r[field], brand)
            src = f"rule: {why}"
            from_rules += 1
        out.append({**r, "intent": intent, "intent_source": src})
    counts = Counter(r["intent"] for r in out)
    tc.decide(f"Intent classification mode: {mode}. Distribution: {dict(counts)}")
    return {"rows": out, "count": len(out), "intent_counts": dict(counts), "rule_based": from_rules}


@tool("map_keywords_to_categories", required=("rows", "categories_path"))
def map_keywords_to_categories(args, tc):
    cats, _ = read_table(tc.config.resolve_path(args["categories_path"]))
    if not cats:
        raise ToolError("Category file is empty")
    prof = []
    for c in cats:
        terms = set(tokenize(c.get("category", "")))
        for t in re.split(r"[;|,]", c.get("terms", "")):
            terms |= set(tokenize(t))
        prof.append((c, terms))
    out, unmapped = [], 0
    for r in args["rows"]:
        kt = set(tokenize(r["keyword"]))
        best, best_s = None, 0.0
        for c, terms in prof:
            s = len(kt & terms)
            if s > best_s:
                best, best_s = c, s
        if best:
            out.append({**r, "category": best["category"], "target_page": best.get("page_url", ""), "mapping_strength": best_s})
        else:
            unmapped += 1
            out.append({**r, "category": "Unmapped", "target_page": "NEW PAGE NEEDED", "mapping_strength": 0})
    tc.decide(f"{len(out) - unmapped} keywords mapped to a category page; {unmapped} unmapped (content gap)")
    return {"rows": out, "count": len(out), "unmapped": unmapped}


@tool("prioritize_keywords", required=("rows",))
def prioritize_keywords(args, tc):
    """score = intent weight x log-scaled volume x difficulty factor x mapping factor (0-100)."""
    w = {"transactional": 1.0, "commercial": 0.8, "informational": 0.5, "navigational": 0.3}
    rows = args["rows"]
    vols = [r.get("search_volume") for r in rows if isinstance(r.get("search_volume"), (int, float))]
    vmax = max(vols) if vols else 0
    high, med = float(args.get("high_cutoff", 40)), float(args.get("medium_cutoff", 20))
    out = []
    for r in rows:
        v = r.get("search_volume")
        vol_n = math.log1p(v) / math.log1p(vmax) if isinstance(v, (int, float)) and vmax else 0.5
        d = r.get("difficulty")
        diff_f = 1 - (d / 200) if isinstance(d, (int, float)) else 0.85
        map_f = 1.0 if r.get("category") != "Unmapped" else 0.7
        score = round(100 * w[r["intent"]] * vol_n * diff_f * map_f, 1)
        pr = "High" if score >= high else "Medium" if score >= med else "Low"
        out.append({**r, "priority_score": score, "priority": pr})
    out.sort(key=lambda r: -r["priority_score"])
    n_high = sum(1 for r in out if r["priority"] == "High")
    tc.decide(f"Priority = High if score >= {high:g}, Medium if >= {med:g}: {n_high} high-priority keywords")
    return {"rows": out, "count": len(out), "high_count": n_high}
