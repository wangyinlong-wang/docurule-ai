# Procurement three-way match recipe

This self-contained, entirely synthetic packet demonstrates a common accounts-payable control: match a purchase order, supplier invoice, and delivery note before approving payment.

## Included assets

- `purchase-order-PO-2026-0812.txt` — 100 units ordered at USD 25.00
- `supplier-invoice-INV-1048.txt` — 96 units invoiced for USD 2,400.00
- `delivery-note-DN-7721.txt` — only 90 units received
- `rules.yml` — the six deterministic checks and eight required fields
- `expected-result.json` — expected extraction, validation, and correction results

## Expected flow

Choose **Run rules.yml** and upload this folder's `rules.yml` plus its three text documents, or use the built-in **Explore the demo** action. The initial review extracts eight merged fields and returns six checks: four pass and two fail because 96 units were invoiced but only 90 were received, making the USD 2,400.00 invoice greater than the USD 2,250.00 received value.

In the review workspace, change **Received quantity** from `90` to `96`. Revalidation should return `6/6 passed`, because the received value becomes USD 2,400.00.

The built-in procurement demo and uploaded recipe both run in `rules-only` mode and do not require Ollama or a cloud model. The same safe recipe runtime evaluates `rules.yml` during initial processing and after reviewer corrections. See the [recipe authoring guide](../../docs/recipes.md) for the supported schema and operators.
