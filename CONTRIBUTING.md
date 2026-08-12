# Contributing to DocuRule

Thanks for helping build a practical, local-first document validation layer. Small, focused contributions are welcome.

## Before opening a change

1. Search existing issues and discussions.
2. Open an issue first for large features, new storage systems, or architecture changes.
3. Never include real customer, medical, identity, financial, or confidential documents. Use synthetic fixtures.

Good first contributions include:

- a reproducible document-packet recipe and its expected result;
- an extraction or validation edge case with a synthetic fixture;
- an Ollama/OpenAI-compatible model compatibility note;
- accessibility, documentation, and test improvements.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r apps/api/requirements-dev.txt
npm install --prefix apps/web
```

Run the API and web app in separate terminals:

```bash
DOCURULE_AI_PROVIDER=local .venv/bin/uvicorn docurule.main:app \
  --app-dir apps/api/src --reload --port 8000
npm run dev --prefix apps/web
```

Or use `docker compose up --build` for the production-shaped path.

## Quality checks

Before submitting a pull request:

```bash
.venv/bin/pytest -q apps/api
.venv/bin/ruff check apps/api
npm run build --prefix apps/web
```

Changes to extraction or validation behavior need a deterministic test. New recipe fixtures need an `expected-result.json` and must not depend on a network model in CI.

## Pull requests

- Keep the scope narrow and explain the user-facing behavior.
- Link the issue when one exists.
- Include before/after screenshots for UI changes.
- Update README or architecture docs when setup, public APIs, or boundaries change.
- Call out migrations, model assumptions, and known limitations.

By contributing, you agree that your work is licensed under the repository's MIT License and that you will follow the [Code of Conduct](CODE_OF_CONDUCT.md).
