"""Regenerate every sample data file under data/ (deterministic). Run: python scripts/generate_sample_data.py"""
import csv
import json
import random
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
D.mkdir(exist_ok=True)


def w(name, header, rows):
    with open(D / name, "w", newline="", encoding="utf-8") as f:
        cw = csv.writer(f)
        cw.writerow(header)
        cw.writerows(rows)


# WF001 - inventory (edge cases: stock == minimum, zero stock, blank reorder_target, bad number, missing number)
w("inventory.csv", ["sku", "product_name", "category", "current_stock", "minimum_stock", "reorder_target", "supplier"], [
    ["TS-001", "Classic Cotton T-Shirt (M)", "Apparel", 12, 25, 80, "Acme Textiles"],
    ["TS-002", "Classic Cotton T-Shirt (L)", "Apparel", 40, 25, 80, "Acme Textiles"],
    ["JN-010", "Slim Fit Jeans 32", "Apparel", 5, 15, "", "Denim Co"],
    ["SH-101", "Trail Runner Shoes 42", "Footwear", 0, 10, 40, "StepUp Ltd"],
    ["SH-102", "Trail Runner Shoes 43", "Footwear", 10, 10, 40, "StepUp Ltd"],
    ["BG-201", "Canvas Backpack", "Accessories", 8, 12, 50, "Carry On"],
    ["BG-202", "Leather Messenger Bag", "Accessories", 30, 10, 30, "Carry On"],
    ["WT-301", "Steel Water Bottle 750ml", "Home", 3, 20, 100, "HydroMax"],
    ["WT-302", "Ceramic Mug", "Home", 55, 20, 100, "HydroMax"],
    ["CP-401", "Wool Beanie", "Apparel", 17, 18, "", "Acme Textiles"],
    ["HD-501", "Zip Hoodie", "Apparel", "N/A", 20, 60, "Acme Textiles"],
    ["SK-601", "Cotton Socks 3-pack", "Apparel", 70, 40, 160, "Acme Textiles"],
    ["LT-701", "LED Desk Lamp", "Home", 6, "", 30, "BrightCo"],
])

# WF002 / WF007 - clean internal product master
products = [
    ("TS-001", "Classic Cotton T-Shirt (M)", "Apparel", 19.99, "Acme", "Blue", "Spring 2026", "no", "Cotton"),
    ("TS-002", "Classic Cotton T-Shirt (L)", "Apparel", 19.99, "Acme", "Blue", "Spring 2026", "no", "Cotton"),
    ("JN-010", "Slim Fit Jeans 32", "Apparel", 59.00, "Denim Co", "Indigo", "Autumn 2026", "yes", "Denim"),
    ("SH-101", "Trail Runner Shoes 42", "Footwear", 89.50, "StepUp", "Black", "Autumn 2026", "yes", "Mesh"),
    ("SH-102", "Trail Runner Shoes 43", "Footwear", 89.50, "StepUp", "Black", "Autumn 2026", "yes", "Mesh"),
    ("BG-201", "Canvas Backpack", "Accessories", 45.00, "Carry On", "Olive", "Autumn 2026", "yes", "Canvas"),
    ("BG-202", "Leather Messenger Bag", "Accessories", 129.00, "Carry On", "Brown", "Classic", "no", "Leather"),
    ("WT-301", "Steel Water Bottle 750ml", "Home", 24.00, "HydroMax", "Silver", "Classic", "no", "Steel"),
    ("WT-302", "Ceramic Mug", "Home", 12.50, "HydroMax", "White", "Classic", "no", "Ceramic"),
    ("CP-401", "Wool Beanie", "Apparel", 22.00, "Acme", "Grey", "Autumn 2026", "yes", "Wool"),
    ("HD-501", "Zip Hoodie", "Apparel", 64.00, "Acme", "Navy", "Autumn 2026", "yes", "Cotton blend"),
    ("SK-601", "Cotton Socks 3-pack", "Apparel", 14.00, "Acme", "White", "Classic", "no", "Cotton"),
    ("LT-701", "LED Desk Lamp", "Home", 35.00, "BrightCo", "Black", "Classic", "no", "Aluminium"),
]
w("products.csv", ["sku", "product_name", "category", "price", "brand", "color", "collection", "is_new", "material"], products)

# WF002 vendor prices: messy SKU formatting, >10%, exactly 10%, <10%, vendor-only, zero price
w("vendor_prices.csv", ["sku", "vendor_price", "vendor_name"], [
    ["ts001", 19.50, "Acme Textiles"],          # +2.5%  OK
    ["TS 002", 17.00, "Acme Textiles"],         # +17.6% EXCEPTION
    ["JN-010", 53.64, "Denim Co"],              # ~+10.0% -> exactly boundary (59/53.64 = 9.99%) OK
    ["SH-101", 70.00, "StepUp Ltd"],            # +27.9% EXCEPTION
    ["SH-102", 91.00, "StepUp Ltd"],            # -1.6% OK
    ["BG-201", 52.00, "Carry On"],              # -13.5% EXCEPTION (internal lower than vendor)
    ["BG-202", 125.00, "Carry On"],             # +3.2% OK
    ["WT-301", 0, "HydroMax"],                  # zero vendor price -> cannot validate
    ["WT-302", 12.00, "HydroMax"],              # +4.2% OK
    ["CP-401", 20.00, "Acme Textiles"],         # +10.0% exactly -> NOT flagged (rule is "exceeds 10%")
    ["ZZ-999", 9.99, "Unknown"],                # vendor-only SKU
])

# WF003 - messy vendor file
w("vendor_file_sample.csv", ["Item No.", "Product Title", "Unit Cost ($)", "Qty on Hand", "Category", "Colour"], [
    ["VX-100", "Bamboo Cutting Board", "$18.50", 40, "Kitchen", "Natural"],
    ["vx-101 ", "  Silicone Spatula Set  ", "12.00", 120, "Kitchen", "Red"],
    ["", "Stainless Colander", "$22.00", 15, "Kitchen", "Silver"],
    ["VX-103", "", "$9.99", 60, "Kitchen", "Black"],
    ["VX-104", "Glass Food Container 1L", "N/A", 75, "Storage", ""],
    ["", "", "", "", "", ""],
    ["VX-106", "Cast Iron Skillet 26cm", "$34.00", 22, "Cookware", "Black"],
    ["VX-107", "Non-stick Frying Pan", "$27.50", 0, "Cookware", "Grey"],
    ["", "Mystery Item Without SKU", "$5.00", 3, "Misc", ""],
    ["VX-109", "Olive Wood Spoon", "$6.25", 200, "Kitchen", "Brown"],
])

# WF006 - catalog with duplicates, near-duplicates and legitimate variants
w("catalog.csv", ["sku", "product_name", "category", "brand", "color", "size", "price"], [
    ["TS-100", "Men's Classic Cotton T-Shirt - Blue (L)", "Apparel", "Acme", "Blue", "L", 19.99],
    ["ts 100", "Mens Classic Cotton Tee Blue L", "Apparel", "Acme", "Blue", "L", 19.99],          # exact SKU after normalisation
    ["TS-205", "Classic Cotton T Shirt Mens Blue L", "Apparel", "Acme", "Blue", "L", 20.49],       # same product, different SKU
    ["TS-101", "Men's Classic Cotton T-Shirt - Red (L)", "Apparel", "Acme", "Red", "L", 19.99],    # colour variant, NOT a duplicate
    ["TS-102", "Men's Classic Cotton T-Shirt - Blue (S)", "Apparel", "Acme", "Blue", "S", 19.99],  # size variant, NOT a duplicate
    ["SH-300", "Trail Runner Shoes 42 Black", "Footwear", "StepUp", "Black", "42", 89.50],
    ["SH-301", "Trail-Runner Shoes, Black, 42", "Footwear", "StepUp", "Black", "42", 89.50],       # near duplicate
    ["BG-400", "Canvas Backpack Olive", "Accessories", "Carry On", "Olive", "", 45.00],
    ["BG-401", "Leather Messenger Bag", "Accessories", "Carry On", "Brown", "", 129.00],
    ["WT-500", "Steel Water Bottle 750ml", "Home", "HydroMax", "Silver", "750ml", 24.00],
    ["WT-501", "Steel Water Bottle 750 ml Silver", "Home", "HydroMax", "Silver", "750ml", 24.00],  # near duplicate
    ["WT-502", "Ceramic Mug", "Home", "HydroMax", "White", "", 12.50],
    ["LT-600", "LED Desk Lamp", "Home", "BrightCo", "Black", "", 35.00],
    ["CP-700", "Wool Beanie Grey", "Apparel", "Acme", "Grey", "", 22.00],
])

# WF008 - keyword list (with case/whitespace duplicates) + category/page map
w("keywords.csv", ["keyword", "search_volume", "difficulty"], [
    ["buy cotton t shirt online", 5400, 45], ["Buy Cotton T Shirt Online", 5400, 45], ["best trail running shoes", 12000, 70],
    ["how to wash a wool beanie", 2300, 20], ["leather messenger bag price", 3100, 38], ["trail runner shoes review", 4100, 55],
    ["acme store login", 900, 5], ["canvas backpack for school", 6600, 42], ["steel water bottle discount code", 1800, 33],
    ["what is a ceramic mug made of", 700, 12], ["slim fit jeans near me", 2900, 40], ["  best led desk lamp ", 3600, 48],
    ["acme official website", 1500, 8], ["wool beanie vs knit beanie", 1200, 25], ["zip hoodie sale", 7200, 52],
    ["how to choose running shoes", 9800, 60], ["cotton socks 3 pack", 2100, 30], ["buy leather messenger bag", 2600, 44],
    ["office chair ergonomic", 8800, 65], ["hiking boots waterproof", 6100, 58], ["water bottle with straw", 4900, 36],
    ["trail runner shoes", 8500, 62], ["desk lamp for study", 2400, 29], ["order canvas backpack", 800, 31],
])
w("seo_categories.csv", ["category", "page_url", "terms"], [
    ["T-Shirts", "/apparel/t-shirts", "t shirt;tee;cotton;shirt"],
    ["Jeans", "/apparel/jeans", "jeans;denim;slim fit"],
    ["Hoodies & Beanies", "/apparel/hoodies-beanies", "hoodie;beanie;wool;zip"],
    ["Socks", "/apparel/socks", "socks;cotton socks"],
    ["Running Shoes", "/footwear/running-shoes", "running;trail;runner;shoes;shoe"],
    ["Bags", "/accessories/bags", "backpack;bag;messenger;leather;canvas"],
    ["Water Bottles & Mugs", "/home/drinkware", "water bottle;bottle;mug;ceramic;steel"],
    ["Lighting", "/home/lighting", "lamp;led;desk lamp;lighting"],
    ["Brand / Home", "/", "acme;store;website"],
])

# WF009 - employees
w("employees.csv", ["employee_id", "name", "role", "skills", "current_workload_hours", "weekly_capacity_hours", "status"], [
    ["E01", "Priya Nair", "Senior Developer", "python;django;sql;aws", 34, 40, "active"],
    ["E02", "Arjun Mehta", "Developer", "react;javascript;css;typescript", 18, 40, "active"],
    ["E03", "Sana Khan", "Developer", "python;fastapi;sql;docker", 24, 40, "active"],
    ["E04", "Rohit Das", "Frontend Developer", "react;typescript;css;figma", 38, 40, "active"],
    ["E05", "Meera Iyer", "UX Designer", "figma;research;css", 12, 40, "active"],
    ["E06", "Karan Singh", "QA Engineer", "selenium;python;testing", 20, 40, "active"],
    ["E07", "Lena Fischer", "Developer", "java;spring;sql;aws", 10, 40, "on_leave"],
    ["E08", "Vikram Rao", "Data Analyst", "sql;python;tableau", 22, 40, "active"],
])

# WF005 - orders + shipments (carrier API simulation flags live in shipments.json)
orders = [
    {"order_id": "ORD-1001", "customer_email": "alice@example.com", "customer_name": "Alice Brown", "order_date": "2026-10-01", "status": "Shipped",
     "items": [{"sku": "TS-001", "name": "Classic Cotton T-Shirt (M)", "qty": 2}], "shipment_id": "SHP-9001"},
    {"order_id": "ORD-1002", "customer_email": "alice@example.com", "customer_name": "Alice Brown", "order_date": "2026-09-20", "status": "Delivered",
     "items": [{"sku": "WT-302", "name": "Ceramic Mug", "qty": 1}], "shipment_id": "SHP-9002"},
    {"order_id": "ORD-1003", "customer_email": "bob@example.com", "customer_name": "Bob Lee", "order_date": "2026-10-05", "status": "Processing",
     "items": [{"sku": "SH-101", "name": "Trail Runner Shoes 42", "qty": 1}], "shipment_id": None},
    {"order_id": "ORD-1004", "customer_email": "carol@example.com", "customer_name": "Carol Diaz", "order_date": "2026-09-28", "status": "Cancelled",
     "items": [{"sku": "BG-202", "name": "Leather Messenger Bag", "qty": 1}], "shipment_id": None},
    {"order_id": "ORD-1005", "customer_email": "dan@example.com", "customer_name": "Dan Wu", "order_date": "2026-10-03", "status": "Shipped",
     "items": [{"sku": "LT-701", "name": "LED Desk Lamp", "qty": 1}], "shipment_id": "SHP-9005"},
    {"order_id": "ORD-1006", "customer_email": "erin@example.com", "customer_name": "Erin Park", "order_date": "2026-10-04", "status": "Shipped",
     "items": [{"sku": "BG-201", "name": "Canvas Backpack", "qty": 1}], "shipment_id": "SHP-9006"},
]
shipments = [
    {"shipment_id": "SHP-9001", "carrier": "FastCarrier", "tracking_number": "FC123456789", "status": "In transit", "eta": "2026-10-09", "last_event": "Departed Mumbai hub 2026-10-06"},
    {"shipment_id": "SHP-9002", "carrier": "FastCarrier", "tracking_number": "FC987654321", "status": "Delivered", "eta": "2026-09-24", "last_event": "Delivered to recipient 2026-09-24"},
    {"shipment_id": "SHP-9005", "carrier": "SkyPost", "tracking_number": "SP555000111", "status": "In transit", "eta": "2026-10-10", "last_event": "Arrived at sorting centre", "_simulate": "outage"},
    {"shipment_id": "SHP-9006", "carrier": "RoadRunner", "tracking_number": "RR777888999", "status": "Out for delivery", "eta": "2026-10-07", "last_event": "Out for delivery in Hyderabad", "_simulate": "flaky"},
]
(D / "orders.json").write_text(json.dumps(orders, indent=2), encoding="utf-8")
(D / "shipments.json").write_text(json.dumps(shipments, indent=2), encoding="utf-8")

# WF010 - seeded execution history (step-level). Same schema the live agent writes to logs/runtime_logs.csv
random.seed(7)
WF_STEPS = {
    "WF001": ["Load inventory", "Compare stock with threshold", "Identify low-stock products", "Calculate reorder quantity", "Generate restock list"],
    "WF002": ["Load product prices", "Load vendor price list", "Match products by SKU", "Compare internal and vendor prices", "Calculate percentage difference", "Flag exceptions", "Generate validation report"],
    "WF003": ["Read vendor file", "Detect columns", "Normalize column names", "Validate required fields", "Identify invalid rows", "Produce cleaned dataset", "Generate validation summary"],
    "WF004": ["Validate required attributes", "Create product description", "Generate short description", "Generate SEO title", "Generate meta description", "Validate generated text", "Compile product content"],
    "WF005": ["Validate identifier", "Search order data", "Retrieve order status", "Retrieve shipment information", "Summarize current status"],
    "WF006": ["Load products", "Normalize names/SKUs", "Compare identifiers", "Compare product attributes", "Group likely duplicates", "Assign confidence", "Generate duplicate report"],
    "WF007": ["Validate inputs", "Identify campaign objective", "Load product data", "Summarize products", "Create messaging", "Create channel recommendations", "Create campaign checklist", "Generate campaign brief"],
    "WF008": ["Read keywords", "Remove duplicates", "Classify search intent", "Map keywords to categories", "Identify high-priority keywords", "Export results", "Generate keyword report"],
    "WF009": ["Understand task requirements", "Compare employee skills", "Check current workload", "Rank candidates", "Select employee", "Generate assignment summary"],
    "WF010": ["Load execution logs", "Calculate success/failure rate", "Calculate average execution time", "Identify frequent errors", "Identify slow steps", "Generate recommendations", "Generate performance report"],
}
# base seconds per step, per-workflow failure rate, failing step + error, slow step
PROFILE = {
    "WF001": (0.12, 0.04, 0, "FileNotFoundError: inventory file not found", None),
    "WF002": (0.2, 0.08, 1, "ValidationError: missing required column 'vendor_price'", None),
    "WF003": (0.3, 0.14, 3, "ValidationError: missing required column 'sku'", None),
    "WF004": (2.4, 0.21, 1, "LLMError: rate limit exceeded (429)", 1),
    "WF005": (0.9, 0.18, 3, "TimeoutError: carrier API timed out after 30s", 3),
    "WF006": (0.8, 0.05, 3, "MemoryError: pairwise comparison too large", 3),
    "WF007": (2.9, 0.12, 4, "LLMError: rate limit exceeded (429)", 4),
    "WF008": (3.6, 0.09, 2, "LLMError: invalid JSON in classifier response", 2),
    "WF009": (0.25, 0.03, 4, "EscalationError: no suitable employee", None),
    "WF010": (0.4, 0.02, 0, "FileNotFoundError: execution log not found", None),
}
rows, n = [], 0
for wid, steps in WF_STEPS.items():
    base, fail_p, fail_idx, err, slow_idx = PROFILE[wid]
    for _ in range(random.randint(24, 40)):
        n += 1
        run_id = f"seed-{n:04d}"
        failed = random.random() < fail_p
        day = random.randint(1, 28)
        ts = f"2026-09-{day:02d}T{random.randint(8, 18):02d}:{random.randint(0, 59):02d}:00"
        for i, s in enumerate(steps):
            dur = base * random.uniform(0.6, 1.5) * (6 if slow_idx == i else 1) * (0.3 if i == 0 else 1)
            status, e = "ok", ""
            if failed and i == fail_idx:
                status, e, dur = "failed", err, dur * 1.2
            rows.append([run_id, ts, wid, i + 1, s, "", status, round(dur, 3), e])
            if failed and i == fail_idx:
                break
w("execution_logs.csv", ["run_id", "timestamp", "workflow_id", "step_no", "step_name", "tool", "status", "duration_sec", "error"], rows)
print("sample data written to", D)
