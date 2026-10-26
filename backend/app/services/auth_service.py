"""Authentication Service implementing Registration, OTP, JWT, Refresh Token Rotation, and Logout."""

import uuid
from datetime import datetime, timezone

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitExceededError,
    UnauthorizedError,
    ValidationError,
)
from app.core.logging import logger
from app.core.rate_limiter import rate_limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import OTPPurpose, User, UserRole, UserStatus
from app.repositories.auth_repo import AuthRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    VerifyOTPRequest,
)
from app.services.otp_service import OTPService

settings = get_settings()


class AuthService:
    """Core Authentication & Token Lifecycle Service."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)
        self.otp_service = OTPService(db)

    async def register_user(
        self,
        payload: RegisterRequest,
        ip_address: str,
        user_agent: str | None = None,
        background_tasks: BackgroundTasks | None = None,
    ) -> tuple[User, str]:
        """
        Register a new user in pending state and dispatch verification OTP.
        """
        if not payload.email and not payload.phone:
            raise ValidationError("Either email or phone must be provided")

        if not payload.password or len(payload.password) < 8 or len(payload.password) > 128:
            raise ValidationError("Password must be between 8 and 128 characters long")

        identifier = (payload.email or payload.phone).strip().lower()

        # Hash password using project's existing bcrypt implementation
        pw_hash = hash_password(payload.password)
        if not pw_hash:
            raise ValidationError("Failed to generate password hash")

        # Check for existing active user
        existing_user = await self.user_repo.get_by_identifier(identifier)
        if existing_user:
            if existing_user.status == UserStatus.ACTIVE:
                raise ConflictError("An account with this identifier already exists.")
            user = existing_user
            user.password_hash = pw_hash
            if payload.full_name and user.patient_profile:
                user.patient_profile.display_name = payload.full_name
            await self.db.flush()
        else:
            user = await self.user_repo.create_user_with_profile(
                role=payload.role or UserRole.USER,
                email=str(payload.email) if payload.email else None,
                phone=payload.phone,
                password_hash=pw_hash,
                full_name=payload.full_name,
            )

        # Dispatch registration OTP
        await self.otp_service.send_otp(
            identifier=identifier,
            purpose=OTPPurpose.REGISTRATION,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user.id,
            background_tasks=background_tasks,
        )

        await self.db.commit()

        return user, identifier

    async def send_otp(
        self,
        identifier: str,
        purpose: OTPPurpose,
        ip_address: str,
        user_agent: str | None = None,
        background_tasks: BackgroundTasks | None = None,
    ) -> bool:
        """Rate-limited OTP dispatch."""
        user = await self.user_repo.get_by_identifier(identifier)
        return await self.otp_service.send_otp(
            identifier=identifier,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user.id if user else None,
            background_tasks=background_tasks,
        )

    async def verify_otp_and_login(
        self,
        payload: VerifyOTPRequest,
        ip_address: str,
        user_agent: str | None = None,
    ) -> TokenResponse:
        """
        Verify OTP code, activate user if pending, and issue access/refresh token pair.
        """
        identifier = payload.identifier.strip().lower()

        # 1. Verify OTP
        await self.otp_service.verify_otp(
            identifier=identifier,
            raw_otp=payload.otp,
            purpose=payload.purpose,
        )

        # 2. Lookup user
        user = await self.user_repo.get_by_identifier(identifier)
        if not user:
            raise NotFoundError("User not found for this identifier")

        # 3. Activate user if pending registration
        if user.status == UserStatus.PENDING_VERIFICATION:
            user.status = UserStatus.ACTIVE

        if "@" in identifier:
            user.email_verified = True
        else:
            user.phone_verified = True

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        # 4. Issue Tokens
        tokens = await self._issue_token_pair(user, ip_address=ip_address, user_agent=user_agent)
        await self.db.commit()
        return tokens

    async def reset_password(
        self,
        identifier: str,
        otp: str,
        new_password: str,
    ) -> None:
        """Reset or establish password securely via verified OTP."""
        clean = identifier.strip().lower()

        if not new_password or len(new_password) < 8 or len(new_password) > 128:
            raise ValidationError("New password must be between 8 and 128 characters")

        # 1. Verify OTP with PASSWORD_RESET purpose
        await self.otp_service.verify_otp(
            identifier=clean,
            raw_otp=otp,
            purpose=OTPPurpose.PASSWORD_RESET,
        )

        # 2. Lookup user
        user = await self.user_repo.get_by_identifier(clean)
        if not user:
            raise NotFoundError("User not found for this identifier")

        # 3. Update password hash securely
        user.password_hash = hash_password(new_password)
        if user.status == UserStatus.PENDING_VERIFICATION:
            user.status = UserStatus.ACTIVE

        await self.db.commit()

    async def login_with_password(
        self,
        payload: LoginRequest,
        ip_address: str,
        user_agent: str | None = None,
        background_tasks: BackgroundTasks | None = None,
    ) -> dict:
        """Authenticate user with identifier + password."""
        identifier = payload.identifier.strip().lower()

        # Rate limit login attempts
        await rate_limiter.check_rate_limit(
            key=f"login_attempt:{identifier}",
            limit=10,
            window_seconds=900,
            error_message="Too many failed login attempts. Please try again in 15 minutes.",
        )

        user = await self.user_repo.get_by_identifier(identifier)
        if not user or not user.password_hash:
            await self.auth_repo.record_login_attempt(
                identifier=identifier,
                ip_address=ip_address,
                success=False,
                failure_reason="Invalid credentials",
                user_agent=user_agent,
            )
            raise UnauthorizedError("Invalid email/phone or password")

        if not verify_password(payload.password or "", user.password_hash):
            await self.auth_repo.record_login_attempt(
                identifier=identifier,
                ip_address=ip_address,
                success=False,
                failure_reason="Incorrect password",
                user_agent=user_agent,
            )
            raise UnauthorizedError("Invalid email/phone or password")

        if user.status == UserStatus.SUSPENDED:
            raise ForbiddenError("Your account has been suspended. Please contact support.")

        user.last_login_at = datetime.now(timezone.utc)
        await self.auth_repo.record_login_attempt(
            identifier=identifier,
            ip_address=ip_address,
            success=True,
            user_agent=user_agent,
        )
        await self.db.flush()

        # 4. Issue token pair for authenticated session
        token_response = await self._issue_token_pair(user, ip_address=ip_address, user_agent=user_agent)

        # 5. Trigger OTP for verification / 2FA flow if required by UI
        try:
            await self.otp_service.send_otp(
                identifier=identifier,
                purpose=OTPPurpose.LOGIN,
                ip_address=ip_address,
                user_agent=user_agent,
                user_id=user.id,
                background_tasks=background_tasks,
            )
        except RateLimitExceededError:
            # An active OTP was already dispatched recently; allow password authentication to proceed
            pass

        await self.db.commit()

        return {
            "message": "Authentication successful. Please verify OTP to continue.",
            "identifier": identifier,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "token_type": "bearer",
            "expires_in": token_response.expires_in,
            "user_id": str(user.id),
            "verification_status": token_response.verification_status,
            "full_name": token_response.full_name,
        }

    async def refresh_access_token(
        self,
        raw_refresh_token: str,
        ip_address: str,
        user_agent: str | None = None,
    ) -> TokenResponse:
        """
        Refresh access token using token rotation.
        Detects reuse attacks: if a revoked token is presented, invalidates the entire token family.
        """
        token_h = hash_token(raw_refresh_token.strip())
        stored_token = await self.auth_repo.get_refresh_token_by_hash(token_h)

        if not stored_token:
            raise UnauthorizedError("Invalid or unknown refresh token", code="INVALID_REFRESH_TOKEN")

        # REUSE DETECTION: If token was already revoked, someone is reusing it -> compromise!
        if stored_token.revoked_at is not None:
            logger.warning(
                f"🚨 Token reuse detected for user {stored_token.user_id}! Revoking token family {stored_token.family_id}."
            )
            await self.auth_repo.revoke_family(stored_token.family_id)
            raise UnauthorizedError(
                "Suspicious session activity detected. Please login again.",
                code="SESSION_COMPROMISED",
            )

        now = datetime.now(timezone.utc)
        expires_at = stored_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise UnauthorizedError("Refresh token has expired", code="REFRESH_TOKEN_EXPIRED")

        # Fetch user
        user = await self.user_repo.get_by_id(stored_token.user_id)
        if not user or user.status == UserStatus.SUSPENDED:
            raise ForbiddenError("User account is inactive or suspended")

        # 1. Issue new refresh token within SAME family
        new_raw_rt, new_rt_hash, new_rt_exp = create_refresh_token(
            subject=str(user.id),
            family_id=str(stored_token.family_id),
        )
        new_token_record = await self.auth_repo.create_refresh_token(
            user_id=user.id,
            token_hash=new_rt_hash,
            family_id=stored_token.family_id,
            expires_at=new_rt_exp,
            ip_address=ip_address,
            device_info={"user_agent": user_agent},
        )

        # 2. Revoke old refresh token (pointing to new token)
        await self.auth_repo.revoke_token(stored_token.id, replaced_by=new_token_record.id)
        await self.db.commit()

        # 3. Issue new short-lived access token
        verification_status = None
        full_name = None
        if user.doctor_profile:
            verification_status = user.doctor_profile.verification_status.value
            full_name = user.doctor_profile.full_name
        elif user.patient_profile:
            full_name = user.patient_profile.display_name

        access_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
            extra_claims={"verification_status": verification_status},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_raw_rt,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            role=user.role,
            verification_status=verification_status,
            full_name=full_name,
        )

    async def logout(self, raw_refresh_token: str) -> None:
        """Revoke a single refresh token."""
        token_h = hash_token(raw_refresh_token.strip())
        stored_token = await self.auth_repo.get_refresh_token_by_hash(token_h)
        if stored_token:
            await self.auth_repo.revoke_token(stored_token.id)
            await self.db.commit()

    async def logout_all(self, user_id: uuid.UUID) -> None:
        """Revoke all sessions for a user."""
        await self.auth_repo.revoke_all_user_tokens(user_id)

    async def _issue_token_pair(
        self,
        user: User,
        ip_address: str,
        user_agent: str | None = None,
    ) -> TokenResponse:
        """Internal helper to create access token and brand new refresh token family."""
        family_id = uuid.uuid4()
        raw_rt, rt_hash, rt_exp = create_refresh_token(
            subject=str(user.id),
            family_id=str(family_id),
        )

        await self.auth_repo.create_refresh_token(
            user_id=user.id,
            token_hash=rt_hash,
            family_id=family_id,
            expires_at=rt_exp,
            ip_address=ip_address,
            device_info={"user_agent": user_agent},
        )

        verification_status = None
        full_name = None
        if user.doctor_profile:
            verification_status = user.doctor_profile.verification_status.value
            full_name = user.doctor_profile.full_name
        elif user.patient_profile:
            full_name = user.patient_profile.display_name

        access_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
            extra_claims={"verification_status": verification_status},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_rt,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            role=user.role,
            verification_status=verification_status,
            full_name=full_name,
        )
