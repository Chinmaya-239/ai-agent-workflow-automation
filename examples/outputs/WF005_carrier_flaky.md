# WF005_carrier_flaky - Carrier API times out once -> engine retries -> succeeds

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
