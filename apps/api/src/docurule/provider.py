import base64
import json
import re
from pathlib import Path
from typing import Any

import httpx

from .config import Settings
from .models import ProviderStatus


SYSTEM_PROMPT = """You extract auditable structured data from business documents.
Return JSON only with this exact shape:
{"kind":"invoice|claim_form|identity|medical_record|unknown","fields":[
{"key":"snake_case_key","label":"Human label","value":"value","confidence":0.0,
"source_quote":"short exact quote from document"}]}
Never invent a value. Omit any field that is not visible. Useful keys include person_name,
document_number, invoice_number, claim_number, service_date, invoice_date, total_amount,
claimed_amount, issuer, identity_number and hospital_name."""


class AIProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def status(self) -> ProviderStatus:
        if self.settings.ai_provider == "local":
            return ProviderStatus(
                provider="local", model="built-in rules", available=True, detail="Rules-only mode"
            )
        try:
            if self.settings.ai_provider == "ollama":
                response = httpx.get(f"{self.settings.ai_base_url.rstrip('/')}/api/tags", timeout=2)
            else:
                response = httpx.get(
                    f"{self.settings.ai_base_url.rstrip('/')}/models",
                    headers=self._headers(),
                    timeout=2,
                )
            response.raise_for_status()
            return ProviderStatus(
                provider=self.settings.ai_provider,
                model=self.settings.ai_model,
                available=True,
                detail="Connected",
            )
        except Exception:
            return ProviderStatus(
                provider=self.settings.ai_provider,
                model=self.settings.ai_model,
                available=False,
                detail="Unavailable; processing falls back to built-in rules",
            )

    def extract(self, text: str, image_path: Path | None = None) -> dict[str, Any] | None:
        if self.settings.ai_provider == "local":
            return None
        user_content = "Extract this document.\n\n" + text[:16000]
        try:
            if self.settings.ai_provider == "ollama":
                message: dict[str, Any] = {"role": "user", "content": user_content}
                if image_path:
                    message["images"] = [base64.b64encode(image_path.read_bytes()).decode()]
                response = httpx.post(
                    f"{self.settings.ai_base_url.rstrip('/')}/api/chat",
                    json={
                        "model": self.settings.ai_model,
                        "stream": False,
                        "format": "json",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            message,
                        ],
                        "options": {"temperature": 0},
                    },
                    timeout=90,
                )
                response.raise_for_status()
                raw = response.json()["message"]["content"]
            else:
                content: list[dict[str, Any]] = [{"type": "text", "text": user_content}]
                if image_path:
                    mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
                    encoded = base64.b64encode(image_path.read_bytes()).decode()
                    content.append(
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}
                    )
                response = httpx.post(
                    f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                    headers=self._headers(),
                    json={
                        "model": self.settings.ai_model,
                        "temperature": 0,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": content},
                        ],
                    },
                    timeout=90,
                )
                response.raise_for_status()
                raw = response.json()["choices"][0]["message"]["content"]
            return json.loads(self._strip_fence(raw))
        except Exception:
            return None

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.settings.ai_api_key}"} if self.settings.ai_api_key else {}

    @staticmethod
    def _strip_fence(value: str) -> str:
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", value.strip(), flags=re.IGNORECASE)
