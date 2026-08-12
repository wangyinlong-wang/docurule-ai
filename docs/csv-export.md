# CSV export contract

DocuRule exposes a flat, review-friendly CSV view for a case:

```text
GET /api/v1/cases/{case_id}/export?format=csv
```

The response is a UTF-8 CSV document with a BOM (`utf-8-sig`) so spreadsheet
applications open non-ASCII labels correctly. The download filename is scoped to
the case: `docurule-{case_id}.csv`. Values are written with standard CSV quoting;
commas, quotes, and newlines in a value or source quote are preserved when a
normal CSV reader parses the file.

There is one row for each normalized case field. The header and column order are
stable:

```text
case_id,case_name,case_status,decision,field_key,label,value,confidence,source_document_id,source_quote,reviewed
```

For example, a synthetic case may produce:

```csv
case_id,case_name,case_status,decision,field_key,label,value,confidence,source_document_id,source_quote,reviewed
case-0001,Synthetic AP review,needs_review,,supplier_name,Supplier name,Northstar Components Ltd,0.99,document-001,"Supplier: Northstar Components Ltd.",True
case-0001,Synthetic AP review,needs_review,,invoice_total,Invoice total,2400.0,0.98,document-002,"Invoice Total: $2,400.00",False
```

The CSV is a review and analysis view, not the complete audit record. Use the
JSON export (`GET /api/v1/cases/{case_id}/export`, the default) as the source of
truth when you need the full document list, field evidence, validations, or
audit log. Empty values are represented by an empty CSV cell; `reviewed` is
serialized as `True` or `False`.

## Download with curl

Start DocuRule locally, set the case id returned by `POST /api/v1/cases` (or by
one of the demo endpoints), and save the response:

```bash
CASE_ID=case-0001
curl --fail --show-error \
  --output "docurule-${CASE_ID}.csv" \
  "http://localhost:8080/api/v1/cases/${CASE_ID}/export?format=csv"
```

The API also sends `Content-Disposition: attachment; filename="docurule-${CASE_ID}.csv"`.
The explicit output path above makes the command convenient in scripts while
the response header remains useful for browser downloads.

## Consume from Python

The standard library's `csv.DictReader` handles quoting. Use `utf-8-sig` so the
reader accepts DocuRule's BOM as well as a BOM-less copy saved by another tool:

```python
import csv
import io
from urllib.request import urlopen

case_id = "case-0001"
url = f"http://localhost:8080/api/v1/cases/{case_id}/export?format=csv"

with urlopen(url) as response:
    text = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
    rows = list(csv.DictReader(text))

for row in rows:
    if row["field_key"] == "invoice_total":
        print(row["value"], row["confidence"], row["source_quote"])
```

For stable integrations, treat `field_key` as the identifier and keep
`source_document_id`/`source_quote` alongside the value. Do not infer an
approval decision from the CSV alone; fetch the JSON audit record when a
workflow needs the complete validation and review history.
