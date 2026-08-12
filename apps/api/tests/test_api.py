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
