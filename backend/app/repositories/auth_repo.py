"""Authentication & Refresh Token Repository."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import LoginAttempt, RefreshToken


class AuthRepository:
    """Handles refresh token rotation, session revocation, and login attempts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        family_id: uuid.UUID,
        expires_at: datetime,
        device_info: dict | None = None,
        ip_address: str | None = None,
    ) -> RefreshToken:
        """Store newly issued refresh token in database."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Fetch token by its HMAC hash."""
        query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def revoke_token(self, token_id: uuid.UUID, replaced_by: uuid.UUID | None = None) -> None:
        """Mark single token as revoked."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked_at=now, replaced_by=replaced_by)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def revoke_family(self, family_id: uuid.UUID) -> None:
        """
        Revoke all tokens in a family when token reuse is detected.
        Critical security mechanism for detecting session hijacking.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revoke all sessions for user (e.g. on password change or full logout)."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def record_login_attempt(
        self,
        identifier: str,
        ip_address: str,
        success: bool,
        failure_reason: str | None = None,
        user_agent: str | None = None,
    ) -> LoginAttempt:
        """Record login attempt for security audit and brute-force tracking."""
        attempt = LoginAttempt(
            identifier=identifier.strip().lower(),
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt
