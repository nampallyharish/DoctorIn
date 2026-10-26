"""OTP Delivery and Management Service.

Flow:
  1. Rate-limit check (per identifier + per IP)
  2. Resend cooldown check (60 seconds between requests)
  3. Generate cryptographically secure 6-digit OTP via secrets module
  4. Hash OTP with HMAC-SHA256 before storing in database
  5. Invalidate any existing unverified OTP records for identifier + purpose
  6. Store new OTPVerification record (hash, expiry, attempt count)
  7. Dispatch via provider (Email / SMTP / Resend / SMS / Dev terminal)
  8. On verification: validate expiration (UTC), attempt limits, and hash match
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import (
    InvalidOTPError,
    OTPExpiredError,
    RateLimitExceededError,
)
from app.core.logging import logger
from app.core.rate_limiter import rate_limiter
from app.core.security import generate_otp, hash_token
from app.models.user import OTPPurpose, OTPVerification

settings = get_settings()


# ────────────────────────────────────────────────────────────────────
# OTP Provider Abstraction
# ────────────────────────────────────────────────────────────────────

class OTPProvider:
    """Abstract base for OTP delivery."""
    async def send(self, identifier: str, otp: str, purpose: str) -> bool:
        raise NotImplementedError


class DevelopmentOTPProvider(OTPProvider):
    """
    Prints OTP to FastAPI backend terminal only.
    Used when EMAIL_PROVIDER=development.
    NEVER sends a real email.
    """
    async def send(self, identifier: str, otp: str, purpose: str) -> bool:
        print("\n" + "=" * 58)
        print("[DOCTORIN DEVELOPMENT ONLY] OTP generated successfully.")
        print(f"  Identifier: {identifier}")
        print(f"  OTP Code  : {otp}")
        print(f"  Purpose   : {purpose}")
        print("  NOTE: Set EMAIL_PROVIDER=smtp + Gmail credentials in .env")
        print("        to deliver real OTP emails to users.")
        print("=" * 58 + "\n")
        logger.info(
            f"[OTP] Generated for terminal in development mode (identifier={identifier}, purpose={purpose})",
        )
        return True


class EmailOTPProvider(OTPProvider):
    """
    Dispatches OTP via the configured email service (SMTP or Resend).
    Raises InvalidOTPError if email delivery fails, so the user sees a real error.
    """
    async def send(self, identifier: str, otp: str, purpose: str) -> bool:
        from app.services.email_service import send_otp_email
        try:
            return await send_otp_email(recipient_email=identifier, otp=otp)
        except RuntimeError as exc:
            # email_service already logged the technical error; raise user-facing error
            logger.error(f"[OTP] Email delivery failed for {identifier}: {exc}")
            raise InvalidOTPError(
                "Unable to send verification code. Please try again."
            ) from exc


class SMSOTPProvider(OTPProvider):
    """Stub for SMS/Twilio delivery (not yet implemented)."""
    async def send(self, identifier: str, otp: str, purpose: str) -> bool:
        logger.error(
            "[OTP] SMS provider requested but not configured. "
            "Set OTP_PROVIDER_API_KEY and OTP_PROVIDER_SECRET for SMS delivery."
        )
        raise InvalidOTPError("SMS delivery is not configured. Please use email registration.")


def resolve_otp_provider(identifier: str) -> OTPProvider:
    """
    Determine the correct OTP provider for this identifier.

    Decision logic:
      - Email identifier (@)
          → EMAIL_PROVIDER in ('smtp', 'gmail', 'email', 'resend') → EmailOTPProvider
          → Otherwise → DevelopmentOTPProvider (terminal only)
      - Phone identifier
          → OTP_PROVIDER in ('sms', 'twilio') → SMSOTPProvider
          → Otherwise → DevelopmentOTPProvider
    """
    is_email = "@" in identifier
    email_provider = (settings.EMAIL_PROVIDER or "development").strip().lower()

    if is_email:
        if email_provider in ("smtp", "gmail", "email", "resend"):
            return EmailOTPProvider()
        return DevelopmentOTPProvider()

    # Phone
    sms_provider = (settings.OTP_PROVIDER or "development").strip().lower()
    if sms_provider in ("sms", "twilio"):
        return SMSOTPProvider()
    return DevelopmentOTPProvider()


async def _safe_background_send(provider: OTPProvider, identifier: str, otp: str, purpose: str) -> None:
    """Safe background worker to deliver OTP email and log any failure without crashing the response."""
    try:
        await provider.send(identifier, otp, purpose)
    except Exception as exc:
        logger.error(f"[OTP] Background email delivery failed for {identifier}: {exc}")


# ────────────────────────────────────────────────────────────────────
# OTP Service
# ────────────────────────────────────────────────────────────────────

class OTPService:
    """Core OTP lifecycle management: generate → store → dispatch → verify."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_otp(
        self,
        identifier: str,
        purpose: OTPPurpose,
        ip_address: str,
        user_agent: str | None = None,
        user_id: uuid.UUID | None = None,
        background_tasks: BackgroundTasks | None = None,
    ) -> bool:
        """
        Generate, hash, store, and dispatch OTP.
        Invalidates previous unverified OTPs for the same identifier & purpose.
        Uses background tasks for non-blocking email delivery when provided.
        Never returns the OTP to the caller.
        """
        clean = identifier.strip().lower()
        now = datetime.now(timezone.utc)
        logger.info(f"[OTP] Request received for {clean} (purpose={purpose.value})")

        # ── 1. Rate limiting ──────────────────────────────────────────
        try:
            await rate_limiter.check_rate_limit(
                key=f"otp_send:id:{clean}",
                limit=settings.OTP_MAX_REQUESTS_PER_HOUR,
                window_seconds=3600,
                error_message="Too many OTP requests for this account. Please wait before trying again.",
            )
            await rate_limiter.check_rate_limit(
                key=f"otp_send:ip:{ip_address}",
                limit=settings.OTP_MAX_REQUESTS_PER_HOUR * 2,
                window_seconds=3600,
                error_message="Too many OTP requests from this network. Please wait before trying again.",
            )
        except RateLimitExceededError:
            raise
        except Exception as exc:
            logger.warning(f"[OTP] Rate limiter unavailable: {exc}. Continuing.")

        # ── 2. Resend cooldown ────────────────────────────────────────
        cooldown_query = (
            select(OTPVerification)
            .where(
                OTPVerification.identifier == clean,
                OTPVerification.purpose == purpose,
                OTPVerification.verified_at.is_(None),
            )
            .order_by(OTPVerification.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(cooldown_query)
        latest = result.scalar_one_or_none()

        if latest:
            created_at = latest.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            elapsed = (now - created_at).total_seconds()
            if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
                wait = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                raise RateLimitExceededError(
                    message=f"Please wait {wait} seconds before requesting another OTP.",
                    retry_after=wait,
                )

        # ── 3. Invalidate previous active OTPs for this identifier & purpose ──
        await self.db.execute(
            delete(OTPVerification).where(
                OTPVerification.identifier == clean,
                OTPVerification.purpose == purpose,
                OTPVerification.verified_at.is_(None),
            )
        )

        # ── 4. Generate OTP (cryptographically secure) ────────────────
        raw_otp = generate_otp(6)  # secrets.choice("0123456789") × 6
        otp_hash = hash_token(raw_otp)  # HMAC-SHA256 with JWT_SECRET pepper

        expiry_secs = getattr(settings, "OTP_EXPIRY_SECONDS", settings.OTP_EXPIRY_MINUTES * 60)
        expires_at = now + timedelta(seconds=expiry_secs)
        identifier_type = "email" if "@" in clean else "phone"

        # ── 5. Persist hashed OTP (never plaintext) ───────────────────
        otp_record = OTPVerification(
            user_id=user_id,
            identifier=clean,
            identifier_type=identifier_type,
            otp_hash=otp_hash,
            purpose=purpose,
            attempts=0,
            max_attempts=settings.OTP_MAX_ATTEMPTS,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(otp_record)
        await self.db.flush()

        logger.info(
            f"[OTP] Database record created for {clean} (purpose={purpose.value}, "
            f"expires_at={expires_at.isoformat()}, ttl={expiry_secs}s)"
        )

        # ── 6. Dispatch via provider ──────────────────────────────────
        provider = resolve_otp_provider(clean)
        if background_tasks is not None:
            # Non-blocking async background delivery
            background_tasks.add_task(_safe_background_send, provider, clean, raw_otp, purpose.value)
            logger.info(f"[OTP] Email dispatch scheduled in background for {clean}")
        else:
            await provider.send(clean, raw_otp, purpose.value)

        return True

    async def verify_otp(
        self,
        identifier: str,
        raw_otp: str,
        purpose: OTPPurpose,
    ) -> OTPVerification:
        """
        Verify submitted OTP against stored hash.
        Enforces expiration (UTC) and max attempt lockout.
        Invalidates OTP on success.
        """
        clean = identifier.strip().lower()
        now = datetime.now(timezone.utc)
        logger.info(f"[OTP] Verification request received for {clean} (purpose={purpose.value})")

        query = (
            select(OTPVerification)
            .where(
                OTPVerification.identifier == clean,
                OTPVerification.purpose == purpose,
                OTPVerification.verified_at.is_(None),
            )
            .order_by(OTPVerification.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        record = result.scalar_one_or_none()

        if not record:
            raise InvalidOTPError(
                "No pending OTP found. Please request a new code.",
                code="NO_PENDING_OTP",
                status_code=400,
            )

        # Expiration check
        exp = record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < now:
            logger.warning(f"[OTP] Expired code presented for {clean} (expired_at={exp.isoformat()}, now={now.isoformat()})")
            raise OTPExpiredError("This OTP has expired. Please request a new code.")

        # Attempt lockout check
        if record.attempts >= record.max_attempts:
            logger.warning(f"[OTP] Max attempts exceeded for {clean}")
            raise InvalidOTPError(
                "Maximum verification attempts exceeded. Please request a new code.",
                code="OTP_MAX_ATTEMPTS",
                status_code=429,
            )

        # Verify hash
        candidate_hash = hash_token(raw_otp.strip())
        if candidate_hash != record.otp_hash:
            record.attempts += 1
            await self.db.flush()
            remaining = record.max_attempts - record.attempts
            if remaining <= 0:
                logger.warning(f"[OTP] Max attempts reached for {clean}")
                raise InvalidOTPError(
                    "Maximum attempts exceeded. This OTP has been invalidated.",
                    code="OTP_MAX_ATTEMPTS",
                    status_code=429,
                )
            logger.warning(f"[OTP] Invalid code entered for {clean} ({remaining} attempts remaining)")
            raise InvalidOTPError(
                f"Incorrect verification code. {remaining} attempt(s) remaining.",
                code="INVALID_OTP",
                status_code=400,
                attempts_left=remaining,
            )

        # Mark verified — invalidates OTP for future use
        record.verified_at = now
        await self.db.flush()

        logger.info(f"[OTP] Verification successful for {clean} (purpose={purpose.value})")
        return record
