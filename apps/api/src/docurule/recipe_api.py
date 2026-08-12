import mimetypes
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from .config import Settings
from .engine import ProcessingEngine
from .models import CaseRecord, DocumentRecord
from .recipes import (
    RecipeDefinition,
    RecipeError,
    load_recipe_definition,
    parse_recipe_yaml,
)
from .store import CaseStore


RECIPE_MEDIA_TYPES_BY_SUFFIX = {
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
    ".csv": {
        "text/csv",
        "text/plain",
        "application/vnd.ms-excel",
        "application/octet-stream",
    },
}


@dataclass
class PendingDocument:
    file_name: str
    suffix: str
    media_type: str
    content: bytes
    kind: str


def build_recipe_router(
    settings: Settings, store: CaseStore, engine: ProcessingEngine
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])

    @router.get("/{recipe_id}", response_model=RecipeDefinition)
    def get_bundled_recipe(recipe_id: str):
        try:
            return load_recipe_definition(recipe_id)
        except RecipeError as exc:
            raise HTTPException(404, str(exc)) from exc

    @router.post("/run", response_model=CaseRecord, status_code=201)
    async def run_recipe(
        background_tasks: BackgroundTasks,
        recipe: UploadFile = File(...),
        files: list[UploadFile] = File(...),
        name: str = Form(default=""),
    ):
        recipe_name = recipe.filename or ""
        if Path(recipe_name).suffix.lower() not in {".yml", ".yaml"}:
            raise HTTPException(415, "Recipe must be a .yml or .yaml file")
        try:
            definition = parse_recipe_yaml(await recipe.read())
        except RecipeError as exc:
            raise HTTPException(422, str(exc)) from exc

        pending = await _validate_documents(definition, files, settings.max_upload_mb)
        case_id = uuid4().hex[:12]
        target_dir = settings.uploads_dir / case_id
        target_dir.mkdir(parents=True, exist_ok=False)
        documents: list[DocumentRecord] = []
        try:
            for item in pending:
                document_id = uuid4().hex[:10]
                (target_dir / f"{document_id}{item.suffix}").write_bytes(item.content)
                documents.append(
                    DocumentRecord(
                        id=document_id,
                        file_name=item.file_name,
                        media_type=item.media_type,
                        kind=item.kind,
                        size_bytes=len(item.content),
                    )
                )
        except OSError as exc:
            for path in target_dir.iterdir():
                path.unlink(missing_ok=True)
            target_dir.rmdir()
            raise HTTPException(500, "Unable to store recipe documents") from exc

        case = store.save(
            CaseRecord(
                id=case_id,
                name=name.strip() or definition.title,
                documents=documents,
                metadata={
                    "scenario": f"recipe:{definition.id}",
                    "processing_mode": definition.processing_mode,
                    "recipe_id": definition.id,
                    "recipe_source": "uploaded",
                    "recipe": definition.model_dump(mode="json"),
                },
            )
        )
        background_tasks.add_task(engine.process, case.id)
        return case

    return router


async def _validate_documents(
    definition: RecipeDefinition, uploads: list[UploadFile], max_upload_mb: int
) -> list[PendingDocument]:
    if not uploads:
        raise HTTPException(400, "Upload at least one recipe document")
    declared = {document.file: document for document in definition.documents}
    required = {document.file for document in definition.documents if document.required}
    pending: list[PendingDocument] = []
    seen: set[str] = set()
    max_bytes = max_upload_mb * 1024 * 1024

    for upload in uploads:
        file_name = upload.filename or ""
        if not file_name or Path(file_name).name != file_name:
            raise HTTPException(422, f"Unsafe document file name: {file_name or 'unnamed'}")
        if file_name in seen:
            raise HTTPException(422, f"Duplicate uploaded document: {file_name}")
        document_contract = declared.get(file_name)
        if not document_contract:
            raise HTTPException(422, f"Document is not declared by the recipe: {file_name}")

        suffix = Path(file_name).suffix.lower()
        guessed_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        media_type = upload.content_type or guessed_type
        allowed_media_types = RECIPE_MEDIA_TYPES_BY_SUFFIX.get(suffix, set())
        if media_type not in allowed_media_types:
            raise HTTPException(
                415,
                f"Executable recipes currently accept UTF-8 TXT, Markdown, and CSV documents; "
                f"{file_name} was sent as {media_type}",
            )
        content = await upload.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise HTTPException(413, f"{file_name} exceeds {max_upload_mb} MB")
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(415, f"Recipe document must be UTF-8 text: {file_name}") from exc
        pending.append(
            PendingDocument(
                file_name=file_name,
                suffix=suffix,
                media_type=media_type,
                content=content,
                kind=document_contract.kind,
            )
        )
        seen.add(file_name)

    missing = sorted(required - seen)
    if missing:
        raise HTTPException(422, f"Missing required recipe documents: {', '.join(missing)}")
    return pending
