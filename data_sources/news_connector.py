import asyncio
import structlog
from typing import List
from shared.models import NewsItem

logger = structlog.get_logger()

MOCK_NEWS: List[NewsItem] = [
    NewsItem(
        headline="TechRival Corp announces $500M AI investment, targeting enterprise market",
        source="FT",
        date="2025-01-15",
        sentiment=-0.6,
        competitor_mentioned="TechRival Corp",
        summary=(
            "Major competitor doubles down on AI capabilities with significant capital allocation, "
            "potentially threatening our market position in the enterprise segment."
        ),
    ),
    NewsItem(
        headline="CloudLeader Inc loses 3 major enterprise contracts amid service reliability concerns",
        source="Reuters",
        date="2025-01-18",
        sentiment=0.7,
        competitor_mentioned="CloudLeader Inc",
        summary=(
            "Competitor reliability issues create market opportunity. Three Fortune 500 companies "
            "reportedly evaluating alternatives."
        ),
    ),
    NewsItem(
        headline="Industry consolidation: StartupX acquired by GlobalTech for $2.1B",
        source="TechCrunch",
        date="2025-01-20",
        sentiment=-0.3,
        competitor_mentioned="GlobalTech",
        summary=(
            "Market consolidation continues. Acquisition strengthens GlobalTech's SMB portfolio, "
            "creating stronger competition in the mid-market segment."
        ),
    ),
    NewsItem(
        headline="Regulatory update: EU AI Act compliance deadline set for Q3 2025",
        source="EU Official Journal",
        date="2025-01-10",
        sentiment=-0.1,
        competitor_mentioned="Industry-wide",
        summary=(
            "All AI products must achieve compliance by September 2025. Estimated compliance cost "
            "EUR 2-5M for companies of our size."
        ),
    ),
    NewsItem(
        headline="ESG ratings agency upgrades our industry sector to 'Positive' outlook",
        source="Bloomberg",
        date="2025-01-22",
        sentiment=0.8,
        competitor_mentioned="None",
        summary=(
            "Improved ESG rating for technology sector creates favourable conditions for institutional "
            "investment and enterprise procurement criteria."
        ),
    ),
]


class NewsConnector:
    """Connects to news aggregation service (Feedly / Meltwater in production)."""

    async def fetch(self) -> List[NewsItem]:
        logger.info("news_connector.fetching")
        await asyncio.sleep(0.15)  # Simulate network latency
        return MOCK_NEWS
