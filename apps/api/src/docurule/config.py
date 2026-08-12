from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCURULE_", env_file=".env", extra="ignore")

    data_dir: Path = Path("./data")
    max_upload_mb: int = 20
    ai_provider: str = "ollama"
    ai_base_url: str = "http://localhost:11434"
    ai_model: str = "gemma4:latest"
    ai_api_key: str = ""
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    return settings
