from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Health endpoint for readiness checks.
    return HealthResponse(status="ok", version="1.0.0")
