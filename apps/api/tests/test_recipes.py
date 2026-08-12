import pytest

from docurule.config import Settings
from docurule.engine import ProcessingEngine
from docurule.models import CaseRecord, DocumentRecord, ValidationStatus
from docurule.provider import AIProvider
from docurule.recipes import RecipeError, load_recipe_definition, parse_recipe_yaml
from docurule.store import CaseStore


def test_bundled_recipe_matches_the_executable_contract():
    recipe = load_recipe_definition("three-way-match")

    assert recipe.id == "procurement-three-way-match"
    assert len(recipe.documents) == 3
    assert len(recipe.rules) == 6


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        (
            """schema_version: 1
id: unsafe-recipe
title: Unsafe
documents:
  - kind: invoice
    file: ../invoice.txt
rules:
  - id: present-rule
    title: Present
    assertion:
      includes_all_document_kinds: [invoice]
""",
            "unsafe document file name",
        ),
        (
            """schema_version: 1
id: unsupported-rule
title: Unsupported
documents:
  - kind: invoice
    file: invoice.txt
rules:
  - id: run_shell
    title: Never executable
    assertion:
      python: __import__('os')
""",
            "unsupported assertion operator",
        ),
        (
            "!!python/object/apply:os.system ['echo unsafe']",
            "invalid YAML",
        ),
        (
            """schema_version: 1
id: duplicate-key
id: hidden-key
title: Duplicate
documents: [{kind: invoice, file: invoice.txt}]
rules:
  - id: packet_present
    title: Present
    assertion: {includes_all_document_kinds: [invoice]}
""",
            "invalid YAML",
        ),
        (
            """schema_version: 1
id: alias-recipe
title: Alias
documents: &documents [{kind: invoice, file: invoice.txt}]
rules:
  - id: packet_present
    title: Present
    assertion:
      includes_all_document_kinds: *documents
""",
            "aliases are not supported",
        ),
        (
            """schema_version: 1
id: duplicate-kind
title: Duplicate kind
documents:
  - {kind: invoice, file: invoice-a.txt}
  - {kind: invoice, file: invoice-b.txt}
rules:
  - id: packet_present
    title: Present
    assertion: {includes_all_document_kinds: [invoice]}
""",
            "one document per kind",
        ),
    ],
)
def test_rejects_unsafe_or_unsupported_recipe_yaml(yaml_text: str, message: str):
    with pytest.raises(RecipeError, match=message):
        parse_recipe_yaml(yaml_text.encode())


def test_executes_a_recipe_with_custom_document_kinds(tmp_path):
    recipe = parse_recipe_yaml(
        b"""schema_version: 1
id: custom-packet
title: Custom packet
documents:
  - {kind: vendor_quote, file: quote.txt}
rules:
  - id: packet_present
    title: Quote is present
    assertion: {includes_all_document_kinds: [vendor_quote]}
"""
    )
    uploads = tmp_path / "uploads"
    case_dir = uploads / "custom-case"
    case_dir.mkdir(parents=True)
    (case_dir / "quote.txt").write_text("Supplier: Northstar", encoding="utf-8")
    store = CaseStore(tmp_path / "test.sqlite3")
    store.save(
        CaseRecord(
            id="custom-case",
            name="Custom",
            documents=[
                DocumentRecord(
                    id="quote", file_name="quote.txt", media_type="text/plain"
                )
            ],
            metadata={
                "processing_mode": "rules-only",
                "recipe": recipe.model_dump(mode="json"),
            },
        )
    )
    engine = ProcessingEngine(
        store,
        AIProvider(Settings(data_dir=tmp_path, ai_provider="local")),
        uploads,
    )

    result = engine.process("custom-case")

    assert result.documents[0].status == "processed"
    assert result.documents[0].kind == "vendor_quote"
    assert result.documents[0].kind_label == "Vendor Quote"
    assert result.validations[0].status == ValidationStatus.PASSED


def test_rejects_unhashable_yaml_mapping_keys():
    with pytest.raises(RecipeError, match="invalid YAML"):
        parse_recipe_yaml(b"? [nested, key]\n: value\n")
