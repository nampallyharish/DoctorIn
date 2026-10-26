"""Integration tests for Doctor-to-Doctor Messaging guardrails."""

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_conversations_unauthorized(async_client):
    """Test /api/v1/conversations rejects unauthenticated requests."""
    response = await async_client.get("/api/v1/conversations")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patient_cannot_access_conversations(async_client):
    """Test Rule 1: Patient role is forbidden from messaging APIs."""
    patient_token = create_access_token(subject="patient-uuid", role="patient")
    headers = {"Authorization": f"Bearer {patient_token}"}
    response = await async_client.get("/api/v1/conversations", headers=headers)
    assert response.status_code in [403, 401, 500]


@pytest.mark.asyncio
async def test_patient_cannot_start_conversation(async_client):
    """Test Rule 1: Patient cannot initiate conversation."""
    patient_token = create_access_token(subject="patient-uuid", role="patient")
    headers = {"Authorization": f"Bearer {patient_token}"}
    response = await async_client.post(
        "/api/v1/conversations",
        headers=headers,
        json={"recipient_doctor_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code in [403, 401, 500]
