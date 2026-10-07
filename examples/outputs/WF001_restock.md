# WF001_restock - Inventory restock (test question)

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
