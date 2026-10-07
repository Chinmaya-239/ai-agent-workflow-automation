# WF005_order - Order status (test question)

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
