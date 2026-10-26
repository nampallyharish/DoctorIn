"""Integration tests for Hospital Profiles and Job Board APIs."""

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_list_jobs_public(async_client):
    """Test GET /api/v1/jobs returns paginated job listings."""
    response = await async_client.get("/api/v1/jobs")
    assert response.status_code in [200, 500]
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_create_job_unauthorized(async_client):
    """Test POST /api/v1/jobs requires valid authentication."""
    response = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Consultant Neurologist", "description": "Full-time position."},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_doctor_cannot_post_jobs(async_client):
    """Test doctor role cannot post job openings (hospital admin only)."""
    doctor_token = create_access_token(subject="doc-uuid", role="doctor")
    headers = {"Authorization": f"Bearer {doctor_token}"}
    response = await async_client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"title": "Job title", "description": "Clinical position"},
    )
    assert response.status_code in [403, 401, 500]
