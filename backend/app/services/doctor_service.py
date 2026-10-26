"""Doctor Profile Business Logic Service."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.repositories.doctor_repo import DoctorRepository
from app.schemas.doctor import (
    AchievementCreate,
    DoctorProfileUpdate,
    EducationCreate,
    ExperienceCreate,
    PublicationCreate,
    SpecializationAddRequest,
)


class DoctorService:
    """Business operations for Doctor profiles and sub-entities."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DoctorRepository(db)

    async def get_doctor_by_user(self, user: User) -> Doctor:
        """Fetch own profile for authenticated doctor."""
        if user.role != UserRole.DOCTOR:
            raise ForbiddenError("Only doctors have a doctor profile.")

        doctor = await self.repo.get_by_user_id(user.id)
        if not doctor:
            raise NotFoundError("Doctor profile not found")
        return doctor

    async def get_public_doctor_by_slug(self, slug: str) -> Doctor:
        """Fetch public doctor profile by slug."""
        doctor = await self.repo.get_by_slug(slug)
        if not doctor:
            raise NotFoundError("Doctor profile not found for slug", slug)
        return doctor

    async def update_profile(self, user: User, payload: DoctorProfileUpdate) -> Doctor:
        """Update doctor's main profile information."""
        doctor = await self.get_doctor_by_user(user)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(doctor, key, value)

        await self.db.flush()
        await self.repo.calculate_and_update_completion(doctor.id)
        return doctor

    # --- Sub-resource Operations ---
    async def add_education(self, user: User, payload: EducationCreate):
        doctor = await self.get_doctor_by_user(user)
        return await self.repo.add_education(doctor.id, **payload.model_dump())

    async def remove_education(self, user: User, education_id: uuid.UUID) -> bool:
        doctor = await self.get_doctor_by_user(user)
        deleted = await self.repo.delete_education(doctor.id, education_id)
        if not deleted:
            raise NotFoundError("Education record not found")
        return True

    async def add_experience(self, user: User, payload: ExperienceCreate):
        doctor = await self.get_doctor_by_user(user)
        return await self.repo.add_experience(doctor.id, **payload.model_dump())

    async def remove_experience(self, user: User, experience_id: uuid.UUID) -> bool:
        doctor = await self.get_doctor_by_user(user)
        deleted = await self.repo.delete_experience(doctor.id, experience_id)
        if not deleted:
            raise NotFoundError("Experience record not found")
        return True

    async def add_specialization(self, user: User, payload: SpecializationAddRequest):
        doctor = await self.get_doctor_by_user(user)
        return await self.repo.add_specialization(
            doctor.id, payload.specialization_id, payload.is_primary
        )

    async def remove_specialization(self, user: User, specialization_id: uuid.UUID) -> bool:
        doctor = await self.get_doctor_by_user(user)
        deleted = await self.repo.remove_specialization(doctor.id, specialization_id)
        if not deleted:
            raise NotFoundError("Specialization association not found")
        return True

    async def add_achievement(self, user: User, payload: AchievementCreate):
        doctor = await self.get_doctor_by_user(user)
        return await self.repo.add_achievement(doctor.id, **payload.model_dump())

    async def remove_achievement(self, user: User, achievement_id: uuid.UUID) -> bool:
        doctor = await self.get_doctor_by_user(user)
        deleted = await self.repo.delete_achievement(doctor.id, achievement_id)
        if not deleted:
            raise NotFoundError("Achievement record not found")
        return True

    async def add_publication(self, user: User, payload: PublicationCreate):
        doctor = await self.get_doctor_by_user(user)
        return await self.repo.add_publication(doctor.id, **payload.model_dump())

    async def remove_publication(self, user: User, publication_id: uuid.UUID) -> bool:
        doctor = await self.get_doctor_by_user(user)
        deleted = await self.repo.delete_publication(doctor.id, publication_id)
        if not deleted:
            raise NotFoundError("Publication record not found")
        return True
