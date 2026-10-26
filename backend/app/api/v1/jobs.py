"""Medical Job Board and Doctor Application REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse, MetaData
from app.schemas.hospital import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobPostingCreate,
    JobPostingResponse,
)
from app.services.hospital_service import HospitalService

router = APIRouter(prefix="/jobs", tags=["Medical Job Board"])


@router.get("", response_model=APIResponse[list[JobPostingResponse]], summary="Browse active medical job openings")
async def list_jobs(
    specialization_id: uuid.UUID | None = Query(None),
    city: str | None = Query(None),
    min_experience: int | None = Query(None, ge=0),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List medical vacancies across verified hospitals."""
    service = HospitalService(db)
    jobs, total = await service.list_jobs(
        specialization_id=specialization_id,
        city=city,
        min_experience=min_experience,
        page=page,
        per_page=per_page,
    )
    return APIResponse(
        success=True,
        data=jobs,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )


@router.post("", response_model=APIResponse[JobPostingResponse], status_code=status.HTTP_201_CREATED, summary="Create job opening (Hospital Admin only)")
async def create_job(
    payload: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Post new medical vacancy."""
    service = HospitalService(db)
    job = await service.create_job_posting(current_user, payload)
    return APIResponse(success=True, data=job)


@router.get("/{job_id}", response_model=APIResponse[JobPostingResponse], summary="Get job vacancy details")
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get single job opening details."""
    service = HospitalService(db)
    job = await service.get_job_by_id(job_id)
    return APIResponse(success=True, data=job)


@router.post("/{job_id}/apply", response_model=APIResponse[JobApplicationResponse], status_code=status.HTTP_201_CREATED, summary="Apply for medical job opening (Doctor only)")
async def apply_job(
    job_id: uuid.UUID,
    payload: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Doctor submits 1-click application with verified profile and optional cover note."""
    service = HospitalService(db)
    application = await service.apply_to_job(current_user, job_id, payload)
    return APIResponse(success=True, data=application)
