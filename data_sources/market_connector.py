import asyncio
import structlog
from shared.models import MarketData

logger = structlog.get_logger()


class MarketConnector:
    """Connects to market intelligence platform (Crayon / Klue in production)."""

    async def fetch(self) -> MarketData:
        logger.info("market_connector.fetching")
        await asyncio.sleep(0.12)  # Simulate network latency
        return MarketData(
            market_share_pct=23.4,
            industry_growth_rate_pct=8.9,
            addressable_market_usd_billions=42.0,
            competitor_1_share_pct=31.2,
            competitor_2_share_pct=18.7,
            competitor_3_share_pct=11.5,
            yoy_share_change_pct=1.3,
            region="EMEA + Americas",
        )
