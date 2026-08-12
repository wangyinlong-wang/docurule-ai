# Executable YAML recipes

DocuRule schema v1 turns a named packet of UTF-8 text documents into deterministic validation results. A recipe declares the exact document file names, their business kinds, the fields expected from them, and an allowlisted set of rules.

The runtime is data-only. It never evaluates Python, JavaScript, shell commands, templates, imports, URLs, or arbitrary expressions.

## Run a recipe

From the web workspace, choose **Run rules.yml**, select the YAML file, and select every required document. File names are part of the contract and must match exactly.

The equivalent API call is:

```bash
curl -F 'recipe=@demo/three-way-match/rules.yml' \
  -F 'files=@demo/three-way-match/purchase-order-PO-2026-0812.txt;type=text/plain' \
  -F 'files=@demo/three-way-match/supplier-invoice-INV-1048.txt;type=text/plain' \
  -F 'files=@demo/three-way-match/delivery-note-DN-7721.txt;type=text/plain' \
  http://localhost:8080/api/v1/recipes/run
```

The response is a normal DocuRule case. Poll `GET /api/v1/cases/{id}` until it reaches `needs_review`, edit a field through the UI or API, and the same recipe rules run again.

When a reviewer or downstream script needs a flat field view, use the [CSV export contract](csv-export.md). It documents the exact columns, UTF-8 BOM, quoting behavior, and a copyable Python consumer; JSON remains the complete audit source.

## Five-minute contribution path

The quickest useful contribution is a small, synthetic packet that makes one deterministic workflow easy to reproduce. Use the public [`demo/three-way-match`](../demo/three-way-match/) directory as the fixture and copy it before editing:

```bash
cp -R demo/three-way-match demo/my-recipe
```

Then keep this checklist:

1. Keep the copied `my-recipe` id or choose another lowercase, hyphenated id, then update `rules.yml` (`id`, title, description, document kinds, and exact file names).
2. Keep packet documents as UTF-8 `.txt`, `.md`, or `.csv`; do not add real personal, medical, financial, or confidential data.
3. Use only the three supported assertion families below: document presence, normalized cross-document equality, and numeric `less_than_or_equal` (including the restricted `multiply` expression).
4. Update the fixture `README.md` and `expected-result.json` with the initial checks, expected pass/fail result, and one reviewer correction that can be reproduced from the packet.
5. Run the copied recipe from the web UI or with the API command above. In the pull request, include the exact command, result, and why the packet is useful.

The fixture layout is intentionally small:

```text
demo/<your-recipe-id>/
├── README.md
├── rules.yml
├── expected-result.json
└── synthetic-input-*.txt
```

For a first documentation-only contribution, start with the [contributing guide](../CONTRIBUTING.md), then check the current [good first issue](https://github.com/wangyinlong-wang/docurule-ai/labels/good%20first%20issue) list or [Discussions](https://github.com/wangyinlong-wang/docurule-ai/discussions) for an active entry point. A current example is [Issue #20: synthetic expense-receipt recipe fixture](https://github.com/wangyinlong-wang/docurule-ai/issues/20); check its assignment before starting. If the workflow or expected result is unclear, include the smallest synthetic packet you can share. A maintainer can help confirm the field keys and rule boundary before you spend time on implementation.

## Minimal schema

```yaml
schema_version: 1
id: invoice-receipt-check
title: Invoice and receipt check
description: Compare an invoice with a receiving record.
processing_mode: rules-only

documents:
  - kind: invoice
    file: invoice.txt
    required: true
  - kind: delivery_note
    file: receipt.txt
    required: true

fields:
  required: [supplier_name, invoiced_quantity, received_quantity]
  numeric: [invoiced_quantity, received_quantity]

rules:
  - id: packet_complete
    title: Required documents are present
    assertion:
      includes_all_document_kinds: [invoice, delivery_note]

  - id: supplier_matches
    title: Supplier matches
    assertion:
      all_equal:
        field: supplier_name
        across: [invoice, delivery_note]
        normalization: trim_casefold_whitespace

  - id: invoice_within_receipt
    title: Invoiced quantity does not exceed received quantity
    assertion:
      less_than_or_equal:
        left: invoiced_quantity
        right: received_quantity
```

## Supported assertions

### `includes_all_document_kinds`

Passes only when every listed kind is present in the packet.

```yaml
assertion:
  includes_all_document_kinds: [purchase_order, invoice, delivery_note]
```

### `all_equal`

Reads one named field from each listed document kind and compares the normalized values. Missing values fail explicitly.

```yaml
assertion:
  all_equal:
    field: po_number
    across: [purchase_order, invoice, delivery_note]
    normalization: lowercase_alphanumeric
```

Supported normalization strategies:

- `trim_casefold_whitespace` — trims, case-folds, and collapses whitespace;
- `lowercase_alphanumeric` — also removes punctuation and separators.

### `less_than_or_equal`

Compares two numeric field expressions. Either side can be a field key or a multiplication expression.

```yaml
assertion:
  less_than_or_equal:
    left: invoice_total
    right:
      multiply: [received_quantity, unit_price]
```

## Current limits

- Recipe YAML: UTF-8, at most 128 KB, schema version `1`.
- Packet: at most 20 declared documents and 50 rules.
- Uploaded recipe documents: UTF-8 `.txt`, `.md`, or `.csv`, up to the configured per-file upload limit.
- Every uploaded file must be declared; every required declaration must be uploaded; duplicates and path-like names are rejected before a case directory is created.
- Field extraction currently uses DocuRule's known normalized field keys and deterministic text patterns. Custom extraction schemas and recipe-driven image/PDF processing are roadmap work.
- `fields.required` and `fields.numeric` document the contract today; rules themselves determine pass/fail behavior.

Use only synthetic or fully anonymized data in public recipes and bug reports. Do not expose the unauthenticated app directly to the public internet.
