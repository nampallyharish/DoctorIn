"""User Repository for database query operations."""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.doctor import Doctor, VerificationStatus
from app.models.patient import Patient
from app.models.user import User, UserRole, UserStatus
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User data access operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        """Lookup user by ID with profiles eager loaded."""
        query = (
            select(User)
            .where(User.id == id, User.deleted_at.is_(None))
            .options(
                selectinload(User.doctor_profile),
                selectinload(User.patient_profile),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Lookup user by either email or phone."""
        clean = identifier.strip().lower()
        query = (
            select(User)
            .where(
                or_(User.email == clean, User.phone == clean),
                User.deleted_at.is_(None),
            )
            .options(
                selectinload(User.doctor_profile),
                selectinload(User.patient_profile),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Lookup user by email."""
        clean = email.strip().lower()
        query = (
            select(User)
            .where(User.email == clean, User.deleted_at.is_(None))
            .options(selectinload(User.doctor_profile))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Lookup user by phone."""
        clean = phone.strip()
        query = (
            select(User)
            .where(User.phone == clean, User.deleted_at.is_(None))
            .options(selectinload(User.doctor_profile))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user_with_profile(
        self,
        role: UserRole,
        email: str | None = None,
        phone: str | None = None,
        password_hash: str | None = None,
        full_name: str | None = None,
    ) -> User:
        """Create new User and automatically associate their domain-specific profile (Doctor or Patient)."""
        user = User(
            email=email.strip().lower() if email else None,
            phone=phone.strip() if phone else None,
            password_hash=password_hash,
            role=role,
            status=UserStatus.PENDING_VERIFICATION,
            email_verified=False,
            phone_verified=False,
        )
        self.session.add(user)
        await self.session.flush()

        if role == UserRole.DOCTOR:
            name = full_name.strip() if full_name else (email.split("@")[0] if email else "Dr. User")
            # Generate clean slug
            base_slug = name.lower().replace(" ", "-").replace(".", "")
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            doctor = Doctor(
                user_id=user.id,
                full_name=name,
                slug=slug,
                verification_status=VerificationStatus.UNVERIFIED,
                profile_completion=10,
            )
            self.session.add(doctor)
        elif role == UserRole.PATIENT:
            patient = Patient(
                user_id=user.id,
                display_name=full_name or "Patient User",
            )
            self.session.add(patient)

        await self.session.flush()
        await self.session.refresh(user)
        return user
