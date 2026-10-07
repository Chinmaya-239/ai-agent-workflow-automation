# WF005_email - Lookup by customer email (multiple orders)

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
