from fastapi.testclient import TestClient

from docurule.main import app
from docurule.recipes import load_recipe


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
