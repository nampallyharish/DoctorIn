"""Admin Doctor Verification Review REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_db, require_admin
from app.models.user import User
from app.schemas.common import APIResponse, MetaData
from app.schemas.hospital import AdminHospitalVerificationQueueItem
from app.schemas.verification import (
    AdminVerificationQueueItem,
    AdminVerificationReviewRequest,
)
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/admin/verification", tags=["Admin Verification"])


@router.get(
    "/queue",
    response_model=APIResponse[list[AdminVerificationQueueItem]],
    summary="List pending doctor verification requests",
)
async def get_verification_queue(
    status_filter: str | None = Query(None, description="pending, under_review, approved, rejected"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin queue listing doctor credential submissions."""
    service = VerificationService(db)
    items, total = await service.list_admin_queue(
        status_filter=status_filter,
        page=page,
        per_page=per_page,
    )

    return APIResponse(
        success=True,
        data=items,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )


@router.put(
    "/{request_id}/review",
    response_model=APIResponse[dict],
    summary="Review doctor verification request (approve, reject, request_info, suspend)",
)
async def review_verification(
    request_id: uuid.UUID,
    payload: AdminVerificationReviewRequest,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute admin decision on credential verification.
    If 'approve', doctor receives the DoctorIn Verified badge.
    """
    service = VerificationService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    req = await service.review_verification_request(
        admin_user=current_admin,
        request_id=request_id,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data={
            "request_id": str(req.id),
            "status": req.status.value,
            "message": f"Verification decision '{payload.action}' recorded successfully.",
        },
    )


# --- Admin Hospital Verification Endpoints ---
@router.get(
    "/hospitals/queue",
    response_model=APIResponse[list[AdminHospitalVerificationQueueItem]],
    summary="List pending hospital verification requests",
)
async def get_hospital_verification_queue(
    status_filter: str | None = Query(None, description="pending, under_review, approved, rejected"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin queue listing hospital applications and credentials."""
    from app.services.hospital_service import HospitalService

    service = HospitalService(db)
    items, total = await service.list_admin_hospital_queue(
        status_filter=status_filter,
        page=page,
        per_page=per_page,
    )

    return APIResponse(
        success=True,
        data=items,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )


@router.put(
    "/hospitals/{request_id}/review",
    response_model=APIResponse[dict],
    summary="Review hospital verification application (approve, reject)",
)
async def review_hospital_verification(
    request_id: uuid.UUID,
    payload: AdminVerificationReviewRequest,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a hospital verification application."""
    from app.services.hospital_service import HospitalService

    service = HospitalService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    req = await service.review_hospital_verification(
        admin_user=current_admin,
        request_id=request_id,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return APIResponse(
        success=True,
        data={
            "request_id": str(req.id),
            "status": req.status.value,
            "message": f"Hospital verification decision '{payload.action}' recorded successfully.",
        },
    )

