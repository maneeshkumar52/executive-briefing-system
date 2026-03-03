from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BriefingStatus(str, Enum):
    PENDING = "pending"
    FETCHING_DATA = "fetching_data"
    ANALYSING = "analysing"
    SYNTHESISING = "synthesising"
    COMPLIANCE_REVIEW = "compliance_review"
    COMPLETE = "complete"
    FAILED = "failed"


class FinancialData(BaseModel):
    quarterly_revenue_usd_millions: float = 2400.0
    gross_margin_pct: float = 68.5
    operating_margin_pct: float = 24.3
    free_cash_flow_usd_millions: float = 487.0
    yoy_revenue_growth_pct: float = 12.4
    yoy_cost_growth_pct: float = 8.7
    ebitda_usd_millions: float = 612.0
    capex_usd_millions: float = 125.0
    period: str = "Q4 2024"


class CustomerData(BaseModel):
    nps_score: int = 42
    churn_rate_pct: float = 2.1
    arpu_usd: float = 284.50
    new_customers_this_quarter: int = 12450
    total_active_customers: int = 387000
    customer_satisfaction_score: float = 4.2
    support_ticket_resolution_hours: float = 18.5
    csat_trend: str = "improving"


class MarketData(BaseModel):
    market_share_pct: float = 23.4
    industry_growth_rate_pct: float = 8.9
    addressable_market_usd_billions: float = 42.0
    competitor_1_share_pct: float = 31.2
    competitor_2_share_pct: float = 18.7
    competitor_3_share_pct: float = 11.5
    yoy_share_change_pct: float = 1.3
    region: str = "EMEA + Americas"


class HRData(BaseModel):
    total_headcount: int = 8547
    new_hires_this_quarter: int = 342
    voluntary_turnover_rate_pct: float = 8.2
    involuntary_turnover_rate_pct: float = 1.1
    offer_acceptance_rate_pct: float = 84.3
    employee_engagement_score: float = 71.0
    training_hours_per_employee: float = 24.5
    open_positions: int = 187


class OperationalData(BaseModel):
    system_uptime_pct: float = 99.87
    sla_compliance_pct: float = 98.3
    incidents_this_quarter: int = 23
    critical_incidents: int = 2
    mean_time_to_recover_hours: float = 2.4
    deployment_frequency_per_week: float = 14.0
    customer_facing_outages_minutes: float = 47.0
    infrastructure_cost_usd_millions: float = 34.2


class NewsItem(BaseModel):
    headline: str
    source: str
    date: str
    sentiment: float  # -1 to 1
    competitor_mentioned: str
    summary: str


class CompanyData(BaseModel):
    financial: FinancialData
    customer: CustomerData
    market: MarketData
    hr: HRData
    operational: OperationalData
    news: List[NewsItem]
    fetch_timestamp: str


class SpecialistAnalysis(BaseModel):
    specialist_name: str
    key_findings: List[str]
    analysis_text: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_flags: List[str] = []
    processing_time_seconds: float


class SynthesisResult(BaseModel):
    executive_summary: str
    key_metrics_dashboard: Dict[str, str]
    strategic_insights: List[str]
    recommendations: List[Dict[str, str]]  # {action, owner, timeline, priority}
    risk_register: List[Dict[str, str]]    # {risk, likelihood, impact, mitigation}
    briefing_date: str


class ComplianceResult(BaseModel):
    approved: bool
    issues: List[str]
    required_disclaimers: List[str]
    reviewer_notes: str


class BriefingResult(BaseModel):
    run_id: str
    status: BriefingStatus
    topic: str
    requested_by: str
    company_data: Optional[CompanyData] = None
    specialist_analyses: Optional[List[SpecialistAnalysis]] = None
    synthesis: Optional[SynthesisResult] = None
    compliance: Optional[ComplianceResult] = None
    formatted_briefing: Optional[str] = None
    phase_timings: Dict[str, float] = {}
    total_pipeline_time_seconds: float = 0.0
    created_at: str


class BriefingRequest(BaseModel):
    topic: str = "Q4 2024 Executive Performance Review"
    date_range: str = "Q4 2024 (October - December 2024)"
    requester: str = "CEO"
    requester_email: str = "ceo@company.com"
