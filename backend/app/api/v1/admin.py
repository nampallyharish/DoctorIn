"""Platform Administration, User Moderation, and Audit Log REST API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_db, require_admin
from app.models.user import User
from app.schemas.admin import (
    AdminReportItem,
    AdminReportReviewRequest,
    AdminStatsResponse,
    AdminUserItem,
    AdminUserStatusUpdate,
    AuditLogResponseItem,
)
from app.schemas.common import APIResponse, MetaData
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Platform Administration"])


@router.get("/stats", response_model=APIResponse[AdminStatsResponse], summary="Get real-time platform KPIs & stats")
async def get_platform_stats(
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve platform statistics and health metrics."""
    service = AdminService(db)
    stats = await service.get_platform_stats(current_admin)
    return APIResponse(success=True, data=stats)


@router.get("/users", response_model=APIResponse[list[AdminUserItem]], summary="List all platform users with search & filters")
async def list_users(
    role: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List users for administrator management."""
    service = AdminService(db)
    users, total = await service.list_users(
        admin_user=current_admin,
        role_filter=role,
        search_query=q,
        page=page,
        per_page=per_page,
    )
    return APIResponse(
        success=True,
        data=users,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )


@router.put("/users/{user_id}/status", response_model=APIResponse[dict], summary="Change user status (activate, suspend, ban)")
async def update_user_status(
    user_id: uuid.UUID,
    payload: AdminUserStatusUpdate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Suspend, ban, or reactivate user account."""
    service = AdminService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    user = await service.update_user_status(
        admin_user=current_admin,
        user_id=user_id,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return APIResponse(
        success=True,
        data={"user_id": str(user.id), "status": user.status.value, "message": f"User status updated to {user.status.value}."},
    )


@router.get("/reports", response_model=APIResponse[list[AdminReportItem]], summary="List community moderation reports")
async def list_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List flagged content for moderation."""
    service = AdminService(db)
    reports, total = await service.list_reports(
        admin_user=current_admin,
        page=page,
        per_page=per_page,
    )
    return APIResponse(
        success=True,
        data=reports,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )


@router.put("/reports/{report_id}/review", response_model=APIResponse[dict], summary="Review report (takedown content or dismiss)")
async def review_report(
    report_id: uuid.UUID,
    payload: AdminReportReviewRequest,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Resolve report."""
    service = AdminService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    report = await service.review_report(
        admin_user=current_admin,
        report_id=report_id,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return APIResponse(
        success=True,
        data={"report_id": str(report.id), "status": report.status.value, "message": f"Report decision '{payload.action}' recorded."},
    )


@router.get("/audit-logs", response_model=APIResponse[list[AuditLogResponseItem]], summary="Query immutable security audit logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List immutable security audit log stream."""
    service = AdminService(db)
    logs, total = await service.list_audit_logs(
        admin_user=current_admin,
        page=page,
        per_page=per_page,
    )
    return APIResponse(
        success=True,
        data=logs,
        meta=MetaData(page=page, per_page=per_page, total=total),
    )
