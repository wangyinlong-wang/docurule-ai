# Ollama model compatibility reports

This page is a small, repeatable format for reporting whether a local model can
cross DocuRule's provider boundary. It is deliberately an evidence log, not an
accuracy leaderboard. A report covers the exact model digest, host and input
that were tested; one report is not a generalized accuracy benchmark or an
endorsement of the model.

## Safety and scope

Use only the public synthetic fixture in
[`demo/three-way-match/`](../demo/three-way-match/) (or a fully anonymized
equivalent). Never attach or paste real medical, financial, identity, invoice,
customer, or other confidential documents into an issue, pull request, model
prompt, log, or screenshot. Redact API keys and private endpoint names from
reports.

The result should describe the tested input type and workflow. `PASS` means the
provider connected and returned parseable output for that narrow input; it does
not mean that all fields, layouts, languages, image formats, or production
workloads are accurate.

## Reproduce a report

Start Ollama and make the exact model available:

```bash
ollama serve
ollama pull gemma4:latest
ollama show gemma4:latest
```

Run DocuRule with the local provider (the Compose default points from the
container to the host Ollama service):

```bash
DOCURULE_AI_PROVIDER=ollama \
DOCURULE_AI_BASE_URL=http://host.docker.internal:11434 \
DOCURULE_AI_MODEL=gemma4:latest \
docker compose up -d --build
```

Check the provider before sending a document:

```bash
curl -sS http://localhost:8080/api/v1/provider
```

Run the public deterministic fixture through the API. This confirms the
DocuRule packet and review flow without requiring a model; it is useful to
separate a provider problem from a fixture/API problem:

```bash
case_json=$(curl -sS -X POST http://localhost:8080/api/v1/demo/procurement)
case_id=$(printf '%s' "$case_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
curl -sS "http://localhost:8080/api/v1/cases/$case_id"
curl -sS "http://localhost:8080/api/v1/cases/$case_id/export"
```

For a provider-backed text smoke test, upload one public synthetic document and
wait for the case response to settle:

```bash
case_json=$(curl -sS -X POST \
  -F 'name=Compatibility report · synthetic PO' \
  -F 'process=true' \
  -F 'files=@demo/three-way-match/purchase-order-PO-2026-0812.txt;type=text/plain' \
  http://localhost:8080/api/v1/cases)
case_id=$(printf '%s' "$case_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
curl -sS "http://localhost:8080/api/v1/cases/$case_id"
```

Record the provider status, case status, fields returned, elapsed time, and
any fallback/error. Do not report a model as compatible solely because
`/api/v1/provider` is reachable: the extraction smoke test must also be
recorded.

## Copyable report template

```markdown
### <model name> — <YYYY-MM-DD>

- Result: PASS | PARTIAL | FAIL
- DocuRule commit/release:
- OS / architecture:
- RAM / GPU:
- Docker / Compose:
- Ollama version:
- Model name and exact digest:
- Provider: `ollama`
- Base URL (redacted if remote):
- Input type: text fixture | image fixture | PDF | other
- Fixture: public synthetic path and commit
- `/api/v1/provider`: available, model, detail
- API flow: endpoint(s), case status, field/JSON result
- Observed latency: provider check __ ms; extraction __ ms
- Limitations or errors:
- Reproduction commands:
```

## Completed example (synthetic only)

The following report was run locally on 2026-08-13 against the repository's
public `demo/three-way-match/purchase-order-PO-2026-0812.txt` fixture. No real
documents or external customer data were used.

### `gemma4:latest` — 2026-08-13

- Result: **PARTIAL**
- DocuRule commit/release: `v0.5.3` (local checkout)
- OS / architecture: macOS Darwin 25.5.0, arm64; Apple M4, 24 GiB RAM
- RAM / GPU: 24 GiB unified memory; Apple M4 GPU (system-reported)
- Docker / Compose: Docker Engine `29.5.2`; Docker Compose `v5.1.4`
- Ollama version: `0.32.4`
- Model name and exact digest: `gemma4:latest`,
  `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb`
- Provider: `ollama`
- Base URL: `http://127.0.0.1:11434` (local only)
- Input type: UTF-8 text fixture; no image was sent
- Fixture: `demo/three-way-match/purchase-order-PO-2026-0812.txt`
- `/api/v1/provider`: `available=true`, model `gemma4:latest`, detail `Connected`
- API flow: `POST /api/v1/demo/procurement` returned `201`; the public fixture
  settled at `needs_review` with the deterministic baseline of `4 passed / 2
  failed` validations (the built-in demo intentionally does not call the
  provider)
- Extraction result: HTTP provider call returned parseable JSON with
  `kind=purchase_order` and one `supplier_name` field; `last_extract_ok=true`
- Observed latency: provider status **23 ms**; extraction **22,616 ms**
- Limitations: this is one short text input, not a vision test. The response
  omitted other expected purchase-order fields, so it is recorded as PARTIAL;
  no claim is made about image OCR, field completeness, throughput, or
  production accuracy. The deterministic three-way-match demo remains the
  reproducible rules-only baseline (`4/6` initially and `6/6` after correcting
  received quantity `90 → 96`).

Reproduction uses the commands above with the model digest recorded by
`curl http://127.0.0.1:11434/api/tags` or `ollama list`, plus the public fixture
path. If a local HTTP proxy is configured, ensure loopback traffic bypasses it
before running the smoke test; do not expose Ollama publicly.

## What a useful follow-up contains

When a model fails, include the exact error class/message, endpoint, model
digest, input type, latency, and whether the deterministic fixture still passes.
Do not include raw document contents beyond the public synthetic fixture. A
failure report is still useful: it narrows a protocol, model-capability, or
resource limitation without pretending that a single run proves general
accuracy.
