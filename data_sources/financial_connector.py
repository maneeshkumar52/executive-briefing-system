import asyncio
import structlog
from shared.models import FinancialData

logger = structlog.get_logger()


class FinancialConnector:
    """Connects to financial data warehouse (Azure Synapse Analytics in production)."""

    async def fetch(self, period: str = "Q4 2024") -> FinancialData:
        logger.info("financial_connector.fetching", period=period)
        await asyncio.sleep(0.1)  # Simulate network latency
        return FinancialData(
            quarterly_revenue_usd_millions=2412.7,
            gross_margin_pct=68.5,
            operating_margin_pct=24.3,
            free_cash_flow_usd_millions=487.2,
            yoy_revenue_growth_pct=12.4,
            yoy_cost_growth_pct=8.7,
            ebitda_usd_millions=612.4,
            capex_usd_millions=125.3,
            period=period,
        )
