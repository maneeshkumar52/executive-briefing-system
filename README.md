# Executive Decision Intelligence Briefing System

**Project 10, Chapter 20 of "Prompt to Production" by Maneesh Kumar**

A production-grade, multi-source, multi-agent executive briefing system that aggregates data from six business domains, runs five concurrent specialist AI analysis agents, synthesises a board-quality briefing with actionable insights, and applies a compliance gate before C-suite delivery. Total pipeline target: under 3 minutes.

---

## Architecture

```
BriefingRequest
     |
+----v--------------------------------------------+
| Phase 1: Data Ingestion (parallel, ~0.15s local) |
| Financial | Customer | Market | HR | Ops | News  |
+----+--------------------------------------------+
     |
+----v--------------------------------------------+
| Phase 2: Specialist Analysis (parallel, 5 agents)|
| Financial | Market | Ops | People | Risk         |
+----+--------------------------------------------+
     |
+----v------------------------+
| Phase 3: Synthesis Agent    |
| (Executive Briefing Draft)  |
+----+------------------------+
     |
+----v--------------------+
| Phase 4: Compliance Gate |
| (Rule + LLM Review)      |
+----+--------------------+
     |
+----v---------------------+
| Phase 5: Report Generator |
| (Markdown Output)         |
+--------------------------+
```

## Data Sources (Phase 1)

| Connector | Domain | Production System |
|-----------|--------|-------------------|
| `FinancialConnector` | Revenue, margins, FCF | Azure Synapse Analytics |
| `CustomerConnector` | NPS, churn, ARPU | Segment / Mixpanel |
| `MarketConnector` | Market share, competitors | Crayon / Klue |
| `HRConnector` | Headcount, turnover, engagement | Workday / BambooHR |
| `OpsConnector` | Uptime, incidents, SLA | Datadog / PagerDuty |
| `NewsConnector` | Competitor and market news | Feedly / Meltwater |

## Specialist Agents (Phase 2)

| Agent | Role | Key Analysis |
|-------|------|-------------|
| `FinancialSpecialist` | CFO perspective | Revenue, margins, cash flow |
| `MarketSpecialist` | CSO perspective | Competitive positioning, share |
| `OperationsSpecialist` | COO perspective | Reliability, incidents, velocity |
| `PeopleSpecialist` | CPO perspective | Talent, engagement, capacity |
| `RiskSpecialist` | CRO perspective | Enterprise risk matrix |

---

## Prerequisites

- Python 3.11+
- Azure OpenAI API access (or set `LOCAL_MODE=true` to run with mock-only LLM fallbacks)

---

## Local Setup

```bash
# Clone / navigate to the project
cd executive-briefing-system

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment (LOCAL_MODE=true skips real Azure calls)
cp .env.example .env

# Start the API server
uvicorn orchestrator.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

---

## API Usage

### Start an async briefing (returns immediately)

```bash
curl -X POST http://localhost:8000/api/v1/briefing \
  -H "Content-Type: application/json" \
  -d '{"topic": "Q4 2024 Executive Review", "requester": "CEO"}'
```

Response:
```json
{"run_id": "a1b2c3d4", "status": "pending", ...}
```

### Poll for results

```bash
curl http://localhost:8000/api/v1/briefing/a1b2c3d4
```

### Check status

```bash
curl http://localhost:8000/api/v1/briefing/a1b2c3d4/status
```

### Run synchronously (waits for full completion)

```bash
curl -X POST http://localhost:8000/api/v1/briefing/sync \
  -H "Content-Type: application/json" \
  -d '{"topic": "Q4 2024 Executive Review", "requester": "CEO"}'
```

### Get formatted markdown

```bash
curl http://localhost:8000/api/v1/briefing/a1b2c3d4/markdown
```

### Health check

```bash
curl http://localhost:8000/health
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests run without real Azure credentials — all LLM calls are mocked.

---

## Docker

```bash
# Build and run with Docker Compose
cd infra
docker-compose up --build
```

---

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | placeholder | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | placeholder | API key |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o` | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | `2024-02-01` | API version |
| `COSMOS_ENDPOINT` | placeholder | Cosmos DB endpoint (production) |
| `COSMOS_KEY` | placeholder | Cosmos DB key (production) |
| `SERVICE_BUS_CONNECTION_STRING` | placeholder | Azure Service Bus (production) |
| `LOCAL_MODE` | `true` | Use in-process queues, no Azure infra needed |

---

## Pipeline Output

A complete briefing includes:

- **Executive Summary** — 3 focused paragraphs: performance, challenges, outlook
- **Key Metrics Dashboard** — one-liner per domain (10 metrics)
- **Strategic Insights** — 4-5 cross-functional insights
- **Recommendations Table** — Action | Owner | Timeline | Priority
- **Risk Register Table** — Risk | Likelihood | Impact | Mitigation
- **Compliance Disclaimers** — Required for C-suite distribution
- **Pipeline Performance** — Per-phase timing breakdown

---

## Project Structure

```
executive-briefing-system/
├── shared/              # Config, models, logging, service bus
├── data_sources/        # 6 data connectors (financial, customer, market, hr, ops, news)
├── specialists/         # 5 AI specialist agents + base class
├── synthesiser/         # Executive briefing synthesis agent
├── compliance_gate/     # Pre-delivery compliance review agent
├── orchestrator/        # FastAPI app, 5-phase pipeline, report generator
├── tests/               # pytest test suite (no Azure credentials needed)
├── infra/               # Dockerfile and docker-compose.yml
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

*"Prompt to Production" — Maneesh Kumar | Chapter 20, Project 10*
