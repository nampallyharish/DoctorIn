"""Unit tests for security utilities and health endpoints."""

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_otp,
    hash_password,
    hash_token,
    verify_password,
)


def test_password_hashing():
    """Test bcrypt hashing and verification."""
    password = "SecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_access_token_lifecycle():
    """Test JWT creation, claim inclusion, and decoding."""
    sub = "user-1234-uuid"
    role = "doctor"
    token = create_access_token(subject=sub, role=role, extra_claims={"is_verified": True})
    decoded = decode_access_token(token)

    assert decoded["sub"] == sub
    assert decoded["role"] == role
    assert decoded["is_verified"] is True
    assert decoded["type"] == "access"


def test_otp_generation():
    """Test 6-digit numeric OTP generation."""
    otp = generate_otp(6)
    assert len(otp) == 6
    assert otp.isdigit()


def test_token_hashing_consistency():
    """Test HMAC-SHA256 token hashing produces consistent hash."""
    raw = "test_raw_token_xyz"
    hash1 = hash_token(raw)
    hash2 = hash_token(raw)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex length


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """Test /api/v1/health liveness probe."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

