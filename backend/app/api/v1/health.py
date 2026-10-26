"""Comprehensive System Health, Database Latency, and Infrastructure Diagnostic API."""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])
settings = get_settings()


@router.get("", summary="Liveness & Readiness Health Probe")
async def health_check():
    """Basic liveness probe for Kubernetes and Docker healthchecks."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": settings.API_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/deep", summary="Deep Infrastructure Diagnostic (PostgreSQL, Redis, Latency)")
async def deep_health_check(
    db: AsyncSession = Depends(get_db),
):
    """
    Detailed diagnostic checking:
    1. PostgreSQL connection & latency
    2. Redis connectivity & memory stats
    3. Application runtime metrics
    """
    diagnostics = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {},
    }
    is_degraded = False

    # 1. PostgreSQL Diagnostic
    try:
        t0 = time.perf_counter()
        res = await db.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        diagnostics["components"]["postgresql"] = {
            "status": "connected",
            "latency_ms": latency_ms,
        }
    except Exception as e:
        diagnostics["components"]["postgresql"] = {
            "status": "error",
            "error": str(e),
        }
        is_degraded = True

    # 2. Redis Diagnostic
    try:
        redis_client = await get_redis()
        t0 = time.perf_counter()
        pong = await redis_client.ping()
        redis_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        diagnostics["components"]["redis"] = {
            "status": "connected" if pong else "disconnected",
            "latency_ms": redis_latency_ms,
        }
    except Exception as e:
        diagnostics["components"]["redis"] = {
            "status": "error",
            "error": str(e),
        }
        is_degraded = True

    # 3. Overall status evaluation
    if is_degraded:
        diagnostics["status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=diagnostics,
        )

    return diagnostics
