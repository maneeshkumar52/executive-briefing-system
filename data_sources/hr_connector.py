import asyncio
import structlog
from shared.models import HRData

logger = structlog.get_logger()


class HRConnector:
    """Connects to HRIS system (Workday / BambooHR in production)."""

    async def fetch(self) -> HRData:
        logger.info("hr_connector.fetching")
        await asyncio.sleep(0.08)  # Simulate network latency
        return HRData(
            total_headcount=8547,
            new_hires_this_quarter=342,
            voluntary_turnover_rate_pct=8.2,
            involuntary_turnover_rate_pct=1.1,
            offer_acceptance_rate_pct=84.3,
            employee_engagement_score=71.0,
            training_hours_per_employee=24.5,
            open_positions=187,
        )
