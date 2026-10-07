# WF005_not_found - Unknown order -> agent asks for another identifier -> user supplies one

```text
--- TURN 1: agent stops and asks ---
No order found for order id 'ORD-9999'. Please provide another order ID or the email used when ordering.

--- user answers (identifier): ORD-1003

--- TURN 2: workflow re-run with the answers ---
==============================================================================
USER REQUEST: Where is order ORD-9999?
==============================================================================

Selected Workflow:
  WF005 - Customer Order Status
  (router: explicit, confidence 1.00) Workflow chosen explicitly by the caller

Inputs resolved:
  - identifier = ORD-1003  [user-provided]
  - orders_path = data/orders.json  [default]
  - shipments_path = data/shipments.json  [default]

Steps Executed:
  1. [OK]   Validate identifier  <validate_identifier, 0.00s> - keys: type, value
  2. [OK]   Search order data  <find_orders, 0.00s> - count=1
  3. [OK]   Retrieve order status  <get_order_status, 0.00s> - 1 items
  4. [SKIP] Retrieve shipment information  <get_shipment_info, 0.00s> - condition not met: orders['with_shipment_count'] > 0
  5. [OK]   Summarize current status  <summarize_orders, 0.00s> - report built: Order status

Conditions / Decisions:
  - [Search order data] Found 1 order(s) for order_id ORD-1003
  - [Retrieve shipment information] skipped because condition `orders['with_shipment_count'] > 0` was false

Result:
## Order status

1 order(s) found.

### Details
- **ORD-1003** (placed 2026-10-05): status **Processing** - 1 x Trail Runner Shoes 42. No shipment yet - it has not been dispatched.

### Overview (1)
| order_id | status | tracking | shipment_status |
|---|---|---|---|
| ORD-1003 | Processing | - | - |
```
