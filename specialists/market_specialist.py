import time
import structlog
from shared.models import CompanyData, SpecialistAnalysis
from .base_specialist import BaseSpecialist

logger = structlog.get_logger()

MARKET_SYSTEM_PROMPT = """You are a Chief Strategy Officer analysing competitive positioning and market dynamics. Provide a concise market analysis covering:
- Current market share and year-on-year trend
- Key competitor movements and threats
- Addressable market opportunity and capture rate
- Recommended strategic positioning adjustments
- 3-4 specific, data-backed findings

Write in board-level language. Be direct and data-driven. Limit to 250 words."""


class MarketSpecialist(BaseSpecialist):
    def __init__(self) -> None:
        super().__init__("Market & Competitive Intelligence Analyst")

    async def analyse(self, data: CompanyData) -> SpecialistAnalysis:
        start = time.monotonic()
        m = data.market
        news_items = [
            f"  - {n.headline} (sentiment: {n.sentiment:+.1f})"
            for n in data.news
            if n.sentiment < -0.2
        ]
        news_summary = "\n".join(news_items) if news_items else "  - No significant negative competitor news"

        user_prompt = (
            f"Analyse this competitive position for {m.region}:\n"
            f"- Our Market Share: {m.market_share_pct:.1f}% (YoY change: {m.yoy_share_change_pct:+.1f}%)\n"
            f"- Industry Growth Rate: {m.industry_growth_rate_pct:.1f}%\n"
            f"- Total Addressable Market: ${m.addressable_market_usd_billions:.1f}B\n"
            f"- Competitor 1 Share: {m.competitor_1_share_pct:.1f}%\n"
            f"- Competitor 2 Share: {m.competitor_2_share_pct:.1f}%\n"
            f"- Competitor 3 Share: {m.competitor_3_share_pct:.1f}%\n"
            f"- Relevant market news:\n{news_summary}"
        )

        analysis = await self._call_llm(MARKET_SYSTEM_PROMPT, user_prompt)
        findings = self._extract_key_findings(analysis)

        risk_flags: list[str] = []
        if m.yoy_share_change_pct < 0:
            risk_flags.append(
                f"Market share declining ({m.yoy_share_change_pct:+.1f}% YoY) — competitive pressure detected"
            )
        if m.competitor_1_share_pct > 35.0:
            risk_flags.append(
                f"Dominant competitor holds {m.competitor_1_share_pct:.1f}% share — potential market power risk"
            )

        return SpecialistAnalysis(
            specialist_name=self.specialist_name,
            key_findings=findings
            if findings
            else [
                f"Market share of {m.market_share_pct:.1f}% represents {m.yoy_share_change_pct:+.1f}% YoY shift",
                f"Addressable market of ${m.addressable_market_usd_billions:.1f}B growing at {m.industry_growth_rate_pct:.1f}%",
                f"Lead competitor holds {m.competitor_1_share_pct:.1f}% — gap of {m.competitor_1_share_pct - m.market_share_pct:.1f}pp",
                "Competitor reliability issues create short-term enterprise acquisition opportunity",
            ],
            analysis_text=analysis,
            confidence_score=0.82,
            risk_flags=risk_flags,
            processing_time_seconds=time.monotonic() - start,
        )
