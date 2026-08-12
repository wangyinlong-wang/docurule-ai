# Changelog

## 0.5.1 - 2026-08-13

### Added

- Validate supported upload extension/MIME pairs before creating storage directories.
- Return a clear `415` response for unknown extensions and mismatched metadata, with regression coverage.

## 0.5.0 - 2026-08-13

### Added

- Added provider-aware empty-field guidance for image-only reviews, including a link to AI provider setup.
- Added a distinct text-document empty state so reviewers can keep editing or exporting without being told to install a vision model.
- Recorded provider availability metadata for explaining a rules fallback without retaining document content.

## 0.4.0 - 2026-08-13

### Added

- Added UTF-8 CSV export at `/api/v1/cases/{id}/export?format=csv` with one row per normalized case field, while JSON remains the complete audit source.
- Added CSV export to the hosted showcase and coverage for quoting, provenance, and unknown format errors.

## 0.3.0 - 2026-08-12

### Added

- Upload and execute schema-v1 `rules.yml` recipes from the web workspace or `POST /api/v1/recipes/run`.
- Safe declarative operators for required document kinds, normalized cross-document equality, and numeric comparisons with multiplication.
- Field corrections re-run the uploaded recipe immediately, preserving the same review and JSON audit flow.
- A recipe authoring guide, API example, schema constraints, and unsafe-input tests.

### Changed

- The bundled procurement demo now executes its public `demo/three-way-match/rules.yml` instead of a separate hard-coded validation path.
- Docker Compose binds the unauthenticated app to `127.0.0.1` by default.

### Limits

- Uploaded recipe packets currently accept UTF-8 TXT, Markdown, and CSV files with exact manifest file names.
- Custom extraction schemas, recipe-driven PDF/image processing, and additional operators remain roadmap work.

## 0.2.1 - 2026-08-12

- Added the reusable procurement recipe fixture, CI-checked golden result, and verified social preview.

## 0.2.0 - 2026-08-12

- Added the deterministic procurement three-way-match Hero demo.
