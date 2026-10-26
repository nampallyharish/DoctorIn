"""Unit tests for DoctorIn OTP lifecycle, expiration, security, and provider dispatch."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import get_settings
from app.core.exceptions import InvalidOTPError, OTPExpiredError
from app.core.security import generate_otp, hash_token
from app.models.user import OTPPurpose, OTPVerification
from app.services.otp_service import (
    DevelopmentOTPProvider,
    EmailOTPProvider,
    OTPService,
    resolve_otp_provider,
)


def test_otp_generation_security():
    """Verify OTP is a 6-digit numeric string generated via secrets."""
    for _ in range(50):
        otp = generate_otp(6)
        assert len(otp) == 6
        assert otp.isdigit()


def test_otp_hashing_consistency():
    """Verify HMAC-SHA256 hashing produces predictable hash with same secret."""
    otp = "123456"
    hash1 = hash_token(otp)
    hash2 = hash_token(otp)
    assert hash1 == hash2
    assert hash1 != hash_token("654321")


def test_smtp_password_sanitization():
    """Verify Google App Password whitespace is automatically stripped."""
    settings = get_settings()
    with patch.object(settings, "SMTP_PASSWORD", "abcd efgh ijkl mnop"):
        assert settings.clean_smtp_password == "abcdefghijklmnop"


def test_resolve_otp_provider():
    """Verify provider routing for email and dev modes."""
    settings = get_settings()
    
    with patch.object(settings, "EMAIL_PROVIDER", "smtp"):
        provider = resolve_otp_provider("doctor@example.com")
        assert isinstance(provider, EmailOTPProvider)
        
    with patch.object(settings, "EMAIL_PROVIDER", "resend"):
        provider = resolve_otp_provider("doctor@example.com")
        assert isinstance(provider, EmailOTPProvider)
        
    with patch.object(settings, "EMAIL_PROVIDER", "development"):
        provider = resolve_otp_provider("doctor@example.com")
        assert isinstance(provider, DevelopmentOTPProvider)


@pytest.mark.asyncio
async def test_otp_verification_expired():
    """Verify OTPExpiredError is raised when OTP has expired."""
    db_mock = AsyncMock()
    service = OTPService(db_mock)
    
    now = datetime.now(timezone.utc)
    expired_time = now - timedelta(minutes=1)
    
    fake_record = OTPVerification(
        identifier="doctor@hospital.org",
        identifier_type="email",
        otp_hash=hash_token("123456"),
        purpose=OTPPurpose.REGISTRATION,
        attempts=0,
        max_attempts=5,
        created_at=expired_time - timedelta(minutes=5),
        expires_at=expired_time,
        ip_address="127.0.0.1",
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_record
    db_mock.execute.return_value = mock_result
    
    with pytest.raises(OTPExpiredError):
        await service.verify_otp("doctor@hospital.org", "123456", OTPPurpose.REGISTRATION)


@pytest.mark.asyncio
async def test_otp_verification_max_attempts_lockout():
    """Verify lockout when max attempts are exceeded."""
    db_mock = AsyncMock()
    service = OTPService(db_mock)
    
    now = datetime.now(timezone.utc)
    fake_record = OTPVerification(
        identifier="doctor@hospital.org",
        identifier_type="email",
        otp_hash=hash_token("123456"),
        purpose=OTPPurpose.REGISTRATION,
        attempts=5,
        max_attempts=5,
        created_at=now,
        expires_at=now + timedelta(minutes=5),
        ip_address="127.0.0.1",
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_record
    db_mock.execute.return_value = mock_result
    
    with pytest.raises(InvalidOTPError) as exc_info:
        await service.verify_otp("doctor@hospital.org", "123456", OTPPurpose.REGISTRATION)
    assert exc_info.value.code == "OTP_MAX_ATTEMPTS"


@pytest.mark.asyncio
async def test_otp_verification_wrong_code_increments_attempts():
    """Verify entering incorrect code decrements remaining attempts."""
    db_mock = AsyncMock()
    service = OTPService(db_mock)
    
    now = datetime.now(timezone.utc)
    fake_record = OTPVerification(
        identifier="doctor@hospital.org",
        identifier_type="email",
        otp_hash=hash_token("654321"),
        purpose=OTPPurpose.REGISTRATION,
        attempts=0,
        max_attempts=5,
        created_at=now,
        expires_at=now + timedelta(minutes=5),
        ip_address="127.0.0.1",
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_record
    db_mock.execute.return_value = mock_result
    
    with pytest.raises(InvalidOTPError) as exc_info:
        await service.verify_otp("doctor@hospital.org", "111111", OTPPurpose.REGISTRATION)
    assert fake_record.attempts == 1
    assert exc_info.value.code == "INVALID_OTP"
