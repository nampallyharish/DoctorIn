import re
import uuid
from datetime import datetime, timezone
from typing import BinaryIO

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import logger
from app.models.doctor import VerificationStatus
from app.models.hospital import (
    Hospital,
    HospitalAdmin,
    HospitalAdminRole,
    HospitalDepartment,
    HospitalType,
    HospitalVerificationStatus,
    JobPosting,
)
from app.models.user import User, UserRole
from app.models.verification import (
    HospitalVerificationDocument,
    HospitalVerificationRequest,
    VerificationRequestStatus,
)
from app.repositories.audit_repo import AuditRepository
from app.repositories.doctor_repo import DoctorRepository
from app.repositories.hospital_repo import HospitalRepository
from app.schemas.hospital import (
    AdminHospitalVerificationQueueItem,
    DepartmentResponse,
    HospitalApplicationRequest,
    HospitalProfileUpdate,
    HospitalResponse,
    HospitalVerificationStatusResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    JobPostingCreate,
    JobPostingResponse,
)
from app.schemas.verification import AdminVerificationReviewRequest
from app.services.file_service import FileService


class HospitalService:
    """Coordinates hospital accounts, medical job vacancies, and doctor affiliations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = HospitalRepository(db)
        self.doc_repo = DoctorRepository(db)

    def _format_hospital_response(self, h: Hospital) -> HospitalResponse:
        depts = [
            DepartmentResponse(
                id=d.id,
                hospital_id=d.hospital_id,
                name=d.name,
                description=d.description,
                head_doctor_id=d.head_doctor_id,
                created_at=d.created_at,
            )
            for d in h.departments
        ]

        return HospitalResponse(
            id=h.id,
            name=h.name,
            slug=h.slug,
            tagline=h.tagline,
            hospital_type=h.hospital_type,
            about=h.about,
            website=h.website,
            email=h.email,
            phone=h.phone,
            address_line1=h.address_line1,
            city_name=h.city_name,
            total_beds=h.total_beds,
            accreditations=h.accreditations or [],
            verification_status=h.verification_status,
            verified_at=h.verified_at,
            logo_key=h.logo_key,
            departments=depts,
            created_at=h.created_at,
        )

    def _format_job_response(self, j: JobPosting) -> JobPostingResponse:
        hospital = j.hospital
        return JobPostingResponse(
            id=j.id,
            hospital_id=j.hospital_id,
            hospital_name=hospital.name if hospital else "Medical Center",
            hospital_slug=hospital.slug if hospital else "",
            hospital_logo_key=hospital.logo_key if hospital else None,
            hospital_verified=hospital.verification_status == VerificationStatus.VERIFIED if hospital else False,
            title=j.title,
            slug=j.slug,
            employment_type=j.employment_type,
            city_name=j.city_name,
            min_experience_years=j.min_experience_years,
            max_experience_years=j.max_experience_years,
            salary_min=j.salary_min,
            salary_max=j.salary_max,
            salary_currency=j.salary_currency,
            description=j.description,
            requirements=j.requirements,
            benefits=j.benefits,
            status=j.status,
            application_deadline=j.application_deadline,
            views_count=j.views_count,
            applications_count=j.applications_count,
            created_at=j.created_at,
        )

    async def get_hospital_by_slug(self, slug: str) -> HospitalResponse:
        """Fetch public hospital profile."""
        hospital = await self.repo.get_by_slug(slug)
        if not hospital:
            raise NotFoundError("Hospital not found.")
        return self._format_hospital_response(hospital)

    async def get_my_hospital(self, user: User) -> HospitalResponse:
        """Fetch hospital profile for hospital admin."""
        if user.role != UserRole.HOSPITAL_ADMIN:
            raise ForbiddenError("Only hospital administrators can access hospital settings.")
        hospital = await self.repo.get_by_user_id(user.id)
        if not hospital:
            raise NotFoundError("Hospital profile not found.")
        return self._format_hospital_response(hospital)

    async def update_my_hospital(
        self, user: User, payload: HospitalProfileUpdate
    ) -> HospitalResponse:
        """Update hospital information."""
        if user.role != UserRole.HOSPITAL_ADMIN:
            raise ForbiddenError("Only hospital administrators can update hospital profile.")
        hospital = await self.repo.get_by_user_id(user.id)
        if not hospital:
            raise NotFoundError("Hospital profile not found.")

        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(hospital, k, v)

        await self.db.flush()
        return self._format_hospital_response(hospital)

    # --- Job Operations ---
    async def create_job_posting(
        self, user: User, payload: JobPostingCreate
    ) -> JobPostingResponse:
        """Hospital admin creates medical job vacancy."""
        if user.role != UserRole.HOSPITAL_ADMIN:
            raise ForbiddenError("Only hospital administrators can post job openings.")

        hospital = await self.repo.get_by_user_id(user.id)
        if not hospital:
            raise NotFoundError("Hospital profile not found.")

        job = await self.repo.create_job_posting(
            hospital_id=hospital.id,
            **payload.model_dump(),
        )
        job.hospital = hospital
        return self._format_job_response(job)

    async def list_jobs(
        self,
        specialization_id: uuid.UUID | None = None,
        city: str | None = None,
        min_experience: int | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[JobPostingResponse], int]:
        """List active medical job postings."""
        skip = (page - 1) * per_page
        jobs, total = await self.repo.list_job_postings(
            specialization_id=specialization_id,
            city=city,
            min_experience=min_experience,
            skip=skip,
            limit=per_page,
        )
        return [self._format_job_response(j) for j in jobs], total

    async def get_job_by_id(self, job_id: uuid.UUID) -> JobPostingResponse:
        """Get single job details."""
        job = await self.repo.get_job_by_id(job_id)
        if not job:
            raise NotFoundError("Job posting not found.")
        return self._format_job_response(job)

    async def apply_to_job(
        self, user: User, job_id: uuid.UUID, payload: JobApplicationCreate
    ) -> JobApplicationResponse:
        """Doctor applies to medical job opening."""
        if user.role != UserRole.DOCTOR:
            raise ForbiddenError("Only doctors can apply to clinical positions.")

        doctor = await self.doc_repo.get_by_user_id(user.id)
        if not doctor:
            raise NotFoundError("Doctor profile not found.")

        job = await self.repo.get_job_by_id(job_id)
        if not job:
            raise NotFoundError("Job posting not found.")

        app = await self.repo.apply_to_job(
            job_id=job_id,
            doctor_id=doctor.id,
            cover_note=payload.cover_note,
        )

        return JobApplicationResponse(
            id=app.id,
            job_id=job.id,
            job_title=job.title,
            doctor_id=doctor.id,
            doctor_name=doctor.full_name,
            doctor_slug=doctor.slug,
            doctor_headline=doctor.headline,
            doctor_verified=doctor.verification_status == VerificationStatus.VERIFIED,
            cover_note=app.cover_note,
            status=app.status,
            applied_at=app.applied_at,
        )

    # --- Hospital Application & Verification ---
    async def upload_hospital_document(
        self,
        user: User,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        size_bytes: int,
    ) -> tuple[str, str]:
        """Upload hospital verification document securely to private storage."""
        hospital = await self.repo.get_by_user_id(user.id)
        entity_id = hospital.id if hospital else user.id

        storage_key, original_name = FileService.upload_document(
            file_obj=file_obj,
            entity_id=entity_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            category="hospital_verification",
        )
        return storage_key, original_name

    async def apply_hospital_account(
        self,
        user: User,
        payload: HospitalApplicationRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> HospitalVerificationRequest:
        """Create hospital account in pending verification state with legal details, facility info, and verification documents."""
        existing_hospital = await self.repo.get_by_user_id(user.id)
        now = datetime.now(timezone.utc)

        h_type = HospitalType.GENERAL
        if payload.hospital_type:
            try:
                h_type = HospitalType(payload.hospital_type)
            except ValueError:
                h_type = HospitalType.GENERAL

        if not existing_hospital:
            name = payload.name.strip()
            base_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            hospital = Hospital(
                name=name,
                slug=unique_slug,
                description=payload.description,
                hospital_type=h_type,
                email=payload.email or user.email,
                phone=payload.phone or user.phone,
                website=payload.website,
                address=payload.address,
                pincode=payload.pincode,
                verification_status=HospitalVerificationStatus.PENDING,
                legal_entity_name=payload.legal_entity_name,
                registration_number=payload.registration_number,
                year_established=payload.year_established,
                ownership_type=payload.ownership_type,
                contact_person_name=payload.contact_person_name,
                contact_person_designation=payload.contact_person_designation,
                contact_person_phone=payload.contact_person_phone,
                contact_person_email=payload.contact_person_email,
                bed_count=payload.bed_count,
                has_emergency_services=payload.has_emergency_services,
            )
            self.db.add(hospital)
            await self.db.flush()

            admin_link = HospitalAdmin(
                hospital_id=hospital.id,
                user_id=user.id,
                role=HospitalAdminRole.OWNER,
            )
            self.db.add(admin_link)
            await self.db.flush()
        else:
            hospital = existing_hospital
            hospital.name = payload.name.strip()
            hospital.description = payload.description
            if payload.email:
                hospital.email = payload.email
            if payload.phone:
                hospital.phone = payload.phone
            if payload.website:
                hospital.website = payload.website
            if payload.address:
                hospital.address = payload.address
            if payload.pincode:
                hospital.pincode = payload.pincode
            hospital.verification_status = HospitalVerificationStatus.PENDING
            hospital.legal_entity_name = payload.legal_entity_name
            hospital.registration_number = payload.registration_number
            hospital.year_established = payload.year_established
            hospital.ownership_type = payload.ownership_type
            hospital.contact_person_name = payload.contact_person_name
            hospital.contact_person_designation = payload.contact_person_designation
            hospital.contact_person_phone = payload.contact_person_phone
            hospital.contact_person_email = payload.contact_person_email
            hospital.bed_count = payload.bed_count
            hospital.has_emergency_services = payload.has_emergency_services
            await self.db.flush()

        for dept_name in payload.departments:
            dept = HospitalDepartment(
                hospital_id=hospital.id,
                name=dept_name.strip(),
            )
            self.db.add(dept)

        ver_req = HospitalVerificationRequest(
            hospital_id=hospital.id,
            status=VerificationRequestStatus.PENDING,
            submitted_at=now,
        )
        self.db.add(ver_req)
        await self.db.flush()

        for doc in payload.documents:
            h_doc = HospitalVerificationDocument(
                verification_request_id=ver_req.id,
                document_type=doc.document_type,
                document_key=doc.document_key,
                original_name=doc.original_name,
                mime_type=doc.mime_type,
                size_bytes=doc.size_bytes,
            )
            self.db.add(h_doc)

        await self.db.flush()

        audit_repo = AuditRepository(self.db)
        await audit_repo.log_action(
            action="HOSPITAL_APPLICATION_SUBMITTED",
            resource_type="hospital_verification_request",
            actor_id=user.id,
            resource_id=ver_req.id,
            details={
                "hospital_id": str(hospital.id),
                "hospital_name": hospital.name,
                "registration_number": payload.registration_number,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return ver_req

    async def get_hospital_verification_status(self, user: User) -> HospitalVerificationStatusResponse:
        """Retrieve applicant's hospital verification status and feedback."""
        hospital = await self.repo.get_by_user_id(user.id)
        if not hospital:
            return HospitalVerificationStatusResponse(
                hospital_id=None,
                verification_status="not_created",
            )

        query = (
            select(HospitalVerificationRequest)
            .where(HospitalVerificationRequest.hospital_id == hospital.id)
            .options(selectinload(HospitalVerificationRequest.documents))
            .order_by(HospitalVerificationRequest.submitted_at.desc())
            .limit(1)
        )
        res = await self.db.execute(query)
        latest_req = res.scalar_one_or_none()

        docs_data = []
        if latest_req and latest_req.documents:
            for d in latest_req.documents:
                download_url = FileService.get_presigned_download_url(d.document_key)
                docs_data.append({
                    "id": str(d.id),
                    "document_type": d.document_type,
                    "original_name": d.original_name,
                    "mime_type": d.mime_type,
                    "size_bytes": d.size_bytes,
                    "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                    "download_url": download_url,
                })

        return HospitalVerificationStatusResponse(
            hospital_id=hospital.id,
            hospital_name=hospital.name,
            verification_status=hospital.verification_status.value,
            verified_at=hospital.verified_at,
            latest_request_id=latest_req.id if latest_req else None,
            latest_request_status=latest_req.status.value if latest_req else None,
            admin_notes=latest_req.admin_notes if latest_req else None,
            rejection_reason=latest_req.admin_notes if (latest_req and latest_req.status == VerificationRequestStatus.REJECTED) else None,
            submitted_at=latest_req.submitted_at if latest_req else None,
            reviewed_at=latest_req.reviewed_at if latest_req else None,
            documents=docs_data,
        )

    # --- Admin Hospital Review Operations ---
    async def list_admin_hospital_queue(
        self,
        status_filter: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[AdminHospitalVerificationQueueItem], int]:
        """Fetch hospital verification applications queue for administrator review."""
        req_status = None
        if status_filter:
            try:
                req_status = VerificationRequestStatus(status_filter)
            except ValueError:
                pass

        skip = (page - 1) * per_page
        query = (
            select(HospitalVerificationRequest)
            .options(
                selectinload(HospitalVerificationRequest.hospital),
                selectinload(HospitalVerificationRequest.documents),
            )
            .order_by(HospitalVerificationRequest.submitted_at.asc())
            .offset(skip)
            .limit(per_page)
        )
        if req_status:
            query = query.where(HospitalVerificationRequest.status == req_status)

        count_query = select(func.count(HospitalVerificationRequest.id))
        if req_status:
            count_query = count_query.where(HospitalVerificationRequest.status == req_status)

        results = await self.db.execute(query)
        total = await self.db.scalar(count_query) or 0
        requests = results.scalars().all()

        items = []
        for r in requests:
            h = r.hospital
            items.append(
                AdminHospitalVerificationQueueItem(
                    request_id=r.id,
                    hospital_id=h.id if h else uuid.uuid4(),
                    hospital_name=h.name if h else "Unknown Hospital",
                    hospital_type=h.hospital_type.value if (h and hasattr(h.hospital_type, "value")) else "general",
                    legal_entity_name=h.legal_entity_name if h else None,
                    registration_number=h.registration_number if h else None,
                    contact_person_name=h.contact_person_name if h else None,
                    contact_person_email=h.contact_person_email if h else None,
                    contact_person_phone=h.contact_person_phone if h else None,
                    city=h.address if h else None,
                    status=r.status.value,
                    submitted_at=r.submitted_at,
                    documents_count=len(r.documents) if r.documents else 0,
                )
            )

        return items, total

    async def review_hospital_verification(
        self,
        admin_user: User,
        request_id: uuid.UUID,
        payload: AdminVerificationReviewRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> HospitalVerificationRequest:
        """Approve or reject hospital verification application."""
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only administrators can review hospital applications.")

        query = (
            select(HospitalVerificationRequest)
            .where(HospitalVerificationRequest.id == request_id)
            .options(selectinload(HospitalVerificationRequest.hospital))
        )
        result = await self.db.execute(query)
        req = result.scalar_one_or_none()
        if not req:
            raise NotFoundError("Hospital verification request not found.")

        now = datetime.now(timezone.utc)
        hospital = req.hospital
        req.admin_id = admin_user.id
        req.reviewed_at = now

        action = payload.action.lower()
        if action == "approve":
            req.status = VerificationRequestStatus.APPROVED
            hospital.verification_status = HospitalVerificationStatus.VERIFIED
            hospital.verified_at = now.date()
            # Promote applicant/admins to HOSPITAL_ADMIN if they are normal users
            admin_query = select(HospitalAdmin).where(HospitalAdmin.hospital_id == hospital.id)
            admins_res = await self.db.execute(admin_query)
            admins = admins_res.scalars().all()
            for ha in admins:
                user_record = await self.db.get(User, ha.user_id)
                if user_record and user_record.role == UserRole.USER:
                    user_record.role = UserRole.HOSPITAL_ADMIN

            logger.info(f"✅ Hospital {hospital.id} APPROVED by admin {admin_user.id}.")
        elif action == "reject":
            req.status = VerificationRequestStatus.REJECTED
            hospital.verification_status = HospitalVerificationStatus.REJECTED
            req.admin_notes = payload.rejection_reason or payload.admin_notes
            logger.info(f"❌ Hospital {hospital.id} REJECTED by admin {admin_user.id}. Reason: {payload.rejection_reason}")

        await self.db.flush()

        audit_repo = AuditRepository(self.db)
        await audit_repo.log_action(
            action=f"HOSPITAL_VERIFICATION_{action.upper()}",
            resource_type="hospital_verification_request",
            actor_id=admin_user.id,
            resource_id=req.id,
            details={
                "hospital_id": str(hospital.id),
                "action": action,
                "rejection_reason": payload.rejection_reason,
                "admin_notes": payload.admin_notes,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return req
