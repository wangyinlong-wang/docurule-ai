import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from yaml.constructor import ConstructorError
from yaml.events import AliasEvent
from yaml.nodes import MappingNode


MAX_RECIPE_BYTES = 128 * 1024
MAX_RECIPE_DOCUMENTS = 20
MAX_RECIPE_RULES = 50
RECIPE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
RULE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
FIELD_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
DOCUMENT_KIND_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
NORMALIZATIONS = {"trim_casefold_whitespace", "lowercase_alphanumeric"}


class RecipeError(RuntimeError):
    """Raised when a recipe is missing, malformed, or outside the supported contract."""


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that fails closed on duplicate mapping keys."""

    def construct_mapping(self, node: MappingNode, deep: bool = False):
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key: {key}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


class RecipeDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str
    file: str
    required: bool = True


class RecipeFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required: list[str] = Field(default_factory=list)
    numeric: list[str] = Field(default_factory=list)


class RecipeRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    assertion: dict[str, Any]


class RecipeDefinition(BaseModel):
    """Safe, deliberately small schema for executable document-packet rules."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    id: str
    title: str
    description: str = ""
    processing_mode: Literal["rules-only"] = "rules-only"
    documents: list[RecipeDocument] = Field(min_length=1, max_length=MAX_RECIPE_DOCUMENTS)
    fields: RecipeFields = Field(default_factory=RecipeFields)
    rules: list[RecipeRule] = Field(min_length=1, max_length=MAX_RECIPE_RULES)

    @model_validator(mode="after")
    def validate_contract(self):
        if not RECIPE_ID_PATTERN.fullmatch(self.id):
            raise ValueError("recipe id must use 2-64 lowercase letters, numbers, or hyphens")
        if not self.title.strip() or len(self.title) > 120:
            raise ValueError("recipe title must contain 1-120 characters")
        if len(self.description) > 500:
            raise ValueError("recipe description must not exceed 500 characters")

        files: set[str] = set()
        kinds: set[str] = set()
        for document in self.documents:
            if Path(document.file).name != document.file or document.file in {".", ".."}:
                raise ValueError(f"unsafe document file name: {document.file}")
            if document.file in files:
                raise ValueError(f"duplicate document file: {document.file}")
            if not DOCUMENT_KIND_PATTERN.fullmatch(document.kind):
                raise ValueError(f"invalid document kind: {document.kind}")
            if document.kind in kinds:
                raise ValueError(f"schema v1 requires one document per kind: {document.kind}")
            files.add(document.file)
            kinds.add(document.kind)

        for field_key in [*self.fields.required, *self.fields.numeric]:
            _validate_field_key(field_key)

        rule_ids: set[str] = set()
        for rule in self.rules:
            if not RULE_ID_PATTERN.fullmatch(rule.id):
                raise ValueError(f"invalid rule id: {rule.id}")
            if rule.id in rule_ids:
                raise ValueError(f"duplicate rule id: {rule.id}")
            if not rule.title.strip() or len(rule.title) > 160:
                raise ValueError(f"invalid title for rule: {rule.id}")
            _validate_assertion(rule.assertion, kinds)
            rule_ids.add(rule.id)
        return self


def _validate_field_key(value: object) -> str:
    if not isinstance(value, str) or not FIELD_KEY_PATTERN.fullmatch(value):
        raise ValueError(f"invalid field key: {value}")
    return value


def _validate_kind_list(value: object, kinds: set[str], rule_name: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{rule_name} must contain a non-empty list of document kinds")
    unknown = sorted(set(value) - kinds)
    if unknown:
        raise ValueError(f"{rule_name} references undeclared document kinds: {', '.join(unknown)}")
    return value


def _validate_value_expression(value: object) -> None:
    if isinstance(value, str):
        _validate_field_key(value)
        return
    if not isinstance(value, dict) or set(value) != {"multiply"}:
        raise ValueError("numeric expressions support only field keys or multiply")
    factors = value["multiply"]
    if not isinstance(factors, list) or len(factors) < 2 or len(factors) > 8:
        raise ValueError("multiply must contain between 2 and 8 factors")
    for factor in factors:
        _validate_value_expression(factor)


def _validate_assertion(assertion: object, kinds: set[str]) -> None:
    if not isinstance(assertion, dict) or len(assertion) != 1:
        raise ValueError("each rule assertion must contain exactly one supported operator")
    operator, payload = next(iter(assertion.items()))
    if operator == "includes_all_document_kinds":
        _validate_kind_list(payload, kinds, operator)
        return
    if operator == "all_equal":
        if not isinstance(payload, dict) or set(payload) - {"field", "across", "normalization"}:
            raise ValueError("all_equal supports field, across, and normalization")
        _validate_field_key(payload.get("field"))
        _validate_kind_list(payload.get("across"), kinds, "all_equal.across")
        normalization = payload.get("normalization", "trim_casefold_whitespace")
        if normalization not in NORMALIZATIONS:
            raise ValueError(f"unsupported normalization: {normalization}")
        return
    if operator == "less_than_or_equal":
        if not isinstance(payload, dict) or set(payload) != {"left", "right"}:
            raise ValueError("less_than_or_equal requires left and right expressions")
        _validate_value_expression(payload["left"])
        _validate_value_expression(payload["right"])
        return
    raise ValueError(f"unsupported assertion operator: {operator}")


def parse_recipe_yaml(content: bytes) -> RecipeDefinition:
    """Parse an uploaded YAML recipe without constructing arbitrary Python objects."""
    if not content:
        raise RecipeError("Recipe file is empty")
    if len(content) > MAX_RECIPE_BYTES:
        raise RecipeError(f"Recipe file exceeds {MAX_RECIPE_BYTES // 1024} KB")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RecipeError("Recipe file must be UTF-8 YAML") from exc
    try:
        if any(isinstance(event, AliasEvent) for event in yaml.parse(text)):
            raise RecipeError("YAML aliases are not supported")
        payload = yaml.load(text, Loader=UniqueKeySafeLoader)
    except RecipeError:
        raise
    except yaml.YAMLError as exc:
        raise RecipeError("Recipe file contains invalid YAML") from exc
    if not isinstance(payload, dict):
        raise RecipeError("Recipe YAML must contain an object at the top level")
    try:
        return RecipeDefinition.model_validate(payload)
    except ValidationError as exc:
        error = exc.errors(include_url=False, include_input=False)[0]["msg"]
        raise RecipeError(str(error).removeprefix("Value error, ")) from exc


def _recipe_directory(recipe_id: str) -> Path:
    candidates = [Path("/app/demo") / recipe_id]
    source_path = Path(__file__).resolve()
    if len(source_path.parents) > 4:
        candidates.append(source_path.parents[4] / "demo" / recipe_id)
    for candidate in candidates:
        if (candidate / "expected-result.json").is_file():
            return candidate
    raise RecipeError(f"Bundled recipe not found: {recipe_id}")


@lru_cache
def load_recipe(recipe_id: str) -> dict[str, Any]:
    """Load and minimally validate a bundled golden-result manifest."""
    recipe_dir = _recipe_directory(recipe_id)
    try:
        payload = json.loads((recipe_dir / "expected-result.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecipeError(f"Unable to load bundled recipe: {recipe_id}") from exc

    if payload.get("recipe_id") != recipe_id or not isinstance(payload.get("documents"), list):
        raise RecipeError(f"Invalid bundled recipe manifest: {recipe_id}")
    return payload


@lru_cache
def load_recipe_definition(recipe_id: str) -> RecipeDefinition:
    """Load the executable rules contract for a bundled recipe."""
    recipe_dir = _recipe_directory(recipe_id)
    try:
        return parse_recipe_yaml((recipe_dir / "rules.yml").read_bytes())
    except OSError as exc:
        raise RecipeError(f"Missing rules.yml in bundled recipe: {recipe_id}") from exc


def load_recipe_documents(recipe_id: str) -> list[tuple[str, str]]:
    """Return the public synthetic document files declared by a recipe."""
    recipe_dir = _recipe_directory(recipe_id)
    documents: list[tuple[str, str]] = []
    for item in load_recipe(recipe_id)["documents"]:
        file_name = str(item.get("file_name", ""))
        if not file_name or Path(file_name).name != file_name:
            raise RecipeError(f"Unsafe document name in bundled recipe: {recipe_id}")
        try:
            content = (recipe_dir / file_name).read_text(encoding="utf-8")
        except OSError as exc:
            raise RecipeError(f"Missing document {file_name} in bundled recipe: {recipe_id}") from exc
        documents.append((file_name, content))
    return documents
