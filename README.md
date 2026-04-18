<div align="center">

# Executive Briefing System

### Multi-Agent Decision Intelligence Platform for Board-Level Reporting

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--4o-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![Azure Cosmos DB](https://img.shields.io/badge/Cosmos_DB-4.7-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/cosmos-db)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*An enterprise-grade 5-phase pipeline that aggregates data from 6 enterprise connectors, runs 5 C-suite specialist AI analysts in parallel, synthesises findings into a board-quality briefing document, validates compliance through a dual-layer gate (deterministic rules + LLM review), and generates a formatted CONFIDENTIAL Markdown report — with full deterministic fallbacks when Azure OpenAI is unavailable.*

[Architecture](#architecture) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Specialist Agents](#specialist-agents) · [Compliance Gate](#compliance-gate) · [Deployment](#deployment)

</div>

---

## Why This Exists

Executive decision-making at enterprise scale requires synthesising information across multiple business domains simultaneously — finance reviewing margins and cash flow, market intelligence tracking competitors, operations monitoring reliability, people analytics assessing talent health, and risk management mapping threat matrices. These analyses must be consolidated into a single board-quality document, validated for compliance, and formatted for C-suite distribution.

This system automates that entire workflow as a **5-phase multi-agent pipeline** — not a chatbot or generic RAG, but a structured intelligence production system with:

- **6 enterprise data connectors** fetching financial, customer, market, HR, operational, and news data in parallel
- **5 specialist agents** (CFO, CSO, COO, CPO, CRO personas) analysing data concurrently with domain-specific risk flag thresholds
- **A synthesiser agent** consolidating all findings into executive summary, KPI dashboard, recommendations, and risk register
- **A dual-layer compliance gate** combining deterministic rule scanning with LLM-based nuanced review
- **A report generator** producing CONFIDENTIAL-classified Markdown briefing documents
- **Full deterministic fallbacks** at every stage — the system produces complete output even without Azure OpenAI

---

## Architecture

### 5-Phase Pipeline Overview

```
                        POST /api/v1/briefing
                                │
                    ┌───────────┴────────────┐
                    │   BriefingPipeline.run()│
                    └───────────┬────────────┘
                                │
         ┌──────────────────────┼──────────────────────────────┐
         │       PHASE 1: DATA FETCH  (asyncio.gather, 6x)    │
         │                                                      │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
         │  │  Financial   │ │  Customer    │ │   Market     ││
         │  │  Connector   │ │  Connector   │ │  Connector   ││
         │  │ (Synapse)    │ │ (Segment)    │ │ (Crayon)     ││
         │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘│
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
         │  │     HR       │ │  Operations  │ │    News      ││
         │  │  Connector   │ │  Connector   │ │  Connector   ││
         │  │ (Workday)    │ │ (Datadog)    │ │ (Feedly)     ││
         │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘│
         │         └────────┬───────┴──────────┬─────┘        │
         │                  ▼                                  │
         │            CompanyData                              │
         └──────────────────┬──────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────────────────────┐
         │      PHASE 2: SPECIALIST ANALYSIS (asyncio.gather)  │
         │                                                      │
         │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
         │  │  Financial   │ │   Market     │ │ Operations   ││
         │  │  Specialist  │ │  Specialist  │ │  Specialist  ││
         │  │  (CFO)       │ │  (CSO)       │ │  (COO)       ││
         │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘│
         │  ┌──────────────┐ ┌──────────────┐                 │
         │  │   People     │ │    Risk      │                 │
         │  │  Specialist  │ │  Specialist  │                 │
         │  │  (CPO)       │ │  (CRO)       │                 │
         │  └──────┬───────┘ └──────┬───────┘                 │
         │         └────────┬───────┘                          │
         │                  ▼                                  │
         │       [SpecialistAnalysis × 5]                      │
         └──────────────────┬──────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────────────────────┐
         │   PHASE 3: SYNTHESIS  (Chief Strategy Officer)      │
         │                                                      │
         │  • Executive Summary (3 paragraphs)                 │
         │  • Key Metrics Dashboard (10 KPIs)                  │
         │  • Strategic Insights (4-5 cross-domain)            │
         │  • Recommendations (action/owner/timeline/priority) │
         │  • Risk Register (risk/likelihood/impact/mitigation)│
         └──────────────────┬──────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────────────────────┐
         │   PHASE 4: COMPLIANCE GATE (Dual-Layer)             │
         │                                                      │
         │  Layer 1: Deterministic rule scanning               │
         │    • "will guarantee", "100% certain" → flagged     │
         │    • "will grow", "will achieve" → flagged          │
         │                                                      │
         │  Layer 2: LLM review (temp=0.1)                     │
         │    • Forward-looking statement hedging               │
         │    • Speculative claims without data                │
         │    • Inappropriate language for C-suite              │
         └──────────────────┬──────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────────────────────┐
         │   PHASE 5: REPORT GENERATION                        │
         │                                                      │
         │  ReportGenerator.generate_markdown()                │
         │    • CONFIDENTIAL header + classification           │
         │    • Disclaimers (from compliance gate)              │
         │    • Executive Summary                              │
         │    • Key Metrics Dashboard                          │
         │    • Strategic Insights                             │
         │    • Recommendations table                          │
         │    • Risk Register table                            │
         │    • Pipeline Performance metrics                   │
         └──────────────────┬──────────────────────────────────┘
                            │
                            ▼
                    BriefingResult (JSON)
```

### Why Not RAG?

| Dimension | This System | Generic RAG |
|-----------|-------------|-------------|
| **Data sources** | 6 structured enterprise connectors (financial, customer, market, HR, ops, news) | Unstructured document chunks |
| **Architecture** | 5 specialist analysts + synthesiser + compliance gate + report generator (8 agents) | Single retriever + single generator |
| **Output** | Structured executive briefing with KPI dashboard, recommendations table, risk register | Free-form answer |
| **Compliance** | Dual-layer gate: deterministic rules + LLM review with required disclaimers | None |
| **Concurrency** | Parallel fan-out for both data collection (6x) and analysis (5x) | Sequential |
| **Fallback design** | Every agent has deterministic fallback — produces complete output without LLM | Fails without LLM |
| **Persona engineering** | C-suite personas (CFO, CSO, COO, CPO, CRO) with domain-specific prompts | Generic assistant |
| **Risk intelligence** | Cross-domain risk assessment with probability×impact matrix and 14 automated risk flag thresholds | No risk analysis |
| **Pipeline observability** | Per-phase timing, 7-state status machine, structured JSON logging | Minimal |
| **Output format** | Board-quality CONFIDENTIAL markdown with tables and disclaimers | Plain text |

### Pipeline Status Machine

```
PENDING ──► FETCHING_DATA ──► ANALYSING ──► SYNTHESISING ──► COMPLIANCE_REVIEW ──► COMPLETE
                                                                                      │
                                                                              (or) FAILED
```

The `BriefingStatus` enum tracks pipeline progress through 7 states, enabling client-side progress indication via the status endpoint.

---

## Design Decisions

### Why 5 Phases Instead of a Single LLM Call?

| Approach | Context Window | Accuracy | Auditability |
|----------|---------------|----------|-------------|
| **Single prompt** | Entire dataset in one call | Low — LLM loses focus across domains | None |
| **Sequential chain** | One domain at a time | Better — focused context per domain | Per-step |
| **5-phase pipeline** ✅ | Domain-specific context per specialist | Highest — each expert analyses their domain | Per-phase timing + per-specialist confidence |

Each specialist receives only the data relevant to their domain (except the Risk Specialist, who receives all data for cross-domain threat assessment). This focused context produces higher-quality analysis than cramming everything into one prompt.

### Why Dual-Layer Compliance (Rules + LLM)?

```python
# Layer 1: Deterministic — catches obvious violations instantly
guaranteed_outcome_phrases = [
    "will guarantee", "guaranteed to", "certain to", "definitely will", "100% certain"
]
forward_looking_triggers = [
    "will grow", "will achieve", "will deliver", "will increase"
]

# Layer 2: LLM — catches nuanced compliance issues
# "Forward-looking statements without hedging language"
# "Overly speculative claims not supported by data"
# Temperature: 0.1 (highly deterministic)
```

| Layer | Catches | Latency | Reliability |
|-------|---------|---------|-------------|
| **Rule-based** | Exact prohibited phrases | <1ms | 100% deterministic |
| **LLM review** | Nuanced tone, hedging, attribution | ~2s | High (temp=0.1) |
| **Combined** ✅ | Both obvious and subtle compliance issues | ~2s | Deterministic floor + LLM ceiling |

### Why Background Task + Polling Over WebSockets?

```python
# Async endpoint — returns immediately
@app.post("/api/v1/briefing")
async def create_briefing(request, background_tasks):
    background_tasks.add_task(_run_pipeline_task, run_id, request)
    return BriefingResult(status=BriefingStatus.PENDING, ...)

# Client polls status
@app.get("/api/v1/briefing/{run_id}/status")
async def get_status(run_id):
    return {"status": store[run_id].status, "phase_timings": ...}
```

| Pattern | Implementation Complexity | Client Complexity | Scaling |
|---------|--------------------------|-------------------|---------|
| Synchronous | Low | Low (single request) | Poor — ties up worker |
| **Background + polling** ✅ | Low | Medium (poll loop) | Good — worker freed |
| WebSockets | High | High (connection mgmt) | Complex |
| SSE | Medium | Medium | Good |

The system also provides a synchronous endpoint (`POST /api/v1/briefing/sync`) for testing and simple integrations.

### Why Deterministic Fallbacks at Every Stage?

```python
# BaseSpecialist._call_llm() on failure:
return f"[Analysis unavailable due to: {type(e).__name__}]"

# Each specialist provides hardcoded fallback findings:
findings = [
    f"Revenue of ${data.financial.quarterly_revenue_usd_millions:.1f}M shows "
    f"{data.financial.yoy_revenue_growth_pct}% YoY growth",
    ...
]

# SynthesiserAgent._fallback_synthesis() produces complete output:
return SynthesisResult(
    executive_summary=self._default_executive_summary(data),
    key_metrics_dashboard=key_metrics_dashboard,
    strategic_insights=self._default_insights(data),
    recommendations=self._default_recommendations(),
    risk_register=self._default_risks(data),
    ...
)
```

| Design | LLM Unavailable | Partial LLM Failure | Full LLM Available |
|--------|-----------------|---------------------|-------------------|
| No fallback | System crashes | System crashes | Works |
| **Full fallback** ✅ | Data-driven output (no AI) | Mix of AI + data-driven | Full AI output |

This means the system can run in `LOCAL_MODE=true` without any Azure credentials and still produce a complete executive briefing from the mock data.

---

## Data Contracts

### 12 Pydantic Models

All models defined in `shared/models.py` using Pydantic v2:

```python
# ── Status Machine ────────────────────────────────────────────────────────
class BriefingStatus(str, Enum):
    PENDING            = "pending"
    FETCHING_DATA      = "fetching_data"
    ANALYSING          = "analysing"
    SYNTHESISING       = "synthesising"
    COMPLIANCE_REVIEW  = "compliance_review"
    COMPLETE           = "complete"
    FAILED             = "failed"

# ── Data Source Models ────────────────────────────────────────────────────
class FinancialData(BaseModel):
    quarterly_revenue_usd_millions: float = 2400.0
    gross_margin_pct: float               = 68.5
    operating_margin_pct: float           = 24.3
    free_cash_flow_usd_millions: float    = 487.0
    yoy_revenue_growth_pct: float         = 12.4
    yoy_cost_growth_pct: float            = 8.7
    ebitda_usd_millions: float            = 612.0
    capex_usd_millions: float             = 125.0
    period: str                           = "Q4 2024"

class CustomerData(BaseModel):
    nps_score: int                          = 42
    churn_rate_pct: float                   = 2.1
    arpu_usd: float                         = 284.50
    new_customers_this_quarter: int         = 12450
    total_active_customers: int             = 387000
    customer_satisfaction_score: float      = 4.2
    support_ticket_resolution_hours: float  = 18.5
    csat_trend: str                         = "improving"

class MarketData(BaseModel):
    market_share_pct: float                 = 23.4
    industry_growth_rate_pct: float         = 8.9
    addressable_market_usd_billions: float  = 42.0
    competitor_1_share_pct: float           = 31.2
    competitor_2_share_pct: float           = 18.7
    competitor_3_share_pct: float           = 11.5
    yoy_share_change_pct: float             = 1.3
    region: str                             = "EMEA + Americas"

class HRData(BaseModel):
    total_headcount: int                    = 8547
    new_hires_this_quarter: int             = 342
    voluntary_turnover_rate_pct: float      = 8.2
    involuntary_turnover_rate_pct: float    = 1.1
    offer_acceptance_rate_pct: float        = 84.3
    employee_engagement_score: float        = 71.0
    training_hours_per_employee: float      = 24.5
    open_positions: int                     = 187

class OperationalData(BaseModel):
    system_uptime_pct: float                   = 99.87
    sla_compliance_pct: float                  = 98.3
    incidents_this_quarter: int                = 23
    critical_incidents: int                    = 2
    mean_time_to_recover_hours: float          = 2.4
    deployment_frequency_per_week: float       = 14.0
    customer_facing_outages_minutes: float     = 47.0
    infrastructure_cost_usd_millions: float    = 34.2

class NewsItem(BaseModel):
    headline: str
    source: str
    date: str
    sentiment: float              # -1.0 to 1.0
    competitor_mentioned: str
    summary: str

# ── Aggregated Company Data ───────────────────────────────────────────────
class CompanyData(BaseModel):
    financial: FinancialData
    customer: CustomerData
    market: MarketData
    hr: HRData
    operational: OperationalData
    news: List[NewsItem]
    fetch_timestamp: str

# ── Analysis & Output Models ─────────────────────────────────────────────
class SpecialistAnalysis(BaseModel):
    specialist_name: str
    key_findings: List[str]
    analysis_text: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_flags: List[str] = Field(default_factory=list)
    processing_time_seconds: float

class SynthesisResult(BaseModel):
    executive_summary: str
    key_metrics_dashboard: Dict[str, str]     # 10 KPIs
    strategic_insights: List[str]             # 4-5 cross-domain
    recommendations: List[Dict[str, str]]     # {action, owner, timeline, priority}
    risk_register: List[Dict[str, str]]       # {risk, likelihood, impact, mitigation}
    briefing_date: str

class ComplianceResult(BaseModel):
    approved: bool
    issues: List[str]
    required_disclaimers: List[str]
    reviewer_notes: str

# ── Final Briefing Envelope ───────────────────────────────────────────────
class BriefingResult(BaseModel):
    run_id: str
    status: BriefingStatus
    topic: str
    requested_by: str
    company_data: Optional[CompanyData]                    = None
    specialist_analyses: Optional[List[SpecialistAnalysis]] = None
    synthesis: Optional[SynthesisResult]                    = None
    compliance: Optional[ComplianceResult]                  = None
    formatted_briefing: Optional[str]                       = None
    phase_timings: Dict[str, float]                        = {}
    total_pipeline_time_seconds: float                     = 0.0
    created_at: str

# ── Request Model ────────────────────────────────────────────────────────
class BriefingRequest(BaseModel):
    topic: str           = "Q4 2024 Executive Performance Review"
    date_range: str      = "Q4 2024 (October - December 2024)"
    requester: str       = "CEO"
    requester_email: str = "ceo@company.com"
```

### Example API Exchange

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/briefing/sync \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Q4 2024 Executive Performance Review",
    "date_range": "Q4 2024 (October - December 2024)",
    "requester": "CEO",
    "requester_email": "ceo@company.com"
  }'
```

**Response (abbreviated):**
```json
{
  "run_id": "a1b2c3d4",
  "status": "complete",
  "topic": "Q4 2024 Executive Performance Review",
  "requested_by": "CEO",
  "synthesis": {
    "executive_summary": "The company delivered revenue of $2400M in Q4 2024...",
    "key_metrics_dashboard": {
      "Revenue": "$2,400.0M (12.4% YoY growth)",
      "Operating Margin": "24.3%",
      "Free Cash Flow": "$487.0M",
      "NPS": "42",
      "Churn Rate": "2.1%",
      "Active Customers": "387,000",
      "Market Share": "23.4%",
      "Employee Engagement": "71.0/100",
      "System Uptime": "99.87%",
      "Critical Incidents": "2"
    },
    "strategic_insights": [
      "Revenue growth of 12.4% outpaces cost growth of 8.7%, expanding margins",
      "Market share gains of +1.3% YoY in a market growing at 8.9%",
      "Two critical incidents and 47 minutes of outage require reliability investment",
      "187 open positions constraining execution capacity across strategic priorities"
    ],
    "recommendations": [
      {"action": "Launch enterprise win-back campaign", "owner": "CRO", "timeline": "6 weeks", "priority": "High"},
      {"action": "Establish EU AI Act compliance taskforce", "owner": "CTO + General Counsel", "timeline": "Q1 2025", "priority": "High"}
    ],
    "risk_register": [
      {"risk": "TechRival Corp $500M AI investment", "likelihood": "High", "impact": "High", "mitigation": "Accelerate AI roadmap"},
      {"risk": "EU AI Act non-compliance", "likelihood": "Medium", "impact": "High", "mitigation": "Compliance taskforce"}
    ]
  },
  "compliance": {
    "approved": true,
    "issues": [],
    "required_disclaimers": [
      "Confidential — For C-Suite Distribution Only",
      "Past performance is not indicative of future results",
      "This briefing contains forward-looking statements subject to material risks"
    ],
    "reviewer_notes": "No critical compliance issues identified."
  },
  "phase_timings": {
    "phase1_data_fetch": 0.15,
    "phase2_specialist_analysis": 3.21,
    "phase3_synthesis": 2.45,
    "phase4_compliance": 1.12,
    "phase5_report_generation": 0.01
  },
  "total_pipeline_time_seconds": 6.94
}
```

---

## Features

| # | Feature | Description | Implementation |
|---|---------|-------------|----------------|
| 1 | **5-Phase Pipeline** | Data fetch → Analysis → Synthesis → Compliance → Report | `BriefingPipeline.run()` |
| 2 | **6 Enterprise Data Connectors** | Financial, Customer, Market, HR, Operations, News | `data_sources/` module |
| 3 | **5 C-Suite Specialist Agents** | CFO, CSO, COO, CPO, CRO personas | `specialists/` module |
| 4 | **Cross-Domain Risk Analysis** | Risk Specialist reads ALL data domains | `RiskSpecialist.analyse()` |
| 5 | **14 Automated Risk Flag Thresholds** | Data-driven risk detection per specialist | Conditional checks in each specialist |
| 6 | **Dual-Layer Compliance Gate** | Deterministic rules + LLM review (temp=0.1) | `compliance_gate/agent.py` |
| 7 | **3 Required Disclaimers** | Auto-appended to every briefing | `REQUIRED_DISCLAIMERS` constant |
| 8 | **Synthesis Agent (1800 tokens)** | Consolidates all specialist findings | `synthesiser/agent.py` |
| 9 | **10-KPI Dashboard** | Revenue, margin, FCF, NPS, churn, share, engagement, uptime, incidents | `key_metrics_dashboard` dict |
| 10 | **Markdown Report Generator** | CONFIDENTIAL-classified board document | `report_generator.py` |
| 11 | **7-State Status Machine** | PENDING → FETCHING → ANALYSING → SYNTHESISING → COMPLIANCE → COMPLETE/FAILED | `BriefingStatus` enum |
| 12 | **Async + Sync API Endpoints** | Background task for production, sync for testing | `POST /briefing` + `POST /briefing/sync` |
| 13 | **Per-Phase Timing** | Independent timing for all 5 phases | `time.monotonic()` instrumentation |
| 14 | **Full Deterministic Fallbacks** | Complete output without LLM | Fallback data in every agent |
| 15 | **Parallel Data Fetch** | 6 connectors via `asyncio.gather()` | Phase 1 |
| 16 | **Parallel Specialist Analysis** | 5 agents via `asyncio.gather()` | Phase 2 |
| 17 | **Graceful Degradation** | Exceptions replaced with defaults; valid results continue | `return_exceptions=True` |
| 18 | **12 Pydantic v2 Models** | Typed data contracts with validation | `shared/models.py` |
| 19 | **Structured JSON Logging** | structlog with ISO timestamps | `shared/logging_config.py` |
| 20 | **Settings Singleton** | `@lru_cache` pydantic-settings | `shared/config.py` |
| 21 | **CORS Middleware** | Cross-origin enabled for frontend | `CORSMiddleware` |
| 22 | **Health Endpoint** | Liveness probe with active briefing count | `GET /health` |
| 23 | **Markdown Retrieval** | Get formatted briefing by run_id | `GET /briefing/{id}/markdown` |
| 24 | **Status Polling** | Lightweight status check with phase timings | `GET /briefing/{id}/status` |
| 25 | **Docker with Health Check** | Built-in HEALTHCHECK in Dockerfile | `urllib.request` probe |
| 26 | **Docker Compose** | Single-command deployment with env loading | `infra/docker-compose.yml` |
| 27 | **Pipe-Table LLM Parsing** | Extracts recommendations/risks from LLM tables | `_parse_pipe_table()` |
| 28 | **Section Extraction** | Markdown header-based section parsing | `_extract_section()` |
| 29 | **News Sentiment Filtering** | Market Specialist filters negative news (sentiment < -0.2) | `MarketSpecialist.analyse()` |
| 30 | **Prohibited Phrase Detection** | "guaranteed to", "100% certain" flagged instantly | Rule-based compliance |
| 31 | **Forward-Looking Statement Detection** | "will grow", "will achieve" flagged | Rule-based compliance |
| 32 | **12 Automated Tests** | Data sources, specialists, compliance, report output | `tests/test_pipeline.py` |
| 33 | **E2E Demo Script** | Full pipeline without FastAPI | `demo_e2e.py` |
| 34 | **Service Bus Abstraction** | Local queue / Azure Service Bus transparent switch | `shared/service_bus.py` |
| 35 | **Data Envelope Pattern** | BriefingResult accumulates all pipeline outputs | Single response object |

---

## Prerequisites

<details>
<summary><strong>macOS</strong></summary>

```bash
# Python 3.11+
brew install python@3.11

# Verify
python3.11 --version
# Python 3.11.x

# Docker (optional — for containerised deployment)
brew install --cask docker

# Azure CLI (optional — for Azure resource provisioning)
brew install azure-cli
```

</details>

<details>
<summary><strong>Windows</strong></summary>

```powershell
# Python 3.11+ from python.org
winget install Python.Python.3.11

# Verify
python --version
# Python 3.11.x

# Docker Desktop (optional)
winget install Docker.DockerDesktop

# Azure CLI (optional)
winget install Microsoft.AzureCLI
```

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
# Python 3.11+
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
# Python 3.11.x

# Docker (optional)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Azure CLI (optional)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

</details>

### Required Services

| Service | Required | Purpose | Free Tier |
|---------|----------|---------|-----------|
| **Azure OpenAI** | No (has fallbacks) | GPT-4o for specialist analysis, synthesis, compliance | Pay-per-token |
| **Azure Cosmos DB** | No | Persistent briefing storage | 1000 RU/s free |
| **Azure Service Bus** | No | Async messaging (remote mode) | Basic tier available |

---

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/maneeshkumar52/executive-briefing-system.git
cd executive-briefing-system
```

**Expected output:**
```
Cloning into 'executive-briefing-system'...
remote: Enumerating objects: 62, done.
remote: Counting objects: 100% (62/62), done.
Receiving objects: 100% (62/62), done.
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows
```

**Expected output:**
```
(.venv) $ python --version
Python 3.11.x
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Collecting fastapi==0.115.0
Collecting uvicorn[standard]==0.30.6
Collecting pydantic==2.9.2
Collecting pydantic-settings==2.5.2
Collecting openai==1.51.0
Collecting azure-cosmos==4.7.0
Collecting structlog==24.4.0
Collecting httpx==0.27.2
Collecting pytest==8.3.3
Collecting pytest-asyncio==0.24.0
Successfully installed fastapi-0.115.0 uvicorn-0.30.6 ...
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials (or leave defaults for local-mode with fallbacks):

```env
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your-key-here
COSMOS_DATABASE=executive-briefings
COSMOS_CONTAINER=briefings
SERVICE_BUS_CONNECTION_STRING=your-connection-string
LOCAL_MODE=true
```

### 5. Start the Server

```bash
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
{"event": "executive_briefing_system_starting", "level": "info", "timestamp": "2024-11-15T14:00:00Z"}
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
```

### 6. Health Check

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status": "healthy", "service": "executive-briefing-system", "active_briefings": 0}
```

### 7. Run a Briefing (Synchronous)

```bash
curl -X POST http://localhost:8000/api/v1/briefing/sync \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Q4 2024 Executive Performance Review",
    "date_range": "Q4 2024 (October - December 2024)",
    "requester": "CEO",
    "requester_email": "ceo@company.com"
  }'
```

**Expected output (abbreviated):**
```json
{
  "run_id": "a1b2c3d4",
  "status": "complete",
  "topic": "Q4 2024 Executive Performance Review",
  "synthesis": {
    "executive_summary": "The company delivered revenue of $2400M...",
    "key_metrics_dashboard": { "Revenue": "$2,400.0M (12.4% YoY)", ... },
    "recommendations": [{ "action": "...", "owner": "CRO", "timeline": "6 weeks", "priority": "High" }],
    "risk_register": [{ "risk": "...", "likelihood": "High", "impact": "High", "mitigation": "..." }]
  },
  "compliance": { "approved": true, "required_disclaimers": [...] },
  "phase_timings": { "phase1_data_fetch": 0.15, "phase2_specialist_analysis": 3.21, ... },
  "total_pipeline_time_seconds": 6.94
}
```

### 8. Run a Briefing (Async + Polling)

```bash
# Start briefing (returns immediately)
curl -X POST http://localhost:8000/api/v1/briefing \
  -H "Content-Type: application/json" \
  -d '{"topic": "Q4 2024 Review", "requester": "CEO"}'
# → {"run_id": "a1b2c3d4", "status": "pending", ...}

# Poll status
curl http://localhost:8000/api/v1/briefing/a1b2c3d4/status
# → {"run_id": "a1b2c3d4", "status": "analysing", "phase_timings": {...}}

# Get full result when complete
curl http://localhost:8000/api/v1/briefing/a1b2c3d4

# Get formatted markdown
curl http://localhost:8000/api/v1/briefing/a1b2c3d4/markdown
```

### 9. Run E2E Demo (No Server Required)

```bash
python demo_e2e.py
```

Runs the full 5-phase pipeline directly, prints first 30 lines of the formatted briefing.

---

## Project Structure

```
executive-briefing-system/
├── .env.example                              # Environment variable template
├── demo_e2e.py                               # End-to-end demo (no server needed)
├── pyproject.toml                            # Python project config + pytest settings
├── requirements.txt                          # Python dependencies (10 packages)
│
├── orchestrator/                             # Pipeline orchestration layer
│   ├── __init__.py
│   ├── main.py                               # FastAPI app, 6 endpoints, lifespan
│   ├── pipeline.py                           # BriefingPipeline — 5-phase execution
│   └── report_generator.py                   # Markdown report renderer
│
├── data_sources/                             # Enterprise data connectors
│   ├── __init__.py
│   ├── financial_connector.py                # FinancialData (Azure Synapse)
│   ├── customer_connector.py                 # CustomerData (Segment/Mixpanel)
│   ├── market_connector.py                   # MarketData (Crayon/Klue)
│   ├── hr_connector.py                       # HRData (Workday/BambooHR)
│   ├── ops_connector.py                      # OperationalData (Datadog/PagerDuty)
│   └── news_connector.py                     # NewsItems (Feedly/Meltwater)
│
├── specialists/                              # C-Suite specialist agents
│   ├── __init__.py
│   ├── base_specialist.py                    # BaseSpecialist ABC — shared LLM infra
│   ├── financial_specialist.py               # CFO — revenue, margins, cash flow
│   ├── market_specialist.py                  # CSO — competitive intelligence
│   ├── operations_specialist.py              # COO — uptime, SLAs, incidents
│   ├── people_specialist.py                  # CPO — talent, engagement, hiring
│   └── risk_specialist.py                    # CRO — cross-domain risk matrix
│
├── synthesiser/                              # Report synthesis
│   ├── __init__.py
│   ├── agent.py                              # SynthesiserAgent — 341 lines, largest module
│   └── prompts.py                            # EXECUTIVE_SYNTHESIS_PROMPT
│
├── compliance_gate/                          # Dual-layer compliance
│   ├── __init__.py
│   └── agent.py                              # Rule-based + LLM compliance review
│
├── shared/                                   # Shared infrastructure
│   ├── __init__.py
│   ├── models.py                             # 12 Pydantic models
│   ├── config.py                             # Settings + OpenAI client factory
│   ├── logging_config.py                     # Structured JSON logging (structlog)
│   └── service_bus.py                        # Dual-mode message queue
│
├── tests/                                    # Test suite
│   ├── __init__.py
│   └── test_pipeline.py                      # 12 async test cases
│
└── infra/                                    # Deployment infrastructure
    ├── Dockerfile                            # Python 3.11 slim + HEALTHCHECK
    └── docker-compose.yml                    # Single-command deployment
```

### Module Responsibility Matrix

| Module | Responsibility | Key Classes/Functions | Lines |
|--------|---------------|----------------------|-------|
| `orchestrator/main.py` | FastAPI app, 6 endpoints, background tasks | `create_briefing()`, `_run_pipeline_task()` | 160 |
| `orchestrator/pipeline.py` | 5-phase pipeline with timing | `BriefingPipeline.run()` | 201 |
| `orchestrator/report_generator.py` | Markdown report formatting | `ReportGenerator.generate_markdown()` | 84 |
| `data_sources/*.py` | 6 enterprise data connectors | `*Connector.fetch()` | 189 |
| `specialists/base_specialist.py` | Shared LLM infrastructure (ABC) | `_call_llm()`, `_extract_key_findings()` | 60 |
| `specialists/financial_specialist.py` | Revenue, margins, cash flow analysis | `FinancialSpecialist.analyse()` | 61 |
| `specialists/market_specialist.py` | Competitive intelligence + news filtering | `MarketSpecialist.analyse()` | 70 |
| `specialists/operations_specialist.py` | Uptime, SLAs, incident analysis | `OperationsSpecialist.analyse()` | 69 |
| `specialists/people_specialist.py` | Talent, engagement, hiring analysis | `PeopleSpecialist.analyse()` | 69 |
| `specialists/risk_specialist.py` | Cross-domain enterprise risk matrix | `RiskSpecialist.analyse()` | 93 |
| `synthesiser/agent.py` | Multi-specialist consolidation + fallbacks | `SynthesiserAgent.synthesise()` | 341 |
| `synthesiser/prompts.py` | Executive synthesis prompt template | `EXECUTIVE_SYNTHESIS_PROMPT` | 33 |
| `compliance_gate/agent.py` | Dual-layer compliance review | `ComplianceGate.review()` | 158 |
| `shared/models.py` | 12 typed data contracts | All Pydantic models | 136 |
| `shared/config.py` | Settings + OpenAI client | `get_settings()`, `get_openai_client()` | 37 |
| `shared/service_bus.py` | Dual-mode message queue | `ServiceBusHelper` | 40 |
| `tests/test_pipeline.py` | 12 async test cases | All test functions | 326 |

---

## Specialist Agents

### Agent Architecture

```
BaseSpecialist (ABC)
├── _call_llm(system_prompt, user_prompt) → str
│   ↳ Azure OpenAI GPT-4o, temperature=0.3, max_tokens=600
│   ↳ Returns "[Analysis unavailable due to: ErrorType]" on failure
├── _extract_key_findings(text, max_findings=4) → List[str]
│   ↳ Parses "- ", "* ", "•" prefixed lines; fallback: sentence splitting
└── analyse(data: CompanyData) → SpecialistAnalysis  [ABSTRACT]

         ┌─────────────────────┐
         │   BaseSpecialist    │
         │   (ABC)             │
         ├─────────────────────┤
         │ _call_llm()         │
         │ _extract_findings() │
         │ analyse() [abstract]│
         └────────┬────────────┘
                  │
    ┌─────────────┼─────────────┐─────────────┐─────────────┐
    │             │             │             │             │
    ▼             ▼             ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Financial│ │ Market  │ │  Ops    │ │ People  │ │  Risk   │
│(CFO)    │ │ (CSO)   │ │ (COO)   │ │ (CPO)   │ │ (CRO)   │
│conf:0.88│ │conf:0.82│ │conf:0.90│ │conf:0.85│ │conf:0.87│
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Specialist Details

| Specialist | C-Suite Persona | Data Domains | Confidence | Risk Flag Count |
|-----------|----------------|-------------|------------|-----------------|
| **FinancialSpecialist** | Chief Financial Officer | `FinancialData` | 0.88 | 2 |
| **MarketSpecialist** | Chief Strategy Officer | `MarketData` + `news` (negative sentiment filtered) | 0.82 | 2 |
| **OperationsSpecialist** | Chief Operations Officer | `OperationalData` | 0.90 | 3 |
| **PeopleSpecialist** | Chief People Officer | `HRData` | 0.85 | 3 |
| **RiskSpecialist** | Chief Risk Officer | ALL data domains (cross-domain) | 0.87 | 4 |

### Risk Flag Thresholds (14 Total)

| Specialist | Condition | Risk Flag |
|-----------|-----------|-----------|
| Financial | `operating_margin_pct < 20.0` | Operating margin below 20% threshold |
| Financial | `yoy_cost_growth_pct > yoy_revenue_growth_pct` | Cost growth exceeds revenue growth — margin compression risk |
| Market | `yoy_share_change_pct < 0` | Market share declining |
| Market | `competitor_1_share_pct > 35.0` | Dominant competitor holds X.X% share |
| Operations | `system_uptime_pct < 99.9` | System uptime below 99.9% SLA target |
| Operations | `critical_incidents > 0` | X critical incident(s) require root cause analysis |
| Operations | `sla_compliance_pct < 99.0` | SLA compliance below 99% contractual threshold |
| People | `voluntary_turnover_rate_pct > 12.0` | Voluntary turnover exceeds 12% risk threshold |
| People | `employee_engagement_score < 65.0` | Engagement score below 65-point floor |
| People | `offer_acceptance_rate_pct < 80.0` | Offer acceptance rate below 80% benchmark |
| Risk | Any news `sentiment < -0.4` | Negative competitor signal: "{headline}" |
| Risk | `critical_incidents > 0` | Operational risk: reputational and contractual exposure |
| Risk | `yoy_cost_growth_pct > yoy_revenue_growth_pct` | Financial risk: margin contraction trajectory |
| Risk | `yoy_share_change_pct < 0` | Strategic risk: market share declining |

### Mock News Data

| # | Headline | Source | Sentiment | Competitor |
|---|----------|--------|-----------|------------|
| 1 | TechRival Corp announces $500M AI investment | FT | -0.6 | TechRival Corp |
| 2 | CloudLeader Inc loses 3 major enterprise contracts | Reuters | +0.7 | CloudLeader Inc |
| 3 | StartupX acquired by GlobalTech for $2.1B | TechCrunch | -0.3 | GlobalTech |
| 4 | EU AI Act compliance deadline set for Q3 2025 | EU Official Journal | -0.1 | Industry-wide |
| 5 | ESG ratings agency upgrades sector to 'Positive' | Bloomberg | +0.8 | None |

---

## Compliance Gate

### Dual-Layer Architecture

```
Synthesised Briefing
       │
       ├──► Layer 1: RULE-BASED SCANNING (deterministic)
       │    ├── Prohibited phrases: "will guarantee", "guaranteed to",
       │    │   "certain to", "definitely will", "100% certain"
       │    └── Forward-looking triggers: "will grow", "will achieve",
       │        "will deliver", "will increase"
       │
       ├──► Layer 2: LLM REVIEW (GPT-4o, temp=0.1)
       │    ├── Forward-looking statement hedging check
       │    ├── Speculative claims without data support
       │    ├── Language appropriateness for C-suite
       │    ├── Third-party data attribution
       │    └── Guaranteed outcome detection
       │
       └──► MERGE: all_issues + final_approved
            └── approved = llm_approved AND no critical/guarantee issues
```

### Required Disclaimers

Every approved briefing includes these 3 disclaimers:

```
1. Confidential — For C-Suite Distribution Only
2. Past performance is not indicative of future results
3. This briefing contains forward-looking statements subject to material risks
```

---

## API Reference

### Endpoints

| Method | Path | Description | Async |
|--------|------|-------------|-------|
| `POST` | `/api/v1/briefing` | Start briefing pipeline (background task) | Yes |
| `POST` | `/api/v1/briefing/sync` | Run full pipeline synchronously | No |
| `GET` | `/api/v1/briefing/{run_id}` | Retrieve full briefing result | — |
| `GET` | `/api/v1/briefing/{run_id}/status` | Lightweight status + phase timings | — |
| `GET` | `/api/v1/briefing/{run_id}/markdown` | Get formatted briefing document | — |
| `GET` | `/health` | Liveness probe with active briefing count | — |

### `POST /api/v1/briefing`

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | No | `"Q4 2024 Executive Performance Review"` | Briefing topic |
| `date_range` | string | No | `"Q4 2024 (October - December 2024)"` | Temporal scope |
| `requester` | string | No | `"CEO"` | Who requested the briefing |
| `requester_email` | string | No | `"ceo@company.com"` | Requester email for audit |

**Response:** `BriefingResult` with `status: "pending"` — pipeline runs in background.

### `GET /api/v1/briefing/{run_id}/status`

```json
{
  "run_id": "a1b2c3d4",
  "status": "analysing",
  "total_pipeline_time_seconds": 3.21,
  "phase_timings": {
    "phase1_data_fetch": 0.15,
    "phase2_specialist_analysis": 3.06
  }
}
```

### `GET /health`

```json
{"status": "healthy", "service": "executive-briefing-system", "active_briefings": 2}
```

---

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | No | `placeholder` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | No | `placeholder` | API key for Azure OpenAI |
| `AZURE_OPENAI_DEPLOYMENT` | No | `gpt-4o` | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | No | `2024-02-01` | API version |
| `COSMOS_ENDPOINT` | No | `placeholder` | Cosmos DB endpoint URL |
| `COSMOS_KEY` | No | `placeholder` | Cosmos DB auth key |
| `COSMOS_DATABASE` | No | `executive-briefings` | Cosmos DB database name |
| `COSMOS_CONTAINER` | No | `briefings` | Cosmos DB container name |
| `SERVICE_BUS_CONNECTION_STRING` | No | `placeholder` | Azure Service Bus connection |
| `LOCAL_MODE` | No | `true` | Use in-memory queues vs Service Bus |

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

**Expected output:**
```
========================= test session starts =========================
platform darwin -- Python 3.11.x, pytest-8.3.3, pluggy-1.5.0
plugins: asyncio-0.24.0
asyncio: mode=auto
collected 12 items

tests/test_pipeline.py::test_financial_connector_returns_data       PASSED  [  8%]
tests/test_pipeline.py::test_customer_connector_returns_data        PASSED  [ 16%]
tests/test_pipeline.py::test_market_connector_returns_data          PASSED  [ 25%]
tests/test_pipeline.py::test_hr_connector_returns_data              PASSED  [ 33%]
tests/test_pipeline.py::test_ops_connector_returns_data             PASSED  [ 41%]
tests/test_pipeline.py::test_news_connector_returns_five_items      PASSED  [ 50%]
tests/test_pipeline.py::test_data_models_valid                      PASSED  [ 58%]
tests/test_pipeline.py::test_report_generator_markdown              PASSED  [ 66%]
tests/test_pipeline.py::test_report_generator_includes_disclaimers  PASSED  [ 75%]
tests/test_pipeline.py::test_compliance_gate_adds_disclaimers       PASSED  [ 83%]
tests/test_pipeline.py::test_compliance_gate_rule_based_checks      PASSED  [ 91%]
tests/test_pipeline.py::test_financial_specialist_builds_analysis   PASSED  [100%]

========================= 12 passed in 2.15s ===========================
```

### Test Coverage by Category

| Category | Tests | What They Verify |
|----------|-------|-----------------|
| **Data Sources** | 6 | Each connector returns valid typed data with correct ranges |
| **Integration** | 1 | CompanyData assembles correctly from all connectors |
| **Report Output** | 2 | Markdown contains all sections, includes disclaimers |
| **Compliance** | 2 | Required disclaimers appended; prohibited phrases detected |
| **Specialist** | 1 | FinancialSpecialist returns valid SpecialistAnalysis with mocked LLM |

---

## Deployment

### Docker

```bash
cd infra
docker-compose up --build
```

**Expected output:**
```
Creating executive-briefing ... done
Attaching to executive-briefing
executive-briefing | {"event": "executive_briefing_system_starting", ...}
executive-briefing | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Dockerfile Details

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Decision | Rationale |
|----------|-----------|
| `python:3.11-slim` | Minimal image size, no unnecessary packages |
| Built-in `HEALTHCHECK` | Container orchestrators (Docker, Kubernetes) auto-detect health |
| `--start-period=10s` | Allows FastAPI + pipeline initialisation time |
| `--no-cache-dir` | Reduces image size by ~30MB |

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|---------|
| `openai.AuthenticationError` | Invalid Azure OpenAI key | Verify `AZURE_OPENAI_API_KEY` in `.env`; or run with defaults (fallback mode) |
| `[Analysis unavailable due to: AuthenticationError]` | LLM call failed | System continues with deterministic fallbacks — this is expected without credentials |
| `status: "failed"` in response | Pipeline exception | Check server logs for traceback; usually a configuration issue |
| `status: "pending"` indefinitely | Background task stuck | Use `/api/v1/briefing/sync` endpoint for debugging |
| `Connection refused :8000` | Server not running | Run `uvicorn orchestrator.main:app --port 8000` |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` in active venv |
| `pydantic.ValidationError` | Invalid request body | Check field types match `BriefingRequest` schema |
| `active_briefings: 0` but expected results | Briefing completed and stored | Use `GET /api/v1/briefing/{run_id}` to retrieve result |
| Compliance `approved: false` | Report contains prohibited phrases | Review executive summary for "will guarantee", "certain to", etc. |
| Missing recommendations in synthesis | LLM returned unexpected format | Pipe-table parser fell back; check synthesiser logs |
| Docker health check failing | App slow to start | Increase `start_period` in docker-compose healthcheck |
| Empty `phase_timings` | Pipeline failed early | Check which phase failed via status endpoint |

---

## Azure Production Mapping

### Resource Mapping

| Component | Azure Service | SKU/Tier | Purpose |
|-----------|--------------|----------|---------|
| **LLM Engine** | Azure OpenAI Service | GPT-4o deployment | 8 agent roles (5 specialists + synthesiser + compliance + report) |
| **Report Storage** | Azure Cosmos DB | Serverless | Persistent briefing storage with run_id retrieval |
| **Message Queue** | Azure Service Bus | Standard | Async pipeline orchestration (remote mode) |
| **Container Host** | Azure Container Apps | Consumption | Serverless container hosting for FastAPI |
| **Container Registry** | Azure Container Registry | Basic | Docker image storage |
| **Secrets** | Azure Key Vault | Standard | API keys, connection strings |
| **Monitoring** | Azure Monitor + App Insights | — | Structured log ingestion, phase timing metrics |
| **Identity** | Managed Identity | System-assigned | Passwordless auth to all services |

### Data Connector Production Targets

| Connector | Mock Source | Production Target |
|-----------|-----------|------------------|
| `FinancialConnector` | Hardcoded `FinancialData()` | Azure Synapse Analytics |
| `CustomerConnector` | Hardcoded `CustomerData()` | Segment / Mixpanel API |
| `MarketConnector` | Hardcoded `MarketData()` | Crayon / Klue API |
| `HRConnector` | Hardcoded `HRData()` | Workday / BambooHR API |
| `OpsConnector` | Hardcoded `OperationalData()` | Datadog / PagerDuty API |
| `NewsConnector` | 5 mock `NewsItem` objects | Feedly / Meltwater API |

### Production Checklist

- [ ] **Azure OpenAI**: Deploy GPT-4o model, note endpoint + deployment name
- [ ] **Cosmos DB**: Create account + `executive-briefings` database + `briefings` container
- [ ] **Key Vault**: Store all API keys and connection strings
- [ ] **Container Apps**: Deploy container with managed identity
- [ ] **Managed Identity**: Grant roles — Cognitive Services OpenAI User, Cosmos DB Data Contributor
- [ ] **Data Connectors**: Replace mock connectors with real API integrations (Synapse, Segment, Crayon, Workday, Datadog, Feedly)
- [ ] **CORS**: Restrict `allow_origins` from `["*"]` to specific frontend domains
- [ ] **Authentication**: Add API key or OAuth middleware to endpoints
- [ ] **Rate Limiting**: Add request throttling for `/api/v1/briefing`
- [ ] **Set `LOCAL_MODE=false`** for Service Bus distributed execution
- [ ] **Monitoring**: Configure App Insights for phase timing dashboards

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.0 | REST API framework |
| `uvicorn[standard]` | 0.30.6 | ASGI server with HTTP/2 support |
| `pydantic` | 2.9.2 | Data validation / typed models |
| `pydantic-settings` | 2.5.2 | Settings management from environment |
| `openai` | 1.51.0 | Azure OpenAI GPT-4o client (async) |
| `azure-cosmos` | 4.7.0 | Cosmos DB persistence |
| `structlog` | 24.4.0 | Structured JSON logging |
| `httpx` | 0.27.2 | HTTP client |
| `pytest` | 8.3.3 | Test framework |
| `pytest-asyncio` | 0.24.0 | Async test support |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**[⬆ Back to Top](#executive-briefing-system)**

*Part of [Prompt to Production](https://github.com/maneeshkumar52) — Chapter 20, Project 5*

</div>