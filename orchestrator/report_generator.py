from datetime import datetime, timezone
from shared.models import BriefingRequest, BriefingResult


class ReportGenerator:
    """Renders a BriefingResult as a formatted Markdown document."""

    def generate_markdown(
        self, result: BriefingResult, request: BriefingRequest
    ) -> str:
        disclaimers = ""
        if result.compliance and result.compliance.required_disclaimers:
            disclaimers = "\n".join(
                f"> {d}" for d in result.compliance.required_disclaimers
            )

        s = result.synthesis
        lines = [
            f"# EXECUTIVE BRIEFING: {result.topic}",
            f"**Classification:** CONFIDENTIAL",
            f"**Date:** {result.created_at[:10]}",
            f"**Prepared for:** {request.requester}",
            f"**Run ID:** {result.run_id}",
            "",
            disclaimers,
            "",
            "---",
            "",
            "## EXECUTIVE SUMMARY",
            s.executive_summary if s else "Not available.",
            "",
            "## KEY METRICS DASHBOARD",
        ]

        if s and s.key_metrics_dashboard:
            for domain, metric in s.key_metrics_dashboard.items():
                lines.append(f"- **{domain}**: {metric}")

        lines.extend(["", "## STRATEGIC INSIGHTS"])
        if s and s.strategic_insights:
            for insight in s.strategic_insights:
                lines.append(f"- {insight}")

        lines.extend(["", "## RECOMMENDATIONS"])
        if s and s.recommendations:
            lines.append("| Action | Owner | Timeline | Priority |")
            lines.append("|--------|-------|----------|----------|")
            for rec in s.recommendations:
                action = rec.get("action", "—")
                owner = rec.get("owner", "—")
                timeline = rec.get("timeline", "—")
                priority = rec.get("priority", "—")
                lines.append(f"| {action} | {owner} | {timeline} | {priority} |")

        lines.extend(["", "## RISK REGISTER"])
        if s and s.risk_register:
            lines.append("| Risk | Likelihood | Impact | Mitigation |")
            lines.append("|------|------------|--------|------------|")
            for risk in s.risk_register:
                r = risk.get("risk", "—")
                likelihood = risk.get("likelihood", "—")
                impact = risk.get("impact", "—")
                mitigation = risk.get("mitigation", "—")
                lines.append(f"| {r} | {likelihood} | {impact} | {mitigation} |")

        lines.extend(["", "---"])

        # Phase timings section
        if result.phase_timings:
            lines.append("")
            lines.append("## PIPELINE PERFORMANCE")
            for phase, elapsed in result.phase_timings.items():
                lines.append(f"- {phase}: {elapsed:.2f}s")

        lines.extend(
            [
                "",
                f"*Total pipeline time: {result.total_pipeline_time_seconds:.1f}s*",
                "",
                "*Executive Decision Intelligence Briefing System — Prompt to Production, Chapter 20*",
            ]
        )

        return "\n".join(lines)
