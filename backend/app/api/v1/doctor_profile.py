"""Doctor Profile and Sub-resources Management REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_doctor
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.doctor import (
    AchievementCreate,
    AchievementResponse,
    DoctorProfileResponse,
    DoctorProfileUpdate,
    EducationCreate,
    EducationResponse,
    ExperienceCreate,
    ExperienceResponse,
    PublicationCreate,
    PublicationResponse,
    SpecializationAddRequest,
    SpecializationItem,
)
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors/me", tags=["Doctor Profile"])


def _format_doctor_response(doctor) -> DoctorProfileResponse:
    """Format SQLAlchemy Doctor entity into DoctorProfileResponse schema."""
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

    return DoctorProfileResponse(
        id=doctor.id,
        user_id=doctor.user_id,
        full_name=doctor.full_name,
        slug=doctor.slug,
        headline=doctor.headline,
        bio=doctor.bio,
        years_of_experience=doctor.years_of_experience,
        current_organization=doctor.current_organization,
        website=doctor.website,
        profile_photo_key=doctor.profile_photo_key,
        verification_status=doctor.verification_status,
        verified_at=doctor.verified_at,
        profile_completion=doctor.profile_completion,
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
            AchievementResponse(
                id=a.id,
                doctor_id=a.doctor_id,
                title=a.title,
                description=a.description,
                issuing_organization=a.issuing_organization,
                achievement_date=a.achievement_date,
                display_order=a.display_order,
                created_at=a.created_at,
            )
            for a in doctor.achievements
        ],
        publications=[
            PublicationResponse(
                id=p.id,
                doctor_id=p.doctor_id,
                title=p.title,
                journal=p.journal,
                publication_url=p.publication_url,
                doi=p.doi,
                publication_date=p.publication_date,
                abstract=p.abstract,
                authors=p.authors,
                display_order=p.display_order,
                created_at=p.created_at,
            )
            for p in doctor.publications
        ],
        created_at=doctor.created_at,
        updated_at=doctor.updated_at,
    )


@router.get("", response_model=APIResponse[DoctorProfileResponse], summary="Get own doctor profile")
async def get_my_profile(
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    doctor = await service.get_doctor_by_user(current_user)
    return APIResponse(success=True, data=_format_doctor_response(doctor))


@router.put("", response_model=APIResponse[DoctorProfileResponse], summary="Update own doctor profile")
async def update_my_profile(
    payload: DoctorProfileUpdate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    doctor = await service.update_profile(current_user, payload)
    return APIResponse(success=True, data=_format_doctor_response(doctor))


# --- Education ---
@router.post("/education", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def add_education(
    payload: EducationCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    edu = await service.add_education(current_user, payload)
    return APIResponse(success=True, data={"id": str(edu.id), "message": "Education added successfully."})


@router.delete("/education/{education_id}", response_model=APIResponse[dict])
async def delete_education(
    education_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    await service.remove_education(current_user, education_id)
    return APIResponse(success=True, data={"message": "Education record deleted."})


# --- Experience ---
@router.post("/experience", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def add_experience(
    payload: ExperienceCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    exp = await service.add_experience(current_user, payload)
    return APIResponse(success=True, data={"id": str(exp.id), "message": "Experience added successfully."})


@router.delete("/experience/{experience_id}", response_model=APIResponse[dict])
async def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    await service.remove_experience(current_user, experience_id)
    return APIResponse(success=True, data={"message": "Experience record deleted."})


# --- Specializations ---
@router.post("/specializations", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def add_specialization(
    payload: SpecializationAddRequest,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    await service.add_specialization(current_user, payload)
    return APIResponse(success=True, data={"message": "Specialization associated."})


@router.delete("/specializations/{specialization_id}", response_model=APIResponse[dict])
async def delete_specialization(
    specialization_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    await service.remove_specialization(current_user, specialization_id)
    return APIResponse(success=True, data={"message": "Specialization removed."})


# --- Achievements ---
@router.post("/achievements", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def add_achievement(
    payload: AchievementCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    ach = await service.add_achievement(current_user, payload)
    return APIResponse(success=True, data={"id": str(ach.id), "message": "Achievement added."})


@router.delete("/achievements/{achievement_id}", response_model=APIResponse[dict])
async def delete_achievement(
    achievement_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    await service.remove_achievement(current_user, achievement_id)
    return APIResponse(success=True, data={"message": "Achievement removed."})


# --- Publications ---
@router.post("/publications", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def add_publication(
    payload: PublicationCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    pub = await service.add_publication(current_user, payload)
    return APIResponse(success=True, data={"id": str(pub.id), "message": "Publication added."})


@router.delete("/publications/{publication_id}", response_model=APIResponse[dict])
async def delete_publication(
    publication_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    service = DoctorService(db)
    await service.remove_publication(current_user, publication_id)
    return APIResponse(success=True, data={"message": "Publication removed."})
