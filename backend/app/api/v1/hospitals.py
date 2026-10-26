"""Hospital Profiles, Applications, and Verification REST API endpoints."""

import io

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.hospital import (
    HospitalApplicationRequest,
    HospitalProfileUpdate,
    HospitalResponse,
    HospitalVerificationStatusResponse,
)
from app.services.hospital_service import HospitalService

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


@router.post(
    "/upload-document",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Upload hospital license or accreditation document",
)
async def upload_hospital_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload verification document (license, accreditation) for hospital application."""
    service = HospitalService(db)
    contents = await file.read()
    size_bytes = len(contents)
    file_io = io.BytesIO(contents)

    storage_key, filename = await service.upload_hospital_document(
        user=current_user,
        file_obj=file_io,
        filename=file.filename or "hospital_document.pdf",
        content_type=file.content_type or "application/pdf",
        size_bytes=size_bytes,
    )

    return APIResponse(
        success=True,
        data={
            "document_key": storage_key,
            "document_original_name": filename,
            "document_mime_type": file.content_type,
            "document_size_bytes": size_bytes,
            "message": "Hospital document uploaded securely.",
        },
    )


@router.post(
    "/apply",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Submit hospital verification application",
)
async def apply_hospital(
    payload: HospitalApplicationRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit hospital application with legal details, facility information, and documents."""
    service = HospitalService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    ver_req = await service.apply_hospital_account(
        user=current_user,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data={
            "request_id": str(ver_req.id),
            "status": ver_req.status.value,
            "message": "Hospital application submitted successfully. Verification team will review it.",
        },
    )


@router.get(
    "/me/verification/status",
    response_model=APIResponse[HospitalVerificationStatusResponse],
    summary="Get hospital verification status for current user",
)
async def get_hospital_verification_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check hospital verification application status and details."""
    service = HospitalService(db)
    status_data = await service.get_hospital_verification_status(current_user)
    return APIResponse(success=True, data=status_data)


@router.get("/me", response_model=APIResponse[HospitalResponse], summary="Get own hospital profile")
async def get_my_hospital(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve hospital profile for authenticated hospital administrator."""
    service = HospitalService(db)
    hospital = await service.get_my_hospital(current_user)
    return APIResponse(success=True, data=hospital)


@router.put("/me", response_model=APIResponse[HospitalResponse], summary="Update own hospital profile")
async def update_my_hospital(
    payload: HospitalProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update hospital profile information."""
    service = HospitalService(db)
    hospital = await service.update_my_hospital(current_user, payload)
    return APIResponse(success=True, data=hospital)


@router.get("/{slug}", response_model=APIResponse[HospitalResponse], summary="Get public hospital profile by slug")
async def get_hospital_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve public hospital details, accredited departments, and affiliations."""
    service = HospitalService(db)
    hospital = await service.get_hospital_by_slug(slug)
    return APIResponse(success=True, data=hospital)

