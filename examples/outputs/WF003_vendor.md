# WF003_vendor - Vendor file processing (test question)

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
