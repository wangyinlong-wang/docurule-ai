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
from .recipes import RecipeDefinition
from .rule_engine import evaluate_recipe
from .store import CaseStore


KIND_LABELS = {
    "purchase_order": "Purchase order",
    "invoice": "Invoice / receipt",
    "delivery_note": "Delivery note",
    "claim_form": "Claim / application form",
    "identity": "Identity document",
    "medical_record": "Medical record",
    "unknown": "Unknown document",
}

FIELD_LABELS = {
    "supplier_name": "Supplier",
    "po_number": "PO number",
    "currency": "Currency",
    "ordered_quantity": "Ordered quantity",
    "invoiced_quantity": "Invoiced quantity",
    "received_quantity": "Received quantity",
    "unit_price": "Unit price",
    "invoice_total": "Invoice total",
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
        rules_only = case.metadata.get("processing_mode") == "rules-only"
        recipe = self._recipe_definition(case)
        declared_kinds = (
            {document.file: document.kind for document in recipe.documents} if recipe else {}
        )
        for index, document in enumerate(case.documents):
            try:
                path = self.uploads_dir / case.id / f"{document.id}{Path(document.file_name).suffix.lower()}"
                text, page_count = self._read_document(path, document.media_type)
                document.page_count = page_count
                image_path = path if document.media_type.startswith("image/") else None
                ai_result = None if rules_only else self.provider.extract(text, image_path=image_path)
                ai_used = ai_used or ai_result is not None
                document.kind = declared_kinds.get(document.file_name) or self._classify(
                    document.file_name, text, ai_result
                )
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
            case.metadata["engine"] = (
                "deterministic-rules"
                if rules_only
                else "ai+rules"
                if ai_used
                else "rules-fallback"
            )
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
            (
                "delivery_note",
                ("delivery note", "goods received note", "receiving report", "收货单", "送货单"),
            ),
            ("purchase_order", ("purchase order", "采购订单", "采购单")),
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
                    if key in {
                        "total_amount",
                        "claimed_amount",
                        "ordered_quantity",
                        "invoiced_quantity",
                        "received_quantity",
                        "unit_price",
                        "invoice_total",
                    }:
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
        numeric_keys = {
            "total_amount",
            "claimed_amount",
            "ordered_quantity",
            "invoiced_quantity",
            "received_quantity",
            "unit_price",
            "invoice_total",
        }
        if key not in numeric_keys or value in (None, ""):
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
            ("supplier_name", "Supplier", (r"(?:supplier(?:\s*name)?|vendor)\s*[:：]\s*([^\n\r]+)",)),
            (
                "po_number",
                "PO number",
                (
                    r"(?:purchase[ \t]*order|p\.?o\.?)"
                    r"[ \t]*(?:no\.?|number|#)[ \t]*[:：#]?[ \t]*([A-Z0-9-]+)",
                ),
            ),
            ("currency", "Currency", (r"(?:currency|币种)\s*[:：]\s*([A-Z]{3})",)),
            ("ordered_quantity", "Ordered quantity", (r"(?:ordered\s*(?:quantity|qty)|order\s*qty|订购数量)\s*[:：]?\s*([\d,]+(?:\.\d+)?)",)),
            ("invoiced_quantity", "Invoiced quantity", (r"(?:invoiced\s*(?:quantity|qty)|invoice\s*qty|开票数量)\s*[:：]?\s*([\d,]+(?:\.\d+)?)",)),
            ("received_quantity", "Received quantity", (r"(?:received\s*(?:quantity|qty)|receipt\s*qty|收货数量)\s*[:：]?\s*([\d,]+(?:\.\d+)?)",)),
            (
                "unit_price",
                "Unit price",
                (r"(?:unit\s*price|单价)\s*[:：]?\s*[¥$]?\s*([\d,]+(?:\.\d{1,4})?)",),
            ),
            (
                "invoice_total",
                "Invoice total",
                (r"(?:invoice\s*total|发票总额)\s*[:：]?\s*[¥$]?\s*([\d,]+(?:\.\d{1,2})?)",),
            ),
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
        recipe = self._recipe_definition(case)
        if recipe:
            return evaluate_recipe(case, recipe)
        kinds = {document.kind for document in case.documents}
        if kinds & {"purchase_order", "delivery_note"}:
            return self._validate_procurement(case)

        results: list[ValidationResult] = []
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
    def _recipe_definition(case: CaseRecord) -> RecipeDefinition | None:
        payload = case.metadata.get("recipe")
        return RecipeDefinition.model_validate(payload) if isinstance(payload, dict) else None

    def _validate_procurement(self, case: CaseRecord) -> list[ValidationResult]:
        """Run the deterministic three-way match checks used by procurement packets."""
        results: list[ValidationResult] = []
        kinds = {document.kind for document in case.documents}
        required_kinds = {"purchase_order", "invoice", "delivery_note"}
        packet_complete = required_kinds.issubset(kinds)
        missing_labels = [KIND_LABELS[kind] for kind in required_kinds - kinds]
        results.append(
            ValidationResult(
                id=uuid4().hex[:10],
                title="Three-way document set complete",
                status=ValidationStatus.PASSED if packet_complete else ValidationStatus.FAILED,
                message=(
                    "Purchase order, invoice, and delivery note are all present."
                    if packet_complete
                    else f"Missing: {', '.join(sorted(missing_labels))}."
                ),
            )
        )

        results.append(
            self._matching_values_result(
                case,
                key="supplier_name",
                title="Supplier matches across documents",
                success_message="All three documents name the same supplier.",
                minimum_values=3,
            )
        )
        results.append(
            self._matching_values_result(
                case,
                key="po_number",
                title="PO number matches across documents",
                success_message="All three documents reference the same purchase order.",
                minimum_values=3,
                compact=True,
            )
        )
        results.append(
            self._matching_values_result(
                case,
                key="currency",
                title="Currency matches across documents",
                success_message="All three documents use the same currency.",
                minimum_values=3,
                compact=True,
            )
        )

        invoiced_quantity = self._as_number(self._first_value(case, "invoiced_quantity"))
        received_quantity = self._as_number(self._first_value(case, "received_quantity"))
        quantity_matches = (
            invoiced_quantity is not None
            and received_quantity is not None
            and invoiced_quantity <= received_quantity
        )
        results.append(
            ValidationResult(
                id=uuid4().hex[:10],
                title="Invoiced quantity does not exceed received quantity",
                status=ValidationStatus.PASSED if quantity_matches else ValidationStatus.FAILED,
                message=(
                    f"Invoiced {invoiced_quantity:g}; received {received_quantity:g}."
                    if invoiced_quantity is not None and received_quantity is not None
                    else "Invoiced or received quantity is missing."
                ),
                related_fields=["invoiced_quantity", "received_quantity"],
            )
        )

        invoice_total = self._as_number(self._first_value(case, "invoice_total"))
        unit_price = self._as_number(self._first_value(case, "unit_price"))
        received_value = (
            received_quantity * unit_price
            if received_quantity is not None and unit_price is not None
            else None
        )
        amount_matches = (
            invoice_total is not None
            and received_value is not None
            and invoice_total <= received_value + 0.001
        )
        results.append(
            ValidationResult(
                id=uuid4().hex[:10],
                title="Invoice total does not exceed received value",
                status=ValidationStatus.PASSED if amount_matches else ValidationStatus.FAILED,
                message=(
                    f"Invoice total is {invoice_total:,.2f}; received value is {received_value:,.2f}."
                    if invoice_total is not None and received_value is not None
                    else "Invoice total, received quantity, or unit price is missing."
                ),
                related_fields=["invoice_total", "received_quantity", "unit_price"],
            )
        )
        return results

    def _matching_values_result(
        self,
        case: CaseRecord,
        *,
        key: str,
        title: str,
        success_message: str,
        minimum_values: int,
        compact: bool = False,
    ) -> ValidationResult:
        values = self._document_values(case, key)
        normalized = {
            (re.sub(r"[^a-z0-9]", "", str(value).lower()) if compact else re.sub(r"\s+", " ", str(value).strip().lower()))
            for value in values
        }
        matches = len(values) >= minimum_values and len(normalized) == 1
        return ValidationResult(
            id=uuid4().hex[:10],
            title=title,
            status=ValidationStatus.PASSED if matches else ValidationStatus.FAILED,
            message=(
                success_message
                if matches
                else f"Expected matching values from all three documents; found: {', '.join(map(str, values)) or 'none'}."
            ),
            related_fields=[key],
        )

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
