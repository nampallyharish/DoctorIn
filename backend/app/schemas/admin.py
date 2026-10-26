"""Pydantic schemas for Platform Administration, User Management, Moderation, and Audit Logs."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.audit import ReportReason, ReportStatus, TargetType
from app.models.user import UserRole, UserStatus


class AdminStatsResponse(BaseModel):
    total_users: int
    total_doctors: int
    total_verified_doctors: int
    pending_verifications: int
    total_hospitals: int
    total_patients: int
    active_jobs: int
    pending_reports: int


class AdminUserItem(BaseModel):
    id: uuid.UUID
    email: str | None = None
    phone: str | None = None
    role: UserRole
    status: UserStatus
    is_active: bool
    name: str
    slug: str | None = None
    verified: bool = False
    created_at: datetime


class AdminUserStatusUpdate(BaseModel):
    action: str = Field(..., pattern="^(activate|suspend|ban)$")
    reason: str | None = Field(None, max_length=500)


class AdminReportItem(BaseModel):
    id: uuid.UUID
    reporter_id: uuid.UUID
    reporter_name: str
    target_type: TargetType
    target_id: uuid.UUID
    reason: ReportReason
    description: str | None = None
    status: ReportStatus
    created_at: datetime


class AdminReportReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(resolve_takedown|dismiss)$")
    review_notes: str | None = Field(None, max_length=1000)


class AuditLogResponseItem(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    actor_name: str | None = None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None = None
    details: dict | None = None
    ip_address: str | None = None
    created_at: datetime
