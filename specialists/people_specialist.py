import time
import structlog
from shared.models import CompanyData, SpecialistAnalysis
from .base_specialist import BaseSpecialist

logger = structlog.get_logger()

PEOPLE_SYSTEM_PROMPT = """You are a Chief People Officer reviewing talent and organisational health metrics. Provide a concise people analysis covering:
- Talent acquisition and retention performance
- Employee engagement and culture indicators
- Workforce capacity and capability gaps
- Key people risks and opportunities
- 3-4 specific, data-backed findings

Write in board-level language. Be direct and data-driven. Limit to 250 words."""


class PeopleSpecialist(BaseSpecialist):
    def __init__(self) -> None:
        super().__init__("People & Talent Analyst")

    async def analyse(self, data: CompanyData) -> SpecialistAnalysis:
        start = time.monotonic()
        h = data.hr

        user_prompt = (
            f"Analyse this workforce performance for the quarter:\n"
            f"- Total Headcount: {h.total_headcount:,}\n"
            f"- New Hires This Quarter: {h.new_hires_this_quarter}\n"
            f"- Voluntary Turnover Rate: {h.voluntary_turnover_rate_pct:.1f}%\n"
            f"- Involuntary Turnover Rate: {h.involuntary_turnover_rate_pct:.1f}%\n"
            f"- Offer Acceptance Rate: {h.offer_acceptance_rate_pct:.1f}%\n"
            f"- Employee Engagement Score: {h.employee_engagement_score:.0f}/100\n"
            f"- Training Hours per Employee: {h.training_hours_per_employee:.1f} hours\n"
            f"- Open Positions: {h.open_positions}"
        )

        analysis = await self._call_llm(PEOPLE_SYSTEM_PROMPT, user_prompt)
        findings = self._extract_key_findings(analysis)

        risk_flags: list[str] = []
        if h.voluntary_turnover_rate_pct > 12.0:
            risk_flags.append(
                f"Voluntary turnover at {h.voluntary_turnover_rate_pct:.1f}% exceeds 12% risk threshold"
            )
        if h.employee_engagement_score < 65.0:
            risk_flags.append(
                f"Engagement score {h.employee_engagement_score:.0f}/100 below 65-point floor — culture intervention needed"
            )
        if h.offer_acceptance_rate_pct < 80.0:
            risk_flags.append(
                f"Offer acceptance rate {h.offer_acceptance_rate_pct:.1f}% below 80% benchmark — EVP review required"
            )

        return SpecialistAnalysis(
            specialist_name=self.specialist_name,
            key_findings=findings
            if findings
            else [
                f"Voluntary turnover of {h.voluntary_turnover_rate_pct:.1f}% is within manageable range but warrants monitoring",
                f"Engagement score of {h.employee_engagement_score:.0f}/100 reflects stable culture, room to improve to 75+",
                f"{h.open_positions} open positions represent {h.open_positions / h.total_headcount * 100:.1f}% vacancy rate — hiring pressure",
                f"Offer acceptance rate of {h.offer_acceptance_rate_pct:.1f}% indicates competitive employer branding",
            ],
            analysis_text=analysis,
            confidence_score=0.85,
            risk_flags=risk_flags,
            processing_time_seconds=time.monotonic() - start,
        )
