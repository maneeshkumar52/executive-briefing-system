import asyncio
import time
import uuid
import structlog
from datetime import datetime, timezone

from shared.models import (
    BriefingRequest,
    BriefingResult,
    BriefingStatus,
    CompanyData,
    CustomerData,
    FinancialData,
    HRData,
    MarketData,
    OperationalData,
)
from data_sources.financial_connector import FinancialConnector
from data_sources.customer_connector import CustomerConnector
from data_sources.market_connector import MarketConnector
from data_sources.hr_connector import HRConnector
from data_sources.ops_connector import OpsConnector
from data_sources.news_connector import NewsConnector
from specialists.financial_specialist import FinancialSpecialist
from specialists.market_specialist import MarketSpecialist
from specialists.operations_specialist import OperationsSpecialist
from specialists.people_specialist import PeopleSpecialist
from specialists.risk_specialist import RiskSpecialist
from synthesiser.agent import SynthesiserAgent
from compliance_gate.agent import ComplianceGate
from orchestrator.report_generator import ReportGenerator

logger = structlog.get_logger()


class BriefingPipeline:
    """5-phase executive briefing pipeline that runs end-to-end in under 3 minutes."""

    async def run(self, request: BriefingRequest) -> BriefingResult:
        run_id = str(uuid.uuid4())[:8]
        start_total = time.monotonic()
        phase_timings: dict[str, float] = {}

        result = BriefingResult(
            run_id=run_id,
            status=BriefingStatus.PENDING,
            topic=request.topic,
            requested_by=request.requester,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            # ----------------------------------------------------------------
            # Phase 1: Fetch all 6 data sources concurrently
            # ----------------------------------------------------------------
            t0 = time.monotonic()
            result.status = BriefingStatus.FETCHING_DATA
            logger.info("pipeline.phase1_starting", run_id=run_id)

            raw_results = await asyncio.gather(
                FinancialConnector().fetch(),
                CustomerConnector().fetch(),
                MarketConnector().fetch(),
                HRConnector().fetch(),
                OpsConnector().fetch(),
                NewsConnector().fetch(),
                return_exceptions=True,
            )
            financial_raw, customer_raw, market_raw, hr_raw, ops_raw, news_raw = raw_results

            company_data = CompanyData(
                financial=financial_raw
                if not isinstance(financial_raw, Exception)
                else FinancialData(),
                customer=customer_raw
                if not isinstance(customer_raw, Exception)
                else CustomerData(),
                market=market_raw
                if not isinstance(market_raw, Exception)
                else MarketData(),
                hr=hr_raw if not isinstance(hr_raw, Exception) else HRData(),
                operational=ops_raw
                if not isinstance(ops_raw, Exception)
                else OperationalData(),
                news=news_raw if not isinstance(news_raw, Exception) else [],
                fetch_timestamp=datetime.now(timezone.utc).isoformat(),
            )
            result.company_data = company_data
            phase_timings["phase1_data_fetch"] = time.monotonic() - t0
            logger.info(
                "pipeline.phase1_complete",
                run_id=run_id,
                elapsed=round(phase_timings["phase1_data_fetch"], 3),
            )

            # ----------------------------------------------------------------
            # Phase 2: Run 5 specialist analyses concurrently
            # ----------------------------------------------------------------
            t0 = time.monotonic()
            result.status = BriefingStatus.ANALYSING
            logger.info("pipeline.phase2_starting", run_id=run_id)

            specialist_results = await asyncio.gather(
                FinancialSpecialist().analyse(company_data),
                MarketSpecialist().analyse(company_data),
                OperationsSpecialist().analyse(company_data),
                PeopleSpecialist().analyse(company_data),
                RiskSpecialist().analyse(company_data),
                return_exceptions=True,
            )
            specialist_analyses = [
                a for a in specialist_results if not isinstance(a, Exception)
            ]
            # Log any specialist failures
            for sr in specialist_results:
                if isinstance(sr, Exception):
                    logger.error(
                        "pipeline.specialist_failed", run_id=run_id, error=str(sr)
                    )

            result.specialist_analyses = specialist_analyses
            phase_timings["phase2_specialist_analysis"] = time.monotonic() - t0
            logger.info(
                "pipeline.phase2_complete",
                run_id=run_id,
                specialists=len(specialist_analyses),
                elapsed=round(phase_timings["phase2_specialist_analysis"], 3),
            )

            # ----------------------------------------------------------------
            # Phase 3: Synthesise into executive briefing
            # ----------------------------------------------------------------
            t0 = time.monotonic()
            result.status = BriefingStatus.SYNTHESISING
            logger.info("pipeline.phase3_starting", run_id=run_id)

            synthesis = await SynthesiserAgent().synthesise(
                specialist_analyses, company_data, request
            )
            result.synthesis = synthesis
            phase_timings["phase3_synthesis"] = time.monotonic() - t0
            logger.info(
                "pipeline.phase3_complete",
                run_id=run_id,
                elapsed=round(phase_timings["phase3_synthesis"], 3),
            )

            # ----------------------------------------------------------------
            # Phase 4: Compliance gate review
            # ----------------------------------------------------------------
            t0 = time.monotonic()
            result.status = BriefingStatus.COMPLIANCE_REVIEW
            logger.info("pipeline.phase4_starting", run_id=run_id)

            compliance = await ComplianceGate().review(synthesis, request)
            result.compliance = compliance
            phase_timings["phase4_compliance"] = time.monotonic() - t0
            logger.info(
                "pipeline.phase4_complete",
                run_id=run_id,
                approved=compliance.approved,
                elapsed=round(phase_timings["phase4_compliance"], 3),
            )

            # ----------------------------------------------------------------
            # Phase 5: Generate formatted markdown briefing
            # ----------------------------------------------------------------
            t0 = time.monotonic()
            logger.info("pipeline.phase5_starting", run_id=run_id)
            result.formatted_briefing = ReportGenerator().generate_markdown(
                result, request
            )
            phase_timings["phase5_report_generation"] = time.monotonic() - t0
            logger.info(
                "pipeline.phase5_complete",
                run_id=run_id,
                elapsed=round(phase_timings["phase5_report_generation"], 3),
            )

            result.status = BriefingStatus.COMPLETE
            result.phase_timings = phase_timings
            result.total_pipeline_time_seconds = time.monotonic() - start_total
            logger.info(
                "pipeline.complete",
                run_id=run_id,
                total_seconds=round(result.total_pipeline_time_seconds, 2),
                status=result.status,
            )

        except Exception as e:
            result.status = BriefingStatus.FAILED
            result.total_pipeline_time_seconds = time.monotonic() - start_total
            result.phase_timings = phase_timings
            logger.error(
                "pipeline.failed",
                run_id=run_id,
                error=str(e),
                exc_info=True,
            )

        return result
