"""Security utilities: password hashing, JWT token operations, OTP hashing."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import get_settings
from app.core.exceptions import UnauthorizedError

settings = get_settings()



def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt."""
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        pw_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False



def hash_token(raw_token: str) -> str:
    """Hash raw token (such as refresh token or OTP) using SHA-256 with pepper."""
    pepper = settings.JWT_SECRET.encode("utf-8")
    return hmac.new(pepper, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_otp(length: int = 6) -> str:
    """Generate cryptographically secure numeric OTP string."""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate cryptographically secure URL-safe random token."""
    return secrets.token_urlsafe(nbytes)


def create_access_token(
    subject: str,
    role: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_hex(16),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    family_id: str,
    expires_delta: timedelta | None = None,
) -> tuple[str, str, datetime]:
    """
    Create a secure refresh token.
    Returns (raw_token, token_hash, expiration_datetime).
    """
    raw_token = f"rt_{generate_secure_token(48)}"
    token_h = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta
        else timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return raw_token, token_h, expire


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate access token JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Access token has expired", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid access token", code="INVALID_TOKEN")
