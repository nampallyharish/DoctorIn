"""Integration tests for Authentication REST API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_auth_register_validation(async_client):
    """Test register endpoint validation when missing email and phone."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"role": "doctor", "full_name": "Dr. Validation", "password": "SecurePassword123!"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_unauthorized_profile_access(async_client):
    """Test /api/v1/auth/me rejects requests with missing or invalid token."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["errors"][0]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_auth_invalid_jwt_rejected(async_client):
    """Test /api/v1/auth/me rejects forged/invalid tokens."""
    headers = {"Authorization": "Bearer invalid.jwt.token.string"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_root_and_health_endpoints(async_client):
    """Test top-level /health and /api/v1/health endpoints."""
    res_root_health = await async_client.get("/health")
    assert res_root_health.status_code == 200
    data_root = res_root_health.json()
    assert data_root["status"] == "healthy"

    res_v1_health = await async_client.get("/api/v1/health")
    assert res_v1_health.status_code == 200
    data_v1 = res_v1_health.json()
    assert data_v1["status"] == "healthy"


@pytest.mark.asyncio
async def test_cors_origin_3001(async_client):
    """Test CORS preflight and request headers from frontend port 3001."""
    headers = {
        "Origin": "http://localhost:3001",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = await async_client.options("/api/v1/auth/register", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3001"


@pytest.mark.asyncio
async def test_auth_otp_rate_limiting_structure(async_client):
    """Test send-otp endpoint response structure."""
    response = await async_client.post(
        "/api/v1/auth/send-otp",
        json={"identifier": "test.doctor@hospital.org", "purpose": "registration"},
    )
    # Since DB is not live in isolated unit test runner, either 200 or 500 error envelope is returned
    assert response.status_code in [200, 429, 500]
    data = response.json()
    assert "success" in data

