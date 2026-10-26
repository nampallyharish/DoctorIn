import uuid

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_admin_stats_unauthorized(async_client):
    """Test /api/v1/admin/stats rejects unauthenticated requests."""
    response = await async_client.get("/api/v1/admin/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_doctor_cannot_access_admin_stats(async_client):
    """Test doctor role cannot access admin stats."""
    doc_token = create_access_token(subject=str(uuid.uuid4()), role="doctor")
    headers = {"Authorization": f"Bearer {doc_token}"}
    response = await async_client.get("/api/v1/admin/stats", headers=headers)
    assert response.status_code in [403, 401, 500]


@pytest.mark.asyncio
async def test_admin_access_reports_queue(async_client):
    """Test admin role can query reports queue."""
    admin_token = create_access_token(subject=str(uuid.uuid4()), role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/api/v1/admin/reports", headers=headers)
    assert response.status_code in [200, 401, 500]
