import re
from uuid import uuid4

from .models import CaseRecord, ValidationResult, ValidationStatus
from .recipes import RecipeDefinition


def evaluate_recipe(case: CaseRecord, recipe: RecipeDefinition) -> list[ValidationResult]:
    """Evaluate the supported declarative rule set against one processed case."""
    results: list[ValidationResult] = []
    for rule in recipe.rules:
        operator, payload = next(iter(rule.assertion.items()))
        if operator == "includes_all_document_kinds":
            results.append(_document_kinds_result(case, rule.id, rule.title, payload))
        elif operator == "all_equal":
            results.append(_all_equal_result(case, rule.id, rule.title, payload))
        elif operator == "less_than_or_equal":
            results.append(_less_than_or_equal_result(case, rule.id, rule.title, payload))
    return results


def _document_kinds_result(
    case: CaseRecord, rule_id: str, title: str, required_kinds: list[str]
) -> ValidationResult:
    present = {document.kind for document in case.documents}
    missing = [kind for kind in required_kinds if kind not in present]
    return ValidationResult(
        id=_result_id(rule_id),
        title=title,
        status=ValidationStatus.FAILED if missing else ValidationStatus.PASSED,
        message=(
            f"Missing required document kinds: {', '.join(missing)}."
            if missing
            else f"All required document kinds are present: {', '.join(required_kinds)}."
        ),
    )


def _all_equal_result(
    case: CaseRecord, rule_id: str, title: str, payload: dict
) -> ValidationResult:
    field_key = payload["field"]
    across = payload["across"]
    normalization = payload.get("normalization", "trim_casefold_whitespace")
    values: list[tuple[str, object]] = []
    missing: list[str] = []
    for kind in across:
        document = next((item for item in case.documents if item.kind == kind), None)
        field = (
            next((item for item in document.fields if item.key == field_key), None)
            if document
            else None
        )
        if not field or field.value in (None, ""):
            missing.append(kind)
        else:
            values.append((kind, field.value))

    normalized = {_normalize(value, normalization) for _, value in values}
    matches = not missing and len(normalized) == 1
    evidence = "; ".join(f"{kind}={value}" for kind, value in values)
    if missing:
        message = f"Missing {field_key} in: {', '.join(missing)}."
    elif matches:
        message = f"Values match across {len(values)} documents: {values[0][1]}."
    else:
        message = f"Conflicting values: {evidence}."
    return ValidationResult(
        id=_result_id(rule_id),
        title=title,
        status=ValidationStatus.PASSED if matches else ValidationStatus.FAILED,
        message=message,
        related_fields=[field_key],
    )


def _less_than_or_equal_result(
    case: CaseRecord, rule_id: str, title: str, payload: dict
) -> ValidationResult:
    related_fields: list[str] = []
    left = _evaluate_numeric_expression(case, payload["left"], related_fields)
    right = _evaluate_numeric_expression(case, payload["right"], related_fields)
    if left is None or right is None:
        status = ValidationStatus.FAILED
        message = f"Could not evaluate required numeric fields: {', '.join(dict.fromkeys(related_fields))}."
    else:
        status = ValidationStatus.PASSED if left <= right + 0.001 else ValidationStatus.FAILED
        message = f"Compared {left:g} ≤ {right:g}."
    return ValidationResult(
        id=_result_id(rule_id),
        title=title,
        status=status,
        message=message,
        related_fields=list(dict.fromkeys(related_fields)),
    )


def _evaluate_numeric_expression(
    case: CaseRecord, expression: str | dict, related_fields: list[str]
) -> float | None:
    if isinstance(expression, str):
        related_fields.append(expression)
        field = next((item for item in case.fields if item.key == expression), None)
        if not field or field.value in (None, ""):
            return None
        match = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(field.value))
        return float(match.group(0).replace(",", "")) if match else None
    values = [
        _evaluate_numeric_expression(case, factor, related_fields)
        for factor in expression["multiply"]
    ]
    if any(value is None for value in values):
        return None
    product = 1.0
    for value in values:
        product *= value or 0
    return product


def _normalize(value: object, strategy: str) -> str:
    text = str(value).strip().casefold()
    if strategy == "lowercase_alphanumeric":
        return re.sub(r"[^a-z0-9]", "", text)
    return re.sub(r"\s+", " ", text)


def _result_id(rule_id: str) -> str:
    return f"{rule_id[:28]}-{uuid4().hex[:8]}"
