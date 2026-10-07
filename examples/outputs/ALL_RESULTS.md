# Demo results (all scenarios)
_LLM mode: none_

## WF001_restock - Inventory restock (test question)

```text
==============================================================================
USER REQUEST: Which products need restocking?
==============================================================================

Selected Workflow:
  WF001 - Inventory Restock Check
  (router: keyword-tfidf, confidence 0.89) Best keyword/TF-IDF match with 'Inventory Restock Check' (score 0.40, runner-up 0.09)

Inputs resolved:
  - inventory_path = data/inventory.csv  [default]

Steps Executed:
  1. [OK]   Load inventory  <load_table, 0.00s> - row_count=11
        note: 2 row(s) quarantined for bad numeric data (not processed)
  2. [OK]   Compare current stock with minimum threshold  <compute_columns, 0.00s> - count=11
  3. [OK]   Identify low-stock products  <filter_rows, 0.00s> - count=6, total=11
  4. [OK]   Calculate reorder quantity  <compute_columns, 0.00s> - count=6
  5. [OK]   Generate restock list  <make_report, 0.00s> - report built: Restock list

Conditions / Decisions:
  - [Identify low-stock products] Rule `current_stock < minimum_stock (threshold)` matched 6 of 11 rows

Result:
## Restock list

6 of 11 products are below their minimum stock and need restocking.

- **Products checked**: 11
- **Rows skipped (bad data)**: 2

### Products requiring restock (6)
| sku | product_name | current_stock | threshold | suggested_reorder_qty |
|---|---|---|---|---|
| WT-301 | Steel Water Bottle 750ml | 3 | 20 | 97 |
| TS-001 | Classic Cotton T-Shirt (M) | 12 | 25 | 68 |
| JN-010 | Slim Fit Jeans 32 | 5 | 15 | 25 |
| SH-101 | Trail Runner Shoes 42 | 0 | 10 | 40 |
| BG-201 | Canvas Backpack | 8 | 12 | 42 |
| CP-401 | Wool Beanie | 17 | 18 | 19 |

### Rows skipped (invalid data) (2)
| row_number | sku | invalid_reason |
|---|---|---|
| 12 | HD-501 | non-numeric value 'N/A' in column 'current_… |
| 14 | LT-701 | missing value in column 'minimum_stock' |

**Files written:**
- outputs/wf001_products_requiring_restock.csv
```

## WF001_threshold - Restock with a user-supplied threshold

```text
==============================================================================
USER REQUEST: Check inventory and list products below a threshold of 20
==============================================================================

Selected Workflow:
  WF001 - Inventory Restock Check
  (router: keyword-tfidf, confidence 0.92) Best keyword/TF-IDF match with 'Inventory Restock Check' (score 0.40, runner-up 0.06)

Inputs resolved:
  - inventory_path = data/inventory.csv  [default]
  - threshold_override = 20  [extracted]

Steps Executed:
  1. [OK]   Load inventory  <load_table, 0.00s> - row_count=11
        note: 2 row(s) quarantined for bad numeric data (not processed)
  2. [OK]   Compare current stock with minimum threshold  <compute_columns, 0.00s> - count=11
  3. [OK]   Identify low-stock products  <filter_rows, 0.00s> - count=7, total=11
  4. [OK]   Calculate reorder quantity  <compute_columns, 0.00s> - count=7
  5. [OK]   Generate restock list  <make_report, 0.00s> - report built: Restock list

Conditions / Decisions:
  - [Identify low-stock products] Rule `current_stock < minimum_stock (threshold)` matched 7 of 11 rows

Result:
## Restock list

7 of 11 products are below their minimum stock and need restocking.

- **Products checked**: 11
- **Rows skipped (bad data)**: 2

### Products requiring restock (7)
| sku | product_name | current_stock | threshold | suggested_reorder_qty |
|---|---|---|---|---|
| SH-101 | Trail Runner Shoes 42 | 0 | 20 | 40 |
| WT-301 | Steel Water Bottle 750ml | 3 | 20 | 97 |
| JN-010 | Slim Fit Jeans 32 | 5 | 20 | 35 |
| BG-201 | Canvas Backpack | 8 | 20 | 42 |
| SH-102 | Trail Runner Shoes 43 | 10 | 20 | 30 |
| TS-001 | Classic Cotton T-Shirt (M) | 12 | 20 | 68 |
| CP-401 | Wool Beanie | 17 | 20 | 23 |

### Rows skipped (invalid data) (2)
| row_number | sku | invalid_reason |
|---|---|---|
| 12 | HD-501 | non-numeric value 'N/A' in column 'current_… |
| 14 | LT-701 | missing value in column 'minimum_stock' |

**Files written:**
- outputs/wf001_products_requiring_restock.csv
```

## WF002_prices - Price validation (test question)

```text
==============================================================================
USER REQUEST: Find products where vendor price differs by more than 10%.
==============================================================================

Selected Workflow:
  WF002 - Product Price Validation
  (router: keyword-tfidf, confidence 0.87) Best keyword/TF-IDF match with 'Product Price Validation' (score 0.49, runner-up 0.13)

Inputs resolved:
  - products_path = data/products.csv  [default]
  - vendor_prices_path = data/vendor_prices.csv  [default]
  - threshold_pct = 10  [extracted]

Steps Executed:
  1. [OK]   Load product prices  <load_table, 0.00s> - row_count=13
  2. [OK]   Load vendor price list  <load_table, 0.00s> - row_count=11
  3. [OK]   Match products by SKU  <join_tables, 0.00s> - count=10
  4. [OK]   Compare internal and vendor prices  <compute_columns, 0.00s> - count=10
  5. [OK]   Calculate percentage difference  <compute_columns, 0.00s> - count=10
  6. [OK]   Flag exceptions  <filter_rows, 0.00s> - count=4, total=10
  7. [OK]   Generate validation report  <make_report, 0.00s> - report built: Product price validation

Conditions / Decisions:
  - [Match products by SKU] Matched 10 rows on 'sku'; 3 left-only, 1 right-only
  - [Flag exceptions] Rule `|price difference %| > threshold_pct (or cannot be computed)` matched 4 of 10 rows

Result:
## Product price validation

10 products matched by SKU; 4 exception(s) where the price difference exceeds 10% (or cannot be validated).

- **Internal products**: 13
- **Matched**: 10
- **No vendor price**: 3
- **Vendor-only SKUs**: 1

### Exceptions (4)
| sku | product_name | price | vendor_price | price_diff | pct_diff | status |
|---|---|---|---|---|---|---|
| WT-301 | Steel Water Bottle 750ml | 24 | 0 | 24 |  | CANNOT VALIDATE |
| SH-101 | Trail Runner Shoes 42 | 89.5 | 70 | 19.5 | 27.86 | EXCEPTION |
| TS-002 | Classic Cotton T-Shirt (L) | 19.99 | 17 | 2.99 | 17.59 | EXCEPTION |
| BG-201 | Canvas Backpack | 45 | 52 | -7 | -13.46 | EXCEPTION |

### All matched products (10)
| sku | price | vendor_price | pct_diff | status |
|---|---|---|---|---|
| TS-001 | 19.99 | 19.5 | 2.51 | OK |
| TS-002 | 19.99 | 17 | 17.59 | EXCEPTION |
| JN-010 | 59 | 53.64 | 9.99 | OK |
| SH-101 | 89.5 | 70 | 27.86 | EXCEPTION |
| SH-102 | 89.5 | 91 | -1.65 | OK |
| BG-201 | 45 | 52 | -13.46 | EXCEPTION |
| BG-202 | 129 | 125 | 3.2 | OK |
| WT-301 | 24 | 0 |  | CANNOT VALIDATE |
| WT-302 | 12.5 | 12 | 4.17 | OK |
| CP-401 | 22 | 20 | 10 | OK |

### Internal SKUs missing from vendor list (3)
| sku | product_name | price |
|---|---|---|
| HD-501 | Zip Hoodie | 64 |
| SK-601 | Cotton Socks 3-pack | 14 |
| LT-701 | LED Desk Lamp | 35 |

### Vendor SKUs not in our catalog (1)
| sku | vendor_price |
|---|---|
| ZZ-999 | 9.99 |

**Files written:**
- outputs/wf002_exceptions.csv
- outputs/wf002_all_matched_products.csv
```

## WF002_strict - Price validation with a stricter 5% rule

```text
==============================================================================
USER REQUEST: Validate vendor prices, flag anything over 5%
==============================================================================

Selected Workflow:
  WF002 - Product Price Validation
  (router: keyword-tfidf, confidence 0.84) Best keyword/TF-IDF match with 'Product Price Validation' (score 0.47, runner-up 0.15)

Inputs resolved:
  - products_path = data/products.csv  [default]
  - vendor_prices_path = data/vendor_prices.csv  [default]
  - threshold_pct = 5  [extracted]

Steps Executed:
  1. [OK]   Load product prices  <load_table, 0.00s> - row_count=13
  2. [OK]   Load vendor price list  <load_table, 0.00s> - row_count=11
  3. [OK]   Match products by SKU  <join_tables, 0.00s> - count=10
  4. [OK]   Compare internal and vendor prices  <compute_columns, 0.00s> - count=10
  5. [OK]   Calculate percentage difference  <compute_columns, 0.00s> - count=10
  6. [OK]   Flag exceptions  <filter_rows, 0.00s> - count=6, total=10
  7. [OK]   Generate validation report  <make_report, 0.00s> - report built: Product price validation

Conditions / Decisions:
  - [Match products by SKU] Matched 10 rows on 'sku'; 3 left-only, 1 right-only
  - [Flag exceptions] Rule `|price difference %| > threshold_pct (or cannot be computed)` matched 6 of 10 rows

Result:
## Product price validation

10 products matched by SKU; 6 exception(s) where the price difference exceeds 5% (or cannot be validated).

- **Internal products**: 13
- **Matched**: 10
- **No vendor price**: 3
- **Vendor-only SKUs**: 1

### Exceptions (6)
| sku | product_name | price | vendor_price | price_diff | pct_diff | status |
|---|---|---|---|---|---|---|
| WT-301 | Steel Water Bottle 750ml | 24 | 0 | 24 |  | CANNOT VALIDATE |
| SH-101 | Trail Runner Shoes 42 | 89.5 | 70 | 19.5 | 27.86 | EXCEPTION |
| TS-002 | Classic Cotton T-Shirt (L) | 19.99 | 17 | 2.99 | 17.59 | EXCEPTION |
| BG-201 | Canvas Backpack | 45 | 52 | -7 | -13.46 | EXCEPTION |
| CP-401 | Wool Beanie | 22 | 20 | 2 | 10 | EXCEPTION |
| JN-010 | Slim Fit Jeans 32 | 59 | 53.64 | 5.36 | 9.99 | EXCEPTION |

### All matched products (10)
| sku | price | vendor_price | pct_diff | status |
|---|---|---|---|---|
| TS-001 | 19.99 | 19.5 | 2.51 | OK |
| TS-002 | 19.99 | 17 | 17.59 | EXCEPTION |
| JN-010 | 59 | 53.64 | 9.99 | EXCEPTION |
| SH-101 | 89.5 | 70 | 27.86 | EXCEPTION |
| SH-102 | 89.5 | 91 | -1.65 | OK |
| BG-201 | 45 | 52 | -13.46 | EXCEPTION |
| BG-202 | 129 | 125 | 3.2 | OK |
| WT-301 | 24 | 0 |  | CANNOT VALIDATE |
| WT-302 | 12.5 | 12 | 4.17 | OK |
| CP-401 | 22 | 20 | 10 | EXCEPTION |

### Internal SKUs missing from vendor list (3)
| sku | product_name | price |
|---|---|---|
| HD-501 | Zip Hoodie | 64 |
| SK-601 | Cotton Socks 3-pack | 14 |
| LT-701 | LED Desk Lamp | 35 |

### Vendor SKUs not in our catalog (1)
| sku | vendor_price |
|---|---|
| ZZ-999 | 9.99 |

**Files written:**
- outputs/wf002_exceptions.csv
- outputs/wf002_all_matched_products.csv
```

## WF003_vendor - Vendor file processing (test question)

```text
==============================================================================
USER REQUEST: Process this vendor spreadsheet and show invalid rows.
==============================================================================

Selected Workflow:
  WF003 - Vendor File Processing
  (router: keyword-tfidf, confidence 0.91) Best keyword/TF-IDF match with 'Vendor File Processing' (score 0.55, runner-up 0.10)

Inputs resolved:
  - vendor_file = data/vendor_file_sample.csv  [default]

Steps Executed:
  1. [OK]   Read file  <load_table, 0.00s> - row_count=9
  2. [OK]   Detect columns  <detect_columns, 0.00s> - keys: mapping, methods, unmapped
        note: 'Item No.' -> sku (exact synonym)
        note: 'Product Title' -> product_name (exact synonym)
        note: 'Unit Cost ($)' -> price (exact synonym)
        note: 'Qty on Hand' -> quantity (exact synonym)
        note: 'Category' -> category (exact synonym)
        note: 'Colour' -> color (exact synonym)
  3. [OK]   Normalize column names  <normalize_vendor_rows, 0.00s> - count=9
        note: 1 unparseable numeric value(s) set to blank (flagged in *_warning columns)
  4. [OK]   Validate required fields  <validate_rows, 0.00s> - count=9
  5. [OK]   Identify invalid rows  <partition_rows, 0.00s> - valid_count=6, total=9
  6. [OK]   Produce cleaned dataset  <export_tables, 0.00s> - count=2
  7. [OK]   Generate validation summary  <make_report, 0.00s> - report built: Vendor file processing

Conditions / Decisions:
  - [Validate required fields] Required fields ['sku', 'product_name']: 3 of 9 rows invalid

Result:
## Vendor file processing

6 of 9 rows are valid; 3 invalid row(s) were separated.

- **Source file**: data/vendor_file_sample.csv
- **Detected columns**: {'sku': 'Item No.', 'product_name': 'Product Title', 'price': 'Unit Cost ($)', 'quantity': 'Qty on Hand', 'category': 'Category', 'color': 'Colour'}

### Invalid rows (3)
| row_number | invalid_reason | sku | product_name | price |
|---|---|---|---|---|
| 4 | missing sku |  | Stainless Colander | 22 |
| 5 | missing product_name | VX-103 |  | 9.99 |
| 10 | missing sku |  | Mystery Item Without SKU | 5 |

### Cleaned dataset (preview) (6)
| sku | product_name | price | quantity | category | color |
|---|---|---|---|---|---|
| VX-100 | Bamboo Cutting Board | 18.5 | 40 | Kitchen | Natural |
| VX-101 | Silicone Spatula Set | 12 | 120 | Kitchen | Red |
| VX-104 | Glass Food Container 1L |  | 75 | Storage |  |
| VX-106 | Cast Iron Skillet 26cm | 34 | 22 | Cookware | Black |
| VX-107 | Non-stick Frying Pan | 27.5 | 0 | Cookware | Grey |
| VX-109 | Olive Wood Spoon | 6.25 | 200 | Kitchen | Brown |

**Files written:**
- outputs/wf003_cleaned.csv
- outputs/wf003_invalid_rows.csv
```

## WF004_missing_prompt - Content generation - nothing provided, agent asks

```text
--- TURN 1: agent stops and asks ---
Before I can run this workflow I need:
  - Please describe the product (name, category, material, color, target audience).

==============================================================================
USER REQUEST: Generate SEO content for this product.
==============================================================================

Selected Workflow:
  WF004 - Product Description Generator
  (router: keyword-tfidf, confidence 0.83) Best keyword/TF-IDF match with 'Product Description Generator' (score 0.49, runner-up 0.16)

Inputs resolved:

STATUS: More information needed before this workflow can continue.
Before I can run this workflow I need:
  - Please describe the product (name, category, material, color, target audience).
```

## WF004_content - Content generation with partly missing attributes (agent asks, user answers; material is NOT invented)

```text
--- TURN 1: agent stops and asks ---
Before I can run this workflow I need:
  - Please describe the product (name, category, material, color, target audience).

--- user answers (product_attributes): name: Trail Runner Pro; category: running shoes; color: blue; audience: trail runners

--- TURN 2: workflow re-run with the answers ---
==============================================================================
USER REQUEST: Generate SEO content for this product.
==============================================================================

Selected Workflow:
  WF004 - Product Description Generator
  (router: explicit, confidence 1.00) Workflow chosen explicitly by the caller

Inputs resolved:
  - product_attributes = {'product_name': 'Trail Runner Pro', 'category': 'running shoes', 'co…  [user-provided]

Steps Executed:
  1. [OK]   Validate required attributes  <validate_attributes, 0.00s> - keys: provided, missing
  2. [OK]   Create product description  <generate_text, 0.00s> - The Trail Runner Pro (running shoes) in blue. It is desig...
        note: description: template fallback (no LLM configured)
  3. [OK]   Generate short description  <generate_text, 0.00s> - Trail Runner Pro - running shoes in blue for trail runners.
        note: short_description: template fallback (no LLM configured)
  4. [OK]   Generate SEO title  <generate_text, 0.00s> - Trail Runner Pro - running shoes (blue)
        note: seo_title: template fallback (no LLM configured)
  5. [OK]   Generate meta description  <generate_text, 0.00s> - Shop the Trail Runner Pro in blue for trail runners. Orde...
        note: meta_description: template fallback (no LLM configured)
  6. [OK]   Validate generated text  <validate_text, 0.00s> - keys: texts, warnings
  7. [OK]   Compile product content  <make_report, 0.00s> - report built: Product content

Conditions / Decisions:
  - [Validate required attributes] Missing attributes ['material', 'features'] will NOT be invented; they are marked as missing in the output
  - [Validate generated text] All generated text passed length and invented-attribute checks

Result:
## Product content

Content generated using only the attributes you provided.

### Product description
The Trail Runner Pro (running shoes) in blue. It is designed for trail runners.

### Short description
Trail Runner Pro - running shoes in blue for trail runners.

### SEO title
Trail Runner Pro - running shoes (blue)

### Meta description
Shop the Trail Runner Pro in blue for trail runners. Order online today.

### Attributes used
- **product_name**: Trail Runner Pro
- **category**: running shoes
- **color**: blue
- **target_audience**: trail runners

### MISSING information (not invented)
- material
- features

### Validation warnings
_(none)_
```

## WF005_order - Order status (test question)

```text
==============================================================================
USER REQUEST: Where is order ORD-1001?
==============================================================================

Selected Workflow:
  WF005 - Customer Order Status
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'Customer Order Status' (score 0.51, runner-up 0.00)

Inputs resolved:
  - identifier = ORD-1001  [extracted]
  - orders_path = data/orders.json  [default]
  - shipments_path = data/shipments.json  [default]

Steps Executed:
  1. [OK]   Validate identifier  <validate_identifier, 0.00s> - keys: type, value
  2. [OK]   Search order data  <find_orders, 0.00s> - count=1
  3. [OK]   Retrieve order status  <get_order_status, 0.00s> - 1 items
  4. [OK]   Retrieve shipment information  <get_shipment_info, 0.00s> - keys: ORD-1001
  5. [OK]   Summarize current status  <summarize_orders, 0.00s> - report built: Order status

Conditions / Decisions:
  - [Search order data] Found 1 order(s) for order_id ORD-1001

Result:
## Order status

1 order(s) found.

### Details
- **ORD-1001** (placed 2026-10-01): status **Shipped** - 2 x Classic Cotton T-Shirt (M). Shipment SHP-9001 via FastCarrier: **In transit**, tracking FC123456789, ETA 2026-10-09; last event: Departed Mumbai hub 2026-10-06.

### Overview (1)
| order_id | status | tracking | shipment_status |
|---|---|---|---|
| ORD-1001 | Shipped | FC123456789 | In transit |
```

## WF005_not_found - Unknown order -> agent asks for another identifier -> user supplies one

```text
--- TURN 1: agent stops and asks ---
No order found for order id 'ORD-9999'. Please provide another order ID or the email used when ordering.

--- user answers (identifier): ORD-1003

--- TURN 2: workflow re-run with the answers ---
==============================================================================
USER REQUEST: Where is order ORD-9999?
==============================================================================

Selected Workflow:
  WF005 - Customer Order Status
  (router: explicit, confidence 1.00) Workflow chosen explicitly by the caller

Inputs resolved:
  - identifier = ORD-1003  [user-provided]
  - orders_path = data/orders.json  [default]
  - shipments_path = data/shipments.json  [default]

Steps Executed:
  1. [OK]   Validate identifier  <validate_identifier, 0.00s> - keys: type, value
  2. [OK]   Search order data  <find_orders, 0.00s> - count=1
  3. [OK]   Retrieve order status  <get_order_status, 0.00s> - 1 items
  4. [SKIP] Retrieve shipment information  <get_shipment_info, 0.00s> - condition not met: orders['with_shipment_count'] > 0
  5. [OK]   Summarize current status  <summarize_orders, 0.00s> - report built: Order status

Conditions / Decisions:
  - [Search order data] Found 1 order(s) for order_id ORD-1003
  - [Retrieve shipment information] skipped because condition `orders['with_shipment_count'] > 0` was false

Result:
## Order status

1 order(s) found.

### Details
- **ORD-1003** (placed 2026-10-05): status **Processing** - 1 x Trail Runner Shoes 42. No shipment yet - it has not been dispatched.

### Overview (1)
| order_id | status | tracking | shipment_status |
|---|---|---|---|
| ORD-1003 | Processing | - | - |
```

## WF005_email - Lookup by customer email (multiple orders)

```text
==============================================================================
USER REQUEST: What orders does alice@example.com have and where are they?
==============================================================================

Selected Workflow:
  WF005 - Customer Order Status
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'Customer Order Status' (score 0.46, runner-up 0.00)

Inputs resolved:
  - identifier = alice@example.com  [extracted]
  - orders_path = data/orders.json  [default]
  - shipments_path = data/shipments.json  [default]

Steps Executed:
  1. [OK]   Validate identifier  <validate_identifier, 0.00s> - keys: type, value
  2. [OK]   Search order data  <find_orders, 0.00s> - count=2
  3. [OK]   Retrieve order status  <get_order_status, 0.00s> - 2 items
  4. [OK]   Retrieve shipment information  <get_shipment_info, 0.00s> - keys: ORD-1001, ORD-1002
  5. [OK]   Summarize current status  <summarize_orders, 0.00s> - report built: Order status

Conditions / Decisions:
  - [Search order data] Found 2 order(s) for email alice@example.com

Result:
## Order status

2 order(s) found.

### Details
- **ORD-1001** (placed 2026-10-01): status **Shipped** - 2 x Classic Cotton T-Shirt (M). Shipment SHP-9001 via FastCarrier: **In transit**, tracking FC123456789, ETA 2026-10-09; last event: Departed Mumbai hub 2026-10-06.
- **ORD-1002** (placed 2026-09-20): status **Delivered** - 1 x Ceramic Mug. Shipment SHP-9002 via FastCarrier: **Delivered**, tracking FC987654321, ETA 2026-09-24; last event: Delivered to recipient 2026-09-24.

### Overview (2)
| order_id | status | tracking | shipment_status |
|---|---|---|---|
| ORD-1001 | Shipped | FC123456789 | In transit |
| ORD-1002 | Delivered | FC987654321 | Delivered |
```

## WF005_carrier_flaky - Carrier API times out once -> engine retries -> succeeds

```text
==============================================================================
USER REQUEST: Where is order ORD-1006?
==============================================================================

Selected Workflow:
  WF005 - Customer Order Status
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'Customer Order Status' (score 0.51, runner-up 0.00)

Inputs resolved:
  - identifier = ORD-1006  [extracted]
  - orders_path = data/orders.json  [default]
  - shipments_path = data/shipments.json  [default]

Steps Executed:
  1. [OK]   Validate identifier  <validate_identifier, 0.00s> - keys: type, value
  2. [OK]   Search order data  <find_orders, 0.00s> - count=1
  3. [OK]   Retrieve order status  <get_order_status, 0.00s> - 1 items
  4. [OK]   Retrieve shipment information  <get_shipment_info, 0.05s x2 attempts> - keys: ORD-1006
  5. [OK]   Summarize current status  <summarize_orders, 0.00s> - report built: Order status

Conditions / Decisions:
  - [Search order data] Found 1 order(s) for order_id ORD-1006

Result:
## Order status

1 order(s) found.

### Details
- **ORD-1006** (placed 2026-10-04): status **Shipped** - 1 x Canvas Backpack. Shipment SHP-9006 via RoadRunner: **Out for delivery**, tracking RR777888999, ETA 2026-10-07; last event: Out for delivery in Hyderabad.

### Overview (1)
| order_id | status | tracking | shipment_status |
|---|---|---|---|
| ORD-1006 | Shipped | RR777888999 | Out for delivery |
```

## WF005_carrier_down - Carrier API down -> retries exhausted -> step skipped, answer still returned

```text
==============================================================================
USER REQUEST: Track order ORD-1005
==============================================================================

Selected Workflow:
  WF005 - Customer Order Status
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'Customer Order Status' (score 0.56, runner-up 0.00)

Inputs resolved:
  - identifier = ORD-1005  [extracted]
  - orders_path = data/orders.json  [default]
  - shipments_path = data/shipments.json  [default]

Steps Executed:
  1. [OK]   Validate identifier  <validate_identifier, 0.00s> - keys: type, value
  2. [OK]   Search order data  <find_orders, 0.00s> - count=1
  3. [OK]   Retrieve order status  <get_order_status, 0.00s> - 1 items
  4. [SKIP] Retrieve shipment information  <get_shipment_info, 0.15s x3 attempts> - failed after 3 attempt(s), skipped: Carrier API 503 Service Unavailable (SkyPost)
        note: attempt 1 failed (Carrier API 503 Service Unavailable (SkyPost)); retrying
        note: attempt 2 failed (Carrier API 503 Service Unavailable (SkyPost)); retrying
  5. [OK]   Summarize current status  <summarize_orders, 0.00s> - report built: Order status

Conditions / Decisions:
  - [Search order data] Found 1 order(s) for order_id ORD-1005
  - [Retrieve shipment information] failed (Carrier API 503 Service Unavailable (SkyPost)); On_Error=skip so the workflow continues without it

Result:
## Order status

1 order(s) found.

### Details
- **ORD-1005** (placed 2026-10-03): status **Shipped** - 1 x LED Desk Lamp. Shipment details are temporarily unavailable from the carrier; please try again shortly.

### Overview (1)
| order_id | status | tracking | shipment_status |
|---|---|---|---|
| ORD-1005 | Shipped | - | - |

**Notes:**
- Shipment lookup failed after retries; status shown from order database only.
```

## WF006_duplicates - Duplicate detection (test question)

```text
==============================================================================
USER REQUEST: Find likely duplicate products in the catalog.
==============================================================================

Selected Workflow:
  WF006 - Duplicate Product Detection
  (router: keyword-tfidf, confidence 0.96) Best keyword/TF-IDF match with 'Duplicate Product Detection' (score 0.60, runner-up 0.05)

Inputs resolved:
  - catalog_path = data/catalog.csv  [default]
  - similarity_threshold = 0.75  [default]

Steps Executed:
  1. [OK]   Load products  <load_table, 0.00s> - row_count=14
  2. [OK]   Normalize names/SKUs  <normalize_fields, 0.00s> - count=14
  3. [OK]   Compare identifiers  <group_exact, 0.00s> - count=1
  4. [OK]   Compare product attributes  <find_similar_pairs, 0.00s> - count=4
  5. [OK]   Group likely duplicates  <build_duplicate_groups, 0.00s> - count=4
  6. [OK]   Assign confidence  <assign_confidence, 0.00s> - count=4
  7. [OK]   Generate duplicate report  <make_report, 0.00s> - report built: Duplicate product detection

Conditions / Decisions:
  - [Compare identifiers] 1 group(s) share an exact normalised SKU -> definite duplicates
  - [Compare product attributes] 4 pair(s) reached similarity >= 0.75 (colour/size mismatch caps a pair below the threshold)
  - [Assign confidence] Exact SKU match => DEFINITE; name/attribute similarity => POSSIBLE (HIGH if score >= 0.90)

Result:
## Duplicate product detection

1 definite and 3 possible duplicate group(s) found in 14 products.

### Duplicate groups (4)
| group | confidence | score | members | example_name | matching_fields | differing_fields |
|---|---|---|---|---|---|---|
| G1 | DEFINITE | 1 | TS-100, ts 100 | Men's Classic Cotton T-Shirt - Blue (L) | sku | - |
| G2 | POSSIBLE - HIGH | 1 | SH-300, SH-301 | Trail Runner Shoes 42 Black | brand, category, color, size | - |
| G3 | POSSIBLE - MEDIUM | 0.85 | TS-100, ts 100, TS-205 | Men's Classic Cotton T-Shirt - Blue (L) | brand, category, color, size | - |
| G4 | POSSIBLE - MEDIUM | 0.76 | WT-500, WT-501 | Steel Water Bottle 750ml | brand, category, color, size | - |

**Files written:**
- outputs/wf006_duplicate_groups.csv

**Notes:**
- Same product in a different colour or size is treated as a variant, not a duplicate.
```

## WF007_missing - Campaign brief (test question) - goal/dates missing, agent asks, user answers

```text
--- TURN 1: agent stops and asks ---
Before I can run this workflow I need:
  - What is the goal of the campaign (e.g. 'increase online sales by 20%')?
  - What are the campaign start and end dates (e.g. 2026-11-01 to 2026-11-30)?

--- user answers (campaign_goal): increase online sales by 20%

--- user answers (campaign_dates): 2026-11-01 to 2026-11-30

--- TURN 2: workflow re-run with the answers ---
==============================================================================
USER REQUEST: Create a campaign brief for the new collection.
==============================================================================

Selected Workflow:
  WF007 - Marketing Campaign Brief
  (router: explicit, confidence 1.00) Workflow chosen explicitly by the caller

Inputs resolved:
  - campaign_goal = increase online sales by 20%  [user-provided]
  - campaign_dates = {'start': '2026-11-01', 'end': '2026-11-30'}  [user-provided]
  - product_filter = new collection  [extracted]
  - products_path = data/products.csv  [default]

Steps Executed:
  1. [OK]   Validate inputs  <validate_campaign_inputs, 0.00s> - keys: goal, start, end, duration_days, audience
  2. [OK]   Identify campaign objective  <classify_objective, 0.00s> - keys: type, label, statement, kpis, target
  3. [OK]   Load product data  <load_table, 0.00s> - row_count=13
  4. [OK]   Summarize products  <summarize_products, 0.00s> - count=6
  5. [OK]   Create messaging  <create_messaging, 0.00s> - keys: headline, key_messages, call_to_action, tone
        note: template messaging (no LLM configured)
  6. [OK]   Create channel recommendations  <recommend_channels, 0.00s> - count=3
  7. [OK]   Create campaign checklist  <build_timeline_checklist, 0.00s> - keys: timeline, checklist
  8. [OK]   Generate campaign brief  <make_report, 0.00s> - report built: Campaign brief

Conditions / Decisions:
  - [Validate inputs] Optional inputs not provided: ['audience', 'promotion'] - will be shown as 'not specified', not invented
  - [Identify campaign objective] Goal classified as 'conversion' -> primary KPIs: Revenue, conversion rate, orders
  - [Summarize products] Product scope: 6 products flagged as new collection

Result:
## Campaign brief

Shop Apparel, Footwear, Accessories while the offer lasts

### Objective
- **Goal**: increase online sales by 20%
- **Type**: Drive sales / conversions
- **KPIs**: Revenue, conversion rate, orders
- **Target**: 20%

### Audience
Not specified

### Promotion
None specified

### Dates
2026-11-01 to 2026-11-30 (30 days)

### Products
6 products (products flagged as new collection); categories {'Apparel': 3, 'Footwear': 2, 'Accessories': 1}; price range 22.00 - 89.50

### Key messaging
- Introducing 6 products across Apparel, Footwear, Accessories (price range 22.00 - 89.50).
- Highlight product quality and everyday value.
- Speak to a broad audience until a target segment is defined.

### Call to action
Shop now

### Tone
Clear, benefit-led, friendly

### Channels (3)
| channel | role |
|---|---|
| Email / CRM | Offer delivery to existing customers |
| Paid search & shopping ads | Capture high-intent demand |
| Retargeting display | Recover abandoned carts |

### Timeline (5)
| phase | dates | focus |
|---|---|---|
| Preparation | 2026-10-18 to 2026-10-31 | Creative, copy, landing pages, channel setup |
| Launch | 2026-11-01 to 2026-11-07 | Go live on all channels; daily monitoring |
| Sustain / optimise | 2026-11-08 to 2026-11-26 | A/B tests, budget shifts, content refresh |
| Final push | 2026-11-27 to 2026-11-30 | Urgency messaging, reminders |
| Review | 2026-12-01 to 2026-12-07 | Results report and learnings |

### Campaign checklist (9)
| task | due | status |
|---|---|---|
| Confirm KPIs and targets with stakeholders | 2026-10-18 | [ ] |
| Finalise product list, pricing and stock av… | 2026-10-22 | [ ] |
| Approve creative and messaging | 2026-10-25 | [ ] |
| Confirm whether a promotion applies | 2026-10-27 | [ ] |
| Set up channels: Email / CRM, Paid search &… | 2026-10-29 | [ ] |
| Set up tracking (UTM links, conversion even… | 2026-10-29 | [ ] |
| Launch campaign and run QA checks | 2026-11-01 | [ ] |
| Mid-campaign performance review | 2026-11-16 | [ ] |
| Publish results report | 2026-12-07 | [ ] |

**Files written:**
- outputs/wf007_campaign_checklist.csv

**Notes:**
- Fields shown as 'Not specified' were not provided and have not been invented.
```

## WF007_full - Campaign brief with everything in one request

```text
==============================================================================
USER REQUEST: Create a campaign brief for the new collection. Goal: increase online sales by 20%. Audience: young professionals. Promotion: 15% off launch week. Dates: 2026-11-01 to 2026-11-30.
==============================================================================

Selected Workflow:
  WF007 - Marketing Campaign Brief
  (router: keyword-tfidf, confidence 0.96) Best keyword/TF-IDF match with 'Marketing Campaign Brief' (score 0.71, runner-up 0.05)

Inputs resolved:
  - campaign_goal = increase online sales by 20%  [extracted]
  - campaign_dates = {'start': '2026-11-01', 'end': '2026-11-30'}  [extracted]
  - target_audience = young professionals  [extracted]
  - promotion = 15% off launch week  [extracted]
  - product_filter = new collection  [extracted]
  - products_path = data/products.csv  [default]

Steps Executed:
  1. [OK]   Validate inputs  <validate_campaign_inputs, 0.00s> - keys: goal, start, end, duration_days, audience
  2. [OK]   Identify campaign objective  <classify_objective, 0.00s> - keys: type, label, statement, kpis, target
  3. [OK]   Load product data  <load_table, 0.00s> - row_count=13
  4. [OK]   Summarize products  <summarize_products, 0.00s> - count=6
  5. [OK]   Create messaging  <create_messaging, 0.00s> - keys: headline, key_messages, call_to_action, tone
        note: template messaging (no LLM configured)
  6. [OK]   Create channel recommendations  <recommend_channels, 0.00s> - count=5
  7. [OK]   Create campaign checklist  <build_timeline_checklist, 0.00s> - keys: timeline, checklist
  8. [OK]   Generate campaign brief  <make_report, 0.00s> - report built: Campaign brief

Conditions / Decisions:
  - [Identify campaign objective] Goal classified as 'conversion' -> primary KPIs: Revenue, conversion rate, orders
  - [Summarize products] Product scope: 6 products flagged as new collection

Result:
## Campaign brief

Shop Apparel, Footwear, Accessories while the offer lasts

### Objective
- **Goal**: increase online sales by 20%
- **Type**: Drive sales / conversions
- **KPIs**: Revenue, conversion rate, orders
- **Target**: 20%

### Audience
young professionals

### Promotion
15% off launch week

### Dates
2026-11-01 to 2026-11-30 (30 days)

### Products
6 products (products flagged as new collection); categories {'Apparel': 3, 'Footwear': 2, 'Accessories': 1}; price range 22.00 - 89.50

### Key messaging
- Introducing 6 products across Apparel, Footwear, Accessories (price range 22.00 - 89.50).
- Offer: 15% off launch week.
- Built for young professionals.

### Call to action
Shop now

### Tone
Clear, benefit-led, friendly

### Channels (5)
| channel | role |
|---|---|
| Email / CRM | Offer delivery to existing customers |
| Paid search & shopping ads | Capture high-intent demand |
| Retargeting display | Recover abandoned carts |
| TikTok / Instagram Reels | Matches the stated young audience |
| LinkedIn | Matches the stated professional audience |

### Timeline (5)
| phase | dates | focus |
|---|---|---|
| Preparation | 2026-10-18 to 2026-10-31 | Creative, copy, landing pages, channel setup |
| Launch | 2026-11-01 to 2026-11-07 | Go live on all channels; daily monitoring |
| Sustain / optimise | 2026-11-08 to 2026-11-26 | A/B tests, budget shifts, content refresh |
| Final push | 2026-11-27 to 2026-11-30 | Urgency messaging, reminders |
| Review | 2026-12-01 to 2026-12-07 | Results report and learnings |

### Campaign checklist (9)
| task | due | status |
|---|---|---|
| Confirm KPIs and targets with stakeholders | 2026-10-18 | [ ] |
| Finalise product list, pricing and stock av… | 2026-10-22 | [ ] |
| Approve creative and messaging | 2026-10-25 | [ ] |
| Configure promotion in store/checkout (15% … | 2026-10-27 | [ ] |
| Set up channels: Email / CRM, Paid search &… | 2026-10-29 | [ ] |
| Set up tracking (UTM links, conversion even… | 2026-10-29 | [ ] |
| Launch campaign and run QA checks | 2026-11-01 | [ ] |
| Mid-campaign performance review | 2026-11-16 | [ ] |
| Publish results report | 2026-12-07 | [ ] |

**Files written:**
- outputs/wf007_campaign_checklist.csv

**Notes:**
- Fields shown as 'Not specified' were not provided and have not been invented.
```

## WF007_asks_only - Campaign brief - agent stops and asks (no guessing)

```text
--- TURN 1: agent stops and asks ---
Before I can run this workflow I need:
  - What is the goal of the campaign (e.g. 'increase online sales by 20%')?
  - What are the campaign start and end dates (e.g. 2026-11-01 to 2026-11-30)?

==============================================================================
USER REQUEST: Create a campaign brief for the new collection.
==============================================================================

Selected Workflow:
  WF007 - Marketing Campaign Brief
  (router: keyword-tfidf, confidence 0.97) Best keyword/TF-IDF match with 'Marketing Campaign Brief' (score 0.62, runner-up 0.04)

Inputs resolved:
  - product_filter = new collection  [extracted]
  - products_path = data/products.csv  [default]

STATUS: More information needed before this workflow can continue.
Before I can run this workflow I need:
  - What is the goal of the campaign (e.g. 'increase online sales by 20%')?
  - What are the campaign start and end dates (e.g. 2026-11-01 to 2026-11-30)?
```

## WF008_keywords - Keyword classification (test question)

```text
==============================================================================
USER REQUEST: Classify these keywords and map them to pages.
==============================================================================

Selected Workflow:
  WF008 - SEO Keyword Classification
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'SEO Keyword Classification' (score 0.60, runner-up 0.00)

Inputs resolved:
  - keywords_path = data/keywords.csv  [default]
  - categories_path = data/seo_categories.csv  [default]

Steps Executed:
  1. [OK]   Read keywords  <load_table, 0.00s> - row_count=24
  2. [OK]   Remove duplicates  <dedupe_rows, 0.00s> - count=23
  3. [OK]   Classify search intent  <classify_intent, 0.00s> - count=23
  4. [OK]   Map keywords to categories  <map_keywords_to_categories, 0.00s> - count=23
  5. [OK]   Identify high-priority keywords  <prioritize_keywords, 0.00s> - count=23
  6. [OK]   Export results  <export_tables, 0.00s> - count=1
  7. [OK]   Generate keyword report  <make_report, 0.00s> - report built: SEO keyword report

Conditions / Decisions:
  - [Remove duplicates] Removed 1 duplicate 'keyword' value(s) (case/whitespace-insensitive)
  - [Classify search intent] Intent classification mode: rules. Distribution: {'transactional': 7, 'commercial': 11, 'informational': 3, 'navigational': 2}
  - [Map keywords to categories] 21 keywords mapped to a category page; 2 unmapped (content gap)
  - [Identify high-priority keywords] Priority = High if score >= 55, Medium if >= 35: 11 high-priority keywords

Result:
## SEO keyword report

23 unique keywords (1 duplicates removed); 11 high priority; 2 without a matching page.

- **Intent distribution**: {'transactional': 7, 'commercial': 11, 'informational': 3, 'navigational': 2}

### Top priority keywords (23)
| keyword | search_volume | intent | category | target_page | priority_score | priority |
|---|---|---|---|---|---|---|
| buy cotton t shirt online | 5400 | transactional | T-Shirts | /apparel/t-shirts | 70.9 | High |
| zip hoodie sale | 7200 | transactional | Hoodies & Beanies | /apparel/hoodies-beanies | 70 | High |
| leather messenger bag price | 3100 | transactional | Bags | /accessories/bags | 69.3 | High |
| slim fit jeans near me | 2900 | transactional | Jeans | /apparel/jeans | 67.9 | High |
| steel water bottle discount code | 1800 | transactional | Water Bottles & Mugs | /home/drinkware | 66.6 | High |
| buy leather messenger bag | 2600 | transactional | Bags | /accessories/bags | 65.3 | High |
| order canvas backpack | 800 | transactional | Bags | /accessories/bags | 60.1 | High |
| water bottle with straw | 4900 | commercial | Water Bottles & Mugs | /home/drinkware | 59.3 | High |
| canvas backpack for school | 6600 | commercial | Bags | /accessories/bags | 59.2 | High |
| desk lamp for study | 2400 | commercial | Lighting | /home/lighting | 56.7 | High |
| cotton socks 3 pack | 2100 | commercial | Socks | /apparel/socks | 55.4 | High |
| trail runner shoes | 8500 | commercial | Running Shoes | /footwear/running-shoes | 53.2 | Medium |

_… 11 more row(s) not shown (full data in exported file)_

### Duplicates removed (1)
| keyword | duplicate_of |
|---|---|
| Buy Cotton T Shirt Online | buy cotton t shirt online |

**Files written:**
- outputs/wf008_keyword_report.csv
```

## WF009_developer - Task assignment (test question)

```text
==============================================================================
USER REQUEST: Assign this urgent task to the best available developer.
==============================================================================

Selected Workflow:
  WF009 - Employee Task Assignment
  (router: keyword-tfidf, confidence 0.97) Best keyword/TF-IDF match with 'Employee Task Assignment' (score 0.57, runner-up 0.04)

Inputs resolved:
  - task_description = Assign this urgent task to the best available developer.  [extracted]
  - employees_path = data/employees.csv  [default]

Steps Executed:
  1. [OK]   Understand task requirements  <analyze_task, 0.01s> - keys: description, skills, role, priority, effort_hours
  2. [OK]   Compare employee skills  <match_employee_skills, 0.00s> - count=8
  3. [OK]   Check current workload  <check_workload, 0.00s> - count=8
  4. [OK]   Rank candidates  <rank_candidates, 0.00s> - count=8
  5. [OK]   Select employee  <select_employee, 0.00s> - keys: selected, reasoning, candidates
  6. [OK]   Generate assignment summary  <make_report, 0.00s> - report built: Task assignment

Conditions / Decisions:
  - [Understand task requirements] Requirements (rules): skills=none stated, role=developer, priority=high, effort=8h (assumed default (not stated)), deadline=2026-10-09 (assumed high-priority SLA (2 days))
  - [Select employee] Selected Arjun Mehta - 3 suitable candidate(s) out of 8

Result:
## Task assignment

Recommended assignee: Arjun Mehta (Developer)

### Reasoning
- Role matches the requested 'developer'
- Has 22h free this week (utilisation 45%) vs 8h needed
- Ranked above 2 other suitable candidate(s) (score 86.5 vs 85.0)

### Priority
high

### Deadline
2026-10-09 (assumed high-priority SLA (2 days))

### Estimated effort
8 hours (assumed default (not stated))

### Required skills
_(none)_

### Task summary
Assign this urgent task to the best available developer.

### Candidate ranking (top 5) (5)
| name | role | skills_matched | skills_missing | remaining_hours | has_capacity | score |
|---|---|---|---|---|---|---|
| Arjun Mehta | Developer | - | - | 22 | yes | 86.5 |
| Karan Singh | QA Engineer | - | - | 20 | yes | 85 |
| Lena Fischer | Developer | - | - | 30 | no | 82.5 |
| Sana Khan | Developer | - | - | 16 | yes | 82 |
| Meera Iyer | UX Designer | - | - | 28 | yes | 71 |
```

## WF009_react - Skill-based assignment

```text
==============================================================================
USER REQUEST: Assign an urgent React bug fix (about 6 hours) to the right person, due 2026-10-12
==============================================================================

Selected Workflow:
  WF009 - Employee Task Assignment
  (router: keyword-tfidf, confidence 0.77) Best keyword/TF-IDF match with 'Employee Task Assignment' (score 0.24, runner-up 0.10)

Inputs resolved:
  - task_description = Assign an urgent React bug fix (about 6 hours) to the right person, d…  [extracted]
  - employees_path = data/employees.csv  [default]

Steps Executed:
  1. [OK]   Understand task requirements  <analyze_task, 0.00s> - keys: description, skills, role, priority, effort_hours
  2. [OK]   Compare employee skills  <match_employee_skills, 0.00s> - count=8
  3. [OK]   Check current workload  <check_workload, 0.00s> - count=8
  4. [OK]   Rank candidates  <rank_candidates, 0.00s> - count=8
  5. [OK]   Select employee  <select_employee, 0.00s> - keys: selected, reasoning, candidates
  6. [OK]   Generate assignment summary  <make_report, 0.00s> - report built: Task assignment

Conditions / Decisions:
  - [Understand task requirements] Requirements (rules): skills=['react'], role=any, priority=high, effort=6h (parsed from request), deadline=2026-10-12 (provided)
  - [Select employee] Selected Arjun Mehta - 1 suitable candidate(s) out of 8

Result:
## Task assignment

Recommended assignee: Arjun Mehta (Developer)

### Reasoning
- Covers all required skills: react
- Has 22h free this week (utilisation 45%) vs 6h needed

### Priority
high

### Deadline
2026-10-12 (provided)

### Estimated effort
6 hours (parsed from request)

### Required skills
- react

### Task summary
Assign an urgent React bug fix (about 6 hours) to the right person, due 2026-10-12

### Candidate ranking (top 5) (5)
| name | role | skills_matched | skills_missing | remaining_hours | has_capacity | score |
|---|---|---|---|---|---|---|
| Arjun Mehta | Developer | react | - | 22 | yes | 86.5 |
| Rohit Das | Frontend Developer | react | - | 2 | no | 61.5 |
| Meera Iyer | UX Designer | - | react | 28 | yes | 51 |
| Karan Singh | QA Engineer | - | react | 20 | yes | 45 |
| Vikram Rao | Data Analyst | - | react | 18 | yes | 43.5 |
```

## WF009_escalate - No suitable employee -> escalation

```text
==============================================================================
USER REQUEST: Assign a Kubernetes migration task that needs about 20 hours
==============================================================================

Selected Workflow:
  WF009 - Employee Task Assignment
  (router: keyword-tfidf, confidence 0.93) Best keyword/TF-IDF match with 'Employee Task Assignment' (score 0.42, runner-up 0.06)

Inputs resolved:
  - task_description = Assign a Kubernetes migration task that needs about 20 hours  [extracted]
  - employees_path = data/employees.csv  [default]

Steps Executed:
  1. [OK]   Understand task requirements  <analyze_task, 0.00s> - keys: description, skills, role, priority, effort_hours
  2. [OK]   Compare employee skills  <match_employee_skills, 0.00s> - count=8
  3. [OK]   Check current workload  <check_workload, 0.00s> - count=8
  4. [OK]   Rank candidates  <rank_candidates, 0.00s> - count=8
  5. [ESC]  Select employee  <select_employee, 0.00s> - No suitable employee found: nobody has the required skills/role (kubernetes). Escalating …

Conditions / Decisions:
  - [Understand task requirements] Requirements (rules): skills=['kubernetes'], role=any, priority=medium, effort=20h (parsed from request), deadline=2026-10-12 (assumed medium-priority SLA (5 days))

STATUS: ESCALATION REQUIRED - No suitable employee found: nobody has the required skills/role (kubernetes). Escalating to the manager.

## Task assignment - escalated

No suitable employee found: nobody has the required skills/role (kubernetes). Escalating to the manager.

### Task
Assign a Kubernetes migration task that needs about 20 hours

### Suggested next steps
- Re-prioritise someone's current work to free capacity
- Approve overtime or contractor support
- Relax the skill requirement / split the task

### Closest candidates (5)
| name | role | skills_matched | skills_missing | remaining_hours | has_capacity | score |
|---|---|---|---|---|---|---|
| Meera Iyer | UX Designer | - | kubernetes | 28 | yes | 51 |
| Arjun Mehta | Developer | - | kubernetes | 22 | yes | 46.5 |
| Karan Singh | QA Engineer | - | kubernetes | 20 | yes | 45 |
| Lena Fischer | Developer | - | kubernetes | 30 | no | 42.5 |
| Vikram Rao | Data Analyst | - | kubernetes | 18 | no | 33.5 |
```

## WF010_performance - Performance report (test question)

```text
==============================================================================
USER REQUEST: Which workflows are failing most often?
==============================================================================

Selected Workflow:
  WF010 - Workflow Performance Report
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'Workflow Performance Report' (score 0.38, runner-up 0.00)

Inputs resolved:
  - log_files = ['data/execution_logs.csv', 'logs/runtime_logs.csv']  [default]
  - failure_rate_threshold_pct = 10  [default]
  - exec_time_threshold_sec = 20  [default]
  - slow_step_threshold_sec = 5  [default]

Steps Executed:
  1. [OK]   Load execution logs  <load_table, 0.03s> - row_count=2499
  2. [OK]   Calculate success/failure rate  <calc_failure_rates, 0.00s> - count=11
  3. [OK]   Calculate average execution time  <calc_execution_times, 0.00s> - count=11
  4. [OK]   Identify frequent errors  <frequent_errors, 0.00s> - count=5
  5. [OK]   Identify slow steps  <slow_steps, 0.00s> - count=3
  6. [OK]   Generate recommendations  <generate_recommendations, 0.00s> - keys: flagged, recommendations, flagged_count
  7. [OK]   Generate performance report  <make_report, 0.00s> - report built: Workflow performance report

Conditions / Decisions:
  - [Identify slow steps] 3 step(s) have average duration above 5s
  - [Generate recommendations] Flag rule: failure rate > 10% OR average execution time > 20s -> 5 workflow(s) flagged

Result:
## Workflow performance report

5 of 11 workflows are flagged (failure rate > 10% or average time > 20s), based on 408 runs.

### Recommendations
- WF004 Product Description Generator: most frequent error 'LLMError: rate limit exceeded (N)' (11x) - throttle/queue requests and cache repeated LLM or API calls.
- WF004 Product Description Generator: step 'Create product description' averages 12.63s - cache, batch or parallelise this step.
- WF003 Vendor File Processing: most frequent error 'ValidationError: missing required column 'sku'' (5x) - add schema validation up-front and return a clear, fixable message to the user.
- WF005 Customer Order Status: most frequent error 'TimeoutError: carrier API timed out after Ns' (6x) - add retries with exponential backoff and a circuit breaker for the flaky dependency.
- WF007 Marketing Campaign Brief: most frequent error 'LLMError: rate limit exceeded (N)' (11x) - throttle/queue requests and cache repeated LLM or API calls.
- WF007 Marketing Campaign Brief: step 'Create messaging' averages 12.89s - cache, batch or parallelise this step.
- WF008 SEO Keyword Classification: most frequent error 'LLMError: invalid JSON in classifier response' (2x) - harden parsing and quarantine bad rows instead of failing the whole run.
- WF008 SEO Keyword Classification: step 'Classify search intent' averages 19.14s - cache, batch or parallelise this step.

### Failure rate by workflow (worst first) (11)
| workflow_id | workflow | runs | failed | failure_rate_pct |
|---|---|---|---|---|
| WF004 | Product Description Generator | 33 | 8 | 24.2 |
| WF003 | Vendor File Processing | 38 | 5 | 13.2 |
| WF005 | Customer Order Status | 64 | 6 | 10.2 |
| WF002 | Product Price Validation | 35 | 3 | 8.6 |
| WF007 | Marketing Campaign Brief | 38 | 3 | 7.9 |
| WF008 | SEO Keyword Classification | 37 | 2 | 5.4 |
| WF010 | Workflow Performance Report | 38 | 2 | 5.3 |
| WF006 | Duplicate Product Detection | 36 | 1 | 2.8 |
| WF009 | Employee Task Assignment | 43 | 1 | 2.6 |
| WF001 | Inventory Restock Check | 45 | 1 | 2.2 |
| WF011 | WF011 | 1 | 0 | 0 |

### Flagged workflows (5)
| workflow_id | workflow | failure_rate_pct | avg_exec_sec | flags |
|---|---|---|---|---|
| WF004 | Product Description Generator | 24.2 | 20.97 | failure rate 24.2% > 10%; avg time 20.97s >… |
| WF003 | Vendor File Processing | 13.2 | 1.66 | failure rate 13.2% > 10% |
| WF005 | Customer Order Status | 10.2 | 5.15 | failure rate 10.2% > 10% |
| WF007 | Marketing Campaign Brief | 7.9 | 26.53 | avg time 26.53s > 20s |
| WF008 | SEO Keyword Classification | 5.4 | 36.21 | avg time 36.21s > 20s |

### Average execution time (11)
| workflow_id | avg_exec_sec | max_exec_sec |
|---|---|---|
| WF008 | 36.21 | 54.81 |
| WF007 | 26.53 | 44.82 |
| WF004 | 20.97 | 34.97 |
| WF006 | 7.96 | 11.64 |
| WF005 | 5.15 | 11.01 |
| WF010 | 2.22 | 2.99 |
| WF003 | 1.66 | 2.55 |
| WF009 | 0.9 | 1.71 |
| WF002 | 0.87 | 1.61 |
| WF001 | 0.39 | 0.69 |

_… 1 more row(s) not shown (full data in exported file)_

### Most frequent errors (5)
| error | occurrences | workflows |
|---|---|---|
| LLMError: rate limit exceeded (N) | 11 | WF004, WF007 |
| TimeoutError: carrier API timed out after Ns | 6 | WF005 |
| ValidationError: missing required column 's… | 5 | WF003 |
| ValidationError: missing required column 'v… | 3 | WF002 |
| LLMError: invalid JSON in classifier respon… | 2 | WF008 |

### Slow steps (3)
| workflow_id | step | avg_sec | samples |
|---|---|---|---|
| WF008 | Classify search intent | 19.14 | 37 |
| WF007 | Create messaging | 12.89 | 38 |
| WF004 | Create product description | 12.63 | 33 |

**Files written:**
- outputs/wf010_failure_rate_by_workflow_worst_first.csv
```
