import contextlib
import logging
import uuid

import fastapi

from app.server import dependencies
from app.server import models
from app.server.dependencies import verify_credentials
from app.server.service import RateLimitException, ServiceUnavailableException

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    logging.basicConfig(level=logging.INFO)
    dependencies.get_configs()
    dependencies.get_llm_adapter()
    yield


app = fastapi.FastAPI(
    title="Transcript Analysis API",
    description="""
    Welcome 🤗! This API lets you analyze conversation transcripts using an LLM and returns summaries with action items. All endpoints require Basic Auth.
    
    This app is hosted via Cloud Run from Google Cloud Platform, and the LLM is accessed through a secure API key stored in Secret Manager. The analysis results are stored in memory for simplicity, but you can easily swap this out for a database if needed.""",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[fastapi.Depends(verify_credentials)],
)


@app.exception_handler(RateLimitException)
async def rate_limit_handler(
    _request: fastapi.Request, exc: RateLimitException
) -> fastapi.Response:
    logger.error("Rate limit hit: %s", exc)
    return fastapi.responses.JSONResponse(
        status_code=429,
        content={"detail": "OpenAI rate limit reached, please retry later"},
    )


@app.exception_handler(ServiceUnavailableException)
async def service_unavailable_handler(
    _request: fastapi.Request, exc: ServiceUnavailableException
) -> fastapi.Response:
    logger.error("LLM service unavailable: %s", exc)
    return fastapi.responses.JSONResponse(
        status_code=503,
        content={"detail": "LLM service unreachable"},
    )


@app.get(
    "/analyses",
    response_model=models.AnalysisRecord,
    summary="Analyze a transcript",
    description="Accepts a plain-text transcript as a query parameter, runs LLM analysis, stores the result in memory, and returns it with a generated UUID.",
)
def analyze_transcript(
    transcript: str = fastapi.Query(
        ..., min_length=1, description="Plain-text transcript to analyze"
    ),
    service: dependencies.AnalysisService = fastapi.Depends(
        dependencies.get_analysis_service
    ),
) -> models.AnalysisRecord:
    return service.analyze(transcript)


@app.get(
    "/analyses/{analysis_id}",
    response_model=models.AnalysisRecord,
    summary="Retrieve a stored analysis",
    responses={404: {"description": "Analysis not found"}},
)
def get_analysis(
    analysis_id: uuid.UUID,
    service: dependencies.AnalysisService = fastapi.Depends(
        dependencies.get_analysis_service
    ),
) -> models.AnalysisRecord:
    record = service.get_analysis(analysis_id)
    if record is None:
        raise fastapi.HTTPException(
            status_code=404, detail=f"Analysis {analysis_id} not found"
        )
    return record


@app.post(
    "/analyses/batch",
    response_model=models.BatchResponse,
    summary="Analyze multiple transcripts concurrently",
    description="Accepts a JSON body with a list of transcripts. Each is processed concurrently via asyncio.",
    responses={422: {"description": "One or more transcripts are blank"}},
)
async def analyze_batch(
    request: models.BatchRequest,
    service: dependencies.AnalysisService = fastapi.Depends(
        dependencies.get_analysis_service
    ),
) -> models.BatchResponse:
    results = await service.analyze_batch(request.transcripts)
    return models.BatchResponse(results=results)
