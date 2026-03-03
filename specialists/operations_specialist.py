import time
import structlog
from shared.models import CompanyData, SpecialistAnalysis
from .base_specialist import BaseSpecialist

logger = structlog.get_logger()

OPERATIONS_SYSTEM_PROMPT = """You are a Chief Operations Officer reviewing operational health metrics. Provide a concise operational analysis covering:
- Platform reliability and SLA performance
- Incident management effectiveness
- Deployment velocity and engineering productivity
- Infrastructure cost efficiency
- 3-4 specific, data-backed findings

Write in board-level language. Be direct and data-driven. Limit to 250 words."""


class OperationsSpecialist(BaseSpecialist):
    def __init__(self) -> None:
        super().__init__("Operational Health Analyst")

    async def analyse(self, data: CompanyData) -> SpecialistAnalysis:
        start = time.monotonic()
        o = data.operational

        user_prompt = (
            f"Analyse this operational performance for the quarter:\n"
            f"- System Uptime: {o.system_uptime_pct:.2f}%\n"
            f"- SLA Compliance: {o.sla_compliance_pct:.1f}%\n"
            f"- Total Incidents: {o.incidents_this_quarter}\n"
            f"- Critical Incidents: {o.critical_incidents}\n"
            f"- Mean Time to Recover: {o.mean_time_to_recover_hours:.1f} hours\n"
            f"- Deployment Frequency: {o.deployment_frequency_per_week:.1f} per week\n"
            f"- Customer-Facing Outage: {o.customer_facing_outages_minutes:.0f} minutes\n"
            f"- Infrastructure Cost: ${o.infrastructure_cost_usd_millions:.1f}M"
        )

        analysis = await self._call_llm(OPERATIONS_SYSTEM_PROMPT, user_prompt)
        findings = self._extract_key_findings(analysis)

        risk_flags: list[str] = []
        if o.system_uptime_pct < 99.9:
            risk_flags.append(
                f"System uptime {o.system_uptime_pct:.2f}% below 99.9% SLA target"
            )
        if o.critical_incidents > 0:
            risk_flags.append(
                f"{o.critical_incidents} critical incident(s) this quarter require root cause analysis"
            )
        if o.sla_compliance_pct < 99.0:
            risk_flags.append(
                f"SLA compliance at {o.sla_compliance_pct:.1f}% below 99% contractual threshold"
            )

        return SpecialistAnalysis(
            specialist_name=self.specialist_name,
            key_findings=findings
            if findings
            else [
                f"System uptime {o.system_uptime_pct:.2f}% — slightly below 99.9% target by {99.9 - o.system_uptime_pct:.2f}pp",
                f"{o.critical_incidents} critical incidents require executive attention and post-mortem review",
                f"Deployment frequency of {o.deployment_frequency_per_week:.0f}/week demonstrates healthy engineering velocity",
                f"Infrastructure cost of ${o.infrastructure_cost_usd_millions:.1f}M requires optimisation review",
            ],
            analysis_text=analysis,
            confidence_score=0.90,
            risk_flags=risk_flags,
            processing_time_seconds=time.monotonic() - start,
        )
