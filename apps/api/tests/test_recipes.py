import pytest

from docurule.recipes import RecipeError, load_recipe_definition, parse_recipe_yaml


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
