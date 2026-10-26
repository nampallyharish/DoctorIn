"""Comprehensive Integration Tests for the complete DoctorIn OTP flow."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_token
from app.models.user import OTPPurpose, OTPVerification


@pytest.mark.asyncio
async def test_full_otp_registration_and_verification_lifecycle(async_client):
    """
    Test complete lifecycle:
    1. Register user -> OTP generated and stored
    2. Enter incorrect OTP -> rejected with remaining attempts
    3. Enter correct OTP -> verification succeeds and tokens issued
    4. Verify session is active and user verified
    """
    email = f"dr.test_{datetime.now().timestamp()}@hospital.org"

    # Step 1: Register user
    reg_response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "role": "doctor",
            "full_name": "Dr. Test Lifecycle",
            "email": email,
            "password": "SecurePassword123!",
        },
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["identifier"] == email

    # Inspect database for the generated OTP
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OTPVerification)
            .where(OTPVerification.identifier == email, OTPVerification.purpose == OTPPurpose.REGISTRATION)
            .order_by(OTPVerification.created_at.desc())
        )
        otp_records = result.scalars().all()
        assert len(otp_records) == 1
        record = otp_records[0]
        assert record.verified_at is None
        assert record.attempts == 0
        exp = record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        assert exp > datetime.now(timezone.utc)

    # Step 2: Try incorrect OTP
    wrong_verify = await async_client.post(
        "/api/v1/auth/verify-otp",
        json={
            "identifier": email,
            "otp": "000000",
            "purpose": "registration",
        },
    )
    assert wrong_verify.status_code == 400
    wrong_data = wrong_verify.json()
    assert wrong_data["success"] is False
    assert wrong_data["errors"][0]["code"] == "INVALID_OTP"

    # Step 3: Verify with known OTP by setting hash in DB or extracting
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OTPVerification)
            .where(OTPVerification.identifier == email, OTPVerification.purpose == OTPPurpose.REGISTRATION)
        )
        active_record = result.scalar_one()
        active_record.otp_hash = hash_token("654321")
        await session.commit()

    # Submit correct OTP
    correct_verify = await async_client.post(
        "/api/v1/auth/verify-otp",
        json={
            "identifier": email,
            "otp": "654321",
            "purpose": "registration",
        },
    )
    assert correct_verify.status_code == 200
    verify_data = correct_verify.json()
    assert verify_data["success"] is True
    assert "access_token" in verify_data["data"]
    assert "refresh_token" in verify_data["data"]
    assert verify_data["data"]["role"] == "doctor"

    # Step 4: Verify that attempting to re-use the same verified OTP is rejected
    reuse_verify = await async_client.post(
        "/api/v1/auth/verify-otp",
        json={
            "identifier": email,
            "otp": "654321",
            "purpose": "registration",
        },
    )
    assert reuse_verify.status_code == 400
    assert reuse_verify.json()["errors"][0]["code"] == "NO_PENDING_OTP"


@pytest.mark.asyncio
async def test_otp_invalidation_on_new_request(async_client):
    """Verify that requesting a new OTP invalidates previous OTP records."""
    email = f"patient_{datetime.now().timestamp()}@example.com"

    # Register
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "role": "user",
            "full_name": "Patient Test",
            "email": email,
            "password": "SecurePassword123!",
        },
    )
    assert reg_res.status_code == 201

    # Set known hash on first OTP
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OTPVerification)
            .where(OTPVerification.identifier == email)
        )
        record1 = result.scalar_one()
        record1.otp_hash = hash_token("111111")
        # Backdate created_at to bypass 60s cooldown for testing
        record1.created_at = datetime.now(timezone.utc) - timedelta(seconds=70)
        await session.commit()

    # Request new OTP (resend)
    resend_res = await async_client.post(
        "/api/v1/auth/send-otp",
        json={"identifier": email, "purpose": "registration"},
    )
    assert resend_res.status_code == 200

    # Old OTP "111111" must fail
    old_verify = await async_client.post(
        "/api/v1/auth/verify-otp",
        json={"identifier": email, "otp": "111111", "purpose": "registration"},
    )
    assert old_verify.status_code == 400

    # Set known hash on newly created OTP and verify it succeeds
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OTPVerification)
            .where(OTPVerification.identifier == email, OTPVerification.verified_at.is_(None))
        )
        record2 = result.scalar_one()
        record2.otp_hash = hash_token("222222")
        await session.commit()

    new_verify = await async_client.post(
        "/api/v1/auth/verify-otp",
        json={"identifier": email, "otp": "222222", "purpose": "registration"},
    )
    assert new_verify.status_code == 200
    assert new_verify.json()["success"] is True
