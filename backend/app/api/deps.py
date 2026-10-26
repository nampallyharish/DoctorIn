"""FastAPI Dependency Injection functions for Auth, RBAC, DB Sessions, etc."""

import uuid
from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.doctor import Doctor, VerificationStatus
from app.models.user import User, UserRole, UserStatus

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT access token, returning active user model."""
    if not credentials:
        raise UnauthorizedError("Missing authorization credentials")

    payload = decode_access_token(credentials.credentials)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token payload")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid user identifier in token")

    query = (
        select(User)
        .where(User.id == user_id, User.deleted_at.is_(None))
        .options(selectinload(User.doctor_profile), selectinload(User.patient_profile))
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User account not found or deleted")

    if user.status == UserStatus.SUSPENDED:
        raise ForbiddenError("Account has been suspended")
    if user.status == UserStatus.DEACTIVATED:
        raise ForbiddenError("Account has been deactivated")

    return user


def require_role(allowed_roles: list[UserRole]) -> Callable:
    """Dependency factory checking that the user has one of the allowed roles."""

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise ForbiddenError(f"Operation requires one of roles: {[r.value for r in allowed_roles]}")
        return user

    return role_checker


async def require_doctor(user: User = Depends(get_current_user)) -> User:
    """Ensure authenticated user is a doctor."""
    if user.role != UserRole.DOCTOR:
        raise ForbiddenError("Doctor role required for this action")
    return user


async def require_verified_doctor(user: User = Depends(get_current_user)) -> Doctor:
    """
    Ensure authenticated user is a VERIFIED doctor.
    Critical requirement for Doctor-to-Doctor Messaging and verified features.
    """
    if user.role != UserRole.DOCTOR:
        raise ForbiddenError("Only doctors can perform this action")

    if not user.doctor_profile:
        raise ForbiddenError("Doctor profile not found")

    if user.doctor_profile.verification_status != VerificationStatus.VERIFIED:
        raise ForbiddenError(
            "Only verified doctors with an active verification badge can perform this action. "
            f"Current status: {user.doctor_profile.verification_status.value}"
        )

    return user.doctor_profile


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Ensure authenticated user is an administrator."""
    if user.role != UserRole.ADMIN:
        raise ForbiddenError("Administrator privileges required")
    return user


def get_client_ip(request: Request) -> str:
    """Extract real client IP address considering proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"
