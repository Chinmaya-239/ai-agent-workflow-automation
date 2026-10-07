# WF008_keywords - Keyword classification (test question)

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
