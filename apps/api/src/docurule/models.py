from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CaseStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class DocumentStatus(StrEnum):
    QUEUED = "queued"
    PROCESSED = "processed"
    FAILED = "failed"


class ValidationStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class ExtractedField(BaseModel):
    key: str
    label: str
    value: str | float | int | None = None
    confidence: float = Field(default=0.0, ge=0, le=1)
    source_document_id: str | None = None
    source_quote: str | None = None
    reviewed: bool = False


class DocumentRecord(BaseModel):
    id: str
    file_name: str
    media_type: str
    kind: str = "unknown"
    kind_label: str = "Unknown document"
    status: DocumentStatus = DocumentStatus.QUEUED
    size_bytes: int = 0
    page_count: int = 1
    fields: list[ExtractedField] = Field(default_factory=list)
    error: str | None = None


class ValidationResult(BaseModel):
    id: str
    title: str
    status: ValidationStatus
    message: str
    related_fields: list[str] = Field(default_factory=list)


class CaseRecord(BaseModel):
    id: str
    name: str
    status: CaseStatus = CaseStatus.UPLOADED
    decision: str | None = None
    progress: int = Field(default=0, ge=0, le=100)
    documents: list[DocumentRecord] = Field(default_factory=list)
    fields: list[ExtractedField] = Field(default_factory=list)
    validations: list[ValidationResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class FieldUpdate(BaseModel):
    value: str | float | int | None
    reviewed: bool = True


class ReviewRequest(BaseModel):
    decision: str
    note: str = ""


class ProviderStatus(BaseModel):
    provider: str
    model: str
    available: bool
    detail: str
