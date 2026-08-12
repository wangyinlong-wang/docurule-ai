import csv
import io

from fastapi.testclient import TestClient

from docurule.main import app
from docurule.recipes import _recipe_directory, load_recipe


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_accepts_matching_extension_and_media_type():
    response = client.post(
        "/api/v1/cases",
        files=[("files", ("document.pdf", b"%PDF-1.4 synthetic", "application/pdf"))],
        data={"name": "Accepted upload", "process": "false"},
    )

    assert response.status_code == 201
    assert response.json()["documents"][0]["media_type"] == "application/pdf"


def test_upload_rejects_unknown_extension_before_storage():
    response = client.post(
        "/api/v1/cases",
        files=[("files", ("payload.exe", b"synthetic", "application/x-executable"))],
        data={"name": "Rejected upload", "process": "false"},
    )

    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_rejects_extension_media_type_mismatch():
    response = client.post(
        "/api/v1/cases",
        files=[("files", ("disguised.jpg", b"synthetic", "application/pdf"))],
        data={"name": "Mismatched upload", "process": "false"},
    )

    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]


def test_demo_review_flow():
    created = client.post("/api/v1/demo")
    assert created.status_code == 201
    case_id = created.json()["id"]

    review = client.get(f"/api/v1/cases/{case_id}")
    assert review.status_code == 200
    assert review.json()["status"] == "needs_review"
    assert len(review.json()["documents"]) == 2

    corrected = client.patch(
        f"/api/v1/cases/{case_id}/fields/claimed_amount",
        json={"value": "3000.00", "reviewed": True},
    )
    assert corrected.status_code == 200
    amount_check = next(
        item
        for item in corrected.json()["validations"]
        if item["title"] == "Claim amount matches invoice"
    )
    assert amount_check["status"] == "failed"
    assert corrected.json()["metadata"]["audit_log"][0]["action"] == "field_updated"

    approved = client.post(
        f"/api/v1/cases/{case_id}/review",
        json={"decision": "approved", "note": "Looks correct"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["metadata"]["audit_log"][-1]["action"] == "review_decision"

    exported = client.get(f"/api/v1/cases/{case_id}/export")
    assert exported.status_code == 200
    assert exported.json()["decision"] == "approved"


def test_csv_export_has_one_row_per_normalized_field_and_safe_utf8_quoting():
    created = client.post("/api/v1/demo/procurement")
    assert created.status_code == 201
    case_id = created.json()["id"]

    corrected = client.patch(
        f"/api/v1/cases/{case_id}/fields/supplier_name",
        json={"value": "ACME, Inc.\nWest", "reviewed": True},
    )
    assert corrected.status_code == 200

    exported = client.get(f"/api/v1/cases/{case_id}/export", params={"format": "csv"})
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    assert exported.headers["content-disposition"] == f'attachment; filename="docurule-{case_id}.csv"'

    rows = list(csv.DictReader(io.StringIO(exported.content.decode("utf-8-sig"))))
    assert len(rows) == 8
    assert len({row["field_key"] for row in rows}) == 8
    supplier_row = next(row for row in rows if row["field_key"] == "supplier_name")
    assert supplier_row["value"] == "ACME, Inc.\nWest"
    assert supplier_row["reviewed"] == "True"


def test_export_rejects_unknown_format():
    created = client.post("/api/v1/demo")
    assert created.status_code == 201

    response = client.get(
        f"/api/v1/cases/{created.json()['id']}/export", params={"format": "xml"}
    )
    assert response.status_code == 422


def test_procurement_three_way_demo_returns_fixed_exceptions():
    expected = load_recipe("three-way-match")
    created = client.post("/api/v1/demo/procurement")
    assert created.status_code == 201
    case_id = created.json()["id"]
    payload = client.get(f"/api/v1/cases/{case_id}").json()

    assert payload["status"] == "needs_review"
    assert payload["metadata"]["processing_mode"] == "rules-only"
    assert payload["metadata"]["engine"] == "deterministic-rules"
    expected_documents = {item["file_name"]: item for item in expected["documents"]}
    assert {document["file_name"] for document in payload["documents"]} == set(expected_documents)
    for document in payload["documents"]:
        expected_document = expected_documents[document["file_name"]]
        assert document["kind"] == expected_document["kind"]
        actual_fields = {field["key"]: field["value"] for field in document["fields"]}
        assert actual_fields == expected_document["fields"]

    assert {field["key"]: field["value"] for field in payload["fields"]} == expected[
        "merged_fields"
    ]
    expected_checks = {
        item["title"]: item["status"] for item in expected["initial_validation"]["checks"]
    }
    assert {item["title"]: item["status"] for item in payload["validations"]} == expected_checks

    corrected = client.patch(
        f"/api/v1/cases/{case_id}/fields/received_quantity",
        json={"value": expected["review_correction"]["to"], "reviewed": True},
    )
    assert corrected.status_code == 200
    corrected_summary = expected["review_correction"]["expected_summary"]
    assert sum(item["status"] == "passed" for item in corrected.json()["validations"]) == corrected_summary[
        "passed"
    ]
    assert sum(item["status"] == "failed" for item in corrected.json()["validations"]) == corrected_summary[
        "failed"
    ]

    reviewed = client.post(
        f"/api/v1/cases/{case_id}/review",
        json={"decision": "approved", "note": "Quantity confirmed against delivery note."},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "approved"

    exported = client.get(f"/api/v1/cases/{case_id}/export")
    assert exported.status_code == 200
    export_payload = exported.json()
    assert export_payload["decision"] == "approved"
    assert len(export_payload["documents"]) == 3
    assert [event["action"] for event in export_payload["metadata"]["audit_log"]] == [
        "field_updated",
        "review_decision",
    ]


def test_runs_an_uploaded_yaml_recipe_and_revalidates_after_correction():
    recipe_dir = _recipe_directory("three-way-match")
    expected = load_recipe("three-way-match")
    multipart = [
        (
            "recipe",
            ("rules.yml", (recipe_dir / "rules.yml").read_bytes(), "application/x-yaml"),
        )
    ]
    multipart.extend(
        (
            "files",
            (item["file_name"], (recipe_dir / item["file_name"]).read_bytes(), "text/plain"),
        )
        for item in expected["documents"]
    )

    created = client.post(
        "/api/v1/recipes/run",
        data={"name": "Uploaded three-way match"},
        files=multipart,
    )

    assert created.status_code == 201
    payload = client.get(f"/api/v1/cases/{created.json()['id']}").json()
    assert payload["status"] == "needs_review"
    assert payload["metadata"]["recipe_id"] == "procurement-three-way-match"
    assert payload["metadata"]["recipe_source"] == "uploaded"
    assert payload["metadata"]["engine"] == "deterministic-rules"
    assert {item["title"]: item["status"] for item in payload["validations"]} == {
        item["title"]: item["status"] for item in expected["initial_validation"]["checks"]
    }

    corrected = client.patch(
        f"/api/v1/cases/{payload['id']}/fields/received_quantity",
        json={"value": expected["review_correction"]["to"], "reviewed": True},
    )
    assert corrected.status_code == 200
    assert [item["status"] for item in corrected.json()["validations"]] == ["passed"] * 6


def test_recipe_run_rejects_missing_and_undeclared_documents_before_creating_a_case():
    recipe_dir = _recipe_directory("three-way-match")
    before = {item["id"] for item in client.get("/api/v1/cases").json()}
    response = client.post(
        "/api/v1/recipes/run",
        files=[
            (
                "recipe",
                ("rules.yml", (recipe_dir / "rules.yml").read_bytes(), "application/x-yaml"),
            ),
            ("files", ("surprise.txt", b"not declared", "text/plain")),
        ],
    )

    assert response.status_code == 422
    assert "not declared" in response.json()["detail"]
    after = {item["id"] for item in client.get("/api/v1/cases").json()}
    assert after == before


def test_recipe_run_rejects_a_missing_required_document():
    recipe_dir = _recipe_directory("three-way-match")
    response = client.post(
        "/api/v1/recipes/run",
        files=[
            (
                "recipe",
                ("rules.yml", (recipe_dir / "rules.yml").read_bytes(), "application/x-yaml"),
            ),
            (
                "files",
                (
                    "purchase-order-PO-2026-0812.txt",
                    (recipe_dir / "purchase-order-PO-2026-0812.txt").read_bytes(),
                    "application/octet-stream",
                ),
            ),
        ],
    )

    assert response.status_code == 422
    assert "Missing required recipe documents" in response.json()["detail"]


def test_reads_the_bundled_executable_recipe_contract():
    response = client.get("/api/v1/recipes/three-way-match")

    assert response.status_code == 200
    assert response.json()["id"] == "procurement-three-way-match"
    assert len(response.json()["rules"]) == 6


def test_recipe_run_accepts_only_utf8_text_documents():
    recipe_dir = _recipe_directory("three-way-match")
    response = client.post(
        "/api/v1/recipes/run",
        files=[
            (
                "recipe",
                ("rules.yml", (recipe_dir / "rules.yml").read_bytes(), "application/x-yaml"),
            ),
            (
                "files",
                ("purchase-order-PO-2026-0812.txt", b"\xff\xfe", "text/plain"),
            ),
        ],
    )

    assert response.status_code == 415
    assert "UTF-8" in response.json()["detail"]
