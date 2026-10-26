"""Unit tests for Security Hardening, XSS Sanitization, PII Masking, and Headers."""

import pytest

from app.core.sanitizer import Sanitizer


def test_xss_sanitization_strips_script_tags():
    """Test that dangerous script tags are completely stripped."""
    malicious_input = "Hello <script>alert('XSS')</script> Doctor"
    cleaned = Sanitizer.sanitize_text(malicious_input)
    assert "<script>" not in cleaned
    assert "alert" not in cleaned
    assert "Hello  Doctor" in cleaned


def test_xss_sanitization_escapes_html_entities():
    """Test that special HTML characters are safely entity-escaped."""
    html_input = "Dr. Smith & <img src=x onerror=alert(1)>"
    cleaned = Sanitizer.sanitize_text(html_input)
    assert "&lt;" in cleaned
    assert "&amp;" in cleaned
    assert "<img" not in cleaned


def test_pii_email_masking():
    """Test email address masking for secure logging."""
    email = "doctor.sarah@apollohospitals.org"
    masked = Sanitizer.mask_email(email)
    assert masked.startswith("d")
    assert masked.endswith("@apollohospitals.org")
    assert "***" in masked
    assert "sarah" not in masked


def test_pii_phone_masking():
    """Test phone number masking."""
    phone = "+919876543210"
    masked = Sanitizer.mask_phone(phone)
    assert masked.startswith("+91")
    assert masked.endswith("3210")
    assert "******" in masked


def test_token_masking():
    """Test JWT token redaction for log safety."""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
    masked = Sanitizer.mask_token(token)
    assert "[REDACTED]" in masked
    assert len(masked) < 30


@pytest.mark.asyncio
async def test_security_headers_present_on_response(async_client):
    """Test that security headers middleware adds all OWASP recommended headers."""
    response = await async_client.get("/api/v1/health")
    headers = response.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
