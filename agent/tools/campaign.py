"""WF007 - marketing campaign brief."""
from __future__ import annotations

import re
from datetime import date, timedelta

from ..errors import LLMError, NeedInput
from ..registry import tool
from ..util import parse_date_range


@tool("validate_campaign_inputs", required=("goal", "dates"))
def validate_campaign_inputs(args, tc):
    dates = parse_date_range(args["dates"])
    if not dates:
        raise NeedInput([{"name": "campaign_dates", "ask": "Please give the campaign start and end dates (e.g. 2026-11-01 to 2026-11-30)."}])
    start, end = date.fromisoformat(dates["start"]), date.fromisoformat(dates["end"])
    if end < start:
        raise NeedInput([{"name": "campaign_dates", "ask": f"The end date {end} is before the start date {start}. Please re-enter the dates."}])
    optional_missing = [k for k in ("audience", "promotion") if not args.get(k)]
    if optional_missing:
        tc.decide(f"Optional inputs not provided: {optional_missing} - will be shown as 'not specified', not invented")
    return {"goal": args["goal"], "start": start.isoformat(), "end": end.isoformat(), "duration_days": (end - start).days + 1,
            "audience": args.get("audience") or "Not specified", "promotion": args.get("promotion") or "None specified",
            "optional_missing": optional_missing}


OBJECTIVES = [
    ("conversion", r"sale|revenue|convert|conversion|purchase|order|buy|boost|sell", "Drive sales / conversions", "Revenue, conversion rate, orders"),
    ("awareness", r"awareness|reach|visib|brand|launch|introduc|new collection|announce", "Build awareness / launch", "Reach, impressions, brand search lift"),
    ("engagement", r"engage|community|follow|social|content|interact", "Increase engagement", "Engagement rate, followers, shares"),
    ("retention", r"retention|loyal|repeat|returning|win.?back|churn", "Improve retention / loyalty", "Repeat purchase rate, CLV"),
    ("leads", r"lead|sign.?up|subscribe|newsletter|register", "Generate leads / sign-ups", "Leads, sign-ups, cost per lead"),
]


@tool("classify_objective", required=("goal",))
def classify_objective(args, tc):
    goal = args["goal"]
    kind = None
    if tc.llm.available:
        try:
            out = tc.llm.structured(
                "Classify the marketing campaign goal.", f"Goal: {goal}", "classify_goal", "Classify goal",
                {"type": "object", "properties": {"type": {"type": "string", "enum": [o[0] for o in OBJECTIVES]}}, "required": ["type"]})
            kind = out.get("type")
        except LLMError:
            kind = None
    if kind not in [o[0] for o in OBJECTIVES]:
        kind = next((o[0] for o in OBJECTIVES if re.search(o[1], goal, re.I)), "awareness")
    label, kpi = next((o[2], o[3]) for o in OBJECTIVES if o[0] == kind)
    target = re.search(r"\d+(?:\.\d+)?\s*%|\$\s?\d[\d,]*|\d[\d,]*\s*(?:orders|leads|sign-?ups)", goal, re.I)
    tc.decide(f"Goal classified as '{kind}' -> primary KPIs: {kpi}")
    return {"type": kind, "label": label, "statement": goal, "kpis": kpi, "target": target.group(0) if target else "not stated"}


@tool("summarize_products", required=("rows",))
def summarize_products(args, tc):
    rows, flt = args["rows"], (args.get("product_filter") or "").lower()
    sel, basis = [], "all products"
    if flt:
        names = [r for r in rows if str(r.get("product_name", "")).lower() in flt or str(r.get("sku", "")).lower() in flt]
        if names:
            sel, basis = names, "products named in the request"
        elif any(w in flt for w in ("new", "latest", "collection")):
            coll = [r for r in rows if str(r.get("is_new", "")).lower() in ("yes", "true", "1", "y")]
            if coll:
                sel, basis = coll, "products flagged as new collection"
        else:
            cat = [r for r in rows if str(r.get("category", "")).lower() in flt]
            if cat:
                sel, basis = cat, "products in the requested category"
    if not sel:
        sel = rows
        if flt:
            tc.note(f"Could not match '{args['product_filter']}' to specific products; using the full catalog")
    cats: dict = {}
    for r in sel:
        cats[r.get("category", "n/a")] = cats.get(r.get("category", "n/a"), 0) + 1
    prices = [r["price"] for r in sel if isinstance(r.get("price"), (int, float))]
    tc.decide(f"Product scope: {len(sel)} {basis}")
    return {"count": len(sel), "basis": basis, "categories": cats,
            "price_range": f"{min(prices):.2f} - {max(prices):.2f}" if prices else "n/a",
            "items": [{"sku": r.get("sku"), "product_name": r.get("product_name"), "category": r.get("category"),
                       "price": r.get("price")} for r in sel]}


@tool("create_messaging", required=("objective", "products"))
def create_messaging(args, tc):
    obj, prod = args["objective"], args["products"]
    audience, promo = args.get("audience"), args.get("promotion")
    cats = ", ".join(prod["categories"]) or "our range"
    fallback = {
        "headline": f"{obj['label']}: discover {cats}" if obj["type"] != "conversion" else f"Shop {cats} while the offer lasts",
        "key_messages": [
            f"Introducing {prod['count']} products across {cats} (price range {prod['price_range']}).",
            f"Offer: {promo}." if promo and promo != "None specified" else "Highlight product quality and everyday value.",
            f"Built for {audience}." if audience and audience != "Not specified" else "Speak to a broad audience until a target segment is defined.",
        ],
        "call_to_action": "Shop now" if obj["type"] == "conversion" else "Discover the collection",
        "tone": "Clear, benefit-led, friendly",
    }
    if tc.llm.available:
        try:
            out = tc.llm.structured(
                "You are a marketing strategist. Write campaign messaging using ONLY the facts supplied "
                "(do not invent discounts, product features or claims).",
                f"Objective: {obj}\nAudience: {audience}\nPromotion: {promo}\nProducts: {prod['items'][:10]}",
                "campaign_messaging", "Campaign messaging",
                {"type": "object", "properties": {"headline": {"type": "string"}, "key_messages": {"type": "array", "items": {"type": "string"}},
                                                   "call_to_action": {"type": "string"}, "tone": {"type": "string"}},
                 "required": ["headline", "key_messages", "call_to_action", "tone"]})
            tc.note(f"messaging generated by {tc.llm.name}")
            return out
        except LLMError as e:
            tc.note(f"LLM unavailable ({e}); template messaging used")
    else:
        tc.note("template messaging (no LLM configured)")
    return fallback


@tool("recommend_channels", required=("objective",))
def recommend_channels(args, tc):
    kind, aud = args["objective"]["type"], (args.get("audience") or "").lower()
    base = {
        "conversion": [("Email / CRM", "Offer delivery to existing customers"), ("Paid search & shopping ads", "Capture high-intent demand"), ("Retargeting display", "Recover abandoned carts")],
        "awareness": [("Social media (organic + paid)", "Reach and storytelling"), ("Influencer / creator partnerships", "Borrowed trust and reach"), ("PR / press release", "Launch coverage")],
        "engagement": [("Instagram / TikTok", "Short-form content and UGC"), ("Community / loyalty app", "Ongoing interaction")],
        "retention": [("Email / SMS", "Personalised win-back and loyalty offers"), ("Loyalty programme", "Reward repeat purchase")],
        "leads": [("Landing page + SEO", "Capture sign-ups"), ("Paid social lead ads", "Low-friction forms"), ("Email nurture", "Convert leads")],
    }[kind]
    out = [{"channel": c, "role": r} for c, r in base]
    if re.search(r"young|gen ?z|student|teen|millennial", aud):
        out.append({"channel": "TikTok / Instagram Reels", "role": "Matches the stated young audience"})
    if re.search(r"professional|b2b|executive|manager", aud):
        out.append({"channel": "LinkedIn", "role": "Matches the stated professional audience"})
    return {"channels": out, "count": len(out)}


@tool("build_timeline_checklist", required=("start", "end", "channels"))
def build_timeline_checklist(args, tc):
    s, e = date.fromisoformat(args["start"]), date.fromisoformat(args["end"])
    days = (e - s).days + 1
    d = lambda x: x.isoformat()
    final_start = max(s, e - timedelta(days=min(3, days - 1)))
    timeline = [
        {"phase": "Preparation", "dates": f"{d(s - timedelta(days=14))} to {d(s - timedelta(days=1))}", "focus": "Creative, copy, landing pages, channel setup"},
        {"phase": "Launch", "dates": f"{d(s)} to {d(min(e, s + timedelta(days=6)))}", "focus": "Go live on all channels; daily monitoring"},
    ]
    if days > 7:
        timeline.append({"phase": "Sustain / optimise", "dates": f"{d(s + timedelta(days=7))} to {d(max(s + timedelta(days=7), final_start - timedelta(days=1)))}", "focus": "A/B tests, budget shifts, content refresh"})
    timeline += [{"phase": "Final push", "dates": f"{d(final_start)} to {d(e)}", "focus": "Urgency messaging, reminders"},
                 {"phase": "Review", "dates": f"{d(e + timedelta(days=1))} to {d(e + timedelta(days=7))}", "focus": "Results report and learnings"}]
    promo = args.get("promotion")
    check = [
        {"task": "Confirm KPIs and targets with stakeholders", "due": d(s - timedelta(days=14)), "status": "[ ]"},
        {"task": "Finalise product list, pricing and stock availability", "due": d(s - timedelta(days=10)), "status": "[ ]"},
        {"task": "Approve creative and messaging", "due": d(s - timedelta(days=7)), "status": "[ ]"},
        {"task": f"Configure promotion in store/checkout ({promo})" if promo and promo != "None specified" else "Confirm whether a promotion applies", "due": d(s - timedelta(days=5)), "status": "[ ]"},
        {"task": "Set up channels: " + ", ".join(c["channel"] for c in args["channels"]["channels"]), "due": d(s - timedelta(days=3)), "status": "[ ]"},
        {"task": "Set up tracking (UTM links, conversion events, dashboard)", "due": d(s - timedelta(days=3)), "status": "[ ]"},
        {"task": "Launch campaign and run QA checks", "due": d(s), "status": "[ ]"},
        {"task": "Mid-campaign performance review", "due": d(s + timedelta(days=days // 2)), "status": "[ ]"},
        {"task": "Publish results report", "due": d(e + timedelta(days=7)), "status": "[ ]"},
    ]
    return {"timeline": timeline, "checklist": check}
