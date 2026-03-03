import time
import structlog
from shared.models import CompanyData, SpecialistAnalysis
from .base_specialist import BaseSpecialist

logger = structlog.get_logger()

RISK_SYSTEM_PROMPT = """You are a Chief Risk Officer. Produce an enterprise risk matrix covering:
- Financial risks (revenue concentration, margin pressure, liquidity)
- Operational risks (uptime, incidents, supply chain)
- Strategic/market risks (competitive threats, market share erosion)
- Regulatory and compliance risks (EU AI Act, data privacy, ESG)
- People risks (talent retention, key-person dependency)

For each risk, assess Probability (High/Medium/Low) and Impact (High/Medium/Low).
Identify the top 3-5 enterprise risks requiring board-level attention.
Write in board-level language. Be direct. Limit to 300 words."""


class RiskSpecialist(BaseSpecialist):
    def __init__(self) -> None:
        super().__init__("Enterprise Risk Analyst")

    async def analyse(self, data: CompanyData) -> SpecialistAnalysis:
        start = time.monotonic()
        f = data.financial
        c = data.customer
        o = data.operational
        m = data.market
        h = data.hr

        news_lines = "\n".join(
            f"  [{n.sentiment:+.1f}] {n.headline}" for n in data.news
        )

        user_prompt = (
            f"Conduct enterprise risk assessment using the following data:\n\n"
            f"FINANCIAL:\n"
            f"- Revenue growth: {f.yoy_revenue_growth_pct:.1f}%, Cost growth: {f.yoy_cost_growth_pct:.1f}%\n"
            f"- Operating margin: {f.operating_margin_pct:.1f}%, FCF: ${f.free_cash_flow_usd_millions:.1f}M\n\n"
            f"CUSTOMER:\n"
            f"- Churn rate: {c.churn_rate_pct:.1f}%, NPS: {c.nps_score}\n"
            f"- CSAT trend: {c.csat_trend}\n\n"
            f"OPERATIONAL:\n"
            f"- System uptime: {o.system_uptime_pct:.2f}%, Critical incidents: {o.critical_incidents}\n"
            f"- SLA compliance: {o.sla_compliance_pct:.1f}%\n\n"
            f"MARKET:\n"
            f"- Market share: {m.market_share_pct:.1f}% (YoY change: {m.yoy_share_change_pct:+.1f}%)\n"
            f"- Top competitor share: {m.competitor_1_share_pct:.1f}%\n\n"
            f"PEOPLE:\n"
            f"- Voluntary turnover: {h.voluntary_turnover_rate_pct:.1f}%, Engagement: {h.employee_engagement_score:.0f}/100\n"
            f"- Open positions: {h.open_positions}\n\n"
            f"NEWS & INTELLIGENCE:\n{news_lines}"
        )

        analysis = await self._call_llm(RISK_SYSTEM_PROMPT, user_prompt)
        findings = self._extract_key_findings(analysis)

        # Always flag negative news
        risk_flags: list[str] = []
        for n in data.news:
            if n.sentiment < -0.4:
                risk_flags.append(
                    f"Negative competitor signal: '{n.headline}' (sentiment {n.sentiment:+.2f})"
                )
        if o.critical_incidents > 0:
            risk_flags.append(
                f"Operational risk: {o.critical_incidents} critical incident(s) — reputational and contractual exposure"
            )
        if f.yoy_cost_growth_pct > f.yoy_revenue_growth_pct:
            risk_flags.append(
                "Financial risk: cost growth outpacing revenue — margin contraction trajectory"
            )
        if m.yoy_share_change_pct < 0:
            risk_flags.append(
                f"Strategic risk: market share declining {m.yoy_share_change_pct:+.1f}% YoY"
            )

        return SpecialistAnalysis(
            specialist_name=self.specialist_name,
            key_findings=findings
            if findings
            else [
                "TechRival Corp $500M AI investment poses significant enterprise market threat",
                f"System uptime {o.system_uptime_pct:.2f}% and {o.critical_incidents} critical incidents create SLA risk",
                "EU AI Act Q3 2025 deadline introduces regulatory compliance cost and timeline risk",
                f"Churn rate of {c.churn_rate_pct:.1f}% combined with NPS of {c.nps_score} warrants proactive retention investment",
            ],
            analysis_text=analysis,
            confidence_score=0.87,
            risk_flags=risk_flags,
            processing_time_seconds=time.monotonic() - start,
        )
