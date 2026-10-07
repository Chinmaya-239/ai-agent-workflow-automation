# WF002_prices - Price validation (test question)

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
