import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.logging_config import configure_logging
from shared.models import BriefingRequest, BriefingResult, BriefingStatus
from orchestrator.pipeline import BriefingPipeline

configure_logging()
logger = structlog.get_logger()

# In-memory store for briefing results (use Cosmos DB in production)
BRIEFING_STORE: dict[str, BriefingResult] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("executive_briefing_system.starting")
    yield
    logger.info("executive_briefing_system.shutdown")


app = FastAPI(
    title="Executive Decision Intelligence Briefing System",
    description=(
        "Multi-agent executive briefing system from Prompt to Production, Chapter 20. "
        "Aggregates 6 data sources, runs 5 concurrent specialist agents, "
        "synthesises a board-quality briefing, and applies compliance review."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/api/v1/briefing",
    response_model=BriefingResult,
    summary="Start a briefing (async)",
    description=(
        "Enqueues a briefing pipeline run as a background task. "
        "Returns immediately with a run_id and PENDING status. "
        "Poll GET /api/v1/briefing/{run_id} for results."
    ),
)
async def create_briefing(
    request: BriefingRequest, background_tasks: BackgroundTasks
) -> BriefingResult:
    run_id = str(uuid.uuid4())[:8]
    initial = BriefingResult(
        run_id=run_id,
        status=BriefingStatus.PENDING,
        topic=request.topic,
        requested_by=request.requester,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    BRIEFING_STORE[run_id] = initial
    background_tasks.add_task(_run_pipeline_task, run_id, request)
    logger.info("briefing.enqueued", run_id=run_id, topic=request.topic)
    return initial


@app.post(
    "/api/v1/briefing/sync",
    response_model=BriefingResult,
    summary="Start a briefing (synchronous)",
    description=(
        "Runs the full briefing pipeline synchronously and returns the "
        "complete result. Suitable for testing or when the client can wait."
    ),
)
async def create_briefing_sync(request: BriefingRequest) -> BriefingResult:
    logger.info("briefing.sync_starting", topic=request.topic)
    result = await BriefingPipeline().run(request)
    BRIEFING_STORE[result.run_id] = result
    return result


@app.get(
    "/api/v1/briefing/{run_id}",
    response_model=BriefingResult,
    summary="Get briefing result",
)
async def get_briefing(run_id: str) -> BriefingResult:
    if run_id not in BRIEFING_STORE:
        raise HTTPException(
            status_code=404, detail=f"Briefing '{run_id}' not found"
        )
    return BRIEFING_STORE[run_id]


@app.get(
    "/api/v1/briefing/{run_id}/status",
    summary="Get briefing status",
)
async def get_briefing_status(run_id: str) -> dict:
    if run_id not in BRIEFING_STORE:
        raise HTTPException(status_code=404, detail="Briefing not found")
    b = BRIEFING_STORE[run_id]
    return {
        "run_id": run_id,
        "status": b.status,
        "total_time": b.total_pipeline_time_seconds,
        "phase_timings": b.phase_timings,
    }


@app.get(
    "/api/v1/briefing/{run_id}/markdown",
    summary="Get formatted markdown briefing",
)
async def get_briefing_markdown(run_id: str) -> dict:
    if run_id not in BRIEFING_STORE:
        raise HTTPException(status_code=404, detail="Briefing not found")
    b = BRIEFING_STORE[run_id]
    if b.formatted_briefing is None:
        raise HTTPException(
            status_code=202,
            detail=f"Briefing is still processing (status: {b.status})",
        )
    return {"run_id": run_id, "markdown": b.formatted_briefing}


@app.get("/health", summary="Health check")
async def health() -> dict:
    return {
        "status": "healthy",
        "service": "executive-briefing-system",
        "active_briefings": len(BRIEFING_STORE),
    }


async def _run_pipeline_task(run_id: str, request: BriefingRequest) -> None:
    """Background task: run the pipeline and update the store."""
    try:
        result = await BriefingPipeline().run(request)
        result.run_id = run_id
        BRIEFING_STORE[run_id] = result
        logger.info(
            "briefing.background_task_complete",
            run_id=run_id,
            status=result.status,
        )
    except Exception as e:
        logger.error(
            "briefing.background_task_failed", run_id=run_id, error=str(e)
        )
        if run_id in BRIEFING_STORE:
            BRIEFING_STORE[run_id].status = BriefingStatus.FAILED
