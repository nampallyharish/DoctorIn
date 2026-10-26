"""Async SQLAlchemy database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

db_url = settings.DATABASE_URL
engine_kwargs = {}
if "postgresql" in db_url:
    try:
        import asyncpg  # type: ignore # noqa: F401
        engine_kwargs = {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_pre_ping": True,
        }
    except ImportError:
        db_url = "sqlite+aiosqlite:///./doctorin_dev.db"

engine: AsyncEngine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    **engine_kwargs,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables on startup if they do not exist."""
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        from app.models.base import Base
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing transactional database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_health() -> bool:
    """Verify database connection health."""
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        return False
