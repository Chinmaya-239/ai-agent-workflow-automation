# WF004_content - Content generation with partly missing attributes (agent asks, user answers; material is NOT invented)

```text
--- TURN 1: agent stops and asks ---
Before I can run this workflow I need:
  - Please describe the product (name, category, material, color, target audience).

--- user answers (product_attributes): name: Trail Runner Pro; category: running shoes; color: blue; audience: trail runners

--- TURN 2: workflow re-run with the answers ---
==============================================================================
USER REQUEST: Generate SEO content for this product.
==============================================================================

Selected Workflow:
  WF004 - Product Description Generator
  (router: explicit, confidence 1.00) Workflow chosen explicitly by the caller

Inputs resolved:
  - product_attributes = {'product_name': 'Trail Runner Pro', 'category': 'running shoes', 'co…  [user-provided]

Steps Executed:
  1. [OK]   Validate required attributes  <validate_attributes, 0.00s> - keys: provided, missing
  2. [OK]   Create product description  <generate_text, 0.00s> - The Trail Runner Pro (running shoes) in blue. It is desig...
        note: description: template fallback (no LLM configured)
  3. [OK]   Generate short description  <generate_text, 0.00s> - Trail Runner Pro - running shoes in blue for trail runners.
        note: short_description: template fallback (no LLM configured)
  4. [OK]   Generate SEO title  <generate_text, 0.00s> - Trail Runner Pro - running shoes (blue)
        note: seo_title: template fallback (no LLM configured)
  5. [OK]   Generate meta description  <generate_text, 0.00s> - Shop the Trail Runner Pro in blue for trail runners. Orde...
        note: meta_description: template fallback (no LLM configured)
  6. [OK]   Validate generated text  <validate_text, 0.00s> - keys: texts, warnings
  7. [OK]   Compile product content  <make_report, 0.00s> - report built: Product content

Conditions / Decisions:
  - [Validate required attributes] Missing attributes ['material', 'features'] will NOT be invented; they are marked as missing in the output
  - [Validate generated text] All generated text passed length and invented-attribute checks

Result:
## Product content

Content generated using only the attributes you provided.

### Product description
The Trail Runner Pro (running shoes) in blue. It is designed for trail runners.

### Short description
Trail Runner Pro - running shoes in blue for trail runners.

### SEO title
Trail Runner Pro - running shoes (blue)

### Meta description
Shop the Trail Runner Pro in blue for trail runners. Order online today.

### Attributes used
- **product_name**: Trail Runner Pro
- **category**: running shoes
- **color**: blue
- **target_audience**: trail runners

### MISSING information (not invented)
- material
- features

### Validation warnings
_(none)_
```
