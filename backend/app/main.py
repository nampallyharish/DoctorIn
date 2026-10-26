"""FastAPI Application Factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.core.redis import close_redis, get_redis
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup
    setup_logging(debug=settings.DEBUG)
    logger.info(
        f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...",
        extra={"extra_data": {"port": settings.BACKEND_PORT, "version": settings.API_VERSION}},
    )

    from app.core.database import init_db
    try:
        await init_db()
    except Exception as db_exc:
        logger.warning(f"Could not initialize database tables: {db_exc}")

    try:
        # Initialize Redis connection pool
        await get_redis()
        logger.info("Redis connection initialized.")
    except Exception as exc:
        logger.warning(f"Could not connect to Redis during startup: {exc}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")
    await close_redis()
    logger.info("Redis connection closed. Shutdown complete.")


def create_application() -> FastAPI:
    """FastAPI Application Factory function."""
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Professional networking and discovery platform for medical professionals.",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # 1. Register Custom Middleware (Order: outermost executed first)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 3. Register Global Exception Handlers
    register_exception_handlers(app)

    # 4. Register Routers
    app.include_router(api_v1_router)

    # 5. Root & Health endpoints
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "tagline": "Connect with Verified Medical Professionals.",
            "version": "0.1.0",
            "docs": "/docs" if not settings.is_production else "disabled in production",
        }

    @app.get("/health", tags=["Health"], include_in_schema=True)
    async def health():
        from datetime import datetime, timezone
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "version": settings.API_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/reload-test", tags=["Health"], include_in_schema=False)
    async def reload_test():
        return {"auto_reload": "verified_live"}

    return app


app = create_application()
