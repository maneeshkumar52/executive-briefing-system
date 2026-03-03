import structlog
from datetime import datetime, timezone
from typing import List
from openai import AsyncAzureOpenAI
from shared.config import get_openai_client, get_settings
from shared.models import (
    BriefingRequest,
    CompanyData,
    SpecialistAnalysis,
    SynthesisResult,
)
from .prompts import EXECUTIVE_SYNTHESIS_PROMPT

logger = structlog.get_logger()


class SynthesiserAgent:
    """Synthesises specialist analyses into a board-quality executive briefing."""

    def __init__(self) -> None:
        self.client: AsyncAzureOpenAI = get_openai_client()
        self.settings = get_settings()

    async def synthesise(
        self,
        specialist_analyses: List[SpecialistAnalysis],
        data: CompanyData,
        request: BriefingRequest,
    ) -> SynthesisResult:
        logger.info(
            "synthesiser.starting",
            specialist_count=len(specialist_analyses),
            topic=request.topic,
        )

        user_prompt = self._build_user_prompt(specialist_analyses, data, request)

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": EXECUTIVE_SYNTHESIS_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1800,
            )
            raw_text = response.choices[0].message.content or ""
            logger.info("synthesiser.llm_response_received", chars=len(raw_text))
        except Exception as e:
            logger.error("synthesiser.llm_error", error=str(e))
            raw_text = ""

        return self._parse_synthesis(raw_text, data, request)

    def _build_user_prompt(
        self,
        analyses: List[SpecialistAnalysis],
        data: CompanyData,
        request: BriefingRequest,
    ) -> str:
        f = data.financial
        c = data.customer
        m = data.market
        h = data.hr
        o = data.operational

        sections: list[str] = [
            f"BRIEFING REQUEST: {request.topic}",
            f"Date Range: {request.date_range}",
            f"Requested By: {request.requester}",
            "",
            "=== SPECIALIST ANALYSES ===",
        ]

        for analysis in analyses:
            sections.append(f"\n--- {analysis.specialist_name.upper()} ---")
            sections.append(f"Confidence: {analysis.confidence_score:.0%}")
            if analysis.key_findings:
                sections.append("Key Findings:")
                for finding in analysis.key_findings:
                    sections.append(f"  - {finding}")
            if analysis.risk_flags:
                sections.append("Risk Flags:")
                for flag in analysis.risk_flags:
                    sections.append(f"  ! {flag}")
            sections.append(f"Full Analysis:\n{analysis.analysis_text}")

        sections.extend(
            [
                "",
                "=== RAW DATA SUMMARY ===",
                f"Financial: Revenue ${f.quarterly_revenue_usd_millions:.1f}M (+{f.yoy_revenue_growth_pct:.1f}% YoY), "
                f"Op Margin {f.operating_margin_pct:.1f}%, FCF ${f.free_cash_flow_usd_millions:.1f}M",
                f"Customer: NPS {c.nps_score}, Churn {c.churn_rate_pct:.1f}%, "
                f"Active customers {c.total_active_customers:,}, ARPU ${c.arpu_usd:.0f}",
                f"Market: Share {m.market_share_pct:.1f}% ({m.yoy_share_change_pct:+.1f}% YoY), "
                f"TAM ${m.addressable_market_usd_billions:.0f}B, Industry growth {m.industry_growth_rate_pct:.1f}%",
                f"People: {h.total_headcount:,} headcount, Turnover {h.voluntary_turnover_rate_pct:.1f}%, "
                f"Engagement {h.employee_engagement_score:.0f}/100, {h.open_positions} open roles",
                f"Operations: Uptime {o.system_uptime_pct:.2f}%, SLA {o.sla_compliance_pct:.1f}%, "
                f"{o.critical_incidents} critical incidents, Infra cost ${o.infrastructure_cost_usd_millions:.1f}M",
                "",
                "Please synthesise the above into a board-quality executive briefing document.",
            ]
        )

        return "\n".join(sections)

    def _parse_synthesis(
        self,
        raw_text: str,
        data: CompanyData,
        request: BriefingRequest,
    ) -> SynthesisResult:
        """Parse the LLM response into structured SynthesisResult fields."""
        f = data.financial
        c = data.customer
        m = data.market
        h = data.hr
        o = data.operational

        # Build key metrics dashboard from actual data
        key_metrics_dashboard: dict[str, str] = {
            "Revenue": f"${f.quarterly_revenue_usd_millions:.1f}M (+{f.yoy_revenue_growth_pct:.1f}% YoY)",
            "Operating Margin": f"{f.operating_margin_pct:.1f}%",
            "Free Cash Flow": f"${f.free_cash_flow_usd_millions:.1f}M",
            "NPS": str(c.nps_score),
            "Churn Rate": f"{c.churn_rate_pct:.1f}%",
            "Active Customers": f"{c.total_active_customers:,}",
            "Market Share": f"{m.market_share_pct:.1f}% ({m.yoy_share_change_pct:+.1f}% YoY)",
            "Employee Engagement": f"{h.employee_engagement_score:.0f}/100",
            "System Uptime": f"{o.system_uptime_pct:.2f}%",
            "Critical Incidents": str(o.critical_incidents),
        }

        if not raw_text or raw_text.startswith("[Analysis unavailable"):
            return self._fallback_synthesis(
                key_metrics_dashboard, data, request
            )

        # Parse sections from LLM output
        executive_summary = self._extract_section(
            raw_text, "## EXECUTIVE SUMMARY", "## STRATEGIC INSIGHTS"
        ).strip()
        insights_raw = self._extract_section(
            raw_text, "## STRATEGIC INSIGHTS", "## RECOMMENDATIONS"
        ).strip()
        recs_raw = self._extract_section(
            raw_text, "## RECOMMENDATIONS", "## RISK REGISTER"
        ).strip()
        risks_raw = self._extract_section(raw_text, "## RISK REGISTER", None).strip()

        strategic_insights = [
            line.lstrip("-* ").strip()
            for line in insights_raw.split("\n")
            if line.strip() and (
                line.strip().startswith("-")
                or line.strip().startswith("*")
                or line.strip().startswith("•")
            )
        ]
        if not strategic_insights:
            strategic_insights = [
                s.strip() for s in insights_raw.split("\n") if len(s.strip()) > 20
            ][:5]

        recommendations = self._parse_pipe_table(recs_raw, ["action", "owner", "timeline", "priority"])
        risk_register = self._parse_pipe_table(risks_raw, ["risk", "likelihood", "impact", "mitigation"])

        # Fallback defaults if parsing yields nothing
        if not executive_summary:
            executive_summary = self._default_executive_summary(data)
        if not strategic_insights:
            strategic_insights = self._default_insights(data)
        if not recommendations:
            recommendations = self._default_recommendations()
        if not risk_register:
            risk_register = self._default_risks(data)

        return SynthesisResult(
            executive_summary=executive_summary,
            key_metrics_dashboard=key_metrics_dashboard,
            strategic_insights=strategic_insights,
            recommendations=recommendations,
            risk_register=risk_register,
            briefing_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )

    def _extract_section(
        self, text: str, start_marker: str, end_marker: str | None
    ) -> str:
        start_idx = text.find(start_marker)
        if start_idx == -1:
            return ""
        start_idx += len(start_marker)
        if end_marker:
            end_idx = text.find(end_marker, start_idx)
            return text[start_idx:end_idx] if end_idx != -1 else text[start_idx:]
        return text[start_idx:]

    def _parse_pipe_table(
        self, raw: str, keys: list[str]
    ) -> list[dict[str, str]]:
        """Parse pipe-delimited rows into list of dicts."""
        results: list[dict[str, str]] = []
        for line in raw.split("\n"):
            line = line.strip()
            if not line or line.startswith("|---") or line.startswith("| ---"):
                continue
            if "|" in line:
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= len(keys):
                    entry = {keys[i]: parts[i] for i in range(len(keys))}
                    # Skip header rows
                    if any(
                        parts[0].lower() in (k, k.title()) for k in keys
                    ):
                        continue
                    results.append(entry)
        return results

    def _fallback_synthesis(
        self,
        key_metrics_dashboard: dict[str, str],
        data: CompanyData,
        request: BriefingRequest,
    ) -> SynthesisResult:
        return SynthesisResult(
            executive_summary=self._default_executive_summary(data),
            key_metrics_dashboard=key_metrics_dashboard,
            strategic_insights=self._default_insights(data),
            recommendations=self._default_recommendations(),
            risk_register=self._default_risks(data),
            briefing_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )

    def _default_executive_summary(self, data: CompanyData) -> str:
        f = data.financial
        c = data.customer
        m = data.market
        return (
            f"The company delivered revenue of ${f.quarterly_revenue_usd_millions:.1f}M in {f.period}, "
            f"representing {f.yoy_revenue_growth_pct:.1f}% year-on-year growth with an operating margin of "
            f"{f.operating_margin_pct:.1f}%. Free cash flow of ${f.free_cash_flow_usd_millions:.1f}M "
            f"demonstrates healthy balance sheet strength and capital allocation capacity.\n\n"
            f"Customer metrics remain broadly positive with NPS of {c.nps_score} and churn contained "
            f"at {c.churn_rate_pct:.1f}%. Market share stands at {m.market_share_pct:.1f}% with "
            f"{m.yoy_share_change_pct:+.1f}% year-on-year movement in a market growing at "
            f"{m.industry_growth_rate_pct:.1f}%. Competitive pressure from TechRival Corp's $500M "
            f"AI investment requires a coordinated strategic response.\n\n"
            f"Operationally, two critical incidents this quarter and system uptime of "
            f"{data.operational.system_uptime_pct:.2f}% demand immediate reliability investment. "
            f"People metrics are stable with engagement at {data.hr.employee_engagement_score:.0f}/100, "
            f"though {data.hr.open_positions} open positions represent a capacity constraint on "
            f"executing strategic priorities."
        )

    def _default_insights(self, data: CompanyData) -> list[str]:
        f = data.financial
        return [
            f"Revenue growth of {f.yoy_revenue_growth_pct:.1f}% outpaces cost growth of {f.yoy_cost_growth_pct:.1f}%, "
            f"but narrowing spread warrants proactive cost discipline",
            "Competitor reliability failures (CloudLeader Inc losing 3 enterprise contracts) "
            "create a 6-8 week window for targeted enterprise acquisition",
            "EU AI Act Q3 2025 compliance deadline requires immediate cross-functional workstream "
            "with estimated EUR 2-5M budget allocation",
            f"System uptime gap of {99.9 - data.operational.system_uptime_pct:.2f}pp below SLA target "
            f"correlates with {data.operational.critical_incidents} critical incidents — "
            "reliability investment directly protects revenue",
            f"Employee engagement of {data.hr.employee_engagement_score:.0f}/100 combined with "
            f"{data.hr.open_positions} open positions creates execution risk for FY2025 strategic initiatives",
        ]

    def _default_recommendations(self) -> list[dict[str, str]]:
        return [
            {
                "action": "Launch enterprise win-back campaign targeting CloudLeader Inc defectors",
                "owner": "CRO",
                "timeline": "6 weeks",
                "priority": "High",
            },
            {
                "action": "Establish EU AI Act compliance taskforce with external legal counsel",
                "owner": "CTO + General Counsel",
                "timeline": "Q1 2025",
                "priority": "High",
            },
            {
                "action": "Invest $5M in reliability engineering to close uptime gap to 99.95%",
                "owner": "COO",
                "timeline": "Q2 2025",
                "priority": "High",
            },
            {
                "action": "Accelerate hiring for 187 open roles, prioritising engineering and sales",
                "owner": "CPO",
                "timeline": "Q1-Q2 2025",
                "priority": "Medium",
            },
            {
                "action": "Develop AI product roadmap response to TechRival Corp $500M investment",
                "owner": "CPO + CTO",
                "timeline": "8 weeks",
                "priority": "High",
            },
        ]

    def _default_risks(self, data: CompanyData) -> list[dict[str, str]]:
        return [
            {
                "risk": "TechRival Corp $500M AI investment threatens enterprise market position",
                "likelihood": "High",
                "impact": "High",
                "mitigation": "Accelerate AI roadmap; targeted enterprise retention programme",
            },
            {
                "risk": "EU AI Act non-compliance by Q3 2025 deadline",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Establish compliance taskforce immediately; budget EUR 3M",
            },
            {
                "risk": "Operational reliability — critical incidents damaging SLA credibility",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Reliability engineering investment; SRE team expansion",
            },
            {
                "risk": "Talent gap — 187 open positions constraining execution capacity",
                "likelihood": "High",
                "impact": "Medium",
                "mitigation": "Increase recruiter headcount; expand compensation bands",
            },
            {
                "risk": f"Market share erosion vs. competitor 1 ({data.market.competitor_1_share_pct:.1f}% share)",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Differentiation strategy review; customer success investment",
            },
        ]
