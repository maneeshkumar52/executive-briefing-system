import time
import structlog
from abc import ABC, abstractmethod
from openai import AsyncAzureOpenAI
from shared.config import get_openai_client, get_settings
from shared.models import CompanyData, SpecialistAnalysis

logger = structlog.get_logger()


class BaseSpecialist(ABC):
    def __init__(self, specialist_name: str):
        self.specialist_name = specialist_name
        self.client: AsyncAzureOpenAI = get_openai_client()
        self.settings = get_settings()

    @abstractmethod
    async def analyse(self, data: CompanyData) -> SpecialistAnalysis:
        pass

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=600,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(
                "specialist.llm_error",
                specialist=self.specialist_name,
                error=str(e),
            )
            return f"[Analysis unavailable due to: {type(e).__name__}]"

    def _extract_key_findings(
        self, text: str, max_findings: int = 4
    ) -> list[str]:
        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
            and (
                line.strip().startswith("-")
                or line.strip().startswith("*")
                or line.strip().startswith("•")
            )
        ]
        findings = [line.lstrip("-*• ") for line in lines[:max_findings]]
        if not findings:
            sentences = [
                s.strip() for s in text.split(".") if len(s.strip()) > 20
            ]
            findings = sentences[:3]
        return findings
