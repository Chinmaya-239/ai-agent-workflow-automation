"""WF005 - customer order status with a simulated order DB and a (deliberately flaky) shipment API."""
from __future__ import annotations

import json
import re

from ..errors import NeedInput, ToolError
from ..registry import tool

_CALLS: dict[str, int] = {}


def reset_simulation():
    _CALLS.clear()


def _load(tc, path):
    fp = tc.config.resolve_path(path)
    if not fp.exists():
        raise ToolError(f"Data source not found: {path}")
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ToolError(f"{fp.name} is not valid JSON: {e}")


@tool("validate_identifier", required=("value",))
def validate_identifier(args, tc):
    v = (args["value"] or "").strip()
    m = re.fullmatch(r"(?i)ORD[-\s]?(\d{3,})", v)
    if m:
        return {"type": "order_id", "value": f"ORD-{m.group(1)}"}
    if re.fullmatch(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", v):
        return {"type": "email", "value": v.lower()}
    raise NeedInput([{"name": "identifier",
                      "ask": f"'{v}' is not a valid order ID (like ORD-1001) or email. Please provide one of those."}])


@tool("find_orders", required=("identifier", "source"))
def find_orders(args, tc):
    """Order database lookup by order id or customer email."""
    ident = args["identifier"]
    db = _load(tc, args["source"])
    key = "order_id" if ident["type"] == "order_id" else "customer_email"
    found = [o for o in db if str(o.get(key, "")).lower() == ident["value"].lower()]
    if not found:
        raise NeedInput([{"name": "identifier",
                          "ask": f"No order found for {ident['type'].replace('_', ' ')} '{ident['value']}'. "
                                 "Please provide another order ID or the email used when ordering."}])
    tc.decide(f"Found {len(found)} order(s) for {ident['type']} {ident['value']}")
    return {"orders": found, "count": len(found), "with_shipment_count": sum(1 for o in found if o.get("shipment_id"))}


@tool("get_order_status", required=("orders",))
def get_order_status(args, tc):
    return [{"order_id": o["order_id"], "status": o["status"], "order_date": o.get("order_date"),
             "customer": o.get("customer_name"), "items": o.get("items", []), "shipment_id": o.get("shipment_id")}
            for o in args["orders"]]


@tool("get_shipment_info", required=("orders", "source"))
def get_shipment_info(args, tc):
    """Simulated carrier API. 'outage' entries always fail; 'flaky' entries fail once then succeed
    (so the engine's retry policy is observable)."""
    table = {s["shipment_id"]: s for s in _load(tc, args["source"])}
    out = {}
    for o in args["orders"]:
        sid = o.get("shipment_id")
        if not sid:
            continue
        s = table.get(sid)
        if s is None:
            raise ToolError(f"Shipment {sid} not found in carrier system")
        sim = s.get("_simulate")
        _CALLS[sid] = _CALLS.get(sid, 0) + 1
        if sim == "outage":
            raise ToolError(f"Carrier API 503 Service Unavailable ({s['carrier']})")
        if sim == "flaky" and _CALLS[sid] == 1:
            raise ToolError(f"Carrier API timeout ({s['carrier']})")
        out[o["order_id"]] = {k: v for k, v in s.items() if not k.startswith("_")}
    return out


@tool("summarize_orders", required=("statuses",))
def summarize_orders(args, tc):
    statuses, shipments = args["statuses"], args.get("shipments")
    lines, tables = [], []
    for st in statuses:
        oid = st["order_id"]
        item_txt = ", ".join(f"{i['qty']} x {i['name']}" for i in st["items"])
        line = f"**{oid}** (placed {st['order_date']}): status **{st['status']}** - {item_txt}."
        if not st.get("shipment_id"):
            line += " No shipment yet" + (" (order cancelled)." if st["status"].lower() == "cancelled" else " - it has not been dispatched.")
        elif shipments is None:
            line += " Shipment details are temporarily unavailable from the carrier; please try again shortly."
        elif oid in shipments:
            s = shipments[oid]
            line += (f" Shipment {s['shipment_id']} via {s['carrier']}: **{s['status']}**, tracking {s['tracking_number']}, "
                     f"ETA {s.get('eta') or 'n/a'}; last event: {s.get('last_event', 'n/a')}.")
        lines.append(line)
        tables.append({"order_id": oid, "status": st["status"],
                       "tracking": (shipments or {}).get(oid, {}).get("tracking_number", "-"),
                       "shipment_status": (shipments or {}).get(oid, {}).get("status", "-")})
    notes = []
    if shipments is None and any(s.get("shipment_id") for s in statuses):
        notes.append("Shipment lookup failed after retries; status shown from order database only.")
    return {"title": "Order status", "summary": f"{len(statuses)} order(s) found.", "metrics": {},
            "sections": [{"heading": "Details", "content": lines}],
            "tables": [{"name": "Overview", "rows": tables, "total": len(tables), "columns": None, "limit": 20}],
            "files": [], "notes": notes}
