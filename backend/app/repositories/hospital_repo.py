"""Hospital Repository for profiles, departments, affiliations, and job postings."""

import re
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hospital import (
    AffiliationStatus,
    DoctorHospitalAffiliation,
    Hospital,
    HospitalAdmin,
    JobApplication,
    JobApplicationStatus,
    JobPosting,
    JobPostingStatus,
)
from app.repositories.base import BaseRepository


class HospitalRepository(BaseRepository[Hospital]):
    """Data access repository for Hospital profiles, jobs, and affiliations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Hospital, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Hospital | None:
        """Fetch hospital profile associated with user account."""
        query = (
            select(Hospital)
            .join(HospitalAdmin, HospitalAdmin.hospital_id == Hospital.id)
            .where(HospitalAdmin.user_id == user_id)
            .options(selectinload(Hospital.departments))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Hospital | None:
        """Fetch public hospital profile by slug with departments."""
        query = (
            select(Hospital)
            .where(Hospital.slug == slug)
            .options(
                selectinload(Hospital.departments),
                selectinload(Hospital.affiliations).selectinload(DoctorHospitalAffiliation.doctor),
                selectinload(Hospital.job_postings),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # --- Job Postings ---
    async def create_job_posting(
        self, hospital_id: uuid.UUID, title: str, **kwargs
    ) -> JobPosting:
        """Create new medical job vacancy."""
        base_slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        job = JobPosting(
            hospital_id=hospital_id,
            title=title,
            slug=unique_slug,
            status=JobPostingStatus.ACTIVE,
            **kwargs,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def list_job_postings(
        self,
        specialization_id: uuid.UUID | None = None,
        city: str | None = None,
        min_experience: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[JobPosting], int]:
        """List active medical jobs with filters and hospital details."""
        query = (
            select(JobPosting)
            .where(
                JobPosting.status == JobPostingStatus.ACTIVE,
            )
            .options(
                selectinload(JobPosting.hospital),
            )
            .order_by(desc(JobPosting.created_at))
            .offset(skip)
            .limit(limit)
        )

        conditions = [
            JobPosting.status == JobPostingStatus.ACTIVE,
        ]
        if specialization_id:
            conditions.append(JobPosting.specialization_id == specialization_id)
        if city:
            conditions.append(JobPosting.city_name.ilike(f"%{city.strip()}%"))
        if min_experience is not None:
            conditions.append(JobPosting.min_experience_years <= min_experience)

        count_query = select(func.count(JobPosting.id)).where(and_(*conditions))

        results = await self.session.execute(query)
        total = await self.session.scalar(count_query) or 0

        return list(results.scalars().all()), total

    async def get_job_by_id(self, job_id: uuid.UUID) -> JobPosting | None:
        """Fetch job posting details with hospital."""
        query = (
            select(JobPosting)
            .where(JobPosting.id == job_id, JobPosting.deleted_at.is_(None))
            .options(
                selectinload(JobPosting.hospital),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def apply_to_job(
        self, job_id: uuid.UUID, doctor_id: uuid.UUID, cover_note: str | None = None
    ) -> JobApplication:
        """Submit doctor application to job."""
        now = datetime.now(timezone.utc)
        app = JobApplication(
            job_posting_id=job_id,
            doctor_id=doctor_id,
            cover_note=cover_note,
            status=JobApplicationStatus.SUBMITTED,
            applied_at=now,
        )
        self.session.add(app)

        # Increment application count on job
        stmt = (
            update(JobPosting)
            .where(JobPosting.id == job_id)
            .values(applications_count=JobPosting.applications_count + 1)
        )
        await self.session.execute(stmt)
        await self.session.flush()

        return app

    async def list_job_applications(
        self, job_id: uuid.UUID
    ) -> list[JobApplication]:
        """List applicants for a hospital job posting."""
        query = (
            select(JobApplication)
            .where(JobApplication.job_posting_id == job_id)
            .options(
                selectinload(JobApplication.doctor),
            )
            .order_by(desc(JobApplication.applied_at))
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())

    # --- Affiliations ---
    async def request_affiliation(
        self, doctor_id: uuid.UUID, hospital_id: uuid.UUID, designation: str, start_date: date
    ) -> DoctorHospitalAffiliation:
        """Doctor requests affiliation verification with hospital."""
        aff = DoctorHospitalAffiliation(
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            designation=designation,
            start_date=start_date,
            status=AffiliationStatus.PENDING,
        )
        self.session.add(aff)
        await self.session.flush()
        return aff

    async def list_hospital_affiliations(
        self, hospital_id: uuid.UUID
    ) -> list[DoctorHospitalAffiliation]:
        """List doctors affiliated or pending affiliation with hospital."""
        query = (
            select(DoctorHospitalAffiliation)
            .where(DoctorHospitalAffiliation.hospital_id == hospital_id)
            .options(
                selectinload(DoctorHospitalAffiliation.doctor),
                selectinload(DoctorHospitalAffiliation.hospital),
            )
            .order_by(desc(DoctorHospitalAffiliation.created_at))
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())
