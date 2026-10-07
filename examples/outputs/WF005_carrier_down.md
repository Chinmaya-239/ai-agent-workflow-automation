# WF005_carrier_down - Carrier API down -> retries exhausted -> step skipped, answer still returned

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
