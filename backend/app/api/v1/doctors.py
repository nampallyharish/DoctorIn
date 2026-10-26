"""Public Doctors Discovery and Profile Viewing REST API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.doctor import Doctor, DoctorSpecialization
from app.schemas.common import APIResponse, MetaData
from app.schemas.doctor import (
    DoctorPublicProfileResponse,
    EducationResponse,
    ExperienceResponse,
    SpecializationItem,
)
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["Doctors Public"])


def _format_public_doctor(doctor: Doctor) -> DoctorPublicProfileResponse:
    specializations = []
    if doctor.specializations:
        for ds in doctor.specializations:
            if ds.specialization:
                specializations.append(
                    SpecializationItem(
                        id=ds.specialization.id,
                        name=ds.specialization.name,
                        slug=ds.specialization.slug,
                        is_primary=ds.is_primary,
                    )
                )

    return DoctorPublicProfileResponse(
        id=doctor.id,
        full_name=doctor.full_name,
        slug=doctor.slug,
        headline=doctor.headline,
        bio=doctor.bio,
        years_of_experience=doctor.years_of_experience,
        current_organization=doctor.current_organization,
        profile_photo_key=doctor.profile_photo_key,
        verification_status=doctor.verification_status,
        verified_at=doctor.verified_at,
        education=[
            EducationResponse(
                id=e.id,
                doctor_id=e.doctor_id,
                institution=e.institution,
                degree=e.degree,
                field_of_study=e.field_of_study,
                start_year=e.start_year,
                end_year=e.end_year,
                grade=e.grade,
                description=e.description,
                display_order=e.display_order,
                created_at=e.created_at,
            )
            for e in doctor.education
        ],
        experience=[
            ExperienceResponse(
                id=x.id,
                doctor_id=x.doctor_id,
                organization=x.organization,
                hospital_id=x.hospital_id,
                job_title=x.job_title,
                employment_type=x.employment_type,
                start_date=x.start_date,
                end_date=x.end_date,
                is_current=x.is_current,
                city=x.city,
                description=x.description,
                display_order=x.display_order,
                created_at=x.created_at,
            )
            for x in doctor.experience
        ],
        specializations=specializations,
        achievements=[
            {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "title": a.title,
                "description": a.description,
                "issuing_organization": a.issuing_organization,
                "achievement_date": a.achievement_date,
                "display_order": a.display_order,
                "created_at": a.created_at,
            }
            for a in doctor.achievements
        ],
        publications=[
            {
                "id": p.id,
                "doctor_id": p.doctor_id,
                "title": p.title,
                "journal": p.journal,
                "publication_url": p.publication_url,
                "doi": p.doi,
                "publication_date": p.publication_date,
                "abstract": p.abstract,
                "authors": p.authors,
                "display_order": p.display_order,
                "created_at": p.created_at,
            }
            for p in doctor.publications
        ],
    )


@router.get("", response_model=APIResponse[list[DoctorPublicProfileResponse]])
async def list_public_doctors(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List public doctors with pagination."""
    offset = (page - 1) * per_page
    query = (
        select(Doctor)
        .options(
            selectinload(Doctor.education),
            selectinload(Doctor.experience),
            selectinload(Doctor.specializations).selectinload(DoctorSpecialization.specialization),
            selectinload(Doctor.achievements),
            selectinload(Doctor.publications),
        )
        .offset(offset)
        .limit(per_page)
        .order_by(Doctor.created_at.desc())
    )
    result = await db.execute(query)
    doctors = result.scalars().all()

    formatted = [_format_public_doctor(d) for d in doctors]
    return APIResponse(
        success=True,
        data=formatted,
        meta=MetaData(page=page, per_page=per_page, total=len(formatted)),
    )


@router.get("/{slug}", response_model=APIResponse[DoctorPublicProfileResponse])
async def get_doctor_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full public doctor profile by slug."""
    service = DoctorService(db)
    doctor = await service.get_public_doctor_by_slug(slug)
    return APIResponse(success=True, data=_format_public_doctor(doctor))
