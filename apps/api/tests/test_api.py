from fastapi.testclient import TestClient

from docurule.main import app


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
    created = client.post("/api/v1/demo/procurement")
    assert created.status_code == 201
    case_id = created.json()["id"]
    payload = client.get(f"/api/v1/cases/{case_id}").json()

    assert payload["status"] == "needs_review"
    assert payload["metadata"]["processing_mode"] == "rules-only"
    assert payload["metadata"]["engine"] == "deterministic-rules"
    assert {document["kind"] for document in payload["documents"]} == {
        "purchase_order",
        "invoice",
        "delivery_note",
    }
    assert {field["key"] for field in payload["fields"]} >= {
        "supplier_name",
        "po_number",
        "currency",
        "ordered_quantity",
        "invoiced_quantity",
        "received_quantity",
        "unit_price",
        "invoice_total",
    }
    assert len(payload["validations"]) == 6
    assert sum(item["status"] == "passed" for item in payload["validations"]) == 4
    assert sum(item["status"] == "failed" for item in payload["validations"]) == 2

    corrected = client.patch(
        f"/api/v1/cases/{case_id}/fields/received_quantity",
        json={"value": "96", "reviewed": True},
    )
    assert corrected.status_code == 200
    assert sum(item["status"] == "passed" for item in corrected.json()["validations"]) == 6

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
