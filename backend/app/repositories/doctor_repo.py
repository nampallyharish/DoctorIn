"""Doctor Profile and Sub-resources Repository."""

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.doctor import (
    Doctor,
    DoctorAchievement,
    DoctorEducation,
    DoctorExperience,
    DoctorPublication,
    DoctorSpecialization,
)
from app.repositories.base import BaseRepository


class DoctorRepository(BaseRepository[Doctor]):
    """Data access repository for Doctor profile, education, experience, etc."""

    def __init__(self, session: AsyncSession):
        super().__init__(Doctor, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Doctor | None:
        """Fetch full doctor profile with all sub-entities by user_id."""
        query = (
            select(Doctor)
            .where(Doctor.user_id == user_id)
            .options(
                selectinload(Doctor.credentials),
                selectinload(Doctor.education),
                selectinload(Doctor.experience),
                selectinload(Doctor.specializations).selectinload(DoctorSpecialization.specialization),
                selectinload(Doctor.achievements),
                selectinload(Doctor.publications),
                selectinload(Doctor.certifications),
                selectinload(Doctor.languages),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Doctor | None:
        """Fetch public doctor profile by unique URL slug."""
        query = (
            select(Doctor)
            .where(Doctor.slug == slug)
            .options(
                selectinload(Doctor.education),
                selectinload(Doctor.experience),
                selectinload(Doctor.specializations).selectinload(DoctorSpecialization.specialization),
                selectinload(Doctor.achievements),
                selectinload(Doctor.publications),
                selectinload(Doctor.certifications),
                selectinload(Doctor.languages),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def calculate_and_update_completion(self, doctor_id: uuid.UUID) -> int:
        """Calculate profile completion percentage (0-100%) and persist."""
        doctor = await self.get_by_id(doctor_id)
        if not doctor:
            return 0

        score = 0
        if doctor.full_name: score += 15
        if doctor.headline: score += 10
        if doctor.bio: score += 15
        if doctor.years_of_experience is not None: score += 10
        if doctor.current_organization: score += 10
        if doctor.profile_photo_key: score += 10

        # Sub-entities checks
        edu_count = await self.session.scalar(
            select(func.count(DoctorEducation.id)).where(DoctorEducation.doctor_id == doctor_id)
        ) or 0
        if edu_count > 0: score += 10

        exp_count = await self.session.scalar(
            select(func.count(DoctorExperience.id)).where(DoctorExperience.doctor_id == doctor_id)
        ) or 0
        if exp_count > 0: score += 10

        spec_count = await self.session.scalar(
            select(func.count(DoctorSpecialization.doctor_id)).where(DoctorSpecialization.doctor_id == doctor_id)
        ) or 0
        if spec_count > 0: score += 10

        final_score = min(score, 100)
        doctor.profile_completion = final_score
        await self.session.flush()
        return final_score

    # --- Education CRUD ---
    async def add_education(self, doctor_id: uuid.UUID, **kwargs) -> DoctorEducation:
        edu = DoctorEducation(doctor_id=doctor_id, **kwargs)
        self.session.add(edu)
        await self.session.flush()
        await self.calculate_and_update_completion(doctor_id)
        return edu

    async def delete_education(self, doctor_id: uuid.UUID, education_id: uuid.UUID) -> bool:
        stmt = delete(DoctorEducation).where(
            DoctorEducation.id == education_id, DoctorEducation.doctor_id == doctor_id
        )
        result = await self.session.execute(stmt)
        await self.calculate_and_update_completion(doctor_id)
        return result.rowcount > 0

    # --- Experience CRUD ---
    async def add_experience(self, doctor_id: uuid.UUID, **kwargs) -> DoctorExperience:
        exp = DoctorExperience(doctor_id=doctor_id, **kwargs)
        self.session.add(exp)
        await self.session.flush()
        await self.calculate_and_update_completion(doctor_id)
        return exp

    async def delete_experience(self, doctor_id: uuid.UUID, experience_id: uuid.UUID) -> bool:
        stmt = delete(DoctorExperience).where(
            DoctorExperience.id == experience_id, DoctorExperience.doctor_id == doctor_id
        )
        result = await self.session.execute(stmt)
        await self.calculate_and_update_completion(doctor_id)
        return result.rowcount > 0

    # --- Specializations ---
    async def add_specialization(
        self, doctor_id: uuid.UUID, specialization_id: uuid.UUID, is_primary: bool = False
    ) -> DoctorSpecialization:
        ds = DoctorSpecialization(
            doctor_id=doctor_id, specialization_id=specialization_id, is_primary=is_primary
        )
        self.session.add(ds)
        await self.session.flush()
        await self.calculate_and_update_completion(doctor_id)
        return ds

    async def remove_specialization(self, doctor_id: uuid.UUID, specialization_id: uuid.UUID) -> bool:
        stmt = delete(DoctorSpecialization).where(
            DoctorSpecialization.doctor_id == doctor_id,
            DoctorSpecialization.specialization_id == specialization_id,
        )
        result = await self.session.execute(stmt)
        await self.calculate_and_update_completion(doctor_id)
        return result.rowcount > 0

    # --- Achievements ---
    async def add_achievement(self, doctor_id: uuid.UUID, **kwargs) -> DoctorAchievement:
        ach = DoctorAchievement(doctor_id=doctor_id, **kwargs)
        self.session.add(ach)
        await self.session.flush()
        return ach

    async def delete_achievement(self, doctor_id: uuid.UUID, achievement_id: uuid.UUID) -> bool:
        stmt = delete(DoctorAchievement).where(
            DoctorAchievement.id == achievement_id, DoctorAchievement.doctor_id == doctor_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # --- Publications ---
    async def add_publication(self, doctor_id: uuid.UUID, **kwargs) -> DoctorPublication:
        pub = DoctorPublication(doctor_id=doctor_id, **kwargs)
        self.session.add(pub)
        await self.session.flush()
        return pub

    async def delete_publication(self, doctor_id: uuid.UUID, publication_id: uuid.UUID) -> bool:
        stmt = delete(DoctorPublication).where(
            DoctorPublication.id == publication_id, DoctorPublication.doctor_id == doctor_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
