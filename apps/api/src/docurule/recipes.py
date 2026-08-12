import json
from functools import lru_cache
from pathlib import Path
from typing import Any


class RecipeError(RuntimeError):
    """Raised when a bundled recipe is missing or malformed."""


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
    """Load and minimally validate a bundled recipe manifest."""
    recipe_dir = _recipe_directory(recipe_id)
    try:
        payload = json.loads((recipe_dir / "expected-result.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecipeError(f"Unable to load bundled recipe: {recipe_id}") from exc

    if payload.get("recipe_id") != recipe_id or not isinstance(payload.get("documents"), list):
        raise RecipeError(f"Invalid bundled recipe manifest: {recipe_id}")
    return payload


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
