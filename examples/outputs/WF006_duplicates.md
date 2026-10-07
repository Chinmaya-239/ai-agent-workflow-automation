# WF006_duplicates - Duplicate detection (test question)

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
