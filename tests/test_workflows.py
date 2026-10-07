"""End-to-end checks of business rules for all 10 workflows (deterministic mode, no API key)."""
from conftest import tables


def skus(t, col="sku"):
    return {r[col] for r in t["rows"]}


def test_wf001_restock_threshold_logic(agent):
    r = agent.run("Which products need restocking?")
    assert r.workflow_id == "WF001" and r.status == "success"
    t = tables(r)["Products requiring restock"]
    assert skus(t) == {"TS-001", "JN-010", "SH-101", "BG-201", "WT-301", "CP-401"}
    assert "SH-102" not in skus(t)                       # stock == minimum is NOT low stock
    qty = {x["sku"]: x["suggested_reorder_qty"] for x in t["rows"]}
    assert qty["TS-001"] == 80 - 12 and qty["JN-010"] == 15 * 2 - 5   # target vs 2x-threshold fallback
    bad = tables(r)["Rows skipped (invalid data)"]
    assert skus(bad) == {"HD-501", "LT-701"}              # bad data quarantined, not silently dropped


def test_wf001_user_threshold(agent):
    r = agent.run("Check inventory and list products below a threshold of 20")
    assert r.inputs["threshold_override"] == 20
    assert "BG-202" not in skus(tables(r)["Products requiring restock"])   # 30 >= 20


def test_wf002_boundary_rules(agent):
    r = agent.run("Find products where vendor price differs by more than 10%.")
    t = tables(r)
    assert skus(t["Exceptions"]) == {"SH-101", "TS-002", "BG-201", "WT-301"}
    status = {x["sku"]: x["status"] for x in t["All matched products"]["rows"]}
    assert status["CP-401"] == "OK"                       # exactly 10% is not "exceeds 10%"
    assert status["WT-301"] == "CANNOT VALIDATE"          # vendor price 0 -> no division by zero
    assert skus(t["Vendor SKUs not in our catalog"]) == {"ZZ-999"}
    assert r.inputs["threshold_pct"] == 10


def test_wf002_custom_threshold(agent):
    r = agent.run("Validate vendor prices, flag anything over 5%")
    assert r.inputs["threshold_pct"] == 5
    assert "CP-401" in skus(tables(r)["Exceptions"])


def test_wf003_invalid_rows(agent):
    r = agent.run("Process this vendor spreadsheet and show invalid rows.")
    t = tables(r)["Invalid rows"]
    assert {x["row_number"] for x in t["rows"]} == {4, 5, 10}
    reasons = {x["row_number"]: x["invalid_reason"] for x in t["rows"]}
    assert reasons[4] == "missing sku" and reasons[5] == "missing product_name"
    assert len(r.result["files"]) == 2


def test_wf003_xlsx_input(agent, tmp_path):
    import openpyxl
    p = tmp_path / "v.xlsx"
    wb = openpyxl.Workbook(); ws = wb.active
    ws.append(["Part No", "Item Name", "Cost"]); ws.append(["A1", "Thing", "$3.50"]); ws.append([None, "No sku", 1])
    wb.save(p)
    r = agent.run(f"Process vendor file {p}")
    assert r.status == "success" and r.workflow_id == "WF003"
    assert tables(r)["Invalid rows"]["total"] == 1


def test_wf004_asks_then_never_invents(agent):
    r = agent.run("Generate SEO content for this product.")
    assert r.status == "needs_input" and r.missing[0]["name"] == "product_attributes"
    r = agent.run("Generate SEO content for this product.", {"product_attributes": "name: Trail Runner Pro; color: blue"})
    assert r.status == "success"
    secs = {s["heading"]: s["content"] for s in r.result["sections"]}
    assert set(secs["MISSING information (not invented)"]) >= {"material", "category"}
    text = " ".join(str(secs[k]) for k in ("Product description", "Short description", "SEO title", "Meta description")).lower()
    assert "cotton" not in text and "leather" not in text
    assert len(secs["SEO title"]) <= 60 and len(secs["Meta description"]) <= 155


def test_wf004_name_required(agent):
    r = agent.run("Generate SEO content for this product.", {"product_attributes": "color: red; material: wool"})
    assert r.status == "needs_input"


def test_wf005_found_not_found_email(agent):
    r = agent.run("Where is order ORD-1001?")
    assert r.status == "success" and "FC123456789" in str(r.result)
    r = agent.run("Where is order ORD-9999?")
    assert r.status == "needs_input" and "No order found" in r.message
    r = agent.run("what orders does alice@example.com have?")
    assert r.status == "success" and r.result["tables"][0]["total"] == 2
    r = agent.run("status of order ORD-1003")
    assert next(s for s in r.steps if s.no == 4).status == "skipped"       # condition: no shipment -> skip API call


def test_wf005_invalid_identifier(agent):
    r = agent.run("status please", {"identifier": "banana"}, workflow_id="WF005")
    assert r.status == "needs_input" and "not a valid order ID" in r.message


def test_wf005_retry_then_success_and_skip_on_outage(agent):
    r = agent.run("Where is order ORD-1006?")
    s4 = next(s for s in r.steps if s.no == 4)
    assert s4.status == "ok" and s4.attempts == 2 and "RR777888999" in str(r.result)
    r = agent.run("Track order ORD-1005")
    s4 = next(s for s in r.steps if s.no == 4)
    assert r.status == "success" and s4.status == "skipped" and s4.attempts == 3
    assert "unavailable" in str(r.result)


def test_wf006_confidence_levels(agent):
    r = agent.run("Find likely duplicate products in the catalog.")
    groups = tables(r)["Duplicate groups"]["rows"]
    definite = [g for g in groups if g["confidence"] == "DEFINITE"]
    assert len(definite) == 1 and {"TS-100", "ts 100"} <= set(definite[0]["members"].split(", "))
    all_members = " ".join(g["members"] for g in groups)
    assert "TS-101" not in all_members and "TS-102" not in all_members     # colour / size variants are NOT duplicates
    assert any("SH-300" in g["members"] and "SH-301" in g["members"] for g in groups)


def test_wf007_requires_goal_and_dates(agent):
    r = agent.run("Create a campaign brief for the new collection.")
    assert r.status == "needs_input" and not r.steps
    assert {m["name"] for m in r.missing} == {"campaign_goal", "campaign_dates"}
    r = agent.run("Create a campaign brief for the new collection. Goal: increase online sales by 20%. "
                  "Audience: young professionals. Dates: 2026-11-01 to 2026-11-30.")
    assert r.status == "success"
    secs = {s["heading"]: s["content"] for s in r.result["sections"]}
    assert secs["Dates"].startswith("2026-11-01 to 2026-11-30")
    assert secs["Promotion"] == "None specified"                          # not invented
    assert secs["Objective"]["Type"] == "Drive sales / conversions"


def test_wf007_bad_dates(agent):
    r = agent.run("campaign brief", {"campaign_goal": "grow brand awareness", "campaign_dates": "2026-12-05 to 2026-12-01"}, "WF007")
    assert r.status == "needs_input" and "before the start" in r.message


def test_wf008_intents_and_mapping(agent):
    r = agent.run("Classify these keywords and map them to pages.")
    rows = {x["keyword"]: x for x in tables(r)["Top priority keywords"]["rows"]}
    allrows = {x["keyword"]: x for x in __import__("csv").DictReader(open(r.result["files"][0]))}
    assert allrows["buy cotton t shirt online"]["intent"] == "transactional"
    assert allrows["best trail running shoes"]["intent"] == "commercial"
    assert allrows["how to wash a wool beanie"]["intent"] == "informational"
    assert allrows["acme store login"]["intent"] == "navigational"
    assert allrows["buy cotton t shirt online"]["target_page"] == "/apparel/t-shirts"
    assert "Buy Cotton T Shirt Online" not in allrows and len(allrows) == 23   # de-duplicated
    assert allrows["office chair ergonomic"]["category"] == "Unmapped"


def test_wf009_assignment_and_escalation(agent):
    r = agent.run("Assign this urgent task to the best available developer.")
    assert r.status == "success" and "Lena Fischer" not in r.result["summary"]   # on leave
    assert r.result["summary"].split(": ")[1].split(" (")[0] in {"Arjun Mehta", "Sana Khan", "Priya Nair"}
    r = agent.run("Assign an urgent React bug fix (about 6 hours) to the right person, due 2026-10-12")
    assert "Arjun Mehta" in r.result["summary"]       # Rohit also knows React but has no capacity
    secs = {s["heading"]: s["content"] for s in r.result["sections"]}
    assert secs["Deadline"].startswith("2026-10-12")  # ISO date must not be mis-read as 2026-12-10
    r = agent.run("Assign a Kubernetes migration task that needs about 20 hours")
    assert r.status == "escalated" and "kubernetes" in r.message.lower()


def test_wf010_report_flags(agent):
    r = agent.run("Which workflows are failing most often?")
    flagged = {x["workflow_id"] for x in tables(r)["Flagged workflows"]["rows"]}
    assert {"WF004", "WF003", "WF005"} <= flagged and "WF001" not in flagged
    worst = tables(r)["Failure rate by workflow (worst first)"]["rows"][0]
    assert worst["workflow_id"] == "WF004"


def test_agent_logs_its_own_runs(agent, tmp_path):
    agent.run("Which products need restocking?")
    log = (tmp_path / "logs" / "runtime_logs.csv").read_text()
    assert "WF001" in log and "Load inventory" in log
