import re
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from .models import (
    CaseRecord,
    CaseStatus,
    DocumentRecord,
    DocumentStatus,
    ExtractedField,
    ValidationResult,
    ValidationStatus,
    utc_now,
)
from .provider import AIProvider
from .store import CaseStore


KIND_LABELS = {
    "invoice": "Invoice / receipt",
    "claim_form": "Claim / application form",
    "identity": "Identity document",
    "medical_record": "Medical record",
    "unknown": "Unknown document",
}

FIELD_LABELS = {
    "person_name": "Person name",
    "document_number": "Document number",
    "invoice_number": "Invoice number",
    "claim_number": "Claim number",
    "service_date": "Service date",
    "invoice_date": "Invoice date",
    "total_amount": "Invoice total",
    "claimed_amount": "Claimed amount",
    "issuer": "Issuer",
    "hospital_name": "Hospital",
    "identity_number": "Identity number",
}


class ProcessingEngine:
    def __init__(self, store: CaseStore, provider: AIProvider, uploads_dir: Path) -> None:
        self.store = store
        self.provider = provider
        self.uploads_dir = uploads_dir

    def process(self, case_id: str) -> CaseRecord:
        case = self.store.get(case_id)
        if not case:
            raise KeyError(case_id)
        case.status = CaseStatus.PROCESSING
        case.progress = 8
        case.updated_at = utc_now()
        self.store.save(case)

        ai_used = False
        for index, document in enumerate(case.documents):
            try:
                path = self.uploads_dir / case.id / f"{document.id}{Path(document.file_name).suffix.lower()}"
                text, page_count = self._read_document(path, document.media_type)
                document.page_count = page_count
                image_path = path if document.media_type.startswith("image/") else None
                ai_result = self.provider.extract(text, image_path=image_path)
                ai_used = ai_used or ai_result is not None
                document.kind = self._classify(document.file_name, text, ai_result)
                document.kind_label = KIND_LABELS[document.kind]
                document.fields = self._extract_fields(document.id, text, ai_result)
                document.status = DocumentStatus.PROCESSED
            except Exception as exc:
                document.status = DocumentStatus.FAILED
                document.error = str(exc)
            case.progress = 15 + round(60 * (index + 1) / max(len(case.documents), 1))
            case.updated_at = utc_now()
            self.store.save(case)

        try:
            case.fields = self._merge_fields(case.documents)
            case.validations = self._validate(case)
            case.status = CaseStatus.NEEDS_REVIEW
            case.metadata["engine"] = "ai+rules" if ai_used else "rules-fallback"
        except Exception as exc:
            case.status = CaseStatus.FAILED
            case.metadata["processing_error"] = str(exc)
        case.progress = 100
        case.updated_at = utc_now()
        return self.store.save(case)

    def revalidate(self, case: CaseRecord) -> CaseRecord:
        """Re-run deterministic validations after a reviewer correction."""
        case.validations = self._validate(case)
        case.updated_at = utc_now()
        return self.store.save(case)

    @staticmethod
    def _read_document(path: Path, media_type: str) -> tuple[str, int]:
        if media_type == "application/pdf" or path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages)
        if media_type.startswith("text/") or path.suffix.lower() in {".txt", ".md", ".csv"}:
            return path.read_text(encoding="utf-8", errors="ignore"), 1
        if media_type.startswith("image/"):
            return "", 1
        raise ValueError(f"Unsupported file type: {media_type or path.suffix}")

    @staticmethod
    def _classify(file_name: str, text: str, ai_result: dict | None) -> str:
        if ai_result and ai_result.get("kind") in KIND_LABELS:
            return ai_result["kind"]
        value = f"{file_name}\n{text}".lower()
        rules = [
            ("claim_form", ("claim form", "claim number", "申请表", "理赔申请")),
            ("invoice", ("invoice", "receipt", "发票", "收据", "total amount")),
            ("identity", ("identity", "passport", "身份证", "证件号码")),
            ("medical_record", ("medical record", "diagnosis", "病历", "诊断")),
        ]
        for kind, tokens in rules:
            if any(token in value for token in tokens):
                return kind
        return "unknown"

    def _extract_fields(
        self, document_id: str, text: str, ai_result: dict | None
    ) -> list[ExtractedField]:
        fields: list[ExtractedField] = []
        if ai_result:
            for item in ai_result.get("fields", []):
                key = self._normalize_key(str(item.get("key", "")))
                value = self._coerce_value(key, item.get("value"))
                if key and value not in (None, ""):
                    fields.append(
                        ExtractedField(
                            key=key,
                            label=str(item.get("label") or FIELD_LABELS.get(key, key.replace("_", " ").title())),
                            value=value,
                            confidence=min(max(float(item.get("confidence", 0.75)), 0), 1),
                            source_document_id=document_id,
                            source_quote=str(item.get("source_quote", ""))[:240] or None,
                        )
                    )
        existing = {field.key for field in fields}
        for key, label, patterns in self._regex_definitions():
            if key in existing:
                continue
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    raw = match.group(1).strip().rstrip(".,")
                    value: str | float = raw
                    if key in {"total_amount", "claimed_amount"}:
                        value = float(raw.replace(",", ""))
                    quote_start = max(0, match.start() - 24)
                    quote_end = min(len(text), match.end() + 24)
                    fields.append(
                        ExtractedField(
                            key=key,
                            label=label,
                            value=value,
                            confidence=0.93,
                            source_document_id=document_id,
                            source_quote=" ".join(text[quote_start:quote_end].split()),
                        )
                    )
                    break
        return fields

    @staticmethod
    def _coerce_value(key: str, value: object) -> object:
        if key not in {"total_amount", "claimed_amount"} or value in (None, ""):
            return value
        match = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(value))
        if not match:
            return value
        return float(match.group(0).replace(",", ""))

    @staticmethod
    def _normalize_key(value: str) -> str:
        key = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
        aliases = {"name": "person_name", "amount": "total_amount", "date": "service_date"}
        return aliases.get(key, key)

    @staticmethod
    def _regex_definitions() -> list[tuple[str, str, tuple[str, ...]]]:
        boundary = r"[^\n\r]{0,60}"
        return [
            ("person_name", "Person name", (r"(?:patient|person|full\s*name|name|姓名)\s*[:：]\s*([^\n\r]+)",)),
            ("invoice_number", "Invoice number", (r"(?:invoice\s*(?:no\.?|number)|发票号码)\s*[:：#]?\s*([A-Z0-9-]+)",)),
            ("claim_number", "Claim number", (r"(?:claim\s*(?:no\.?|number)|理赔号)\s*[:：#]?\s*([A-Z0-9-]+)",)),
            ("identity_number", "Identity number", (r"(?:identity\s*(?:no\.?|number)|身份证号|证件号码)\s*[:：#]?\s*([A-Z0-9-]+)",)),
            ("invoice_date", "Invoice date", (r"(?:invoice\s*date|开票日期)\s*[:：]?\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",)),
            ("service_date", "Service date", (r"(?:service\s*date|visit\s*date|就诊日期|服务日期)\s*[:：]?\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",)),
            ("total_amount", "Invoice total", (rf"(?:total\s*amount|amount\s*due|合计金额|总金额){boundary}?[:：¥$\s]\s*([\d,]+(?:\.\d{{1,2}})?)",)),
            ("claimed_amount", "Claimed amount", (rf"(?:claimed\s*amount|claim\s*amount|申请金额|理赔金额){boundary}?[:：¥$\s]\s*([\d,]+(?:\.\d{{1,2}})?)",)),
            ("hospital_name", "Hospital", (r"(?:hospital|医院)\s*[:：]\s*([^\n\r]+)",)),
            ("issuer", "Issuer", (r"(?:issuer|issued\s*by|开具方)\s*[:：]\s*([^\n\r]+)",)),
        ]

    @staticmethod
    def _merge_fields(documents: list[DocumentRecord]) -> list[ExtractedField]:
        best: dict[str, ExtractedField] = {}
        for document in documents:
            for field in document.fields:
                if field.key not in best or field.confidence > best[field.key].confidence:
                    best[field.key] = field.model_copy(deep=True)
        return list(best.values())

    def _validate(self, case: CaseRecord) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        kinds = {document.kind for document in case.documents}
        for kind, label in (("invoice", "Invoice"), ("claim_form", "Claim form")):
            present = kind in kinds
            results.append(
                ValidationResult(
                    id=uuid4().hex[:10],
                    title=f"{label} present",
                    status=ValidationStatus.PASSED if present else ValidationStatus.WARNING,
                    message=f"{label} was classified in this case." if present else f"No {label.lower()} was found.",
                )
            )

        names = self._document_values(case, "person_name")
        if names:
            normalized = {re.sub(r"\s+", "", str(value)).lower() for value in names}
            results.append(
                ValidationResult(
                    id=uuid4().hex[:10],
                    title="Names match across documents",
                    status=ValidationStatus.PASSED if len(normalized) == 1 else ValidationStatus.FAILED,
                    message="All extracted names are consistent." if len(normalized) == 1 else f"Conflicting names: {', '.join(map(str, names))}",
                    related_fields=["person_name"],
                )
            )

        invoice_amount = self._first_value(case, "total_amount")
        claimed_amount = self._first_value(case, "claimed_amount")
        if invoice_amount is not None and claimed_amount is not None:
            invoice_number = self._as_number(invoice_amount)
            claimed_number = self._as_number(claimed_amount)
            if invoice_number is None or claimed_number is None:
                results.append(
                    ValidationResult(
                        id=uuid4().hex[:10],
                        title="Claim amount matches invoice",
                        status=ValidationStatus.WARNING,
                        message="One or both amount values could not be normalized; manual review is required.",
                        related_fields=["total_amount", "claimed_amount"],
                    )
                )
                invoice_number = claimed_number = None
            if invoice_number is not None and claimed_number is not None:
                matches = abs(invoice_number - claimed_number) < 0.01
                results.append(
                    ValidationResult(
                        id=uuid4().hex[:10],
                        title="Claim amount matches invoice",
                        status=ValidationStatus.PASSED if matches else ValidationStatus.FAILED,
                        message=(
                            f"Both documents show {invoice_number:,.2f}."
                            if matches
                            else f"Invoice is {invoice_number:,.2f}; claim is {claimed_number:,.2f}."
                        ),
                        related_fields=["total_amount", "claimed_amount"],
                    )
                )

        low_confidence = [field.label for field in case.fields if field.confidence < 0.75]
        results.append(
            ValidationResult(
                id=uuid4().hex[:10],
                title="Extraction confidence",
                status=ValidationStatus.WARNING if low_confidence else ValidationStatus.PASSED,
                message=(
                    f"Review low-confidence fields: {', '.join(low_confidence)}."
                    if low_confidence
                    else "All surfaced fields meet the 75% confidence threshold."
                ),
            )
        )
        return results

    @staticmethod
    def _document_values(case: CaseRecord, key: str) -> list[str | float | int]:
        return [
            field.value
            for document in case.documents
            for field in document.fields
            if field.key == key and field.value is not None
        ]

    @staticmethod
    def _first_value(case: CaseRecord, key: str) -> str | float | int | None:
        values = ProcessingEngine._document_values(case, key)
        return values[0] if values else None

    @staticmethod
    def _as_number(value: object) -> float | None:
        match = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(value))
        return float(match.group(0).replace(",", "")) if match else None
