# WF007_full - Campaign brief with everything in one request

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
