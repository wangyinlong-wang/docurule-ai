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


def test_upload_accepted_file():
    response = client.post(
        "/api/v1/cases",
        files=[("files", ("document.pdf", b"%PDF-1.4 test content", "application/pdf"))],
        data={"name": "Test PDF upload", "process": "false"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test PDF upload"
    assert len(data["documents"]) == 1
    assert data["documents"][0]["file_name"] == "document.pdf"
    assert data["documents"][0]["media_type"] == "application/pdf"


def test_upload_rejected_file():
    response = client.post(
        "/api/v1/cases",
        files=[("files", ("payload.exe", b"\x7fELF...", "application/x-executable"))],
        data={"name": "Test bad upload", "process": "false"},
    )
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]

