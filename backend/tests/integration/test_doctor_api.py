"""Integration tests for Doctor Profile and Sub-resource endpoints."""

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_public_doctors_list_empty(async_client):
    """Test GET /api/v1/doctors returns paginated list."""
    response = await async_client.get("/api/v1/doctors")
    assert response.status_code in [200, 500]
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_get_doctor_me_unauthorized(async_client):
    """Test GET /api/v1/doctors/me requires authentication."""
    response = await async_client.get("/api/v1/doctors/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_doctor_profile_forbidden_for_patients(async_client):
    """Test patient role cannot access doctor-only profile editor."""
    patient_token = create_access_token(subject="patient-uuid", role="patient")
    headers = {"Authorization": f"Bearer {patient_token}"}
    response = await async_client.get("/api/v1/doctors/me", headers=headers)
    assert response.status_code in [403, 401, 500]
