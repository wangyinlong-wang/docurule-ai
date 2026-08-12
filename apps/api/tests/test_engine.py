from pathlib import Path

from docurule.config import Settings
from docurule.engine import ProcessingEngine
from docurule.models import CaseRecord, CaseStatus, DocumentRecord, ValidationStatus
from docurule.provider import AIProvider
from docurule.recipes import load_recipe, load_recipe_documents
from docurule.store import CaseStore


def build_engine(tmp_path: Path) -> tuple[ProcessingEngine, CaseStore, Path]:
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    store = CaseStore(tmp_path / "test.sqlite3")
    settings = Settings(data_dir=tmp_path, ai_provider="local")
    return ProcessingEngine(store, AIProvider(settings), uploads), store, uploads


def test_processes_and_cross_validates_a_document_packet(tmp_path: Path):
    engine, store, uploads = build_engine(tmp_path)
    case_id = "demo-case"
    case_dir = uploads / case_id
    case_dir.mkdir()

    invoice = DocumentRecord(
        id="invoice01", file_name="invoice.txt", media_type="text/plain", size_bytes=120
    )
    claim = DocumentRecord(
        id="claim01", file_name="claim-form.txt", media_type="text/plain", size_bytes=120
    )
    (case_dir / "invoice01.txt").write_text(
        "MEDICAL INVOICE\nInvoice Number: INV-01\nPatient Name: Alex Chen\n"
        "Service Date: 2026-08-03\nTotal Amount: $3,258.67",
        encoding="utf-8",
    )
    (case_dir / "claim01.txt").write_text(
        "CLAIM FORM\nClaim Number: CLM-01\nFull Name: Alex Chen\n"
        "Service Date: 2026-08-03\nClaimed Amount: $3,258.67",
        encoding="utf-8",
    )
    store.save(CaseRecord(id=case_id, name="Test packet", documents=[invoice, claim]))

    result = engine.process(case_id)

    assert result.status == CaseStatus.NEEDS_REVIEW
    assert result.progress == 100
    assert {document.kind for document in result.documents} == {"invoice", "claim_form"}
    assert {field.key for field in result.fields} >= {
        "person_name",
        "invoice_number",
        "claim_number",
        "total_amount",
        "claimed_amount",
    }
    amount_check = next(
        validation for validation in result.validations if validation.title == "Claim amount matches invoice"
    )
    assert amount_check.status == ValidationStatus.PASSED


def test_detects_conflicting_names_and_amounts(tmp_path: Path):
    engine, store, uploads = build_engine(tmp_path)
    case_id = "conflict-case"
    case_dir = uploads / case_id
    case_dir.mkdir()
    documents = [
        DocumentRecord(id="inv", file_name="invoice.txt", media_type="text/plain"),
        DocumentRecord(id="clm", file_name="claim.txt", media_type="text/plain"),
    ]
    (case_dir / "inv.txt").write_text(
        "INVOICE\nName: Alex Chen\nTotal Amount: $100.00", encoding="utf-8"
    )
    (case_dir / "clm.txt").write_text(
        "CLAIM FORM\nName: Jamie Lee\nClaimed Amount: $120.00", encoding="utf-8"
    )
    store.save(CaseRecord(id=case_id, name="Conflict", documents=documents))

    result = engine.process(case_id)

    failed = {check.title for check in result.validations if check.status == ValidationStatus.FAILED}
    assert "Names match across documents" in failed
    assert "Claim amount matches invoice" in failed


def test_normalizes_currency_values_returned_by_a_model(tmp_path: Path):
    engine, _, _ = build_engine(tmp_path)

    fields = engine._extract_fields(
        "invoice",
        "",
        {
            "kind": "invoice",
            "fields": [
                {
                    "key": "total_amount",
                    "label": "Total",
                    "value": "$3,258.67 USD",
                    "confidence": 0.98,
                    "source_quote": "Total $3,258.67 USD",
                }
            ],
        },
    )

    assert fields[0].value == 3258.67


def test_procurement_three_way_demo_is_deterministic(tmp_path: Path, monkeypatch):
    engine, store, uploads = build_engine(tmp_path)
    engine.provider.settings.ai_provider = "ollama"
    expected = load_recipe("three-way-match")
    case_id = "procurement-demo"
    case_dir = uploads / case_id
    case_dir.mkdir()
    samples = [
        (
            DocumentRecord(
                id=f"document-{index}", file_name=file_name, media_type="text/plain"
            ),
            content,
        )
        for index, (file_name, content) in enumerate(load_recipe_documents("three-way-match"))
    ]
    for document, content in samples:
        (case_dir / f"{document.id}.txt").write_text(content, encoding="utf-8")
    store.save(
        CaseRecord(
            id=case_id,
            name="Three-way match",
            documents=[document for document, _ in samples],
            metadata={"processing_mode": "rules-only"},
        )
    )

    def fail_if_model_is_called(*_args, **_kwargs):
        raise AssertionError("The deterministic demo must not call an AI provider")

    monkeypatch.setattr(engine.provider, "extract", fail_if_model_is_called)
    result = engine.process(case_id)

    assert result.metadata["engine"] == "deterministic-rules"
    assert {document.file_name: document.kind for document in result.documents} == {
        item["file_name"]: item["kind"] for item in expected["documents"]
    }
    assert {field.key: field.value for field in result.fields} == expected["merged_fields"]
    assert {validation.title: validation.status.value for validation in result.validations} == {
        item["title"]: item["status"] for item in expected["initial_validation"]["checks"]
    }
