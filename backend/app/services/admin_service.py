"""Platform Administration, User Moderation, and Security Audit Service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import logger
from app.models.audit import AuditLog, Report, ReportStatus, TargetType
from app.models.doctor import Doctor, VerificationStatus
from app.models.hospital import Hospital, JobPosting, JobPostingStatus
from app.models.patient import Patient
from app.models.post import Post, PostComment
from app.models.user import User, UserRole, UserStatus
from app.models.verification import VerificationRequest, VerificationRequestStatus
from app.repositories.audit_repo import AuditRepository
from app.schemas.admin import (
    AdminReportItem,
    AdminReportReviewRequest,
    AdminStatsResponse,
    AdminUserItem,
    AdminUserStatusUpdate,
    AuditLogResponseItem,
)


class AdminService:
    """Business operations for system administration and platform security."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditRepository(db)

    async def get_platform_stats(self, admin_user: User) -> AdminStatsResponse:
        """Calculate real-time KPIs and platform analytics."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Administrator access required.")

        total_users = await self.db.scalar(select(func.count(User.id))) or 0
        total_doctors = await self.db.scalar(select(func.count(Doctor.id))) or 0
        total_verified_doctors = await self.db.scalar(
            select(func.count(Doctor.id)).where(Doctor.verification_status == VerificationStatus.VERIFIED)
        ) or 0
        pending_verifications = await self.db.scalar(
            select(func.count(VerificationRequest.id)).where(
                VerificationRequest.status == VerificationRequestStatus.PENDING
            )
        ) or 0
        total_hospitals = await self.db.scalar(select(func.count(Hospital.id))) or 0
        total_patients = await self.db.scalar(select(func.count(Patient.id))) or 0
        active_jobs = await self.db.scalar(
            select(func.count(JobPosting.id)).where(
                JobPosting.status == JobPostingStatus.ACTIVE, JobPosting.deleted_at.is_(None)
            )
        ) or 0
        pending_reports = await self.db.scalar(
            select(func.count(Report.id)).where(Report.status == ReportStatus.PENDING)
        ) or 0

        return AdminStatsResponse(
            total_users=total_users,
            total_doctors=total_doctors,
            total_verified_doctors=total_verified_doctors,
            pending_verifications=pending_verifications,
            total_hospitals=total_hospitals,
            total_patients=total_patients,
            active_jobs=active_jobs,
            pending_reports=pending_reports,
        )

    async def list_users(
        self,
        admin_user: User,
        role_filter: str | None = None,
        search_query: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[AdminUserItem], int]:
        """List platform users with details, verification status, and search."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Administrator access required.")

        query = (
            select(User)
            .options(
                selectinload(User.doctor_profile),
                selectinload(User.hospital_profile),
                selectinload(User.patient_profile),
            )
            .order_by(desc(User.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        conditions = []
        if role_filter:
            try:
                r_enum = UserRole(role_filter)
                conditions.append(User.role == r_enum)
            except ValueError:
                pass

        if search_query and search_query.strip():
            clean = f"%{search_query.strip()}%"
            conditions.append(
                or_(
                    User.email.ilike(clean),
                    User.phone.ilike(clean),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        count_q = select(func.count(User.id))
        if conditions:
            count_q = count_q.where(and_(*conditions))

        results = await self.db.execute(query)
        users = results.scalars().all()
        total = await self.db.scalar(count_q) or 0

        items = []
        for u in users:
            name = "User"
            slug = None
            verified = False

            if u.doctor_profile:
                name = u.doctor_profile.full_name
                slug = u.doctor_profile.slug
                verified = u.doctor_profile.verification_status == VerificationStatus.VERIFIED
            elif u.hospital_profile:
                name = u.hospital_profile.name
                slug = u.hospital_profile.slug
                verified = u.hospital_profile.verification_status == VerificationStatus.VERIFIED
            elif u.patient_profile:
                name = u.patient_profile.full_name

            items.append(
                AdminUserItem(
                    id=u.id,
                    email=u.email,
                    phone=u.phone,
                    role=u.role,
                    status=u.status,
                    is_active=u.is_active,
                    name=name,
                    slug=slug,
                    verified=verified,
                    created_at=u.created_at,
                )
            )

        return items, total

    async def update_user_status(
        self,
        admin_user: User,
        user_id: uuid.UUID,
        payload: AdminUserStatusUpdate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        """Suspend, ban, or reactivate user account with audit trail."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Administrator access required.")

        target_user = await self.db.get(User, user_id)
        if not target_user:
            raise NotFoundError("User not found.")

        old_status = target_user.status
        action = payload.action.lower()

        if action == "activate":
            target_user.status = UserStatus.ACTIVE
            target_user.is_active = True
        elif action == "suspend":
            target_user.status = UserStatus.SUSPENDED
            target_user.is_active = False
        elif action == "ban":
            target_user.status = UserStatus.BANNED
            target_user.is_active = False

        await self.db.flush()

        # Audit log
        await self.audit_repo.log_action(
            action=f"USER_{action.upper()}",
            resource_type="user",
            actor_id=admin_user.id,
            resource_id=target_user.id,
            details={
                "old_status": old_status.value,
                "new_status": target_user.status.value,
                "reason": payload.reason,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.warning(
            f"🛡️ Admin {admin_user.id} updated user {target_user.id} status to {target_user.status.value}"
        )
        return target_user

    async def list_reports(
        self,
        admin_user: User,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[AdminReportItem], int]:
        """Fetch pending community moderation reports."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Administrator access required.")

        query = (
            select(Report)
            .options(
                selectinload(Report.reporter).selectinload(User.doctor_profile),
            )
            .order_by(desc(Report.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        count_q = select(func.count(Report.id))

        results = await self.db.execute(query)
        reports = results.scalars().all()
        total = await self.db.scalar(count_q) or 0

        items = []
        for r in reports:
            rep_name = "Community User"
            if r.reporter and r.reporter.doctor_profile:
                rep_name = r.reporter.doctor_profile.full_name
            elif r.reporter and r.reporter.email:
                rep_name = r.reporter.email

            items.append(
                AdminReportItem(
                    id=r.id,
                    reporter_id=r.reporter_id,
                    reporter_name=rep_name,
                    target_type=r.target_type,
                    target_id=r.target_id,
                    reason=r.reason,
                    description=r.description,
                    status=r.status,
                    created_at=r.created_at,
                )
            )

        return items, total

    async def review_report(
        self,
        admin_user: User,
        report_id: uuid.UUID,
        payload: AdminReportReviewRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Report:
        """Resolve report by taking down content or dismissing."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Administrator access required.")

        report = await self.db.get(Report, report_id)
        if not report:
            raise NotFoundError("Report not found.")

        now = datetime.now(timezone.utc)
        report.reviewer_id = admin_user.id
        report.reviewed_at = now
        report.review_notes = payload.review_notes

        action = payload.action.lower()
        if action == "resolve_takedown":
            report.status = ReportStatus.RESOLVED
            # Takedown target
            if report.target_type == TargetType.POST:
                post = await self.db.get(Post, report.target_id)
                if post:
                    post.is_moderated = True
                    post.deleted_at = now
            elif report.target_type == TargetType.COMMENT:
                comment = await self.db.get(PostComment, report.target_id)
                if comment:
                    comment.is_moderated = True
                    comment.deleted_at = now

            logger.info(f"🚫 Admin {admin_user.id} took down content for report {report.id}")
        else:
            report.status = ReportStatus.DISMISSED
            logger.info(f"Admin {admin_user.id} dismissed report {report.id}")

        await self.db.flush()

        # Audit log
        await self.audit_repo.log_action(
            action=f"REPORT_{action.upper()}",
            resource_type="report",
            actor_id=admin_user.id,
            resource_id=report.id,
            details={
                "target_type": report.target_type.value,
                "target_id": str(report.target_id),
                "review_notes": payload.review_notes,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return report

    async def list_audit_logs(
        self,
        admin_user: User,
        page: int = 1,
        per_page: int = 30,
    ) -> tuple[list[AuditLogResponseItem], int]:
        """Fetch immutable platform security audit log records."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Administrator access required.")

        query = (
            select(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        count_q = select(func.count(AuditLog.id))

        results = await self.db.execute(query)
        logs = results.scalars().all()
        total = await self.db.scalar(count_q) or 0

        items = [
            AuditLogResponseItem(
                id=l.id,
                actor_id=l.actor_id,
                actor_name=str(l.actor_id) if l.actor_id else "System",
                action=l.action,
                resource_type=l.resource_type,
                resource_id=l.resource_id,
                details=l.details,
                ip_address=l.ip_address,
                created_at=l.created_at,
            )
            for l in logs
        ]

        return items, total
