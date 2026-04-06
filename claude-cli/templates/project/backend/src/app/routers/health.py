"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health", summary="Health check")
async def health_check() -> dict:
    """Return service status."""
    return {"status": "ok"}
