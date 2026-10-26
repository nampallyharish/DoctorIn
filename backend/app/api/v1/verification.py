"""Doctor Verification REST API endpoints."""

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.verification import (
    DoctorApplicationRequest,
    VerificationStatusResponse,
    VerificationSubmitRequest,
)
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/doctors/me/verification", tags=["Doctor Verification"])


@router.get(
    "/status",
    response_model=APIResponse[VerificationStatusResponse],
    summary="Get doctor verification status and uploaded credentials",
)
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve current verification status, admin feedback, and active credentials."""
    service = VerificationService(db)
    status_data = await service.get_doctor_verification_status(current_user)
    return APIResponse(success=True, data=status_data)


@router.post(
    "/upload-document",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Securely upload verification credential document (PDF, PNG, JPG)",
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Uploads a verification document to private S3 storage.
    Validates MIME type, limits file size (max 10MB), and returns storage key.
    """
    service = VerificationService(db)
    contents = await file.read()
    size_bytes = len(contents)

    import io
    file_io = io.BytesIO(contents)

    storage_key, filename = await service.upload_verification_document(
        user=current_user,
        file_obj=file_io,
        filename=file.filename or "credential_document.pdf",
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
            "message": "Document uploaded securely.",
        },
    )


@router.post(
    "/apply",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Submit comprehensive doctor application for admin verification review",
)
async def apply_doctor(
    payload: DoctorApplicationRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit full doctor onboarding application with personal, professional, education,
    and medical council registration details.
    """
    service = VerificationService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    req = await service.apply_doctor_account(
        user=current_user,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data={
            "request_id": str(req.id),
            "status": req.status.value,
            "message": "Doctor application submitted successfully. Our medical verification team will review your credentials.",
        },
    )


@router.post(
    "/submit",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Submit professional credentials for DoctorIn verification review",
)
async def submit_verification(
    payload: VerificationSubmitRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit medical registration number, issuing council, and supporting documents for admin review.
    """
    service = VerificationService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    req = await service.submit_verification_request(
        user=current_user,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data={
            "request_id": str(req.id),
            "status": req.status.value,
            "message": "Verification submitted successfully. Our medical verification team will review your credentials.",
        },
    )
