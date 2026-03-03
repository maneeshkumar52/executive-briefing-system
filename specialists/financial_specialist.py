import time
import structlog
from shared.models import CompanyData, SpecialistAnalysis
from .base_specialist import BaseSpecialist

logger = structlog.get_logger()

FINANCIAL_SYSTEM_PROMPT = """You are a Chief Financial Officer reviewing quarterly performance data. Provide a concise financial analysis covering:
- Revenue performance vs targets and YoY growth
- Margin trends (gross, operating, EBITDA)
- Cash flow quality and sustainability
- Key financial risks and opportunities
- 3-4 specific, data-backed findings

Write in board-level language. Be direct and data-driven. Limit to 250 words."""


class FinancialSpecialist(BaseSpecialist):
    def __init__(self) -> None:
        super().__init__("Financial Performance Analyst")

    async def analyse(self, data: CompanyData) -> SpecialistAnalysis:
        start = time.monotonic()
        f = data.financial
        user_prompt = (
            f"Analyse this financial performance for {f.period}:\n"
            f"- Revenue: ${f.quarterly_revenue_usd_millions:.1f}M (+{f.yoy_revenue_growth_pct:.1f}% YoY)\n"
            f"- Gross Margin: {f.gross_margin_pct:.1f}%\n"
            f"- Operating Margin: {f.operating_margin_pct:.1f}%\n"
            f"- EBITDA: ${f.ebitda_usd_millions:.1f}M\n"
            f"- Free Cash Flow: ${f.free_cash_flow_usd_millions:.1f}M\n"
            f"- CapEx: ${f.capex_usd_millions:.1f}M\n"
            f"- Cost Growth: {f.yoy_cost_growth_pct:.1f}% YoY"
        )

        analysis = await self._call_llm(FINANCIAL_SYSTEM_PROMPT, user_prompt)
        findings = self._extract_key_findings(analysis)

        risk_flags: list[str] = []
        if f.operating_margin_pct < 20.0:
            risk_flags.append("Operating margin below 20% threshold")
        if f.yoy_cost_growth_pct > f.yoy_revenue_growth_pct:
            risk_flags.append(
                "Cost growth exceeds revenue growth — margin compression risk"
            )

        return SpecialistAnalysis(
            specialist_name=self.specialist_name,
            key_findings=findings
            if findings
            else [
                f"Revenue of ${f.quarterly_revenue_usd_millions:.1f}M shows {f.yoy_revenue_growth_pct:.1f}% YoY growth",
                f"Operating margin of {f.operating_margin_pct:.1f}% reflects operational efficiency",
                f"FCF of ${f.free_cash_flow_usd_millions:.1f}M provides strong balance sheet flexibility",
                f"Cost growth of {f.yoy_cost_growth_pct:.1f}% vs revenue growth of {f.yoy_revenue_growth_pct:.1f}%",
            ],
            analysis_text=analysis,
            confidence_score=0.88,
            risk_flags=risk_flags,
            processing_time_seconds=time.monotonic() - start,
        )
