import json
import mimetypes
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import get_settings
from .engine import ProcessingEngine
from .models import CaseRecord, CaseStatus, DocumentRecord, FieldUpdate, ReviewRequest, utc_now
from .provider import AIProvider
from .store import CaseStore

settings = get_settings()
store = CaseStore(settings.data_dir / "docurule.sqlite3")
provider = AIProvider(settings)
engine = ProcessingEngine(store, provider, settings.uploads_dir)

app = FastAPI(
    title="DocuRule AI API",
    version=__version__,
    description="Extract, validate and review documents with an auditable evidence trail.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/v1/provider")
def provider_status():
    return provider.status()


@app.get("/api/v1/cases", response_model=list[CaseRecord])
def list_cases():
    return store.list()


@app.get("/api/v1/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str):
    return _require_case(case_id)


@app.post("/api/v1/cases", response_model=CaseRecord, status_code=201)
async def create_case(
    background_tasks: BackgroundTasks,
    name: str = Form(default="Untitled review"),
    files: list[UploadFile] = File(...),
    process: bool = Form(default=True),
):
    if not files:
        raise HTTPException(400, "Upload at least one document")
    case_id = uuid4().hex[:12]
    target_dir = settings.uploads_dir / case_id
    target_dir.mkdir(parents=True, exist_ok=True)
    documents: list[DocumentRecord] = []
    max_bytes = settings.max_upload_mb * 1024 * 1024

    for upload in files:
        content = await upload.read(max_bytes + 1)
        if len(content) > max_bytes:
            shutil.rmtree(target_dir, ignore_errors=True)
            raise HTTPException(413, f"{upload.filename} exceeds {settings.max_upload_mb} MB")
        document_id = uuid4().hex[:10]
        safe_name = Path(upload.filename or "document").name
        suffix = Path(safe_name).suffix.lower()
        media_type = upload.content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        (target_dir / f"{document_id}{suffix}").write_bytes(content)
        documents.append(
            DocumentRecord(
                id=document_id,
                file_name=safe_name,
                media_type=media_type,
                size_bytes=len(content),
            )
        )

    case = store.save(CaseRecord(id=case_id, name=name.strip() or "Untitled review", documents=documents))
    if process:
        background_tasks.add_task(engine.process, case.id)
    return case


@app.post("/api/v1/demo", response_model=CaseRecord, status_code=201)
def create_demo(background_tasks: BackgroundTasks):
    case_id = uuid4().hex[:12]
    target_dir = settings.uploads_dir / case_id
    target_dir.mkdir(parents=True, exist_ok=True)
    samples = [
        (
            "medical-invoice.txt",
            """MEDICAL INVOICE\nInvoice Number: INV-2026-0812\nPatient Name: Alex Chen\nHospital: Riverside Medical Center\nService Date: 2026-08-03\nInvoice Date: 2026-08-04\nTotal Amount: $3,258.67\nStatus: Paid\n""",
        ),
        (
            "claim-form.txt",
            """HEALTH CLAIM FORM\nClaim Number: CLM-260812-07\nFull Name: Alex Chen\nService Date: 2026-08-03\nClaimed Amount: $3,258.67\nIdentity Number: ID-8842-1937\nDeclaration: I confirm this claim is accurate.\n""",
        ),
    ]
    documents = []
    for file_name, content in samples:
        document_id = uuid4().hex[:10]
        (target_dir / f"{document_id}.txt").write_text(content, encoding="utf-8")
        documents.append(
            DocumentRecord(
                id=document_id,
                file_name=file_name,
                media_type="text/plain",
                size_bytes=len(content.encode()),
            )
        )
    case = store.save(CaseRecord(id=case_id, name="Medical claim · Demo", documents=documents))
    background_tasks.add_task(engine.process, case.id)
    return case


@app.post("/api/v1/cases/{case_id}/process", response_model=CaseRecord)
def process_case(case_id: str, background_tasks: BackgroundTasks):
    case = _require_case(case_id)
    background_tasks.add_task(engine.process, case.id)
    case.status = CaseStatus.PROCESSING
    case.progress = 5
    case.updated_at = utc_now()
    return store.save(case)


@app.patch("/api/v1/cases/{case_id}/fields/{field_key}", response_model=CaseRecord)
def update_field(case_id: str, field_key: str, update: FieldUpdate):
    case = _require_case(case_id)
    field = next((item for item in case.fields if item.key == field_key), None)
    if not field:
        raise HTTPException(404, "Field not found")
    field.value = update.value
    field.reviewed = update.reviewed
    field.confidence = 1.0 if update.reviewed else field.confidence
    for document in case.documents:
        for document_field in document.fields:
            if document_field.key == field_key and document_field.source_document_id == field.source_document_id:
                document_field.value = update.value
                document_field.reviewed = update.reviewed
                document_field.confidence = field.confidence
    case.metadata.setdefault("audit_log", []).append(
        {
            "action": "field_updated",
            "field": field_key,
            "value": update.value,
            "at": utc_now().isoformat(),
        }
    )
    return engine.revalidate(case)


@app.post("/api/v1/cases/{case_id}/review", response_model=CaseRecord)
def review_case(case_id: str, review: ReviewRequest):
    case = _require_case(case_id)
    decision = review.decision.lower()
    if decision not in {"approved", "rejected"}:
        raise HTTPException(422, "Decision must be approved or rejected")
    case.decision = decision
    case.status = CaseStatus.APPROVED if decision == "approved" else CaseStatus.REJECTED
    case.metadata["review_note"] = review.note
    case.metadata.setdefault("audit_log", []).append(
        {
            "action": "review_decision",
            "decision": decision,
            "note": review.note,
            "at": utc_now().isoformat(),
        }
    )
    case.updated_at = utc_now()
    return store.save(case)


@app.get("/api/v1/cases/{case_id}/export")
def export_case(case_id: str):
    case = _require_case(case_id)
    payload = json.loads(case.model_dump_json())
    return JSONResponse(
        payload,
        headers={"Content-Disposition": f'attachment; filename="docurule-{case.id}.json"'},
    )


@app.get("/api/v1/cases/{case_id}/documents/{document_id}")
def download_document(case_id: str, document_id: str):
    case = _require_case(case_id)
    document = next((item for item in case.documents if item.id == document_id), None)
    if not document:
        raise HTTPException(404, "Document not found")
    suffix = Path(document.file_name).suffix.lower()
    path = settings.uploads_dir / case_id / f"{document_id}{suffix}"
    if not path.exists():
        raise HTTPException(404, "Stored file not found")
    return FileResponse(path, media_type=document.media_type, filename=document.file_name)


def _require_case(case_id: str) -> CaseRecord:
    case = store.get(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


static_candidates = [Path("/app/static"), Path(__file__).resolve().parents[3] / "web" / "dist"]
static_dir = next((candidate for candidate in static_candidates if (candidate / "index.html").exists()), None)
if static_dir:
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        target = static_dir / path
        if path and target.is_file():
            return FileResponse(target)
        return FileResponse(static_dir / "index.html")
