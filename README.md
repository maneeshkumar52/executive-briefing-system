# Executive Briefing System

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

AI-powered executive decision intelligence system for multi-source analysis, specialist synthesis, and decision-ready briefings — with 6 data source connectors, 5 specialist analysts, compliance gating, and async background processing.

## Architecture

```
Briefing Request
        │
        ▼
┌─────────────────────────────────────────────┐
│  FastAPI Service (:8000)                    │
│                                             │
│  BriefingPipeline (orchestrator)            │
│       │                                     │
│  Data Sources (parallel fetch):             │
│       ├──► FinancialConnector              │
│       ├──► MarketConnector                 │
│       ├──► NewsConnector                   │
│       ├──► HRConnector                     │
│       ├──► OpsConnector                    │
│       └──► CustomerConnector               │
│       │                                     │
│  Specialists (parallel analysis):           │
│       ├──► FinancialSpecialist             │
│       ├──► MarketSpecialist                │
│       ├──► OperationsSpecialist            │
│       ├──► PeopleSpecialist                │
│       └──► RiskSpecialist                  │
│       │                                     │
│  ComplianceGate ──► Validation             │
│       │                                     │
│  Synthesiser ──► Executive briefing         │
│  ReportGenerator ──► Formatted output       │
└─────────────────────────────────────────────┘
        │
        ▼
Cosmos DB (briefing storage) + Service Bus (async)
```

## Key Features

- **6 Data Source Connectors** — Financial, market, news, HR, operations, and customer data feeds
- **5 Specialist Analysts** — Financial, market, operations, people, and risk specialists analyze data in parallel
- **Compliance Gate** — Validates specialist outputs for factual consistency and bias
- **Report Generator** — Produces structured executive briefings with recommendations
- **Async Processing** — Background task execution with status polling via `GET /briefings/{id}`
- **Synthesiser with Prompts** — Dedicated prompt engineering in `prompts.py` for executive-grade output
- **Cosmos DB** — Briefing persistence with status tracking (pending → processing → completed)

## Step-by-Step Flow

### Step 1: Briefing Request
Executive submits a `BriefingRequest` with topic, scope, and urgency via `POST /briefings`.

### Step 2: Data Collection (Parallel)
`BriefingPipeline` triggers all 6 data source connectors in parallel to gather financial metrics, market data, news, HR stats, ops metrics, and customer sentiment.

### Step 3: Specialist Analysis (Parallel)
5 specialists analyze the collected data concurrently. Each extends `BaseSpecialist` and produces domain-specific insights.

### Step 4: Compliance Validation
`ComplianceGate` validates all specialist outputs against consistency rules.

### Step 5: Synthesis & Report
`Synthesiser` consolidates outputs into a unified briefing. `ReportGenerator` formats the final deliverable.

### Step 6: Status & Retrieval
Client polls `GET /briefings/{id}` for status. Completed briefings return the full `BriefingResult`.

## Repository Structure

```
executive-briefing-system/
├── orchestrator/
│   ├── main.py              # FastAPI entry point
│   ├── pipeline.py           # BriefingPipeline — multi-agent orchestration
│   └── report_generator.py   # Formatted report generation
├── data_sources/
│   ├── financial_connector.py
│   ├── market_connector.py
│   ├── news_connector.py
│   ├── hr_connector.py
│   ├── ops_connector.py
│   └── customer_connector.py
├── specialists/
│   ├── base_specialist.py    # BaseSpecialist ABC
│   ├── financial_specialist.py
│   ├── market_specialist.py
│   ├── operations_specialist.py
│   ├── people_specialist.py
│   └── risk_specialist.py
├── compliance_gate/
│   └── agent.py
├── synthesiser/
│   ├── agent.py
│   └── prompts.py
├── shared/
│   ├── config.py, models.py, service_bus.py, logging_config.py
├── tests/
│   └── test_pipeline.py
├── infra/
│   ├── Dockerfile
│   └── docker-compose.yml
├── demo_e2e.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
git clone https://github.com/maneeshkumar52/executive-briefing-system.git
cd executive-briefing-system
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Set LOCAL_MODE=true
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Model deployment (gpt-4o) |
| `LOCAL_MODE` | No | Run without Azure (default: true) |
| `COSMOS_ENDPOINT` | No | Cosmos DB for briefing storage |
| `SERVICE_BUS_CONNECTION_STRING` | No | Azure Service Bus for async |

## Testing

```bash
pytest -q
python demo_e2e.py
```

## License

MIT
