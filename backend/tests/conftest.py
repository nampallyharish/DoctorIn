"""Pytest fixtures for testing DoctorIn backend."""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import init_db
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Ensure database tables exist before tests run."""
    await init_db()


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
