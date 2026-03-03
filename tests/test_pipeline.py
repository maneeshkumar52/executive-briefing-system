"""
Tests for the executive-briefing-system pipeline.

All tests run without real Azure credentials (LOCAL_MODE=True).
LLM calls are mocked where needed.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from shared.models import (
    BriefingRequest,
    BriefingResult,
    BriefingStatus,
    CompanyData,
    ComplianceResult,
    CustomerData,
    FinancialData,
    HRData,
    MarketData,
    OperationalData,
    SpecialistAnalysis,
    SynthesisResult,
)
from data_sources.financial_connector import FinancialConnector
from data_sources.customer_connector import CustomerConnector
from data_sources.market_connector import MarketConnector
from data_sources.hr_connector import HRConnector
from data_sources.ops_connector import OpsConnector
from data_sources.news_connector import NewsConnector
from orchestrator.report_generator import ReportGenerator
from compliance_gate.agent import ComplianceGate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_company_data() -> CompanyData:
    return CompanyData(
        financial=FinancialData(),
        customer=CustomerData(),
        market=MarketData(),
        hr=HRData(),
        operational=OperationalData(),
        news=[],
        fetch_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _make_synthesis() -> SynthesisResult:
    return SynthesisResult(
        executive_summary="The company delivered strong quarterly performance.",
        key_metrics_dashboard={"Revenue": "$2412.7M (+12.4% YoY)"},
        strategic_insights=["Revenue growth outpaces cost growth."],
        recommendations=[
            {
                "action": "Launch enterprise campaign",
                "owner": "CRO",
                "timeline": "6 weeks",
                "priority": "High",
            }
        ],
        risk_register=[
            {
                "risk": "Competitor AI investment",
                "likelihood": "High",
                "impact": "High",
                "mitigation": "Accelerate roadmap",
            }
        ],
        briefing_date="2025-01-22",
    )


def _make_briefing_result() -> BriefingResult:
    return BriefingResult(
        run_id="abc12345",
        status=BriefingStatus.COMPLETE,
        topic="Q4 2024 Executive Review",
        requested_by="CEO",
        synthesis=_make_synthesis(),
        compliance=ComplianceResult(
            approved=True,
            issues=[],
            required_disclaimers=[
                "Confidential — For C-Suite Distribution Only",
                "Past performance is not indicative of future results",
                "This briefing contains forward-looking statements subject to material risks",
            ],
            reviewer_notes="No compliance issues found.",
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Test: data connectors
# ---------------------------------------------------------------------------


async def test_financial_connector_returns_data() -> None:
    """FinancialConnector.fetch() should return FinancialData with positive revenue."""
    connector = FinancialConnector()
    result = await connector.fetch()
    assert isinstance(result, FinancialData)
    assert result.quarterly_revenue_usd_millions > 0
    assert result.gross_margin_pct > 0
    assert result.operating_margin_pct > 0
    assert result.free_cash_flow_usd_millions > 0


async def test_customer_connector_returns_data() -> None:
    """CustomerConnector.fetch() should return CustomerData with a valid NPS score."""
    connector = CustomerConnector()
    result = await connector.fetch()
    assert isinstance(result, CustomerData)
    assert 0 <= result.nps_score <= 100
    assert result.churn_rate_pct >= 0
    assert result.total_active_customers > 0


async def test_market_connector_returns_data() -> None:
    """MarketConnector.fetch() should return MarketData with valid share percentages."""
    connector = MarketConnector()
    result = await connector.fetch()
    assert isinstance(result, MarketData)
    assert 0 < result.market_share_pct < 100
    assert result.addressable_market_usd_billions > 0


async def test_hr_connector_returns_data() -> None:
    """HRConnector.fetch() should return HRData with positive headcount."""
    connector = HRConnector()
    result = await connector.fetch()
    assert isinstance(result, HRData)
    assert result.total_headcount > 0
    assert 0 <= result.employee_engagement_score <= 100


async def test_ops_connector_returns_data() -> None:
    """OpsConnector.fetch() should return OperationalData with valid uptime."""
    connector = OpsConnector()
    result = await connector.fetch()
    assert isinstance(result, OperationalData)
    assert 0 < result.system_uptime_pct <= 100
    assert result.sla_compliance_pct > 0


async def test_news_connector_returns_five_items() -> None:
    """NewsConnector.fetch() should return exactly 5 mock news items."""
    connector = NewsConnector()
    result = await connector.fetch()
    assert len(result) == 5
    for item in result:
        assert item.headline
        assert item.source
        assert -1.0 <= item.sentiment <= 1.0


# ---------------------------------------------------------------------------
# Test: data models
# ---------------------------------------------------------------------------


async def test_data_models_valid() -> None:
    """CompanyData can be constructed from all connector outputs."""
    fin = await FinancialConnector().fetch()
    cust = await CustomerConnector().fetch()
    mkt = await MarketConnector().fetch()
    hr = await HRConnector().fetch()
    ops = await OpsConnector().fetch()
    news = await NewsConnector().fetch()

    company_data = CompanyData(
        financial=fin,
        customer=cust,
        market=mkt,
        hr=hr,
        operational=ops,
        news=news,
        fetch_timestamp=datetime.now(timezone.utc).isoformat(),
    )
    assert company_data.financial.quarterly_revenue_usd_millions > 0
    assert company_data.customer.nps_score >= 0
    assert len(company_data.news) == 5


# ---------------------------------------------------------------------------
# Test: ReportGenerator
# ---------------------------------------------------------------------------


def test_report_generator_markdown() -> None:
    """ReportGenerator.generate_markdown() returns a markdown string with expected header."""
    result = _make_briefing_result()
    request = BriefingRequest(topic="Q4 2024 Executive Review", requester="CEO")
    generator = ReportGenerator()
    markdown = generator.generate_markdown(result, request)

    assert isinstance(markdown, str)
    assert "EXECUTIVE BRIEFING" in markdown
    assert "EXECUTIVE SUMMARY" in markdown
    assert "KEY METRICS DASHBOARD" in markdown
    assert "STRATEGIC INSIGHTS" in markdown
    assert "RECOMMENDATIONS" in markdown
    assert "RISK REGISTER" in markdown
    assert "CONFIDENTIAL" in markdown
    assert "abc12345" in markdown  # run_id present


def test_report_generator_includes_disclaimers() -> None:
    """ReportGenerator includes all compliance disclaimers in the output."""
    result = _make_briefing_result()
    request = BriefingRequest()
    markdown = ReportGenerator().generate_markdown(result, request)
    assert "Confidential" in markdown
    assert "forward-looking statements" in markdown


# ---------------------------------------------------------------------------
# Test: ComplianceGate
# ---------------------------------------------------------------------------


async def test_compliance_gate_adds_disclaimers() -> None:
    """ComplianceGate.review() always returns the required disclaimers list."""
    synthesis = _make_synthesis()
    request = BriefingRequest()

    # Mock the LLM call so no Azure credentials are needed
    with patch.object(ComplianceGate, "_llm_review", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = (
            "No compliance issues detected. Approved for distribution.",
            [],
            True,
        )
        gate = ComplianceGate()
        compliance = await gate.review(synthesis, request)

    assert isinstance(compliance, ComplianceResult)
    assert len(compliance.required_disclaimers) == 3
    assert "Confidential — For C-Suite Distribution Only" in compliance.required_disclaimers
    assert "Past performance is not indicative of future results" in compliance.required_disclaimers
    assert compliance.approved is True


async def test_compliance_gate_rule_based_checks() -> None:
    """ComplianceGate rule-based checks detect guaranteed outcome language."""
    synthesis = SynthesisResult(
        executive_summary="Revenue will guarantee 20% growth next quarter.",
        key_metrics_dashboard={},
        strategic_insights=[],
        recommendations=[],
        risk_register=[],
        briefing_date="2025-01-22",
    )
    request = BriefingRequest()

    with patch.object(ComplianceGate, "_llm_review", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = ("Review complete.", [], True)
        gate = ComplianceGate()
        compliance = await gate.review(synthesis, request)

    assert any("guarantee" in issue.lower() for issue in compliance.issues)


# ---------------------------------------------------------------------------
# Test: FinancialSpecialist with mocked LLM
# ---------------------------------------------------------------------------


async def test_financial_specialist_builds_analysis() -> None:
    """FinancialSpecialist.analyse() returns SpecialistAnalysis with valid fields."""
    from specialists.financial_specialist import FinancialSpecialist

    company_data = _make_company_data()

    mock_llm_response = (
        "- Revenue of $2412.7M shows 12.4% YoY growth, exceeding sector median.\n"
        "- Operating margin of 24.3% reflects cost discipline.\n"
        "- FCF of $487.2M provides balance sheet flexibility.\n"
        "- Cost growth of 8.7% vs revenue growth of 12.4% is positive spread."
    )

    with patch.object(
        FinancialSpecialist, "_call_llm", new_callable=AsyncMock
    ) as mock_call:
        mock_call.return_value = mock_llm_response
        specialist = FinancialSpecialist()
        analysis = await specialist.analyse(company_data)

    assert isinstance(analysis, SpecialistAnalysis)
    assert analysis.specialist_name == "Financial Performance Analyst"
    assert len(analysis.key_findings) > 0
    assert 0.0 <= analysis.confidence_score <= 1.0
    assert analysis.processing_time_seconds >= 0.0
    assert isinstance(analysis.risk_flags, list)


async def test_risk_specialist_flags_negative_news() -> None:
    """RiskSpecialist flags news items with sentiment below -0.4."""
    from specialists.risk_specialist import RiskSpecialist
    from data_sources.news_connector import NewsConnector

    company_data = _make_company_data()
    company_data.news = await NewsConnector().fetch()

    mock_llm_response = (
        "- TechRival Corp investment poses enterprise market threat.\n"
        "- Regulatory risk from EU AI Act deadline.\n"
        "- Operational incidents create SLA exposure.\n"
    )

    with patch.object(
        RiskSpecialist, "_call_llm", new_callable=AsyncMock
    ) as mock_call:
        mock_call.return_value = mock_llm_response
        specialist = RiskSpecialist()
        analysis = await specialist.analyse(company_data)

    assert isinstance(analysis, SpecialistAnalysis)
    # TechRival Corp news has sentiment -0.6, should be flagged
    negative_flags = [f for f in analysis.risk_flags if "TechRival" in f]
    assert len(negative_flags) > 0
