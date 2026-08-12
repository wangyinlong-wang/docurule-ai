# Procurement three-way match recipe

This self-contained, entirely synthetic packet demonstrates a common accounts-payable control: match a purchase order, supplier invoice, and delivery note before approving payment.

## Included assets

- `purchase-order-PO-2026-0812.txt` — 100 units ordered at USD 25.00
- `supplier-invoice-INV-1048.txt` — 96 units invoiced for USD 2,400.00
- `delivery-note-DN-7721.txt` — only 90 units received
- `rules.yml` — the six deterministic checks and eight required fields
- `expected-result.json` — expected extraction, validation, and correction results

## Expected flow

Upload the three text documents together, or use the built-in **Explore the demo** action. The initial review extracts eight merged fields and returns six checks: four pass and two fail because 96 units were invoiced but only 90 were received, making the USD 2,400.00 invoice greater than the USD 2,250.00 received value.

In the review workspace, change **Received quantity** from `90` to `96`. Revalidation should return `6/6 passed`, because the received value becomes USD 2,400.00.

The built-in procurement demo runs in `rules-only` mode and does not require Ollama or a cloud model. `rules.yml` documents the reusable recipe contract; the current application keeps the executable rule implementation in its deterministic processing engine.
