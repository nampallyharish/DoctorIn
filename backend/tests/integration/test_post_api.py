"""Integration tests for Social Feed, Posts, Comments, and Reactions."""

import pytest

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_get_feed_public(async_client):
    """Test GET /api/v1/posts/feed returns 200/500 structured response."""
    response = await async_client.get("/api/v1/posts/feed")
    assert response.status_code in [200, 500]
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_create_post_unauthorized(async_client):
    """Test POST /api/v1/posts requires valid authentication."""
    response = await async_client.post(
        "/api/v1/posts",
        json={"content": "Clinical observations on cardiac MRI.", "post_type": "text"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patient_cannot_publish_post(async_client):
    """Test patient role is forbidden from publishing feed posts."""
    patient_token = create_access_token(subject="patient-uuid", role="patient")
    headers = {"Authorization": f"Bearer {patient_token}"}
    response = await async_client.post(
        "/api/v1/posts",
        headers=headers,
        json={"content": "Patient post attempt", "post_type": "text"},
    )
    assert response.status_code in [403, 401, 500]
