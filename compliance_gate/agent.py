import structlog
from openai import AsyncAzureOpenAI
from shared.config import get_openai_client, get_settings
from shared.models import BriefingRequest, ComplianceResult, SynthesisResult

logger = structlog.get_logger()

REQUIRED_DISCLAIMERS = [
    "Confidential — For C-Suite Distribution Only",
    "Past performance is not indicative of future results",
    "This briefing contains forward-looking statements subject to material risks",
]

COMPLIANCE_SYSTEM_PROMPT = """You are a Corporate Compliance Officer reviewing an executive briefing document.

Check the provided executive summary for the following compliance issues:
1. Forward-looking statements made without appropriate hedging language (e.g., "will" vs "is expected to")
2. Language that guarantees financial outcomes or promises specific returns
3. Overly speculative claims not supported by stated data
4. Inappropriate language for C-suite distribution (hyperbolic, sensational, or legally risky phrasing)
5. Missing attribution for third-party data or projections

Respond in this exact format:
ISSUES: [comma-separated list of issues found, or "None" if no issues]
NOTES: [brief reviewer commentary, max 100 words]
APPROVED: [YES or NO — NO only if there are critical legal or regulatory compliance failures]
"""

COMPLIANCE_USER_TEMPLATE = """Review this executive briefing summary for compliance:

---
{executive_summary}
---

Provide your compliance assessment."""


class ComplianceGate:
    """Reviews synthesised briefings for compliance before C-suite distribution."""

    def __init__(self) -> None:
        self.client: AsyncAzureOpenAI = get_openai_client()
        self.settings = get_settings()

    async def review(
        self,
        synthesis: SynthesisResult,
        request: BriefingRequest,
    ) -> ComplianceResult:
        logger.info("compliance_gate.reviewing", requester=request.requester)

        # Rule-based pre-checks
        issues = self._rule_based_checks(synthesis)

        # LLM-based review of the executive summary
        llm_notes, llm_issues, approved = await self._llm_review(
            synthesis.executive_summary
        )

        # Merge issues
        all_issues = list(set(issues + llm_issues))

        # Compliance is only blocked on critical issues
        final_approved = approved and len(
            [i for i in all_issues if "critical" in i.lower() or "guarantee" in i.lower()]
        ) == 0

        logger.info(
            "compliance_gate.complete",
            approved=final_approved,
            issue_count=len(all_issues),
        )

        return ComplianceResult(
            approved=final_approved,
            issues=all_issues,
            required_disclaimers=REQUIRED_DISCLAIMERS,
            reviewer_notes=llm_notes,
        )

    def _rule_based_checks(self, synthesis: SynthesisResult) -> list[str]:
        """Apply deterministic rule-based compliance checks."""
        issues: list[str] = []
        text_to_check = synthesis.executive_summary.lower()

        guaranteed_outcome_phrases = [
            "will guarantee",
            "guaranteed to",
            "certain to",
            "definitely will",
            "100% certain",
        ]
        for phrase in guaranteed_outcome_phrases:
            if phrase in text_to_check:
                issues.append(
                    f"Guaranteed outcome language detected: '{phrase}' — replace with hedged phrasing"
                )

        forward_looking_triggers = ["will grow", "will achieve", "will deliver", "will increase"]
        for phrase in forward_looking_triggers:
            if phrase in text_to_check:
                issues.append(
                    f"Unhedged forward-looking statement detected: '{phrase}' — add appropriate qualifier"
                )

        return issues

    async def _llm_review(
        self, executive_summary: str
    ) -> tuple[str, list[str], bool]:
        """Use LLM to perform nuanced compliance review."""
        if not executive_summary:
            return "No executive summary provided for review.", [], True

        try:
            user_prompt = COMPLIANCE_USER_TEMPLATE.format(
                executive_summary=executive_summary
            )
            response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": COMPLIANCE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=300,
            )
            raw = response.choices[0].message.content or ""
            return self._parse_llm_response(raw)
        except Exception as e:
            logger.warning("compliance_gate.llm_unavailable", error=str(e))
            return (
                f"LLM review unavailable ({type(e).__name__}). Rule-based checks applied only.",
                [],
                True,
            )

    def _parse_llm_response(
        self, raw: str
    ) -> tuple[str, list[str], bool]:
        """Parse structured LLM compliance response."""
        issues: list[str] = []
        notes = "Compliance review completed."
        approved = True

        for line in raw.split("\n"):
            line = line.strip()
            if line.startswith("ISSUES:"):
                issues_text = line[len("ISSUES:"):].strip()
                if issues_text.lower() != "none" and issues_text:
                    issues = [i.strip() for i in issues_text.split(",") if i.strip()]
            elif line.startswith("NOTES:"):
                notes = line[len("NOTES:"):].strip()
            elif line.startswith("APPROVED:"):
                approved_text = line[len("APPROVED:"):].strip().upper()
                approved = approved_text == "YES"

        return notes, issues, approved
